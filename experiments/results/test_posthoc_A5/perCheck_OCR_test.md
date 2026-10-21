# perCheck_OCR — test split

1620 images, 45 people. Percentages; 95% CIs from a person-clustered bootstrap (B = 10000).

| Metric | Value | 95% CI |
|---|---|---|
| Detection recall (all forged) | 36.1 | [33.9, 38.4] |
| FPR (C0) | 5.0 | [3.5, 6.5] |
| Precision | 93.5 | [91.7, 95.3] |
| F1 | 0.521 | |
| Rule-coverage recall (expected_rule = FAIL) | 74.6 | |

Confusion: TP 390, FP 27, TN 513, FN 690

Flag rate by document type and category (on C0 this is the FPR):

| | C0 | C1 | C2 | C3 | C4 |
|---|---|---|---|---|---|
| aadhaar | 3.7 | 21.5 | 100.0 | 4.4 | 3.0 |
| pan | 6.3 | 31.1 | 43.7 | 80.0 | 5.2 |

C1 recall by edit type: local_recompression 37.9, resample_patch 0.0, font_substitution 41.7, field_displacement 17.6, patch_splice 36.7
C1 recall, fine-trace 20.3, coarse 31.3

| Threshold-free | AUROC | PR-AUC |
|---|---|---|
| all_forged_vs_C0 | 0.720 | 0.849 |
| C1_vs_C0 | 0.708 | 0.597 |
| C2_vs_C0 | 0.957 | 0.864 |
| C3_vs_C0 | 0.707 | 0.628 |
| C4_vs_C0 | 0.508 | 0.336 |
