
import csv
import hashlib
from pathlib import Path

ROOT = Path(".")
REPORT = Path("experiments/near_duplicate_candidates.csv")

with REPORT.open(encoding="utf-8-sig", newline="") as f:
    rows = list(csv.DictReader(f))

pairs = [
    row for row in rows
    if int(row["phash_distance"]) == 0
]

print("Zero-distance pairs:", len(pairs))

same = 0
different = 0
missing = 0

for row in pairs[:20]:
    path_a = ROOT / row["path_a"].replace("\\", "/")
    path_b = ROOT / row["path_b"].replace("\\", "/")

    if not path_a.is_file() or not path_b.is_file():
        print("MISSING:", path_a, "<->", path_b)
        missing += 1
        continue

    hash_a = hashlib.sha256(path_a.read_bytes()).hexdigest()
    hash_b = hashlib.sha256(path_b.read_bytes()).hexdigest()

    if hash_a == hash_b:
        same += 1
        result = "SAME_BYTES"
    else:
        different += 1
        result = "DIFFERENT_BYTES"

    print(result, "|", row["image_a"], "<->", row["image_b"])

print("\nSummary for first 20 pairs:")
print("Same bytes:", same)
print("Different bytes:", different)
print("Missing paths:", missing)
