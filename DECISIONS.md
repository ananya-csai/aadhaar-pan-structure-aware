# Experiment Protocol Decisions

**Status:** Approved (see Section 11).

**Dataset:** Synthetic Aadhaar/PAN-format forgery detection

**Primary task:** C0 versus C1 classification

## 1. Dataset and reproducibility

- Original frozen dataset tag: `v1.0-dataset`
- Environment/setup tag: `v1.0.1-dataset`
- Original dataset commit: `d766fb2d0a5436913a52830458dda39c8fe946e2`
- Environment/setup commit: `dbb654e30e13a650d85d237a5986c9f82a02c30d`
- Corpus SHA-256: `7253245a10732303a0b22520a502a0e1f1390bf4a88b83e77ea920781abdedef` (10,800 images, 941,456,686 bytes). Corrected 20 Oct 2026, see Section 18; the value first recorded here, `f3302cc7…0394`, belongs to the 29 Aug pre-freeze build.
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

### A2 results so far (validation only, 768 × 512, seed 0)

| Variant | Best epoch | Val PR-AUC | Val AUROC | Note |
|---|---|---|---|---|
| `base` | 18 | 0.448 | 0.578 | memorised training set (train loss 0.002) |
| `reg` | 5 | 0.435 | 0.564 | no memorisation, no generalisation (train loss 0.58) |

`reg` is below 0.65 AUROC, so by the rule above the tile-based candidate is specified next and then run.

### Candidate `tiles` — specification (fixed before it is run)

- **Input:** the released JPEG at its original size (at most 1012 × 638), placed top-left on a white 1024 × 640 canvas. No resizing, so every pixel of evidence is kept (Section 12).
- **Tiles:** fixed grid of 15 overlapping 256 × 256 tiles (x = 0, 192, 384, 576, 768; y = 0, 192, 384).
- **Tile labels (training only):** all tiles of C0 images are negative. For C1, a tile is positive if it holds at least 25% of the edit region's area, ignored if it overlaps less, and negative otherwise. Edit regions come from `c1_region` in `manifest.jsonl`, mapped into released-image coordinates by recomputing the generator's homography from `degrade_seed` (`experiments/e2_visual/map_c1_regions.py`). The mapping reproduces the stored layout-independent boxes exactly. Every C1 image has at least one positive tile; train has 2,751 positive and 52,929 negative tiles.
- **Sampling:** each epoch uses all positive tiles plus 8 times as many negative tiles, drawn afresh with a seeded generator.
- **Model and training:** as `base`. ResNet-50 IMAGENET1K_V2 with a one-logit head, plain BCE, no augmentation, AdamW lr 1e-4 and weight decay 1e-4, 1 warm-up epoch then cosine decay over 30 epochs, fp16, batch 32, patience 5.
- **Document score:** maximum tile logit. No region information is used at validation or test time. Early stopping uses document-level validation PR-AUC (C0 vs C1).
- **Selection:** `tiles` replaces `base` only if its validation PR-AUC (seed 0) is at least 0.03 higher (0.478 or more).
- **If `tiles` is selected:** the resolution analysis (E-res) and the use of the 384 × 256 arm are re-specified as Amendment A3 before any test scoring.

## 15. Amendment A3 — visual branch selected; resolution analysis re-specified

**Status:** recorded 18 Oct 2026, before any test scoring; mentor informed on: ________.

**Selection (Section 14 rule).** `tiles`, seed 0: best epoch 12, validation PR-AUC 0.627, AUROC 0.699. This passes the 0.478 threshold, so `tiles` is the visual branch for every later step (calibration, fusion, test).

Validation AUROC by subgroup, seed 0 (`base` → `tiles`): all C1 0.578 → 0.699; fine-trace 0.559 → 0.722; coarse 0.590 → 0.684; clean 0.603 → 0.842; mild 0.613 → 0.671; severe 0.517 → 0.535; Aadhaar 0.620 → 0.691; PAN 0.535 → 0.709. For 195 of 270 validation C1 images, the highest-scoring tile overlaps the edit. C2–C4 images score like C0 (median document logit about −2.7), as expected for re-rendered forgeries with no pixel trace.

**Runs for E2.**
- Primary: `tiles`, seeds 0–4 (`train_tiles.py`).
- Comparison: `base` (768 × 512 whole-document), seeds 0–4 (`train.py --variant base`). It is used only in the analysis below, never in fusion.
- `reg` stays as a single reported pilot (seed 0).
- The 384 × 256 training arm is dropped. With a tile model at native resolution, a down-scaled whole-document arm no longer tests the primary model. The effect of down-scaling is already measured directly in Section 12.

