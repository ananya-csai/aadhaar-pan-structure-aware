# visual_base_comparison — val split

1620 images, 45 people. Percentages; 95% CIs from a person-clustered bootstrap (B = 10000).

| Metric | Value | 95% CI |
|---|---|---|
| Detection recall (all forged) | 9.8 | [7.8, 11.9] |
| FPR (C0) | 5.0 | [3.1, 7.0] |
| Precision | 79.7 | [72.1, 86.6] |
| F1 | 0.175 | |
| Rule-coverage recall (expected_rule = FAIL) | 5.9 | |

Confusion: TP 106, FP 27, TN 513, FN 974

Flag rate by document type and category (on C0 this is the FPR):

| | C0 | C1 | C2 | C3 | C4 |
|---|---|---|---|---|---|
| aadhaar | 4.4 | 25.9 | 5.9 | 6.7 | 5.2 |
| pan | 5.6 | 16.3 | 4.4 | 7.4 | 6.7 |

C1 recall by edit type: local_recompression 14.3, resample_patch 2.4, font_substitution 59.0, field_displacement 15.9, patch_splice 22.8
C1 recall, fine-trace 9.5, coarse 28.5

| Threshold-free | AUROC | PR-AUC |
|---|---|---|
| all_forged_vs_C0 | 0.530 | 0.709 |
| C1_vs_C0 | 0.638 | 0.531 |
| C2_vs_C0 | 0.499 | 0.343 |
| C3_vs_C0 | 0.503 | 0.350 |
| C4_vs_C0 | 0.481 | 0.323 |
