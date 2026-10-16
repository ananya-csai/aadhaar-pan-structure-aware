# Research Roadmap v3 — Structure-Aware Forgery Detection for Aadhaar and PAN

**Supersedes:** "Final Unified Research Roadmap (GPU and CPU)". Same phases and step numbers. Changes are marked **[v3]**.

**Owners:** [GPU] GPU-laptop owner · [CPU] partner without a GPU · [BOTH] joint.

**Status key:** ✅ done and committed · 🟡 partly done or needs checking · ⬜ not started.
Status was checked against the repository at commit `32eedb4` (16 Oct 2026). Steps marked 🟡 were not checked; confirm them before ticking.

## What changed in v3, and why

1. **[v3] Primary input size is now 768 × 512, not 384 × 256.**
   `experiments/measure_edit_survival.py` showed that shrinking to 384 × 256 erases most of the evidence for two of the five C1 edit types:
   - On clean images, only 10% (`local_recompression`) and 3% (`resample_patch`) of the edit signal survives.
   - These two types make up about 41% of C1.
   - At 768 × 512, 82–87% survives.

   At 384 × 256, the visual baseline would look weak because of our preprocessing. That would unfairly favour the rule branch in RQ1 and RQ3, and a reviewer could catch it. Full numbers and reasoning: `DECISIONS.md`, Amendment A1.
2. **[v3] Resolution sensitivity is now 384 × 256**, using the cache that already exists. 224 × 160 is dropped: it only destroys more evidence and answers no question.
3. **[v3] C1 recall is pre-registered per edit type** (`c1_op`), and in two groups: *fine-trace* (recompression, resampling) and *coarse* (font, displacement, splice). Without this, a pooled C1 number hides the effect above.
4. **[v3] Cache scripts take `--width/--height`**, and the inspection sheet now shows each original beside its cached version. Step 9 required that and it was missing.

Cost of the change: about 1 extra day (a new cache, and more GPU time per run). The four-month plan still holds.

---

## PHASE 0 — Stabilise the project

### Step 1. Agree protocol and target venue [BOTH] — 🟡
- ✅ Draft protocol committed (`8b32a6b`): `DECISIONS.md`, `experiments/EXPERIMENT_PLAN.md`.
- ⬜ **[v3] Commit Amendment A1** (resolution change) together with the edit-survival script and its output.
- ⬜ Partner and mentor approve the six shared decisions **and A1**. Record names and date in `DECISIONS.md`, Section 11.
- ⬜ Settle the open definition of mechanism-aware recall (Section 6).
- ⬜ After approval, tag the commit: `git tag -a protocol-e2-v1 -m "E2 protocol incl. Amendment A1"` and push the tag.
- ⬜ Check ICDAR 2027 dates on the official portal. Planning targets: abstract 31 Jan 2027, full paper 20 Feb 2027.

### Step 2. Verify corpus, manifest and repository state [CPU + GPU] — 🟡
- ✅ Corpus SHA-256 and dataset tags recorded in `DECISIONS.md`.
- ✅ Person-level split check committed (`verify_splits.py`).
- 🟡 [GPU] Run `dataset/scripts/corpus_checksum.py --verify` on your copy and save its output.
- 🟡 [CPU] Save `git status`, `git log --oneline --decorate` and `git tag -l` output into the run log.

### Step 3. Reconcile stale report and dataset documentation [CPU] — 🟡
- Unchanged from the unified roadmap: the FPR mismatch (4.1/18.9 vs 3.8/19.7), the 5,824 vs 5,848 hashes, the Table IX 256-bit hash code, and the README size and runtime.

## PHASE 1 — Canonical rule-only evaluation (CPU)

### Step 4. Build and test `evaluate.py` [CPU] — ⬜
- Unchanged.
- **[v3]** It must also report recall per `c1_op` and per pre-declared group (fine-trace / coarse). Test that with a toy predictor.

### Step 5. Reproduce E3 and commit the canonical test report [CPU] — 🟡
- `experiments/e3_rule_branch/` exists. Check that it matches the unified roadmap's requirements (GT and OCR, by document type and C0–C4, exact commit).

## PHASE 2 — Leakage and construction checks

### Step 6. Direct split and duplicate audits [CPU] — ✅
- ✅ Committed (`744f166`): split separation, exact hashes and pHash candidates, with the limitation stated.
- ✅ **[v3] "Is each edit visible at the approved resolution?"** This is now answered by measurement, not by eye: `measure_edit_survival.py`.

### Step 7. Validate any learned leakage probe [GPU + BOTH] — 🟡
- Unchanged. If the probe's positive control is not done, limit claims to the Step 6 audits.

## PHASE 3 — Visual baseline (GPU)

### Step 8. GPU environment and sanity checks [GPU] — 🟡
- ✅ `experiments/requirements-vision.txt` committed.
- ⬜ Record GPU model, VRAM, OS, Python, PyTorch and CUDA. Confirm `torch.cuda.is_available()`.
- ⬜ **[v3] Smoke test at 768 × 512** with mixed precision (AMP):
  - Use the largest batch of 32, 16 or 8 that fits.
  - If it is below 32, use gradient accumulation to an effective batch of 32.
  - Record batch size and seconds per epoch.

  This choice uses memory only, never accuracy.
- ⬜ Tiny-overfit test: 50 train images (C0 and C1), training accuracy close to 100%.

