# OR_OCR — val split

1620 images, 45 people. Percentages; 95% CIs from a person-clustered bootstrap (B = 10000).

| Metric | Value | 95% CI |
|---|---|---|
| Detection recall (all forged) | 53.0 | [50.6, 55.5] |
| FPR (C0) | 15.0 | [10.6, 19.8] |
| Precision | 87.6 | [84.4, 90.8] |
| F1 | 0.660 | |
| Rule-coverage recall (expected_rule = FAIL) | 97.3 | |

Confusion: TP 572, FP 81, TN 459, FN 508

Flag rate by document type and category (on C0 this is the FPR):

| | C0 | C1 | C2 | C3 | C4 |
|---|---|---|---|---|---|
| aadhaar | 7.4 | 37.0 | 100.0 | 8.9 | 6.7 |
| pan | 22.6 | 48.9 | 96.3 | 95.6 | 30.4 |

C1 recall by edit type: local_recompression 55.6, resample_patch 21.4, font_substitution 53.8, field_displacement 30.4, patch_splice 52.6
C1 recall, fine-trace 41.9, coarse 43.6
