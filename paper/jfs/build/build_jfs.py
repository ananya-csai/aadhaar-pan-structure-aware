r"""Build the Journal of Forensic Sciences (JFS) submission from the authors'
Wiley/IET LaTeX project, without changing the wording beyond a short,
logged list of edits.

    python -I build_jfs.py <source project dir> <output project dir>

Writes into <out>: manuscript.tex (anonymised, double-spaced, JFS order:
title / abstract + keywords / highlights / text / references / tables /
figure legends), supplementary.tex (Appendix S1), fig_src/figNN.tex
(stand-alone bodies of every figure, numbered in order of first citation)
and build_log.txt (every edit made to the text).

The reference list is written in a second step (refs.py), once the order
of first citation is known from manuscript.aux.
"""
import re
import sys
from pathlib import Path

SRC, OUT = Path(sys.argv[1]), Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)
log = []

s = (SRC / "main.tex").read_text(encoding="utf-8")
for name in re.findall(r"\\input\{(generated/res_\w+)\}", s):
    s = s.replace("\\input{%s}" % name, (SRC / (name + ".tex")).read_text(encoding="utf-8").rstrip("\n"))


def one(text, old, new, why, count=1):
    n = text.count(old)
    if n != count:
        sys.exit(f"[{why}] expected {count} match(es), found {n}: {old[:90]!r}")
    log.append(why)
    return text.replace(old, new)


def braced(text, start):
    """Return (content, end) of the {...} group whose '{' is at text[start]."""
    assert text[start] == "{", text[start:start + 20]
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "{" and text[i - 1] != "\\":
            depth += 1
        elif text[i] == "}" and text[i - 1] != "\\":
            depth -= 1
            if depth == 0:
                return text[start + 1:i], i + 1
    raise ValueError("unbalanced")


# ------------------------------------------------------------------ pieces
title = braced(s, s.index(r"\title{") + 6)[0]
abstract = braced(s, s.index(r"\abstract[Abstract]{") + 19)[0].strip()
kw_old = braced(s, s.index(r"\keywords{") + 9)[0]

doc = s[s.index(r"\begin{document}"):]
intro_at = doc.index(r"\section{Introduction}")
fig0 = re.search(r"\\begin\{figure\*?\}.*?\\end\{figure\*?\}", doc[:intro_at], re.S).group(0)
body = doc[intro_at:doc.index(r"\bmsection*{Author contributions}")]
back = doc[doc.index(r"\bmsection*{Author contributions}"):doc.index(r"\bibliography{references}")]
appendix = doc[doc.index(r"\appendix"):doc.index(r"\end{document}")]
ai_decl = re.search(r"\\bmsection\*\{Declaration of generative AI[^}]*\}\s*(.*?)\s*\\bmsection", back, re.S).group(1)
body = fig0 + "\n" + body