### Step 9. Resize caches and loader [GPU; CPU reviews] — 🟡
- ✅ 384 × 256 cache built and fingerprinted (`32eedb4`, hash `a9c0ba03…`). This is now the **sensitivity** cache.
- ⬜ **[v3] Build the primary cache**, about 5–6 GB. Do not commit it.
  ```
  python experiments/build_resize_cache.py --width 768 --height 512
  python experiments/inspect_resize_cache.py --width 768 --height 512
  python experiments/fingerprint_resize_cache.py --width 768 --height 512
  ```
- ⬜ **[v3] Regenerate the 384 × 256 contact sheet** with the new side-by-side script (`python experiments/inspect_resize_cache.py`). Open both sheets and check:
  - cropping, colour order and aspect ratio;
  - visible edits in the C1 rows.
- ⬜ Loader: manifest `split` column only, RGB, ImageNet normalisation, one output per `image_id`. Both sizes must go through the same loader; only `--width/--height` differs.

### Step 10. Train E2 [GPU] — ⬜
- ResNet-50 (ImageNet-pretrained), one-logit head, C0 vs C1, early stopping on validation.
- **[v3] Primary:** 5 seeds at 768 × 512. **Sensitivity:** the same 5 seeds at 384 × 256. Everything else stays identical.
- Save for every run: checkpoint, raw logits, config, curves, PR-AUC/AUROC on validation, runtime, environment.
- **[v3] Score all 10,800 images** (C0–C4) with each frozen model, not just C0/C1. Fusion in Phase 4 needs visual scores for every category.
- Report every seed. Do not look at test scores.

### Step 11. Validate outputs and freeze [GPU + CPU] — ⬜
- Unchanged. Freeze the 768 × 512 configuration as primary **before** looking at any 384 × 256 vs 768 × 512 comparison.

## PHASE 4 — Recovery, calibration and fusion

### Steps 12–15 — ⬜
- Unchanged. Fusion is built and frozen on the **primary (768 × 512)** visual scores.
- **[v3]** In Step 12, count both-detect / visual-only / rule-only / neither **per `c1_op` group** as well as by C1–C4.
- **[v3]** Step 15: run the frozen test evaluation for both resolutions. The 384 × 256 arm reuses the same fusion rule and its own validation-chosen threshold. No retuning on test.

## PHASE 5 — Robustness, explanations and statistics

### Step 16. E6–E9/E12 [CPU; GPU supplies scores] — ⬜
- **[v3] New analysis, "E-res" (resolution sensitivity):** C1 recall at 768 × 512 vs 384 × 256, per `c1_op` group, with person-clustered bootstrap CIs.
  - Expected: little change on coarse edits, and a large drop on fine-trace edits.
  - If there is no drop, report that honestly. It would mean the model is not using fine traces even at 768 × 512.
- Optional analyses: unchanged. Drop "resolution sensitivity" from the optional list, because E-res now covers it.

### Step 17. Cluster-aware statistics [CPU] — ⬜
- Unchanged. Add E-res to the pre-defined comparison families for Holm correction.
- Note: there are about 54 test C1 images per `c1_op` from 45 people, so per-operation CIs will be wide. Lead with the two groups; per-operation results are supporting detail.

## PHASE 6 — Paper and submission

### Step 18. Results and Sections VI–IX [CPU] — ⬜
- **[v3]** Section VI must state the input size, the resize policy, the edit-survival measurement and Amendment A1.
- **[v3]** RQ1 asks about "conventional, visually apparent forgeries". Fine-trace edits are not visually apparent. Answer RQ1 separately for the two groups rather than with one pooled number. Do not reword RQ1 silently; if the wording changes, record it as a decision.

### Steps 19–21 — ⬜
- Unchanged. Step 19 also reports both canvas sizes, the batch-size rule and its outcome.
- Step 20 adds one limitation: the visual baseline is a whole-document ResNet-50 at 768 × 512. A higher-resolution or crop-based detector might catch more fine-trace edits.

---

## Timeline (unchanged dates)

| Window | Milestone | Lead |
|---|---|---|
| Days 1–2 | Commit A1, partner/mentor approval, tag `protocol-e2-v1`, report reconciliation | BOTH |
| Days 3–5 | 768 × 512 cache + loader + smoke test + tiny-overfit; canonical E3 report | GPU / CPU |
| Days 5–15 | E2: 5 seeds × 2 resolutions; scores for all 10,800 images | GPU; CPU reviews |
| Days 15–18 | Freeze configs, test once, recovery analysis, fusion | BOTH |
| Weeks 3–5 | E6–E9/E12, E-res, cluster-aware statistics, lock results | CPU; GPU supplies scores |
| Weeks 5–8 | Sections VI–IX, literature audit, LNCS formatting, clean reproduction | BOTH |
| By 31 Jan 2027 | Abstract (verify portal) | BOTH |
| By 20 Feb 2027 | Full paper (verify portal) | BOTH |

## Final submission checklist — additions in v3
- [ ] Amendment A1 committed and approved **before** any E2 training run.
- [ ] Both caches fingerprinted; hashes recorded in the paper's reproducibility section.
- [ ] C1 recall reported per `c1_op` group for both resolutions, with CIs.
- [ ] RQ1 answered separately for fine-trace and coarse edits.
- Everything else as in the unified roadmap's checklist.
