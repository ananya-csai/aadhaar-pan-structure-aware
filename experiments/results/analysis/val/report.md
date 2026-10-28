# Step 16-17 analyses — val split

1620 images, 45 people. Person-clustered bootstrap, B = 10000, seed 0, shared replicates (paired). Percentages. Families and Holm correction: DECISIONS.md Section 22.

## Systems

| System | Recall [95% CI] | FPR [95% CI] | Precision | F1 | C1 | C2 | C3 | C4 |
|---|---|---|---|---|---|---|---|---|
| visual | 12.8 [11.1, 14.4] | 5.0 [3.3, 6.9] | 83.6 | 0.222 | 34.8 | 5.2 | 5.2 | 5.9 |
| base | 9.8 [7.8, 11.9] | 5.0 [3.1, 7.0] | 79.7 | 0.175 | 21.1 | 5.2 | 7.0 | 5.9 |
| rules_GT | 37.5 [37.5, 37.5] | 0.0 [0.0, 0.0] | 100.0 | 0.545 | 0.0 | 100.0 | 50.0 | 0.0 |
| rules_OCR | 43.2 [41.0, 45.6] | 11.3 [7.0, 16.1] | 88.4 | 0.581 | 11.9 | 98.1 | 50.0 | 13.0 |
| OR_GT | 48.1 [46.5, 49.9] | 5.0 [3.3, 6.9] | 95.1 | 0.639 | 34.8 | 100.0 | 51.9 | 5.9 |
| AND_GT | 2.1 [1.3, 3.1] | 0.0 [0.0, 0.0] | 100.0 | 0.042 | 0.0 | 5.2 | 3.3 | 0.0 |
| OR_OCR | 53.0 [50.6, 55.5] | 15.0 [10.6, 19.8] | 87.6 | 0.66 | 43.0 | 98.1 | 52.2 | 18.5 |
| AND_OCR | 3.1 [2.0, 4.1] | 1.3 [0.6, 2.2] | 82.5 | 0.059 | 3.7 | 5.2 | 3.0 | 0.4 |
| A4_GT | 48.1 [46.5, 49.9] | 5.0 [3.3, 6.9] | 95.1 | 0.639 | 34.8 | 100.0 | 51.9 | 5.9 |
| A4_OCR | 24.2 [22.0, 26.5] | 5.0 [3.0, 7.0] | 90.6 | 0.382 | 23.7 | 58.5 | 11.1 | 3.3 |
| A4_OCR@rules | 48.1 [45.6, 50.7] | 11.3 [7.0, 16.1] | 89.5 | 0.626 | 31.9 | 97.8 | 49.6 | 13.3 |
| A4_OCR@OR | 53.0 [50.6, 55.5] | 15.0 [10.6, 19.8] | 87.6 | 0.66 | 43.0 | 98.1 | 52.2 | 18.5 |
| A5_GT | 48.1 [46.5, 49.9] | 5.0 [3.3, 6.9] | 95.1 | 0.639 | 34.8 | 100.0 | 51.9 | 5.9 |
| A5_OCR | 36.3 [34.1, 38.5] | 5.0 [3.1, 7.0] | 93.6 | 0.523 | 27.0 | 69.3 | 44.4 | 4.4 |
| A5_OCR@rules | 48.1 [45.6, 50.6] | 11.3 [7.8, 15.2] | 89.5 | 0.625 | 38.9 | 90.4 | 49.3 | 13.7 |
| A5_OCR@OR | 52.5 [50.1, 55.0] | 15.0 [10.7, 19.6] | 87.5 | 0.656 | 43.0 | 96.7 | 51.9 | 18.5 |

## Flag rate by document type and category

