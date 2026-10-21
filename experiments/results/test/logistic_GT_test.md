# logistic_GT — test split

1620 images, 45 people. Percentages; 95% CIs from a person-clustered bootstrap (B = 10000).

| Metric | Value | 95% CI |
|---|---|---|
| Detection recall (all forged) | 48.8 | [46.9, 50.7] |
| FPR (C0) | 4.8 | [3.1, 6.5] |
| Precision | 95.3 | [93.7, 96.8] |
| F1 | 0.645 | |
| Rule-coverage recall (expected_rule = FAIL) | 100.0 | |

Confusion: TP 527, FP 26, TN 514, FN 553

Flag rate by document type and category (on C0 this is the FPR):

| | C0 | C1 | C2 | C3 | C4 |
|---|---|---|---|---|---|
| aadhaar | 5.6 | 34.8 | 100.0 | 3.7 | 3.7 |
| pan | 4.1 | 40.0 | 100.0 | 100.0 | 8.1 |

C1 recall by edit type: local_recompression 51.5, resample_patch 8.8, font_substitution 55.6, field_displacement 21.6, patch_splice 51.7
C1 recall, fine-trace 31.7, coarse 42.2

| Threshold-free | AUROC | PR-AUC |
|---|---|---|
| all_forged_vs_C0 | 0.744 | 0.881 |
| C1_vs_C0 | 0.720 | 0.665 |
| C2_vs_C0 | 1.000 | 1.000 |
| C3_vs_C0 | 0.745 | 0.741 |
| C4_vs_C0 | 0.510 | 0.350 |
