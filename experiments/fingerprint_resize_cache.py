"""Fingerprint the 384x256 resize cache so it can be verified without committing it.

The cache (~1.4 GB of PNGs) is derived data and is git-ignored. This script
writes two small, tracked files that pin exactly what the cache contains:

  experiments/cache_fingerprints/384x256_manifest.csv  one row per image + sha256
  experiments/cache_fingerprints/384x256_SHA256.txt    one aggregate hash + environment

Anyone (including the partner without a GPU) can rebuild the cache with
build_resize_cache.py and rerun this script: if the aggregate hash matches the
committed one, the two caches are byte-identical.

Run from the repository root:
    python experiments/fingerprint_resize_cache.py                       # 384x256
    python experiments/fingerprint_resize_cache.py --width 768 --height 512
"""

import argparse
import csv
import hashlib
import platform
import sys
from pathlib import Path

import PIL
from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument("--width", type=int, default=384)
ap.add_argument("--height", type=int, default=256)
_args = ap.parse_args()
SIZE = f"{_args.width}x{_args.height}"

ROOT = Path.cwd()
CACHE_DIR = ROOT / "experiments" / "cache" / SIZE
CACHE_MANIFEST = CACHE_DIR / "cache_manifest.csv"
DATASET_MANIFEST = ROOT / "dataset" / "data" / "v1" / "manifest.csv"
CORPUS_SHA_FILE = ROOT / "dataset" / "data" / "v1" / "CORPUS_SHA256.txt"
OUT_DIR = ROOT / "experiments" / "cache_fingerprints"
OUT_MANIFEST = OUT_DIR / f"{SIZE}_manifest.csv"
OUT_SUMMARY = OUT_DIR / f"{SIZE}_SHA256.txt"

EXPECTED_SIZE = (_args.width, _args.height)


def sha256_file(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    for p in (CACHE_MANIFEST, DATASET_MANIFEST):
        if not p.is_file():
            sys.exit(f"Missing {p}. Run from the repository root after building the cache.")

    with CACHE_MANIFEST.open(newline="", encoding="utf-8-sig") as f:
        cache_rows = list(csv.DictReader(f))
    with DATASET_MANIFEST.open(newline="", encoding="utf-8-sig") as f:
        dataset_rows = {r["image_id"]: r for r in csv.DictReader(f)}

    # 1. Exactly one cached image per manifest image, and matching metadata.
    cache_ids = [r["image_id"] for r in cache_rows]
    assert len(cache_ids) == len(set(cache_ids)), "duplicate image_id in cache manifest"
    assert set(cache_ids) == set(dataset_rows), "cache and dataset manifest image_ids differ"
    for r in cache_rows:
        d = dataset_rows[r["image_id"]]
        for col in ("split", "doc_type", "forgery_category", "label"):
            assert r[col] == d[col], f"{r['image_id']}: {col} mismatch ({r[col]} vs {d[col]})"

    # 2. No stale PNGs left over from an earlier run.
    on_disk = {p.stem for p in CACHE_DIR.glob("*.png")}
    extra = on_disk - set(cache_ids)
    missing = set(cache_ids) - on_disk
    assert not missing, f"{len(missing)} cached PNGs missing, e.g. {sorted(missing)[:3]}"
    assert not extra, f"{len(extra)} stale PNGs not in manifest, e.g. {sorted(extra)[:3]}"

    # 3. Hash and check every cached image.
    out_rows = []
    for i, r in enumerate(sorted(cache_rows, key=lambda x: x["image_id"]), start=1):
        path = ROOT / Path(r["cached_file"])
        with Image.open(path) as im:
            assert im.size == EXPECTED_SIZE, f"{path}: size {im.size}"
            assert im.mode == "RGB", f"{path}: mode {im.mode}"
        out_rows.append({
            "image_id": r["image_id"],
            "split": r["split"],
            "doc_type": r["doc_type"],
            "forgery_category": r["forgery_category"],
            "label": r["label"],
            "source_file": r["source_file"].replace("\\", "/"),
            "cached_file": r["cached_file"],
            "original_width": r["original_width"],
            "original_height": r["original_height"],
            "resized_width": r["resized_width"],
            "resized_height": r["resized_height"],
            "sha256": sha256_file(path),
        })
        if i % 1000 == 0 or i == len(cache_rows):
            print(f"hashed {i}/{len(cache_rows)}")

    aggregate = hashlib.sha256(
        "".join(f"{r['image_id']}:{r['sha256']}\n" for r in out_rows).encode()
    ).hexdigest()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with OUT_MANIFEST.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out_rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(out_rows)

    corpus_sha = CORPUS_SHA_FILE.read_text().strip() if CORPUS_SHA_FILE.is_file() else "unknown"
    OUT_SUMMARY.write_text(
        f"cache_sha256: {aggregate}\n"
        f"images: {len(out_rows)}\n"
        f"canvas: {SIZE} RGB PNG, aspect-preserving LANCZOS resize, white pad, centred\n"
        f"built_by: experiments/build_resize_cache.py\n"
        f"source_corpus_sha256_file: {corpus_sha}\n"
        f"python: {platform.python_version()}\n"
        f"pillow: {PIL.__version__}\n"
        f"platform: {platform.platform()}\n"
        f"aggregate_definition: sha256 over lines 'image_id:sha256\\n' sorted by image_id\n",
        encoding="utf-8",
    )

    print("\nPASS: cache verified and fingerprinted.")
    print(f"cache_sha256: {aggregate}")
    print(f"wrote {OUT_MANIFEST.relative_to(ROOT)} and {OUT_SUMMARY.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