# ------------------------------------------------------------------ abstract (<= 250 words)
# Only deletions and contractions; no sentence is rewritten.
ABS = [
    ("To do so under control, we build", "We build", "dropped 'To do so under control,'"),
    ("identities, two document formats, five forgery\ncategories", "identities, five forgery\ncategories",
     "dropped 'two document formats' (stated earlier in the abstract)"),
    ("tiers) in which every image carries\nfield-level ground truth", "tiers) with\nfield-level ground truth",
     "'in which every image carries' -> 'with'"),
    ("a tile-based ResNet-50, a\ndeterministic rule validator", "a tile-based ResNet-50, a\nrule validator", "dropped 'deterministic'"),
    ("under a protocol that was\nfixed before", "under a protocol\nfixed before", "'protocol that was fixed' -> 'protocol fixed'"),
    ("fusion\nraises detection recall from", "fusion\nraises recall from", "'detection recall' -> 'recall'"),
    ("mainly because character misreads make PAN rule failures unreliable:\nwith OCR text the rules alone flag",
     "mainly because misreads make the rules alone flag",
     "'character misreads make PAN rule failures unreliable: with OCR text the rules alone flag' -> 'misreads make the rules alone flag'"),
    ("Feeding each rule to the fusion as a separate input recovers", "Feeding each rule to the fusion separately recovers",
     "'as a separate input' -> 'separately'"),
    ("and a fresh, pre-registered set of 90 unseen", "and a pre-registered set of 90 unseen", "dropped 'fresh,'"),
    ("$[11.2, 14.1]$, with no measurable increase in false positives)", "$[11.2, 14.1]$; no measurable increase in false positives)",
     "', with no' -> '; no'"),
    (" that we reviewed\ntreats", "\ntreats", "dropped 'that we reviewed' (the scope is stated in Section 1.1.5)"),
    ("yet it may still break\nrules", "yet it may break\nrules", "dropped 'still'"),
    ("such as the Verhoeff\ncheck digit of an Aadhaar number or the taxpayer-category and\nname-initial positions of a PAN.",
     "such as the Verhoeff\ncheck digit of an Aadhaar number.", "dropped the PAN example (PAN rules are described in the text)"),
    ("We measure how much these format rules\nadd", "We measure how much these rules\nadd", "dropped 'format' (repeated)"),
    ("genuine card, which suggests that a passed checksum", "genuine card, so a passed checksum", "'which suggests that' -> 'so'"),
]
for old, new_, why in ABS:
    abstract = one(abstract, old, new_, "abstract (250-word limit): " + why)

# ------------------------------------------------------------------ figures and tables out of the text
floats = []  # (kind, labels, env text)


def pull(m):
    env = m.group(0)
    kind = "table" if m.group(1).startswith("table") else "figure"
    floats.append((kind, re.findall(r"\\label\{([^}]*)\}", env), env))
    return "%%FLOAT:%d%%" % (len(floats) - 1)


body = re.sub(r"\\begin\{(table\*?|figure\*?)\}.*?\\end\{\1\}", pull, body, flags=re.S)
body = re.sub(r"\n?%%FLOAT:\d+%%\n?", "\n", body)
log.append(f"moved {sum(k=='table' for k,_,_ in floats)} tables after the references and "
           f"{sum(k=='figure' for k,_,_ in floats)} figures to separate files (legends at the end)")

# ------------------------------------------------------------------ IMRaD headings
parts = re.split(r"(?=\\section\{)", body)
head = parts[0]
out = [head]
demote = {"Search Protocol": "Search Protocol",
          "Problem Setting and Validation Rules": "Problem Setting and Validation Rules",
          "Benchmark Construction": "Benchmark Construction",
          "Methodology": "Detection Methods",
          "Experimental Setup": "Experimental Setup"}
for p in parts[1:]:
    name = re.match(r"\\section\{([^}]*)\}", p).group(1)
    if name in demote:
        if name == "Problem Setting and Validation Rules":
            out.append("%" + "=" * 70 + "\n\\section{Materials and Methods}\n\\label{sec:methods}\n\n")
        p = p.replace("\\subsection{", "\\subsubsection{")
        p = p.replace("\\section{%s}" % name, "\\subsection{%s}" % demote[name], 1)
    elif name == "Conclusion and Future Work":
        p = p.replace("\\section{Conclusion and Future Work}", "\\section{Conclusions}", 1)
    out.append(p)
body = "".join(out)
log.append("headings: Search Protocol is now subsection 1.1 of the Introduction; Problem Setting, "
           "Benchmark Construction, Methodology (renamed Detection Methods) and Experimental Setup "
           "are subsections of a new MATERIALS AND METHODS section; 'Conclusion and Future Work' -> 'Conclusions'")

# ------------------------------------------------------------------ text edits (logged)
body = one(body, r"""The rest of the paper is organised as follows. Section~\ref{sec:related}
reviews related work and the literature search protocol. Section~\ref{sec:framework} specifies the
validation rules, Section~\ref{sec:dataset} the benchmark,
Section~\ref{sec:method} the detection pipeline and
Section~\ref{sec:setup} the experimental protocol. Results, discussion
and conclusions follow in Sections~\ref{sec:results}--\ref{sec:conclusion}.""",
           r"""The rest of the paper is organised as follows. Section~\ref{sec:related}
reviews related work and the literature search protocol. Section~\ref{sec:methods} specifies the
validation rules (Section~\ref{sec:framework}), the benchmark (Section~\ref{sec:dataset}),
the detection pipeline (Section~\ref{sec:method}) and
the experimental protocol (Section~\ref{sec:setup}). Results, discussion
and conclusions follow in Sections~\ref{sec:results}--\ref{sec:conclusion}.""",
           "roadmap paragraph updated to the new section structure")
