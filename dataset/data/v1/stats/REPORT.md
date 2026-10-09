# Dataset v1 — characterisation report

Everything in this report characterises the DATASET and the rule branch operating on it. No visual model is trained and no fusion is performed here, so none of these numbers is a detection result for the hybrid system.

- persons: **300**   documents: **3600**   images: **10800**
- genuine images (C0): **3600**   forged (C1-C4): **7200**
- on disk: **0.877 GiB**

## Composition (images per document type x forgery category)

| category | aadhaar | pan |
|---|---|---|
| C0 | 1800 | 1800 |
| C1 | 900 | 900 |
| C2 | 900 | 900 |
| C3 | 900 | 900 |
| C4 | 900 | 900 |

Split sizes (images): {'train': 7560, 'val': 1620, 'test': 1620}  
Split sizes (persons): {'test': 45, 'train': 210, 'val': 45}  
Naming strata (persons): {'surname_last': 108, 'initial_first': 92, 'mononymic': 100}  
PAN fifth-character source (persons): {'surname': 108, 'given_name': 63, 'mononym': 100, 'leading_initial': 29}

## OCR field extraction quality (exact match %, 95% Wilson CI)

| document | field | tier | n | exact match % [95% CI] | mean CER % | empty % |
|---|---|---|---|---|---|---|
| aadhaar | aadhaar_number | clean | 1800 | 99.9 [99.7, 100.0] | 0.01 | 0.0 |
| aadhaar | aadhaar_number | mild | 1800 | 99.8 [99.4, 99.9] | 0.02 | 0.0 |
| aadhaar | aadhaar_number | severe | 1800 | 88.3 [86.8, 89.7] | 2.74 | 0.8 |
| aadhaar | dob | clean | 1800 | 99.9 [99.7, 100.0] | 0.01 | 0.0 |
| aadhaar | dob | mild | 1800 | 99.8 [99.5, 99.9] | 0.02 | 0.0 |
| aadhaar | dob | severe | 1800 | 43.1 [40.8, 45.4] | 45.45 | 33.5 |
| aadhaar | name | clean | 1800 | 98.9 [98.4, 99.3] | 0.09 | 0.0 |
| aadhaar | name | mild | 1800 | 98.7 [98.0, 99.1] | 0.10 | 0.0 |
| aadhaar | name | severe | 1800 | 64.4 [62.2, 66.6] | 23.93 | 14.2 |
| pan | dob | clean | 1800 | 99.7 [99.3, 99.8] | 0.03 | 0.0 |
| pan | dob | mild | 1800 | 99.8 [99.4, 99.9] | 0.02 | 0.0 |
| pan | dob | severe | 1800 | 34.9 [32.8, 37.2] | 51.93 | 39.6 |
| pan | father_name | clean | 1800 | 99.9 [99.6, 100.0] | 0.01 | 0.0 |
| pan | father_name | mild | 1800 | 99.9 [99.7, 100.0] | 0.00 | 0.0 |
| pan | father_name | severe | 1800 | 46.7 [44.4, 49.0] | 42.12 | 27.7 |
| pan | name | clean | 1800 | 99.8 [99.4, 99.9] | 0.02 | 0.0 |
| pan | name | mild | 1800 | 99.3 [98.8, 99.6] | 0.10 | 0.0 |
| pan | name | severe | 1800 | 54.6 [52.3, 56.9] | 31.81 | 19.8 |
| pan | pan_number | clean | 1800 | 84.5 [82.8, 86.1] | 1.61 | 0.0 |
| pan | pan_number | mild | 1800 | 85.3 [83.6, 86.9] | 1.56 | 0.0 |
| pan | pan_number | severe | 1800 | 66.7 [64.5, 68.8] | 8.00 | 1.9 |

## Rule-branch flag rate by forgery category

A FAIL here means an applicable rule evaluated FALSE. On C0 it is a false positive; on C4 it is expected to be a miss by construction, so any FAIL on C4 is an OCR-induced false alarm rather than detection of the fabrication.

| document | category | ground-truth text | OCR text |
|---|---|---|---|
| aadhaar | C0 | 0.0 [0.0, 0.2] | 3.8 [3.0, 4.8] |
| aadhaar | C1 | 0.0 [0.0, 0.4] | 3.3 [2.3, 4.7] |
| aadhaar | C2 | 100.0 [99.6, 100.0] | 99.9 [99.4, 100.0] |
| aadhaar | C3 | 0.0 [0.0, 0.4] | 4.8 [3.6, 6.4] |
| aadhaar | C4 | 0.0 [0.0, 0.4] | 3.6 [2.5, 5.0] |
| pan | C0 | 0.0 [0.0, 0.2] | 19.7 [17.9, 21.6] |
| pan | C1 | 0.0 [0.0, 0.4] | 21.9 [19.3, 24.7] |
| pan | C2 | 100.0 [99.6, 100.0] | 97.2 [95.9, 98.1] |
| pan | C3 | 100.0 [99.6, 100.0] | 96.1 [94.6, 97.2] |
| pan | C4 | 0.0 [0.0, 0.4] | 22.6 [19.9, 25.4] |

