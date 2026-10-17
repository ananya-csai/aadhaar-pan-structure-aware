"""Threshold-free metrics used for early stopping (numpy only, no scikit-learn).

average_precision matches sklearn.metrics.average_precision_score (step-wise,
ties grouped by threshold). roc_auc matches sklearn.metrics.roc_auc_score
(Mann-Whitney U with average ranks for ties). Both are checked against
scikit-learn in test_metrics.py.
"""

import numpy as np


def _check(y, s):
    y = np.asarray(y, dtype=np.int64).ravel()
    s = np.asarray(s, dtype=np.float64).ravel()
    if y.shape != s.shape:
        raise ValueError("labels and scores differ in length")
    if not np.isin(y, (0, 1)).all():
        raise ValueError("labels must be 0/1")
    if not np.isfinite(s).all():
        raise ValueError("scores contain NaN or inf")
    n_pos = int(y.sum())
    if n_pos == 0 or n_pos == len(y):
        raise ValueError("need both classes")
    return y, s, n_pos


def average_precision(y, s):
    y, s, n_pos = _check(y, s)
    order = np.argsort(-s, kind="mergesort")
    y, s = y[order], s[order]
    last = np.r_[np.flatnonzero(np.diff(s)), len(s) - 1]     # last index of each distinct score
    tp = np.cumsum(y)[last]
    fp = (last + 1) - tp
    precision = tp / (tp + fp)
    recall = tp / n_pos
    recall_prev = np.r_[0.0, recall[:-1]]
    return float(np.sum((recall - recall_prev) * precision))


def roc_auc(y, s):
    y, s, n_pos = _check(y, s)
    n_neg = len(y) - n_pos
    order = np.argsort(s, kind="mergesort")
    s_sorted = s[order]
    ranks = np.empty(len(s), dtype=np.float64)
    i = 0
    while i < len(s):                                         # average ranks for ties
        j = i
        while j + 1 < len(s) and s_sorted[j + 1] == s_sorted[i]:
            j += 1
        ranks[order[i:j + 1]] = (i + j) / 2.0 + 1.0
        i = j + 1
    u = ranks[y == 1].sum() - n_pos * (n_pos + 1) / 2.0
    return float(u / (n_pos * n_neg))
