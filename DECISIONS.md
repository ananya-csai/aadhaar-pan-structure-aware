# Experiment Protocol Decisions

**Status:** Draft — initial defaults approved by lead researcher; collaborator/mentor agreement pending.

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

- Primary input canvas: 384 × 256 pixels (width × height).
- Sensitivity canvas: 224 × 160 pixels (width × height).
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

Proposed definition: count a detection as mechanism-aware only when the rule flag matches the known corrupted mechanism or field.

**Pending agreement:** Confirm the precise definition, eligible cases and denominator with the research collaborator/mentor before reporting this metric.

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
4. Run a GPU forward/backward smoke test.
5. Run a tiny-overfit test on a small, fixed training subset containing C0 and C1 examples.
6. Save configurations and logs needed to reproduce the experiment.

Do not use test-set results to choose preprocessing, checkpoints, calibration, thresholds or other model settings.

## 11. Approval record

- Lead researcher initial approval: approved.
- Collaborator/mentor approval: pending.
- Approval date and names: to be recorded after agreement.
- Protocol amendment commit: to be recorded after the approved files are committed.