## Rule-branch false-positive rate on genuine documents (RQ6 input)

| document | tier | n | FP | FP % [95% CI] |
|---|---|---|---|---|
| aadhaar | clean | 600 | 0 | 0.0 [0.0, 0.6] |
| aadhaar | mild | 600 | 0 | 0.0 [0.0, 0.6] |
| aadhaar | severe | 600 | 69 | 11.5 [9.2, 14.3] |
| aadhaar | ALL | 1800 | 69 | 3.8 [3.0, 4.8] |
| pan | clean | 600 | 82 | 13.7 [11.1, 16.6] |
| pan | mild | 600 | 72 | 12.0 [9.6, 14.8] |
| pan | severe | 600 | 200 | 33.3 [29.7, 37.2] |
| pan | ALL | 1800 | 354 | 19.7 [17.9, 21.6] |

## PAN cross-field rule: permissive vs strict, genuine documents only

| subset | source | n | permissive FAIL % | strict FAIL % | SKIPPED % |
|---|---|---|---|---|---|
| ALL | gt | 1800 | 0.0 [0.0, 0.2] | 9.0 [7.8, 10.4] | 0.0 [0.0, 0.2] |
| ALL | ocr | 1800 | 1.9 [1.4, 2.7] | 9.7 [8.4, 11.1] | 21.1 [19.3, 23.1] |
| surname_last | gt | 648 | 0.0 [0.0, 0.6] | 0.0 [0.0, 0.6] | 0.0 [0.0, 0.6] |
| surname_last | ocr | 648 | 2.0 [1.2, 3.4] | 2.2 [1.3, 3.6] | 21.8 [18.8, 25.1] |
| initial_first | gt | 552 | 0.0 [0.0, 0.7] | 29.3 [25.7, 33.3] | 0.0 [0.0, 0.7] |
| initial_first | ocr | 552 | 2.4 [1.4, 4.0] | 26.6 [23.1, 30.5] | 20.8 [17.7, 24.4] |
| mononymic | gt | 600 | 0.0 [0.0, 0.6] | 0.0 [0.0, 0.6] | 0.0 [0.0, 0.6] |
| mononymic | ocr | 600 | 1.5 [0.8, 2.8] | 2.2 [1.3, 3.7] | 20.7 [17.6, 24.1] |
| p5src:leading_initial | gt | 174 | 0.0 [0.0, 2.2] | 93.1 [88.3, 96.0] | 0.0 [0.0, 2.2] |
| p5src:leading_initial | ocr | 174 | 4.0 [2.0, 8.1] | 81.0 [74.6, 86.2] | 13.2 [9.0, 19.1] |
| p5src:given_name | gt | 378 | 0.0 [0.0, 1.0] | 0.0 [0.0, 1.0] | 0.0 [0.0, 1.0] |
| p5src:given_name | ocr | 378 | 1.6 [0.7, 3.4] | 1.6 [0.7, 3.4] | 24.3 [20.3, 28.9] |

## Leakage audit (Table V)

| leakage mode | required | result |
|---|---|---|
| identity | empty person-id intersection | {'test|train': 0, 'test|val': 0, 'train|val': 0} — PASS |
| identifier | empty identifier intersection | {'test|train': 0, 'test|val': 0, 'train|val': 0} — PASS |
| template | every variant in every split | {'train': 6, 'val': 6, 'test': 6} of 6 — PASS |
| near-duplicate | (diagnostic, not gating) | see below |
| augmentation | degradation draws confined to one split | 0 documents span splits — PASS |
| printed values (exact) | no field-value set in two splits | 0 of 2100 span splits — PASS |

Near-duplicate audit uses a 64-bit perceptual hash. The 64-bit hash yields only 5848 distinct values for 10800 images and is not usable here; the 64-bit hash yields 5848. Median distance between two captures of the same document: 6 bits; between different persons: 24 bits.

## Coincidence with issued identifiers

Distinct generated Aadhaar strings: 1083; PAN strings: 1200.

| document | assumed issued population | P(single coincidence) | expected coincidences | P(at least one) |
|---|---|---|---|---|
| aadhaar | 1e+09 | 0.01250 | 13.54 | 1.0000 |
| aadhaar | 1.42e+09 | 0.01775 | 19.22 | 1.0000 |
| pan | 7e+08 | 0.01532 | 18.38 | 1.0000 |
| pan | 8e+08 | 0.01751 | 21.01 | 1.0000 |
