# AND_GT — test split

1620 images, 45 people. Percentages; 95% CIs from a person-clustered bootstrap (B = 10000).

| Metric | Value | 95% CI |
|---|---|---|
| Detection recall (all forged) | 2.1 | [1.2, 3.1] |
| FPR (C0) | 0.0 | [0.0, 0.0] |
| Precision | 100.0 | [100.0, 100.0] |
| F1 | 0.042 | |
| Rule-coverage recall (expected_rule = FAIL) | 5.7 | |

Confusion: TP 23, FP 0, TN 540, FN 1057

Flag rate by document type and category (on C0 this is the FPR):

| | C0 | C1 | C2 | C3 | C4 |
|---|---|---|---|---|---|
| aadhaar | 0.0 | 0.0 | 6.7 | 0.0 | 0.0 |
| pan | 0.0 | 0.0 | 7.4 | 3.0 | 0.0 |

C1 recall by edit type: local_recompression 0.0, resample_patch 0.0, font_substitution 0.0, field_displacement 0.0, patch_splice 0.0
C1 recall, fine-trace 0.0, coarse 0.0
