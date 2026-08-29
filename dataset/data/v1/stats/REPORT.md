# Dataset v1 — characterisation report

Everything in this report characterises the DATASET and the rule branch operating on it. No visual model is trained and no fusion is performed here, so none of these numbers is a detection result for the hybrid system.

- persons: **300**   documents: **3600**   images: **10800**
- genuine images (C0): **3600**   forged (C1-C4): **7200**
- on disk: **0.874 GiB**

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
| aadhaar | aadhaar_number | clean | 1800 | 99.8 [99.5, 99.9] | 0.01 | 0.0 |
| aadhaar | aadhaar_number | mild | 1800 | 99.4 [99.0, 99.7] | 0.07 | 0.0 |
| aadhaar | aadhaar_number | severe | 1800 | 88.3 [86.8, 89.7] | 2.50 | 0.6 |
| aadhaar | dob | clean | 1800 | 100.0 [99.8, 100.0] | 0.00 | 0.0 |
| aadhaar | dob | mild | 1800 | 100.0 [99.8, 100.0] | 0.00 | 0.0 |
| aadhaar | dob | severe | 1800 | 41.5 [39.2, 43.8] | 45.33 | 33.7 |
| aadhaar | name | clean | 1800 | 98.8 [98.2, 99.2] | 0.10 | 0.0 |
| aadhaar | name | mild | 1800 | 98.7 [98.1, 99.2] | 0.10 | 0.0 |
| aadhaar | name | severe | 1800 | 64.7 [62.5, 66.9] | 22.22 | 10.8 |
| pan | dob | clean | 1800 | 99.7 [99.3, 99.9] | 0.03 | 0.0 |
| pan | dob | mild | 1800 | 99.9 [99.7, 100.0] | 0.01 | 0.0 |
| pan | dob | severe | 1800 | 33.8 [31.7, 36.0] | 50.84 | 36.7 |
| pan | father_name | clean | 1800 | 100.0 [99.8, 100.0] | 0.00 | 0.0 |
| pan | father_name | mild | 1800 | 100.0 [99.8, 100.0] | 0.00 | 0.0 |
| pan | father_name | severe | 1800 | 44.7 [42.4, 47.0] | 43.68 | 26.5 |
| pan | name | clean | 1800 | 99.7 [99.3, 99.8] | 0.04 | 0.0 |
| pan | name | mild | 1800 | 99.6 [99.2, 99.8] | 0.06 | 0.0 |
| pan | name | severe | 1800 | 53.8 [51.5, 56.1] | 31.78 | 18.3 |
| pan | pan_number | clean | 1800 | 85.2 [83.5, 86.7] | 1.57 | 0.0 |
| pan | pan_number | mild | 1800 | 84.9 [83.2, 86.5] | 1.57 | 0.0 |
| pan | pan_number | severe | 1800 | 67.7 [65.5, 69.8] | 7.30 | 1.3 |

## Rule-branch flag rate by forgery category

A FAIL here means an applicable rule evaluated FALSE. On C0 it is a false positive; on C4 it is expected to be a miss by construction, so any FAIL on C4 is an OCR-induced false alarm rather than detection of the fabrication.

| document | category | ground-truth text | OCR text |
|---|---|---|---|
| aadhaar | C0 | 0.0 [0.0, 0.2] | 4.1 [3.3, 5.1] |
| aadhaar | C1 | 0.0 [0.0, 0.4] | 4.1 [3.0, 5.6] |
| aadhaar | C2 | 100.0 [99.6, 100.0] | 99.8 [99.2, 99.9] |
| aadhaar | C3 | 0.0 [0.0, 0.4] | 3.9 [2.8, 5.4] |
| aadhaar | C4 | 0.0 [0.0, 0.4] | 4.0 [2.9, 5.5] |
| pan | C0 | 0.0 [0.0, 0.2] | 18.9 [17.1, 20.8] |
| pan | C1 | 0.0 [0.0, 0.4] | 20.8 [18.3, 23.5] |
| pan | C2 | 100.0 [99.6, 100.0] | 97.1 [95.8, 98.0] |
| pan | C3 | 100.0 [99.6, 100.0] | 96.2 [94.8, 97.3] |
| pan | C4 | 0.0 [0.0, 0.4] | 23.2 [20.6, 26.1] |

## Rule-branch false-positive rate on genuine documents (RQ6 input)

