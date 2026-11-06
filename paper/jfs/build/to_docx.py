r"""Convert the compiled JFS manuscript (manuscript.tex + manuscript.aux) to
an MS Word file, as the JFS submission portal requires a Word main document.

    python -I to_docx.py <project dir> <out.docx>

The LaTeX is first simplified into what pandoc reads reliably: every
cross-reference, citation and equation number is replaced by the number
LaTeX assigned (read from manuscript.aux), so the Word file carries exactly
the numbers of the PDF; dataset macros are expanded; the algorithm, the
research-question box, table and figure legends and the reference list are
written out as plain paragraphs. pandoc then writes the .docx (equations
become editable Word equations, tables become Word tables) and python-docx
applies the JFS layout: Times New Roman 12 pt, double spacing, continuous
line numbers, page numbers, headings in the JFS styles, page breaks.
"""
import re
import subprocess
import sys
from pathlib import Path

from docx import Document
from docx.enum.text import WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor

d = Path(sys.argv[1])
OUT = Path(sys.argv[2])
tex = (d / "manuscript.tex").read_text(encoding="utf-8")
aux = (d / "manuscript.aux").read_text(encoding="utf-8")
labels = dict(re.findall(r"\\newlabel\{([^}]*)\}\{\{([^}]*)\}", aux))
bibnum = {k: int(v) for k, v in re.findall(r"\\bibcite\{([^}]*)\}\{\{?(\d+)", aux)}
PB = "PAGEBREAKMARKER"


def braced(text, start):
    assert text[start] == "{", text[start:start + 30]
    depth = 0
    for i in range(start, len(text)):
        c = text[i]
        if c == "{" and text[i - 1] != "\\":
            depth += 1
        elif c == "}" and text[i - 1] != "\\":
            depth -= 1
            if depth == 0:
                return text[start + 1:i], i + 1
    raise ValueError("unbalanced")


def sub_cmd(text, cmd, fn):
    """Replace \\cmd{arg} (balanced) by fn(arg)."""
    out, i = [], 0
    pat = "\\" + cmd + "{"
    while True:
        j = text.find(pat, i)
        if j < 0:
            out.append(text[i:])
            return "".join(out)
        arg, end = braced(text, j + len(pat) - 1)
        out.append(text[i:j])
        out.append(fn(arg))
        i = end


body = tex[tex.index("\\begin{document}") + len("\\begin{document}"):tex.index("\\ifdefined\\withfigures")]

# ---------------------------------------------------------------- dataset macros
nums = (d / "generated" / "numbers.tex").read_text(encoding="utf-8")
macros = dict(re.findall(r"\\newcommand\{\\(\w+)\}\{(.*?)\}\s*(?:%.*)?$", nums, re.M))
for name in sorted(macros, key=len, reverse=True):
    val = macros[name]
    body = re.sub(r"\\%s(\{\})?(?![A-Za-z])" % name, lambda m: val, body)

# numbers written as maths ($+12.6$, $[11.2, 14.1]$) become plain text, so the
# abstract can be pasted into the submission form unchanged
body = re.sub(r"\$([-+]?[\d.,\[\]\s]+)\$", lambda m: m.group(1).replace("-", "\u2212"), body)

# ---------------------------------------------------------------- numbers from LaTeX
def cites(arg):
    ns = sorted({bibnum[k.strip()] for k in arg.split(",")})
    parts, run = [], [ns[0]]
    for n in ns[1:]:
        if n == run[-1] + 1:
            run.append(n)
        else:
            parts.append(run); run = [n]
    parts.append(run)
    txt = ", ".join(f"{r[0]}--{r[-1]}" if len(r) > 2 else ", ".join(map(str, r)) for r in parts)
    return "[" + txt + "]"


body = re.sub(r"\\nocite\{[^}]*\}", "", body)
body = sub_cmd(body, "cite", cites)
body = sub_cmd(body, "eqref", lambda a: "(" + labels[a] + ")")
body = sub_cmd(body, "ref", lambda a: labels[a])

# equations: number written into the display
def equation(m):
    inner = m.group(1)
    lab = re.search(r"\\label\{([^}]*)\}", inner)
    inner = re.sub(r"\\label\{[^}]*\}", "", inner).strip()
    inner = sub_cmd(inner, "textsc", lambda a: "\\text{" + a.upper() + "}")
    num = labels[lab.group(1)] if lab else None
    return "\n\\[" + inner + (r"\qquad(" + num + ")" if num else "") + "\\]\n"


