Environment: python 3.13.14, numpy 2.4.4, pillow 12.2.0, opencv 4.13.0, Windows-11-10.0.26200-SP0

Persons (train split): 60; pairs: 360

Median retention of edit energy relative to native size (1.0 = fully kept).

| C1 operation | pairs | 1024x640 | 768x512 | 384x256 | 224x160 |
|---|---|---|---|---|---|
| field_displacement | 87 | 0.97 | 0.97 | 0.89 | 0.69 |
| font_substitution | 60 | 0.98 | 0.96 | 0.90 | 0.76 |
| local_recompression | 87 | 0.89 | 0.83 | 0.32 | 0.16 |
| patch_splice | 60 | 0.98 | 0.97 | 0.91 | 0.83 |
| resample_patch | 66 | 0.87 | 0.86 | 0.26 | 0.11 |
| *reference: white noise* | | 0.80 | 0.71 | 0.18 | 0.06 |

Median retention at 384x256 by tier:

| C1 operation | clean | mild | severe |
|---|---|---|---|
| field_displacement | 0.84 | 0.90 | 0.93 |
| font_substitution | 0.83 | 0.91 | 0.94 |
| local_recompression | 0.11 | 0.32 | 0.70 |
| patch_splice | 0.90 | 0.89 | 0.94 |
| resample_patch | 0.03 | 0.28 | 0.73 |
