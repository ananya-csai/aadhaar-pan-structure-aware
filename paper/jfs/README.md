# Paper — Journal of Forensic Sciences version (current)

The manuscript formatted for the *Journal of Forensic Sciences* (JFS, Wiley /
American Academy of Forensic Sciences), following the JFS *Information for
Authors* (June 2025) and the JFS statement on the use of artificial
intelligence.

The text is the master text in `paper/wiley/main.tex`, converted by the
scripts in `build/`. Every change to the wording made by the conversion is
listed in [`CHANGES_FROM_WILEY.txt`](CHANGES_FROM_WILEY.txt).

## Files

| File | What it is | Upload to JFS? |
|---|---|---|
| `manuscript.tex` | anonymised manuscript: title, abstract + keywords, highlights, text, references, tables, figure legends; double-spaced, line-numbered | yes, as the main document (compiled PDF) |
| `supplementary.tex` | Supplemental Information, Appendix S1 (reproducibility record, Tables S1–S3), anonymised | yes, as Supplemental Information |
| `figure_pdf/FigureN.pdf` | vector copies of the 12 figures, numbered in order of first citation | no; upload the TIFF files made by the build |
| `manuscript_with_figures.tex` | reading copy: the manuscript with the figures appended | no |
| `generated/numbers.tex` | dataset numbers (thousands separators added) | — |
| `build/` | conversion and figure scripts | — |

The title page and the cover letter contain contact details and are not kept
in this public repository.

## How the JFS rules were applied

- **Double-blind review:** no names, affiliations, e-mail addresses,
  repository links, commit hashes or author initials in the manuscript or
  the supplement; PDF metadata empty. The links are on the title page.
- **Order:** title / abstract and keywords (own page) / highlights (own page)
  / text / references / tables / figure legends (last pages).
- **Headings:** INTRODUCTION, MATERIALS AND METHODS, RESULTS, DISCUSSION,
  CONCLUSIONS (bold capitals); subheadings in italics; sub-subheadings plain.
- **Abstract:** 245 words (limit 250), unstructured. **Keywords:** eight,
  including the forensic specialty and both spelled-out terms and
  abbreviations. **Highlights:** five sentences, each under 100 characters.
- **References:** Vancouver/NLM style, numbered in order of first citation,
  [n] in the text, six authors then "et al.", NLM journal abbreviations,
  DOI at the end. References cited only in a table or legend are numbered
  where that table or figure is first cited.
- **Tables:** after the references, one per page, "TABLE n" legends, no
  internal rules or shading, footnote symbols in the order *, †.
- **Figures:** not embedded; separate TIFF files at 600 dpi, numbered in
  order of first citation; legends on the last pages.
- **Generative AI:** the authors' declaration is in Methods (Section 2.5) and
  repeated in the title-page Acknowledgments, as the JFS AI statement asks.

## Rebuild

From the repository root (pdfLaTeX, Python 3 with Pillow and pypdf):

    bash paper/jfs/build/make_jfs.sh

The script rebuilds the files above from the master text and prints the
folder that holds the PDFs and `figure_files/FigureN.tif`. The build is
deterministic: the same inputs give identical LaTeX sources and identical
TIFF files.

## During review

JFS does not allow versions revised in response to reviewers to be posted
publicly while the paper is under review. Keep revised manuscripts out of
this repository until a decision is made.
