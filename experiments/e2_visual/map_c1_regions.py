"""Map each C1 edit region into the coordinates of the released (degraded) image.

manifest.jsonl stores `c1_region` in render coordinates (1012 x 638, before the
capture degradation). The degradation's geometry is a homography drawn first
from np.random.default_rng(degrade_seed), so it can be recomputed exactly and
applied to the region with the same box-mapping function the generator used.

Self-check: for the first --check persons, the documents are re-rendered and
their boxes mapped the same way. Boxes that do not depend on text layout (photo,
signature, QR placeholder) must equal the stored boxes EXACTLY; this verifies the
homography. Text boxes are reported for information only, because text layout
can differ by a few pixels between Pillow builds. Run with:

    .\\.venv-dataset\\Scripts\\python experiments\\e2_visual\\map_c1_regions.py

Writes experiments/e2_visual/c1_regions.csv (tracked).
"""

import argparse
import csv
import hashlib
import json
import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "dataset" / "src"))
from idforge import build as B                       # noqa: E402
from idforge import templates as TPL                 # noqa: E402
from idforge.degrade import PARAMS, _homography, _map_box   # noqa: E402
from idforge.forgery import apply_c1                 # noqa: E402
from idforge.records import make_records             # noqa: E402

MANIFEST_JSONL = ROOT / "dataset" / "data" / "v1" / "manifest.jsonl"
OUT = ROOT / "experiments" / "e2_visual" / "c1_regions.csv"


def homography(row):
    rng = np.random.default_rng(row["degrade_seed"])
    H, ow, oh = _homography(TPL.CARD_W, TPL.CARD_H, PARAMS[row["quality_tier"]], rng)
    if (ow, oh) != (row["width"], row["height"]):
        raise ValueError(f"{row['image_id']}: recomputed size {(ow, oh)} != "
                         f"stored {(row['width'], row['height'])}")
    return H, ow, oh


def self_check(rows, n_persons):
    cfg = dict(B.DEFAULT_CFG)
    cfg.update(B._read_cfg(str(ROOT / "dataset" / "configs" / "dataset_v1.yaml")))
    records = make_records(cfg["n_persons"], cfg["seed"], cfg)[:n_persons]
    fixed = {"photo", "signature", "qr_placeholder"}
    checked, max_diff, text_diff, region_diff = 0, 0, 0, 0
    for rec in records:
        for doc in ("aadhaar", "pan"):
            styles = TPL.AADHAAR_STYLES if doc == "aadhaar" else TPL.PAN_STYLES
            style = styles[rec.template_aadhaar if doc == "aadhaar" else rec.template_pan]
            fields = B.base_fields(rec, doc)
            seed = B._seed_for(cfg["seed"], rec.person_id, doc, "base")
            render = TPL.render_aadhaar if doc == "aadhaar" else TPL.render_pan
            img, boxes = render(dict(fields), style, seed=seed)
            vals = B.gt_text(fields, doc)
            vals["gender"] = ""
            _, prov = apply_c1(img, boxes, doc, vals, style, random.Random(seed ^ 0x9E37))
            for tier in ("clean", "mild", "severe"):
                row = rows[f"{rec.person_id}_{doc}_C1_{tier}"]
                region_diff = max(region_diff, max(abs(a - b) for a, b in
                                                   zip(prov["c1_region"], row["c1_region"])))
                H, ow, oh = homography(row)
                for k, b in boxes.items():
                    mapped = _map_box(H, b, ow, oh)
                    d = max(abs(p - q) for p, q in zip(mapped, row["boxes"][k]))
                    if k in fixed:
                        max_diff = max(max_diff, d)
                        checked += 1
                    else:
                        text_diff = max(text_diff, d)
    return checked, max_diff, text_diff, region_diff


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", type=int, default=25, help="persons to re-render for the self-check")
    ap.add_argument("--tolerance", type=int, default=0,
                    help="allowed px difference in the self-check (keep 0 unless told otherwise)")
    a = ap.parse_args()

    raw = MANIFEST_JSONL.read_bytes()
    rows = {}
    for line in raw.decode("utf-8").splitlines():
        r = json.loads(line)
        rows[r["image_id"]] = r
    if len(rows) != 10800:
        sys.exit(f"STOP: manifest.jsonl has {len(rows)} images, expected 10,800")

    checked, max_diff, text_diff, region_diff = self_check(rows, a.check)
    print(f"self-check: {checked} layout-independent boxes mapped, max difference {max_diff} px "
          f"(must be 0). For information: text boxes differ by up to {text_diff} px and "
          f"re-rendered C1 regions by up to {region_diff} px in this environment; the stored "
          f"c1_region values are used, not re-rendered ones.")
    if checked == 0 and a.check > 0:
        sys.exit("STOP: self-check found no layout-independent boxes.")
    if max_diff > a.tolerance:
        sys.exit("STOP: the homography does not reproduce the stored boxes exactly.")

    out = []
    for iid in sorted(rows):
        r = rows[iid]
        if r["forgery_category"] != "C1":
            continue
        H, ow, oh = homography(r)
        x0, y0, x1, y1 = _map_box(H, r["c1_region"], ow, oh)
        if not (x1 > x0 and y1 > y0):
            sys.exit(f"STOP: {iid}: empty mapped region {[x0, y0, x1, y1]}")
        out.append([iid, r["split"], r["doc_type"], r["c1_op"], r["c1_field"],
                    x0, y0, x1, y1, ow, oh])
    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["image_id", "split", "doc_type", "c1_op", "c1_field",
                    "x0", "y0", "x1", "y1", "image_width", "image_height"])
        w.writerows(out)
    print(f"PASS: wrote {len(out)} C1 regions to {OUT.relative_to(ROOT)}")
    print(f"manifest.jsonl sha256: {hashlib.sha256(raw).hexdigest()}")


if __name__ == "__main__":
    main()