body = re.sub(r"\\begin\{equation\}(.*?)\\end\{equation\}", equation, body, flags=re.S)

# ---------------------------------------------------------------- algorithm -> numbered lines
def algorithm(m):
    env = m.group(0)
    cap = braced(env, env.index("\\caption{") + 8)[0]
    lab = re.search(r"\\label\{([^}]*)\}", env).group(1)
    alg = env[env.index("\\begin{algorithmic}"):env.index("\\end{algorithmic}")]
    alg = re.sub(r"\\begin\{algorithmic\}(\[\d\])?", "", alg)
    alg = alg.replace("\\gets", "\\leftarrow")
    alg = sub_cmd(alg, "textsc", lambda a: "\\mathrm{" + a.upper() + "}")
    alg = sub_cmd(alg, "Comment", lambda a: " \u25B7 " + a)
    lines, depth, out, n = [], 0, [], 0
    for raw in re.split(r"(?=\\(?:Require|Ensure|State|For|EndFor|If|EndIf)\b)", alg):
        raw = " ".join(raw.split())
        if not raw:
            continue
        if raw.startswith("\\Require"):
            out.append("\\textbf{Input:} " + raw[8:].strip())
        elif raw.startswith("\\Ensure"):
            out.append("\\textbf{Output:} " + raw[7:].strip())
        elif raw.startswith("\\EndFor") or raw.startswith("\\EndIf"):
            depth -= 1
        elif raw.startswith("\\For"):
            arg, end = braced(raw, 4)
            n += 1; out.append(f"{n}: " + "\u2003" * depth + "\\textbf{for} " + arg + " \\textbf{do}" + raw[end:]); depth += 1
        elif raw.startswith("\\If"):
            arg, end = braced(raw, 3)
            n += 1; out.append(f"{n}: " + "\u2003" * depth + "\\textbf{if} " + arg + " \\textbf{then}" + raw[end:]); depth += 1
        elif raw.startswith("\\State"):
            line = raw[6:].strip().replace("\\Return", "\\textbf{return}")
            n += 1; out.append(f"{n}: " + "\u2003" * depth + line)
    head = "\\textbf{Algorithm %s} %s" % (labels[lab], cap)
    return "\n\n" + head + "\n\n" + "\n\n".join(out) + "\n\n"


body = re.sub(r"\\begin\{algorithm\}.*?\\end\{algorithm\}", algorithm, body, flags=re.S)

# ---------------------------------------------------------------- research-question box
def rqbox(m):
    title, inner = m.group(1), m.group(2)
    inner = inner.replace("\\par\\smallskip", "\n\n")
    return "\n\n\\textbf{" + title + "}\n\n" + inner + "\n\n"


body = re.sub(r"\\begin\{rqbox\}\{([^}]*)\}(.*?)\\end\{rqbox\}", rqbox, body, flags=re.S)

# run-in paragraph headings -> italic lead-in
body = re.sub(r"\\paragraph\*\{(.*?)\}\s*", r"\\emph{\1} ", body)

# ---------------------------------------------------------------- tables
def ncols(spec):
    spec = re.sub(r"[@<>!]\{[^}]*\}", "", spec)
    spec = re.sub(r"(p|m|b)\{[^}]*\}", "l", spec)
    spec = re.sub(r"\*\{(\d+)\}\{([^}]*)\}", lambda m: m.group(2) * int(m.group(1)), spec)
    return sum(1 for c in spec if c in "lcrX")


def table(m):
    env = m.group(0)
    cap = braced(env, env.index("\\caption{") + 8)[0]
    lab = re.search(r"\\label\{([^}]*)\}", env).group(1)
    tab = re.search(r"\\begin\{tabular\}.*?\\end\{tabular\}", env, re.S).group(0)
    spec, end = braced(tab, len("\\begin{tabular}"))
    tab = "\\begin{tabular}{" + "l" * ncols(spec) + "}" + tab[end:]
    tab = re.sub(r"\\cmidrule(\([^)]*\))?\{[^}]*\}", "", tab)
    tab = re.sub(r"\\addlinespace(\[[^\]]*\])?", "", tab)
    tab = sub_cmd(tab, "makecell", lambda a: a.replace("\\\\", " "))
    tab = re.sub(r"\\makecell\[[^\]]*\]", r"\\makecell", tab)
    tab = sub_cmd(tab, "makecell", lambda a: a.replace("\\\\", " "))
    tab = re.sub(r"\\(scriptsize|footnotesize|small|tiny|normalsize)\b", "", tab)
    tab = re.sub(r"\\multicolumn\{(\d+)\}\{(?:[^{}]|\{[^{}]*\})*\}", r"\\multicolumn{\1}{l}", tab)
    tab = re.sub(r"\n\s*\n", "\n", tab)  # no blank lines inside a tabular
    tab = re.sub(r"\\\\\[[^\]]*\]", r"\\\\", tab)
    return f"\n\n{PB}\n\n\\textbf{{TABLE {labels[lab]}}} {cap}\n\n{tab}\n\n"


