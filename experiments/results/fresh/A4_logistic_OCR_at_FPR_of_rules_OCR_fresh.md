# A4_logistic_OCR_at_FPR_of_rules_OCR — fresh split

3240 images, 90 people. Percentages; 95% CIs from a person-clustered bootstrap (B = 10000).

| Metric | Value | 95% CI |
|---|---|---|
| Detection recall (all forged) | 47.7 | [46.4, 49.0] |
| FPR (C0) | 10.6 | [7.8, 13.6] |
| Precision | 90.0 | [87.6, 92.4] |
| F1 | 0.623 | |
| Rule-coverage recall (expected_rule = FAIL) | 97.2 | |

Confusion: TP 1030, FP 114, TN 966, FN 1130

Flag rate by document type and category (on C0 this is the FPR):

| | C0 | C1 | C2 | C3 | C4 |
|---|---|---|---|---|---|
| aadhaar | 3.3 | 30.0 | 100.0 | 4.1 | 4.8 |
| pan | 17.8 | 37.8 | 96.3 | 95.2 | 13.3 |

C1 recall by edit type: local_recompression 45.0, resample_patch 8.5, font_substitution 49.1, field_displacement 17.7, patch_splice 49.5
C1 recall, fine-trace 27.0, coarse 39.3

| Threshold-free | AUROC | PR-AUC |
|---|---|---|
| all_forged_vs_C0 | 0.727 | 0.848 |
| C1_vs_C0 | 0.739 | 0.616 |
| C2_vs_C0 | 0.954 | 0.874 |
| C3_vs_C0 | 0.708 | 0.546 |
| C4_vs_C0 | 0.507 | 0.339 |
