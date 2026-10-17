# Research Roadmap — Structure-Aware Forgery Detection for Aadhaar and PAN

This is the single plan for finishing the paper. Follow the steps in order. A step is done only when its output, the command that produced it and its log are committed.

**Owners:** [GPU] GPU-laptop owner · [CPU] partner without a GPU · [BOTH] joint.
**Status:** ✅ done and committed · 🟡 started or needs checking · ⬜ not started.
**Status checked against:** commit `f76bdfb`, 18 Oct 2026.

## Ground rules

- Use only the frozen corpus. Do not regenerate it, overwrite its tags or rewrite pushed history.
- Membership, split and labels come from `dataset/data/v1/manifest.csv` only.
- **Train** is for fitting. **Validation** is for every choice: checkpoint, calibration, threshold and fusion. **Test** is scored once, after everything is frozen.
- Results apply to this synthetic benchmark only. Never claim real-world accuracy, identity verification or government authenticity.
- Report every planned seed and configuration, not the best one. Write any deviation into `DECISIONS.md` before looking at test results.

## Frozen artefacts

| Artefact | Value |
|---|---|
| Corpus | `dataset/data/v1`, 10,800 images, tags `v1.0-dataset` / `v1.0.1-dataset` |
| Corpus SHA-256 | `f3302cc7…0394` |
| Splits (people) | train 210 · val 45 · test 45 |
| C0 / C1 images | train 2,520 / 1,260 · val 540 / 270 · test 540 / 270 |
| Primary cache | 768 × 512, SHA-256 `8229b7d9…0bcc` |
| Sensitivity cache | 384 × 256, SHA-256 `a9c0ba03…cf49` |
| Visual model | ResNet-50, ImageNet-pretrained, one-logit head |
| GPU | NVIDIA GeForce RTX 4060 Laptop GPU, 8 GB |
| Protocol | `DECISIONS.md` and `experiments/EXPERIMENT_PLAN.md`; tag `protocol-e2-final` when Gate G1 passes |

## Gates

Do not cross a gate until everything before it is ✅.

- **G1 — before any full training run:** protocol approved, training settings recorded, corrected smoke test passed.
- **G2 — before scoring the test set:** all models, calibration, thresholds and fusion frozen and committed.
- **G3 — before writing claims:** results locked, every table regenerated from committed code.

---

## Phase 0 — Protocol and project state

### Step 1. Agree and freeze the protocol [BOTH] — 🟡 (✅ once the approval commit is tagged)
- ✅ Protocol drafted: input size, normalisation, splits, operating point, seed averaging (`DECISIONS.md` Sections 1–10).
- ✅ Input-resolution decision measured and recorded (Section 12). At 384 × 256, most of the evidence for the two fine-trace edits is lost: on clean images only 3–11% survives. At 768 × 512, 83–86% survives. So 768 × 512 is primary and 384 × 256 is the sensitivity arm.
- ✅ Training settings decided (Section 13) and implemented in `experiments/e2_visual/train.py`.
- 🟡 Mechanism-aware recall defined (Section 6); confirm it in Section 11.
- 🟡 Partner and mentor approved. Write names and dates into Section 11 (the `[[FILL]]` fields).
- 🟡 Re-create `protocol-e2-final` on the approval commit. The first tag pointed at a commit where approval still read "pending". `train.py` refuses to run until this is done.
- ⬜ Check ICDAR 2027 dates, page limit and anonymity rules on the official site. Planning targets: abstract 31 Jan 2027, full paper 20 Feb 2027.

**Done when:** Sections 6, 11 and 13 are filled in and `protocol-e2-final` is pushed.

### Step 2. Verify corpus and repository state [CPU + GPU] — 🟡
- ✅ Corpus hash and tags recorded. Person-level split separation passed (`verify_splits.py`). The loader re-checks it on every run.
- ⬜ [GPU] From the `dataset` folder, run `python scripts/corpus_checksum.py data/v1 --verify` (with `.venv-dataset`) and save the output to `experiments/logs/`.
- ⬜ [CPU] Save `git log --oneline --decorate` and `git tag -l` output to the same folder.

### Step 3. Reconcile the dataset report and paper numbers [CPU] — ⬜
- Regenerate `dataset/data/v1/stats/REPORT.md`, `dataset_stats.json`, figures and paper tables from the frozen manifest.
- Resolve the known mismatch: the paper says 4.1% Aadhaar and 18.9% PAN OCR false-positive rates and 5,824 distinct 64-bit hashes; the committed report says 3.8%, 19.7% and 5,848. Find the Tesseract run behind each number. Use the one that matches the frozen manifest, not the one that looks better.
- Check that the code for the paper's 256-bit hash analysis (Table IX) is committed (`dataset/scripts/add_phash256.py`). If it is not reproducible, correct the paper.
- Apply the open items in `docs/CORRECTIONS_NEEDED.md`.

