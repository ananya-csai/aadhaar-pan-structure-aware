r"""Write supplementary.tex (JFS Supplemental Information: Appendix S1).

    python -I supp.py <project dir>

Cross-references to the main text are written as numbers taken from
manuscript.aux (the two files are uploaded separately). Tables are numbered
S1, S2, ... in order of first citation, and styled like the manuscript
tables (no internal rules).
"""
import re
import sys
from pathlib import Path

d = Path(sys.argv[1])
app = (d / "supplement_body.tex").read_text(encoding="utf-8")
labels = dict(re.findall(r"\\newlabel\{([^}]*)\}\{\{([^}]*)\}", (d / "manuscript.aux").read_text(encoding="utf-8")))
title = re.search(r"\{\\large\\bfseries (.*?)\\par\}", (d / "manuscript.tex").read_text(encoding="utf-8"), re.S).group(1)


def one(t, old, new, count=1):
    n = t.count(old)
    assert n == count, (n, old[:80])
    return t.replace(old, new)


# main-text references -> fixed numbers, marked as main text
app = one(app, r"(Fig.~\ref{fig:survival})", "(Fig.~%s in the main text)" % labels["fig:survival"])
app = one(app, r"Section~\ref{sec:results}", "Section~%s of the main text" % labels["sec:results"], count=2)
app = one(app, r"Table~\ref{tab:tests}", "Table~%s of the main text" % labels["tab:tests"])
app = app.replace(r"Appendix~\ref{app:levels}", "Appendix~S1")
app = app.replace("\\label{app:repro}", "").replace("\\label{app:levels}", "")

# number tables by first citation: move the protocol record table to its section
prot = re.search(r"\\begin\{table\}\[H\]\s*\\caption\{Protocol record.*?\\end\{table\}\n", app, re.S).group(0)
app = app.replace(prot, "")
prot = prot.replace("\\scriptsize", "\\fontsize{8.5}{10}\\selectfont", 1)  # fits one page
app = one(app, "is confirmatory.\n", "is confirmatory.\n\n" + prot)


def style(t):
    def fix(m):
        s = m.group(0)
        i = s.find("\\midrule")
        return "\\begin{adjustbox}{max width=\\linewidth}\n" + s[:i + 8] + s[i + 8:].replace("\\midrule", "\\addlinespace[4pt]") + "\n\\end{adjustbox}"
    return re.sub(r"\\begin\{tabular\}.*?\\end\{tabular\}", fix, t, flags=re.S)


app = style(app)
preamble = (Path(__file__).parent / "preamble.tex").read_text(encoding="utf-8")
doc = rf"""% Journal of Forensic Sciences -- Supplemental Information (upload as a
% separate file, designated "Supplemental Information"). Anonymised.
% Overleaf: set this file as the main document to compile it.
\documentclass[12pt]{{article}}
{preamble}
\renewcommand{{\thetable}}{{S\arabic{{table}}}}
\onehalfspacing
\begin{{document}}
\begin{{center}}
{{\large\bfseries Supplemental Information\par}}
\medskip
{title}
\end{{center}}
\bigskip
{app.strip()}
\end{{document}}
"""
(d / "supplementary.tex").write_text(doc, encoding="utf-8")
print("supplementary.tex written; main-text numbers used:",
      {k: labels[k] for k in ("fig:survival", "sec:results", "tab:tests")})
