# logistic_OCR — val split

1620 images, 45 people. Percentages; 95% CIs from a person-clustered bootstrap (B = 10000).

| Metric | Value | 95% CI |
|---|---|---|
| Detection recall (all forged) | 24.2 | [22.0, 26.5] |
| FPR (C0) | 5.0 | [3.0, 7.0] |
| Precision | 90.6 | [87.2, 94.0] |
| F1 | 0.382 | |
| Rule-coverage recall (expected_rule = FAIL) | 44.7 | |

Confusion: TP 261, FP 27, TN 513, FN 819

Flag rate by document type and category (on C0 this is the FPR):

| | C0 | C1 | C2 | C3 | C4 |
|---|---|---|---|---|---|
| aadhaar | 3.3 | 22.2 | 97.0 | 5.2 | 1.5 |
| pan | 6.7 | 25.2 | 20.0 | 17.0 | 5.2 |

C1 recall by edit type: local_recompression 31.7, resample_patch 9.5, font_substitution 30.8, field_displacement 10.1, patch_splice 36.8
C1 recall, fine-trace 22.9, coarse 24.2

| Threshold-free | AUROC | PR-AUC |
|---|---|---|
| all_forged_vs_C0 | 0.729 | 0.845 |
| C1_vs_C0 | 0.751 | 0.617 |
| C2_vs_C0 | 0.945 | 0.854 |
| C3_vs_C0 | 0.703 | 0.534 |
| C4_vs_C0 | 0.515 | 0.344 |
