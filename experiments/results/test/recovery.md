# Recovery analysis (test split)

Counts of images by which branch flags them. Visual = frozen `tiles` ensemble at t_v. On C0 every flag is a false positive.

## Rules on GT text

| Document | Group | n | Both | Visual only | Rules only | Neither |
|---|---|---|---|---|---|---|
| aadhaar | C0 | 270 | 0 | 15 | 0 | 255 |
| aadhaar | C1 | 135 | 0 | 47 | 0 | 88 |
| aadhaar | C1-fine | 57 | 0 | 14 | 0 | 43 |
| aadhaar | C1-coarse | 78 | 0 | 33 | 0 | 45 |
| aadhaar | C2 | 135 | 9 | 0 | 126 | 0 |
| aadhaar | C3 | 135 | 0 | 5 | 0 | 130 |
| aadhaar | C4 | 135 | 0 | 5 | 0 | 130 |
| pan | C0 | 270 | 0 | 11 | 0 | 259 |
| pan | C1 | 135 | 0 | 54 | 0 | 81 |
| pan | C1-fine | 66 | 0 | 25 | 0 | 41 |
| pan | C1-coarse | 69 | 0 | 29 | 0 | 40 |
| pan | C2 | 135 | 10 | 0 | 125 | 0 |
| pan | C3 | 135 | 4 | 0 | 131 | 0 |
| pan | C4 | 135 | 0 | 11 | 0 | 124 |

## Rules on OCR text

| Document | Group | n | Both | Visual only | Rules only | Neither |
|---|---|---|---|---|---|---|
| aadhaar | C0 | 270 | 1 | 14 | 9 | 246 |
| aadhaar | C1 | 135 | 0 | 47 | 3 | 85 |
| aadhaar | C1-fine | 57 | 0 | 14 | 0 | 43 |
| aadhaar | C1-coarse | 78 | 0 | 33 | 3 | 42 |
| aadhaar | C2 | 135 | 9 | 0 | 126 | 0 |
| aadhaar | C3 | 135 | 0 | 5 | 6 | 124 |
| aadhaar | C4 | 135 | 0 | 5 | 6 | 124 |
| pan | C0 | 270 | 1 | 10 | 48 | 211 |
| pan | C1 | 135 | 7 | 47 | 20 | 61 |
| pan | C1-fine | 66 | 3 | 22 | 6 | 35 |
| pan | C1-coarse | 69 | 4 | 25 | 14 | 26 |
| pan | C2 | 135 | 10 | 0 | 125 | 0 |
| pan | C3 | 135 | 4 | 0 | 126 | 5 |
| pan | C4 | 135 | 1 | 10 | 23 | 101 |
