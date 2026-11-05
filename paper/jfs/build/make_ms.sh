#!/bin/bash
# Build the JFS manuscript project from the authors' source.  usage: make_ms.sh SRC OUT
set -e
B=$(dirname "$0"); SRC=$1; OUT=$2
rm -rf "$OUT"; python3 -I $B/build_jfs.py "$SRC" "$OUT" > "$OUT.buildlog" || { cat "$OUT.buildlog"; exit 1; }
mkdir -p "$OUT/generated"
python3 -I $B/fmt_numbers.py "$SRC/generated/numbers.tex" "$OUT/generated/numbers.tex"
cd "$OUT"
pdflatex -interaction=nonstopmode manuscript >/dev/null || true
python3 -I $B/refs.py "$OUT"
pdflatex -interaction=nonstopmode manuscript >/dev/null || true
pdflatex -interaction=nonstopmode manuscript >/dev/null || true
echo "errors: $(grep -c '^!' manuscript.log)  pages: $(pdfinfo manuscript.pdf | awk '/Pages/{print $2}')"
grep -i "undefined\|overfull\|multiply" manuscript.log | sort | uniq -c | head
