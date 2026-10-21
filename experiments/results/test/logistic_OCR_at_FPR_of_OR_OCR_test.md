# logistic_OCR_at_FPR_of_OR_OCR — test split

1620 images, 45 people. Percentages; 95% CIs from a person-clustered bootstrap (B = 10000).

| Metric | Value | 95% CI |
|---|---|---|
| Detection recall (all forged) | 53.6 | [51.1, 56.2] |
| FPR (C0) | 15.4 | [12.2, 18.9] |
| Precision | 87.5 | [85.2, 89.7] |
| F1 | 0.665 | |
| Rule-coverage recall (expected_rule = FAIL) | 98.8 | |

Confusion: TP 579, FP 83, TN 457, FN 501

Flag rate by document type and category (on C0 this is the FPR):

| | C0 | C1 | C2 | C3 | C4 |
|---|---|---|---|---|---|
| aadhaar | 8.9 | 37.0 | 100.0 | 8.1 | 8.1 |
| pan | 21.9 | 54.1 | 100.0 | 96.3 | 25.2 |

C1 recall by edit type: local_recompression 57.6, resample_patch 10.5, font_substitution 75.0, field_displacement 37.3, patch_splice 55.0
C1 recall, fine-trace 35.8, coarse 53.7

| Threshold-free | AUROC | PR-AUC |
|---|---|---|
| all_forged_vs_C0 | 0.714 | 0.841 |
| C1_vs_C0 | 0.704 | 0.587 |
| C2_vs_C0 | 0.957 | 0.875 |
| C3_vs_C0 | 0.688 | 0.525 |
| C4_vs_C0 | 0.509 | 0.343 |
