# Paper source — version 7 (complete through Section IV)

## What is here

```
main.tex        the whole paper. This is the file you compile.
generated/      numbers.tex + six table files, ALL auto-generated from the
                built corpus by scripts/export_latex.py in the idforge repo.
                Do not edit these by hand — regenerate them.
figures/        the five Section IV figures as vector PDF.
```

`main.tex` is your previous file with Section IV replaced in full, plus the
edits listed at the bottom of this README. Sections I–III and V–IX are
otherwise untouched.

## Compiling in Overleaf

1. **New Project → Upload Project** and give it this zip. Overleaf keeps the
   `generated/` and `figures/` folders.
2. Set the main document to `main.tex` if Overleaf does not pick it up.
3. Compile with **pdfLaTeX**. Run it **twice** — the cross-references to
   tables and figures need the second pass.

There is **no `IEEEtran.cls` in this zip on purpose**. Overleaf provides the
real one. If you ever see a file called `IEEEtran.cls` next to `main.tex`,
delete it — a local copy will override the real class.

## Compiling locally

```bash
pdflatex main.tex && pdflatex main.tex
```

You need a TeX distribution with `IEEEtran` (`texlive-publishers` on
Debian/Ubuntu, or the `IEEEtran` package via `tlmgr`).

## Why the numbers live in generated/numbers.tex

Every numeral in Section IV — corpus size, split sizes, OCR accuracies,
false-positive rates, leakage-audit outcomes, coincidence bounds — is a LaTeX
macro defined in `generated/numbers.tex`, which is written directly from the
built dataset. Rebuild the corpus, re-run the exporter, recompile, and the
paper updates itself. A number in the text therefore cannot drift away from
the data it describes, and you never have to re-transcribe a figure by hand.

To regenerate after a rebuild, from the idforge repository:

```bash
bash scripts/build_all.sh data/v1        # corpus, audits, figures, LaTeX
cp -r paper/generated  <this folder>/
cp data/v1/figures/*.pdf <this folder>/figures/
```

## What changed relative to your previous main.tex

**Section IV — replaced in full** (was 255 lines, now ~600). It reports the
dataset that actually exists rather than describing one to be built: realised
counts, measured OCR quality, measured rule-branch behaviour on both
ground-truth and OCR text, the five leakage audits, the renderer-leakage
probe, and six figures and six tables drawn from the corpus.

**Section III-A** — the `\TODO` about the admissible Aadhaar leading-digit
range is resolved. The primary numbering document specifies eleven digits plus
a Verhoeff check digit (a nominal $10^{11}$ space) and states no leading-digit
restriction; the "does not begin with 0 or 1" rule is a widely implemented
convention, not a specification. The text now says so, the validator does not
enforce it, and the generator does.

**Bibliography** — the `uidai-scheme` entry is corrected and its `\TODO`
reduced to confirming a page number.

**Title and author block** — the empty `{\footnotesize\textsuperscript{}}`
group and the "Identify applicable funding agency here" placeholder are
removed. The author block was rebuilt with IEEEtran's own
`\IEEEauthorblockN` / `\IEEEauthorblockA` / `\and`: the previous version used
`\IEEEauthorblock`, which IEEEtran does not define, and wrapped two of the
three affiliations in a bare group. That is a compile error Overleaf silently
continues past. If your venue's template wants the "1st / 2nd / 3rd" ordinals
back, add them inside `\IEEEauthorblockN`.

**Abstract** — one sentence added recording that the benchmark now exists,
with its scale and the one result established before any detector is trained.
Nothing about detection performance is claimed.

## TODOs that remain (all yours, none resolvable from the dataset)

| where | what |
|---|---|
| Section II-E | search date, year range, $n_1$, $n_2$, and how many retained records were in venues without indexed peer review |
| Bibliography, `itd-pan` | access date |
| Bibliography, `uidai-scheme` | page reference in the primary PDF |

## Verification performed on this file

Compiled clean: no undefined references, no undefined citations, no overfull
boxes above 10 pt. 18 pages with Sections V–IX still empty. Every `\ds…` macro
used in the text is defined in `generated/numbers.tex` (56 used, 76 defined).
