"""Convert paper v15 (IEEEtran) into the Wiley NJD-v5 template.

    python paper/wiley/to_wiley.py paper/main.tex paper/generated <out dir>

Writes <out dir>/main.tex and <out dir>/generated/*.tex. The Wiley class,
styles and fonts come from the official NJD-v5 template on Overleaf and are
not stored in the repository (the fonts are not freely redistributable).

Only the frame changes (class, author block, abstract, back matter, citations,
bibliography). Body text, tables, figures and equations are carried over
verbatim, apart from the small edits listed in EDITS.
"""
import re
import sys
from pathlib import Path

src = open(sys.argv[1], encoding="utf-8").read()


def between(a, b, s=src):
    i, j = s.index(a), s.index(b)
    assert i < j, (a, b)
    return s[i + len(a):j]


def once(s, a, b):
    n = s.count(a)
    if n != 1:
        sys.exit(f"expected exactly one match, found {n}: {a[:80]!r}")
    return s.replace(a, b)


# ---------------------------------------------------------------- pieces
preamble_defs = between(r"% --- colour palette used by every figure ------------------------------",
                        r"\input{generated/numbers}")
preamble_defs = once(preamble_defs, "\\newcommand{\\email}[1]{\\href{mailto:#1}{\\textcolor{blue}{#1}}}\n", "")
abstract = between(r"\begin{abstract}", r"\end{abstract}").strip()
keywords = between(r"\begin{IEEEkeywords}", r"\end{IEEEkeywords}").strip()
body = between(r"\end{IEEEkeywords}", r"%======================================================================" "\n" r"\appendices")
appendix = between(r"\appendices", r"%======================================================================" "\n" r"\begin{thebibliography}")

# ---------------------------------------------------------------- body edits
EDITS = [
    # The availability paragraph moves to the Data Availability Statement.
    (body, r"""\paragraph*{Data and code availability.} The generator, configuration,
manifests, frozen model scores, calibration and fusion parameters, the
protocol file and all evaluation scripts are available at
\url{https://github.com/ananya-csai/aadhaar-pan-structure-aware}.
Images are not stored in the repository; they regenerate from the seed,
and released per-image SHA-256 digests show which rebuilt images, if
any, differ (Appendix~\ref{app:repro}). The five trained tile-model checkpoints
are archived at \url{https://doi.org/10.5281/zenodo.23618373}.
""", r"""Code, data generator and model checkpoints are described in the Data
Availability Statement.
"""),
    # Superscript citations: a citation must not follow "in".
    (body, r"exactly as published in~\cite{verhoeff}", r"exactly as published by Verhoeff\cite{verhoeff}"),
]
for _ in EDITS:
    pass
body = once(body, EDITS[0][1], EDITS[0][2])
body = once(body, EDITS[1][1], EDITS[1][2])

appendix = once(appendix, "\\section{Reproducibility Record}", "\\bmsection{Reproducibility record}")
appendix = appendix.replace("\\subsection{", "\\bmsubsection{")


def fix_cites(s):
    # Superscript citation style: attach the marker to the preceding word.
    s = re.sub(r"~\\cite\{", r"\\cite{", s)
    s = re.sub(r" \\cite\{", r"\\cite{", s)
    return s


body, appendix, abstract = fix_cites(body), fix_cites(appendix), fix_cites(abstract)

# Single-column layout: figures drawn for one IEEE column would span the
# full text width, so they are scaled to a readable size.
body = once(body, r"\includegraphics[width=\columnwidth]{figures/fig_c1_ops.pdf}",
            r"\includegraphics[width=0.72\textwidth]{figures/fig_c1_ops.pdf}")
body = body.replace(r"width=\columnwidth, height=", r"width=0.75\textwidth, height=")
assert "\\cite" not in abstract

