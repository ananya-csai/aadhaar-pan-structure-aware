# perCheck_OCR_at_FPR_of_OR_OCR — test split

1620 images, 45 people. Percentages; 95% CIs from a person-clustered bootstrap (B = 10000).

| Metric | Value | 95% CI |
|---|---|---|
| Detection recall (all forged) | 53.5 | [51.0, 56.1] |
| FPR (C0) | 15.4 | [12.2, 18.9] |
| Precision | 87.4 | [85.2, 89.7] |
| F1 | 0.664 | |
| Rule-coverage recall (expected_rule = FAIL) | 98.3 | |

Confusion: TP 578, FP 83, TN 457, FN 502

Flag rate by document type and category (on C0 this is the FPR):

| | C0 | C1 | C2 | C3 | C4 |
|---|---|---|---|---|---|
| aadhaar | 8.9 | 37.0 | 100.0 | 8.1 | 8.1 |
| pan | 21.9 | 54.8 | 99.3 | 95.6 | 25.2 |

C1 recall by edit type: local_recompression 59.1, resample_patch 10.5, font_substitution 75.0, field_displacement 37.3, patch_splice 55.0
C1 recall, fine-trace 36.6, coarse 53.7

| Threshold-free | AUROC | PR-AUC |
|---|---|---|
| all_forged_vs_C0 | 0.720 | 0.849 |
| C1_vs_C0 | 0.708 | 0.597 |
| C2_vs_C0 | 0.957 | 0.864 |
| C3_vs_C0 | 0.707 | 0.628 |
| C4_vs_C0 | 0.508 | 0.336 |
