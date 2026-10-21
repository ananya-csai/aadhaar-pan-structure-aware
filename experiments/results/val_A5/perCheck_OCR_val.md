# perCheck_OCR — val split

1620 images, 45 people. Percentages; 95% CIs from a person-clustered bootstrap (B = 10000).

| Metric | Value | 95% CI |
|---|---|---|
| Detection recall (all forged) | 36.3 | [34.1, 38.5] |
| FPR (C0) | 5.0 | [3.1, 7.0] |
| Precision | 93.6 | [91.1, 95.9] |
| F1 | 0.523 | |
| Rule-coverage recall (expected_rule = FAIL) | 74.3 | |

Confusion: TP 392, FP 27, TN 513, FN 688

Flag rate by document type and category (on C0 this is the FPR):

| | C0 | C1 | C2 | C3 | C4 |
|---|---|---|---|---|---|
| aadhaar | 3.0 | 23.0 | 98.5 | 4.4 | 1.5 |
| pan | 7.0 | 31.1 | 40.0 | 84.4 | 7.4 |

C1 recall by edit type: local_recompression 33.3, resample_patch 9.5, font_substitution 38.5, field_displacement 15.9, patch_splice 38.6
C1 recall, fine-trace 23.8, coarse 29.1

| Threshold-free | AUROC | PR-AUC |
|---|---|---|
| all_forged_vs_C0 | 0.737 | 0.857 |
| C1_vs_C0 | 0.755 | 0.624 |
| C2_vs_C0 | 0.951 | 0.857 |
| C3_vs_C0 | 0.726 | 0.648 |
| C4_vs_C0 | 0.516 | 0.352 |
