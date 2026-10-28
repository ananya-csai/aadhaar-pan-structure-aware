# Step 16-17 analyses — test split

1620 images, 45 people. Person-clustered bootstrap, B = 10000, seed 0, shared replicates (paired). Percentages. Families and Holm correction: DECISIONS.md Section 22.

## Systems

| System | Recall [95% CI] | FPR [95% CI] | Precision | F1 | C1 | C2 | C3 | C4 |
|---|---|---|---|---|---|---|---|---|
| visual | 13.4 [11.3, 15.6] | 4.8 [3.1, 6.5] | 84.8 | 0.232 | 37.4 | 7.0 | 3.3 | 5.9 |
| base | 9.3 [7.5, 11.1] | 5.2 [3.1, 7.4] | 78.1 | 0.166 | 22.2 | 3.3 | 4.4 | 7.0 |
| rules_GT | 37.5 [37.5, 37.5] | 0.0 [0.0, 0.0] | 100.0 | 0.545 | 0.0 | 100.0 | 50.0 | 0.0 |
| rules_OCR | 43.1 [41.3, 45.1] | 10.9 [7.4, 14.8] | 88.8 | 0.581 | 11.1 | 100.0 | 50.4 | 11.1 |
| OR_GT | 48.8 [46.9, 50.7] | 4.8 [3.1, 6.5] | 95.3 | 0.645 | 37.4 | 100.0 | 51.9 | 5.9 |
| AND_GT | 2.1 [1.2, 3.1] | 0.0 [0.0, 0.0] | 100.0 | 0.042 | 0.0 | 7.0 | 1.5 | 0.0 |
| OR_OCR | 53.7 [51.2, 56.3] | 15.4 [12.2, 18.9] | 87.5 | 0.666 | 45.9 | 100.0 | 52.2 | 16.7 |
| AND_OCR | 2.9 [1.8, 4.1] | 0.4 [0.0, 0.9] | 93.9 | 0.056 | 2.6 | 7.0 | 1.5 | 0.4 |
| A4_GT | 48.8 [46.9, 50.7] | 4.8 [3.1, 6.5] | 95.3 | 0.645 | 37.4 | 100.0 | 51.9 | 5.9 |
| A4_OCR | 21.9 [20.0, 24.0] | 4.1 [2.8, 5.6] | 91.5 | 0.354 | 18.5 | 56.7 | 8.5 | 4.1 |
| A4_OCR@rules | 47.8 [45.4, 50.2] | 10.9 [7.4, 14.8] | 89.7 | 0.624 | 32.6 | 99.6 | 47.8 | 11.1 |
| A4_OCR@OR | 53.6 [51.1, 56.2] | 15.4 [12.2, 18.9] | 87.5 | 0.665 | 45.6 | 100.0 | 52.2 | 16.7 |
| A5_GT | 48.8 [46.9, 50.7] | 4.8 [3.1, 6.5] | 95.3 | 0.645 | 37.4 | 100.0 | 51.9 | 5.9 |
| A5_OCR | 36.1 [33.9, 38.4] | 5.0 [3.5, 6.5] | 93.5 | 0.521 | 26.3 | 71.9 | 42.2 | 4.1 |
| A5_OCR@rules | 48.2 [45.9, 50.6] | 11.9 [9.1, 15.0] | 89.1 | 0.626 | 38.5 | 93.7 | 48.1 | 12.6 |
| A5_OCR@OR | 53.5 [51.0, 56.1] | 15.4 [12.2, 18.9] | 87.4 | 0.664 | 45.9 | 99.6 | 51.9 | 16.7 |

## Flag rate by document type and category