| System | aadhaar C0 | aadhaar C1 | aadhaar C2 | aadhaar C3 | aadhaar C4 | pan C0 | pan C1 | pan C2 | pan C3 | pan C4 |
|---|---|---|---|---|---|---|---|---|---|---|
| visual | 4.1 | 33.3 | 3.0 | 3.7 | 5.2 | 5.9 | 36.3 | 7.4 | 6.7 | 6.7 |
| base | 4.4 | 25.9 | 5.9 | 6.7 | 5.2 | 5.6 | 16.3 | 4.4 | 7.4 | 6.7 |
| rules_GT | 0.0 | 0.0 | 100.0 | 0.0 | 0.0 | 0.0 | 0.0 | 100.0 | 100.0 | 0.0 |
| rules_OCR | 3.3 | 3.7 | 100.0 | 5.2 | 1.5 | 19.3 | 20.0 | 96.3 | 94.8 | 24.4 |
| OR_GT | 4.1 | 33.3 | 100.0 | 3.7 | 5.2 | 5.9 | 36.3 | 100.0 | 100.0 | 6.7 |
| AND_GT | 0.0 | 0.0 | 3.0 | 0.0 | 0.0 | 0.0 | 0.0 | 7.4 | 6.7 | 0.0 |
| OR_OCR | 7.4 | 37.0 | 100.0 | 8.9 | 6.7 | 22.6 | 48.9 | 96.3 | 95.6 | 30.4 |
| AND_OCR | 0.0 | 0.0 | 3.0 | 0.0 | 0.0 | 2.6 | 7.4 | 7.4 | 5.9 | 0.7 |
| A4_GT | 4.1 | 33.3 | 100.0 | 3.7 | 5.2 | 5.9 | 36.3 | 100.0 | 100.0 | 6.7 |
| A4_OCR | 3.3 | 22.2 | 97.0 | 5.2 | 1.5 | 6.7 | 25.2 | 20.0 | 17.0 | 5.2 |
| A4_OCR@rules | 3.3 | 24.4 | 100.0 | 5.2 | 2.2 | 19.3 | 39.3 | 95.6 | 94.1 | 24.4 |
| A4_OCR@OR | 7.4 | 37.0 | 100.0 | 8.9 | 6.7 | 22.6 | 48.9 | 96.3 | 95.6 | 30.4 |
| A5_GT | 4.1 | 33.3 | 100.0 | 3.7 | 5.2 | 5.9 | 36.3 | 100.0 | 100.0 | 6.7 |
| A5_OCR | 3.0 | 23.0 | 98.5 | 4.4 | 1.5 | 7.0 | 31.1 | 40.0 | 84.4 | 7.4 |
| A5_OCR@rules | 4.8 | 34.1 | 100.0 | 6.7 | 3.0 | 17.8 | 43.7 | 80.7 | 91.9 | 24.4 |
| A5_OCR@OR | 7.8 | 37.0 | 100.0 | 8.9 | 6.7 | 22.2 | 48.9 | 93.3 | 94.8 | 30.4 |

## Delta and rho

| Quantity | Value | 95% CI |
|---|---|---|
| Delta_GT/forged | 35.4 | [34.4, 36.2] |
| Delta_GT/forged/aadhaar | 24.3 | [23.5, 24.8] |
| Delta_GT/forged/pan | 46.5 | [44.8, 48.0] |
| Delta_OCR/forged | 11.4 | [9.4, 13.3] |
| Delta_OCR/forged/aadhaar | 20.2 | [17.4, 23.0] |
| Delta_OCR/forged/pan | 2.6 | [0.0, 5.4] |
| Delta_OCR_A5/forged | 23.5 | [21.6, 25.5] |
| Delta_OCR_A5/forged/aadhaar | 20.6 | [18.3, 22.8] |
| Delta_OCR_A5/forged/pan | 26.5 | [23.0, 30.0] |
| rho_OCR/forged | 0.322 | [0.264, 0.38] |
| rho_OCR/forged/aadhaar | 0.831 | [0.718, 0.947] |
| rho_OCR/forged/pan | 0.056 | [0.0, 0.116] |
| rho_OCR_A5/forged | 0.664 | [0.604, 0.728] |
| rho_OCR_A5/forged/aadhaar | 0.848 | [0.761, 0.932] |
| rho_OCR_A5/forged/pan | 0.57 | [0.492, 0.651] |

