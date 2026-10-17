"""Manifest-driven data loading over a resize cache (roadmap Steps 9 and 11).

Rules this file enforces:
  * membership, split and label come from the frozen dataset manifest only;
  * the cache manifest must agree with it row for row;
  * one item per image_id, sorted by image_id, no duplicates;
  * images must be exactly the cache canvas size and RGB;
  * normalisation is ImageNet mean/std (DECISIONS.md, Section 2).

`read_index` is pure Python so it can be tested without PyTorch.
"""

import csv
from pathlib import Path

IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STD = (0.229, 0.224, 0.225)
SPLITS = ("train", "val", "test")
CATEGORIES = ("C0", "C1", "C2", "C3", "C4")


def parse_size(size):
    w, h = size.lower().split("x")
    return int(w), int(h)


def read_index(root, size, splits, categories):
    """Return the checked list of image records for the given splits and categories."""
    root = Path(root)
    cache_manifest = root / "experiments" / "cache" / size / "cache_manifest.csv"
    dataset_manifest = root / "dataset" / "data" / "v1" / "manifest.csv"
    for p in (cache_manifest, dataset_manifest):
        if not p.is_file():
            raise FileNotFoundError(f"{p} not found. Run from the repository root; "
                                    f"build the {size} cache first.")
    bad = set(splits) - set(SPLITS)
    if bad:
        raise ValueError(f"unknown split(s): {sorted(bad)}")
    bad = set(categories) - set(CATEGORIES)
    if bad:
        raise ValueError(f"unknown category(ies): {sorted(bad)}")

    with dataset_manifest.open(newline="", encoding="utf-8-sig") as f:
        ds = list(csv.DictReader(f))
    with cache_manifest.open(newline="", encoding="utf-8-sig") as f:
        cache = list(csv.DictReader(f))

    ds_by_id = {r["image_id"]: r for r in ds}
    if len(ds_by_id) != len(ds):
        raise ValueError("duplicate image_id in dataset manifest")
    cache_by_id = {r["image_id"]: r for r in cache}
    if len(cache_by_id) != len(cache):
        raise ValueError("duplicate image_id in cache manifest")
    if set(ds_by_id) != set(cache_by_id):
        raise ValueError("cache manifest and dataset manifest contain different image_ids")

    w, h = parse_size(size)
    rows = []
    for image_id in sorted(ds_by_id):
        d, c = ds_by_id[image_id], cache_by_id[image_id]
        for col in ("split", "doc_type", "forgery_category", "label"):
            if d[col] != c[col]:
                raise ValueError(f"{image_id}: {col} differs between manifests")
        if (int(c["canvas_width"]), int(c["canvas_height"])) != (w, h):
            raise ValueError(f"{image_id}: cache canvas is not {size}")
        expected_label = "0" if d["forgery_category"] == "C0" else "1"
        if d["label"] != expected_label:
            raise ValueError(f"{image_id}: label {d['label']} inconsistent with "
                             f"category {d['forgery_category']}")
        if d["split"] in splits and d["forgery_category"] in categories:
            rows.append({
                "image_id": image_id,
                "person_id": d["person_id"],
                "split": d["split"],
                "doc_type": d["doc_type"],
                "forgery_category": d["forgery_category"],
                "c1_op": d.get("c1_op", ""),
                "quality_tier": d["quality_tier"],
                "label": int(d["label"]),
                "cached_file": c["cached_file"],
            })
    if not rows:
        raise ValueError(f"no images for splits={splits} categories={categories}")
    return rows


# Module-level class so DataLoader workers can pickle it (Windows uses "spawn").
try:
    import numpy as np
    import torch
    from PIL import Image
    _Base = torch.utils.data.Dataset
except ImportError:            # read_index stays usable without PyTorch
    torch = None
    _Base = object


class CacheDataset(_Base):
    def __init__(self, root, size, splits, categories):
        if torch is None:
            raise ImportError("PyTorch is required for CacheDataset")
        self.root = Path(root)
        self.size = parse_size(size)
        self.rows = read_index(root, size, splits, categories)
        self.mean = torch.tensor(IMAGENET_MEAN).view(3, 1, 1)
        self.std = torch.tensor(IMAGENET_STD).view(3, 1, 1)

    def __len__(self):
        return len(self.rows)

    def load_rgb(self, i):
        path = self.root / Path(self.rows[i]["cached_file"])
        with Image.open(path) as im:
            if im.mode != "RGB":
                raise ValueError(f"{path}: mode {im.mode}, expected RGB")
            if im.size != self.size:
                raise ValueError(f"{path}: size {im.size}, expected {self.size}")
            return np.asarray(im, dtype=np.uint8).copy()          # H x W x 3, RGB

    def __getitem__(self, i):
        arr = self.load_rgb(i)
        x = torch.from_numpy(arr).permute(2, 0, 1).float().div_(255.0)
        x = (x - self.mean) / self.std
        r = self.rows[i]
        return x, torch.tensor(float(r["label"])), r["image_id"]


def make_dataset(root, size, splits, categories):
    return CacheDataset(root, size, splits, categories)