| document | tier | n | FP | FP % [95% CI] |
|---|---|---|---|---|
| aadhaar | clean | 600 | 2 | 0.3 [0.1, 1.2] |
| aadhaar | mild | 600 | 2 | 0.3 [0.1, 1.2] |
| aadhaar | severe | 600 | 70 | 11.7 [9.3, 14.5] |
| aadhaar | ALL | 1800 | 74 | 4.1 [3.3, 5.1] |
| pan | clean | 600 | 76 | 12.7 [10.2, 15.6] |
| pan | mild | 600 | 73 | 12.2 [9.8, 15.0] |
| pan | severe | 600 | 191 | 31.8 [28.2, 35.7] |
| pan | ALL | 1800 | 340 | 18.9 [17.1, 20.8] |

## PAN cross-field rule: permissive vs strict, genuine documents only

| subset | source | n | permissive FAIL % | strict FAIL % | SKIPPED % |
|---|---|---|---|---|---|
| ALL | gt | 1800 | 0.0 [0.0, 0.2] | 9.0 [7.8, 10.4] | 0.0 [0.0, 0.2] |
| ALL | ocr | 1800 | 1.9 [1.4, 2.6] | 9.4 [8.2, 10.9] | 20.2 [18.4, 22.1] |
| surname_last | gt | 648 | 0.0 [0.0, 0.6] | 0.0 [0.0, 0.6] | 0.0 [0.0, 0.6] |
| surname_last | ocr | 648 | 1.1 [0.5, 2.2] | 1.4 [0.7, 2.6] | 21.0 [18.0, 24.3] |
| initial_first | gt | 552 | 0.0 [0.0, 0.7] | 29.3 [25.7, 33.3] | 0.0 [0.0, 0.7] |
| initial_first | ocr | 552 | 3.8 [2.5, 5.7] | 27.4 [23.8, 31.2] | 19.4 [16.3, 22.9] |
| mononymic | gt | 600 | 0.0 [0.0, 0.6] | 0.0 [0.0, 0.6] | 0.0 [0.0, 0.6] |
| mononymic | ocr | 600 | 1.0 [0.5, 2.2] | 1.7 [0.9, 3.0] | 20.2 [17.2, 23.6] |
| p5src:leading_initial | gt | 174 | 0.0 [0.0, 2.2] | 93.1 [88.3, 96.0] | 0.0 [0.0, 2.2] |
| p5src:leading_initial | ocr | 174 | 6.9 [4.0, 11.7] | 81.0 [74.6, 86.2] | 13.2 [9.0, 19.1] |
| p5src:given_name | gt | 378 | 0.0 [0.0, 1.0] | 0.0 [0.0, 1.0] | 0.0 [0.0, 1.0] |
| p5src:given_name | ocr | 378 | 2.4 [1.3, 4.5] | 2.6 [1.4, 4.8] | 22.2 [18.3, 26.7] |

## Leakage audit (Table V)

| leakage mode | required | result |
|---|---|---|
| identity | empty person-id intersection | {'test|train': 0, 'test|val': 0, 'train|val': 0} — PASS |
| identifier | empty identifier intersection | {'test|train': 0, 'test|val': 0, 'train|val': 0} — PASS |
| template | every variant in every split | {'train': 6, 'val': 6, 'test': 6} of 6 — PASS |
| near-duplicate | (diagnostic, not gating) | see below |
| augmentation | degradation draws confined to one split | 0 documents span splits — PASS |
| printed values (exact) | no field-value set in two splits | 0 of 2100 span splits — PASS |

Near-duplicate audit uses a 256-bit perceptual hash. The 64-bit hash yields only 5824 distinct values for 10800 images and is not usable here; the 256-bit hash yields 10757. Median distance between two captures of the same document: 30 bits; between different persons: 108 bits.

## Coincidence with issued identifiers

Distinct generated Aadhaar strings: 1083; PAN strings: 1200.

| document | assumed issued population | P(single coincidence) | expected coincidences | P(at least one) |
|---|---|---|---|---|
| aadhaar | 1e+09 | 0.01250 | 13.54 | 1.0000 |
| aadhaar | 1.42e+09 | 0.01775 | 19.22 | 1.0000 |
| pan | 7e+08 | 0.01532 | 18.38 | 1.0000 |
| pan | 8e+08 | 0.01751 | 21.01 | 1.0000 |