| System | aadhaar C0 | aadhaar C1 | aadhaar C2 | aadhaar C3 | aadhaar C4 | pan C0 | pan C1 | pan C2 | pan C3 | pan C4 |
|---|---|---|---|---|---|---|---|---|---|---|
| visual | 5.6 | 34.8 | 6.7 | 3.7 | 3.7 | 4.1 | 40.0 | 7.4 | 3.0 | 8.1 |
| base | 5.6 | 23.0 | 3.0 | 5.9 | 4.4 | 4.8 | 21.5 | 3.7 | 3.0 | 9.6 |
| rules_GT | 0.0 | 0.0 | 100.0 | 0.0 | 0.0 | 0.0 | 0.0 | 100.0 | 100.0 | 0.0 |
| rules_OCR | 3.7 | 2.2 | 100.0 | 4.4 | 4.4 | 18.1 | 20.0 | 100.0 | 96.3 | 17.8 |
| OR_GT | 5.6 | 34.8 | 100.0 | 3.7 | 3.7 | 4.1 | 40.0 | 100.0 | 100.0 | 8.1 |
| AND_GT | 0.0 | 0.0 | 6.7 | 0.0 | 0.0 | 0.0 | 0.0 | 7.4 | 3.0 | 0.0 |
| OR_OCR | 8.9 | 37.0 | 100.0 | 8.1 | 8.1 | 21.9 | 54.8 | 100.0 | 96.3 | 25.2 |
| AND_OCR | 0.4 | 0.0 | 6.7 | 0.0 | 0.0 | 0.4 | 5.2 | 7.4 | 3.0 | 0.7 |
| A4_GT | 5.6 | 34.8 | 100.0 | 3.7 | 3.7 | 4.1 | 40.0 | 100.0 | 100.0 | 8.1 |
| A4_OCR | 3.7 | 17.0 | 98.5 | 4.4 | 4.4 | 4.4 | 20.0 | 14.8 | 12.6 | 3.7 |
| A4_OCR@rules | 3.7 | 21.5 | 100.0 | 4.4 | 4.4 | 18.1 | 43.7 | 99.3 | 91.1 | 17.8 |
| A4_OCR@OR | 8.9 | 37.0 | 100.0 | 8.1 | 8.1 | 21.9 | 54.1 | 100.0 | 96.3 | 25.2 |
| A5_GT | 5.6 | 34.8 | 100.0 | 3.7 | 3.7 | 4.1 | 40.0 | 100.0 | 100.0 | 8.1 |
| A5_OCR | 3.7 | 21.5 | 100.0 | 4.4 | 3.0 | 6.3 | 31.1 | 43.7 | 80.0 | 5.2 |
| A5_OCR@rules | 6.3 | 30.4 | 100.0 | 4.4 | 5.9 | 17.4 | 46.7 | 87.4 | 91.9 | 19.3 |
| A5_OCR@OR | 8.9 | 37.0 | 100.0 | 8.1 | 8.1 | 21.9 | 54.8 | 99.3 | 95.6 | 25.2 |

## Delta and rho

| Quantity | Value | 95% CI |
|---|---|---|
| Delta_GT/forged | 35.4 | [34.4, 36.3] |
| Delta_GT/forged/aadhaar | 23.3 | [22.2, 24.3] |
| Delta_GT/forged/pan | 47.4 | [45.9, 48.7] |
| Delta_OCR/forged | 8.5 | [6.3, 10.6] |
| Delta_OCR/forged/aadhaar | 18.9 | [15.4, 22.2] |
| Delta_OCR/forged/pan | -1.9 | [-4.4, 0.9] |
| Delta_OCR_A5/forged | 22.7 | [19.6, 25.5] |
| Delta_OCR_A5/forged/aadhaar | 20.0 | [16.7, 23.1] |
| Delta_OCR_A5/forged/pan | 25.4 | [21.1, 29.8] |
| rho_OCR/forged | 0.24 | [0.18, 0.299] |
| rho_OCR/forged/aadhaar | 0.811 | [0.672, 0.937] |
| rho_OCR/forged/pan | -0.04 | [-0.094, 0.019] |
| rho_OCR_A5/forged | 0.641 | [0.562, 0.715] |
| rho_OCR_A5/forged/aadhaar | 0.858 | [0.732, 0.969] |
| rho_OCR_A5/forged/pan | 0.536 | [0.445, 0.625] |

