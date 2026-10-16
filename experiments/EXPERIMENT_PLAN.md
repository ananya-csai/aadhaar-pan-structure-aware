# Experiment Plan

## Approved resolution protocol

- Primary input canvas: 384 × 256 pixels (width × height).
- Sensitivity input canvas: 224 × 160 pixels (width × height).
- Resize policy: preserve aspect ratio and pad to the target canvas.
- Padding color: white before normalization.
- Image channels: RGB.
- Normalization: ImageNet mean and standard deviation.
- Primary visual task: C0 versus C1, using the manifest's `forgery_category` column.
- Dataset: frozen `dataset/data/v1` corpus; do not regenerate or modify it.
- Split source: manifest `split` column.
- Training: training split only.
- Checkpoint selection, calibration and threshold selection: validation split only.
- Test evaluation: only after the model, preprocessing, checkpoint, calibration and threshold are frozen.
- Resolution sensitivity: repeat the agreed experiment at 224 × 160, holding other settings constant wherever possible.
- Initial target: five random seeds, with probability averaging across seeds.
- Operating point: maximize C1 recall subject to validation C0 FPR ≤ 5%.
- Document any deviations before test evaluation.

## Protocol approval

Detailed decisions are recorded in `DECISIONS.md`.

Initial defaults have been approved by the lead researcher. Collaborator/mentor agreement is pending. Full training must not begin until the required protocol agreement and pre-training checks are complete.
