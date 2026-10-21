# A5_perCheck_GT — fresh split

3240 images, 90 people. Percentages; 95% CIs from a person-clustered bootstrap (B = 10000).

| Metric | Value | 95% CI |
|---|---|---|
| Detection recall (all forged) | 48.5 | [47.3, 49.8] |
| FPR (C0) | 4.9 | [3.7, 6.2] |
| Precision | 95.2 | [94.0, 96.3] |
| F1 | 0.643 | |
| Rule-coverage recall (expected_rule = FAIL) | 100.0 | |

Confusion: TP 1048, FP 53, TN 1027, FN 1112

Flag rate by document type and category (on C0 this is the FPR):

| | C0 | C1 | C2 | C3 | C4 |
|---|---|---|---|---|---|
| aadhaar | 4.1 | 38.5 | 100.0 | 4.4 | 3.7 |
| pan | 5.7 | 37.4 | 100.0 | 100.0 | 4.1 |

C1 recall by edit type: local_recompression 48.3, resample_patch 7.7, font_substitution 61.1, field_displacement 21.9, patch_splice 51.5
C1 recall, fine-trace 28.3, coarse 45.5

| Threshold-free | AUROC | PR-AUC |
|---|---|---|
| all_forged_vs_C0 | 0.761 | 0.889 |
| C1_vs_C0 | 0.764 | 0.696 |
| C2_vs_C0 | 1.000 | 1.000 |
| C3_vs_C0 | 0.765 | 0.752 |
| C4_vs_C0 | 0.515 | 0.339 |
