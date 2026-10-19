# Recovery analysis (val split)

Counts of images by which branch flags them. Visual = frozen `tiles` ensemble at t_v. On C0 every flag is a false positive.

## Rules on GT text

| Document | Group | n | Both | Visual only | Rules only | Neither |
|---|---|---|---|---|---|---|
| aadhaar | C0 | 270 | 0 | 11 | 0 | 259 |
| aadhaar | C1 | 135 | 0 | 45 | 0 | 90 |
| aadhaar | C1-fine | 51 | 0 | 16 | 0 | 35 |
| aadhaar | C1-coarse | 84 | 0 | 29 | 0 | 55 |
| aadhaar | C2 | 135 | 4 | 0 | 131 | 0 |
| aadhaar | C3 | 135 | 0 | 5 | 0 | 130 |
| aadhaar | C4 | 135 | 0 | 7 | 0 | 128 |
| pan | C0 | 270 | 0 | 16 | 0 | 254 |
| pan | C1 | 135 | 0 | 49 | 0 | 86 |
| pan | C1-fine | 54 | 0 | 19 | 0 | 35 |
| pan | C1-coarse | 81 | 0 | 30 | 0 | 51 |
| pan | C2 | 135 | 10 | 0 | 125 | 0 |
| pan | C3 | 135 | 9 | 0 | 126 | 0 |
| pan | C4 | 135 | 0 | 9 | 0 | 126 |

## Rules on OCR text

| Document | Group | n | Both | Visual only | Rules only | Neither |
|---|---|---|---|---|---|---|
| aadhaar | C0 | 270 | 0 | 11 | 9 | 250 |
| aadhaar | C1 | 135 | 0 | 45 | 5 | 85 |
| aadhaar | C1-fine | 51 | 0 | 16 | 2 | 33 |
| aadhaar | C1-coarse | 84 | 0 | 29 | 3 | 52 |
| aadhaar | C2 | 135 | 4 | 0 | 131 | 0 |
| aadhaar | C3 | 135 | 0 | 5 | 7 | 123 |
| aadhaar | C4 | 135 | 0 | 7 | 2 | 126 |
| pan | C0 | 270 | 7 | 9 | 45 | 209 |
| pan | C1 | 135 | 10 | 39 | 17 | 69 |
| pan | C1-fine | 54 | 5 | 14 | 7 | 28 |
| pan | C1-coarse | 81 | 5 | 25 | 10 | 41 |
| pan | C2 | 135 | 10 | 0 | 120 | 5 |
| pan | C3 | 135 | 8 | 1 | 120 | 6 |
| pan | C4 | 135 | 1 | 8 | 32 | 94 |
