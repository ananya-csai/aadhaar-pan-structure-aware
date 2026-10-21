# A4_logistic_OCR_at_FPR_of_OR_OCR — fresh split

3240 images, 90 people. Percentages; 95% CIs from a person-clustered bootstrap (B = 10000).

| Metric | Value | 95% CI |
|---|---|---|
| Detection recall (all forged) | 52.1 | [50.7, 53.5] |
| FPR (C0) | 14.4 | [11.4, 17.5] |
| Precision | 87.9 | [85.6, 90.1] |
| F1 | 0.654 | |
| Rule-coverage recall (expected_rule = FAIL) | 98.0 | |

Confusion: TP 1126, FP 155, TN 925, FN 1034

Flag rate by document type and category (on C0 this is the FPR):

| | C0 | C1 | C2 | C3 | C4 |
|---|---|---|---|---|---|
| aadhaar | 7.0 | 40.0 | 100.0 | 8.5 | 7.4 |
| pan | 21.7 | 49.6 | 97.4 | 96.7 | 17.4 |

C1 recall by edit type: local_recompression 56.7, resample_patch 14.5, font_substitution 67.6, field_displacement 30.2, patch_splice 55.6
C1 recall, fine-trace 35.9, coarse 51.8

| Threshold-free | AUROC | PR-AUC |
|---|---|---|
| all_forged_vs_C0 | 0.727 | 0.848 |
| C1_vs_C0 | 0.739 | 0.616 |
| C2_vs_C0 | 0.954 | 0.874 |
| C3_vs_C0 | 0.708 | 0.546 |
| C4_vs_C0 | 0.507 | 0.339 |
