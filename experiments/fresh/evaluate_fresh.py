"""Amendment A6 (DECISIONS.md Section 20): score every system on the fresh set, once.

    python experiments/fresh/evaluate_fresh.py --corpus dataset/data/fresh_20261021

Nothing is fitted. Inputs:
  - the fresh manifest (dataset/data/fresh_20261021/manifest.csv and .jsonl),
  - experiments/fresh/visual/tiles_seed<k>.csv (SHA-checked against summary.json),
  - experiments/e2_visual/frozen/tiles_calibration.json (temperatures, t_v),
  - experiments/fusion/frozen_fusion.json (A4) and frozen_fusion_A5.json (A5).
Gate: Section 20 of DECISIONS.md must already be in the commit that added the
fresh visual scores, and the output folder must not exist (one run only).

Writes experiments/results/fresh/: prediction files, a report per system
(evaluate.py metrics, person-clustered 95% CIs), and confirmatory.md with the
pre-registered H1 and the Holm-corrected secondary comparisons.
"""
import argparse
import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments"))
sys.path.insert(0, str(ROOT / "experiments" / "fresh"))
import evaluate as E  # noqa: E402
import check_fresh_identity  # noqa: E402

VIS = ROOT / "experiments" / "fresh" / "visual"
CAL = ROOT / "experiments" / "e2_visual" / "frozen" / "tiles_calibration.json"
A4 = ROOT / "experiments" / "fusion" / "frozen_fusion.json"
A5 = ROOT / "experiments" / "fusion" / "frozen_fusion_A5.json"
CHECKS = {"aadhaar": ("format_check", "checksum_check"),
          "pan": ("format_check", "category_check", "semantic_check")}
A5_FEATURES = [("aadhaar", "format_check"), ("aadhaar", "checksum_check"),
               ("pan", "format_check"), ("pan", "category_check"), ("pan", "semantic_check")]
SPLIT = "test"          # evaluate.py label for the scored set; every fresh image is relabelled to it
B, SEED = 10000, 0


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)


def check_gate(out):
    if out.exists():
        sys.exit(f"STOP: {out} exists. The fresh set is evaluated once.")
    added = git("log", "--diff-filter=A", "--format=%H", "--", "experiments/fresh/visual/summary.json").stdout.split()
    if not added:
        sys.exit("STOP: experiments/fresh/visual/summary.json is not committed.")
    dec = git("show", f"{added[-1]}:DECISIONS.md").stdout
    if "## 20. Amendment A6" not in dec:
        sys.exit("STOP: DECISIONS.md Section 20 is not in the commit that added the fresh scores.")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def logit(p):
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return np.log(p / (1 - p))


def visual(ids, vis_dir=VIS):
    cal = json.loads(CAL.read_text(encoding="utf-8"))
    summary = json.loads((vis_dir / "summary.json").read_text(encoding="utf-8"))
    probs = []
    for s in cal["seeds"]:
        path = vis_dir / f"tiles_seed{s['seed']}.csv"
        if sha(path) != summary["seeds"][str(s["seed"])]["scores_sha256"]:
            sys.exit(f"STOP: {path} does not match its recorded SHA-256.")
        with path.open(newline="", encoding="utf-8") as f:
            z = {r["image_id"]: float(r["logit"]) for r in csv.DictReader(f)}
        if set(z) != set(ids):
            sys.exit(f"STOP: {path} does not cover the fresh set exactly.")
        probs.append(np.array([sigmoid(z[i] / s["temperature"]) for i in ids]))
    return np.mean(probs, axis=0), cal["operating_point"]["threshold"]


def failed_checks(rows, ids, cond):
    out = []
    for i in ids:
        r = rows[i]
        detail = r[f"rule_{cond}_detail"]
        f = {c for c in CHECKS[r["doc_type"]] if detail.get(c) == "FAIL"}
        if bool(f) != (r[f"rule_{cond}_verdict"] == "FAIL"):
            sys.exit(f"STOP: {i}: {cond} verdict disagrees with its checks")
        out.append(f)
    return out


