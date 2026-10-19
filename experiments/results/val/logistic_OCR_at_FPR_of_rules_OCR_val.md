# logistic_OCR_at_FPR_of_rules_OCR — val split

1620 images, 45 people. Percentages; 95% CIs from a person-clustered bootstrap (B = 10000).

| Metric | Value | 95% CI |
|---|---|---|
| Detection recall (all forged) | 48.1 | [45.6, 50.7] |
| FPR (C0) | 11.3 | [7.0, 16.1] |
| Precision | 89.5 | [85.9, 93.1] |
| F1 | 0.626 | |
| Rule-coverage recall (expected_rule = FAIL) | 96.5 | |

Confusion: TP 520, FP 61, TN 479, FN 560

Flag rate by document type and category (on C0 this is the FPR):

| | C0 | C1 | C2 | C3 | C4 |
|---|---|---|---|---|---|
| aadhaar | 3.3 | 24.4 | 100.0 | 5.2 | 2.2 |
| pan | 19.3 | 39.3 | 95.6 | 94.1 | 24.4 |

C1 recall by edit type: local_recompression 38.1, resample_patch 14.3, font_substitution 43.6, field_displacement 17.4, patch_splice 47.4
C1 recall, fine-trace 28.6, coarse 33.9

| Threshold-free | AUROC | PR-AUC |
|---|---|---|
| all_forged_vs_C0 | 0.729 | 0.845 |
| C1_vs_C0 | 0.751 | 0.617 |
| C2_vs_C0 | 0.945 | 0.854 |
| C3_vs_C0 | 0.703 | 0.534 |
| C4_vs_C0 | 0.515 | 0.344 |