## Families (Holm within family)

### F1 (RQ1, E-vis)

| ID | Comparison | Diff | 95% CI | p | p (Holm) | FPR diff [CI] |
|---|---|---|---|---|---|---|
| 1a | C1 fine-trace recall: tiles - whole card | +23.8 | [14.0, 32.5] | < 1e-4 | < 1e-4 | +0.0 [-2.6, 2.6] |
| 1b | C1 coarse recall: tiles - whole card | +7.3 | [0.6, 13.9] | 0.042 | 0.042 | +0.0 [-2.6, 2.6] |

### F3 (RQ3)

| ID | Comparison | Diff | 95% CI | p | p (Holm) | FPR diff [CI] |
|---|---|---|---|---|---|---|
| 3a | recall: A4-GT - visual (5% FPR) | +35.4 | [34.4, 36.2] | < 1e-4 | < 1e-4 | +0.0 [0.0, 0.0] |
| 3b | recall: A4-OCR - visual (5% FPR) | +11.4 | [9.4, 13.3] | < 1e-4 | < 1e-4 | +0.0 [-2.4, 2.4] |
| 3c | recall: A4-OCR - rules-OCR (matched FPR) | +4.9 | [3.5, 6.3] | < 1e-4 | < 1e-4 | +0.0 [0.0, 0.0] |
| 3d | recall: A4-OCR - OR-OCR (matched FPR) | +0.0 | [0.0, 0.0] | 1.000 | 1.000 | +0.0 [0.0, 0.0] |

### F4 (RQ4)

| ID | Comparison | Diff | 95% CI | p | p (Holm) | FPR diff [CI] |
|---|---|---|---|---|---|---|
| 4a | recall: A4-GT - A4-OCR (5% FPR) | +24.0 | [21.6, 26.3] | < 1e-4 | < 1e-4 | +0.0 [-2.4, 2.4] |
| 4b | rule-coverage recall: rules-GT - rules-OCR | +3.0 | [1.0, 5.7] | 0.0004 | 0.0004 |  |
| 4c | FPR: rules-OCR - rules-GT | +11.3 | [7.0, 16.1] | < 1e-4 | < 1e-4 |  |

### F5 (RQ5)

| ID | Comparison | Diff | 95% CI | p | p (Holm) | FPR diff [CI] |
|---|---|---|---|---|---|---|
| 5a | Delta_GT(Aadhaar) - Delta_GT(PAN) | -22.2 | [-23.9, -20.4] | < 1e-4 | < 1e-4 |  |
| 5b | Delta_OCR(Aadhaar) - Delta_OCR(PAN) | +17.6 | [13.7, 21.5] | < 1e-4 | < 1e-4 |  |

### F6 (RQ6)

| ID | Comparison | Diff | 95% CI | p | p (Holm) | FPR diff [CI] |
|---|---|---|---|---|---|---|
| 6a | rules-OCR FPR: PAN - Aadhaar | +15.9 | [7.8, 25.2] | < 1e-4 | < 1e-4 |  |
| 6b | rules-OCR FPR: severe - clean | +15.6 | [9.4, 22.2] | < 1e-4 | < 1e-4 |  |

### Post-hoc (A5; not in any family)

| ID | Comparison | Diff | 95% CI | p |
|---|---|---|---|---|
| Pa | recall: A5-OCR - A4-OCR (5% FPR) | +12.1 | [9.8, 14.4] | < 1e-4 |
| Pb | FPR: A5-OCR - A4-OCR (5% FPR) | +0.0 | [-0.6, 0.6] | 1.000 |
| Pc | recall: A5-GT - A4-GT (5% FPR) | +0.0 | [0.0, 0.0] | 1.000 |

