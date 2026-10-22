# Paper source — version 08 (Sections I–VI complete, VII–IX in preparation)

## Contents

```
main.tex        the whole paper; compile this file
generated/      numbers.tex (auto-generated from the frozen corpus) + earlier table exports
figures/        fig_specimens.pdf, fig_quality_tiers.pdf, fig_ocr_quality.pdf
```

All other figures (system overview, validation flows, generation pipeline,
tile grid, protocol timeline, edit-survival chart) are drawn in TikZ/pgfplots
inside `main.tex`, so they stay sharp and editable.

## Compiling in Overleaf

1. New Project → Upload Project → choose this zip.
2. Main document: `main.tex`. Compiler: **pdfLaTeX**. Compile twice.
3. Do **not** add an `IEEEtran.cls` file; Overleaf provides the real class.

## What changed from version 07

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

> `main_single_file.tex` and `section_IV.tex` in this folder are superseded earlier drafts (v7 and the August Section IV). `main.tex` is the current paper.
