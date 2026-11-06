#!/bin/bash
# Full JFS package build.  usage: build_all.sh SRC OUT
B=$(cd "$(dirname "$0")" && pwd); SRC=$1; OUT=$2
"$B/make_ms.sh" "$SRC" "$OUT"
python3 -I "$B/figures.py" "$OUT" "$SRC" > "$OUT.figlog"
python3 -I "$B/supp.py" "$OUT"
# title page and cover letter hold contact details and are kept out of the
# public repository; they are compiled when present next to this script.
for f in titlepage cover_letter; do [ -f "$B/$f.tex" ] && cp "$B/$f.tex" "$OUT/"; done
printf '%% Reading copy (NOT for upload): manuscript with the figures appended.\n\\def\\withfigures{}\n\\input{manuscript}\n' > "$OUT/manuscript_with_figures.tex"
cd "$OUT"
for f in supplementary titlepage cover_letter manuscript_with_figures; do
  [ -f $f.tex ] || continue
  pdflatex -interaction=nonstopmode $f >/dev/null; pdflatex -interaction=nonstopmode $f >/dev/null
  echo "$f: errors $(grep -c '^!' $f.log), pages $(pdfinfo $f.pdf | awk '/Pages/{print $2}'), overfull $(grep -c 'Overfull' $f.log), undefined $(grep -ci 'undefined' $f.log)"
done
echo "manuscript: errors $(grep -c '^!' manuscript.log), pages $(pdfinfo manuscript.pdf | awk '/Pages/{print $2}'), overfull $(grep -c 'Overfull' manuscript.log), undefined $(grep -ci 'undefined' manuscript.log)"
# Word copy of the main document (the JFS portal asks for MS Word); needs
# pandoc and python-docx, and is skipped when either is missing.
if command -v pandoc >/dev/null && python3 -c "import docx" 2>/dev/null; then
  python3 -I "$B/to_docx.py" "$OUT" "$OUT/manuscript.docx" && echo "manuscript.docx written"
else
  echo "manuscript.docx skipped (needs pandoc and python-docx)"
fi
