# perCheck_OCR_at_FPR_of_rules_OCR — test split

1620 images, 45 people. Percentages; 95% CIs from a person-clustered bootstrap (B = 10000).

| Metric | Value | 95% CI |
|---|---|---|
| Detection recall (all forged) | 48.2 | [45.9, 50.6] |
| FPR (C0) | 11.9 | [9.1, 15.0] |
| Precision | 89.1 | [86.8, 91.3] |
| F1 | 0.626 | |
| Rule-coverage recall (expected_rule = FAIL) | 93.1 | |

Confusion: TP 521, FP 64, TN 476, FN 559

Flag rate by document type and category (on C0 this is the FPR):

| | C0 | C1 | C2 | C3 | C4 |
|---|---|---|---|---|---|
| aadhaar | 6.3 | 30.4 | 100.0 | 4.4 | 5.9 |
| pan | 17.4 | 46.7 | 87.4 | 91.9 | 19.3 |

C1 recall by edit type: local_recompression 48.5, resample_patch 5.3, font_substitution 66.7, field_displacement 31.4, patch_splice 48.3
C1 recall, fine-trace 28.5, coarse 46.9

| Threshold-free | AUROC | PR-AUC |
|---|---|---|
| all_forged_vs_C0 | 0.720 | 0.849 |
| C1_vs_C0 | 0.708 | 0.597 |
| C2_vs_C0 | 0.957 | 0.864 |
| C3_vs_C0 | 0.707 | 0.628 |
| C4_vs_C0 | 0.508 | 0.336 |
