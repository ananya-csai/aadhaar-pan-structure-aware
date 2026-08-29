#!/usr/bin/env bash
# Full pipeline: corpus -> 256-bit hashes -> statistics/audits/figures -> LaTeX.
set -euo pipefail
OUT="${1:-data/v1}"
export PYTHONPATH=src
python3 -m idforge.build --config configs/dataset_v1.yaml --out "$OUT"
python3 scripts/add_phash256.py "$OUT"
python3 -m idforge.report --out "$OUT"
python3 -m idforge.probe_cli --out "$OUT"
python3 scripts/export_latex.py --out "$OUT" --dest paper/generated
echo "pipeline complete -> $OUT"
