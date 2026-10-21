# perCheck_GT — val split

1620 images, 45 people. Percentages; 95% CIs from a person-clustered bootstrap (B = 10000).

| Metric | Value | 95% CI |
|---|---|---|
| Detection recall (all forged) | 48.1 | [46.5, 49.9] |
| FPR (C0) | 5.0 | [3.3, 6.9] |
| Precision | 95.1 | [93.3, 96.7] |
| F1 | 0.639 | |
| Rule-coverage recall (expected_rule = FAIL) | 100.0 | |

Confusion: TP 520, FP 27, TN 513, FN 560

Flag rate by document type and category (on C0 this is the FPR):

| | C0 | C1 | C2 | C3 | C4 |
|---|---|---|---|---|---|
| aadhaar | 4.1 | 33.3 | 100.0 | 3.7 | 5.2 |
| pan | 5.9 | 36.3 | 100.0 | 100.0 | 6.7 |

C1 recall by edit type: local_recompression 49.2, resample_patch 9.5, font_substitution 43.6, field_displacement 23.2, patch_splice 45.6
C1 recall, fine-trace 33.3, coarse 35.8

| Threshold-free | AUROC | PR-AUC |
|---|---|---|
| all_forged_vs_C0 | 0.761 | 0.889 |
| C1_vs_C0 | 0.780 | 0.702 |
| C2_vs_C0 | 1.000 | 1.000 |
| C3_vs_C0 | 0.760 | 0.754 |
| C4_vs_C0 | 0.506 | 0.350 |
