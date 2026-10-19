"""Shared evaluation harness (roadmap Step 4). Every system in the paper is scored here.

Input: a CSV with one row per image of the evaluated split:
    image_id, and either `decision` (0/1, 1 = flagged as forged) or `score`
    (higher = more likely forged; give --threshold to turn it into a decision).

Checks (any failure stops the run):
    exactly one row per image of the split and category set; no unknown,
    duplicate or other-split image_ids; decisions in {0, 1}; scores finite;
    if the file has label / split / forgery_category columns they must match
    the manifest.

Metrics (all from dataset/data/v1/manifest.csv; label 1 = any forgery C1-C4):
    confusion matrix, precision, recall, F1, FPR, FNR, specificity;
    detection recall      = flagged / all forged images (C1-C4)
    rule-coverage recall  = flagged / images the rules are designed to catch
                            (expected_rule == FAIL); a check of the rule
                            implementation, not a detection metric;
    flag rate per document type x category (on C0 this is the FPR);
    C0 FPR per document type x quality tier;
    C1 recall per c1_op and per group (fine-trace / coarse);
    AUROC and PR-AUC when scores are given (all forged, and C0 vs each category);
    person-clustered bootstrap 95% CIs (people resampled with their images).
Undefined values (0/0) are reported as null with the reason, never as 0.

    python experiments/evaluate.py --pred P.csv --split test --name rules_gt --out experiments/results
    python experiments/evaluate.py --pred S.csv --split val --threshold 0.53 --name visual --out ...
"""

import argparse
import csv
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "experiments" / "e2_visual"))
from metrics import average_precision, roc_auc  # noqa: E402

MANIFEST = ROOT / "dataset" / "data" / "v1" / "manifest.csv"
CATS = ("C0", "C1", "C2", "C3", "C4")
DOCS = ("aadhaar", "pan")
TIERS = ("clean", "mild", "severe")
FINE = ("local_recompression", "resample_patch")
COARSE = ("font_substitution", "field_displacement", "patch_splice")


class EvalError(ValueError):
    pass


def load_manifest(path=MANIFEST):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return {r["image_id"]: r for r in csv.DictReader(f)}


def load_predictions(path, manifest, split, categories, threshold=None):
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        cols = reader.fieldnames or []
        rows = list(reader)
    if "image_id" not in cols:
        raise EvalError("prediction file has no image_id column")
    has_dec, has_score = "decision" in cols, "score" in cols
    if not (has_dec or has_score):
        raise EvalError("prediction file needs a decision or a score column")
    if has_score and not has_dec and threshold is None:
        raise EvalError("scores given without --threshold: decisions are undefined")

    expected = {i for i, r in manifest.items()
                if r["split"] == split and r["forgery_category"] in categories}
    seen = set()
    dec, score = {}, {}
    for r in rows:
        iid = r["image_id"]
        if iid in seen:
            raise EvalError(f"duplicate image_id {iid}")
        seen.add(iid)
        if iid not in manifest:
            raise EvalError(f"unknown image_id {iid}")
        m = manifest[iid]
        if m["split"] != split:
            raise EvalError(f"{iid} belongs to split {m['split']}, not {split}")
        if m["forgery_category"] not in categories:
            raise EvalError(f"{iid} is {m['forgery_category']}, outside {categories}")
        for col in ("label", "split", "forgery_category", "doc_type"):
            if col in cols and r[col] != m[col]:
                raise EvalError(f"{iid}: {col}={r[col]} but manifest says {m[col]}")
        if has_score:
            try:
                s = float(r["score"])
            except ValueError:
                raise EvalError(f"{iid}: score {r['score']!r} is not a number")
            if not math.isfinite(s):
                raise EvalError(f"{iid}: score is not finite")
            score[iid] = s
        if has_dec:
            if r["decision"] not in ("0", "1"):
                raise EvalError(f"{iid}: decision {r['decision']!r} is not 0 or 1")
            dec[iid] = int(r["decision"])
        else:
            dec[iid] = int(score[iid] >= threshold)
    missing = expected - seen
    if missing:
        raise EvalError(f"{len(missing)} image(s) of the split have no prediction, "
                        f"e.g. {sorted(missing)[:3]}")
    return dec, (score if has_score else None)


def ratio(num, den, why):
    return {"value": num / den, "num": int(num), "den": int(den)} if den else \
        {"value": None, "num": int(num), "den": 0, "undefined": why}