**Done when:** every number in Section IV regenerates from a committed command.

---

## Phase 1 — Rule-only evaluation (CPU)

### Step 4. Build and test `evaluate.py` [CPU] — ⬜
One script computes every metric in the paper, so all systems are scored the same way.

- **Inputs:** a predictions file (`image_id`, `score` or `decision`) plus the manifest.
- **Required checks:** exactly one prediction per expected `image_id`; no duplicates or unknown IDs; the split is named in every report.
- **Metrics:** confusion matrix, precision, recall, F1, FPR, FNR. PR-AUC and AUROC where scores exist. State how undefined values (0/0) are handled.
- **Breakdowns:** document type × C0–C4. For C1, also per `c1_op` and per group: fine-trace (`local_recompression`, `resample_patch`) and coarse (`font_substitution`, `field_displacement`, `patch_splice`).
- **Two recall definitions, always labelled:**
  - *Detection recall*: positives are all forged images (C1–C4, `label = 1`). This is the metric for RQ2, RQ3 and RQ5, because it compares directly with the visual branch.
  - *Rule-coverage recall*: positives are only images the rules are designed to catch (`expected_rule = FAIL`). This is a sanity check of the rule implementation.
- **Tests:** perfect, random and all-flagged predictors; missing IDs; duplicate IDs; invalid labels.

### Step 5. Reproduce E3 and commit the canonical rule report [CPU] — 🟡
- 🟡 `experiments/e3_rule_branch/` exists, but it reports only rule-coverage recall (GT 100%, OCR 99.0%). That is not comparable with the visual branch.
- On the frozen manifest, test split, detection recall is: GT recall 0.375, precision 1.000, FPR 0; OCR recall 0.431, precision 0.888, FPR 0.109. The earlier plan expected OCR values of 0.433 / 0.883 / 0.115. Explain the small gap in Step 3 (OCR run); do not force the numbers.
- Re-run E3 through `evaluate.py` with both recall definitions, by document type and C0–C4. Save the command, confusion matrices and commit hash in `experiments/e3_rule_branch/`.
- State in the paper that perfect GT-rule results are expected by construction, because the rules and labels come from the same generator. This is a sanity check, not evidence of real-world accuracy.

---

## Phase 2 — Leakage and construction checks

### Step 6. Split, duplicate and edit-visibility audits [CPU] — ✅
- ✅ No person in two splits. No missing images. No exact duplicates across splits (`744f166`).
- ✅ pHash near-duplicate audit run. It is inconclusive because layouts are shared; this limitation is stated in `NEAR_DUPLICATE_AUDIT.md`.
- ✅ Edit visibility at each input size measured (`experiments/edit_survival/`).

### Step 7. Learned leakage probe [GPU + BOTH] — 🟡
- `dataset/src/idforge/probe.py` exists. Check whether it has a leakage-specific positive control: inject a known cue into a controlled copy, show the probe detects it, and include negative controls.
- If it has no such control, either add one or drop the probe from the paper and rely on the Step 6 audits. Separating C0 from C1 is not evidence about leakage.

---

## Phase 3 — Visual baseline (GPU)

### Step 8. GPU environment and pre-training checks [GPU] — ✅
- ✅ Environment recorded: Python 3.12.7, torch 2.14.1+cu130, CUDA 13.0, RTX 4060 Laptop 8 GB (`experiments/requirements-vision.txt`).
- ✅ Loader checks, one real batch, and tiny-overfit (50 images, 100% accuracy) passed (`experiments/e2_visual/logs/smoke_768x512.json`).
- ✅ Batch size measured inside physical VRAM, with NVIDIA system-memory fallback turned off. 768 × 512: batch 16 × 2 accumulation, 6.6 GB peak, about 1.5 minutes per epoch of compute. 384 × 256: batch 32, 3.5 GB, about 22 seconds per epoch. Both tiny-overfit tests reached 100%.

### Step 9. Resize caches and loader [GPU; CPU reviews] — ✅
- ✅ Both caches built from the manifest, fingerprinted, and inspected beside the originals (contact sheets committed).
- ✅ Loader (`experiments/e2_visual/data.py`): manifest-only membership, RGB, ImageNet normalisation, one item per `image_id`, sorted, size checked.
- [CPU] Review `data.py` and both contact sheets, and note any problem in an issue.

