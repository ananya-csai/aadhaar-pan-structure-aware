
import csv
from pathlib import Path

import imagehash
from PIL import Image
from scipy.spatial.distance import hamming

ROOT = Path("dataset/data/v1")
OUT = Path("experiments/near_duplicate_candidates.csv")
MAX_DISTANCE = 4

with (ROOT / "manifest.csv").open(
    encoding="utf-8-sig", newline=""
) as f:
    rows = list(csv.DictReader(f))

records = []
for i, row in enumerate(rows, start=1):
    path = ROOT / row["file"].replace("\\", "/")
    with Image.open(path) as im:
        ph = imagehash.phash(im.convert("RGB"))

    records.append({
        "image_id": row["image_id"],
        "split": row["split"],
        "category": row["forgery_category"],
        "path": str(path),
        "hash": int(str(ph), 16),
    })

    if i % 1000 == 0:
        print(f"Hashed {i}/{len(rows)} images...", flush=True)

# Build a BK-tree over the 64-bit perceptual hashes.
class BKNode:
    def __init__(self, value, record_index):
        self.value = value
        self.indices = [record_index]
        self.children = {}

def bit_distance(a, b):
    return (a ^ b).bit_count()

tree = None

def insert(node, value, index):
    if node is None:
        return BKNode(value, index)

    distance = bit_distance(value, node.value)
    if distance == 0:
        node.indices.append(index)
    elif distance in node.children:
        insert(node.children[distance], value, index)
    else:
        node.children[distance] = BKNode(value, index)
    return node

def query(node, value, radius, found):
    if node is None:
        return

    distance = bit_distance(value, node.value)
    if distance <= radius:
        found.extend(node.indices)

    low = max(0, distance - radius)
    high = distance + radius

    for edge, child in node.children.items():
        if low <= edge <= high:
            query(child, value, radius, found)

for i, record in enumerate(records):
    tree = insert(tree, record["hash"], i)

pairs = []
seen = set()

for i, record in enumerate(records):
    candidates = []
    query(tree, record["hash"], MAX_DISTANCE, candidates)

    for j in candidates:
        if j <= i:
            continue

        other = records[j]
        if record["split"] == other["split"]:
            continue

        distance = bit_distance(record["hash"], other["hash"])
        key = (i, j)

        if key not in seen:
            seen.add(key)
            pairs.append({
                "image_a": record["image_id"],
                "split_a": record["split"],
                "category_a": record["category"],
                "path_a": record["path"],
                "image_b": other["image_id"],
                "split_b": other["split"],
                "category_b": other["category"],
                "path_b": other["path"],
                "phash_distance": distance,
            })

    if (i + 1) % 1000 == 0:
        print(f"Compared {i + 1}/{len(records)} images...", flush=True)

fields = [
    "image_a", "split_a", "category_a", "path_a",
    "image_b", "split_b", "category_b", "path_b",
    "phash_distance",
]

OUT.parent.mkdir(parents=True, exist_ok=True)
with OUT.open("w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(sorted(pairs, key=lambda x: x["phash_distance"]))

print("Images hashed:", len(records))
print("Cross-split candidate pairs:", len(pairs))
print("Candidate report:", OUT)
print("Review candidates visually; a small hash distance is not proof of leakage.")

