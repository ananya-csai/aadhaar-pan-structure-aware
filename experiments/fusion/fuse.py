"""Roadmap Step 14: evidence fusion, chosen and frozen on VALIDATION only (Amendment A4).

Population: all validation images, C0-C4 (1,620 images, 45 people).
Target: label (1 = any forgery C1-C4, 0 = C0).
Inputs per image:
  p_v  calibrated 5-seed `tiles` ensemble probability, computed from the per-seed
       logits and the stored temperatures by score_frozen.ensemble -- the SAME
       function that later scores the test split, so validation and test inputs
       are computed identically
  z_v  logit(p_v)
  r    rule flag: 1 if the rule verdict is FAIL, else 0, under two text conditions:
       GT  (ground-truth text, oracle)   -> manifest column rule_gt_verdict
       OCR (Tesseract text, realistic)   -> manifest column rule_ocr_verdict
  pan  1 for PAN, 0 for Aadhaar

Systems (each under GT and OCR where rules are involved):
  visual   flag if p_v >= t_v, the frozen visual threshold (Step 13)
  rules    flag if r = 1
  OR       flag if (p_v >= t_v) or r = 1
  AND      flag if (p_v >= t_v) and r = 1
  logistic s = sigmoid(w0 + w1*z_v + w2*r + w3*r*pan), L2-penalised as in
           scikit-learn's default (C = 1, intercept not penalised), fitted on
           validation; flag if s >= t_s, where t_s maximises validation recall
           subject to validation C0 FPR <= 5%.
Binary systems (rules, OR, AND) are reported at the FPR they reach; they are not
forced to 5%. For a fair comparison with each of them, the logistic score is ALSO
thresholded on validation at that system's own validation FPR ("matched-FPR"
rows). Threshold-free AUROC and PR-AUC are reported for the continuous scores. Train-split scores are never used (they are in-sample for the
visual model).

    python experiments/fusion/fuse.py
Writes experiments/fusion/frozen_fusion.json and experiments/fusion/validation_report.md.
"""

import csv
import json
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import minimize

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "experiments" / "e2_visual"))
from calibrate_visual import operating_point  # noqa: E402
sys.path.insert(0, str(ROOT / "experiments"))
from score_frozen import ensemble  # noqa: E402
from metrics import average_precision, roc_auc  # noqa: E402

FROZEN_VIS = ROOT / "experiments" / "e2_visual" / "frozen"
OUT = ROOT / "experiments" / "fusion"
CATS = ("C0", "C1", "C2", "C3", "C4")
TARGET_FPR = 0.05


def logit(p):
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return np.log(p / (1 - p))


def fit_logistic(X, y, C=1.0):
    """L2-penalised logistic regression, intercept unpenalised (sklearn default form)."""
    Xb = np.hstack([np.ones((len(X), 1)), X])

    def f(w):
        z = Xb @ w
        loss = np.sum(np.logaddexp(0, z) - y * z) + 0.5 / C * np.sum(w[1:] ** 2)
        p = 1 / (1 + np.exp(-z))
        grad = Xb.T @ (p - y)
        grad[1:] += w[1:] / C
        return loss, grad

    res = minimize(f, np.zeros(Xb.shape[1]), jac=True, method="L-BFGS-B",
                   options={"maxiter": 2000, "gtol": 1e-8})
    if not res.success:
        raise RuntimeError(f"logistic fit failed: {res.message}")
    return res.x


def features(z_v, r, pan):
    return np.column_stack([z_v, r, r * pan])


def summarise(flag, y, cat, doc):
    out = {"fpr": float(flag[y == 0].mean()), "recall_all": float(flag[y == 1].mean()),
           "n_flagged": int(flag.sum())}
    for d in ("aadhaar", "pan"):
        m = doc == d
        out[f"fpr_{d}"] = float(flag[m & (y == 0)].mean())
        for c in CATS[1:]:
            mc = m & (cat == c)
            out[f"recall_{d}_{c}"] = float(flag[mc].mean())
    for c in CATS[1:]:
        out[f"recall_{c}"] = float(flag[cat == c].mean())
    return out


