"""Tile grid and tile labels for the tile-based visual detector (Amendment A2, variant `tiles`).

Every released image (at most 1012 x 638) is placed top-left on a white
1024 x 640 canvas, with NO resizing, so every original pixel is kept. The canvas
is cut into a fixed grid of 15 overlapping 256 x 256 tiles (stride 192).

Tile labels are used for TRAINING only:
  * every tile of a C0 image is negative (0);
  * for a C1 image, a tile is positive (1) if it contains at least 25% of the
    edit region's area, ignored (-1) if it touches the region but holds less
    than that, and negative (0) if it does not touch it.
The document score is the maximum tile logit, so no region information is
needed at validation or test time.

The pure-Python parts here are tested in test_tiles.py without PyTorch.
"""

import csv
from pathlib import Path

CANVAS_W, CANVAS_H = 1024, 640
TILE = 256
STRIDE = 192
XS = list(range(0, CANVAS_W - TILE + 1, STRIDE))      # 0 192 384 576 768
YS = list(range(0, CANVAS_H - TILE + 1, STRIDE))      # 0 192 384
GRID = [(x, y) for y in YS for x in XS]               # 15 tiles, row-major
POS_FRACTION = 0.25


def area(b):
    return max(0, b[2] - b[0]) * max(0, b[3] - b[1])


def intersect(a, b):
    return (max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3]))


def tile_labels(region):
    """Labels for the 15 tiles given an edit region (x0, y0, x1, y1), or None for C0."""
    if region is None:
        return [0] * len(GRID)
    ra = area(region)
    if ra <= 0:
        raise ValueError(f"empty region {region}")
    labels = []
    for x, y in GRID:
        inter = area(intersect(region, (x, y, x + TILE, y + TILE)))
        labels.append(1 if inter >= POS_FRACTION * ra else (-1 if inter > 0 else 0))
    return labels


def read_regions(root):
    path = Path(root) / "experiments" / "e2_visual" / "c1_regions.csv"
    if not path.is_file():
        raise FileNotFoundError(f"{path} not found; run map_c1_regions.py first")
    with path.open(newline="", encoding="utf-8") as f:
        return {r["image_id"]: (int(r["x0"]), int(r["y0"]), int(r["x1"]), int(r["y1"]))
                for r in csv.DictReader(f)}


def read_files(root):
    path = Path(root) / "dataset" / "data" / "v1" / "manifest.csv"
    with path.open(newline="", encoding="utf-8-sig") as f:
        return {r["image_id"]: r["file"].replace("\\", "/") for r in csv.DictReader(f)}


def training_tiles(index_rows, regions):
    """(row_index, tile_index, label) for every non-ignored tile of the given images."""
    out = []
    for i, r in enumerate(index_rows):
        if r["forgery_category"] == "C0":
            labels = tile_labels(None)
        elif r["forgery_category"] == "C1":
            labels = tile_labels(regions[r["image_id"]])
            if 1 not in labels:
                raise ValueError(f"{r['image_id']}: no positive tile for region "
                                 f"{regions[r['image_id']]}")
        else:
            raise ValueError("tile training uses C0 and C1 only")
        out.extend((i, t, lab) for t, lab in enumerate(labels) if lab != -1)
    return out


# ---------------------------------------------------------------- PyTorch part
try:
    import numpy as np
    import torch
    from PIL import Image
    _Base = torch.utils.data.Dataset
except ImportError:
    torch = None
    _Base = object

IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STD = (0.229, 0.224, 0.225)


class _ImageSource:
    def __init__(self, root, rows):
        self.root = Path(root)
        self.rows = rows
        self.files = read_files(root)
        self.mean = torch.tensor(IMAGENET_MEAN).view(3, 1, 1)
        self.std = torch.tensor(IMAGENET_STD).view(3, 1, 1)

    def canvas(self, i):
        iid = self.rows[i]["image_id"]
        path = self.root / "dataset" / "data" / "v1" / self.files[iid]
        with Image.open(path) as im:
            im = im.convert("RGB")
            w, h = im.size
            if w > CANVAS_W or h > CANVAS_H:
                raise ValueError(f"{path}: {w}x{h} exceeds the {CANVAS_W}x{CANVAS_H} canvas")
            c = Image.new("RGB", (CANVAS_W, CANVAS_H), (255, 255, 255))
            c.paste(im, (0, 0))
        return np.asarray(c, dtype=np.uint8)

    def to_tensor(self, arr):
        x = torch.from_numpy(arr.copy()).permute(2, 0, 1).float().div_(255.0)
        return (x - self.mean) / self.std


class TileTrainSet(_ImageSource, _Base):
    """One item = one labelled tile. `items` is a list of (row_index, tile_index, label)."""

    def __init__(self, root, rows, items):
        _ImageSource.__init__(self, root, rows)
        self.items = items

    def __len__(self):
        return len(self.items)

    def __getitem__(self, k):
        i, t, lab = self.items[k]
        x, y = GRID[t]
        arr = self.canvas(i)[y:y + TILE, x:x + TILE]
        return self.to_tensor(arr), torch.tensor(float(lab))


class TileImageSet(_ImageSource, _Base):
    """One item = all 15 tiles of one image, for scoring: (15,3,256,256), label, image_id."""

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, i):
        arr = self.canvas(i)
        tiles = torch.stack([self.to_tensor(arr[y:y + TILE, x:x + TILE]) for x, y in GRID])
        r = self.rows[i]
        return tiles, torch.tensor(float(r["label"])), r["image_id"]
