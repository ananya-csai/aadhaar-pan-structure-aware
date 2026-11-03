r"""Re-render the 12 pre-rendered figures with the document's current preamble.

    python rerender.py <project dir>

Writes <dir>/main_ext.tex: main.tex with each \includegraphics{tikzfig/fig-NN.pdf}
replaced by its TikZ source from figures/tikz_src/ (named with
\tikzsetnextfilename) and the TikZ external library enabled. Compiling it once
with -shell-escape rewrites tikzfig/fig-NN.pdf; main.tex itself is unchanged.
"""
import re
import sys
from pathlib import Path

d = Path(sys.argv[1])
s = (d / "main.tex").read_text(encoding="utf-8")


def sub(m):
    k = m.group(1)
    src = (d / "figures" / "tikz_src" / f"fig-{k}.tex").read_text(encoding="utf-8").rstrip("\n")
    return r"\tikzsetnextfilename{fig-%s}" % k + src


s, n = re.subn(r"\\includegraphics\{tikzfig/fig-(\d\d)\.pdf\}", sub, s)
assert n == 12, n
pkgs = r"""\usepackage{tikz}
\usetikzlibrary{shapes.geometric, arrows.meta, positioning, calc, fit,
                backgrounds, decorations.pathreplacing, patterns, external}
\usepackage{pgfplots}
\pgfplotsset{compat=1.17}
\tikzexternalize[prefix=tikzfig/]
\tikzset{external/system call={xelatex \tikzexternalcheckshellescape -halt-on-error -interaction=batchmode -jobname "\image" "\texsource"}}
"""
s = s.replace(r"\usepackage{tcolorbox}", pkgs + r"\usepackage{tcolorbox}", 1)
(d / "main_ext.tex").write_text(s, encoding="utf-8")
print("wrote main_ext.tex with", n, "figures")
