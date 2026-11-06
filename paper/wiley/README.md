# Paper in the Wiley NJD-v5 template (master text)

This folder holds the master text of the paper. The *Journal of Forensic
Sciences* (JFS) submission files in `../jfs/` are generated from it by
`../jfs/build/make_jfs.sh`, which removes the names, ORCID iDs, e-mail
addresses and links for double-blind review.

## Current version: v4 (6 Nov 2026)

`main.tex` is the Wiley-template copy of the paper submitted to the Journal of
Forensic Sciences:

- journal field, page header and "How to cite" line: Journal of Forensic
  Sciences; article type "Original Paper";
- authors with ORCID iDs (linked iD logo next to each name, and an "ORCID"
  section before the references), departments and postal address of
  Manipal University Jaipur; Ananya Shukla and Soham Phulwaria as equal first
  authors; corresponding author Dinesh Kumar Saini;
- e-mail addresses of the first authors in a footnote on page 1, the
  corresponding author's in the Correspondence box;
- keywords identical to the JFS submission, including the forensic specialty
  (questioned documents);
- back matter: author contributions, generative-AI declaration,
  acknowledgments, funding, conflict of interest, data availability, ethics,
  permissions.

v4 changed only the title-page information and the end statements; the text
of the paper is word-for-word the same as v3.

Version history: v1 (IET Image Processing layout), v2 (preamble tidy-up),
v3 (author details, Section 2 renamed "Search Protocol", Limitations as one
paragraph), v4 (this version).

## Open in Overleaf

1. Overleaf home → **New Project → Upload Project** → choose the zip made from
   this folder plus the Wiley template files (see below).
2. **Menu** → **Compiler: XeLaTeX**, **TeX Live version: 2022** or later.
3. Main document: `main.tex`. Click **Recompile** (about 5 seconds).

Do not add the old `listings.sty` (v1.8d) that comes with the Wiley template:
it stops the paper compiling on TeX Live 2023 and later. The standard
`listings` package of the TeX Live installation is used instead.

## Files

```
main.tex          the paper (edit this)
references.bib    all 38 references (BibTeX)
tikzfig/          the drawn figures as ready-made PDFs (used by main.tex)
tikz_src/         TikZ source of the drawn figures
graphical_abstract.tex / .png   graphical abstract (pdflatex, 600 dpi)
to_wiley.py, externalize.py   scripts that built the first Wiley version
rerender.py       re-renders the figures in tikzfig/ from tikz_src/ with the current preamble
```

The Wiley class, styles and fonts (`WileyNJDv5.cls`, `*.bst`, `*.sty`,
`Fonts/`) come from the official NJD-v5 template on Overleaf and are not
stored here, because the fonts are not freely redistributable.
`orcidlink.sty` is a standard CTAN package included in TeX Live. The tables in
`../generated/` and the image figures in `../figures/` are shared with the
other layouts.

## Reference style

`\documentclass[VANCOUVER,Times1COL]{WileyNJDv5}`: numbered Vancouver
citations, single column, Times font.

## Compile time (Overleaf free plan)

Overleaf's free plan stops any compile that takes longer than 10 seconds. The
12 TikZ/pgfplots figures are therefore included as ready-made PDFs from
`tikzfig/`; a full clean build takes about 5 seconds. Their source is in
`tikz_src/`.

## History of the scripts

`to_wiley.py` converted the IEEE version (paper v15, `../main.tex`) into the
first Wiley version, and `externalize.py` replaced the TikZ figures by the
PDFs in `tikzfig/`. `main.tex` has been edited by hand since then (v1–v4), so
running these scripts again does not reproduce the current file.
