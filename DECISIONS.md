# Experiment Protocol Decisions

**Status:** Approved (see Section 11).

**Dataset:** Synthetic Aadhaar/PAN-format forgery detection

**Primary task:** C0 versus C1 classification

## 1. Dataset and reproducibility

- Original frozen dataset tag: `v1.0-dataset`
- Environment/setup tag: `v1.0.1-dataset`
- Original dataset commit: `d766fb2d0a5436913a52830458dda39c8fe946e2`
- Environment/setup commit: `dbb654e30e13a650d85d237a5986c9f82a02c30d`
- Corpus SHA-256: `f3302cc72561a46ca869788bd4f31f3fcbbf562a2d65fc750b157df12d700394`
- Corpus size: 10,800 images.
- Do not regenerate or modify the frozen dataset.
- Use the canonical manifest for dataset membership and split assignment.

## 2. Image preprocessing

- Primary input canvas: 768 × 512 pixels (width × height). Changed from 384 × 256 by Amendment A1 (Section 12).
- Sensitivity canvas: 384 × 256 pixels (width × height). The 224 × 160 arm is dropped (Amendment A1).
- Preserve aspect ratio and pad to the target canvas.
- Padding color: white before normalization.
- Image channels: RGB.
- Normalization: ImageNet mean and standard deviation.
- Keep other experimental settings unchanged in the resolution-sensitivity experiment wherever possible.

## 3. Classification and splits

- Primary learned task: C0 versus C1, selected using the manifest's `forgery_category` column.
- Training split: model fitting only.
- Validation split: checkpoint selection, threshold selection and calibration.
- Test split: evaluate only after the model, preprocessing, checkpoint, calibration and threshold are frozen.
- C2–C4 are not primary training classes for this experiment.

## 4. Calibration and operating point

- Use validation data only for calibration.
- Target validation C0 false-positive rate (FPR): at most 5%.
- Choose the threshold that maximizes C1 recall while satisfying the validation FPR constraint.
- Document threshold ties and cases where no threshold satisfies the constraint.
- Report realized test FPR without retuning the threshold on test data.

## 5. Random seeds and fusion

- Initial target: five pre-registered random seeds.
- Combine seed predictions by averaging predicted probabilities.
- Record all seeds and the aggregation implementation before test evaluation.
- Document any compute-driven deviation before test evaluation.

## 6. Mechanism-aware recall

Definition (needed from roadmap Step 12; not used during training):

- **Eligible images:** those the rules are designed to catch (`expected_rule = FAIL`): Aadhaar C2, PAN C2 and PAN C3. Aadhaar C3 is reported separately as an expected miss (no rule reads the Devanagari line). C1 and C4 are not eligible.
- **Counted as mechanism-aware:** the image is flagged **and** the failing check is the one tied to the corrupted field: Aadhaar C2 → length/checksum check on the Aadhaar number; PAN C2 → format/category check on the PAN; PAN C3 → fifth-character cross-field check.
- **Mechanism-aware recall** = mechanism-aware detections / eligible images, reported by document type and category, for GT text and OCR text.
- A flag raised for a different reason counts toward ordinary detection recall but not toward this metric; such cases are reported as over-attribution.


## 7. Reference OCR environment

The dataset tag annotation records:

- Tesseract: 5.3.4
- Leptonica: 1.82.0
- Language model: English only

Record the actual OCR environment used in each experiment and any differences from this reference setup.

## 8. Research venue

ICDAR 2027 is a candidate venue only. Verify its official scope, submission requirements and deadlines before making a submission decision.

## 9. Audit status

- Person-level split separation: passed in the recorded audit.
- Missing referenced images: none found in the recorded audit.
- Exact duplicate hashes across splits: none found in the recorded audit.
- Perceptual-hash near-duplicate audit: inconclusive. The inspected candidates showed different document content with similar layouts. This neither establishes leakage nor proves its absence.

## 10. Required pre-training checks

Before full training:

