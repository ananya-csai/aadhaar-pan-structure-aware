# AND_GT — fresh split

3240 images, 90 people. Percentages; 95% CIs from a person-clustered bootstrap (B = 10000).

| Metric | Value | 95% CI |
|---|---|---|
| Detection recall (all forged) | 1.8 | [1.2, 2.3] |
| FPR (C0) | 0.0 | [0.0, 0.0] |
| Precision | 100.0 | [100.0, 100.0] |
| F1 | 0.035 | |
| Rule-coverage recall (expected_rule = FAIL) | 4.7 | |

Confusion: TP 38, FP 0, TN 1080, FN 2122

Flag rate by document type and category (on C0 this is the FPR):

| | C0 | C1 | C2 | C3 | C4 |
|---|---|---|---|---|---|
| aadhaar | 0.0 | 0.0 | 3.7 | 0.0 | 0.0 |
| pan | 0.0 | 0.0 | 6.3 | 4.1 | 0.0 |

C1 recall by edit type: local_recompression 0.0, resample_patch 0.0, font_substitution 0.0, field_displacement 0.0, patch_splice 0.0
C1 recall, fine-trace 0.0, coarse 0.0
