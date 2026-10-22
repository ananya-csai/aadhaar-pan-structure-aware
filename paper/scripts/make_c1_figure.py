"""Render the five C1 pixel-edit operations for the record shown in Fig. 4.

Uses the released generator (dataset/src/idforge) unchanged: the identity record
P000000 is regenerated from the frozen seed, rendered with its own template and
render seed, and each C1 operation is applied to the PAN number with the
generator's own apply_c1(). Output: figures/fig_c1_ops.pdf (pre-capture crops,
edited crops and amplified absolute differences).
"""
import random
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

REPO = sys.argv[1]
OUT = sys.argv[2]
sys.path.insert(0, f"{REPO}/dataset/src")
from idforge import templates as TPL                      # noqa: E402
from idforge.build import DEFAULT_CFG, _seed_for, base_fields, gt_text  # noqa: E402
from idforge.forgery import apply_c1                       # noqa: E402
from idforge.records import make_records                   # noqa: E402

cfg = dict(DEFAULT_CFG)
rec = make_records(1, cfg["seed"], cfg)[0]
assert rec.person_id == "P000000" and rec.pan == "TNZPK5344W", (rec.person_id, rec.pan)
style = TPL.PAN_STYLES[rec.template_pan]
bf = base_fields(rec, "pan")
seed = _seed_for(cfg["seed"], rec.person_id, "pan", "base")
base, boxes = TPL.render_pan(bf, style, seed=seed)
base_a = np.asarray(base.convert("RGB")).astype(np.int16)


class Forced(random.Random):
    """random.Random whose first choice() calls return fixed values."""
    def __init__(self, seed, forced):
        super().__init__(seed)
        self.forced = list(forced)

    def choice(self, seq):
        if self.forced:
            v = self.forced.pop(0)
            assert v in seq, (v, seq)
            return v
        return super().choice(seq)


OPS = [("font_substitution", "font substitution", "coarse"),
       ("field_displacement", "field displacement", "coarse"),
       ("patch_splice", "patch splice", "coarse"),
       ("local_recompression", "local recompression", "fine-trace"),
       ("resample_patch", "patch resampling", "fine-trace")]

vals = gt_text(bf, "pan")
vals["gender"] = ""
panels = []
for k, (op, title, group) in enumerate(OPS):
    rng = Forced(seed ^ 0x9E37 ^ (k + 1), [op, "pan_number"])
    im, prov = apply_c1(base, boxes, "pan", vals, style, rng)
    rx0, ry0, rx1, ry1 = prov["c1_region"]
    W, H = 500, 132                       # one fixed window for every panel
    cx, cy = (rx0 + rx1) // 2, (ry0 + ry1) // 2
    x0 = min(max(0, cx - W // 2), base.width - W)
    y0 = min(max(0, cy - H // 2), base.height - H)
    x1, y1 = x0 + W, y0 + H
    a = np.asarray(im.convert("RGB")).astype(np.int16)
    crop0 = base_a[y0:y1, x0:x1].astype(np.uint8)
    crop1 = a[y0:y1, x0:x1].astype(np.uint8)
    diff = np.abs(a - base_a).sum(axis=2)[y0:y1, x0:x1]
    changed = int((np.abs(a - base_a).sum(axis=2) > 0).sum())
    panels.append((title, group, crop0, crop1, diff, prov.get("c1_detail", ""), changed))
    print(op, prov["c1_region"], prov.get("c1_detail"), "changed px:", changed)

plt.rcParams.update({"font.family": "serif", "font.size": 6.5})
fig, axes = plt.subplots(5, 3, figsize=(3.4, 2.05),
                         gridspec_kw=dict(wspace=0.04, hspace=0.07))
vmax = 120
for i, (title, group, c0, c1, d, detail, changed) in enumerate(panels):
    axes[i, 0].imshow(c0)
    axes[i, 1].imshow(c1)
    axes[i, 2].imshow(np.clip(d, 0, vmax), cmap="magma", vmin=0, vmax=vmax)
    colour = "#2F6DB5" if group == "coarse" else "#C0392B"
    axes[i, 0].set_ylabel(title.replace(" ", "\n", 1), fontsize=6.3, color=colour,
                          rotation=0, ha="right", va="center", labelpad=3)
    for j in range(3):
        axes[i, j].set_xticks([]); axes[i, j].set_yticks([])
        for s in axes[i, j].spines.values():
            s.set_linewidth(0.4); s.set_color("#888888")
for j, lab in enumerate(["original", "edited", r"$|\Delta|$ (amplified)"]):
    axes[0, j].set_title(lab, fontsize=6.8, pad=2.5)
fig.savefig(OUT, bbox_inches="tight", pad_inches=0.02, dpi=300)
print("wrote", OUT)