## E-vis (RQ1): AUROC against C0

| Subset | Tiles [CI] | Whole card [CI] | Diff [CI] | p |
|---|---|---|---|---|
| c1 | 0.78 [0.748, 0.812] | 0.638 [0.591, 0.683] | +0.142 [0.107, 0.179] | < 1e-4 |
| c1_fine | 0.776 [0.724, 0.826] | 0.6 [0.537, 0.663] | +0.176 [0.114, 0.242] | < 1e-4 |
| c1_coarse | 0.783 [0.745, 0.821] | 0.662 [0.6, 0.719] | +0.121 [0.077, 0.171] | < 1e-4 |
| c1/clean | 0.948 [0.917, 0.976] | 0.733 [0.669, 0.793] | +0.215 [0.156, 0.278] | < 1e-4 |
| c1/mild | 0.704 [0.627, 0.773] | 0.636 [0.561, 0.707] | +0.068 [-0.021, 0.158] | 0.133 |
| c1/severe | 0.59 [0.519, 0.66] | 0.545 [0.468, 0.619] | +0.045 [-0.021, 0.11] | 0.177 |
| c1/local_recompression | 0.848 [0.789, 0.903] | 0.649 [0.563, 0.73] | +0.199 [0.113, 0.298] | < 1e-4 |
| c1/resample_patch | 0.667 [0.576, 0.745] | 0.526 [0.435, 0.597] | +0.141 [0.077, 0.205] | < 1e-4 |
| c1/font_substitution | 0.845 [0.773, 0.909] | 0.85 [0.787, 0.91] | -0.005 [-0.04, 0.023] | 0.783 |
| c1/field_displacement | 0.742 [0.682, 0.798] | 0.605 [0.519, 0.68] | +0.137 [0.042, 0.229] | 0.0064 |
| c1/patch_splice | 0.791 [0.732, 0.855] | 0.6 [0.473, 0.73] | +0.191 [0.104, 0.285] | 0.0002 |

Per-seed AUROC (mean ± SD over 5 seeds):

- tiles: c1 0.722 ± 0.034 [0.699, 0.685, 0.735, 0.717, 0.773]; c1_fine 0.718 ± 0.023 [0.722, 0.709, 0.705, 0.697, 0.756]; c1_coarse 0.724 ± 0.048 [0.684, 0.67, 0.754, 0.729, 0.783]
- base: c1 0.611 ± 0.02 [0.578, 0.613, 0.629, 0.622, 0.611]; c1_fine 0.572 ± 0.018 [0.559, 0.603, 0.573, 0.561, 0.563]; c1_coarse 0.636 ± 0.031 [0.59, 0.62, 0.664, 0.662, 0.641]

Visual bounding check (should be near 0.5): C2 vs C0 0.525 [0.491, 0.558]; C3 vs C0 0.526 [0.492, 0.56]; C4 vs C0 0.506 [0.463, 0.549]

## E6 (RQ4): rule verdicts, GT vs OCR text