body = one(body, "\\end{rqbox}\n",
           "\\end{rqbox}\n\nThe working hypothesis is that format-level rules add detection mainly on\n"
           "forgeries that leave no pixel-level trace (RQ2, RQ3), and that part of\n"
           "this gain is lost when the rules read OCR output instead of ground-truth\n"
           "text (RQ4).\n",
           "NEW SENTENCE: stated hypothesis after the research questions (JFS review criterion)")
body = one(body, "opened, every frozen parameter file was committed, all three authors\nsigned",
           "opened, every frozen parameter file was committed, all authors\nsigned",
           "anonymity: 'all three authors' -> 'all authors'")
body = one(body, "with OCR text by a smaller but significant margin",
           "with OCR text by a smaller but statistically significant margin",
           "JFS statistics wording: 'significant' -> 'statistically significant'")
body = one(body, r"Appendix~\ref{app:repro}", r"Appendix~S1 (Supplemental Information)",
           "appendix moved to the Supplemental Information (Appendix S1)", count=2)
body = one(body, "category C4 shows that structural validity does not\nestablish authenticity.",
           "category C4 shows that structural validity does not\nestablish authenticity. "
           "No human participants were involved; ethics approval was\ntherefore not required.",
           "ethics sentence from the former Ethics statement added to Section 2.2.8")
body = one(body, "\\subsection{Relation to Prior Work}",
           r"""\paragraph*{Implications for forensic document examination.} For examiners
of questioned identity documents, the results suggest three practical
points. First, a passed checksum or format check shows only the absence
of one kind of inconsistency and should not be reported as support for
authenticity (C4). Second, a rule failure on a field read by OCR should
be checked against the image before it is treated as evidence: in this
study, every rule failure on a genuine card came from an OCR misread.
Third, visual examination and field-consistency checks address
different forgery types, so neither can replace the other.

\subsection{Relation to Prior Work}""",
           "NEW PARAGRAPH: implications for forensic document examination (Discussion 4.1)")

# methods: generative-AI disclosure (JFS/Wiley: Methods or Acknowledgments)
body = one(body, "%" + "=" * 70 + "\n\\section{Results}",
           "\\subsection{Use of Generative AI}\n\\label{subsec:ai}\n\n" + ai_decl.strip() +
           "\n\n%" + "=" * 70 + "\n\\section{Results}",
           "generative-AI declaration moved unchanged into Methods (Section 2.5), as the JFS AI statement asks")

# data availability (anonymised) after the conclusions
data_avail = r"""\section*{Data Availability Statement}

The data generator, configuration files, manifests, frozen model
scores, calibration and fusion parameters, the protocol file and all
evaluation scripts are available in a public code repository. To keep
the review double-blind, its address is given on the title page and not
in this file. The images are not stored in the repository; they
regenerate from the seed, and released per-image SHA-256 digests show
which rebuilt images, if any, differ (Appendix~S1, Supplemental
Information). The five trained tile-model checkpoints will be made
publicly available in a DOI-registered archive upon publication.
"""
log.append("data availability statement anonymised (repository and Zenodo links moved to the title page)")

# citations: superscript style -> bracketed numbers, with a space before
n_before = len(re.findall(r"\\cite\{", body))
body = re.sub(r"(?<=[^\s~(\[{])\\cite\{", r"~\\cite{", body)
log.append(f"{n_before} citations now print as [n] after a non-breaking space")

# ------------------------------------------------------------------ table styling (JFS: no internal rules, no shading)
def cite_space(t):
    return re.sub(r"(?<=[^\s~(\[{])\\cite\{", r"~\\cite{", t)


