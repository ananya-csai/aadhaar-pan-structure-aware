# -*- coding: utf-8 -*-
"""Check a built corpus against the frozen manifest, file by file.

    python scripts/verify_corpus_files.py data/v1                # check only
    python scripts/verify_corpus_files.py data/v1 --write-stamp  # also rewrite CORPUS_SHA256.txt

For every row of data/v1/manifest.jsonl the image must exist and its size must
equal the recorded `bytes` (the length of the JPEG the build wrote). No other
.jpg may exist under images/. Then the corpus digest is computed exactly as
corpus_checksum.py does and printed in the CORPUS_SHA256.txt format.

--write-stamp rewrites the stamp only if every file matches the manifest, so a
stamp can never be written for a corpus other than the one the manifest
describes. This is the corpus every experiment used: the manifest carries the
rule and OCR verdicts, and the caches and edit regions were built from these files.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from corpus_checksum import STAMP, corpus_digest  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default="data/v1")
    ap.add_argument("--write-stamp", action="store_true")
    a = ap.parse_args()

    with open(os.path.join(a.root, "manifest.jsonl"), encoding="utf-8") as fh:
        rows = [json.loads(l) for l in fh if l.strip()]
    expected = {r["file"].replace("\\", "/"): r["bytes"] for r in rows}

    missing, wrong = [], []
    for rel, size in expected.items():
        p = os.path.join(a.root, *rel.split("/"))
        if not os.path.isfile(p):
            missing.append(rel)
        elif os.path.getsize(p) != size:
            wrong.append((rel, size, os.path.getsize(p)))
    found = set()
    for dirpath, _, names in os.walk(os.path.join(a.root, "images")):
        for n in names:
            if n.lower().endswith(".jpg"):
                found.add(os.path.relpath(os.path.join(dirpath, n), a.root).replace(os.sep, "/"))
    extra = sorted(found - set(expected))

    print(f"manifest rows {len(rows)}, expected bytes {sum(expected.values())}")
    print(f"missing {len(missing)}, size mismatches {len(wrong)}, extra .jpg {len(extra)}")
    for x in (missing[:5] + [w[0] for w in wrong[:5]] + extra[:5]):
        print("  problem:", x)

    digest, n, total = corpus_digest(a.root)
    line = f"{digest}  {n} images  {total} bytes\n"
    print("corpus digest:", line, end="")
    ok = not (missing or wrong or extra) and n == len(rows)
    if not ok:
        sys.exit("FAIL: the images on disk are not the ones the manifest describes")
    print("PASS: every image matches the frozen manifest")
    if a.write_stamp:
        with open(os.path.join(a.root, STAMP), "w", newline="\n") as fh:
            fh.write(line)
        print(f"wrote {os.path.join(a.root, STAMP)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
