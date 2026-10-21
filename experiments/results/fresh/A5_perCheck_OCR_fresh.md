# A5_perCheck_OCR — fresh split

3240 images, 90 people. Percentages; 95% CIs from a person-clustered bootstrap (B = 10000).

| Metric | Value | 95% CI |
|---|---|---|
| Detection recall (all forged) | 36.1 | [34.5, 37.8] |
| FPR (C0) | 3.9 | [2.8, 5.1] |
| Precision | 94.9 | [93.4, 96.3] |
| F1 | 0.523 | |
| Rule-coverage recall (expected_rule = FAIL) | 74.2 | |

Confusion: TP 780, FP 42, TN 1038, FN 1380

Flag rate by document type and category (on C0 this is the FPR):

| | C0 | C1 | C2 | C3 | C4 |
|---|---|---|---|---|---|
| aadhaar | 2.6 | 27.8 | 97.8 | 3.0 | 3.3 |
| pan | 5.2 | 28.5 | 41.9 | 83.0 | 3.7 |

C1 recall by edit type: local_recompression 39.2, resample_patch 3.4, font_substitution 42.6, field_displacement 8.3, patch_splice 47.5
C1 recall, fine-trace 21.5, coarse 33.3

| Threshold-free | AUROC | PR-AUC |
|---|---|---|
| all_forged_vs_C0 | 0.735 | 0.862 |
| C1_vs_C0 | 0.746 | 0.640 |
| C2_vs_C0 | 0.958 | 0.889 |
| C3_vs_C0 | 0.729 | 0.666 |
| C4_vs_C0 | 0.507 | 0.339 |
