# rules_OCR — val split

1620 images, 45 people. Percentages; 95% CIs from a person-clustered bootstrap (B = 10000).

| Metric | Value | 95% CI |
|---|---|---|
| Detection recall (all forged) | 43.2 | [41.0, 45.6] |
| FPR (C0) | 11.3 | [7.0, 16.1] |
| Precision | 88.4 | [84.6, 92.3] |
| F1 | 0.581 | |
| Rule-coverage recall (expected_rule = FAIL) | 97.0 | |

Confusion: TP 467, FP 61, TN 479, FN 613

Flag rate by document type and category (on C0 this is the FPR):

| | C0 | C1 | C2 | C3 | C4 |
|---|---|---|---|---|---|
| aadhaar | 3.3 | 3.7 | 100.0 | 5.2 | 1.5 |
| pan | 19.3 | 20.0 | 96.3 | 94.8 | 24.4 |

C1 recall by edit type: local_recompression 12.7, resample_patch 14.3, font_substitution 10.3, field_displacement 8.7, patch_splice 14.0
C1 recall, fine-trace 13.3, coarse 10.9
