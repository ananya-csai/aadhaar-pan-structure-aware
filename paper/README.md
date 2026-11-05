# Paper source

> **Structure-Aware Forgery Detection for Aadhaar and Permanent Account Number
> Cards: A Controlled Study of Visual, Structural, and Semantic Evidence Fusion**

The same paper exists in three layouts. The text is maintained in the Wiley
version; the journal version is generated from it.

| Folder / file | Layout | Status |
|---|---|---|
| [`jfs/`](jfs/) | *Journal of Forensic Sciences*: anonymised, double-spaced, figures as separate files | **current** (generated from `wiley/main.tex`) |
| [`wiley/`](wiley/) | Wiley New Journal Design v5 (XeLaTeX) | master text |
| `main.tex` | IEEE conference layout (paper v15) | earlier version; also the input of `wiley/to_wiley.py` |
| `archive/` | early drafts (Section IV draft, single-file v7 source) | historical record only |

Shared inputs:

```
generated/   numbers.tex and the result tables, written by scripts/ from the
             committed experiment outputs (CI checks that they regenerate)
figures/     image figures made by the released generator
scripts/     make_results_tables.py, make_c1_figure.py
```

[`CHANGELOG.md`](CHANGELOG.md) records what changed between the IEEE
versions (v12–v15).
