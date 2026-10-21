# OR_OCR — test split

1620 images, 45 people. Percentages; 95% CIs from a person-clustered bootstrap (B = 10000).

| Metric | Value | 95% CI |
|---|---|---|
| Detection recall (all forged) | 53.7 | [51.2, 56.3] |
| FPR (C0) | 15.4 | [12.2, 18.9] |
| Precision | 87.5 | [85.2, 89.7] |
| F1 | 0.666 | |
| Rule-coverage recall (expected_rule = FAIL) | 98.8 | |

Confusion: TP 580, FP 83, TN 457, FN 500

Flag rate by document type and category (on C0 this is the FPR):

| | C0 | C1 | C2 | C3 | C4 |
|---|---|---|---|---|---|
| aadhaar | 8.9 | 37.0 | 100.0 | 8.1 | 8.1 |
| pan | 21.9 | 54.8 | 100.0 | 96.3 | 25.2 |

C1 recall by edit type: local_recompression 59.1, resample_patch 10.5, font_substitution 75.0, field_displacement 37.3, patch_splice 55.0
C1 recall, fine-trace 36.6, coarse 53.7