### Step 10. Train E2 [GPU] — ⬜ (after Gate G1)
- Task: C0 vs C1 on the train split, with settings from `DECISIONS.md` Section 13.
- **Primary:** 768 × 512, seeds 0–4. **Sensitivity:** 384 × 256, the same seeds and settings.
- Early stopping on validation PR-AUC. Never compute test metrics during development.
- Save for every run: config, checkpoint, per-epoch train loss and validation PR-AUC/AUROC, runtime, environment, git commit.
- With each final checkpoint, save raw logits for **all 10,800 images** (C0–C4, all splits) in one file per run. Fusion needs visual scores for every category. Test logits are written but not opened until Step 15.

### Step 11. Validate outputs and freeze [GPU + CPU] — ⬜
- [CPU] Run `evaluate.py` on validation logits only. Check the prediction schema, IDs and split membership.
- [GPU] For each seed, choose the checkpoint from validation. Save validation scores and config hashes.
- [BOTH] Commit the final configuration. Do not compare the two resolutions until both are frozen.

---

## Phase 4 — Calibration, fusion and the single test run

### Step 12. Rule outputs and recovery analysis [CPU] — ⬜
- Export rule decisions for all 10,800 images, GT-text and OCR-text versions, in the `evaluate.py` schema.
- Join with the visual scores by `image_id`. Count both-detect, visual-only, rule-only and neither, by document type, C1–C4 and C1 group (validation now; test after Step 15).
- Compute mechanism-aware recall with the Section 6 definition.

### Step 13. Calibrate each visual model [GPU] — ⬜
- Fit temperature scaling per seed on validation logits. Save the temperatures and reliability diagrams.
- Average the calibrated probabilities over the five seeds (Section 5).

### Step 14. Choose and freeze fusion [GPU + CPU] — ⬜
- Candidates, in this order of simplicity: OR, AND, weighted score, and logistic fusion fitted on validation.
- Operating point: maximise C1 recall subject to validation C0 FPR ≤ 5%. Report the realised test FPR; it is not guaranteed to be 5%.
- Compare each fusion rule with the best single branch at the same validation-chosen operating point.
- Test the fusion code on hand-made examples with known answers. Commit the parameters.

**Gate G2:** models, temperatures, thresholds and fusion parameters committed.

### Step 15. Score the test set once [GPU + CPU] — ⬜
- [GPU] Use the saved test logits from the frozen checkpoints.
- [CPU] Apply the frozen calibration, thresholds and fusion. No retuning.
- [BOTH] Save predictions, thresholds, config hashes and run logs for both resolutions.

---

## Phase 5 — Analyses and statistics (CPU; GPU supplies scores)

### Step 16. Planned analyses — ⬜
| ID | Question | Research question |
|---|---|---|
| E6 | GT-text vs OCR-text verdicts on the same images: stable, OCR-induced failure, OCR-masked failure; by tier and document type | RQ4 |
| E7 | Incremental fusion gain, Aadhaar vs PAN, with person-level uncertainty | RQ5 |
| E8 | C0 false positives by quality tier, document type and OCR outcome (post-hoc splits labelled exploratory) | RQ3, RQ4 |
| E9/E12 | For flagged C2/C3, does the explanation name the corrupted field? Over-attribution reported separately; GT vs OCR | RQ2 |
| E-res | C1 recall at 768 × 512 vs 384 × 256 for fine-trace and coarse groups | RQ1 |

- Expected E-res result: little change for coarse edits and a clear drop for fine-trace edits at 384 × 256. If there is no drop, report that the model does not use fine traces even at 768 × 512.
- Optional, only if pre-registered first: a position-aware OCR whitelist ablation, and a second OCR engine on the test split.

### Step 17. Statistics and locking results [CPU] — ⬜
- Primary inference: person-clustered bootstrap (10,000 resamples) on paired metric differences. Resample people and keep each person's documents together. The test set has 45 people, not 1,620 independent samples.
- Paired tests: cluster-aware permutation or bootstrap. Image-level McNemar is supplementary only, with its independence limitation stated.
- Holm correction within each pre-defined family of comparisons, including E-res.
- About 54 test C1 images per edit type means wide intervals. Lead with the two C1 groups; per-operation results are supporting detail.
- Audit row counts, IDs, labels, thresholds and code traceability. Then lock the results.

**Gate G3:** results locked.

---

