
import csv
import random
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path.cwd()
CACHE_DIR = ROOT / "experiments" / "cache" / "384x256"
METADATA = CACHE_DIR / "cache_manifest.csv"
OUTPUT = ROOT / "experiments" / "resize_cache_contact_sheet.jpg"

SAMPLES_PER_CATEGORY = 4
random.seed(42)

with METADATA.open("r", newline="", encoding="utf-8-sig") as f:
    rows = list(csv.DictReader(f))

# Sample four images from each category.
selected = []
for category in sorted({r["forgery_category"] for r in rows}):
    candidates = [r for r in rows if r["forgery_category"] == category]
    selected.extend(random.sample(candidates, min(SAMPLES_PER_CATEGORY, len(candidates))))

thumb_w, thumb_h = 384, 256
label_h = 42
columns = 2
rows_per_pair = (len(selected) + columns - 1) // columns

sheet = Image.new(
    "RGB",
    (columns * thumb_w, rows_per_pair * (thumb_h + label_h)),
    "white",
)
draw = ImageDraw.Draw(sheet)

for i, row in enumerate(selected):
    path = ROOT / Path(row["cached_file"])
    with Image.open(path) as image:
        image = image.convert("RGB")
        if image.size != (384, 256):
            raise ValueError(f"Wrong size: {path} -> {image.size}")

    x = (i % columns) * thumb_w
    y = (i // columns) * (thumb_h + label_h)
    sheet.paste(image, (x, y))

    label = (
        f"{row['forgery_category']} | {row['doc_type']} | "
        f"{row['split']}"
    )
    draw.text((x + 5, y + thumb_h + 4), label, fill="black")

sheet.save(OUTPUT, quality=95)
print(f"PASS: inspected {len(selected)} cached images.")
print(f"Contact sheet: {OUTPUT}")