def core(y, f):
    tp = int(((y == 1) & (f == 1)).sum())
    fp = int(((y == 0) & (f == 1)).sum())
    tn = int(((y == 0) & (f == 0)).sum())
    fn = int(((y == 1) & (f == 0)).sum())
    prec = ratio(tp, tp + fp, "nothing flagged")
    rec = ratio(tp, tp + fn, "no forged images")
    p, r = prec["value"], rec["value"]
    f1 = {"value": None, "undefined": "precision or recall undefined"} if p is None or r is None \
        else {"value": 0.0 if p + r == 0 else 2 * p * r / (p + r)}
    return {"confusion": {"TP": tp, "FP": fp, "TN": tn, "FN": fn},
            "precision": prec, "recall": rec, "f1": f1,
            "fpr": ratio(fp, fp + tn, "no C0 images"),
            "fnr": ratio(fn, fn + tp, "no forged images"),
            "specificity": ratio(tn, tn + fp, "no C0 images")}


def bootstrap(ids, manifest, f, y, B, seed):
    persons = sorted({manifest[i]["person_id"] for i in ids})
    by_p = defaultdict(list)
    for k, i in enumerate(ids):
        by_p[manifest[i]["person_id"]].append(k)
    rng = np.random.default_rng(seed)
    stats = {"recall": [], "fpr": [], "precision": []}
    for _ in range(B):
        idx = np.concatenate([by_p[p] for p in rng.choice(persons, len(persons), replace=True)])
        yy, ff = y[idx], f[idx]
        tp, fp = ((yy == 1) & (ff == 1)).sum(), ((yy == 0) & (ff == 1)).sum()
        npos, nneg = (yy == 1).sum(), (yy == 0).sum()
        if npos:
            stats["recall"].append(tp / npos)
        if nneg:
            stats["fpr"].append(fp / nneg)
        if tp + fp:
            stats["precision"].append(tp / (tp + fp))
    return {k: ({"lo": float(np.percentile(v, 2.5)), "hi": float(np.percentile(v, 97.5)),
                 "n_resamples": len(v)} if v else None) for k, v in stats.items()} | \
        {"n_persons": len(persons), "B": B, "seed": seed}


def evaluate(dec, score, manifest, B=2000, seed=0):
    ids = sorted(dec)
    m = [manifest[i] for i in ids]
    y = np.array([int(r["label"]) for r in m])
    f = np.array([dec[i] for i in ids])
    cat = np.array([r["forgery_category"] for r in m])
    doc = np.array([r["doc_type"] for r in m])
    tier = np.array([r["quality_tier"] for r in m])
    op = np.array([r["c1_op"] for r in m])
    exp_fail = np.array([r["expected_rule"] == "FAIL" for r in m])

    out = {"n_images": len(ids), "overall": core(y, f)}
    out["detection_recall"] = out["overall"]["recall"]
    out["rule_coverage_recall"] = ratio(int((f[exp_fail] == 1).sum()), int(exp_fail.sum()),
                                        "no image with expected_rule == FAIL")
    out["by_doc"] = {d: core(y[doc == d], f[doc == d]) for d in DOCS if (doc == d).any()}
    out["flag_rate"] = {f"{d}/{c}": ratio(int(f[(doc == d) & (cat == c)].sum()),
                                          int(((doc == d) & (cat == c)).sum()), "empty cell")
                        for d in DOCS for c in CATS if ((doc == d) & (cat == c)).any()}
    out["flag_rate_by_category"] = {c: ratio(int(f[cat == c].sum()), int((cat == c).sum()),
                                             "empty") for c in CATS if (cat == c).any()}
    out["c0_fpr_by_tier"] = {f"{d}/{t}": ratio(int(f[(cat == "C0") & (doc == d) & (tier == t)].sum()),
                                               int(((cat == "C0") & (doc == d) & (tier == t)).sum()),
                                               "empty cell")
                             for d in DOCS for t in TIERS if ((cat == "C0") & (doc == d)).any()}
    c1 = cat == "C1"
    out["c1_recall_by_op"] = {o: ratio(int(f[c1 & (op == o)].sum()), int((c1 & (op == o)).sum()),
                                       "no images") for o in FINE + COARSE if (c1 & (op == o)).any()}
    for g, ops in (("fine_trace", FINE), ("coarse", COARSE)):
        mask = c1 & np.isin(op, ops)
        out[f"c1_recall_{g}"] = ratio(int(f[mask].sum()), int(mask.sum()), "no images")
    out["c1_recall_by_tier"] = {t: ratio(int(f[c1 & (tier == t)].sum()), int((c1 & (tier == t)).sum()),
                                         "no images") for t in TIERS if (c1 & (tier == t)).any()}
    if score is not None:
        s = np.array([score[i] for i in ids])
        thr = {}
        if (y == 1).any() and (y == 0).any():
            thr["all_forged_vs_C0"] = {"auroc": roc_auc(y, s), "pr_auc": average_precision(y, s)}
        for c in CATS[1:]:
            mask = (cat == "C0") | (cat == c)
            if (cat == c).any() and (cat == "C0").any():
                thr[f"{c}_vs_C0"] = {"auroc": roc_auc(y[mask], s[mask]),
                                     "pr_auc": average_precision(y[mask], s[mask])}
        out["threshold_free"] = thr
    out["bootstrap_ci_95"] = bootstrap(ids, manifest, f, y, B, seed)
    return out


