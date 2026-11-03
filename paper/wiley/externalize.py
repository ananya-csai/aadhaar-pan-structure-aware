r"""Pre-render every TikZ/pgfplots figure of the Wiley paper to PDF, so that
Overleaf's free plan (10-second compile limit) only places images.

    python externalize.py <project dir>

Step 1 writes <dir>/main_ext.tex: main.tex with the two generated figure
files inlined, \tikzsetnextfilename{tikzfig/fig-NN} before every picture and
the TikZ external library switched on. Compile it once with -shell-escape.
Step 2 (--finalize) rewrites <dir>/main.tex: each picture is replaced by
\includegraphics of its PDF, the TikZ source is kept in figures/tikz_src/,
and TikZ/pgfplots are no longer loaded.
"""
import re
import sys
from pathlib import Path

d = Path(sys.argv[1])
src = (d / "main.tex").read_text(encoding="utf-8")
for name in ("res_roc_fig", "res_delta_fig"):
    src = src.replace(r"\input{generated/%s}" % name,
                      (d / "generated" / f"{name}.tex").read_text(encoding="utf-8").rstrip("\n"))

ENV = re.compile(r"\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}", re.S)
INL = re.compile(r"\\tikz\\draw\[[^\]]*\][^;]*;")
spans = sorted([(m.start(), m.end()) for m in ENV.finditer(src)] +
               [(m.start(), m.end()) for m in INL.finditer(src)])
print(len(spans), "pictures")


def rebuild(fn):
    out, last = [], 0
    for i, (a, b) in enumerate(spans):
        out.append(src[last:a]); out.append(fn(i, src[a:b])); last = b
    out.append(src[last:])
    return "".join(out)


if "--finalize" not in sys.argv:
    ext = rebuild(lambda i, t: r"\tikzsetnextfilename{fig-%02d}" % i + t)
    ext = ext.replace(r"\pgfplotsset{compat=1.17}", r"""\pgfplotsset{compat=1.17}
\usetikzlibrary{external}
\tikzexternalize[prefix=tikzfig/]
\tikzset{external/system call={xelatex \tikzexternalcheckshellescape -halt-on-error -interaction=batchmode -jobname "\image" "\texsource"}}""", 1)
    # the research-question box must not be externalized (tcolorbox "enhanced"
    # draws with TikZ); the final version uses the standard skin anyway
    ext = ext.replace(r"\newtcolorbox{rqbox}[1]{enhanced, ", r"\newtcolorbox{rqbox}[1]{")
    (d / "tikzfig").mkdir(exist_ok=True)
    (d / "main_ext.tex").write_text(ext, encoding="utf-8")
    print("wrote main_ext.tex")
else:
    srcdir = d / "figures" / "tikz_src"
    srcdir.mkdir(parents=True, exist_ok=True)

    def repl(i, t):
        (srcdir / f"fig-{i:02d}.tex").write_text(t + "\n", encoding="utf-8")
        assert (d / "tikzfig" / f"fig-{i:02d}.pdf").exists(), i
        return r"\includegraphics{tikzfig/fig-%02d.pdf}" % i

    fin = rebuild(repl)
    old_pkgs = r"""\usepackage{tikz}
\usetikzlibrary{shapes.geometric, arrows.meta, positioning, calc, fit,
                backgrounds, decorations.pathreplacing, patterns}
\usepackage{pgfplots}
\pgfplotsset{compat=1.17}
\usepackage[most]{tcolorbox}"""
    assert fin.count(old_pkgs) == 1
    fin = fin.replace(old_pkgs, r"""% Figures are pre-rendered PDFs in tikzfig/ (sources in figures/tikz_src/),
% which keeps the compile within Overleaf's free-plan time limit.
\usepackage{tcolorbox}""")
    assert fin.count(r"\newtcolorbox{rqbox}[1]{enhanced, ") == 1
    fin = fin.replace(r"\newtcolorbox{rqbox}[1]{enhanced, ", r"\newtcolorbox{rqbox}[1]{")
    assert "tikzpicture" not in fin and r"\tikz\draw" not in fin
    (d / "main.tex").write_text(fin, encoding="utf-8")
    print("main.tex finalized")
