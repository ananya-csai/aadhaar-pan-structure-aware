# Research Roadmap — Structure-Aware Forgery Detection for Aadhaar and PAN

This is the single plan for finishing the paper. Follow the steps in order. A task is done only when its output, the command that produced it and its log are committed.

**Owners:** [GPU] Soham (GPU laptop; holds the image corpus and checkpoints) · [CPU] Ananya (no GPU; works from the repository) · [BOTH] joint · [Mentor] Dinesh Saini.
**Status:** ✅ done and committed · ⬜ not done. A step is ✅ only when every task in it is ✅.
**Status checked against:** 19 Oct 2026, `main` after PR #3 (plus this update).

## What runs where

- The 10,800 images, the resize caches and the model checkpoints exist only on the GPU laptop; they are not in the repository.
- Everything the remaining analyses need is in the repository: the manifest, rule verdicts, per-seed logits for all 10,800 images (`scores_trainval.csv`, sealed `scores_test.csv`), calibration and fusion parameters. All of Steps 15–18 therefore run on any CPU machine.
- Tasks that need the images or a GPU: Step 2 corpus check, Step 21 clean re-training run.
- Work on a branch and merge into `main` through a pull request on GitHub, so `main` commits are signed ("Verified"). Pull before starting; never force-push `main`.

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
| Visual branch | `tiles`: ResNet-50 (ImageNet), 15 native tiles of 256 × 256, 5 seeds, temperature-scaled ensemble (`experiments/e2_visual/frozen/`) |
| Comparison model | `base`: ResNet-50 at 768 × 512, 5 seeds (E-vis only) |
| Edit regions | `c1_regions.csv`, SHA-256 `b0138b52…7c91` |
| Caches | 768 × 512 `8229b7d9…0bcc` · 384 × 256 `a9c0ba03…cf49` |
| Fusion | Amendment A4, `experiments/fusion/frozen_fusion.json` (validation only) |
| Protocol | `DECISIONS.md`, `experiments/EXPERIMENT_PLAN.md`; tag `protocol-e2-final` (`8392d83`) |

## Gates

- **G1 — before any full training run** — ✅ passed 17 Oct 2026 (`protocol-e2-final`).
- **G2 — before scoring the test set** — ⬜ parameters frozen and committed ✅; A4 sign-off in `DECISIONS.md` §16 ⬜; tag `frozen-before-test` ⬜.
- **G3 — before writing claims** — ⬜ results locked, every table regenerated from committed code.

## Who is waiting for whom

- **Nobody is waiting for the GPU partner.** His remaining tasks (Steps 2, 19, 21) run in parallel.
- **The test scoring (Step 15) waits only for the A4 sign-off** from all three people. After that, Steps 15–18 are CPU work.

---

## Phase 0 — Protocol and project state

### Step 1. Agree and freeze the protocol [BOTH] — ⬜
- ✅ [BOTH] Protocol drafted: input size, normalisation, splits, operating point, seed averaging (`DECISIONS.md` §1–10).
- ✅ [BOTH] Input-resolution decision measured and recorded (§12): at 384 × 256 only 3–11% of fine-trace edit signal survives on clean images; 83–86% at 768 × 512.
- ✅ [BOTH] Training settings decided (§13) and implemented in `experiments/e2_visual/train.py`.
- ✅ [BOTH] Mechanism-aware recall defined (§6) and confirmed (§11).
- ✅ [Mentor] Approval recorded (§11); `protocol-e2-final` tagged on `8392d83`.
- ✅ [CPU] Venue checked (19 Oct): ICDAR 2027, 18–22 Aug 2027, Kuala Lumpur (icdar2027.org). Deadlines listed by a third-party tracker: abstract 31 Jan 2027, full paper 20 Feb 2027. ICDAR 2026 rules, the best guide until 2027's are posted: LNCS, at most 17 pages including references, double-blind.
- ⬜ [CPU] Confirm the 2027 deadlines, page limit and anonymity rules on the official "Important dates" and submission pages once posted.