# ---------------------------------------------------------------- document
out = r"""%======================================================================
%  Structure-Aware Forgery Detection for Aadhaar and PAN
%  Wiley New Journal Design v5 (NJD-v5) version of paper v15.
%
%  Overleaf: Menu -> Compiler: XeLaTeX, TeX Live version: 2022.
%  References: references.bib with Wiley's numbered Vancouver style
%  (option VANCOUVER below). When the journal is chosen, change the option
%  to the style it requires (e.g. AMA, APA, HARVARD).
%======================================================================
\PassOptionsToPackage{table}{xcolor}
\documentclass[VANCOUVER,Times1COL]{WileyNJDv5}

% amsmath, amssymb, booktabs, algorithm and algpseudocode are loaded by the class.
\algtext*{EndFor}% omit "end for" / "end if" lines, as in the original layout
\algtext*{EndIf}
\usepackage{array}
\usepackage{makecell}
\usepackage{pifont}
\usepackage{tikz}
\usetikzlibrary{shapes.geometric, arrows.meta, positioning, calc, fit,
                backgrounds, decorations.pathreplacing, patterns}
\usepackage{pgfplots}
\pgfplotsset{compat=1.17}
\usepackage[most]{tcolorbox}
\usepackage{xurl}
\usepackage{placeins}

% --- float placement --------------------------------------------------
\setcounter{topnumber}{3}
\setcounter{bottomnumber}{2}
\setcounter{totalnumber}{4}
\renewcommand{\topfraction}{0.92}
\renewcommand{\bottomfraction}{0.70}
\renewcommand{\textfraction}{0.06}
\renewcommand{\floatpagefraction}{0.70}
\AtBeginDocument{\hypersetup{hidelinks}}

""" + "% --- colour palette used by every figure ------------------------------" + preamble_defs + r"""\input{generated/numbers}

\articletype{Research Article}

\received{Date Month Year}
\revised{Date Month Year}
\accepted{Date Month Year}
\journal{Journal}
\volume{00}
\copyyear{2026}
\startpage{1}

\raggedbottom

\begin{document}

\title{Structure-Aware Forgery Detection for Aadhaar and PAN: A Controlled Study of Visual, Structural, and Semantic Evidence Fusion}

\author[1]{Ananya Shukla}
\author[2]{Soham Phulwaria}
\author[3]{Dinesh Saini}

\authormark{SHUKLA \textsc{et al.}}
\titlemark{STRUCTURE-AWARE FORGERY DETECTION FOR AADHAAR AND PAN}

\address[1]{\orgdiv{Department of Computer Science and Engineering}, \orgname{Manipal University Jaipur}, \orgaddress{\state{Jaipur, Rajasthan}, \country{India}}}

\address[2]{\orgdiv{Department of Computer Science (AI and ML)}, \orgname{Manipal University Jaipur}, \orgaddress{\state{Jaipur, Rajasthan}, \country{India}}}

\address[3]{\orgdiv{Department of IoT and Intelligent Systems}, \orgname{Manipal University Jaipur}, \orgaddress{\state{Jaipur, Rajasthan}, \country{India}}}

\corres{Ananya Shukla, Soham Phulwaria and Dinesh Saini, Manipal University Jaipur, Jaipur, Rajasthan, India.
\email{ananya.2427030029@muj.manipal.edu};
\email{soham.2427010107@muj.manipal.edu};
\email{dineshkumar.saini@jaipur.manipal.edu}}

\jnlcitation{\cname{%
\author{Shukla A},
\author{Phulwaria S}, and
\author{Saini D}}.
\ctitle{Structure-aware forgery detection for Aadhaar and PAN: a controlled study of visual, structural, and semantic evidence fusion.} \cjournal{\it Journal.} \cvol{2026;00(00):1--00}.}

\abstract[Abstract]{""" + abstract + r"""}

\keywords{""" + keywords + r"""}

\maketitle

\renewcommand\thefootnote{}
\footnotetext{\textbf{Author note:} All three authors contributed equally to this work and share first authorship.}

\renewcommand\thefootnote{\fnsymbol{footnote}}
\setcounter{footnote}{1}
""" + body + r"""
%======================================================================
\bmsection*{Author contributions}

All three authors contributed equally to this work and share first
authorship. Ananya Shukla: conceptualization, methodology, software,
formal analysis, validation, writing (original draft), writing (review
and editing). Soham Phulwaria: conceptualization, methodology, software,
investigation, data curation, resources, writing (original draft),
writing (review and editing). Dinesh Saini: conceptualization,
methodology, supervision, project administration, writing (review and
editing).

\bmsection*{Declaration of generative AI and AI-assisted technologies}

During the preparation of this work, the authors used Claude
(Anthropic) to assist with drafting parts of the text, language
improvement and editing of the manuscript, and analysis scripting. The
authors designed the study, made all methodological decisions, ran the
experiments, and reviewed, revised and verified all text, code and
results themselves. The authors take full responsibility for the content
of this published article.

\bmsection*{Financial disclosure}

None reported.

\bmsection*{Conflict of interest}

The authors declare no potential conflict of interests.

\bmsection*{Data availability statement}

The data generator, configuration files, manifests, frozen model
scores, calibration and fusion parameters, the protocol file and all
evaluation scripts are available at
\url{https://github.com/ananya-csai/aadhaar-pan-structure-aware}. The
images are not stored in the repository; they regenerate from the
seed, and released per-image SHA-256 digests show which rebuilt images,
if any, differ (Appendix~\ref{app:repro}). The five trained tile-model
checkpoints will be made publicly available at
\url{https://doi.org/10.5281/zenodo.23618373} upon publication.

\bmsection*{Ethics statement}

The study uses synthetic documents and invented identifiers only. No
real Aadhaar or PAN card, image or number was collected, processed or
submitted to any verification service, and no human participants were
involved.

\bibliography{references}

%======================================================================
\appendix
""" + appendix + r"""
\end{document}
"""
outdir = Path(sys.argv[3])
(outdir / "generated").mkdir(parents=True, exist_ok=True)
(outdir / "main.tex").write_text(out, encoding="utf-8")
for f in sorted(Path(sys.argv[2]).glob("*.tex")):
    t = f.read_text(encoding="utf-8").replace(r"width=\columnwidth, height=", r"width=0.75\textwidth, height=")
    (outdir / "generated" / f.name).write_text(t, encoding="utf-8")
print("written", outdir / "main.tex", len(out.splitlines()), "lines")