**E-res is replaced by E-vis (visual input handling, RQ1).** Compare C1 detection of `tiles` (native, local) and `base` (768 × 512, whole document): AUROC and recall at the frozen operating point, per C1 group (fine-trace / coarse), per edit type and per quality tier, averaged over 5 seeds with person-clustered bootstrap CIs. Report the Section 12 edit-survival measurement alongside. This analysis is descriptive: it compares two pre-specified models and does not choose between them again.

**Limitation to state.** `tiles` uses edit locations during training (tile labels). No location information is used at validation or test time.

**Run log note (19 Oct 2026).** An automatic Windows update stopped `base` seed 3 before its first epoch finished. It was re-run from scratch, and the incomplete folder was replaced as `train.py` intends. The update changed the OS build from Windows 11 10.0.26200 to 10.0.26300. `base` seeds 3 and 4 ran on the new build; all other runs ran on the old one. Python, PyTorch, CUDA, cuDNN, GPU and code are unchanged (recorded in each `config.json`).

## 16. Amendment A4 — evidence fusion (roadmap Step 14, validation only)

**Status:** recorded 19 Oct 2026, before any test scoring. Approval (required before the tag `frozen-before-test` is created):
- Lead researcher / collaborator: [Soham Phulwaria] — approved on [2026-10-20].
- Lead researcher / collaborator: [Ananya Shukla] — approved on [2026-10-20].
- Faculty mentor: [Dinesh Saini] — approved on [2026-10-20].
- Scope of approval: Section 16 (Amendment A4) and the parameters in `experiments/fusion/frozen_fusion.json` and `experiments/e2_visual/frozen/`.

**Why an amendment is needed.** On validation C0, OCR-text rules flag 11.3% of documents (Aadhaar 3.3%, PAN 19.3%); with ground-truth text they flag 0%. Under OCR text, a hard OR of the visual and rule flags therefore cannot meet the 5% FPR operating point of Section 4. The fusion rules below fix how this is handled. They were written after inspecting validation results only; the test split is untouched.

**Inputs.**
- `p_v`: the calibrated 5-seed `tiles` ensemble probability (Section 15), computed from per-seed logits and stored temperatures by `experiments/score_frozen.py:ensemble`. The same function is used for validation (fitting) and test (scoring), so both are computed identically.
- `z_v` = logit(p_v); `t_v` = frozen visual threshold (val C0 FPR ≤ 5%).
- `r` = 1 if the rule verdict is FAIL, under GT text (`rule_gt_verdict`, oracle) and under OCR text (`rule_ocr_verdict`).
- `pan` = 1 for PAN.

