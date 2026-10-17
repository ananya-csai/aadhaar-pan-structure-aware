"""Check metrics.py against scikit-learn. Needs scikit-learn (any environment).

    python experiments/e2_visual/test_metrics.py
"""
import sys
from pathlib import Path

import numpy as np
from sklearn.metrics import average_precision_score, roc_auc_score

sys.path.insert(0, str(Path(__file__).resolve().parent))
from metrics import average_precision, roc_auc  # noqa: E402

rng = np.random.default_rng(0)
cases = 0
for n in (2, 3, 10, 50, 810):
    for _ in range(200):
        y = rng.integers(0, 2, n)
        if y.min() == y.max():
            continue
        for s in (rng.normal(size=n),                      # no ties
                  rng.integers(0, 4, n).astype(float),     # heavy ties
                  np.round(rng.normal(size=n), 1)):        # some ties
            assert abs(average_precision(y, s) - average_precision_score(y, s)) < 1e-12
            assert abs(roc_auc(y, s) - roc_auc_score(y, s)) < 1e-12
            cases += 1
y = np.array([0, 0, 1, 1]); assert average_precision(y, [0, 0, 1, 1]) == 1.0 == roc_auc(y, [0, 0, 1, 1])
assert roc_auc(y, [1, 1, 0, 0]) == 0.0
assert roc_auc(y, [0.5] * 4) == 0.5
for bad in (([0, 0], [1, 2]), ([0, 1], [1, np.nan]), ([0, 2], [1, 2])):
    try:
        average_precision(*bad)
        raise AssertionError("expected ValueError")
    except ValueError:
        pass
print(f"PASS: {cases} random cases match scikit-learn, plus edge cases.")