def jfs_table(env, label):
    env = cite_space(env)
    env = re.sub(r"\\begin\{table\*?\}(\[[^\]]*\])?", r"\\begin{table}[H]", env)
    env = env.replace("\\end{table*}", "\\end{table}")
    # internal horizontal rules -> space (keep top rule, header rule, bottom rule)
    def fix_tab(m):
        t = m.group(0)
        first = t.find("\\midrule")
        if first < 0:
            return t
        head, rest = t[:first + 8], t[first + 8:]
        rest = rest.replace("\\midrule", "\\addlinespace[4pt]")
        return "\\begin{adjustbox}{max width=\\linewidth}\n" + head + rest + "\n\\end{adjustbox}"
    env = re.sub(r"\\begin\{tabular\}.*?\\end\{tabular\}", fix_tab, env, flags=re.S)
    # footnote symbols in JFS order: * then dagger ...
    if label == "tab:capture":
        env = env.replace("$^{a}$", "$^{*}$").replace("$^{b}$", "$^{\\dagger}$")
    if label == "tab:weights":
        env = env.replace("$^{\\dagger}$", "$^{*}$")
    env = env.replace("\\resizebox{\\textwidth}{!}", "\\resizebox{\\linewidth}{!}")
    return env


# ------------------------------------------------------------------ order of first citation
def first_mention(labels, text):
    pos = [m.start() for l in labels for m in re.finditer(r"\\ref\{%s\}" % re.escape(l), text)]
    return min(pos) if pos else None


order = {}
for i, (kind, labels, env) in enumerate(floats):
    p = first_mention(labels, body)
    if p is None:
        sys.exit(f"float {labels} is never cited in the text")
    order[i] = p
tables = sorted([i for i in order if floats[i][0] == "table"], key=order.get)
figures = sorted([i for i in order if floats[i][0] == "figure"], key=order.get)

# references cited only inside a table or legend take the number of the
# point where that table or figure is first cited (JFS rule)
for i in tables + figures:
    kind, labels, env = floats[i]
    keys = [k.strip() for c in re.findall(r"\\cite\{([^}]*)\}", env) for k in c.split(",")]
    if not keys:
        continue
    m = None
    for l in labels:
        mm = re.search(r"\\ref\{%s\}\}?" % re.escape(l), body)
        if mm and (m is None or mm.start() < m.start()):
            m = mm
    body = body[:m.end()] + "\\nocite{%s}" % ",".join(dict.fromkeys(keys)) + body[m.end():]

# ------------------------------------------------------------------ tables section
tab_tex = []
for i in tables:
    kind, labels, env = floats[i]
    tab_tex.append("\\clearpage\n" + jfs_table(env, labels[0]))
log.append("tables restyled for JFS: internal rules removed, footnote symbols *, dagger; numbered in order of first citation")

# ------------------------------------------------------------------ figures: legends + stand-alone bodies
legends, fig_files = [], []
(OUT / "fig_src").mkdir(exist_ok=True)
for n, i in enumerate(figures, 1):
    kind, labels, env = floats[i]
    cap_at = env.index("\\caption{")
    cap, cap_end = braced(env, cap_at + 8)
    inner = re.sub(r"^\\begin\{figure\*?\}(\[[^\]]*\])?", "", env)
    inner = re.sub(r"\\end\{figure\*?\}$", "", inner)
    fig_body = inner.replace("\\caption{" + cap + "}", "")
    for l in labels:
        fig_body = fig_body.replace("\\label{%s}" % l, "")
    (OUT / "fig_src" / f"fig{n:02d}.tex").write_text(fig_body.strip() + "\n", encoding="utf-8")
    lab = "".join("\\label{%s}" % l for l in labels)
    legends.append("{\\captionsetup{type=figure}\\caption{%s}%s}\\par\\medskip" % (cite_space(cap.strip()), lab))
    fig_files.append((n, labels))
(OUT / "figure_map.txt").write_text("".join(f"Figure{n}\t{', '.join(l)}\n" for n, l in fig_files))

