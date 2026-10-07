# E3 — Rule-Only Branch

This experiment independently reproduces the rule-only validation
results on the frozen test split.

## Inputs

- dataset/data/v1/manifest.csv
- test split only
- ground-truth rule verdict
- OCR rule verdict

## Systems

1. Structural/semantic rules with ground-truth text
2. Structural/semantic rules with OCR-extracted text

## Overall test results

| System | Precision | Recall | F1 | FPR |
|---|---:|---:|---:|---:|
| Ground-truth text | 100.00% | 100.00% | 100.00% | 0.00% |
| OCR text | 75.66% | 99.01% | 85.78% | 10.62% |

## Document-level results

| Document | System | Precision | Recall | F1 | FPR |
|---|---|---:|---:|---:|---:|
| Aadhaar | Ground-truth | 100.00% | 100.00% | 100.00% | 0.00% |
| Aadhaar | OCR | 85.35% | 99.26% | 91.78% | 3.41% |
| PAN | Ground-truth | 100.00% | 100.00% | 100.00% | 0.00% |
| PAN | OCR | 71.58% | 98.89% | 83.05% | 19.63% |

## Interpretation

Ground-truth text gives perfect rule performance on this controlled
test set. OCR extraction introduces false positives and a small number
of false negatives. The degradation is substantially larger for PAN.

C2 structural inconsistencies are detected very reliably. C4 is
intentionally structurally valid, so passing the rules does not imply
authenticity.

Per-category F1 is not interpreted for categories with no expected
FAIL samples; false-positive/flag rates are reported instead.