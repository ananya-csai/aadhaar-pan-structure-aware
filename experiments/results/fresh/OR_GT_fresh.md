# OR_GT — fresh split

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
