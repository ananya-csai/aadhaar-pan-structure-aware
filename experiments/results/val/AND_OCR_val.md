# AND_OCR — val split

1620 images, 45 people. Percentages; 95% CIs from a person-clustered bootstrap (B = 10000).

| Metric | Value | 95% CI |
|---|---|---|
| Detection recall (all forged) | 3.1 | [2.0, 4.1] |
| FPR (C0) | 1.3 | [0.6, 2.2] |
| Precision | 82.5 | [71.4, 92.6] |
| F1 | 0.059 | |
| Rule-coverage recall (expected_rule = FAIL) | 5.4 | |

Confusion: TP 33, FP 7, TN 533, FN 1047

Flag rate by document type and category (on C0 this is the FPR):

| | C0 | C1 | C2 | C3 | C4 |
|---|---|---|---|---|---|
| aadhaar | 0.0 | 0.0 | 3.0 | 0.0 | 0.0 |
| pan | 2.6 | 7.4 | 7.4 | 5.9 | 0.7 |

C1 recall by edit type: local_recompression 6.3, resample_patch 2.4, font_substitution 0.0, field_displacement 1.4, patch_splice 7.0
C1 recall, fine-trace 4.8, coarse 3.0