def v(x, pct=True):
    return "n/a" if x["value"] is None else (f"{100 * x['value']:.1f}" if pct else f"{x['value']:.3f}")


def markdown(name, split, res):
    o, ci = res["overall"], res["bootstrap_ci_95"]
    L = [f"# {name} — {split} split", "",
         f"{res['n_images']} images, {ci['n_persons']} people. Percentages; 95% CIs from a "
         f"person-clustered bootstrap (B = {ci['B']}).", "",
         "| Metric | Value | 95% CI |", "|---|---|---|"]
    for k, label in (("recall", "Detection recall (all forged)"), ("fpr", "FPR (C0)"),
                     ("precision", "Precision")):
        c = ci[k]
        L.append(f"| {label} | {v(o[k])} | " +
                 (f"[{100 * c['lo']:.1f}, {100 * c['hi']:.1f}]" if c else "n/a") + " |")
    L += [f"| F1 | {v(o['f1'], False)} | |",
          f"| Rule-coverage recall (expected_rule = FAIL) | {v(res['rule_coverage_recall'])} | |", "",
          "Confusion: " + ", ".join(f"{k} {n}" for k, n in o["confusion"].items()), "",
          "Flag rate by document type and category (on C0 this is the FPR):", "",
          "| | " + " | ".join(CATS) + " |", "|---|" + "---|" * len(CATS)]
    for d in DOCS:
        L.append(f"| {d} | " + " | ".join(v(res["flag_rate"][f"{d}/{c}"]) if f"{d}/{c}" in res["flag_rate"]
                                          else "–" for c in CATS) + " |")
    if res["c1_recall_by_op"]:
        L += ["", "C1 recall by edit type: " + ", ".join(f"{k} {v(x)}" for k, x in res["c1_recall_by_op"].items()),
              f"C1 recall, fine-trace {v(res['c1_recall_fine_trace'])}, coarse {v(res['c1_recall_coarse'])}"]
    if "threshold_free" in res:
        L += ["", "| Threshold-free | AUROC | PR-AUC |", "|---|---|---|"]
        L += [f"| {k} | {x['auroc']:.3f} | {x['pr_auc']:.3f} |" for k, x in res["threshold_free"].items()]
    return "\n".join(L) + "\n"


def _rel(path):
    p = Path(path).resolve()
    try:
        return p.relative_to(ROOT).as_posix()
    except ValueError:
        return p.name


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pred", required=True)
    ap.add_argument("--split", required=True, choices=["train", "val", "test"])
    ap.add_argument("--categories", default=",".join(CATS))
    ap.add_argument("--threshold", type=float)
    ap.add_argument("--name", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--bootstrap", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args(argv)
    cats = tuple(c.strip() for c in a.categories.split(","))
    manifest = load_manifest()
    try:
        dec, score = load_predictions(a.pred, manifest, a.split, cats, a.threshold)
    except EvalError as e:
        sys.exit(f"STOP: {e}")
    res = evaluate(dec, score, manifest, a.bootstrap, a.seed)
    res.update(name=a.name, split=a.split, categories=list(cats), threshold=a.threshold,
               prediction_file=_rel(a.pred))
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{a.name}_{a.split}.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
    md = markdown(a.name, a.split, res)
    (out / f"{a.name}_{a.split}.md").write_text(md, encoding="utf-8")
    print(md)


if __name__ == "__main__":
    main()