## Families (Holm within family)

### F1 (RQ1, E-vis)

| ID | Comparison | Diff | 95% CI | p | p (Holm) | FPR diff [CI] |
|---|---|---|---|---|---|---|
| 1a | C1 fine-trace recall: tiles - whole card | +18.7 | [12.6, 24.4] | < 1e-4 | < 1e-4 | -0.4 [-3.0, 2.2] |
| 1b | C1 coarse recall: tiles - whole card | +12.2 | [2.1, 21.6] | 0.023 | 0.023 | -0.4 [-3.0, 2.2] |

### F3 (RQ3)

| ID | Comparison | Diff | 95% CI | p | p (Holm) | FPR diff [CI] |
|---|---|---|---|---|---|---|
| 3a | recall: A4-GT - visual (5% FPR) | +35.4 | [34.4, 36.3] | < 1e-4 | < 1e-4 | +0.0 [0.0, 0.0] |
| 3b | recall: A4-OCR - visual (5% FPR) | +8.5 | [6.3, 10.6] | < 1e-4 | < 1e-4 | -0.7 [-3.1, 1.5] |
| 3c | recall: A4-OCR - rules-OCR (matched FPR) | +4.6 | [3.1, 6.2] | < 1e-4 | < 1e-4 | +0.0 [0.0, 0.0] |
| 3d | recall: A4-OCR - OR-OCR (matched FPR) | -0.1 | [-0.3, 0.0] | 0.748 | 0.748 | +0.0 [0.0, 0.0] |

### F4 (RQ4)

| ID | Comparison | Diff | 95% CI | p | p (Holm) | FPR diff [CI] |
|---|---|---|---|---|---|---|
| 4a | recall: A4-GT - A4-OCR (5% FPR) | +26.9 | [24.8, 28.9] | < 1e-4 | < 1e-4 | +0.7 [-1.5, 3.1] |
| 4b | rule-coverage recall: rules-GT - rules-OCR | +1.2 | [0.2, 2.5] | 0.0096 | 0.0096 |  |
| 4c | FPR: rules-OCR - rules-GT | +10.9 | [7.4, 14.8] | < 1e-4 | < 1e-4 |  |

### F5 (RQ5)

| ID | Comparison | Diff | 95% CI | p | p (Holm) | FPR diff [CI] |
|---|---|---|---|---|---|---|
| 5a | Delta_GT(Aadhaar) - Delta_GT(PAN) | -24.1 | [-25.7, -22.4] | < 1e-4 | < 1e-4 |  |
| 5b | Delta_OCR(Aadhaar) - Delta_OCR(PAN) | +20.7 | [16.1, 24.8] | < 1e-4 | < 1e-4 |  |

### F6 (RQ6)

| ID | Comparison | Diff | 95% CI | p | p (Holm) | FPR diff [CI] |
|---|---|---|---|---|---|---|
| 6a | rules-OCR FPR: PAN - Aadhaar | +14.4 | [7.4, 23.0] | < 1e-4 | < 1e-4 |  |
| 6b | rules-OCR FPR: severe - clean | +20.6 | [15.0, 26.7] | < 1e-4 | < 1e-4 |  |

### Post-hoc (A5; not in any family)

| ID | Comparison | Diff | 95% CI | p |
|---|---|---|---|---|
| Pa | recall: A5-OCR - A4-OCR (5% FPR) | +14.2 | [12.1, 16.1] | < 1e-4 |
| Pb | FPR: A5-OCR - A4-OCR (5% FPR) | +0.9 | [0.2, 1.7] | 0.011 |
| Pc | recall: A5-GT - A4-GT (5% FPR) | +0.0 | [0.0, 0.0] | 1.000 |

