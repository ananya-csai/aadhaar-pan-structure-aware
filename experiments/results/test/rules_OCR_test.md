# rules_OCR — test split

1620 images, 45 people. Percentages; 95% CIs from a person-clustered bootstrap (B = 10000).

| Metric | Value | 95% CI |
|---|---|---|
| Detection recall (all forged) | 43.1 | [41.3, 45.1] |
| FPR (C0) | 10.9 | [7.4, 14.8] |
| Precision | 88.8 | [85.6, 91.8] |
| F1 | 0.581 | |
| Rule-coverage recall (expected_rule = FAIL) | 98.8 | |

Confusion: TP 466, FP 59, TN 481, FN 614

Flag rate by document type and category (on C0 this is the FPR):

| | C0 | C1 | C2 | C3 | C4 |
|---|---|---|---|---|---|
| aadhaar | 3.7 | 2.2 | 100.0 | 4.4 | 4.4 |
| pan | 18.1 | 20.0 | 100.0 | 96.3 | 17.8 |

C1 recall by edit type: local_recompression 12.1, resample_patch 1.8, font_substitution 25.0, field_displacement 19.6, patch_splice 3.3
C1 recall, fine-trace 7.3, coarse 14.3
