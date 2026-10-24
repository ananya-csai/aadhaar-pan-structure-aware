# -*- coding: utf-8 -*-
"""Compare a rebuilt corpus with the frozen v1 images, image by image.

    python scripts/compare_to_frozen.py /path/to/rebuild
    python scripts/compare_to_frozen.py /path/to/rebuild --frozen-images data/v1

The first form uses data/v1/IMAGE_SHA256.txt and lists the images whose bytes
differ. If the frozen images are also available, the second form adds how many
pixels differ and by how much (needs numpy and Pillow).

Reference result (24 Oct 2026, Linux, Python 3.13, pinned requirements,
`--skip-ocr`): 10,791 of 10,800 images byte-identical; 9 differ in at most
37 pixels, by at most 3 grey levels, all at the right edge of the image
(experiments/logs/corpus_rebuild_linux_2026-10-24.txt).
"""
from __future__ import annotations

import argparse
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LIST = os.path.join(HERE, "..", "data", "v1", "IMAGE_SHA256.txt")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rebuild")
    ap.add_argument("--frozen-images", default=None)
    a = ap.parse_args()

    expected = {}
    with open(LIST, encoding="utf-8") as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            h, rel = line.split(None, 1)
            expected[rel.strip()] = h
    missing, differ = [], []
    for rel, h in sorted(expected.items()):
        p = os.path.join(a.rebuild, rel)
        if not os.path.exists(p):
            missing.append(rel)
            continue
        with open(p, "rb") as fh:
            if hashlib.sha256(fh.read()).hexdigest() != h:
                differ.append(rel)
    same = len(expected) - len(missing) - len(differ)
    print(f"images {len(expected)}: identical {same}, different {len(differ)}, missing {len(missing)}")
    for rel in differ:
        line = f"  {rel}"
        if a.frozen_images:
            import numpy as np
            from PIL import Image
            x = np.asarray(Image.open(os.path.join(a.frozen_images, rel)), dtype=int)
            y = np.asarray(Image.open(os.path.join(a.rebuild, rel)), dtype=int)
            if x.shape != y.shape:
                line += f": shape {x.shape} vs {y.shape}"
            else:
                d = np.abs(x - y).max(-1)
                line += f": {int((d > 0).sum())} pixels differ, max {int(d.max())} levels"
        print(line)
    sys.exit(0 if not missing else 1)


if __name__ == "__main__":
    main()