| Cell | n | stable pass | stable fail | OCR-induced | OCR-masked |
|---|---|---|---|---|---|
| C0/aadhaar/clean | 90 | 90 | 0 | 0 | 0 |
| C0/aadhaar/mild | 90 | 90 | 0 | 0 | 0 |
| C0/aadhaar/severe | 90 | 81 | 0 | 9 | 0 |
| C0/aadhaar/all | 270 | 261 | 0 | 9 | 0 |
| C0/pan/clean | 90 | 78 | 0 | 12 | 0 |
| C0/pan/mild | 90 | 81 | 0 | 9 | 0 |
| C0/pan/severe | 90 | 59 | 0 | 31 | 0 |
| C0/pan/all | 270 | 218 | 0 | 52 | 0 |
| C1/aadhaar/clean | 45 | 45 | 0 | 0 | 0 |
| C1/aadhaar/mild | 45 | 44 | 0 | 1 | 0 |
| C1/aadhaar/severe | 45 | 41 | 0 | 4 | 0 |
| C1/aadhaar/all | 135 | 130 | 0 | 5 | 0 |
| C1/pan/clean | 45 | 38 | 0 | 7 | 0 |
| C1/pan/mild | 45 | 40 | 0 | 5 | 0 |
| C1/pan/severe | 45 | 30 | 0 | 15 | 0 |
| C1/pan/all | 135 | 108 | 0 | 27 | 0 |
| C2/aadhaar/clean | 45 | 0 | 45 | 0 | 0 |
| C2/aadhaar/mild | 45 | 0 | 45 | 0 | 0 |
| C2/aadhaar/severe | 45 | 0 | 45 | 0 | 0 |
| C2/aadhaar/all | 135 | 0 | 135 | 0 | 0 |
| C2/pan/clean | 45 | 0 | 43 | 0 | 2 |
| C2/pan/mild | 45 | 0 | 43 | 0 | 2 |
| C2/pan/severe | 45 | 0 | 44 | 0 | 1 |
| C2/pan/all | 135 | 0 | 130 | 0 | 5 |
| C3/aadhaar/clean | 45 | 45 | 0 | 0 | 0 |
| C3/aadhaar/mild | 45 | 45 | 0 | 0 | 0 |
| C3/aadhaar/severe | 45 | 38 | 0 | 7 | 0 |
| C3/aadhaar/all | 135 | 128 | 0 | 7 | 0 |
| C3/pan/clean | 45 | 0 | 45 | 0 | 0 |
| C3/pan/mild | 45 | 0 | 45 | 0 | 0 |
| C3/pan/severe | 45 | 0 | 38 | 0 | 7 |
| C3/pan/all | 135 | 0 | 128 | 0 | 7 |
| C4/aadhaar/clean | 45 | 45 | 0 | 0 | 0 |
| C4/aadhaar/mild | 45 | 45 | 0 | 0 | 0 |
| C4/aadhaar/severe | 45 | 43 | 0 | 2 | 0 |
| C4/aadhaar/all | 135 | 133 | 0 | 2 | 0 |
| C4/pan/clean | 45 | 38 | 0 | 7 | 0 |
| C4/pan/mild | 45 | 39 | 0 | 6 | 0 |
| C4/pan/severe | 45 | 25 | 0 | 20 | 0 |
| C4/pan/all | 135 | 102 | 0 | 33 | 0 |

## E8 (RQ6): C0 false-positive rate by stratum

### rules_OCR

| Cell | n | FPR | 95% CI |
|---|---|---|---|
| aadhaar/clean | 90 | 0.0 | [0.0, 0.0] |
| aadhaar/mild | 90 | 0.0 | [0.0, 0.0] |
| aadhaar/severe | 90 | 10.0 | [3.3, 17.8] |
| pan/clean | 90 | 13.3 | [4.4, 24.4] |
| pan/mild | 90 | 10.0 | [2.2, 20.0] |
| pan/severe | 90 | 34.4 | [23.3, 45.6] |
| pan/naming=initial_first | 84 | 20.2 | [6.0, 37.9] |
| pan/naming=mononymic | 90 | 18.9 | [8.3, 33.3] |
| pan/naming=surname_last | 96 | 18.8 | [4.8, 36.7] |
| pan/fifth=given_name | 48 | 31.2 | [6.7, 58.3] |
| pan/fifth=leading_initial | 36 | 5.6 | [0.0, 12.5] |
| pan/fifth=mononym | 90 | 18.9 | [8.3, 33.3] |
| pan/fifth=surname | 96 | 18.8 | [4.8, 36.7] |
| aadhaar/id_read_exact=1 | 261 | 0.0 | [0.0, 0.0] |
| aadhaar/id_read_exact=0 | 9 | 100.0 | [100.0, 100.0] |
| pan/id_read_exact=1 | 221 | 1.8 | [0.4, 3.7] |
| pan/id_read_exact=0 | 49 | 98.0 | [92.1, 100.0] |
| pan/name_read_exact=1 | 227 | 12.3 | [4.0, 22.4] |
| pan/name_read_exact=0 | 43 | 55.8 | [38.5, 73.3] |

