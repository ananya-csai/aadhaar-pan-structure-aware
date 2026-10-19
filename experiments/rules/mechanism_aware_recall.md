# Mechanism-aware recall (rule branch)

Eligible images are those the rules are designed to catch. *Flagged* counts any FAIL; *mechanism-aware* counts a FAIL from the check tied to the corrupted field; *over-attribution* counts a FAIL from a different check only. 95% Wilson intervals.

## test split

| Text | Cell | n | Flagged % | Mechanism-aware % [95% CI] | Over-attribution n |
|---|---|---|---|---|---|
| GT | aadhaar C2 | 135 | 100.0 | 100.0 [97.2, 100.0] | 0 |
| GT | pan C2 | 135 | 100.0 | 100.0 [97.2, 100.0] | 0 |
| GT | pan C3 | 135 | 100.0 | 100.0 [97.2, 100.0] | 0 |
| GT | aadhaar C3 (expected miss) | 135 | 0.0 | 0.0 [0.0, 2.8] | 0 |
| OCR | aadhaar C2 | 135 | 100.0 | 100.0 [97.2, 100.0] | 0 |
| OCR | pan C2 | 135 | 100.0 | 100.0 [97.2, 100.0] | 0 |
| OCR | pan C3 | 135 | 96.3 | 76.3 [68.5, 82.7] | 27 |
| OCR | aadhaar C3 (expected miss) | 135 | 4.4 | 0.0 [0.0, 2.8] | 0 |

## val split

| Text | Cell | n | Flagged % | Mechanism-aware % [95% CI] | Over-attribution n |
|---|---|---|---|---|---|
| GT | aadhaar C2 | 135 | 100.0 | 100.0 [97.2, 100.0] | 0 |
| GT | pan C2 | 135 | 100.0 | 100.0 [97.2, 100.0] | 0 |
| GT | pan C3 | 135 | 100.0 | 100.0 [97.2, 100.0] | 0 |
| GT | aadhaar C3 (expected miss) | 135 | 0.0 | 0.0 [0.0, 2.8] | 0 |
| OCR | aadhaar C2 | 135 | 100.0 | 100.0 [97.2, 100.0] | 0 |
| OCR | pan C2 | 135 | 96.3 | 96.3 [91.6, 98.4] | 0 |
| OCR | pan C3 | 135 | 94.8 | 78.5 [70.9, 84.6] | 22 |
| OCR | aadhaar C3 (expected miss) | 135 | 5.2 | 0.0 [0.0, 2.8] | 0 |

## train split

| Text | Cell | n | Flagged % | Mechanism-aware % [95% CI] | Over-attribution n |
|---|---|---|---|---|---|
| GT | aadhaar C2 | 630 | 100.0 | 100.0 [99.4, 100.0] | 0 |
| GT | pan C2 | 630 | 100.0 | 100.0 [99.4, 100.0] | 0 |
| GT | pan C3 | 630 | 100.0 | 100.0 [99.4, 100.0] | 0 |
| GT | aadhaar C3 (expected miss) | 630 | 0.0 | 0.0 [0.0, 0.6] | 0 |
| OCR | aadhaar C2 | 630 | 99.8 | 99.8 [99.1, 100.0] | 0 |
| OCR | pan C2 | 630 | 96.8 | 96.8 [95.1, 97.9] | 0 |
| OCR | pan C3 | 630 | 96.3 | 75.4 [71.9, 78.6] | 132 |
| OCR | aadhaar C3 (expected miss) | 630 | 4.8 | 0.0 [0.0, 0.6] | 0 |
