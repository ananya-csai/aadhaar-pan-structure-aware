# perCheck_OCR_at_FPR_of_OR_OCR — val split

1620 images, 45 people. Percentages; 95% CIs from a person-clustered bootstrap (B = 10000).

| Metric | Value | 95% CI |
|---|---|---|
| Detection recall (all forged) | 52.5 | [50.1, 55.0] |
| FPR (C0) | 15.0 | [10.7, 19.6] |
| Precision | 87.5 | [84.4, 90.6] |
| F1 | 0.656 | |
| Rule-coverage recall (expected_rule = FAIL) | 96.0 | |

Confusion: TP 567, FP 81, TN 459, FN 513

Flag rate by document type and category (on C0 this is the FPR):

| | C0 | C1 | C2 | C3 | C4 |
|---|---|---|---|---|---|
| aadhaar | 7.8 | 37.0 | 100.0 | 8.9 | 6.7 |
| pan | 22.2 | 48.9 | 93.3 | 94.8 | 30.4 |

C1 recall by edit type: local_recompression 55.6, resample_patch 21.4, font_substitution 53.8, field_displacement 30.4, patch_splice 52.6
C1 recall, fine-trace 41.9, coarse 43.6

| Threshold-free | AUROC | PR-AUC |
|---|---|---|
| all_forged_vs_C0 | 0.737 | 0.857 |
| C1_vs_C0 | 0.755 | 0.624 |
| C2_vs_C0 | 0.951 | 0.857 |
| C3_vs_C0 | 0.726 | 0.648 |
| C4_vs_C0 | 0.516 | 0.352 |
