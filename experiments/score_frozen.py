"""Roadmap Step 15: apply every frozen parameter to one split and score all systems.

Nothing is fitted here. The script reads:
  experiments/e2_visual/frozen/{tiles,base}_calibration.json   per-seed temperatures, t_v
  experiments/e2_visual/runs/<model>/seed<k>/scores_*.csv       per-seed logits
  experiments/fusion/frozen_fusion.json                         fusion coefficients, thresholds
  dataset/data/v1/manifest.csv                                  rule verdicts (GT and OCR)
and writes one prediction file per system plus its evaluate.py report.

    python experiments/score_frozen.py --split val    # check: must reproduce validation_report.md
    python experiments/score_frozen.py --split test   # the single test scoring (Gate G2 required)

For --split test the script refuses to run unless the tag `frozen-before-test`
exists, the fusion file is committed at that tag, and every scores_test.csv
still has the SHA-256 recorded in its run's summary.json and in the calibration
file (proof that the sealed files were not changed after freezing).
"""
import argparse
import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "experiments"))
import evaluate as E  # noqa: E402

FROZEN_VIS = ROOT / "experiments" / "e2_visual" / "frozen"
RUNS = {"tiles": ROOT / "experiments" / "e2_visual" / "runs" / "native_tiles",
        "base": ROOT / "experiments" / "e2_visual" / "runs" / "768x512"}
FUSION = ROOT / "experiments" / "fusion" / "frozen_fusion.json"
TAG = "frozen-before-test"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)


def check_gate():
    if git("rev-parse", "-q", "--verify", f"refs/tags/{TAG}").returncode != 0:
        sys.exit(f"STOP: tag {TAG} does not exist; Gate G2 is not passed.")
    rel = FUSION.relative_to(ROOT).as_posix()
    if git("cat-file", "-e", f"{TAG}:{rel}").returncode != 0:
        sys.exit(f"STOP: {rel} is not committed at {TAG}.")
    if git("diff", "--quiet", TAG, "--", rel, "experiments/e2_visual/frozen").returncode != 0:
        sys.exit("STOP: frozen calibration or fusion files differ from the tagged versions.")


def ensemble(model, split, manifest, ids):
    cal = json.loads((FROZEN_VIS / f"{model}_calibration.json").read_text(encoding="utf-8"))
    fname = "scores_test.csv" if split == "test" else "scores_trainval.csv"
    probs = []
    for s in cal["seeds"]:
        run = RUNS[model] / f"seed{s['seed']}"
        path = run / fname
        recorded = json.loads((run / "summary.json").read_text(encoding="utf-8"))
        key = "scores_test_sha256" if split == "test" else "scores_trainval_sha256"
        if sha(path) != recorded[key] or sha(path) != s[key]:
            sys.exit(f"STOP: {path} does not match its recorded SHA-256.")
        with path.open(newline="", encoding="utf-8") as f:
            z = {r["image_id"]: float(r["logit"]) for r in csv.DictReader(f)}
        missing = set(ids) - set(z)
        if missing:
            sys.exit(f"STOP: {path} lacks {len(missing)} images of the {split} split.")
        t = s["temperature"]
        probs.append(np.array([1 / (1 + np.exp(-z[i] / t)) for i in ids]))
    return np.mean(probs, axis=0), cal["operating_point"]["threshold"]


def logit(p):
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return np.log(p / (1 - p))


def write_pred(path, ids, decision, score=None):
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["image_id", "decision"] + (["score"] if score is not None else []))
        for k, i in enumerate(ids):
            w.writerow([i, int(decision[k])] + ([f"{score[k]:.6f}"] if score is not None else []))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", required=True, choices=["val", "test"])
    ap.add_argument("--bootstrap", type=int, default=10000)
    a = ap.parse_args()
    if a.split == "test":
        check_gate()
    out = ROOT / "experiments" / "results" / a.split
    out.mkdir(parents=True, exist_ok=True)

    manifest = E.load_manifest()
    ids = sorted(i for i, r in manifest.items() if r["split"] == a.split)
    pan = np.array([manifest[i]["doc_type"] == "pan" for i in ids], dtype=float)
    fusion = json.loads(FUSION.read_text(encoding="utf-8"))

    systems = {}
    p_v, t_v = ensemble("tiles", a.split, manifest, ids)
    if abs(t_v - fusion["visual_threshold"]) > 1e-12:
        sys.exit("STOP: fusion file and calibration file disagree on the visual threshold.")
    vis = p_v >= t_v
    systems["visual"] = (vis, p_v)
    p_b, t_b = ensemble("base", a.split, manifest, ids)
    systems["visual_base_comparison"] = (p_b >= t_b, p_b)

    for cond, c in fusion["conditions"].items():
        r = np.array([manifest[i][c["rule_column"]] == "FAIL" for i in ids], dtype=float)
        lg = c["logistic"]
        s = 1 / (1 + np.exp(-(lg["intercept"] + lg["coef"][0] * logit(p_v)
                              + lg["coef"][1] * r + lg["coef"][2] * r * pan)))
        systems[f"rules_{cond}"] = (r == 1, None)
        systems[f"OR_{cond}"] = (vis | (r == 1), None)
        systems[f"AND_{cond}"] = (vis & (r == 1), None)
        systems[f"logistic_{cond}"] = (s >= lg["threshold"], s)
        for ref, m in lg.get("matched_fpr_thresholds", {}).items():
            systems[f"logistic_{cond}_at_FPR_of_{ref}"] = (s >= m["threshold"], s)

    index = {}
    for name, (dec, score) in systems.items():
        pred = out / f"{name}_predictions.csv"
        write_pred(pred, ids, dec, score)
        E.main(["--pred", str(pred), "--split", a.split, "--name", name, "--out", str(out),
                "--bootstrap", str(a.bootstrap), "--seed", "0"])
        res = json.loads((out / f"{name}_{a.split}.json").read_text(encoding="utf-8"))
        index[name] = {k: res["overall"][k]["value"] for k in ("fpr", "recall", "precision")} | \
            {f"recall_{c}": res["flag_rate_by_category"][c]["value"] for c in ("C1", "C2", "C3", "C4")}
    (out / "summary.json").write_text(json.dumps(index, indent=2), encoding="utf-8")
    cols = ["fpr", "recall", "precision", "recall_C1", "recall_C2", "recall_C3", "recall_C4"]
    lines = [f"| System ({a.split}) | " + " | ".join(cols) + " |", "|---|" + "---|" * len(cols)]
    lines += [f"| {n} | " + " | ".join("n/a" if v[c] is None else f"{v[c]:.3f}" for c in cols) + " |"
              for n, v in index.items()]
    (out / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
