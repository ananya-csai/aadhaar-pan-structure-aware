"""Roadmap Step 14: fusion code checked on hand-made examples with known answers,
plus consistency checks on the committed validation outputs.

    python experiments/fusion/test_fusion.py
"""
import csv
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments" / "e2_visual"))
sys.path.insert(0, str(ROOT / "experiments" / "fusion"))
from calibrate_visual import operating_point  # noqa: E402
from fuse import fit_logistic, logit  # noqa: E402

VAL = ROOT / "experiments" / "results" / "val"


def close(a, b, tol=1e-9):
    assert abs(a - b) <= tol, (a, b)


def test_operating_point_hand_made():
    # 4 negatives, 2 positives; 25% FPR allows exactly one negative to be flagged.
    p = np.array([0.1, 0.2, 0.3, 0.4, 0.9, 0.8])
    y = np.array([0, 0, 0, 0, 1, 1])
    t, fpr, rec = operating_point(p, y, 0.25)
    close(t, 0.35); close(fpr, 0.25); close(rec, 1.0)       # midway between 0.3 and 0.4
    t, fpr, rec = operating_point(p, y, 0.0)
    close(t, 0.6); close(fpr, 0.0); close(rec, 1.0)         # midway between 0.4 and 0.8
    # Tied negatives: flagging one would flag both, so neither may be flagged at 50%.
    p = np.array([0.5, 0.5, 0.5, 0.9])
    y = np.array([0, 0, 1, 1])
    t, fpr, rec = operating_point(p, y, 0.5)
    close(t, 0.7); close(fpr, 0.0); close(rec, 0.5)


def test_logistic_fit_is_optimal():
    # At the optimum of the penalised loss the gradient is zero.
    rng = np.random.default_rng(0)
    X = np.column_stack([rng.normal(size=200), rng.integers(0, 2, 200), rng.integers(0, 2, 200)])
    y = (X[:, 0] + 2 * X[:, 1] + rng.normal(size=200) > 1).astype(float)
    w = fit_logistic(X, y, C=1.0)
    Xb = np.hstack([np.ones((200, 1)), X])
    g = Xb.T @ (1 / (1 + np.exp(-Xb @ w)) - y)
    g[1:] += w[1:]
    assert np.abs(g).max() / len(y) < 1e-5, g          # per-sample gradient ~ 0
    try:                                               # same model as sklearn's default
        from sklearn.linear_model import LogisticRegression
        m = LogisticRegression(C=1.0, tol=1e-10, max_iter=10000).fit(X, y)
        assert np.allclose(np.r_[m.intercept_, m.coef_[0]], w, atol=1e-4), (m.coef_, w)
    except ImportError:
        pass
    # Penalty pulls coefficients toward zero relative to a much weaker penalty.
    w_weak = fit_logistic(X, y, C=1e6)
    assert np.linalg.norm(w[1:]) < np.linalg.norm(w_weak[1:])


def read(name):
    with (VAL / f"{name}_predictions.csv").open(newline="", encoding="utf-8") as f:
        return {r["image_id"]: r for r in csv.DictReader(f)}


def test_binary_fusion_on_validation_outputs():
    vis = read("visual")
    for cond in ("GT", "OCR"):
        rules, o, a = read(f"rules_{cond}"), read(f"OR_{cond}"), read(f"AND_{cond}")
        assert set(vis) == set(rules) == set(o) == set(a) and len(vis) == 1620
        for i in vis:
            v, r = int(vis[i]["decision"]), int(rules[i]["decision"])
            assert int(o[i]["decision"]) == (v | r), i
            assert int(a[i]["decision"]) == (v & r), i


def test_logistic_formula_on_validation_outputs():
    fusion = json.loads((ROOT / "experiments" / "fusion" / "frozen_fusion.json").read_text(encoding="utf-8"))
    vis = read("visual")
    for cond, c in fusion["conditions"].items():
        lg, rules, out = c["logistic"], read(f"rules_{cond}"), read(f"logistic_{cond}")
        for i in list(vis)[::40]:
            pan = 1.0 if "_pan_" in i else 0.0
            r = float(rules[i]["decision"])
            z = lg["intercept"] + lg["coef"][0] * logit(np.array(float(vis[i]["score"]))) \
                + lg["coef"][1] * r + lg["coef"][2] * r * pan
            close(1 / (1 + np.exp(-z)), float(out[i]["score"]), 1e-4)   # 6-dp inputs


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
    print("PASS: all fusion tests")
