# Fresh confirmatory test set (Amendment A6, `DECISIONS.md` Section 20)

A new set of 90 synthetic people (seed 20261021, 3,240 images), generated after all parameters were frozen. It is scored once with the frozen visual models, calibration, A4 and A5. Nothing is refitted.

| Step | Where | Command |
|---|---|---|
| 1. Build | GPU laptop, `dataset/`, `.venv-dataset` | `python -m idforge.build --config configs/dataset_v1.yaml --seed 20261021 --n-persons 90 --out data/fresh_20261021` (with `PYTHONPATH=src`) |
| 2. Leakage and design check | GPU laptop | `python experiments/fresh/check_fresh_identity.py dataset/data/fresh_20261021` |
| 3. Visual scores | GPU laptop, `.venv-vision` | `python experiments/fresh/score_fresh_visual.py --corpus dataset/data/fresh_20261021` |
| 4. Commit | GPU laptop | manifest, records, splits, config and visual scores (images stay git-ignored) |
| 5. Evaluate once | any CPU | `python experiments/fresh/evaluate_fresh.py --corpus dataset/data/fresh_20261021` |

Do not run `scripts/build_all.sh` for this set: its later steps overwrite the v1 statistics and the paper tables. `score_fresh_visual.py` first checks that each checkpoint reproduces its committed v1 test logits. `evaluate_fresh.py` refuses to run twice, or without Section 20 already committed.
