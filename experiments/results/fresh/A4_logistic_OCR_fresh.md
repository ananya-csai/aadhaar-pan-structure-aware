# A4_logistic_OCR — fresh split

3240 images, 90 people. Percentages; 95% CIs from a person-clustered bootstrap (B = 10000).

| Metric | Value | 95% CI |
|---|---|---|
| Detection recall (all forged) | 23.5 | [22.1, 24.9] |
| FPR (C0) | 3.7 | [2.6, 4.9] |
| Precision | 92.7 | [90.6, 94.8] |
| F1 | 0.375 | |
| Rule-coverage recall (expected_rule = FAIL) | 45.2 | |

Confusion: TP 507, FP 40, TN 1040, FN 1653

Flag rate by document type and category (on C0 this is the FPR):

| | C0 | C1 | C2 | C3 | C4 |
|---|---|---|---|---|---|
| aadhaar | 3.1 | 20.0 | 95.9 | 4.1 | 4.4 |
| pan | 4.3 | 21.1 | 21.5 | 18.1 | 2.6 |

C1 recall by edit type: local_recompression 32.5, resample_patch 3.4, font_substitution 21.3, field_displacement 6.2, patch_splice 39.4
C1 recall, fine-trace 18.1, coarse 22.4

| Threshold-free | AUROC | PR-AUC |
|---|---|---|
| all_forged_vs_C0 | 0.727 | 0.848 |
| C1_vs_C0 | 0.739 | 0.616 |
| C2_vs_C0 | 0.954 | 0.874 |
| C3_vs_C0 | 0.708 | 0.546 |
| C4_vs_C0 | 0.507 | 0.339 |