1. Confirm collaborator/mentor agreement on the protocol.
2. Verify dataset tags, manifest hashes and repository state.
3. Validate the manifest-driven loader and split counts.
4. Run a GPU forward/backward smoke test at 768 × 512. Choose the batch size by memory only: the largest of 32, 16 or 8 that trains under mixed precision with peak reserved memory at most 92% of physical VRAM. (Correction, 17 Oct 2026: the first rule said "without running out of memory". On Windows the driver can silently spill GPU memory into system RAM, so batch 32 "fitted" on the 8 GB RTX 4060 Laptop GPU at 10.78 GB peak and 13.4 s per step. That is not a usable configuration, so the rule now requires the batch to stay inside physical VRAM.) If it is below 32, use gradient accumulation to an effective batch of 32. Record GPU model, VRAM, batch size and seconds per epoch.
5. Run a tiny-overfit test on a small, fixed training subset containing C0 and C1 examples.
6. Save configurations and logs needed to reproduce the experiment.

Do not use test-set results to choose preprocessing, checkpoints, calibration, thresholds or other model settings.

## 11. Approval record

- Lead researcher: [Soham Phulwaria , Ananya Shukla] — approved on [2026-10-3].
- Collaborator: [Soham Phulwaria , Ananya Shukla] — approved on [2026-10-3].
- Faculty mentor: [Dinesh Saini] — approved on [2026-10-3].
- Scope of approval: Sections 1–5, 7–10, 12 (Amendment A1) and 13.
- Section 6 definition (written 18 Oct 2026) confirmed by all three: [yes].
- Protocol commit: the commit tagged `protocol-e2-final`.
- Tag `protocol-e2-v1` (commit `16a867d`) marks Amendment A1 and the first pre-training checks. It was created before the approval above was recorded and before the training settings in Section 13 were decided. The protocol used for E2 will be tagged `protocol-e2-final` once Section 13 is filled in and approved.
- Tag `protocol-e2-final` was first created on 17 Oct 2026 at commit `f76bdfb`, where this section still read "pending". It was deleted and re-created on the commit that records the approvals above, before any E2 training run. No model had been trained at either point.

## 12. Amendment A1 — input resolution (before any model training)

**Status:** Approved (see Section 11).

**What changed**

- Primary canvas: 384 × 256 → **768 × 512**.
- Sensitivity canvas: 224 × 160 → **384 × 256** (the existing, fingerprinted cache).
- Same resize policy for both: aspect-preserving LANCZOS, white pad, centred.
- New pre-registered reporting rule: C1 recall is reported **per `c1_op`**, and for two pre-declared groups:
  - *fine-trace edits*: `local_recompression`, `resample_patch`;
  - *coarse edits*: `font_substitution`, `field_displacement`, `patch_splice`.
- Results by quality tier within each operation are exploratory (about 18 test images per operation and tier).

**Why**

`experiments/measure_edit_survival.py` re-creates matched C0/C1 pairs from the generator (same render seed, same degradation seed, train-split persons only), so each pair differs only by the edit. It measures how much of the edit's pixel energy survives resizing, relative to the native image. Median retention (60 train persons, 360 pairs):

| C1 operation | 1024×640 | 768×512 | 384×256 | 224×160 |
|---|---|---|---|---|
| field_displacement | 0.97 | 0.97 | 0.89 | 0.69 |
| font_substitution | 0.98 | 0.96 | 0.90 | 0.75 |
| patch_splice | 0.98 | 0.97 | 0.91 | 0.84 |
| local_recompression | 0.89 | 0.82 | 0.30 | 0.15 |
| resample_patch | 0.89 | 0.87 | 0.26 | 0.10 |

On clean-tier images at 384 × 256, retention falls to 0.10 (recompression) and 0.03 (resampling). These two operations make up about 41% of C1 (747 of 1,800 images). At 384 × 256, a visual-baseline miss on them would mainly reflect our preprocessing, not the detector, and that would bias RQ1 and RQ3 in favour of the rule branch. 768 × 512 keeps most of the evidence with 60% of the pixels of 1024 × 640 (and 4× the pixels of 384 × 256). Going up to 1024 × 640 adds little (0.89 vs 0.82–0.87 for the fine-trace edits).

**Limits of this evidence**

- Retention is an upper bound on usable evidence. The detector never sees the reference C0, so high retention does not mean a model will detect the edit.
- The measurement environment's library versions are recorded with its output. Values may differ slightly from the pinned corpus build; the conclusion does not depend on small differences.

