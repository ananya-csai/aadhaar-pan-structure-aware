# Reproducibility guide

This file is the long version of the paper's Appendix A (roadmap Step 19). It says what is needed to repeat each stage, how exactly each stage repeats, and where the evidence is. The protocol and every change to it are in `DECISIONS.md`; this file does not repeat the reasons.

Recorded 24 Oct 2026. Everything below comes from committed files (run configs, summaries, logs), except where a line says otherwise.

---

## 1. Four levels of reproduction

| Level | You start from | You run | What agrees | Evidence |
|---|---|---|---|---|
| **L1 Scoring** | committed per-image scores + frozen calibration and fusion files | `python experiments/score_frozen.py --split val` | exact (rounded summary, byte for byte) | CI job "Evaluation harness" on every commit |
| **L2 Inference** | released checkpoints + corpus | `python experiments/fresh/score_fresh_visual.py --corpus …` (its self-check) | logits equal to 6 decimals (max diff 5e-7) | `experiments/fresh/visual/summary.json`, `experiments/logs/fresh_visual_2026-10-21.txt` |
| **L3 Corpus** | generator + `configs/dataset_v1.yaml` | `python -m idforge.build --config configs/dataset_v1.yaml --out data/v1` | 10,791 / 10,800 images byte-identical (Linux rebuild); 9 differ in ≤ 37 pixels by ≤ 3 grey levels; labels, splits and GT verdicts identical | `experiments/logs/corpus_rebuild_linux_2026-10-24.txt`; check any rebuild with `dataset/scripts/compare_to_frozen.py` |
| **L4 Training** | corpus + training script + seed | `python experiments/e2_visual/train_tiles.py --seed k` | **not bit-exact** (Section 4) | Step 21 re-run (pending) |

---

## 2. Frozen artefacts and their SHA-256

### Data

| Item | SHA-256 | Notes |
|---|---|---|
| v1 corpus (10,800 JPEGs) | `7253245a10732303a0b22520a502a0e1f1390bf4a88b83e77ea920781abdedef` | 941,456,686 bytes; `dataset/scripts/corpus_checksum.py`; corrected 20 Oct (DECISIONS §18) |
| `dataset/data/v1/manifest.csv` | `009f4827129a65b82de87be6f2aea838a181f41c38cc34509ea0e31c03a4fc7e` | labels, splits, rule and OCR verdicts |
| `dataset/data/fresh_20261021/manifest.csv` | `89e2eb789d0ca7023c2d6b589bd2f2ce73fe61453a71ca829197cad490b5f3c6` | fresh set, seed 20261021 (DECISIONS §20) |
| `experiments/e2_visual/c1_regions.csv` | `b0138b52d37f7312b2b77e6f0735e5a429d62427c11f4175f0cfe60173597c91` | edit boxes for tile labels (training only) |
| 768×512 resize cache | `8229b7d987c19f5bba2e3b4724b3238fe7c2a5e388be103303128da9e7e90bcc` | whole-card model input |
| 384×256 resize cache | `a9c0ba03f33f960a0887ee53129104d79ed0d9ef02ec45563ed529411d59cf49` | built, not used for training (A3) |

### Frozen decision files

| File | SHA-256 |
|---|---|
| `experiments/e2_visual/frozen/tiles_calibration.json` | `8b4e1cf3c9faff0005f9c5539b23c4c6c273d5255aed2d30fcf00d56ad0f7732` |
| `experiments/fusion/frozen_fusion.json` (A4) | `a6f00c5385ebc4c9ec1e227ed993f451fc8f380e378e75075a3a221e9fe51808` |
| `experiments/fusion/frozen_fusion_A5.json` (A5, post-hoc) | `a60c40a5094414414733e581145357c11c28749aacd945d8a185797323dee0b7` |

### Tile-model checkpoints (`best.pt`, ~94 MB each, git-ignored)

| Seed | SHA-256 | MD5 (as shown by Zenodo) |
|---|---|---|
| 0 | `45af4819f39d1e250802f2d40b171b91083e257dbcdcaa557ebffd54ab552190` | `d22ff95731aa8574ea1a7cebc4189fef` |
| 1 | `6345fc360d84842465226724577bb92abb6f2b37d327a99a053b151829087eb6` | `ccf8b7699d62229e3ccd7ba3811c276d` |
| 2 | `1d3ef7d9b2cc34916ca853544c50f295c83b358aa741927bc752bb1c843aef52` | `6d4622b8b1a89043aa5ee2e2cd22e157` |
| 3 | `5c9b1159472374413f471e398c37db64f99d35223261a412f1e80844699b4080` | `e3160da8bcc17da9b022a675e7469ade` |
| 4 | `c0eb2d121c1a381a24359556c2eedaa38547d64720a35f7d743ba1e2e5546952` | `2766cb2c804225524da3805fc151ff02` |

