# visual — fresh split

3240 images, 90 people. Percentages; 95% CIs from a person-clustered bootstrap (B = 10000).

| Metric | Value | 95% CI |
|---|---|---|
| Detection recall (all forged) | 12.8 | [11.4, 14.2] |
| FPR (C0) | 4.9 | [3.7, 6.2] |
| Precision | 83.9 | [80.2, 87.5] |
| F1 | 0.222 | |
| Rule-coverage recall (expected_rule = FAIL) | 4.7 | |

Confusion: TP 276, FP 53, TN 1027, FN 1884

Flag rate by document type and category (on C0 this is the FPR):

| | C0 | C1 | C2 | C3 | C4 |
|---|---|---|---|---|---|
| aadhaar | 4.1 | 38.5 | 3.7 | 4.4 | 3.7 |
| pan | 5.7 | 37.4 | 6.3 | 4.1 | 4.1 |

C1 recall by edit type: local_recompression 48.3, resample_patch 7.7, font_substitution 61.1, field_displacement 21.9, patch_splice 51.5
C1 recall, fine-trace 28.3, coarse 45.5

| Threshold-free | AUROC | PR-AUC |
|---|---|---|
| all_forged_vs_C0 | 0.580 | 0.750 |
| C1_vs_C0 | 0.764 | 0.696 |
| C2_vs_C0 | 0.519 | 0.347 |
| C3_vs_C0 | 0.521 | 0.346 |
| C4_vs_C0 | 0.515 | 0.339 |
