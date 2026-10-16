# Near-Duplicate Audit

## Findings

- Person-level split check: PASS.
- Missing manifest-referenced images: 0.
- Exact duplicate image hashes across splits: 0.
- Perceptual-hash audit (pHash distance <= 4): 1,214,863 candidate pairs.
- Visual inspection: sampled documents show different content with similar layouts.
- First 20 zero-distance pHash pairs: all had different file bytes.

## Interpretation

The pHash audit generates many candidates because documents share similar layouts. These candidates are not confirmed duplicates or evidence of data leakage.

## Limitation

The visual sample is not exhaustive. The pHash audit alone cannot establish that all cross-split near-duplicates are absent.

## Decision

Preserve the frozen dataset. Do not remove images based only on pHash matches. Continue with preprocessing validation and retain this limitation in the experiment report.

## Artefacts
- `near_duplicate_candidates.csv` (224 MB) is not committed: it exceeds GitHub's 100 MB file limit. Regenerate it with `python experiments/verify_near_duplicates.py`.
- `near_duplicate_contact_sheet.jpg` is committed as the visual-inspection record.
