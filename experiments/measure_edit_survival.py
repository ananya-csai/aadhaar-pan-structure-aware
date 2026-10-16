"""How much of each C1 pixel edit survives degradation + resizing?

For a person, C0 control 0 and C1 are rendered from the SAME base seed
(build.py, render-seed policy), so before degradation they differ only inside
the edited region. Here both are degraded with the SAME degradation seed, so the
pair still differs only by the edit. Then both are resized with the cache
policy (aspect-preserving LANCZOS + white pad) to each candidate canvas.

Metric (per pair, per canvas), inside the mapped edit region, on luma:
    retention = mean((C1 - C0)^2) at canvas / mean((C1 - C0)^2) at native size
A uniform change keeps retention ~1 under resizing; fine high-frequency
evidence (block artefacts, resampling traces) drops toward 0. As a reference,
the same ratio is computed for i.i.d. Gaussian noise, which is the most
fragile signal possible.

Retention is an UPPER BOUND on usable evidence: the detector never sees the
reference C0. Low retention means the evidence is gone; high retention means it
is present, not that a model will find it.

Uses TRAIN-split persons only. Run from the repository root:
    python experiments/measure_edit_survival.py --persons 60
"""

import argparse
import csv
import random
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "dataset" / "src"))

from idforge import build as B                      # noqa: E402
from idforge import templates as TPL                # noqa: E402
from idforge.degrade import degrade                 # noqa: E402
from idforge.forgery import apply_c1                # noqa: E402
from idforge.records import make_records            # noqa: E402
from idforge.splits import assign_splits            # noqa: E402

CANVASES = {"native": None, "1024x640": (1024, 640), "768x512": (768, 512),
            "384x256": (384, 256), "224x160": (224, 160)}


def resize_pad(img, tw, th):
    """Identical policy to experiments/build_resize_cache.py."""
    w, h = img.size
    s = min(tw / w, th / h)
    nw, nh = max(1, round(w * s)), max(1, round(h * s))
    r = img.resize((nw, nh), Image.Resampling.LANCZOS)
    c = Image.new("RGB", (tw, th), (255, 255, 255))
    ox, oy = (tw - nw) // 2, (th - nh) // 2
    c.paste(r, (ox, oy))
    return c, s, ox, oy


def luma(img):
    return np.asarray(img.convert("L"), dtype=np.float64)


def region_energy(a, b, box):
    x0, y0, x1, y1 = box
    x0, y0 = max(0, x0), max(0, y0)
    x1, y1 = max(x0 + 1, x1), max(y0 + 1, y1)
    d = a[y0:y1, x0:x1] - b[y0:y1, x0:x1]
    return float(np.mean(d ** 2))


