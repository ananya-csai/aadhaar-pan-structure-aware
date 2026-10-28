# Paper source — version 13 (all sections complete; no red TODO left)

## Contents

```
main.tex        the whole paper; compile this file
generated/      numbers.tex (auto-generated from the frozen corpus) + earlier table exports
figures/        fig_specimens.pdf, fig_quality_tiers.pdf, fig_ocr_quality.pdf,
                fig_c1_ops.pdf (made by scripts/make_c1_figure.py from the released generator)
```

All other figures (system overview, validation flows, generation pipeline,
tile grid, protocol timeline, edit-survival chart) are drawn in TikZ/pgfplots
inside `main.tex`, so they stay sharp and editable.

## Compiling in Overleaf

1. New Project → Upload Project → choose this zip.
2. Main document: `main.tex`. Compiler: **pdfLaTeX**. Compile twice.
3. Do **not** add an `IEEEtran.cls` file; Overleaf provides the real class.

## What changed from version 12 (in version 13)

- Appendix A, L4: the Step 21 clean re-run of tile seed 0 is reported (red
  TODO removed). Under the pre-registered rule it formally failed: Git for
  Windows converted the line endings of `c1_regions.csv`, so its recorded
  digest changed (content identical). The metric check passed, and the re-run
  is bit-identical to the original (every epoch, all scores, the checkpoint).
  The sentence "a second run ... is expected to differ slightly" is replaced by
  what was observed; other hardware was not tested, so the five seeds remain
  the unit of variation.
- Table XX (levels): L4 row updated. Table XXI (runs): re-run row added.
  Table XIX (protocol record): "Re-run, 29 Oct" row added.

## What changed from version 11 (in version 12)

- Section IX (Conclusion and Future Work) written.
- Section II-E: the literature-search placeholders are replaced by a real,
  documented search (Crossref, 28 Oct 2026, 64 queries, 573 works screened,
  68 included). Queries, all records and every screening decision are in the
  repository (`docs/literature_search/`).
- Section II: five newly found works cited (Lim and Connie 2026; Kumar et al.
  2026; three PAN tampering papers and one Aadhaar e-KYC paper, stated as only
  partly accessible). Table I gains two rows.
- References corrected against publisher metadata: Shaikh and Patil is in
  IJIRT, not IJARCCE; the PAN-recognition paper's authors are Devi, Gokula and
  Gladence (the text said "Lakshmi et al."); IDNet's current title and author
  order; page numbers added; unverified LNCS volume removed; the Income Tax
  reference now points to the official FAQ page (accessed 28 Oct 2026); the
  UIDAI numbering-scheme reference gives pages 6 and 12.
- Section VII: AUROC/PR-AUC of the fused scores; Section VIII: the closest
  hybrid design is discussed. Abstract: "that we reviewed" qualifier, the
  rule false-positive rate, and the C4 sentence made exact.
- `xurl` instead of `url` so long URLs break inside the column.

## What changed from version 10 (in version 11)

- Section VII Results written: RQ1–RQ6 and per-check fusion / fresh
  confirmation. Tables XIV–XVIII and Fig. 11 are generated from the committed
  analysis output by `paper/scripts/make_results_tables.py` in the repository
  (files `generated/res_*.tex`);
  no table number is typed by hand.
- Section VIII Discussion written: interpretation, relation to prior work,
  limitations, threats to validity.
- Abstract and contributions corrected to match the results: C4 is flagged at
  each system's false-positive rate (not "evades every configuration"), and OCR
  removes about three quarters of the ground-truth gain (not "more than half").
- Appendix A: new protocol row for the analysis plan (DECISIONS.md §22).

## What changed from version 09 (in version 10)

- New Appendix A, Reproducibility Record (roadmap Step 19): how exactly each
  stage can be repeated (Table XV), all eleven visual training runs with
  epochs, minutes, validation metrics and temperatures (Table XVI), the
  training environment, and a dated protocol record of every amendment,
  correction and run event (Table XIV).
- Appendix A reports an independent Linux rebuild of the corpus: 10,791 of
  10,800 images byte-identical after fixing the text-layout engine.
- Section VI-G shortened; the continuous-integration claim now states exactly
  what is checked; the data-availability note mentions per-image digests.
- One new red TODO in Appendix A, filled after the Step 21 re-run.

## What changed from version 08 (in version 09)

- Title block now matches the requested format: every author marked `*†`,
  one corresponding-author e-mail block (one address per line) and the
  equal-contribution note. To change who is corresponding, edit the `*`
  marks and the e-mail list in `\author{...}`.
- Section III opens with a formal problem setting (recall, false-positive
  rate, incremental value Δ, OCR retention ρ) and an explicit threat model;
  adds a Verhoeff worked example and a table of the cross-field rule on
  typical name forms.
- Section IV adds the exact C1 edit parameters with a close-up figure of the
  five operations, a capture-simulation parameter table, a per-check
  false-positive chart and a table of real OCR misreads.
- Section V adds the tile-score, tile-label, calibration, threshold, fusion
  objective and matched-threshold equations, and Algorithm 1 (verification
  of one document).
- Section VI adds formulas for the three recalls, the person-clustered
  paired bootstrap and Holm's correction, and a data/code availability note.
- Layout: all lines fit the column even with columns 0.1 in narrower than
  IEEE's; floats re-ordered so figures follow their first mention.

## What changed from version 07 (in version 08)

- Title block restyled: numbered affiliations, corresponding author and
  contributing-author e-mails. To mark equal contribution, un-comment the
  `\dag` line in `\author{...}` and add `\textsuperscript{\dag}` to the
  relevant names.
- Sections I–VI rewritten and tightened (about 30% shorter through Section IV).
  New: Fig. 1 system overview, Table I positioning, Fig. 2 merged validation
  flows, Fig. 6 tile grid, Fig. 7 protocol timeline, Fig. 8 edit survival,
  Tables VII–X (explanations, systems, model selection, fusion weights).
- Methodology and setup now cover the frozen visual branch, fusion A4,
  the post-hoc per-check fusion A5 and the pre-registered fresh test set (A6).
- OCR engine corrected to Tesseract 5.5.3 / Leptonica 1.87.0 (the engine that
  produced the frozen corpus).
- Six references added (Wilson, ImageNet, AdamW, temperature scaling,
  bootstrap, Holm); bibliography is in order of first citation.
- Sections VII–IX remain placeholders until the Step 16–17 analyses are locked.

## Items only the authors can fill (shown in red)

| Where | What |
|---|---|
| — | none left in version 13 |

Recommended before submission (not marked in the PDF):
- Open the archived UIDAI PDF (link in Ref. [3]) once and confirm pages 6 and 12.
- With institutional access, read the seven Aadhaar/PAN papers listed in
  `docs/literature_search/README.md` that could not be assessed, and adjust
  Section II-B if any of them applies check-digit or cross-field rules.
