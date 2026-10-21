"""Amendment A6 (DECISIONS.md Section 20): leakage and design checks for the fresh set.

    python experiments/fresh/check_fresh_identity.py dataset/data/fresh_20261021

Fails (exit 1) if any Aadhaar number, PAN or photo seed of the fresh set also
occurs in v1, if the pre-flight or the design counts are wrong, or if any image
file is missing or has the wrong size. Reports the share of fresh full names that
also occur in v1 (names come from a shared pool, as within v1).
"""
import argparse
import json
import os
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
V1 = ROOT / "dataset" / "data" / "v1"


def jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("corpus")
    ap.add_argument("--n-persons", type=int, default=90)
    ap.add_argument("--skip-files", action="store_true", help="skip image-file checks (no images on this machine)")
    a = ap.parse_args(argv)
    fresh = Path(a.corpus)
    if fresh.resolve() == V1.resolve():
        sys.exit("STOP: the fresh corpus path is the v1 corpus.")
    problems = []

    v1_rec, fr_rec = jsonl(V1 / "records.jsonl"), jsonl(fresh / "records.jsonl")
    for key in ("aadhaar", "pan", "photo_seed"):
        shared = {r[key] for r in fr_rec} & {r[key] for r in v1_rec}
        print(f"{key}: {len(shared)} shared with v1")
        if shared:
            problems.append(f"{len(shared)} {key} value(s) shared with v1, e.g. {sorted(shared)[:3]}")
    v1_names = {r["name_latin"] for r in v1_rec}
    same = sum(r["name_latin"] in v1_names for r in fr_rec)
    print(f"full names also in v1: {same}/{len(fr_rec)} ({100 * same / len(fr_rec):.1f}%, informational)")

    if len(fr_rec) != a.n_persons:
        problems.append(f"{len(fr_rec)} persons, expected {a.n_persons}")
    rows = jsonl(fresh / "manifest.jsonl")
    want = a.n_persons * 2 * 6 * 3
    if len(rows) != want:
        problems.append(f"{len(rows)} images, expected {want}")
    cells = Counter((r["doc_type"], r["forgery_category"], r["quality_tier"]) for r in rows)
    for (doc, cat, tier), n in sorted(cells.items()):
        expect = a.n_persons * (2 if cat == "C0" else 1)
        if n != expect:
            problems.append(f"{doc}/{cat}/{tier}: {n} images, expected {expect}")
    if len(cells) != 2 * 5 * 3:
        problems.append(f"{len(cells)} doc/category/tier cells, expected 30")
    bad_gt = [r["image_id"] for r in rows if r["rule_gt_verdict"] != r["expected_rule"]]
    if bad_gt:
        problems.append(f"{len(bad_gt)} images whose GT rule verdict differs from the design")
    if len({r["image_id"] for r in rows}) != len(rows):
        problems.append("duplicate image_id")
    missing = wrong = 0
    for r in ([] if a.skip_files else rows):
        p = fresh / Path(r["file"].replace("\\", "/"))
        if not p.is_file():
            missing += 1
        elif os.path.getsize(p) != r["bytes"]:
            wrong += 1
    print("image files: not checked (--skip-files)" if a.skip_files else
          f"image files: {len(rows)} listed, {missing} missing, {wrong} wrong size")
    if missing or wrong:
        problems.append(f"{missing} missing and {wrong} wrong-size image files")

    if problems:
        print("FAIL:\n  " + "\n  ".join(problems))
        return 1
    print(f"PASS: {len(fr_rec)} persons, {len(rows)} images, no identifier or photo shared with v1")
    return 0


if __name__ == "__main__":
    sys.exit(main())
