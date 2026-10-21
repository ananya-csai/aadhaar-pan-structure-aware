# A5_perCheck_OCR_at_FPR_of_rules_OCR — fresh split

3240 images, 90 people. Percentages; 95% CIs from a person-clustered bootstrap (B = 10000).

| Metric | Value | 95% CI |
|---|---|---|
| Detection recall (all forged) | 46.9 | [45.5, 48.4] |
| FPR (C0) | 10.6 | [8.2, 13.1] |
| Precision | 89.9 | [87.8, 92.0] |
| F1 | 0.617 | |
| Rule-coverage recall (expected_rule = FAIL) | 91.1 | |

Confusion: TP 1014, FP 114, TN 966, FN 1146

Flag rate by document type and category (on C0 this is the FPR):

| | C0 | C1 | C2 | C3 | C4 |
|---|---|---|---|---|---|
| aadhaar | 5.4 | 35.2 | 98.9 | 6.7 | 5.9 |
| pan | 15.7 | 42.2 | 80.7 | 93.7 | 12.2 |

C1 recall by edit type: local_recompression 47.5, resample_patch 9.4, font_substitution 61.1, field_displacement 25.0, patch_splice 51.5
C1 recall, fine-trace 28.7, coarse 46.5

| Threshold-free | AUROC | PR-AUC |
|---|---|---|
| all_forged_vs_C0 | 0.735 | 0.862 |
| C1_vs_C0 | 0.746 | 0.640 |
| C2_vs_C0 | 0.958 | 0.889 |
| C3_vs_C0 | 0.729 | 0.666 |
| C4_vs_C0 | 0.507 | 0.339 |