body = re.sub(r"\\clearpage\s*\\begin\{table\}.*?\\end\{table\}", table, body, flags=re.S)

# ---------------------------------------------------------------- figure legends
def legend(m):
    cap, labs = m.group(1), re.findall(r"\\label\{([^}]*)\}", m.group(2))
    return "\n\n\\textbf{FIGURE %s} %s\n\n" % (labels[labs[0]], cap)


body = re.sub(r"\{\\captionsetup\{type=figure\}\\caption\{(.*?)\}((?:\\label\{[^}]*\})+)\}\\par\\medskip", legend, body, flags=re.S)
body = body.replace("\\noindent\\textbf{Figure Legends}\\par\\medskip", "\\textbf{Figure Legends}\n\n")

# ---------------------------------------------------------------- references
def bibliography(m):
    items = re.findall(r"\\bibitem\{([^}]*)\}\s*(.*?)(?=\\bibitem|\\end\{thebibliography\})", m.group(0), re.S)
    out = ["\\textbf{References}"]
    for k, t in items:
        out.append(f"{bibnum[k]}. " + " ".join(t.split()))
    return "\n\n".join(out) + "\n\n"


body = re.sub(r"\\begin\{thebibliography\}.*?\\end\{thebibliography\}", bibliography, body, flags=re.S)

# ---------------------------------------------------------------- remaining layout commands
body = body.replace("\\clearpage", "\n\n" + PB + "\n\n")
for c in ["linenumbers", "nolinenumbers", "noindent", "bigskip", "medskip", "smallskip", "centering", "par"]:
    body = re.sub(r"\\%s(?![A-Za-z])" % c, "\n" if c == "par" else "", body)
body = body.replace("\\cmark", "\u2713").replace("\\xmark", "\u2717")
body = sub_cmd(body, "textcolor", lambda a: "")  # colour name; the coloured text follows in braces
body = re.sub(r"\\S(?![A-Za-z])", "\u00a7", body)
body = re.sub(r"\\(vspace|hspace)\*?\{[^}]*\}", "", body)
body = body.replace("{\\large\\bfseries ", "{\\bfseries ")

doc = "\\documentclass{article}\n\\usepackage{amsmath,amssymb}\n\\begin{document}\n" + body + "\n\\end{document}\n"
(d / "manuscript_for_word.tex").write_text(doc, encoding="utf-8")
subprocess.run(["pandoc", "-f", "latex", "-t", "docx", "--number-sections",
                str(d / "manuscript_for_word.tex"), "-o", str(OUT)], check=True)

# ---------------------------------------------------------------- JFS layout in Word
w = Document(OUT)
for st in w.styles:
    if st.type != 1:  # paragraph styles
        continue
    f = st.font
    f.name = "Times New Roman"
    rpr = st.element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts"); rpr.append(rfonts)
    for a in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rfonts.set(qn(a), "Times New Roman")
    for a in ("w:asciiTheme", "w:hAnsiTheme", "w:cstheme", "w:eastAsiaTheme"):
        if rfonts.get(qn(a)) is not None:
            del rfonts.attrib[qn(a)]
    f.color.rgb = RGBColor(0, 0, 0)
    pf = st.paragraph_format
    pf.line_spacing = 2.0
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)
    f.size = Pt(12)
    if st.name.startswith("Heading"):
        f.bold = False; f.italic = False; f.all_caps = False
        pf.space_before = Pt(12)
        pf.keep_with_next = True
        if st.name == "Heading 1":
            f.bold = True; f.all_caps = True
        elif st.name == "Heading 2":
            f.italic = True
for st in ("Title", "Subtitle"):
    if st in [s.name for s in w.styles]:
        w.styles[st].font.size = Pt(12)