## E-vis (RQ1): AUROC against C0

| Subset | Tiles [CI] | Whole card [CI] | Diff [CI] | p |
|---|---|---|---|---|
| c1 | 0.72 [0.676, 0.762] | 0.596 [0.555, 0.636] | +0.124 [0.08, 0.165] | < 1e-4 |
| c1_fine | 0.676 [0.614, 0.738] | 0.526 [0.474, 0.578] | +0.150 [0.085, 0.213] | < 1e-4 |
| c1_coarse | 0.757 [0.708, 0.803] | 0.655 [0.594, 0.719] | +0.102 [0.046, 0.154] | 0.0004 |
| c1/clean | 0.905 [0.853, 0.949] | 0.745 [0.691, 0.798] | +0.160 [0.095, 0.226] | < 1e-4 |
| c1/mild | 0.654 [0.587, 0.718] | 0.565 [0.496, 0.631] | +0.089 [0.007, 0.166] | 0.032 |
| c1/severe | 0.518 [0.434, 0.602] | 0.478 [0.41, 0.544] | +0.040 [-0.044, 0.127] | 0.351 |
| c1/local_recompression | 0.797 [0.739, 0.857] | 0.585 [0.51, 0.655] | +0.212 [0.139, 0.287] | < 1e-4 |
| c1/resample_patch | 0.536 [0.435, 0.629] | 0.458 [0.387, 0.53] | +0.078 [-0.043, 0.184] | 0.188 |
| c1/font_substitution | 0.838 [0.778, 0.898] | 0.814 [0.743, 0.879] | +0.024 [-0.089, 0.138] | 0.677 |
| c1/field_displacement | 0.684 [0.6, 0.767] | 0.568 [0.467, 0.666] | +0.116 [0.012, 0.22] | 0.030 |
| c1/patch_splice | 0.769 [0.684, 0.846] | 0.635 [0.524, 0.744] | +0.134 [0.046, 0.22] | 0.0060 |

Per-seed AUROC (mean ± SD over 5 seeds):

- tiles: c1 0.681 ± 0.025 [0.652, 0.663, 0.682, 0.696, 0.713]; c1_fine 0.65 ± 0.019 [0.635, 0.642, 0.646, 0.645, 0.684]; c1_coarse 0.707 ± 0.033 [0.667, 0.681, 0.712, 0.739, 0.738]
- base: c1 0.583 ± 0.028 [0.586, 0.597, 0.555, 0.554, 0.62]; c1_fine 0.517 ± 0.027 [0.508, 0.543, 0.491, 0.495, 0.548]; c1_coarse 0.638 ± 0.032 [0.652, 0.642, 0.609, 0.604, 0.681]

Visual bounding check (should be near 0.5): C2 vs C0 0.488 [0.446, 0.534]; C3 vs C0 0.481 [0.441, 0.52]; C4 vs C0 0.51 [0.473, 0.548]

## E6 (RQ4): rule verdicts, GT vs OCR text

