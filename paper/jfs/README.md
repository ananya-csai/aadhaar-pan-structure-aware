# Paper — Journal of Forensic Sciences version (current)

The manuscript formatted for the *Journal of Forensic Sciences* (JFS, Wiley /
American Academy of Forensic Sciences), following the JFS *Information for
Authors* (June 2025) and the JFS statement on the use of artificial
intelligence.

The text is the master text in `paper/wiley/main.tex`, converted by the
scripts in `build/`. Every change to the wording made by the conversion is
listed in [`CHANGES_FROM_WILEY.txt`](CHANGES_FROM_WILEY.txt).

## Files

| File | What it is |
|---|---|
| `manuscript.tex` | anonymised manuscript: title, abstract + keywords, highlights, text, references, tables, figure legends; double-spaced, line-numbered |
| `supplementary.tex` | Supplemental Information, Appendix S1 (reproducibility record, Tables S1–S3), anonymised |
| `figure_pdf/FigureN.pdf` | vector copies of the 12 figures, numbered in order of first citation |
| `figure_pages.tex`, `figure_map.txt` | figure pages of the reading copy; map from paper figures to JFS figure numbers |
| `manuscript_with_figures.tex` | reading copy: the manuscript with the figures appended (not for upload) |
| `generated/numbers.tex` | dataset numbers (thousands separators added) |
| `build/` | conversion, figure and Word scripts |

The build (below) also writes, outside the repository, the compiled PDFs,
the 600-dpi TIFF figures and `manuscript.docx`, the Word copy of the
manuscript. The title page, the cover letter and the conflict-of-interest
statement contain contact details and are not kept in this public
repository.

## What goes into the JFS submission portal

| Portal item | File |
|---|---|
| Anonymized Main Document (MS Word) | `manuscript.docx` (from the build) |
| Title Page (MS Word) | kept outside the repository |
| Conflict of Interest (one document for all authors) | kept outside the repository |
| Figure (TIFF, at least 300 dpi, not embedded) | `figure_files/Figure1.tif` … `Figure12.tif` (from the build) |
| Supplementary Material for Review | `supplementary.pdf` (from the build) |

Abstract, keywords and highlights are pasted into the submission form exactly
as they appear in the manuscript.

## How the JFS rules were applied

- **Double-blind review:** no names, affiliations, e-mail addresses,
  repository links, commit hashes or author initials in the manuscript or
  the supplement; file metadata empty. The links are on the title page.
- **Order:** title / abstract and keywords (own page) / highlights (own page)
  / text / references / tables / figure legends (last pages).
- **Headings:** INTRODUCTION, SEARCH PROTOCOL, MATERIALS AND METHODS,
  RESULTS, DISCUSSION, CONCLUSIONS (bold capitals); subheadings in italics;
  sub-subheadings plain.
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
- **Word copy:** Times New Roman 12 pt, double-spaced, continuous line
  numbers and page numbers; equations are editable Word equations (they
  display in Microsoft Word; LibreOffice does not show them).
- **Generative AI:** the authors' declaration is in Materials and Methods
  (Section 3.5) and repeated in the title-page Acknowledgments, as the JFS AI
  statement asks.

## Rebuild

From the repository root (pdfLaTeX; Python 3 with Pillow and pypdf; for the
Word copy also pandoc and python-docx):

    bash paper/jfs/build/make_jfs.sh

The script rebuilds the LaTeX files above from the master text and prints
the folder that holds the PDFs, `manuscript.docx` and
`figure_files/FigureN.tif`. The LaTeX sources and the TIFF files are
deterministic: the same inputs give identical files.

## During review

JFS does not allow versions revised in response to reviewers to be posted
publicly while the paper is under review. Keep revised manuscripts out of
this repository until a decision is made.