## Phase 6 — Paper and submission

### Step 18. Write Sections VI–IX [CPU lead; BOTH] — ⬜
- Every number comes from a committed script and maps to a table or figure. Each research question maps to at least one table with uncertainty.
- Section VI states the input size, the resize policy, the edit-survival measurement and why 768 × 512 was chosen.
- Answer RQ1 separately for coarse and fine-trace C1 edits. Fine-trace edits are not "visually apparent", so one pooled number would misrepresent RQ1. If the RQ1 wording is changed, record it in `DECISIONS.md`.
- Finish the literature audit: databases searched, search date, screening counts, and every citation verified against its source.

### Step 19. Reproducibility section [GPU] — ⬜
- Report from the logs: architecture, weights, preprocessing, optimizer, learning rate, batch size and accumulation, seeds, early stopping, calibration, hardware, software versions, runtime, commit hash and both cache hashes.
- List every deviation from the protocol.

### Step 20. Claims and limitations [BOTH] — ⬜
- Central claim, only if the results support it: a controlled evaluation of the incremental detection value and false-positive cost of structural/semantic evidence over a visual baseline on synthetic Aadhaar/PAN-format documents, including OCR degradation.
- Limitations to state:
  - the data is synthetic and design-unfaithful;
  - one English OCR engine;
  - the test set has 45 people;
  - the visual branch is a whole-document ResNet-50 at 768 × 512, and a crop-based or higher-resolution detector might catch more fine-trace edits.
- C0 = unmodified synthetic controls, not genuine documents. C4 = rule-valid fabricated identifiers; passing the rules is not identity verification.
- Aadhaar C3 is a known capability boundary (no rule reads the Devanagari line). PAN: Individual-format scope only, and the tenth character is not claimed to be a recomputable check digit.
- No "first" claims. No real-world accuracy, verification or fraud-prevalence claims.

### Step 21. Format, reproduce, submit [BOTH + mentor] — ⬜
- Convert to Springer LNCS and meet the official page limit and anonymity rules.
- [GPU] Reproduce one key visual run from a clean environment and match the hashes and configs.
- [CPU] Regenerate every table from committed artefacts.
- [BOTH] Do a reviewer-style read-through with the mentor and freeze author order. Release code and configs; release a corpus archive only if permitted. Do not submit to two venues at once.

---

## Timeline

| Dates (2026–27) | Milestone | Lead |
|---|---|---|
| 18–24 Oct | Gate G1: settings decided, approval recorded, `protocol-e2-final` tagged, smoke tests re-run (both sizes) | BOTH / GPU |
| 18 Oct – 7 Nov | Steps 2–5 and 7: report reconciliation, `evaluate.py`, canonical E3, probe decision | CPU |
| 25 Oct – 14 Nov | Step 10: E2 training, 5 seeds × 2 sizes, logits for all images | GPU |
| 15–21 Nov | Steps 11–14: freeze, calibration, fusion on validation (Gate G2) | BOTH |
| 22–28 Nov | Steps 12 and 15: test scored once, recovery analysis | BOTH |
| 29 Nov – 26 Dec | Steps 16–17: analyses, statistics, results locked (Gate G3) | CPU; GPU supplies scores |
| 27 Dec – 24 Jan | Steps 18–20: Sections VI–IX, literature audit, LNCS formatting | BOTH |
| By 31 Jan | Abstract submitted (verify date) | BOTH |
| 1–20 Feb | Step 21: clean reproduction, mentor review, full paper submitted (verify date) | BOTH + mentor |

Leave room for end-semester exams. If a window slips, move the later windows and keep the order and gates.

## Final submission checklist

- [ ] Protocol approved and tagged `protocol-e2-final` before any E2 training run.
- [ ] Corpus, both caches and splits verified from pinned hashes.
- [ ] Every planned seed and both resolutions reported.
- [ ] Calibration, thresholds and fusion chosen on validation only; realised test FPR and recall reported.
- [ ] Detection recall and rule-coverage recall reported separately and named correctly.
- [ ] Results broken down by document type, C0–C4 and C1 group (fine-trace vs coarse).
- [ ] E6, E7, E8, E9/E12 and E-res completed, or omissions disclosed.
- [ ] Person-clustered uncertainty, paired inference and multiplicity correction applied.
- [ ] Every table and figure regenerates from committed artefacts; no TODOs remain.
- [ ] Limitations, PAN scope, C4 and OCR boundaries stated accurately.
- [ ] LNCS format, page limit, anonymity, citations and authorship checked against official rules.