### A4_OCR

| Cell | n | FPR | 95% CI |
|---|---|---|---|
| aadhaar/clean | 90 | 0.0 | [0.0, 0.0] |
| aadhaar/mild | 90 | 0.0 | [0.0, 0.0] |
| aadhaar/severe | 90 | 10.0 | [3.3, 17.8] |
| pan/clean | 90 | 0.0 | [0.0, 0.0] |
| pan/mild | 90 | 2.2 | [0.0, 5.6] |
| pan/severe | 90 | 17.8 | [10.0, 26.7] |
| pan/naming=initial_first | 84 | 4.8 | [0.0, 10.4] |
| pan/naming=mononymic | 90 | 6.7 | [1.9, 12.5] |
| pan/naming=surname_last | 96 | 8.3 | [3.0, 14.7] |
| pan/fifth=given_name | 48 | 8.3 | [0.0, 16.7] |
| pan/fifth=leading_initial | 36 | 0.0 | [0.0, 0.0] |
| pan/fifth=mononym | 90 | 6.7 | [1.9, 12.5] |
| pan/fifth=surname | 96 | 8.3 | [3.0, 14.7] |
| aadhaar/id_read_exact=1 | 261 | 0.0 | [0.0, 0.0] |
| aadhaar/id_read_exact=0 | 9 | 100.0 | [100.0, 100.0] |
| pan/id_read_exact=1 | 221 | 1.4 | [0.0, 3.1] |
| pan/id_read_exact=0 | 49 | 30.6 | [16.7, 52.3] |
| pan/name_read_exact=1 | 227 | 1.3 | [0.0, 3.5] |
| pan/name_read_exact=0 | 43 | 34.9 | [18.9, 52.5] |

### A5_OCR

| Cell | n | FPR | 95% CI |
|---|---|---|---|
| aadhaar/clean | 90 | 0.0 | [0.0, 0.0] |
| aadhaar/mild | 90 | 0.0 | [0.0, 0.0] |
| aadhaar/severe | 90 | 8.9 | [2.2, 16.7] |
| pan/clean | 90 | 0.0 | [0.0, 0.0] |
| pan/mild | 90 | 2.2 | [0.0, 5.6] |
| pan/severe | 90 | 18.9 | [11.1, 27.8] |
| pan/naming=initial_first | 84 | 4.8 | [0.0, 10.4] |
| pan/naming=mononymic | 90 | 7.8 | [2.8, 13.6] |
| pan/naming=surname_last | 96 | 8.3 | [3.0, 14.7] |
| pan/fifth=given_name | 48 | 8.3 | [0.0, 16.7] |
| pan/fifth=leading_initial | 36 | 0.0 | [0.0, 0.0] |
| pan/fifth=mononym | 90 | 7.8 | [2.8, 13.6] |
| pan/fifth=surname | 96 | 8.3 | [3.0, 14.7] |
| aadhaar/id_read_exact=1 | 261 | 0.0 | [0.0, 0.0] |
| aadhaar/id_read_exact=0 | 9 | 88.9 | [57.1, 100.0] |
| pan/id_read_exact=1 | 221 | 1.8 | [0.4, 3.7] |
| pan/id_read_exact=0 | 49 | 30.6 | [16.7, 52.3] |
| pan/name_read_exact=1 | 227 | 1.3 | [0.0, 3.5] |
| pan/name_read_exact=0 | 43 | 37.2 | [20.9, 54.9] |

### visual