| Cell | n | stable pass | stable fail | OCR-induced | OCR-masked |
|---|---|---|---|---|---|
| C0/aadhaar/clean | 90 | 90 | 0 | 0 | 0 |
| C0/aadhaar/mild | 90 | 90 | 0 | 0 | 0 |
| C0/aadhaar/severe | 90 | 80 | 0 | 10 | 0 |
| C0/aadhaar/all | 270 | 260 | 0 | 10 | 0 |
| C0/pan/clean | 90 | 83 | 0 | 7 | 0 |
| C0/pan/mild | 90 | 82 | 0 | 8 | 0 |
| C0/pan/severe | 90 | 56 | 0 | 34 | 0 |
| C0/pan/all | 270 | 221 | 0 | 49 | 0 |
| C1/aadhaar/clean | 45 | 45 | 0 | 0 | 0 |
| C1/aadhaar/mild | 45 | 45 | 0 | 0 | 0 |
| C1/aadhaar/severe | 45 | 42 | 0 | 3 | 0 |
| C1/aadhaar/all | 135 | 132 | 0 | 3 | 0 |
| C1/pan/clean | 45 | 39 | 0 | 6 | 0 |
| C1/pan/mild | 45 | 42 | 0 | 3 | 0 |
| C1/pan/severe | 45 | 27 | 0 | 18 | 0 |
| C1/pan/all | 135 | 108 | 0 | 27 | 0 |
| C2/aadhaar/clean | 45 | 0 | 45 | 0 | 0 |
| C2/aadhaar/mild | 45 | 0 | 45 | 0 | 0 |
| C2/aadhaar/severe | 45 | 0 | 45 | 0 | 0 |
| C2/aadhaar/all | 135 | 0 | 135 | 0 | 0 |
| C2/pan/clean | 45 | 0 | 45 | 0 | 0 |
| C2/pan/mild | 45 | 0 | 45 | 0 | 0 |
| C2/pan/severe | 45 | 0 | 45 | 0 | 0 |
| C2/pan/all | 135 | 0 | 135 | 0 | 0 |
| C3/aadhaar/clean | 45 | 45 | 0 | 0 | 0 |
| C3/aadhaar/mild | 45 | 45 | 0 | 0 | 0 |
| C3/aadhaar/severe | 45 | 39 | 0 | 6 | 0 |
| C3/aadhaar/all | 135 | 129 | 0 | 6 | 0 |
| C3/pan/clean | 45 | 0 | 45 | 0 | 0 |
| C3/pan/mild | 45 | 0 | 45 | 0 | 0 |
| C3/pan/severe | 45 | 0 | 40 | 0 | 5 |
| C3/pan/all | 135 | 0 | 130 | 0 | 5 |
| C4/aadhaar/clean | 45 | 45 | 0 | 0 | 0 |
| C4/aadhaar/mild | 45 | 44 | 0 | 1 | 0 |
| C4/aadhaar/severe | 45 | 40 | 0 | 5 | 0 |
| C4/aadhaar/all | 135 | 129 | 0 | 6 | 0 |
| C4/pan/clean | 45 | 41 | 0 | 4 | 0 |
| C4/pan/mild | 45 | 39 | 0 | 6 | 0 |
| C4/pan/severe | 45 | 31 | 0 | 14 | 0 |
| C4/pan/all | 135 | 111 | 0 | 24 | 0 |

## E8 (RQ6): C0 false-positive rate by stratum

### rules_OCR

| Cell | n | FPR | 95% CI |
|---|---|---|---|
| aadhaar/clean | 90 | 0.0 | [0.0, 0.0] |
| aadhaar/mild | 90 | 0.0 | [0.0, 0.0] |
| aadhaar/severe | 90 | 11.1 | [5.6, 17.8] |
| pan/clean | 90 | 7.8 | [1.1, 15.6] |
| pan/mild | 90 | 8.9 | [2.2, 16.7] |
| pan/severe | 90 | 37.8 | [27.8, 48.9] |
| pan/naming=initial_first | 84 | 15.5 | [6.0, 29.2] |
| pan/naming=mononymic | 90 | 17.8 | [6.7, 32.2] |
| pan/naming=surname_last | 96 | 20.8 | [8.8, 35.9] |
| pan/fifth=given_name | 36 | 19.4 | [0.0, 50.0] |
| pan/fifth=leading_initial | 48 | 12.5 | [4.2, 20.8] |
| pan/fifth=mononym | 90 | 17.8 | [6.7, 32.2] |
| pan/fifth=surname | 96 | 20.8 | [8.8, 35.9] |
| aadhaar/id_read_exact=1 | 260 | 0.0 | [0.0, 0.0] |
| aadhaar/id_read_exact=0 | 10 | 100.0 | [100.0, 100.0] |
| pan/id_read_exact=1 | 226 | 2.7 | [0.9, 4.7] |
| pan/id_read_exact=0 | 44 | 97.7 | [91.9, 100.0] |
| pan/name_read_exact=1 | 235 | 11.1 | [4.3, 19.3] |
| pan/name_read_exact=0 | 35 | 65.7 | [50.0, 81.5] |

