
import csv
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(".")
REPORT = Path("experiments/near_duplicate_candidates.csv")
OUT = Path("experiments/near_duplicate_contact_sheet.jpg")

with REPORT.open(encoding="utf-8-sig", newline="") as f:
    rows = list(csv.DictReader(f))

# Select diverse examples among the closest cross-split matches.
rows.sort(key=lambda r: int(r["phash_distance"]))
selected = []
seen_people = set()

for row in rows:
    people = {
        row["image_a"].split("_")[0],
        row["image_b"].split("_")[0],
    }
    if people & seen_people:
        continue
    selected.append(row)
    seen_people.update(people)
    if len(selected) == 12:
        break

thumb_w, thumb_h = 360, 230
label_h = 44
sheet = Image.new("RGB", (thumb_w * 2, (thumb_h + label_h) * len(selected)), "white")
draw = ImageDraw.Draw(sheet)

for i, row in enumerate(selected):
    y = i * (thumb_h + label_h)
    paths = [
        ROOT / row["path_a"].replace("\\", "/"),
        ROOT / row["path_b"].replace("\\", "/"),
    ]

    for j, path in enumerate(paths):
        with Image.open(path) as source:
            im = source.convert("RGB")
            im.thumbnail((thumb_w - 8, thumb_h - 8))
            x = j * thumb_w + (thumb_w - im.width) // 2
            sheet.paste(im, (x, y))

    text = (
        f"Distance {row['phash_distance']} | "
        f"{row['split_a']} {row['image_a']}  <->  "
        f"{row['split_b']} {row['image_b']}"
    )
    draw.text((5, y + thumb_h), text[:115], fill="black")

OUT.parent.mkdir(parents=True, exist_ok=True)
sheet.save(OUT, quality=90)

print("Pairs inspected:", len(selected))
print("Contact sheet:", OUT)
