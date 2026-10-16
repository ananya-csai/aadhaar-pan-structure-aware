
import csv
import hashlib
from collections import defaultdict
from pathlib import Path

ROOT = Path("dataset/data/v1")
manifest = ROOT / "manifest.csv"

with manifest.open("r", encoding="utf-8-sig", newline="") as f:
    rows = list(csv.DictReader(f))

print("Manifest rows:", len(rows))

# Check that each person appears in only one split.
person_splits = defaultdict(set)
for row in rows:
    person_splits[row["person_id"]].add(row["split"])

leaked_people = {
    person: splits
    for person, splits in person_splits.items()
    if len(splits) > 1
}
print("Unique people:", len(person_splits))
print("People crossing splits:", len(leaked_people))

# Check exact image duplicates across splits.
hash_splits = defaultdict(set)
missing = []

for row in rows:
    path = ROOT / row["file"].replace("\\", "/")

    if not path.is_file():
        missing.append(str(path))
        continue

    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    hash_splits[digest].add(row["split"])

duplicate_leaks = {
    digest: splits
    for digest, splits in hash_splits.items()
    if len(splits) > 1
}

print("Missing referenced images:", len(missing))
print("Exact duplicate hashes crossing splits:", len(duplicate_leaks))

if not leaked_people and not missing and not duplicate_leaks:
    print("PASS: basic split checks passed.")
else:
    print("CHECK REQUIRED: investigate the reported issues.")