### Step 2. Verify corpus and repository state [GPU + CPU] — ⬜
- ✅ [CPU] Corpus hash and tags recorded; person-level split separation passed (`verify_splits.py`).
- ✅ [CPU] `git log --oneline --decorate` and tag list saved: `experiments/logs/repo_state_2026-10-19.txt`.
- ⬜ [GPU] From `dataset/`, run `python scripts/corpus_checksum.py data/v1 --verify` (with `.venv-dataset`) and commit the output as `experiments/logs/corpus_verify_<date>.txt`. Needs the images, so only the GPU laptop can do it.

### Step 3. Reconcile the dataset report and paper numbers [CPU] — ✅
- ✅ Section IV regenerated from the frozen statistics (PR #1): Aadhaar OCR FPR 3.8%, PAN 19.7%, 5,848 distinct 64-bit hashes; 64-bit hash audit only.
- ✅ Open items in `docs/CORRECTIONS_NEEDED.md` applied.

---

## Phase 1 — Rule-only evaluation

### Step 4. Build and test `evaluate.py` [CPU] — ✅
- ✅ `experiments/evaluate.py`: one prediction per `image_id`, no duplicates or unknown IDs, split named in every report; confusion matrix, precision, recall, F1, FPR, FNR, AUROC, PR-AUC; document type × C0–C4; C1 by operation and by fine-trace / coarse group; person-clustered bootstrap.
- ✅ Detection recall (all forged images) and rule-coverage recall (`expected_rule = FAIL`) always reported separately.
- ✅ Tests (`experiments/test_evaluate.py`) run in CI.

### Step 5. Canonical E3 rule report [CPU] — ✅
- ✅ `experiments/e3_rule_branch/results/`, test split: GT detection recall 37.5%, FPR 0%; OCR detection recall 43.1% [41.3, 45.1], FPR 10.9% [7.4, 14.8] (Aadhaar 3.7%, PAN 18.1%). Regenerated exactly in CI.

---

## Phase 2 — Leakage and construction checks

### Step 6. Split, duplicate and edit-visibility audits [CPU] — ✅
- ✅ No person in two splits, no missing images, no exact duplicates across splits (`744f166`).
- ✅ pHash near-duplicate audit run; inconclusive because layouts are shared (`NEAR_DUPLICATE_AUDIT.md`).
- ✅ Edit survival at each input size measured (`experiments/edit_survival/`).

### Step 7. Learned leakage probe [BOTH] — ✅
- ✅ Probe has no leakage-specific positive control; reported as uninformative. The paper relies on the exact audits and uses the visual branch as a bounding check (`DECISIONS.md` §17).

---

## Phase 3 — Visual baseline

### Step 8. GPU environment and pre-training checks [GPU] — ✅
- ✅ Environment recorded: Python 3.12.7, torch 2.14.1+cu130, CUDA 13.0, RTX 4060 Laptop 8 GB (`experiments/requirements-vision.txt`).
- ✅ Loader checks, one real batch, tiny-overfit test passed; batch size measured inside physical VRAM with system-memory fallback off.

### Step 9. Resize caches and loader [GPU; CPU reviews] — ✅
- ✅ [GPU] Both caches built from the manifest, fingerprinted, contact sheets committed.
- ✅ [GPU] Loader `experiments/e2_visual/data.py`: manifest-only membership, RGB, ImageNet normalisation, one item per `image_id`, size checked.
- ✅ [CPU] Reviewed `data.py` and the 768 × 512 contact sheet (19 Oct): manifests cross-checked row by row, labels checked against category, aspect ratio kept with padding; no problems found.

### Step 10. Train E2 [GPU] — ✅
- ✅ `base` pilot, 768 × 512, seed 0: validation AUROC 0.578, PR-AUC 0.448; memorised the training set.
- ✅ `reg` (A2), seed 0: validation AUROC 0.564, PR-AUC 0.435; no better.
- ✅ `tiles` (A2), seed 0: validation AUROC 0.699, PR-AUC 0.627; selected (A3, §15).
- ✅ `tiles` seeds 0–4 and `base` seeds 0–4 trained; logits for all 10,800 images saved and committed; test logits sealed by SHA-256.

### Step 11. Validate outputs and freeze [GPU + CPU] — ✅
- ✅ [GPU] Checkpoints chosen on validation PR-AUC; configs and hashes saved.
- ✅ [CPU] Validation scores cross-checked through `evaluate.py` (`score_frozen.py --split val`, in CI).

---

## Phase 4 — Calibration, fusion and the single test run

### Step 12. Rule outputs and recovery analysis [CPU] — ⬜
- ✅ Rule decisions for all 10,800 images, GT and OCR text, with the failing check (`experiments/rules/rule_decisions.csv`).
- ✅ Mechanism-aware recall (`experiments/rules/mechanism_aware_recall.md`).
- ✅ Recovery table on validation (both / visual only / rules only / neither, by document type, C0–C4, C1 group): `experiments/rules/recovery.py`, output `experiments/results/val/recovery.md`.
- ⬜ Recovery table on test: `python experiments/rules/recovery.py --split test` after Step 15.

### Step 13. Calibrate each visual model [GPU] — ✅
- ✅ Per-seed temperature scaling on validation, reliability data, 5-seed ensemble (`experiments/e2_visual/frozen/`; `tiles` ensemble validation AUROC 0.780, PR-AUC 0.702).

### Step 14. Choose and freeze fusion [GPU + CPU] — ⬜
- ✅ [CPU] OR, AND and logistic fusion fitted on validation only, GT and OCR text; thresholds at 5% FPR and at matched FPR (Amendment A4, `DECISIONS.md` §16; `experiments/fusion/`).
- ✅ [CPU] Fusion code tested on hand-made examples with known answers and against the validation outputs (`experiments/fusion/test_fusion.py`, in CI).
- ⬜ [BOTH + Mentor] Sign-off in `DECISIONS.md` §16 (three names and dates).
- ⬜ [CPU] After the sign-off: create and push the tag `frozen-before-test` on that commit. **This is Gate G2.**

### Step 15. Score the test set once [CPU] — ⬜
- ✅ [GPU] Sealed `scores_test.csv` for all 10 runs committed; `score_frozen.py` refuses to run if any hash changed.
- ⬜ [CPU] `python experiments/score_frozen.py --split test` — once, after the tag. Commit `experiments/results/test/` immediately, without re-running.

---

## Phase 5 — Analyses and statistics (CPU)

Scripts for each analysis can be written and checked on validation now; they are run on test after Step 15.

### Step 16. Planned analyses [CPU] — ⬜
| ID | Question | RQ | Status |
|---|---|---|---|
| E6 | GT vs OCR verdicts on the same images: stable, OCR-induced failure, OCR-masked failure; by tier and document type | RQ4 | ⬜ |
| E7 | Incremental fusion gain, Aadhaar vs PAN, with person-level uncertainty | RQ5 | ⬜ |
| E8 | C0 false positives by quality tier, document type and OCR outcome (post-hoc splits labelled exploratory) | RQ3, RQ4, RQ6 | ⬜ |
| E9/E12 | For flagged C2/C3, does the explanation name the corrupted field? Over-attribution separately; GT vs OCR | RQ2 | ⬜ |
| E-vis | `tiles` vs `base` on C1, by C1 group, edit type and quality tier, 5 seeds each, with edit survival | RQ1 | ⬜ |

- Optional, only if recorded in `DECISIONS.md` first: a position-aware OCR whitelist ablation; a second OCR engine.

### Step 17. Statistics and locking results [CPU] — ⬜
- ⬜ Person-clustered bootstrap (10,000) on paired metric differences; Holm correction within each pre-defined family, including E-vis.
- ⬜ Lead with the two C1 groups; per-operation results (about 54 test images each) are supporting detail.
- ⬜ Audit row counts, IDs, labels, thresholds and code traceability; lock results. **This is Gate G3.**

---

## Phase 6 — Paper and submission

### Step 18. Write the paper [CPU lead; BOTH] — ⬜
- ✅ [CPU] Sections I–IV written; Section IV numbers generated from committed statistics (Section II-E details are the next task).
- ✅ [CPU] Sections V (Methodology) and VI (Experimental Setup) drafted, all numbers checked (PR #2).
- ⬜ [CPU] Fill Section II-E literature-search details: search date, year range, n₁, n₂, venues without peer review.
- ⬜ [CPU] Fill the reference access date and confirm the page reference in the bibliography.
- ⬜ [CPU] Section VII Results — after Step 17. RQ1 answered separately for coarse and fine-trace edits.
- ⬜ [CPU] Section VIII Discussion — the limitations part can be written now; the interpretation waits for results.
- ⬜ [CPU] Section IX Conclusion, and final numbers in the abstract — last.

### Step 19. Reproducibility section [GPU] — ⬜
- ⬜ [GPU] From the logs: architecture, weights, preprocessing, optimizer, learning rate, batch size, seeds, early stopping, calibration, hardware, software versions, runtime, commit hash and cache hashes; list every deviation from the protocol (A1–A4).

### Step 20. Claims and limitations [BOTH] — ⬜
- ⬜ Central claim, only if the results support it: a controlled evaluation of the incremental detection value and false-positive cost of structural/semantic evidence over a visual baseline on synthetic Aadhaar/PAN-format documents, including OCR degradation.
- ⬜ State the limitations:
  - the data is synthetic;
  - one English OCR engine;
  - the test set has 45 people;
  - the visual branch is near chance on severely degraded images;
  - C0 are synthetic controls, not genuine documents;
  - C4 passing the rules is not identity verification;
  - Aadhaar C3 is a capability boundary;
  - PAN covers the Individual format only, and the tenth character is not claimed to be a check digit.
- ⬜ No "first" claims; no real-world accuracy, verification or fraud-prevalence claims.

### Step 21. Format, reproduce, submit [BOTH + mentor] — ⬜
- ⬜ [CPU] Convert to Springer LNCS and cut to the page limit. The draft already has about 12,600 words before Results; 17 LNCS pages hold roughly 6,500–7,500. Sections III and IV need the largest cuts; move detail to an appendix or the repository.
- ⬜ [CPU] Anonymise: remove author names, affiliation and acknowledgements. The repository URL contains an author's name, so link to an anonymised copy at submission.
- ⬜ [GPU] Reproduce one `tiles` training run from a clean environment and match hashes and configs.
- ⬜ [CPU] Regenerate every table from committed artefacts.
- ⬜ [BOTH + Mentor] Reviewer-style read-through; freeze author order; release code and configs. Do not submit to two venues at once.

---

## Timeline

| Dates (2026–27) | Milestone | Lead |
|---|---|---|
| ✅ by 19 Oct | Gate G1, all training, calibration, fusion frozen on validation, Sections V–VI drafted | BOTH |
| 20–26 Oct | A4 sign-off; tag `frozen-before-test`; test scored once (Step 15); Step 2 corpus check | BOTH / CPU / GPU |
| 20 Oct – 15 Nov | Write analysis scripts on validation; run them on test (Steps 12, 16) | CPU |
| 16–30 Nov | Statistics and Gate G3 (Step 17); reproducibility section (Step 19) | CPU / GPU |
| 1–31 Dec | Sections VII–IX; literature details; claims and limitations (Steps 18, 20) | CPU lead, BOTH |
| 1–24 Jan | LNCS conversion, length cut, anonymisation; clean re-run (Step 21) | BOTH |
| By 31 Jan | Abstract submitted (confirm date on icdar2027.org) | BOTH |
| 1–20 Feb | Mentor review, final checks, full paper submitted (confirm date) | BOTH + mentor |

Leave room for end-semester exams. If a window slips, move the later windows and keep the order and gates.

## Final submission checklist

- ✅ Protocol approved and tagged `protocol-e2-final` before any full E2 training run.
- ⬜ Corpus, caches and splits verified from pinned hashes (Step 2 corpus check outstanding).
- ✅ Every planned seed reported for `tiles` and `base`; `reg` reported as a pilot.
- ⬜ Calibration, thresholds and fusion chosen on validation only ✅; realised test FPR and recall reported ⬜.
- ✅ Detection recall and rule-coverage recall reported separately and named correctly.
- ⬜ Results broken down by document type, C0–C4 and C1 group.
- ⬜ E6, E7, E8, E9/E12 and E-vis completed, or omissions disclosed.
- ⬜ Person-clustered uncertainty, paired inference and multiplicity correction applied.
- ⬜ Every table and figure regenerates from committed artefacts; no TODOs remain.
- ⬜ Limitations, PAN scope, C4 and OCR boundaries stated accurately.
- ⬜ LNCS format, page limit, anonymity, citations and authorship checked against official rules.