def main():
    with (ROOT / "dataset" / "data" / "v1" / "manifest.csv").open(newline="", encoding="utf-8-sig") as f:
        man = {r["image_id"]: r for r in csv.DictReader(f)}
    ids = sorted(i for i, r in man.items() if r["split"] == "val")
    if len(ids) != 1620:
        raise ValueError(f"expected 1,620 validation images, found {len(ids)}")
    p_v, t_v = ensemble("tiles", "val", man, ids)
    y = np.array([int(man[i]["label"]) for i in ids])
    cat = np.array([man[i]["forgery_category"] for i in ids])
    doc = np.array([man[i]["doc_type"] for i in ids])
    pan = (doc == "pan").astype(float)
    z_v = logit(p_v)
    vis_flag = p_v >= t_v

    frozen = {"visual_threshold": t_v, "conditions": {}}
    report = {"visual": summarise(vis_flag, y, cat, doc)}
    auc = {"visual": (roc_auc(y, z_v), average_precision(y, z_v))}
    for cond, col in (("GT", "rule_gt_verdict"), ("OCR", "rule_ocr_verdict")):
        r = np.array([1.0 if man[i][col] == "FAIL" else 0.0 for i in ids])
        report[f"rules_{cond}"] = summarise(r == 1, y, cat, doc)
        report[f"OR_{cond}"] = summarise(vis_flag | (r == 1), y, cat, doc)
        report[f"AND_{cond}"] = summarise(vis_flag & (r == 1), y, cat, doc)
        X = features(z_v, r, pan)
        w = fit_logistic(X, y.astype(float))
        s = 1 / (1 + np.exp(-(w[0] + X @ w[1:])))
        t_s, _, _ = operating_point(s, y, TARGET_FPR)
        report[f"logistic_{cond}"] = summarise(s >= t_s, y, cat, doc)
        matched = {}
        for ref in (f"rules_{cond}", f"OR_{cond}"):
            ref_fpr = report[ref]["fpr"]
            if ref_fpr > TARGET_FPR:
                t_m, _, _ = operating_point(s, y, ref_fpr)
                report[f"logistic_{cond}@FPR({ref})"] = summarise(s >= t_m, y, cat, doc)
                matched[ref] = {"target_fpr": ref_fpr, "threshold": float(t_m)}
        auc[f"logistic_{cond}"] = (roc_auc(y, s), average_precision(y, s))
        frozen["conditions"][cond] = {
            "rule_column": col,
            "logistic": {"features": ["z_v", "r", "r*pan"], "intercept": float(w[0]),
                         "coef": [float(v) for v in w[1:]], "C": 1.0, "threshold": float(t_s),
                         "matched_fpr_thresholds": matched}}

    OUT.mkdir(parents=True, exist_ok=True)
    frozen["note"] = "Fitted and thresholded on validation only (1,620 images). Test untouched."
    (OUT / "frozen_fusion.json").write_text(json.dumps(frozen, indent=2), encoding="utf-8")

    cols = ["fpr", "fpr_aadhaar", "fpr_pan", "recall_all", "recall_C1", "recall_C2", "recall_C3", "recall_C4"]
    lines = ["# Fusion — validation results (Step 14)", "",
             "Validation only; 1,620 images from 45 people (540 C0, 270 of each C1–C4). "
             "Recall is the fraction of forged images flagged; FPR is the fraction of C0 flagged.", "",
             "| System | " + " | ".join(cols) + " |", "|---|" + "---|" * len(cols)]
    for name, v in report.items():
        lines.append(f"| {name} | " + " | ".join(f"{v[c]:.3f}" for c in cols) + " |")
    lines += ["", "Per document type and category:", "",
              "| System | " + " | ".join(f"{d} {c}" for d in ("aadhaar", "pan") for c in CATS[1:]) + " |",
              "|---|" + "---|" * 8]
    for name, v in report.items():
        lines.append(f"| {name} | " + " | ".join(f"{v[f'recall_{d}_{c}']:.3f}"
                                                for d in ("aadhaar", "pan") for c in CATS[1:]) + " |")
    lines += ["", "Threshold-free (all validation images, forged vs C0):", "",
              "| Score | AUROC | PR-AUC |", "|---|---|---|"]
    lines += [f"| {k} | {a:.3f} | {b:.3f} |" for k, (a, b) in auc.items()]
    (OUT / "validation_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(f"\nPASS: wrote {OUT.relative_to(ROOT)}/frozen_fusion.json and validation_report.md")


if __name__ == "__main__":
    main()
