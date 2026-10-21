# rules_GT — fresh split

3240 images, 90 people. Percentages; 95% CIs from a person-clustered bootstrap (B = 10000).

| Metric | Value | 95% CI |
|---|---|---|
| Detection recall (all forged) | 37.5 | [37.5, 37.5] |
| FPR (C0) | 0.0 | [0.0, 0.0] |
| Precision | 100.0 | [100.0, 100.0] |
| F1 | 0.545 | |
| Rule-coverage recall (expected_rule = FAIL) | 100.0 | |

Confusion: TP 810, FP 0, TN 1080, FN 1350

Flag rate by document type and category (on C0 this is the FPR):

| | C0 | C1 | C2 | C3 | C4 |
|---|---|---|---|---|---|
| aadhaar | 0.0 | 0.0 | 100.0 | 0.0 | 0.0 |
| pan | 0.0 | 0.0 | 100.0 | 100.0 | 0.0 |

C1 recall by edit type: local_recompression 0.0, resample_patch 0.0, font_substitution 0.0, field_displacement 0.0, patch_splice 0.0
C1 recall, fine-trace 0.0, coarse 0.0
