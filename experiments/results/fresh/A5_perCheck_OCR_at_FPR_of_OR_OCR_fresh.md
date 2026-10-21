# A5_perCheck_OCR_at_FPR_of_OR_OCR — fresh split

3240 images, 90 people. Percentages; 95% CIs from a person-clustered bootstrap (B = 10000).

| Metric | Value | 95% CI |
|---|---|---|
| Detection recall (all forged) | 51.4 | [50.0, 52.9] |
| FPR (C0) | 14.0 | [11.2, 16.9] |
| Precision | 88.0 | [85.8, 90.2] |
| F1 | 0.649 | |
| Rule-coverage recall (expected_rule = FAIL) | 96.5 | |

Confusion: TP 1111, FP 151, TN 929, FN 1049

Flag rate by document type and category (on C0 this is the FPR):

| | C0 | C1 | C2 | C3 | C4 |
|---|---|---|---|---|---|
| aadhaar | 7.0 | 40.4 | 98.9 | 8.5 | 7.4 |
| pan | 20.9 | 48.9 | 95.2 | 95.6 | 16.7 |

C1 recall by edit type: local_recompression 57.5, resample_patch 14.5, font_substitution 66.7, field_displacement 30.2, patch_splice 54.5
C1 recall, fine-trace 36.3, coarse 51.2

| Threshold-free | AUROC | PR-AUC |
|---|---|---|
| all_forged_vs_C0 | 0.735 | 0.862 |
| C1_vs_C0 | 0.746 | 0.640 |
| C2_vs_C0 | 0.958 | 0.889 |
| C3_vs_C0 | 0.729 | 0.666 |
| C4_vs_C0 | 0.507 | 0.339 |
