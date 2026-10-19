"""Tests for evaluate.py on the real frozen manifest (no images needed).

    python experiments/test_evaluate.py
"""
import csv
import sys
import tempfile
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import evaluate as E  # noqa: E402

M = E.load_manifest()
SPLIT = "val"
IDS = sorted(i for i, r in M.items() if r["split"] == SPLIT)
TMP = Path(tempfile.mkdtemp())


def write(rows, cols):
    p = TMP / f"p{np.random.randint(1e9)}.csv"
    with p.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(cols)
        w.writerows(rows)
    return p


def run(rows, cols=("image_id", "decision"), cats=E.CATS, thr=None):
    dec, score = E.load_predictions(write(rows, cols), M, SPLIT, cats, thr)
    return E.evaluate(dec, score, M, B=200, seed=1)


def expect_error(rows, cols=("image_id", "decision"), cats=E.CATS, thr=None, text=""):
    try:
        E.load_predictions(write(rows, cols), M, SPLIT, cats, thr)
    except E.EvalError as e:
        assert text in str(e), (text, str(e))
        return
    raise AssertionError(f"expected an error containing {text!r}")


label = {i: int(M[i]["label"]) for i in IDS}
n_pos, n_neg = sum(label.values()), len(IDS) - sum(label.values())

# 1. perfect predictor
r = run([(i, label[i]) for i in IDS])
o = r["overall"]
assert o["recall"]["value"] == 1 and o["fpr"]["value"] == 0 and o["precision"]["value"] == 1
assert o["f1"]["value"] == 1 and o["confusion"] == {"TP": n_pos, "FP": 0, "TN": n_neg, "FN": 0}
assert r["bootstrap_ci_95"]["recall"]["lo"] == 1.0 and r["bootstrap_ci_95"]["n_persons"] == 45

# 2. all flagged: recall 1, FPR 1, precision = prevalence
r = run([(i, 1) for i in IDS])
assert r["overall"]["fpr"]["value"] == 1
assert abs(r["overall"]["precision"]["value"] - n_pos / len(IDS)) < 1e-12

# 3. nothing flagged: precision undefined (null, not 0), recall 0
r = run([(i, 0) for i in IDS])
assert r["overall"]["precision"]["value"] is None and "undefined" in r["overall"]["precision"]
assert r["overall"]["recall"]["value"] == 0 and r["overall"]["f1"]["value"] is None

# 4. random scores: AUROC near 0.5, threshold turns scores into decisions
rng = np.random.default_rng(0)
r = run([(i, rng.random()) for i in IDS], cols=("image_id", "score"), thr=0.5)
assert 0.4 < r["threshold_free"]["all_forged_vs_C0"]["auroc"] < 0.6
assert 0.4 < r["overall"]["fpr"]["value"] < 0.6

# 5. rule-only predictor from the manifest reproduces the known detection recall
r = run([(i, int(M[i]["rule_gt_verdict"] == "FAIL")) for i in IDS])
assert r["overall"]["fpr"]["value"] == 0
assert r["rule_coverage_recall"]["value"] == 1.0
assert abs(r["detection_recall"]["value"] - 0.375) < 1e-12           # 405 / 1080

# 6. category subset (C0 vs C1 only)
c01 = [i for i in IDS if M[i]["forgery_category"] in ("C0", "C1")]
r = run([(i, label[i]) for i in c01], cats=("C0", "C1"))
assert r["n_images"] == 810 and r["c1_recall_fine_trace"]["value"] == 1

# 7. errors
good = [(i, 0) for i in IDS]
expect_error(good[:-1], text="have no prediction")
expect_error(good + [good[0]], text="duplicate")
expect_error(good + [("NOT_AN_ID", 0)], text="unknown")
test_id = next(i for i, x in M.items() if x["split"] == "test")
expect_error(good + [(test_id, 0)], text="belongs to split test")
expect_error([(i, 2) for i in IDS], text="not 0 or 1")
expect_error([(i, 0.3) for i in IDS], cols=("image_id", "score"), text="without --threshold")
expect_error([(i, "nan") for i in IDS], cols=("image_id", "score"), thr=0.5, text="not finite")
expect_error([(i, 0, 1 - label[i]) for i in IDS], cols=("image_id", "decision", "label"),
             text="manifest says")
expect_error([(i, 0) for i in IDS], cols=("id", "decision"), text="no image_id")
expect_error([(i, 0) for i in c01] + [(IDS[0], 0)] if M[IDS[0]]["forgery_category"] not in ("C0", "C1")
             else [(i, 0) for i in c01] + [(next(i for i in IDS if M[i]["forgery_category"] == "C2"), 0)],
             cats=("C0", "C1"), text="outside")
print("PASS: all evaluate.py tests")
