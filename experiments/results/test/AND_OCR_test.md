# AND_OCR — test split

1620 images, 45 people. Percentages; 95% CIs from a person-clustered bootstrap (B = 10000).

| Metric | Value | 95% CI |
|---|---|---|
| Detection recall (all forged) | 2.9 | [1.8, 4.1] |
| FPR (C0) | 0.4 | [0.0, 0.9] |
| Precision | 93.9 | [84.8, 100.0] |
| F1 | 0.056 | |
| Rule-coverage recall (expected_rule = FAIL) | 5.7 | |

Confusion: TP 31, FP 2, TN 538, FN 1049

Flag rate by document type and category (on C0 this is the FPR):

| | C0 | C1 | C2 | C3 | C4 |
|---|---|---|---|---|---|
| aadhaar | 0.4 | 0.0 | 6.7 | 0.0 | 0.0 |
| pan | 0.4 | 5.2 | 7.4 | 3.0 | 0.7 |

C1 recall by edit type: local_recompression 4.5, resample_patch 0.0, font_substitution 5.6, field_displacement 3.9, patch_splice 0.0
C1 recall, fine-trace 2.4, coarse 2.7
