# perCheck_OCR_at_FPR_of_rules_OCR — val split

1620 images, 45 people. Percentages; 95% CIs from a person-clustered bootstrap (B = 10000).

| Metric | Value | 95% CI |
|---|---|---|
| Detection recall (all forged) | 48.1 | [45.6, 50.6] |
| FPR (C0) | 11.3 | [7.8, 15.2] |
| Precision | 89.5 | [86.5, 92.4] |
| F1 | 0.625 | |
| Rule-coverage recall (expected_rule = FAIL) | 90.9 | |

Confusion: TP 519, FP 61, TN 479, FN 561

Flag rate by document type and category (on C0 this is the FPR):

| | C0 | C1 | C2 | C3 | C4 |
|---|---|---|---|---|---|
| aadhaar | 4.8 | 34.1 | 100.0 | 6.7 | 3.0 |
| pan | 17.8 | 43.7 | 80.7 | 91.9 | 24.4 |

C1 recall by edit type: local_recompression 50.8, resample_patch 19.0, font_substitution 51.3, field_displacement 24.6, patch_splice 49.1
C1 recall, fine-trace 38.1, coarse 39.4

| Threshold-free | AUROC | PR-AUC |
|---|---|---|
| all_forged_vs_C0 | 0.737 | 0.857 |
| C1_vs_C0 | 0.755 | 0.624 |
| C2_vs_C0 | 0.951 | 0.857 |
| C3_vs_C0 | 0.726 | 0.648 |
| C4_vs_C0 | 0.516 | 0.352 |
