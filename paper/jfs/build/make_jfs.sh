#!/bin/bash
# Rebuild the Journal of Forensic Sciences files from the repository sources.
#   bash paper/jfs/build/make_jfs.sh        (run from the repository root)
# Inputs : paper/wiley/main.tex (master text), paper/generated/, paper/figures/,
#          paper/wiley/tikzfig/ and paper/wiley/tikz_src/
# Outputs: the LaTeX sources in paper/jfs/ (committed) and, in a temporary
#          folder printed at the end, the PDFs and the TIFF figure files.
set -e
ROOT=$(cd "$(dirname "$0")/../../.." && pwd)
B=$ROOT/paper/jfs/build
TMP=$(mktemp -d)
SRC=$TMP/src; OUT=$TMP/out
mkdir -p "$SRC/figures"
cp "$ROOT/paper/wiley/main.tex" "$SRC/"
cp -r "$ROOT/paper/generated" "$SRC/generated"
cp "$ROOT"/paper/figures/*.pdf "$SRC/figures/"
cp -r "$ROOT/paper/wiley/tikz_src" "$SRC/figures/tikz_src"
cp -r "$ROOT/paper/wiley/tikzfig" "$SRC/tikzfig"
bash "$B/build_all.sh" "$SRC" "$OUT"
J=$ROOT/paper/jfs
cp "$OUT"/{manuscript,supplementary,manuscript_with_figures,figure_pages}.tex "$J/"
mkdir -p "$J/generated" "$J/figure_pdf"
cp "$OUT/generated/numbers.tex" "$J/generated/"
cp "$OUT"/figure_pdf/*.pdf "$J/figure_pdf/"
cp "$OUT/build_log.txt" "$J/CHANGES_FROM_WILEY.txt"
cp "$OUT/figure_map.txt" "$J/figure_map.txt"
echo "PDFs and figure_files/*.tif: $OUT"