### A4_OCR

| Cell | n | FPR | 95% CI |
|---|---|---|---|
| aadhaar/clean | 90 | 0.0 | [0.0, 0.0] |
| aadhaar/mild | 90 | 0.0 | [0.0, 0.0] |
| aadhaar/severe | 90 | 11.1 | [5.6, 17.8] |
| pan/clean | 90 | 0.0 | [0.0, 0.0] |
| pan/mild | 90 | 0.0 | [0.0, 0.0] |
| pan/severe | 90 | 13.3 | [6.7, 21.1] |
| pan/naming=initial_first | 84 | 4.8 | [1.1, 9.1] |
| pan/naming=mononymic | 90 | 6.7 | [1.7, 12.3] |
| pan/naming=surname_last | 96 | 2.1 | [0.0, 5.2] |
| pan/fifth=given_name | 36 | 5.6 | [0.0, 12.7] |
| pan/fifth=leading_initial | 48 | 4.2 | [0.0, 10.0] |
| pan/fifth=mononym | 90 | 6.7 | [1.7, 12.3] |
| pan/fifth=surname | 96 | 2.1 | [0.0, 5.2] |
| aadhaar/id_read_exact=1 | 260 | 0.0 | [0.0, 0.0] |
| aadhaar/id_read_exact=0 | 10 | 100.0 | [100.0, 100.0] |
| pan/id_read_exact=1 | 226 | 0.9 | [0.0, 2.2] |
| pan/id_read_exact=0 | 44 | 22.7 | [12.8, 33.3] |
| pan/name_read_exact=1 | 235 | 1.3 | [0.0, 2.9] |
| pan/name_read_exact=0 | 35 | 25.7 | [11.1, 41.9] |

### A5_OCR

| Cell | n | FPR | 95% CI |
|---|---|---|---|
| aadhaar/clean | 90 | 0.0 | [0.0, 0.0] |
| aadhaar/mild | 90 | 0.0 | [0.0, 0.0] |
| aadhaar/severe | 90 | 11.1 | [5.6, 17.8] |
| pan/clean | 90 | 0.0 | [0.0, 0.0] |
| pan/mild | 90 | 0.0 | [0.0, 0.0] |
| pan/severe | 90 | 18.9 | [11.1, 26.7] |
| pan/naming=initial_first | 84 | 7.1 | [2.8, 11.7] |
| pan/naming=mononymic | 90 | 7.8 | [2.8, 13.5] |
| pan/naming=surname_last | 96 | 4.2 | [1.0, 7.9] |
| pan/fifth=given_name | 36 | 5.6 | [0.0, 12.7] |
| pan/fifth=leading_initial | 48 | 8.3 | [2.4, 14.3] |
| pan/fifth=mononym | 90 | 7.8 | [2.8, 13.5] |
| pan/fifth=surname | 96 | 4.2 | [1.0, 7.9] |
| aadhaar/id_read_exact=1 | 260 | 0.0 | [0.0, 0.0] |
| aadhaar/id_read_exact=0 | 10 | 100.0 | [100.0, 100.0] |
| pan/id_read_exact=1 | 226 | 2.7 | [0.9, 4.7] |
| pan/id_read_exact=0 | 44 | 25.0 | [15.2, 36.2] |
| pan/name_read_exact=1 | 235 | 1.3 | [0.0, 2.9] |
| pan/name_read_exact=0 | 35 | 40.0 | [24.2, 55.6] |

### visual