**Why this is a legitimate change**

The decision uses only the data generator and train-split persons. No model has been trained and no validation or test score has been seen. C2–C4 are re-rendered without pixel edits (docs/DECISIONS.md, D1), so the rule branch is unaffected.

## 13. Training settings for E2 (to decide before any full training run)

**Status:** Approved as proposed in the table below (see Section 11). `experiments/e2_visual/train.py` implements exactly these settings.

| Setting | Proposal | Reason |
|---|---|---|
| Pretrained weights | torchvision `IMAGENET1K_V2` | Standard ImageNet ResNet-50 weights; used in the smoke test |
| Augmentation | None | Flips and rotations produce documents that cannot exist; the three quality tiers already vary the images |
| Class weighting | None (plain BCE) | The decision threshold is set on validation at 5% C0 FPR, so loss weighting is not needed to handle the 2:1 imbalance |
| Optimizer | AdamW, weight decay 1e-4 | Common, stable default for fine-tuning |
| Learning rate | 1e-4, cosine decay, 1 warm-up epoch | Passed the tiny-overfit check at 1e-4 |
| Batch size | From the corrected smoke test; gradient accumulation to an effective 32 | Section 10, item 4 |
| Maximum epochs | 30 | Upper bound; early stopping decides the actual length |
| Early stopping | Validation PR-AUC (C0 vs C1), patience 5 epochs, keep the best epoch | PR-AUC fits the 2:1 imbalance and does not depend on a threshold |
| Mixed precision | float16 autocast with gradient scaling | Needed to fit 768 × 512 in 8 GB |
| Seeds | 0, 1, 2, 3, 4 for both canvases | Section 5 |
| Determinism | Fixed seeds; cuDNN benchmark off | Results are averaged over seeds, so exact bit-level repeatability is not required |
| Data loader | Shuffle the training set each epoch with a seeded generator | Reproducible order per seed |

## 14. Amendment A2 — validation-only model development for the visual baseline

**Status:** proposed 18 Oct 2026 by lead researcher; mentor informed on: ________ (record the date; this does not block training because the test split is untouched).

**What happened.** The first E2 run (768 × 512, variant `base`, seed 0; commit `8392d83`) trained without errors but did not generalise:

- training AUROC 1.00 (training loss 0.002), validation AUROC 0.578, validation PR-AUC 0.448 (chance PR-AUC = 0.333);
- validation AUROC by C1 operation: font_substitution 0.73, patch_splice 0.63, local_recompression 0.56, resample_patch 0.56, field_displacement 0.48;
- Aadhaar 0.62, PAN 0.54.

No pipeline fault was found: labels and splits match the manifest, and the model fits its training data perfectly. Field displacement, whose evidence survives almost fully at 768 × 512 (Section 12), is still at chance, so the failure is overfitting rather than input resolution. A near-chance visual baseline would make the incremental value of the rule branch (RQ3) look larger than it is, and reviewers would call it a weak baseline.

**What is allowed.** Model development uses training and validation data only. The test split stays sealed: `scores_test.csv` files are written but not opened before Step 15. Every variant tried is kept and reported with its validation metrics (appendix of the paper).

**Candidate added now: variant `reg`.** Same as `base` except:
- augmentation that keeps forensic traces: integer-pixel shift up to ±16 px with white fill (no resampling), per-image contrast ×[0.9, 1.1] and brightness ±0.05; no blur, resizing or re-compression;
- dropout 0.5 before the one-logit head;
- AdamW weight decay 0.05.

**Selection rule.** Compare variants on validation PR-AUC (C0 vs C1) at 768 × 512, seed 0. Prefer the simpler variant unless the more complex one is at least 0.03 higher. The selected variant is then run with seeds 0–4 at both 768 × 512 and 384 × 256, and becomes the visual branch for all later steps.

**If `reg` is also near chance** (validation AUROC below 0.65), the next candidate is a tile-based detector at native resolution: overlapping tiles scored by the same ResNet-50, with the document score taken as the maximum over tiles. It will be specified here before it is run. If no candidate generalises, the paper reports a weak visual baseline as a finding and limits RQ3 claims to it.

