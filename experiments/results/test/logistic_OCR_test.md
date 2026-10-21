# logistic_OCR — test split

1620 images, 45 people. Percentages; 95% CIs from a person-clustered bootstrap (B = 10000).

| Metric | Value | 95% CI |
|---|---|---|
| Detection recall (all forged) | 21.9 | [20.0, 24.0] |
| FPR (C0) | 4.1 | [2.8, 5.6] |
| Precision | 91.5 | [89.0, 94.1] |
| F1 | 0.354 | |
| Rule-coverage recall (expected_rule = FAIL) | 42.0 | |

Confusion: TP 237, FP 22, TN 518, FN 843

Flag rate by document type and category (on C0 this is the FPR):

| | C0 | C1 | C2 | C3 | C4 |
|---|---|---|---|---|---|
| aadhaar | 3.7 | 17.0 | 98.5 | 4.4 | 4.4 |
| pan | 4.4 | 20.0 | 14.8 | 12.6 | 3.7 |

C1 recall by edit type: local_recompression 30.3, resample_patch 0.0, font_substitution 25.0, field_displacement 11.8, patch_splice 25.0
C1 recall, fine-trace 16.3, coarse 20.4

| Threshold-free | AUROC | PR-AUC |
|---|---|---|
| all_forged_vs_C0 | 0.714 | 0.841 |
| C1_vs_C0 | 0.704 | 0.587 |
| C2_vs_C0 | 0.957 | 0.875 |
| C3_vs_C0 | 0.688 | 0.525 |
| C4_vs_C0 | 0.509 | 0.343 |
