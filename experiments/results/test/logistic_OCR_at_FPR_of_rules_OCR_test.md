# logistic_OCR_at_FPR_of_rules_OCR — test split

1620 images, 45 people. Percentages; 95% CIs from a person-clustered bootstrap (B = 10000).

| Metric | Value | 95% CI |
|---|---|---|
| Detection recall (all forged) | 47.8 | [45.4, 50.2] |
| FPR (C0) | 10.9 | [7.4, 14.8] |
| Precision | 89.7 | [86.7, 92.6] |
| F1 | 0.624 | |
| Rule-coverage recall (expected_rule = FAIL) | 96.8 | |

Confusion: TP 516, FP 59, TN 481, FN 564

Flag rate by document type and category (on C0 this is the FPR):

| | C0 | C1 | C2 | C3 | C4 |
|---|---|---|---|---|---|
| aadhaar | 3.7 | 21.5 | 100.0 | 4.4 | 4.4 |
| pan | 18.1 | 43.7 | 99.3 | 91.1 | 17.8 |

C1 recall by edit type: local_recompression 42.4, resample_patch 1.8, font_substitution 55.6, field_displacement 29.4, patch_splice 40.0
C1 recall, fine-trace 23.6, coarse 40.1

| Threshold-free | AUROC | PR-AUC |
|---|---|---|
| all_forged_vs_C0 | 0.714 | 0.841 |
| C1_vs_C0 | 0.704 | 0.587 |
| C2_vs_C0 | 0.957 | 0.875 |
| C3_vs_C0 | 0.688 | 0.525 |
| C4_vs_C0 | 0.509 | 0.343 |
