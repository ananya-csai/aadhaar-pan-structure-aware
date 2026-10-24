# Paper source — version 10 (Sections I–VI and Appendix A complete, VII–IX in preparation)

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

## What changed from version 09

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
| Section II-E | search date, year range, n1, n2, count of non-peer-reviewed records |
| Ref. [5] (`itd-pan`) | access date |
| Ref. [3] (`uidai-scheme`) | page reference in the primary PDF |
| Appendix A-1 (L4) | result of the Step 21 clean re-run of one tile seed |
