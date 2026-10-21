"""Amendment A5 (DECISIONS.md Section 19): post-hoc per-check fusion.

Fitted and thresholded on validation only, exactly as A4, but with one 0/1
input per rule check and document type instead of a single "any check failed"
input. Applied once to the test split. A4 remains the primary result.

    python experiments/fusion/fuse_per_check.py
Writes experiments/fusion/frozen_fusion_A5.json, experiments/results/val_A5/
and experiments/results/test_posthoc_A5/.
"""
import csv
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments"))
sys.path.insert(0, str(ROOT / "experiments" / "e2_visual"))
sys.path.insert(0, str(ROOT / "experiments" / "fusion"))
import evaluate as E  # noqa: E402
from calibrate_visual import operating_point  # noqa: E402
from fuse import fit_logistic, logit  # noqa: E402
from score_frozen import ensemble, write_pred  # noqa: E402

FEATURES = [("aadhaar", "format_check"), ("aadhaar", "checksum_check"),
            ("pan", "format_check"), ("pan", "category_check"), ("pan", "semantic_check")]
TARGET_FPR = 0.05
OUT = ROOT / "experiments" / "fusion"


def indicators(rules, ids, cond):
    X = np.zeros((len(ids), len(FEATURES)))
    for i, image_id in enumerate(ids):
        r = rules[image_id]
        failed = set(filter(None, r[f"{cond}_failed_checks"].split("|")))
        for j, (doc, check) in enumerate(FEATURES):
            X[i, j] = float(r["doc_type"] == doc and check in failed)
    return X


def score(z_v, X, w):
    return 1 / (1 + np.exp(-(w[0] + w[1] * z_v + X @ w[2:])))


def main():
    manifest = E.load_manifest()
    with (ROOT / "experiments" / "rules" / "rule_decisions.csv").open(newline="", encoding="utf-8") as f:
        rules = {r["image_id"]: r for r in csv.DictReader(f)}
    split_ids = {s: sorted(i for i, r in manifest.items() if r["split"] == s) for s in ("val", "test")}
    y_val = np.array([int(manifest[i]["label"]) for i in split_ids["val"]])
    zv = {s: logit(ensemble("tiles", s, manifest, split_ids[s])[0]) for s in ("val", "test")}
    a4 = json.loads((OUT / "frozen_fusion.json").read_text(encoding="utf-8"))

    frozen = {"amendment": "A5 (post-hoc)", "features": ["z_v"] + [f"{d}:{c}" for d, c in FEATURES],
              "C": 1.0, "conditions": {}}
    for cond, tag in (("gt", "GT"), ("ocr", "OCR")):
        Xv = indicators(rules, split_ids["val"], cond)
        w = fit_logistic(np.column_stack([zv["val"], Xv]), y_val.astype(float))
        s_val = score(zv["val"], Xv, w)
        t5, _, _ = operating_point(s_val, y_val, TARGET_FPR)
        thresholds = {"5pct": float(t5)}
        for ref, m in a4["conditions"][tag]["logistic"].get("matched_fpr_thresholds", {}).items():
            thresholds[f"at_FPR_of_{ref}"] = float(operating_point(s_val, y_val, m["target_fpr"])[0])
        frozen["conditions"][tag] = {"intercept": float(w[0]), "coef": [float(v) for v in w[1:]],
                                     "thresholds": thresholds}
        for split in ("val", "test"):
            X = indicators(rules, split_ids[split], cond)
            s = score(zv[split], X, w)
            out = ROOT / "experiments" / "results" / ("val_A5" if split == "val" else "test_posthoc_A5")
            out.mkdir(parents=True, exist_ok=True)
            for tname, t in thresholds.items():
                name = f"perCheck_{tag}" + ("" if tname == "5pct" else f"_{tname}")
                pred = out / f"{name}_predictions.csv"
                write_pred(pred, split_ids[split], s >= t, s)
                E.main(["--pred", str(pred), "--split", split, "--name", name, "--out", str(out),
                        "--bootstrap", "10000", "--seed", "0"])
    frozen["note"] = "Fitted and thresholded on validation only; applied to test once (post-hoc, DECISIONS.md 19)."
    (OUT / "frozen_fusion_A5.json").write_text(json.dumps(frozen, indent=2), encoding="utf-8")
    print(json.dumps(frozen, indent=2))


if __name__ == "__main__":
    main()
