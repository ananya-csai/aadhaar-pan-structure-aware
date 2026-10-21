# visual — test split

1620 images, 45 people. Percentages; 95% CIs from a person-clustered bootstrap (B = 10000).

| Metric | Value | 95% CI |
|---|---|---|
| Detection recall (all forged) | 13.4 | [11.3, 15.6] |
| FPR (C0) | 4.8 | [3.1, 6.5] |
| Precision | 84.8 | [79.9, 89.4] |
| F1 | 0.232 | |
| Rule-coverage recall (expected_rule = FAIL) | 5.7 | |

Confusion: TP 145, FP 26, TN 514, FN 935

Flag rate by document type and category (on C0 this is the FPR):

| | C0 | C1 | C2 | C3 | C4 |
|---|---|---|---|---|---|
| aadhaar | 5.6 | 34.8 | 6.7 | 3.7 | 3.7 |
| pan | 4.1 | 40.0 | 7.4 | 3.0 | 8.1 |

C1 recall by edit type: local_recompression 51.5, resample_patch 8.8, font_substitution 55.6, field_displacement 21.6, patch_splice 51.7
C1 recall, fine-trace 31.7, coarse 42.2

| Threshold-free | AUROC | PR-AUC |
|---|---|---|
| all_forged_vs_C0 | 0.550 | 0.734 |
| C1_vs_C0 | 0.720 | 0.665 |
| C2_vs_C0 | 0.488 | 0.340 |
| C3_vs_C0 | 0.481 | 0.322 |
| C4_vs_C0 | 0.510 | 0.350 |