# ------------------------------------------------------------------ highlights and keywords
highlights = [
    "A valid Aadhaar check digit is not evidence that an identity card is genuine.",
    "Format and cross-field rules expose forged cards that leave no pixel-level trace.",
    "On genuine cards, every rule failure came from an OCR misread, not from a forger.",
    "Weighting each rule check separately recovers about half of the loss caused by OCR.",
    "A synthetic benchmark lets forgery detection be tested without real identity data.",
]
for h in highlights:
    assert len(h) <= 100, (len(h), h)
keywords = ("questioned documents, identity document forgery, Aadhaar, "
            "Permanent Account Number (PAN), document image forensics, "
            "optical character recognition (OCR), checksum validation, evidence fusion")
log.append("NEW: 5 highlights (each <= 100 characters)")
log.append(f"keywords: added 'questioned documents' (forensic specialty) and the abbreviations PAN, OCR; was: {' '.join(kw_old.split())}")

# ------------------------------------------------------------------ manuscript
preamble = (Path(__file__).parent / "preamble.tex").read_text(encoding="utf-8")
manuscript = rf"""% Journal of Forensic Sciences -- anonymised manuscript file (no author
% information; the title page is a separate file, titlepage.tex).
% Overleaf: Compiler pdfLaTeX (any TeX Live version). No BibTeX run is
% needed: the reference list below is already in JFS (Vancouver/NLM) style.
\documentclass[12pt]{{article}}
{preamble}
\begin{{document}}

% ---------------------------------------------------------------- page 1: title
\begin{{center}}
{{\large\bfseries {title}\par}}
\bigskip
Original Paper
\end{{center}}

\clearpage
% ---------------------------------------------------------------- page 2: abstract and keywords
\noindent\textbf{{Abstract}}\par
\noindent {abstract}

\bigskip
\noindent\textbf{{KEYWORDS}}\par
\noindent {keywords}

\clearpage
% ---------------------------------------------------------------- page 3: highlights
\noindent\textbf{{Highlights}}
\begin{{itemize}}
{chr(10).join("  \\item " + h for h in highlights)}
\end{{itemize}}

\clearpage
\linenumbers
% ---------------------------------------------------------------- text
{body.strip()}

{data_avail}
% ---------------------------------------------------------------- references
%%REFERENCES%%

\nolinenumbers
% ---------------------------------------------------------------- tables (after the references)
{chr(10).join(tab_tex)}

% ---------------------------------------------------------------- figure legends (last page)
\clearpage
\noindent\textbf{{Figure Legends}}\par\medskip
{chr(10).join(legends)}

\ifdefined\withfigures
% ---------------------------------------------------------------- reading copy only: figure pages
\input{{figure_pages}}
\fi
\end{{document}}
"""
(OUT / "manuscript.tex").write_text(manuscript, encoding="utf-8")

# ------------------------------------------------------------------ supplement (Appendix S1)
app = appendix.replace("\\appendix", "")
app = one(app, "approved by all three authors; freeze tag created at commit \\texttt{1294c23}.",
          "approved by all authors; freeze tag created (commit identifier withheld for double-blind review).",
          "supplement anonymity: commit hash and author count removed")
app = one(app, "Agreed by S.P.\\ on 21 Oct, confirmed by A.S.\\ and D.S.\\ on 23 Oct.",
          "Agreed by one author on 21 Oct and confirmed by the other authors on 23 Oct.",
          "supplement anonymity: author initials removed")
app = app.replace("\\bmsection{Reproducibility record}", "\\section*{Appendix S1. Reproducibility Record}")
app = app.replace("\\bmsubsection{", "\\subsection*{")
app = re.sub(r"\\begin\{table\*?\}(\[[^\]]*\])?", r"\\begin{table}[H]", app).replace("\\end{table*}", "\\end{table}")
(OUT / "supplement_body.tex").write_text(app, encoding="utf-8")

(OUT / "build_log.txt").write_text("\n".join("- " + x for x in log) + "\n", encoding="utf-8")
print("\n".join("- " + x for x in log))
print("figures:", [f"Figure{n}={l}" for n, l in fig_files])
print("tables:", [floats[i][1][0] for i in tables])
