# AND_OCR — fresh split

3240 images, 90 people. Percentages; 95% CIs from a person-clustered bootstrap (B = 10000).

| Metric | Value | 95% CI |
|---|---|---|
| Detection recall (all forged) | 2.7 | [1.9, 3.5] |
| FPR (C0) | 1.0 | [0.5, 1.6] |
| Precision | 84.1 | [74.6, 92.1] |
| F1 | 0.052 | |
| Rule-coverage recall (expected_rule = FAIL) | 4.6 | |

Confusion: TP 58, FP 11, TN 1069, FN 2102

Flag rate by document type and category (on C0 this is the FPR):

| | C0 | C1 | C2 | C3 | C4 |
|---|---|---|---|---|---|
| aadhaar | 0.2 | 0.4 | 3.7 | 0.0 | 0.7 |
| pan | 1.9 | 5.9 | 6.3 | 3.7 | 0.7 |

C1 recall by edit type: local_recompression 3.3, resample_patch 1.7, font_substitution 2.8, field_displacement 2.1, patch_splice 6.1
C1 recall, fine-trace 2.5, coarse 3.6