def scaled_box(box, s, ox, oy):
    x0, y0, x1, y1 = box
    return [int(np.floor(x0 * s)) + ox, int(np.floor(y0 * s)) + oy,
            int(np.ceil(x1 * s)) + ox, int(np.ceil(y1 * s)) + oy]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--persons", type=int, default=60)
    ap.add_argument("--out", default="experiments/edit_survival")
    a = ap.parse_args()

    cfg = dict(B.DEFAULT_CFG)
    cfg.update(B._read_cfg(str(ROOT / "dataset" / "configs" / "dataset_v1.yaml")))
    records = make_records(cfg["n_persons"], cfg["seed"], cfg)
    splits = assign_splits(records, cfg["seed"] ^ 0x51D)
    train = [r for r in records if splits[r.person_id] == "train"][: a.persons]
    gseed = cfg["seed"]

    rows = []
    for rec in train:
        for doc_type in ("aadhaar", "pan"):
            styles = TPL.AADHAAR_STYLES if doc_type == "aadhaar" else TPL.PAN_STYLES
            tv = rec.template_aadhaar if doc_type == "aadhaar" else rec.template_pan
            style = styles[tv]
            fields = B.base_fields(rec, doc_type)
            base_seed = B._seed_for(gseed, rec.person_id, doc_type, "base")
            render = TPL.render_aadhaar if doc_type == "aadhaar" else TPL.render_pan

            c0, boxes = render(dict(fields), style, seed=base_seed)
            c1_src, _ = render(dict(fields), style, seed=base_seed)
            vals = B.gt_text(fields, doc_type)
            vals["gender"] = ""
            frng = random.Random(base_seed ^ 0x9E37)          # same as build.py
            c1, prov = apply_c1(c1_src, boxes, doc_type, vals, style, frng)

            for tier in cfg["tiers"]:
                dseed = B._seed_for(gseed, rec.person_id, doc_type, "C1", 0, tier)
                d0, _, _ = degrade(c0, tier, dseed, {"edit": prov["c1_region"]})
                d1, nb, _ = degrade(c1, tier, dseed, {"edit": prov["c1_region"]})
                ebox = nb["edit"]
                row = {"person_id": rec.person_id, "doc_type": doc_type,
                       "tier": tier, "c1_op": prov["c1_op"],
                       "c1_field": prov["c1_field"],
                       "native_w": d0.width, "native_h": d0.height,
                       "edit_w": ebox[2] - ebox[0], "edit_h": ebox[3] - ebox[1]}
                e_native = region_energy(luma(d1), luma(d0), ebox)
                row["energy_native"] = e_native
                rng = np.random.default_rng(dseed)
                noise = Image.fromarray(np.clip(128 + rng.normal(0, 20, (d0.height, d0.width, 3)),
                                                0, 255).astype(np.uint8))
                grey = Image.new("RGB", d0.size, (128, 128, 128))
                n_native = region_energy(luma(noise), luma(grey), ebox)
                for name, wh in CANVASES.items():
                    if wh is None:
                        continue
                    r0, s, ox, oy = resize_pad(d0, *wh)
                    r1, _, _, _ = resize_pad(d1, *wh)
                    rb = scaled_box(ebox, s, ox, oy)
                    e = region_energy(luma(r1), luma(r0), rb)
                    rn, _, _, _ = resize_pad(noise, *wh)
                    rg, _, _, _ = resize_pad(grey, *wh)
                    row[f"ret_{name}"] = e / e_native if e_native > 0 else float("nan")
                    row[f"noise_ret_{name}"] = region_energy(luma(rn), luma(rg), rb) / n_native
                rows.append(row)

    out = ROOT / a.out
    out.mkdir(parents=True, exist_ok=True)
    with (out / "pairs.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)

    names = [n for n in CANVASES if n != "native"]
    groups = defaultdict(list)
    for r in rows:
        groups[r["c1_op"]].append(r)
    lines = ["| C1 operation | pairs | " + " | ".join(names) + " |",
             "|---|---|" + "---|" * len(names)]
    for op in sorted(groups):
        g = groups[op]
        med = [np.nanmedian([r[f"ret_{n}"] for r in g]) for n in names]
        lines.append(f"| {op} | {len(g)} | " + " | ".join(f"{m:.2f}" for m in med) + " |")
    nmed = [np.median([r[f"noise_ret_{n}"] for r in rows]) for n in names]
    lines.append("| *reference: white noise* | | " + " | ".join(f"{m:.2f}" for m in nmed) + " |")
    by_tier = defaultdict(list)
    for r in rows:
        by_tier[(r["c1_op"], r["tier"])].append(r["ret_384x256"])
    lines += ["", "Median retention at 384x256 by tier:", "",
              "| C1 operation | clean | mild | severe |", "|---|---|---|---|"]
    for op in sorted(groups):
        lines.append(f"| {op} | " + " | ".join(
            f"{np.nanmedian(by_tier[(op, t)]):.2f}" for t in ("clean", "mild", "severe")) + " |")
    table = "\n".join(lines)
    import platform
    import cv2
    import PIL
    env = (f"python {platform.python_version()}, numpy {np.__version__}, "
           f"pillow {PIL.__version__}, opencv {cv2.__version__}, {platform.platform()}")
    (out / "summary.md").write_text(
        f"Environment: {env}\n\n"
        f"Persons (train split): {len(train)}; pairs: {len(rows)}\n\n"
        "Median retention of edit energy relative to native size (1.0 = fully kept).\n\n"
        + table + "\n", encoding="utf-8")
    print(table)


if __name__ == "__main__":
    main()