| Cell | n | FPR | 95% CI |
|---|---|---|---|
| aadhaar/clean | 90 | 0.0 | [0.0, 0.0] |
| aadhaar/mild | 90 | 1.1 | [0.0, 3.3] |
| aadhaar/severe | 90 | 11.1 | [4.4, 18.9] |
| pan/clean | 90 | 1.1 | [0.0, 3.3] |
| pan/mild | 90 | 3.3 | [0.0, 7.8] |
| pan/severe | 90 | 13.3 | [7.8, 20.0] |
| pan/naming=initial_first | 84 | 7.1 | [1.9, 13.0] |
| pan/naming=mononymic | 90 | 1.1 | [0.0, 3.7] |
| pan/naming=surname_last | 96 | 9.4 | [4.4, 14.6] |
| pan/fifth=given_name | 48 | 8.3 | [0.0, 16.7] |
| pan/fifth=leading_initial | 36 | 5.6 | [0.0, 12.5] |
| pan/fifth=mononym | 90 | 1.1 | [0.0, 3.7] |
| pan/fifth=surname | 96 | 9.4 | [4.4, 14.6] |
| aadhaar/id_read_exact=1 | 261 | 4.2 | [1.9, 6.9] |
| aadhaar/id_read_exact=0 | 9 | 0.0 | [0.0, 0.0] |
| pan/id_read_exact=1 | 221 | 4.1 | [1.8, 6.5] |
| pan/id_read_exact=0 | 49 | 14.3 | [5.7, 27.6] |
| pan/name_read_exact=1 | 227 | 3.5 | [1.3, 5.9] |
| pan/name_read_exact=0 | 43 | 18.6 | [8.1, 30.4] |

Failing check on flagged C0 (rules-OCR): aadhaar/checksum_check 8, aadhaar/format_check 1, pan/format_check 47, pan/semantic_check 5

## E9/E12 (RQ2): explanations on images the rules target

| Cell | n | Flagged [CI] | Mechanism-aware [CI] | Over-attribution n | Correct share of flags | Over-attributed to |
|---|---|---|---|---|---|---|
| aadhaar/C2/GT | 135 | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 0 | 100.0 | {} |
| aadhaar/C2/OCR | 135 | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 0 | 100.0 | {} |
| pan/C2/GT | 135 | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 0 | 100.0 | {} |
| pan/C2/OCR | 135 | 96.3 [90.4, 100.0] | 96.3 [90.4, 100.0] | 0 | 100.0 | {} |
| pan/C3/GT | 135 | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 0 | 100.0 | {} |
| pan/C3/OCR | 135 | 94.8 [91.1, 97.8] | 78.5 [68.1, 87.4] | 22 | 82.8 | {'format_check': 22} |

## Rules on forgeries the visual branch misses (RQ2)

| Cell | visual missed | rules catch | % [CI] |
|---|---|---|---|
| GT/aadhaar/C2 | 131 | 131 | 100.0 [100.0, 100.0] |
| GT/pan/C2 | 125 | 125 | 100.0 [100.0, 100.0] |
| GT/aadhaar/C3 | 130 | 0 | 0.0 [0.0, 0.0] |
| GT/pan/C3 | 126 | 126 | 100.0 [100.0, 100.0] |
| GT/aadhaar/C4 | 128 | 0 | 0.0 [0.0, 0.0] |
| GT/pan/C4 | 126 | 0 | 0.0 [0.0, 0.0] |
| OCR/aadhaar/C2 | 131 | 131 | 100.0 [100.0, 100.0] |
| OCR/pan/C2 | 125 | 120 | 96.0 [89.6, 100.0] |
| OCR/aadhaar/C3 | 130 | 7 | 5.4 [2.3, 9.2] |
| OCR/pan/C3 | 126 | 120 | 95.2 [91.5, 98.4] |
| OCR/aadhaar/C4 | 128 | 2 | 1.6 [0.0, 3.9] |
| OCR/pan/C4 | 126 | 32 | 25.4 [15.5, 36.3] |