# page breaks
for p in list(w.paragraphs):
    if p.text.strip() == PB:
        for r in p.runs:
            r.text = ""
        p.runs[0].add_break(WD_BREAK.PAGE) if p.runs else p.add_run().add_break(WD_BREAK.PAGE)
        p.paragraph_format.line_spacing = 1.0
# title block centred (first page, before "Abstract")
from docx.enum.text import WD_ALIGN_PARAGRAPH
for p in w.paragraphs:
    if p.text.strip().startswith("Abstract"):
        break
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
# first line indent for body text paragraphs
for p in w.paragraphs:
    if p.style.name in ("Body Text", "First Paragraph"):
        p.paragraph_format.first_line_indent = Pt(0)
# tables: full text width, autofit, single-spaced 10 pt
for t in w.tables:
    tblPr = t._tbl.tblPr
    for tag in ("w:tblW", "w:tblLayout"):
        e = tblPr.find(qn(tag))
        if e is not None:
            tblPr.remove(e)
    tw = OxmlElement("w:tblW"); tw.set(qn("w:w"), "5000"); tw.set(qn("w:type"), "pct"); tblPr.append(tw)
    lay = OxmlElement("w:tblLayout"); lay.set(qn("w:type"), "autofit"); tblPr.append(lay)
    # column widths in proportion to the longest entry of each column
    grid = t._tbl.tblGrid
    cols = grid.findall(qn("w:gridCol"))
    longest = [6] * len(cols)
    for row in t._tbl.findall(qn("w:tr")):
        ci = 0
        for tc in row.findall(qn("w:tc")):
            span = tc.find(qn("w:tcPr") + "/" + qn("w:gridSpan"))
            n = int(span.get(qn("w:val"))) if span is not None else 1
            txt = "".join(x.text or "" for x in tc.iter(qn("w:t")))
            if n == 1 and ci < len(cols):
                longest[ci] = max(longest[ci], min(len(txt), 38))
            ci += n
    tot = sum(x + 3 for x in longest)
    widths = [int(9360 * (x + 3) / tot) for x in longest]
    for gc, wd in zip(cols, widths):
        gc.set(qn("w:w"), str(wd))
    for row in t._tbl.findall(qn("w:tr")):
        ci = 0
        for tc in row.findall(qn("w:tc")):
            tcPr = tc.find(qn("w:tcPr"))
            if tcPr is None:
                tcPr = OxmlElement("w:tcPr"); tc.insert(0, tcPr)
            span = tcPr.find(qn("w:gridSpan"))
            n = int(span.get(qn("w:val"))) if span is not None else 1
            tcw = tcPr.find(qn("w:tcW"))
            if tcw is None:
                tcw = OxmlElement("w:tcW"); tcPr.insert(0, tcw)
            tcw.set(qn("w:w"), str(sum(widths[ci:ci + n]))); tcw.set(qn("w:type"), "dxa")
            ci += n
    for row in t.rows:
        for cell in row.cells:
            for p in cell.paragraphs:
                p.paragraph_format.line_spacing = 1.0
                for r in p.runs:
                    r.font.size = Pt(8 if len(t.columns) >= 9 else 9)
# section: Letter, 1-inch margins, line numbers, page numbers
sec = w.sections[0]
from docx.shared import Inches
sec.page_width, sec.page_height = Inches(8.5), Inches(11)
for side in ("left_margin", "right_margin", "top_margin", "bottom_margin"):
    setattr(sec, side, Inches(1))
ln = OxmlElement("w:lnNumType")
ln.set(qn("w:countBy"), "1"); ln.set(qn("w:restart"), "continuous"); ln.set(qn("w:distance"), "360")
sec._sectPr.append(ln)
fp = sec.footer.paragraphs[0]
fp.alignment = 1
run = fp.add_run()
for tag, txt in (("begin", None), (None, " PAGE "), ("end", None)):
    if tag:
        e = OxmlElement("w:fldChar"); e.set(qn("w:fldCharType"), tag); run._r.append(e)
    else:
        e = OxmlElement("w:instrText"); e.set(qn("xml:space"), "preserve"); e.text = txt; run._r.append(e)
# empty document properties (double-blind)
cp = w.core_properties
cp.author = ""; cp.last_modified_by = ""; cp.title = ""; cp.subject = ""; cp.keywords = ""; cp.comments = ""
w.save(OUT)
print("wrote", OUT)
