# -*- coding: utf-8 -*-
"""Add a 256-bit perceptual hash to an existing manifest (in place)."""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from PIL import Image
from idforge.phash import phash256

out = sys.argv[1] if len(sys.argv) > 1 else "data/v1"
mp = os.path.join(out, "manifest.jsonl")
rows = [json.loads(l) for l in open(mp)]
for i, r in enumerate(rows):
    r["phash256"] = phash256(Image.open(os.path.join(out, r["file"]))).hex()
    if (i + 1) % 2000 == 0:
        print(f"  {i+1}/{len(rows)}", flush=True)
with open(mp, "w") as fh:
    for r in rows:
        fh.write(json.dumps(r, ensure_ascii=False) + "\n")
print("updated", mp)
