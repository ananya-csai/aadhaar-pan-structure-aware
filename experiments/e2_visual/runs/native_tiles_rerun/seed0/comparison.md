# Step 21 re-run, tiles seed 0: FAIL

| | Original | Re-run |
|---|---|---|
| best epoch / epochs run | 12 / 17 | 12 / 17 |
| minutes | 42.6 | 42.3 |
| val AUROC (C0 vs C1) | 0.699 | 0.699 |
| val PR-AUC (C0 vs C1) | 0.627 | 0.627 |

## Checks

- FAIL: config identical (except commit/env)
- FAIL: edit regions identical
- PASS: val AUROC in [0.685, 0.773]
- PASS: val PR-AUC in [0.611, 0.684]
- PASS: summary metrics recomputed from scores

Config differences: {'c1_regions_sha256': ('b0138b52d37f7312b2b77e6f0735e5a429d62427c11f4175f0cfe60173597c91', 'c5417e9fcc6576c17dddf062d19040382b2aba3b773f8c4c09970f4c7e2e9618')}
Environment differences: {'platform': ('Windows-11-10.0.26200-SP0', 'Windows-11-10.0.26300-SP0')}

Validation logits, all 1620 images: Pearson 1.000, Spearman 1.000, max |diff| 0.00, bit-identical: True (not expected; not part of the rule).

| Epoch | original val PR-AUC | re-run val PR-AUC |
|---|---|---|
| 1 | 0.35578 | 0.35578 |
| 2 | 0.44288 | 0.44288 |
| 3 | 0.48553 | 0.48553 |
| 4 | 0.56423 | 0.56423 |
| 5 | 0.58711 | 0.58711 |
| 6 | 0.60325 | 0.60325 |
| 7 | 0.58058 | 0.58058 |
| 8 | 0.59338 | 0.59338 |
| 9 | 0.59297 | 0.59297 |
| 10 | 0.61746 | 0.61746 |
| 11 | 0.59873 | 0.59873 |
| 12 | 0.62714 | 0.62714 |
| 13 | 0.61513 | 0.61513 |
| 14 | 0.61641 | 0.61641 |
| 15 | 0.59167 | 0.59167 |
| 16 | 0.61888 | 0.61888 |
| 17 | 0.60807 | 0.60807 |
