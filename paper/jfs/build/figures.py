r"""Render every figure as a separate file for upload (JFS: TIFF/PNG/EPS,
>= 300 dpi; figures must not be embedded in the manuscript file).

    python -I figures.py <project dir> <source project dir>

For FigureN (numbered in order of first citation, see figure_map.txt) the
figure body is typeset exactly as in the paper (same graphics, same
sub-panel labels, 16.5 cm wide), then written as
  figure_files/FigureN.tif   600 dpi, RGB, LZW-compressed (upload these)
  figure_pdf/FigureN.pdf     vector copy, used only by the reading copy
"""
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image
from pypdf import PdfReader, PdfWriter
from pypdf.generic import RectangleObject

d, src = Path(sys.argv[1]), Path(sys.argv[2])
for sub in ("tikzfig", "figures"):
    if (d / sub).exists():
        shutil.rmtree(d / sub)
    shutil.copytree(src / sub, d / sub, ignore=shutil.ignore_patterns("tikz_src"))
bodies = sorted((d / "fig_src").glob("fig*.tex"))

# Drawn figures that print a section or table number are re-drawn from
# their TikZ source with the numbers of this manuscript (from manuscript.aux).
import re
labels = dict(re.findall(r"\\newlabel\{([^}]*)\}\{\{([^}]*)\}", (d / "manuscript.aux").read_text(encoding="utf-8")))
need_tikz = False
for b in bodies:
    t = b.read_text(encoding="utf-8")
    for k in re.findall(r"\\includegraphics\{tikzfig/fig-(\d\d)\.pdf\}", t):
        tik = (src / "figures" / "tikz_src" / f"fig-{k}.tex").read_text(encoding="utf-8")
        if "\\ref{" not in tik:
            continue
        tik = re.sub(r"\\ref\{([^}]*)\}", lambda m: labels[m.group(1)], tik)
        t = t.replace("\\includegraphics{tikzfig/fig-%s.pdf}" % k, tik.strip())
        need_tikz = True
        print(f"{b.stem}: fig-{k} redrawn with current cross-reference numbers")
    b.write_text(t, encoding="utf-8")
doc = r"""\documentclass[10pt]{article}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{mathptmx}
\usepackage[paperwidth=18cm,paperheight=40cm,margin=0.75cm]{geometry}
\usepackage{graphicx,amsmath,amssymb,pifont}
\usepackage{xcolor}
\usepackage{tikz}
\usetikzlibrary{shapes.geometric, arrows.meta, positioning, calc, fit,
                backgrounds, decorations.pathreplacing, patterns}
\usepackage{pgfplots}
\pgfplotsset{compat=1.17}
\definecolor{cvis}{HTML}{2F6DB5}
\definecolor{crule}{HTML}{D27A1E}
\definecolor{cfuse}{HTML}{2E8B57}
\definecolor{cbad}{HTML}{C0392B}
\definecolor{cink}{HTML}{2B2B2B}
\definecolor{cgrey}{HTML}{6B7280}
\pagestyle{empty}
\makeatletter
\renewcommand\small{\@setfontsize\small{9}{11}}
\renewcommand\footnotesize{\@setfontsize\footnotesize{8}{9.5}}
\renewcommand\scriptsize{\@setfontsize\scriptsize{7}{8}}
\makeatother
\begin{document}
""" + "".join("\\clearpage\\noindent\\begin{minipage}{\\textwidth}\\centering\n\\input{fig_src/%s}\n\\end{minipage}\n" % b.stem for b in bodies) + "\\end{document}\n"
(d / "figure_build.tex").write_text(doc, encoding="utf-8")
subprocess.run(["pdflatex", "-interaction=nonstopmode", "figure_build.tex"], cwd=d, stdout=subprocess.DEVNULL, check=False)
pdf = d / "figure_build.pdf"
n_pages = len(PdfReader(pdf).pages)
assert n_pages == len(bodies), (n_pages, len(bodies))
(d / "figure_files").mkdir(exist_ok=True)
(d / "figure_pdf").mkdir(exist_ok=True)
DPI = 600
for i in range(1, n_pages + 1):
    subprocess.run(["pdftoppm", "-r", str(DPI), "-f", str(i), "-l", str(i), "-png", "-singlefile", str(pdf), str(d / "tmp_fig")], check=True)
    im = Image.open(d / "tmp_fig.png").convert("RGB")
    g = im.convert("L").point(lambda v: 255 if v < 250 else 0)
    x0, y0, x1, y1 = g.getbbox()
    m = int(0.08 * DPI / 2.54)  # 0.8 mm margin
    x0, y0, x1, y1 = max(x0 - m, 0), max(y0 - m, 0), min(x1 + m, im.width), min(y1 + m, im.height)
    im.crop((x0, y0, x1, y1)).save(d / "figure_files" / f"Figure{i}.tif", compression="tiff_lzw", dpi=(DPI, DPI))
    r = PdfReader(pdf)
    w = PdfWriter()
    page = r.pages[i - 1]
    H = float(page.mediabox.height)
    k = 72 / DPI
    box = RectangleObject([x0 * k, H - y1 * k, x1 * k, H - y0 * k])
    page.mediabox = box
    page.cropbox = box
    w.add_page(page)
    with open(d / "figure_pdf" / f"Figure{i}.pdf", "wb") as fh:
        w.write(fh)
    print(f"Figure{i}: {(x1-x0)/DPI*2.54:.1f} x {(y1-y0)/DPI*2.54:.1f} cm")
(d / "tmp_fig.png").unlink()
pages = "".join("\\clearpage\n\\noindent\\textbf{FIGURE %d}\\par\\medskip\n\\begin{center}\\includegraphics[width=\\linewidth,height=0.85\\textheight,keepaspectratio]{figure_pdf/Figure%d.pdf}\\end{center}\n" % (i, i) for i in range(1, n_pages + 1))
(d / "figure_pages.tex").write_text(pages, encoding="utf-8")