| Cell | n | FPR | 95% CI |
|---|---|---|---|
| aadhaar/clean | 90 | 0.0 | [0.0, 0.0] |
| aadhaar/mild | 90 | 4.4 | [1.1, 8.9] |
| aadhaar/severe | 90 | 12.2 | [5.6, 20.0] |
| pan/clean | 90 | 0.0 | [0.0, 0.0] |
| pan/mild | 90 | 2.2 | [0.0, 5.6] |
| pan/severe | 90 | 10.0 | [4.4, 16.7] |
| pan/naming=initial_first | 84 | 3.6 | [0.0, 7.7] |
| pan/naming=mononymic | 90 | 6.7 | [1.7, 12.5] |
| pan/naming=surname_last | 96 | 2.1 | [0.0, 5.1] |
| pan/fifth=given_name | 36 | 2.8 | [0.0, 8.3] |
| pan/fifth=leading_initial | 48 | 4.2 | [0.0, 10.0] |
| pan/fifth=mononym | 90 | 6.7 | [1.7, 12.5] |
| pan/fifth=surname | 96 | 2.1 | [0.0, 5.1] |
| aadhaar/id_read_exact=1 | 260 | 5.4 | [3.1, 7.7] |
| aadhaar/id_read_exact=0 | 10 | 10.0 | [0.0, 33.3] |
| pan/id_read_exact=1 | 226 | 4.0 | [1.7, 6.7] |
| pan/id_read_exact=0 | 44 | 4.5 | [0.0, 12.5] |
| pan/name_read_exact=1 | 235 | 3.4 | [1.3, 5.9] |
| pan/name_read_exact=0 | 35 | 8.6 | [0.0, 19.4] |

Failing check on flagged C0 (rules-OCR): aadhaar/checksum_check 9, aadhaar/format_check 1, pan/format_check 41, pan/semantic_check 8

## E9/E12 (RQ2): explanations on images the rules target

| Cell | n | Flagged [CI] | Mechanism-aware [CI] | Over-attribution n | Correct share of flags | Over-attributed to |
|---|---|---|---|---|---|---|
| aadhaar/C2/GT | 135 | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 0 | 100.0 | {} |
| aadhaar/C2/OCR | 135 | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 0 | 100.0 | {} |
| pan/C2/GT | 135 | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 0 | 100.0 | {} |
| pan/C2/OCR | 135 | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 0 | 100.0 | {} |
| pan/C3/GT | 135 | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 0 | 100.0 | {} |
| pan/C3/OCR | 135 | 96.3 [92.6, 99.3] | 76.3 [65.2, 86.7] | 27 | 79.2 | {'format_check': 27} |

## Rules on forgeries the visual branch misses (RQ2)

| Cell | visual missed | rules catch | % [CI] |
|---|---|---|---|
| GT/aadhaar/C2 | 126 | 126 | 100.0 [100.0, 100.0] |
| GT/pan/C2 | 125 | 125 | 100.0 [100.0, 100.0] |
| GT/aadhaar/C3 | 130 | 0 | 0.0 [0.0, 0.0] |
| GT/pan/C3 | 131 | 131 | 100.0 [100.0, 100.0] |
| GT/aadhaar/C4 | 130 | 0 | 0.0 [0.0, 0.0] |
| GT/pan/C4 | 124 | 0 | 0.0 [0.0, 0.0] |
| OCR/aadhaar/C2 | 126 | 126 | 100.0 [100.0, 100.0] |
| OCR/pan/C2 | 125 | 125 | 100.0 [100.0, 100.0] |
| OCR/aadhaar/C3 | 130 | 6 | 4.6 [1.5, 8.4] |
| OCR/pan/C3 | 131 | 126 | 96.2 [92.5, 99.2] |
| OCR/aadhaar/C4 | 130 | 6 | 4.6 [1.5, 8.4] |
| OCR/pan/C4 | 124 | 23 | 18.5 [9.4, 28.7] |
