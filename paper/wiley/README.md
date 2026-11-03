# Paper in the Wiley NJD-v5 template

Same content as paper v15 (IEEE version), moved into Wiley's general
New Journal Design v5 template.

## Open in Overleaf

1. Overleaf home → **New Project → Upload Project** → choose this zip.
2. **Menu** (or the Settings gear) → **Compiler: XeLaTeX**, **TeX Live version: 2022**.
   The template does not work with TeX Live 2023 or with pdfLaTeX.
3. Main document: `main.tex`. Click **Recompile**.

## Files

```
main.tex          the paper (edit this)
references.bib    all 38 references (BibTeX)
generated/        tables and plots generated from the experiment results
figures/          image figures
WileyNJDv5.cls, *.bst, *.sty, Fonts/   Wiley template files (do not edit)
```

## Reference style

The first line of `main.tex` is

    \documentclass[VANCOUVER,Times1COL]{WileyNJDv5}

- `VANCOUVER`: numbered, superscript citations (the usual Wiley numbered style).
- When the journal is chosen, replace it with the style in the journal's author
  guidelines: `AMA`, `APA`, `HARVARD`, `CHICAGO`, `AMS`, `MLA`, `APS`, `MPS`.
  Author–year styles (APA, Harvard, Chicago) also need sentence-level checks,
  because the text was written for numbered citations.
- `Times1COL` = single column, Times font (normal for submission).

## What changed from the IEEE version (v15)

- Wiley title page: author block, correspondence, abstract box, keywords.
- Author note: all three authors contributed equally and share first authorship;
  all three are listed as corresponding authors.
- Back matter added: Author contributions, Declaration of generative AI and
  AI-assisted technologies, Financial disclosure, Conflict of interest,
  Data availability statement, Ethics statement.
- The "Data and code availability" paragraph of Section 6 moved to the Data
  availability statement; the Zenodo DOI now reads "will be made publicly
  available ... upon publication" (the record is still a draft).
- Bibliography converted from a hand-written list to `references.bib`; DOIs kept.
- Appendix moved after the references, as the template requires.
- Figures drawn for one IEEE column scaled to 72–75% of the text width.
- No result, number, table, equation or citation changed.

## The authors must check before showing or submitting

1. **Author contributions**: the roles listed are a draft based on who did what
   in the project. Correct them.
2. **Financial disclosure**: "None reported." Change it if there was any funding.
3. **Journal fields** (`\journal{Journal}`, dates, "How to cite" box): placeholders
   filled by Wiley at production; set `\journal{...}` once the journal is chosen.
4. **Word limit**: about 20,700 words now; most Wiley journals ask for far less.
   Cut to the chosen journal's limit.
5. **Double-blind journals** need an anonymised version (no names, affiliations,
   e-mails or repository link in the manuscript).

## In this repository

`paper/wiley/` holds only the files we wrote: `main.tex`, `references.bib`
and the converter `to_wiley.py`. The Wiley class, styles and fonts come from
the official NJD-v5 template on Overleaf and are not stored here (the fonts
are not freely redistributable). To rebuild `main.tex` and the scaled plot
files from the IEEE source:

    python paper/wiley/to_wiley.py paper/main.tex paper/generated <out dir>