**Archived (draft, 24 Oct 2026).** Zenodo record, version DOI `10.5281/zenodo.23618373` (concept DOI `10.5281/zenodo.23618372`), files `tiles_seed{0..4}_best.pt`. The DOI is reserved and resolves only once the record is published, which is planned for acceptance or camera-ready, because a published record shows the authors' names (double-blind review). Checked 24 Oct: the MD5 that Zenodo shows for each file equals the MD5 of the laptop file, and that file's SHA-256 equals the value above.

Per-image score files: each run's `summary.json` records the SHA-256 of its `scores_trainval.csv` and `scores_test.csv`; `score_frozen.py` refuses to score if any file differs.

### Tags

| Tag | Commit | Meaning |
|---|---|---|
| `v1.0-dataset`, `v1.0.1-dataset` | `d766fb2`, `dbb654e` | 29 Aug pre-freeze build (stamp later corrected, §18) |
| `protocol-e2-final` | `8392d83` | E2 protocol approved (Gate G1) |
| `frozen-before-test` | `1294c23` | visual models, calibration and A4 fusion frozen (Gate G2) |

---

## 3. Environments

**GPU laptop (training, inference, corpus build, OCR)**
- NVIDIA GeForce RTX 4060 Laptop GPU, 8 GB; Windows 11, build 26200 (build 26300 after an automatic update on 19 Oct: whole-card seeds 3–4 and the fresh-set scoring).
- Python 3.12.7; torch 2.14.1+cu130; torchvision 0.29.1+cu130; CUDA 13.0; cuDNN 9.24.0 (reported as `92400` in `experiments/e2_visual/logs/smoke_768x512.json`). Full list: `experiments/requirements-vision.txt`.
- NVIDIA driver version: **not recorded** — run `nvidia-smi` once and add it here (Section 7).
- Corpus build: Python 3.13, numpy 2.4.4, pillow 12.2.0, opencv-python 4.13.0.92, matplotlib 3.10.9 (`dataset/requirements.txt`).
- OCR: Tesseract 5.5.3, Leptonica 1.87.0, English model, installed 25 Jul 2026 (before v1 was built on 9 Oct). The protocol originally listed 5.3.4 / 1.82.0; see DECISIONS §20 run record.

**CPU laptop / CI (rules, fusion, statistics, paper):** Linux CI with Python 3.12 runs the L1 checks. No GPU needed.

---

## 4. Known sources of non-reproducibility

1. **Training is not bit-exact (L4).** Seeds fix head initialisation, data order and the negative tiles drawn each epoch; `cudnn.benchmark` is off. Deterministic kernels (`torch.use_deterministic_algorithms`) were not enforced, and training uses fp16 autocast. A second run of the same seed will differ slightly. The paper therefore treats the five seeds as the unit of variation. Acceptance rule for the Step 21 re-run: same config, same input hashes, and validation AUROC / PR-AUC inside the five-seed range (0.685–0.773 / 0.611–0.684). Matching score-file hashes is **not** expected and is not the test.
2. **Text layout differs by platform (L3).** Pillow applies complex-script layout (libraqm) only when FriBiDi is installed: usually on Linux, usually not on Windows. The frozen corpus was built on Windows, so with Pillow's BASIC layout. A Linux rebuild before the fix differed in almost every image (text shifted by a few pixels). Since 24 Oct the generator forces BASIC layout everywhere (`dataset/src/idforge/templates.py`); the v1 and fresh images do not change, because they were already built that way. After the fix a full Linux rebuild (Python 3.13.16, pinned requirements, `--skip-ocr`) gave 10,791 byte-identical images; the other 9 differ in at most 37 pixels by at most 3 grey levels, all at the right image border (consistent with floating-point differences in the perspective warp). Labels, identifiers, splits, records and ground-truth rule verdicts are identical. Consequence of BASIC layout: Devanagari is drawn without complex-script shaping. No Devanagari field is validated, but it is a fidelity limitation of the synthetic cards.
3. **OCR depends on the engine version.** Every OCR verdict in the manifest came from Tesseract 5.5.3. Another version will change some OCR readings and therefore the OCR-condition results; ground-truth-condition results do not depend on OCR.
4. **Code commits differ across runs.** Runs span commits `8392d83`, `744fabd`, `678ab45`, `41c6235`, `bb931f2`, `e421e5c`. Checked with `git diff`: `train_tiles.py` and `tiles.py` are identical for all tile runs; `train.py` changed only by adding the `--variant` switch (A2), and the `base` path is unchanged.

---

## 5. All training runs (validation, C0 vs C1)

