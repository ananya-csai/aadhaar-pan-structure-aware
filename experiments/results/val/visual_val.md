# visual — val split

1620 images, 45 people. Percentages; 95% CIs from a person-clustered bootstrap (B = 10000).

| Metric | Value | 95% CI |
|---|---|---|
| Detection recall (all forged) | 12.8 | [11.1, 14.4] |
| FPR (C0) | 5.0 | [3.3, 6.9] |
| Precision | 83.6 | [78.5, 88.8] |
| F1 | 0.222 | |
| Rule-coverage recall (expected_rule = FAIL) | 5.7 | |

Confusion: TP 138, FP 27, TN 513, FN 942

Flag rate by document type and category (on C0 this is the FPR):

| | C0 | C1 | C2 | C3 | C4 |
|---|---|---|---|---|---|
| aadhaar | 4.1 | 33.3 | 3.0 | 3.7 | 5.2 |
| pan | 5.9 | 36.3 | 7.4 | 6.7 | 6.7 |

C1 recall by edit type: local_recompression 49.2, resample_patch 9.5, font_substitution 43.6, field_displacement 23.2, patch_splice 45.6
C1 recall, fine-trace 33.3, coarse 35.8

| Threshold-free | AUROC | PR-AUC |
|---|---|---|
| all_forged_vs_C0 | 0.584 | 0.754 |
| C1_vs_C0 | 0.780 | 0.702 |
| C2_vs_C0 | 0.525 | 0.357 |
| C3_vs_C0 | 0.526 | 0.359 |
| C4_vs_C0 | 0.506 | 0.350 |
