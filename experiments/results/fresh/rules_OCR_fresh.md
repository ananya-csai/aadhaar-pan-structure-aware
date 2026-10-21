# rules_OCR — fresh split

3240 images, 90 people. Percentages; 95% CIs from a person-clustered bootstrap (B = 10000).

| Metric | Value | 95% CI |
|---|---|---|
| Detection recall (all forged) | 42.0 | [40.9, 43.2] |
| FPR (C0) | 10.5 | [7.7, 13.6] |
| Precision | 88.9 | [86.2, 91.6] |
| F1 | 0.571 | |
| Rule-coverage recall (expected_rule = FAIL) | 97.9 | |

Confusion: TP 908, FP 113, TN 967, FN 1252

Flag rate by document type and category (on C0 this is the FPR):

| | C0 | C1 | C2 | C3 | C4 |
|---|---|---|---|---|---|
| aadhaar | 3.1 | 1.9 | 100.0 | 4.1 | 4.4 |
| pan | 17.8 | 18.1 | 97.4 | 96.3 | 14.1 |

C1 recall by edit type: local_recompression 11.7, resample_patch 8.5, font_substitution 9.3, field_displacement 10.4, patch_splice 10.1
C1 recall, fine-trace 10.1, coarse 9.9
