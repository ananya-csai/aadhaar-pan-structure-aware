"""Contact sheet of cached images: 4 per category, each ORIGINAL beside its CACHED version.

    python experiments/inspect_resize_cache.py                          # 384x256
    python experiments/inspect_resize_cache.py --width 768 --height 512
"""
import argparse
import csv
import random
from pathlib import Path
from PIL import Image, ImageDraw

ap = argparse.ArgumentParser()
ap.add_argument("--width", type=int, default=384)
ap.add_argument("--height", type=int, default=256)
args = ap.parse_args()
W, H = args.width, args.height

ROOT = Path.cwd()
DATASET_DIR = ROOT / "dataset" / "data" / "v1"
CACHE_DIR = ROOT / "experiments" / "cache" / f"{W}x{H}"
METADATA = CACHE_DIR / "cache_manifest.csv"
OUTPUT = ROOT / "experiments" / (
    "resize_cache_contact_sheet.jpg" if (W, H) == (384, 256)
    else f"resize_cache_contact_sheet_{W}x{H}.jpg")

SAMPLES_PER_CATEGORY = 4
random.seed(42)

with METADATA.open("r", newline="", encoding="utf-8-sig") as f:
    rows = list(csv.DictReader(f))

# Sample four images from each category.
selected = []
for category in sorted({r["forgery_category"] for r in rows}):
    candidates = [r for r in rows if r["forgery_category"] == category]
    selected.extend(random.sample(candidates, min(SAMPLES_PER_CATEGORY, len(candidates))))

# Each tile = original (left, fitted to the same box) | cached (right), so
# cropping, colour order, aspect ratio and edit visibility can be compared.
thumb_w, thumb_h = W, H
label_h = 42
tile_w = 2 * thumb_w
sheet = Image.new("RGB", (tile_w, len(selected) * (thumb_h + label_h)), "white")
draw = ImageDraw.Draw(sheet)

for i, row in enumerate(selected):
    cached_path = ROOT / Path(row["cached_file"])
    with Image.open(cached_path) as image:
        cached = image.convert("RGB")
    if cached.size != (W, H):
        raise ValueError(f"Wrong size: {cached_path} -> {cached.size}")
    with Image.open(DATASET_DIR / Path(row["source_file"].replace("\\", "/"))) as image:
        original = image.convert("RGB")
    original.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)

    y = i * (thumb_h + label_h)
    sheet.paste(original, (0, y))
    sheet.paste(cached, (thumb_w, y))
    draw.text((5, y + thumb_h + 4),
              f"{row['image_id']} | {row['forgery_category']} | {row['split']}"
              f"   left: original {row['original_width']}x{row['original_height']}   right: cached {W}x{H}",
              fill="black")

sheet.save(OUTPUT, quality=95)
print(f"PASS: inspected {len(selected)} cached images beside their originals.")
print(f"Contact sheet: {OUTPUT}")
