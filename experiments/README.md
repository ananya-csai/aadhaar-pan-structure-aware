# Experiments

Every experiment reported in the paper, with its frozen parameters, results
and run logs. The protocol and every amendment to it are in
[`../DECISIONS.md`](../DECISIONS.md); the commands that reproduce each stage
and the SHA-256 of every frozen file are in
[`../docs/REPRODUCIBILITY.md`](../docs/REPRODUCIBILITY.md).

Two rules hold throughout:

* **Calibrate on validation, evaluate on test once.** No threshold, weight or
  model choice was fitted on test data; the test split was scored once, after
  the freeze tag `frozen-before-test`.
* **Report per document type and per forgery category, never pooled alone.**

## Map

| Folder / file | What it holds | Paper |
|---|---|---|
| `evaluate.py`, `test_evaluate.py` | shared evaluation harness used to score every system, and its tests | Metrics and statistical analysis |
| `score_frozen.py` | applies every frozen parameter to one split and scores all systems; on the test split it refuses to run unless the tag `frozen-before-test` exists and the frozen files match their tagged versions | Evaluation protocol, Results |
| `e2_visual/` | visual branch: tile and whole-card ResNet-50 training, calibration (`frozen/`), run records (`runs/`) | Visual branch, visual branch development |
| `e3_rule_branch/` | rule-only branch on the test split | RQ2, RQ4, RQ6 |
| `rules/` | per-image rule decisions with the failing check, mechanism-aware recall, and the recovery analysis (which images each branch catches) | RQ2–RQ4, rule-level explanations |
| `fusion/` | A4 and A5 fusion fitting, frozen fusion files, tests | Evidence fusion, frozen fusion parameters |
| `fresh/` | fresh confirmation set (90 new people): identity check, visual scoring, one-time evaluation | Per-check fusion and fresh confirmation |
| `analysis/` | planned analyses and statistics behind the RQ tables (paired bootstrap, Holm correction) | Results |
| `results/` | summaries per split: `val/`, `test/`, `test_posthoc_A5/`, `val_A5/`, `fresh/`, `analysis/` | all result tables |
| `edit_survival/`, `measure_edit_survival.py` | how much of each C1 pixel edit survives degradation and resizing | Visual branch development |
| `build_resize_cache.py`, `fingerprint_resize_cache.py`, `cache_fingerprints/`, `inspect_resize_cache.py` | resized-input cache for the whole-card model and its fingerprints | Visual branch development |
| `verify_splits.py`, `verify_near_duplicates.py`, `check_zero_hash_pairs.py`, `inspect_near_duplicates.py`, `NEAR_DUPLICATE_AUDIT.md` | split and near-duplicate leakage audits | Splits and leakage control |
| `logs/` | run logs of the one-time test and fresh-set scoring, corpus checks and rebuilds | Appendix S1 |
| `EXPERIMENT_PLAN.md` | the plan written before the experiments | — |
| `requirements-vision.txt` | Python environment of the GPU runs | Implementation details |

Trained checkpoints (`*.pt`, ~95 MB each) are not stored in Git; they will be
released in a DOI-registered archive (see `CITATION.cff` and the paper's data
availability statement).