def paired(a, b, y, persons, B, seed):
    """Person-clustered paired bootstrap of recall(a)-recall(b) and fpr(a)-fpr(b)."""
    by_p = {}
    for k, p in enumerate(persons):
        by_p.setdefault(p, []).append(k)
    keys = sorted(by_p)
    rng = np.random.default_rng(seed)
    dr, df = [], []
    for _ in range(B):
        idx = np.concatenate([by_p[p] for p in rng.choice(keys, len(keys), replace=True)])
        yy, aa, bb = y[idx], a[idx], b[idx]
        pos, neg = yy == 1, yy == 0
        dr.append(aa[pos].mean() - bb[pos].mean())
        df.append(aa[neg].mean() - bb[neg].mean())
    dr, df = np.array(dr), np.array(df)
    pos, neg = y == 1, y == 0
    p_two = min(1.0, 2 * min((dr <= 0).mean(), (dr >= 0).mean()))
    return {"recall_diff": float(a[pos].mean() - b[pos].mean()),
            "recall_ci": [float(np.percentile(dr, 2.5)), float(np.percentile(dr, 97.5))],
            "fpr_diff": float(a[neg].mean() - b[neg].mean()),
            "fpr_ci": [float(np.percentile(df, 2.5)), float(np.percentile(df, 97.5))],
            "p_two_sided": float(p_two)}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", required=True)
    ap.add_argument("--out", default=str(ROOT / "experiments" / "results" / "fresh"))
    ap.add_argument("--trial", action="store_true", help="pipeline test on a trial corpus: skips the gate")
    ap.add_argument("--n-persons", type=int, default=90)
    ap.add_argument("--bootstrap", type=int, default=B)
    ap.add_argument("--visual-dir", default=str(VIS), help=argparse.SUPPRESS)
    a = ap.parse_args(argv)
    corpus, out = Path(a.corpus), Path(a.out)
    if not a.trial:
        check_gate(out)
    if check_fresh_identity.main([str(corpus), "--n-persons", str(a.n_persons), "--skip-files"]) != 0:
        sys.exit("STOP: fresh-set leakage/design check failed.")

    with (corpus / "manifest.csv").open(newline="", encoding="utf-8-sig") as f:
        manifest = {r["image_id"]: dict(r, split=SPLIT) for r in csv.DictReader(f)}
    with (corpus / "manifest.jsonl").open(encoding="utf-8") as f:
        rows = {r["image_id"]: r for r in map(json.loads, filter(str.strip, f))}
    ids = sorted(manifest)
    y = np.array([int(manifest[i]["label"]) for i in ids])
    doc = np.array([manifest[i]["doc_type"] for i in ids])
    persons = [manifest[i]["person_id"] for i in ids]
    pan = (doc == "pan").astype(float)

    if not a.trial and Path(a.visual_dir).resolve() != VIS.resolve():
        sys.exit("STOP: --visual-dir is for --trial runs only.")
    p_v, t_v = visual(ids, Path(a.visual_dir))
    a4, a5 = (json.loads(p.read_text(encoding="utf-8")) for p in (A4, A5))
    if abs(a4["visual_threshold"] - t_v) > 1e-12:
        sys.exit("STOP: A4 and calibration disagree on t_v.")
    z_v = logit(p_v)
    vis = p_v >= t_v
    systems = {"visual": (vis, p_v)}
    for cond, tag in (("gt", "GT"), ("ocr", "OCR")):
        fc = failed_checks(rows, ids, cond)
        r = np.array([float(bool(f)) for f in fc])
        lg = a4["conditions"][tag]["logistic"]
        s4 = sigmoid(lg["intercept"] + lg["coef"][0] * z_v + lg["coef"][1] * r + lg["coef"][2] * r * pan)
        systems[f"rules_{tag}"] = (r == 1, None)
        systems[f"OR_{tag}"] = (vis | (r == 1), None)
        systems[f"AND_{tag}"] = (vis & (r == 1), None)
        systems[f"A4_logistic_{tag}"] = (s4 >= lg["threshold"], s4)
        for ref, m in lg.get("matched_fpr_thresholds", {}).items():
            systems[f"A4_logistic_{tag}_at_FPR_of_{ref}"] = (s4 >= m["threshold"], s4)
        X = np.array([[float(doc[k] == d and c in fc[k]) for d, c in A5_FEATURES] for k in range(len(ids))])
        c5 = a5["conditions"][tag]
        s5 = sigmoid(c5["intercept"] + c5["coef"][0] * z_v + X @ np.array(c5["coef"][1:]))
        for tname, t in c5["thresholds"].items():
            systems[f"A5_perCheck_{tag}" + ("" if tname == "5pct" else f"_{tname}")] = (s5 >= t, s5)

    out.mkdir(parents=True, exist_ok=True)
    index = {}
    for name, (dec, score) in systems.items():
        with (out / f"{name}_predictions.csv").open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f, lineterminator="\n")
            w.writerow(["image_id", "decision"] + (["score"] if score is not None else []))
            for k, i in enumerate(ids):
                w.writerow([i, int(dec[k])] + ([f"{score[k]:.6f}"] if score is not None else []))
        res = E.evaluate({i: int(dec[k]) for k, i in enumerate(ids)},
                         None if score is None else {i: float(score[k]) for k, i in enumerate(ids)},
                         manifest, a.bootstrap, SEED)
        res.update(name=name, split="fresh", corpus=corpus.name)
        (out / f"{name}_fresh.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
        (out / f"{name}_fresh.md").write_text(E.markdown(name, "fresh", res), encoding="utf-8")
        index[name] = {k: res["overall"][k]["value"] for k in ("fpr", "recall", "precision")} | \
            {f"recall_{c}": res["flag_rate_by_category"][c]["value"] for c in ("C1", "C2", "C3", "C4")}

    def dec(n):
        return systems[n][0].astype(int)
    h1 = paired(dec("A5_perCheck_OCR"), dec("A4_logistic_OCR"), y, persons, a.bootstrap, SEED)
    sec = {"(a) A4_logistic_GT vs visual": paired(dec("A4_logistic_GT"), dec("visual"), y, persons, a.bootstrap, SEED),
           "(b) A4_logistic_OCR vs visual": paired(dec("A4_logistic_OCR"), dec("visual"), y, persons, a.bootstrap, SEED),
           "(c) A4_logistic_OCR_at_FPR_of_rules_OCR vs rules_OCR":
               paired(dec("A4_logistic_OCR_at_FPR_of_rules_OCR"), dec("rules_OCR"), y, persons, a.bootstrap, SEED)}
    order = sorted(sec, key=lambda k: sec[k]["p_two_sided"])
    running = 0.0
    for rank, k in enumerate(order):
        running = max(running, min(1.0, (len(order) - rank) * sec[k]["p_two_sided"]))
        sec[k]["p_holm"] = running
    h1_ok = h1["recall_ci"][0] > 0
    like_for_like = h1["fpr_diff"] <= 0.02

    pct = lambda v: f"{100 * v:+.1f}"  # noqa: E731
    lines = ["# Fresh confirmatory test (Amendment A6, DECISIONS.md Section 20)", "",
             f"Corpus `{corpus.name}`: {len(ids)} images, {len(set(persons))} people, never used before. "
             f"All parameters frozen; nothing fitted. Paired person-clustered bootstrap, B = {a.bootstrap}.", "",
             "## H1 (primary): A5 vs A4, OCR text, frozen 5%-FPR thresholds", "",
             f"- Recall difference A5 − A4: {pct(h1['recall_diff'])} points, 95% CI "
             f"[{pct(h1['recall_ci'][0])}, {pct(h1['recall_ci'][1])}]",
             f"- FPR difference A5 − A4: {pct(h1['fpr_diff'])} points, 95% CI "
             f"[{pct(h1['fpr_ci'][0])}, {pct(h1['fpr_ci'][1])}]",
             f"- **H1 {'supported' if h1_ok else 'not supported'}** (CI above 0: {h1_ok}); "
             f"FPR increase at most 2 points: {like_for_like}.", "",
             "## Secondary (Holm-corrected over three)", "",
             "| Comparison | Recall diff [95% CI] | FPR diff [95% CI] | p (Holm) |", "|---|---|---|---|"]
    for k in sec:
        d = sec[k]
        lines.append(f"| {k} | {pct(d['recall_diff'])} [{pct(d['recall_ci'][0])}, {pct(d['recall_ci'][1])}] | "
                     f"{pct(d['fpr_diff'])} [{pct(d['fpr_ci'][0])}, {pct(d['fpr_ci'][1])}] | {d['p_holm']:.4f} |")
    cols = ["fpr", "recall", "precision", "recall_C1", "recall_C2", "recall_C3", "recall_C4"]
    lines += ["", "## All systems (fresh set)", "", "| System | " + " | ".join(cols) + " |",
              "|---|" + "---|" * len(cols)]
    lines += [f"| {n} | " + " | ".join(f"{v[c]:.3f}" for c in cols) + " |" for n, v in index.items()]
    (out / "confirmatory.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (out / "confirmatory.json").write_text(json.dumps({"H1": h1, "H1_supported": h1_ok,
                                                        "H1_like_for_like": like_for_like,
                                                        "secondary": sec, "systems": index}, indent=2),
                                           encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
