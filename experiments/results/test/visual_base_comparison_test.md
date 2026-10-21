# visual_base_comparison — test split

1620 images, 45 people. Percentages; 95% CIs from a person-clustered bootstrap (B = 10000).

| Metric | Value | 95% CI |
|---|---|---|
| Detection recall (all forged) | 9.3 | [7.5, 11.1] |
| FPR (C0) | 5.2 | [3.1, 7.4] |
| Precision | 78.1 | [70.9, 85.5] |
| F1 | 0.166 | |
| Rule-coverage recall (expected_rule = FAIL) | 3.2 | |

Confusion: TP 100, FP 28, TN 512, FN 980

Flag rate by document type and category (on C0 this is the FPR):

| | C0 | C1 | C2 | C3 | C4 |
|---|---|---|---|---|---|
| aadhaar | 5.6 | 23.0 | 3.0 | 5.9 | 4.4 |
| pan | 4.8 | 21.5 | 3.7 | 3.0 | 9.6 |

C1 recall by edit type: local_recompression 19.7, resample_patch 5.3, font_substitution 50.0, field_displacement 9.8, patch_splice 35.0
C1 recall, fine-trace 13.0, coarse 29.9

| Threshold-free | AUROC | PR-AUC |
|---|---|---|
| all_forged_vs_C0 | 0.504 | 0.695 |
| C1_vs_C0 | 0.596 | 0.516 |
| C2_vs_C0 | 0.470 | 0.319 |
| C3_vs_C0 | 0.462 | 0.316 |
| C4_vs_C0 | 0.488 | 0.343 |
