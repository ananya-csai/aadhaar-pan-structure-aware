# -*- coding: utf-8 -*-
"""Deterministic checksum over a built image corpus.

    python scripts/corpus_checksum.py data/v1            # compute and print
    python scripts/corpus_checksum.py data/v1 --verify   # compare to the
                                                         # committed value

The hash covers every image file's path (relative to the corpus root, with
forward slashes) and its exact bytes, in sorted path order. Two builds that
agree on this value are byte-identical corpora, which is the strongest
reproducibility statement the dataset can make: it lets a reviewer confirm that
the images they regenerated are the images the paper reports on, without
anybody having to transfer a gigabyte.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import sys

STAMP = "CORPUS_SHA256.txt"


def corpus_digest(root: str) -> tuple:
    img = os.path.join(root, "images")
    if not os.path.isdir(img):
        sys.exit(f"no images/ directory under {root} — build the corpus first "
                 f"(bash scripts/build_all.sh {root})")
    files = []
    for dirpath, _, names in os.walk(img):
        for n in names:
            if n.lower().endswith(".jpg"):
                p = os.path.join(dirpath, n)
                files.append((os.path.relpath(p, root).replace(os.sep, "/"), p))
    files.sort()
    h = hashlib.sha256()
    total = 0
    for rel, p in files:
        h.update(rel.encode("utf-8"))
        h.update(b"\0")
        with open(p, "rb") as fh:
            while True:
                b = fh.read(1 << 20)
                if not b:
                    break
                h.update(b)
                total += len(b)
    return h.hexdigest(), len(files), total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default="data/v1")
    ap.add_argument("--verify", action="store_true")
    a = ap.parse_args()
    digest, n, total = corpus_digest(a.root)
    line = f"{digest}  {n} images  {total} bytes\n"
    stamp = os.path.join(a.root, STAMP)
    if a.verify:
        if not os.path.exists(stamp):
            sys.exit(f"no {stamp} to verify against")
        want = open(stamp).read().strip().split()[0]
        print(f"expected {want}\ncomputed {digest}")
        if want == digest:
            print(f"MATCH — your {n} images are byte-identical to the released corpus")
            return 0
        sys.exit("MISMATCH — see dataset/README.md on pinned library versions; "
                 "the dataset CONTENT (values, labels, splits) still derives "
                 "from the seed, only the JPEG encoding can differ")
    print(line, end="")
    with open(stamp, "w") as fh:
        fh.write(line)
    print(f"wrote {stamp}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