| Model | Seed | Commit | Best / run epochs | Minutes | Val AUROC | Val PR-AUC | Temperature | ECE before → after |
|---|---|---|---|---|---|---|---|---|
| tiles | 0 | 678ab45 | 12 / 17 | 42.6 | 0.699 | 0.627 | 4.40 | 0.223 → 0.109 |
| tiles | 1 | 41c6235 | 6 / 11 | 30.9 | 0.685 | 0.611 | 1.52 | 0.077 → 0.055 |
| tiles | 2 | 41c6235 | 17 / 22 | 53.9 | 0.735 | 0.661 | 4.54 | 0.207 → 0.052 |
| tiles | 3 | 41c6235 | 15 / 20 | 49.3 | 0.717 | 0.661 | 4.16 | 0.193 → 0.089 |
| tiles | 4 | 41c6235 | 13 / 18 | 45.0 | 0.773 | 0.684 | 3.42 | 0.183 → 0.058 |
| tiles ensemble | — | — | — | — | **0.780** | **0.702** | — | 0.073 |
| base (768×512) | 0 | 8392d83 | 18 / 23 | 38.6 | 0.578 | 0.448 | 6.48 | 0.255 → 0.098 |
| base | 1 | 41c6235 | 20 / 25 | 41.6 | 0.613 | 0.500 | 5.40 | 0.237 → 0.082 |
| base | 2 | 41c6235 | 19 / 24 | 39.9 | 0.629 | 0.501 | 4.94 | 0.226 → 0.052 |
| base | 3 | bb931f2 | 18 / 23 | 39.9 | 0.622 | 0.507 | 5.17 | 0.234 → 0.078 |
| base | 4 | e421e5c | 18 / 23 | 37.9 | 0.611 | 0.518 | 5.90 | 0.241 → 0.112 |
| base ensemble | — | — | — | — | 0.638 | 0.531 | — | 0.082 |
| reg (pilot) | 0 | 744fabd | 5 / 10 | 18.5 | 0.564 | 0.435 | — | — |

Totals: 438 GPU-minutes of training (tiles 222, base 198, reg 18.5). Settings common to all runs: ResNet-50 `IMAGENET1K_V2`, one-logit head, plain BCE, AdamW lr 1e-4, 1 warm-up epoch then cosine to 0 over 30 epochs (per step), early stopping on document-level validation PR-AUC with patience 5, fp16. Tiles: batch 32, 15 tiles of 256 px (stride 192) on a 1024×640 canvas, 8 negatives per positive tile per epoch, positive if the tile holds ≥ 25% of the edit box, document score = max tile logit. Base: 768×512, batch 16 × 2 accumulation (92% VRAM rule). Reg: as base plus shift/photometric augmentation, dropout 0.5, weight decay 0.05.

Visual operating point: t_v = 0.5305 (validation C0 FPR 5.0%, C1 recall 34.8%).

---

## 6. Protocol record

In order. Full text in `DECISIONS.md`.

| Entry | DECISIONS | Date | Test split | Change | Effect |
|---|---|---|---|---|---|
| A1 | §12 | before training | sealed | whole-card input 384×256 → 768×512; C1 reported per edit group | defines the comparison model |
| Batch rule | §10 item 4 | 17 Oct | sealed | batch must fit in 92% of physical VRAM (Windows spills to RAM) | base batch 16 × 2 |
| A2 | §14 | 18 Oct | sealed | validation-only development; `reg` and `tiles` specified before running | all candidates reported |
| A3 | §15 | 18 Oct | sealed | `tiles` selected; 384×256 arm dropped; E-res → E-vis | tiles = visual branch |
| Run event | §15 | 19 Oct | sealed | OS update killed base seed 3; re-run; build 26300 for base 3–4 | none expected |
| A4 | §16 | 19–20 Oct | sealed | fusion frozen on validation; all three approved; tag `frozen-before-test` | primary fusion |
| Correction | §18 | 20 Oct | sealed | corpus digest stamp was from the 29 Aug build; corrected | none |
| Test scored | — | 21 Oct | scored once | all frozen systems | — |
| A5 | §19 | 21 Oct | **scored** | per-check fusion, post-hoc | post-hoc on test |
| A6 | §20 | 21 Oct | scored | fresh set pre-registered, then built; first build crashed on cp1252, re-run with UTF-8 | confirmatory A5 vs A4 |
| OCR record | §7, §20 | 21 Oct | scored | Tesseract 5.5.3, not 5.3.4 | none; one engine throughout |
| Generator fix | §21 | 24 Oct | scored | text layout forced to BASIC on all platforms (the engine that built v1); found by a Linux rebuild | none for v1/fresh; rebuilds elsewhere now match |

---

## 7. Still open

- ✅ [GPU] Five tile checkpoints uploaded to a Zenodo draft (Section 2). ⬜ Publish the record at acceptance / camera-ready; for double-blind submission, give reviewers an anonymous copy if they need the files.
- [GPU] Record the NVIDIA driver version (`nvidia-smi`, top line) in Section 3.
- [GPU] Step 21: one clean-environment re-run of a tile seed; acceptance rule in Section 4, item 1.