**Systems (all reported, by document type and C0–C4).**
1. Visual only: p_v ≥ t_v.
2. Rules only: r = 1 (GT and OCR).
3. OR: (p_v ≥ t_v) or r = 1. AND: (p_v ≥ t_v) and r = 1. These are binary rules, reported at the FPR they reach and never forced to 5%.
4. **Primary hybrid — logistic fusion:** s = sigmoid(w0 + w1·z_v + w2·r + w3·r·pan), L2-penalised (C = 1, intercept unpenalised, as in scikit-learn's default). Fitted on all 1,620 validation images (forged vs C0), separately for GT and OCR. The r·pan term lets the model learn that PAN rule flags are less reliable under OCR, and keeps the Aadhaar/PAN asymmetry of Table III.
5. Hybrid thresholds: (a) primary — max recall subject to val C0 FPR ≤ 5%; (b) **matched-FPR** — at the validation FPR of each binary system that exceeds 5% (rules_OCR, OR_OCR), so fusion and that system are compared at equal false-positive cost.

**Primary comparisons.** Hybrid vs visual only at 5% FPR (RQ3); hybrid vs rules only at matched FPR (RQ3); GT vs OCR versions (RQ4); Aadhaar vs PAN (RQ5); C0 false-positive rates of every system (RQ6). Threshold-free AUROC and PR-AUC are reported for continuous scores. The test split uses exactly the coefficients and thresholds in `experiments/fusion/frozen_fusion.json`, applied by `experiments/score_frozen.py --split test`.

**Validation results (record only; test numbers will differ).**
- At 5% FPR: visual recall 0.128 (C1 0.348); logistic-GT 0.481 (rules-GT alone 0.375 at 0% FPR).
- Logistic-OCR: 0.242 at 5% FPR. At matched FPR 0.113 it reaches 0.481 vs 0.432 for rules-OCR, mainly through C1 (0.119 → 0.319).
- Logistic AUROC: GT 0.761, OCR 0.729; visual 0.584 (forged vs C0, all categories).

**Numerical precision note.** Temperatures are stored at full precision. Fitting the fusion on 6-decimal rounded probabilities, as in the first draft of this step, flipped one validation image at the threshold when probabilities were recomputed from logits. With the shared function, `score_frozen.py --split val` reproduces `experiments/fusion/validation_report.md` exactly. The frozen files are generated on one machine from the committed run scores. Every threshold (visual t_v and all fusion thresholds, via the shared `operating_point` function) is placed halfway between the highest negative score that may not be flagged and the next higher validation score, not one floating-point step above it. Cross-platform differences are at the 16th significant digit, so they cannot move any validation image across a threshold. Validation FPR and recall are unchanged by this rule (the same images are flagged).

## 17. Research question RQ6 and other recorded decisions (19 Oct 2026)

- **RQ6 is part of the study.** The paper (Section I-D) states six research questions. RQ6 asks what false-positive rate structural/semantic validation imposes on genuine documents, as a function of image quality, OCR error and naming convention. This log and the roadmap previously listed RQ1–RQ5 only. Analyses map to RQ6 through the C0 FPR of every system (Section 16), Tables VI–VIII of Section IV and E8.
- **Section IV numbers (roadmap Step 3).** `paper/generated/` is regenerated from the frozen `dataset_stats.json`. The earlier numbers (4.1% / 18.9% / 5,824) came from the pre-freeze build. The 256-bit hash analysis is not reproducible from frozen artefacts and was removed from the text; the 64-bit audit is reported.
- **Learned leakage probe (roadmap Step 7).** Its positive control is at chance, so it certifies nothing and is reported as such. The exact difference audit carries the claim. The visual branch's C2/C3/C4-vs-C0 separability on test is reported as a bounding check (validation AUROC 0.525 / 0.526 / 0.506; C1 0.780).
- **Recall definitions.** Detection recall (all forged) is the cross-system metric. Rule-coverage recall (expected FAIL only) and mechanism-aware recall (Section 6) are reported separately and labelled.

## 18. Correction — corpus hash (20 Oct 2026)

- **What was wrong.** `dataset/data/v1/CORPUS_SHA256.txt` and Section 1 recorded `f3302cc72561a46ca869788bd4f31f3fcbbf562a2d65fc750b157df12d700394` (10,800 images, 938,517,904 bytes). That stamp was written on 29 Aug 2026 (`d766fb2`) for the pre-freeze build. The corpus frozen in `976eade` (9 Oct 2026) was rebuilt on the GPU laptop, and the stamp was not refreshed. `corpus_checksum.py --verify` therefore reported a mismatch on the frozen images (roadmap Step 2, 20 Oct 2026).
- **Evidence that the frozen images are intact.** `dataset/scripts/verify_corpus_files.py` checked all 10,800 images on the GPU laptop against `manifest.jsonl`: none missing, no size mismatches, no extra files. The total, 941,456,686 bytes, equals the sum of the manifest's per-image `bytes` and differs from the old stamp's total, which confirms that the old stamp belongs to a different build. Log: `experiments/logs/corpus_verify_2026-10-20.txt`.
- **Correct value.** `7253245a10732303a0b22520a502a0e1f1390bf4a88b83e77ea920781abdedef`, 10,800 images, 941,456,686 bytes, now in `CORPUS_SHA256.txt`.
- **Effect on results: none.** The manifest (labels, splits, rule and OCR verdicts), the resize caches, the edit regions and every training run were produced from the 9 Oct images. Only the recorded hash was wrong. No image, label or result changes.
- **Tags.** `v1.0-dataset` and `v1.0.1-dataset` are not moved. The corrected stamp is committed as a new commit, consistent with the rule not to rewrite pushed history.

## 19. Amendment A5 — per-check fusion (post-hoc; recorded 21 Oct 2026, after the test split was scored)

**Status.** Post-hoc. Written after the single test scoring of 21 Oct 2026 (Step 15, tag `frozen-before-test`), before any A5 model was fitted. A4 remains the primary, pre-registered result. A5 is reported beside it and is always labelled post-hoc. Agreed by Soham Phulwaria on 21 Oct 2026; Ananya Shukla and Dinesh Saini to confirm.

**Motivation (from the test results).** Under OCR text, the A4 fusion has one rule input r ("any check failed"). On genuine PAN, the format check fails on 15.2% of documents (OCR misreads), while the cross-field (semantic) check fails on 3.0% and still catches 76.3% of PAN C3. A single r cannot separate the reliable check from the noisy one, so A4 largely discounts all PAN rule failures (PAN C3 recall 12.6% at 5% FPR).

**Design, fixed before fitting.**
- Inputs: z_v = logit(p_v) from the frozen `tiles` ensemble (unchanged), plus one 0/1 indicator per check and document type:
  - Aadhaar: format, checksum;
  - PAN: format, category, semantic.

  An indicator is 1 when that check failed on that document type, taken from `experiments/rules/rule_decisions.csv` (`gt_failed_checks` / `ocr_failed_checks`).
- Model: s = sigmoid(w0 + w1·z_v + Σ w_k·indicator_k). L2 penalty with C = 1 and the intercept unpenalised, as in A4. Fitted on all 1,620 validation images (any forgery vs C0), separately for GT and OCR text.
- Thresholds, chosen on validation exactly as in A4: (a) maximum recall with validation C0 FPR ≤ 5%; (b) matched FPR at the validation FPR of `rules_OCR` and `OR_OCR`.
- No other variant is fitted or reported: no feature selection, no tuning of C, no second attempt.
- Applied to the test split once (`experiments/fusion/fuse_per_check.py`). Outputs go to `experiments/results/test_posthoc_A5/`.

**Pre-stated expectation.** Under OCR text at 5% FPR, A5 recall exceeds A4's 21.9%, with the gain concentrated in PAN C3. With GT text, A5 should match A4 (48.8%), because every rule failure is then reliable. If A5 does not beat A4, that is reported too.

**How it is reported.** In the paper, A5 appears only as a post-hoc diagnostic of where the OCR loss arises (RQ4, RQ5), next to the A4 numbers, never in place of them. Its test numbers are not used to answer RQ3 confirmatively.

## 20. Amendment A6 — fresh confirmatory test set (recorded 21 Oct 2026, before generation)

**Status.** Approved by Soham Phulwaria, Ananya Shukla and Dinesh Saini on 21 Oct 2026, as reported by Soham Phulwaria. Recorded before any fresh image, OCR output or score exists.

**Purpose.** A5 (Section 19) was designed after the v1 test split had been scored, so its v1 test result is post-hoc. A fresh set of synthetic people, never seen by anyone, gives a confirmatory test of A5 against A4, and an independent replication of the main results. No model, calibration, threshold or fusion parameter is refitted.

**Generation (fixed now).**
- Generator: `dataset/src/idforge`, unchanged, at the commit that adds this section.
- Config: `configs/dataset_v1.yaml` with two overrides only: `--seed 20261021 --n-persons 90`, giving 90 × 2 documents × 6 variants × 3 tiers = 3,240 images.
- Output folder: `dataset/data/fresh_20261021`. Command: `python -m idforge.build --config configs/dataset_v1.yaml --seed 20261021 --n-persons 90 --out data/fresh_20261021`. Nothing else from `build_all.sh` is run, because those steps would overwrite v1 statistics and the paper tables.
- Built on the GPU laptop with `.venv-dataset` and the same Tesseract installation as v1, so image encoding and OCR match the frozen corpus. The Tesseract version is logged.
- All 90 people form the fresh test set. The generator's `split` labels are ignored.
- 90 people rather than 45, to narrow the person-clustered intervals; the cost is small (no training).

**Leakage checks before scoring** (`experiments/fresh/check_fresh_identity.py`):
- no Aadhaar or PAN number shared with v1;
- no photo seed shared with v1;
- the share of full names that also occur in v1 is reported (names come from a shared pool, as within v1);
- generator pre-flight passes, and category, document and tier counts are as designed.

If a check fails, the set is not used, and the failure is reported.

**Scoring (frozen everything).**
- Visual: the five `tiles` checkpoints, scored as in training (`experiments/fresh/score_fresh_visual.py`, GPU). The script first re-scores v1 test images and must reproduce the committed logits, which proves the checkpoints are the frozen ones. The `base` comparison model is not scored (E-vis stays on v1).
- Calibration, t_v, A4 and A5: the committed files `experiments/e2_visual/frozen/tiles_calibration.json`, `experiments/fusion/frozen_fusion.json` and `experiments/fusion/frozen_fusion_A5.json`.
- Run once by `experiments/fresh/evaluate_fresh.py`. Outputs go to `experiments/results/fresh/`.

**Hypotheses and analysis (fixed now).**
- **H1 (primary, confirmatory).** Under OCR text, at their frozen 5%-FPR thresholds, A5 detection recall exceeds A4 detection recall. Test: person-clustered paired bootstrap (10,000 resamples, seed 0) of the recall difference A5 − A4. H1 is supported if the 95% interval is above 0. The paired FPR difference is reported beside it. If A5's FPR is more than 2 points above A4's, the gain is not claimed as a like-for-like improvement.
- **Secondary (replication, reported with Holm correction over the three):**
  - (a) A4 logistic with GT text vs visual only (RQ3);
  - (b) A4 logistic with OCR text vs visual only (RQ3, RQ4);
  - (c) A4 at the matched rules-OCR threshold vs rules-only with OCR text (RQ3).
- Everything is reported by document type, C0–C4 and C1 group, as on v1. Realised FPRs are reported; they are not forced to 5%.

**What changes in the paper.** If H1 is supported, A5's advantage is reported as confirmed on fresh data, and v1 A4 remains the primary pre-registered result. If H1 is not supported, that is reported, and A5 stays a post-hoc diagnostic.
