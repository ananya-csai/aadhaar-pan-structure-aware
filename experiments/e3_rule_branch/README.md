# E3 — Rule-only branch (test split)

Canonical report for roadmap Step 5. Reproduce with:

```
python experiments/e3_rule_branch/run_e3.py
```

It writes the prediction files and full reports (`*_test.json`, `*_test.md`) to `results/`, scored by `experiments/evaluate.py`. The rule branch has no learned parameters or thresholds, so scoring it on the test split tunes nothing. Decisions are the frozen verdicts in `dataset/data/v1/manifest.csv` (`rule_gt_verdict`, `rule_ocr_verdict`); a FAIL verdict counts as a flag.

Test split: 1,620 images from 45 people (540 C0; 270 each of C1–C4). The 95% intervals come from a person-clustered bootstrap (10,000 resamples), because the 1,620 images are not independent.

## Two recall measures — keep them apart

- **Detection recall** = flagged / all forged images (C1–C4). This is the measure comparable with the visual branch and the hybrid, and the one used for RQ2–RQ5.
- **Rule-coverage recall** = flagged / images the rules are designed to catch (`expected_rule = FAIL`: Aadhaar C2, PAN C2, PAN C3). It checks the rule implementation; it is not a detection result.

The earlier version of this README reported only rule-coverage numbers (100% / 99.0% "recall"), with a false-positive rate whose denominator was every image expected to pass, including C1, C4 and Aadhaar C3. Those figures are superseded by the table below.

## Results

| System | Detection recall | FPR on C0 | Precision | F1 | Rule-coverage recall |
|---|---|---|---|---|---|
| Rules, ground-truth text | 37.5 [37.5, 37.5] | 0.0 [0.0, 0.0] | 100.0 | 0.545 | 100.0 |
| Rules, OCR text | 43.1 [41.3, 45.1] | 10.9 [7.4, 14.8] | 88.8 [85.6, 91.8] | 0.581 | 98.8 |

Flag rate (%) by document type and category; on C0 it is the false-positive rate:

| Text | Document | C0 | C1 | C2 | C3 | C4 |
|---|---|---|---|---|---|---|
| Ground truth | Aadhaar | 0.0 | 0.0 | 100.0 | 0.0 | 0.0 |
| Ground truth | PAN | 0.0 | 0.0 | 100.0 | 100.0 | 0.0 |
| OCR | Aadhaar | 3.7 | 2.2 | 100.0 | 4.4 | 4.4 |
| OCR | PAN | 18.1 | 20.0 | 100.0 | 96.3 | 17.8 |

## How to read this

- **Ground-truth text gives perfect rule behaviour by construction.** The rules and the labels come from the same generator. This is a sanity check of the implementation, not evidence of real-world accuracy.
- **Detection recall is 37.5% because the rules can only catch C2 and PAN C3.** C1 (pixel edits), C4 (rule-valid fabricated identifiers) and Aadhaar C3 (no rule reads the Devanagari line) are outside what the rules check.
- **The higher OCR detection recall (43.1%) is not a better detector.** Flags on C1, C4 and Aadhaar C3 under OCR text are OCR-induced false alarms that happen to land on forged images. Their rate matches the C0 false-positive rate of the same document type (Aadhaar about 4%, PAN about 18%). They must not be reported as detection.
- **OCR's cost falls mostly on PAN:** an 18.1% false-positive rate on genuine PAN against 3.7% on Aadhaar. This is the RQ6 measurement on the test split; Section IV, Table VII gives the same effect on the whole corpus.

`reproduce_rule_metrics.py` is the earlier script that produced the rule-coverage figures; it is kept for traceability.
