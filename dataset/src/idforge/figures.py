# -*- coding: utf-8 -*-
"""Paper figures generated directly from the released corpus.

Every figure is produced from files in the dataset directory, so a figure in the
paper can always be traced back to a specific image_id in the manifest.  Output
is PDF (vector text over embedded raster panels) for direct \\includegraphics.
"""
from __future__ import annotations

import json
import os
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle
from PIL import Image

plt.rcParams.update({
    "font.family": "serif", "font.serif": ["DejaVu Serif"],
    "font.size": 6.4, "axes.linewidth": 0.6,
    "pdf.fonttype": 42, "savefig.bbox": "tight", "savefig.pad_inches": 0.02,
})

CAT_TITLE = {
    "C0": "C0  unmodified control",
    "C1": "C1  pixel edit, values valid",
    "C2": "C2  structural fault",
    "C3": "C3  semantic fault",
    "C4": "C4  fabricated, valid",
}


def _load(out_dir):
    rows = [json.loads(l) for l in open(os.path.join(out_dir, "manifest.jsonl"))]
    return rows


def _panel(ax, path, box=None, title=None, sub=None):
    im = Image.open(path).convert("RGB")
    ax.imshow(np.asarray(im))
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_linewidth(0.5); s.set_color("#888")
    if box:
        x0, y0, x1, y1 = box
        ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False,
                               edgecolor="#d02020", linewidth=1.0))
    if title:
        ax.set_title(title, fontsize=5.6, pad=2.0)
    if sub:
        ax.set_xlabel(sub, fontsize=4.9, labelpad=1.2, color="#333")


# IEEE two-column geometry: 3.45 in for a single column, 7.16 in for figure*.
W_ONE, W_TWO = 3.45, 7.16


def _pick_person(rows):
    """Choose the record the specimen figure is drawn from.

    Preference is for a record whose C1 edit is one of the visible operations on
    a long field, and whose name is surname-last, so that the figure actually
    shows what each category does rather than an instance too small to see. This
    only selects which example is displayed; it changes nothing in the corpus.
    """
    VISIBLE = {"font_substitution": 2, "field_displacement": 2,
               "resample_patch": 1, "local_recompression": 1, "patch_splice": 0}
    LONG = {"aadhaar_number": 3, "pan_number": 3, "name": 2,
            "father_name": 2, "dob": 1, "gender": 1, "background": 0}
    best, best_score = None, -1
    by = defaultdict(dict)
    for r in rows:
        if r["forgery_category"] == "C1" and r["quality_tier"] == "clean":
            by[r["person_id"]][r["doc_type"]] = r
    for pid, d in by.items():
        if len(d) < 2:
            continue
        score = sum(VISIBLE.get(r.get("c1_op"), 0) + LONG.get(r.get("c1_field"), 0)
                    for r in d.values())
        if next(iter(d.values()))["naming_stratum"] == "surname_last":
            score += 2
        if score > best_score:
            best, best_score = pid, score
    return best or sorted({r["person_id"] for r in rows})[0]


def fig_specimens(out_dir, fig_dir, person=None, tier="clean"):
    rows = _load(out_dir)
    pid = person or _pick_person(rows)
    sel = defaultdict(dict)
    for r in rows:
        if r["person_id"] == pid and r["quality_tier"] == tier:
            if r["forgery_category"] == "C0" and r["control_index"] != 0:
                continue
            sel[r["doc_type"]][r["forgery_category"]] = r
    cats = ["C0", "C1", "C2", "C3", "C4"]
    fig, axes = plt.subplots(2, 5, figsize=(W_TWO, 2.75))
    ids = []
    for i, dt in enumerate(["aadhaar", "pan"]):
        for j, c in enumerate(cats):
            r = sel[dt].get(c)
            ax = axes[i][j]
            if r is None:
                ax.axis("off"); continue
            fld = r.get("c1_field") if c == "C1" else r.get("forgery_field")
            box = r["boxes"].get(fld) if fld else None
            sub = ""
            if c == "C1":
                sub = f"{r['c1_op'].replace('_', ' ')}\non '{r['c1_field']}'"
            elif r.get("forgery_field"):
                gv, fv = r.get("gt_value"), r.get("forged_value")
                if fld in ("aadhaar_number", "pan_number"):
                    sub = f"{gv}\n$\\rightarrow$ {fv}"
                else:
                    sub = "Devanagari name line\nreplaced"
            _panel(ax, os.path.join(out_dir, r["file"]), box,
                   CAT_TITLE[c] if i == 0 else None, sub)
            ids.append(r["image_id"])
        axes[i][0].set_ylabel("Aadhaar-format" if dt == "aadhaar" else "PAN-format",
                              fontsize=6.2)
    fig.subplots_adjust(wspace=0.04, hspace=0.36)
    p = os.path.join(fig_dir, "fig_specimens")
    fig.savefig(p + ".pdf"); fig.savefig(p + ".png", dpi=200)
    plt.close(fig)
    return {"figure": "fig_specimens", "person_id": pid, "tier": tier,
            "image_ids": ids}


def fig_quality_tiers(out_dir, fig_dir, person=None):
    rows = _load(out_dir)
    pid = person or sorted({r["person_id"] for r in rows})[0]
    fig, axes = plt.subplots(2, 3, figsize=(W_TWO, 3.1))
    ids = []
    for i, dt in enumerate(["aadhaar", "pan"]):
        for j, t in enumerate(["clean", "mild", "severe"]):
            r = next(r for r in rows if r["person_id"] == pid and r["doc_type"] == dt
                     and r["forgery_category"] == "C0" and r["control_index"] == 0
                     and r["quality_tier"] == t)
            _panel(axes[i][j], os.path.join(out_dir, r["file"]), None,
                   f"{t}  ({r['width']}$\\times${r['height']}, q={r['jpeg_q_capture']})")
            ids.append(r["image_id"])
        axes[i][0].set_ylabel("Aadhaar-format" if dt == "aadhaar" else "PAN-format",
                              fontsize=6.2)
    fig.subplots_adjust(wspace=0.05, hspace=0.25)
    p = os.path.join(fig_dir, "fig_quality_tiers")
    fig.savefig(p + ".pdf"); fig.savefig(p + ".png", dpi=200)
    plt.close(fig)
    return {"figure": "fig_quality_tiers", "person_id": pid, "image_ids": ids}


def fig_templates(out_dir, fig_dir):
    rows = _load(out_dir)
    fig, axes = plt.subplots(2, 3, figsize=(W_TWO, 3.1))
    ids = []
    for i, dt in enumerate(["aadhaar", "pan"]):
        for v in range(3):
            r = next((r for r in rows if r["doc_type"] == dt
                      and r["template_variant"] == v
                      and r["forgery_category"] == "C0"
                      and r["quality_tier"] == "clean"), None)
            if r is None:
                axes[i][v].axis("off"); continue
            _panel(axes[i][v], os.path.join(out_dir, r["file"]), None,
                   f"variant {v}")
            ids.append(r["image_id"])
        axes[i][0].set_ylabel("Aadhaar-format" if dt == "aadhaar" else "PAN-format",
                              fontsize=6.2)
    fig.subplots_adjust(wspace=0.05, hspace=0.25)
    p = os.path.join(fig_dir, "fig_templates")
    fig.savefig(p + ".pdf"); fig.savefig(p + ".png", dpi=200)
    plt.close(fig)
    return {"figure": "fig_templates", "image_ids": ids}


def fig_ocr_quality(stats, fig_dir):
    tiers = ["clean", "mild", "severe"]
    fields = [("aadhaar", "aadhaar_number"), ("aadhaar", "name"), ("aadhaar", "dob"),
              ("pan", "pan_number"), ("pan", "name"), ("pan", "father_name"),
              ("pan", "dob")]
    fig, ax = plt.subplots(figsize=(W_ONE, 2.15))
    w = 0.26
    x = np.arange(len(fields))
    colours = ["#3b6ea5", "#c8842a", "#9b3b3b"]
    for k, t in enumerate(tiers):
        vals, err = [], []
        for dt, fl in fields:
            v = stats["ocr"].get(f"{dt}/{fl}/{t}")
            vals.append(v["exact_match_pct"] if v else 0)
            err.append([vals[-1] - v["ci95"][0], v["ci95"][1] - vals[-1]] if v else [0, 0])
        err = np.array(err).T
        ax.bar(x + (k - 1) * w, vals, w, yerr=err, capsize=1.6, label=t,
               color=colours[k], edgecolor="none", error_kw={"lw": 0.6})
    ax.set_xticks(x)
    ax.set_xticklabels([f"{d[:1].upper()}:{f.replace('_number','').replace('_name','.name')}"
                        for d, f in fields], fontsize=5.4, rotation=30, ha="right")
    ax.set_ylabel("field exact-match (%)")
    ax.set_ylim(0, 104)
    ax.legend(frameon=False, fontsize=5.8, ncol=3, loc="lower center",
              bbox_to_anchor=(0.5, 1.0), handlelength=1.2, columnspacing=1.4)
    ax.grid(axis="y", lw=0.4, alpha=0.35)
    ax.set_axisbelow(True)
    p = os.path.join(fig_dir, "fig_ocr_quality")
    fig.savefig(p + ".pdf"); fig.savefig(p + ".png", dpi=200)
    plt.close(fig)
    return {"figure": "fig_ocr_quality"}


def fig_phash(stats, fig_dir):
    """The near-duplicate diagnostic: why a distance threshold cannot decide
    leakage on a corpus where every document shares one of six templates."""
    nd = stats["leakage"]["near_duplicate"]
    fig, ax = plt.subplots(figsize=(W_ONE, 1.95))
    labels = [("within_document", "same document,\ndifferent capture", "#3b6ea5"),
              ("same_person_other_document", "same person,\ndifferent document", "#c8842a"),
              ("cross_person_same_split", "different\npersons", "#7a4b8a")]
    for i, (k, lab, col) in enumerate(labels):
        s = nd[k]
        ax.barh(i, s["p1"] and (s["median"] - s["p1"]) or s["median"],
                left=s["p1"], height=0.42, color=col, alpha=0.85, edgecolor="none")
        ax.plot([s["min"], s["max"]], [i, i], color="#444", lw=0.8, zorder=1)
        ax.plot([s["median"]], [i], "o", color="#111", ms=3.2, zorder=3)
        ax.plot([s["min"], s["max"]], [i, i], "|", color="#444", ms=5, zorder=3)
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels([l for _, l, _ in labels], fontsize=5.6)
    ax.set_xlabel(f"perceptual-hash Hamming distance (bits of {nd['hash_bits']})",
                  fontsize=6.0)
    ax.set_xlim(0, nd["hash_bits"] * 0.65)
    auc = nd["separability_auc_within_vs_crossperson"]
    ov = 100 * nd["cross_person_pairs_closer_than_median_within_document"]
    ax.set_title(f"AUC {auc:.3f}; {ov:.1f}% of different-person pairs are\n"
                 f"closer than the median same-document pair", fontsize=5.8, pad=3)
    ax.grid(axis="x", lw=0.4, alpha=0.35)
    ax.set_axisbelow(True)
    p = os.path.join(fig_dir, "fig_phash_leakage")
    fig.savefig(p + ".pdf"); fig.savefig(p + ".png", dpi=200)
    plt.close(fig)
    return {"figure": "fig_phash_leakage"}


def build_all(out_dir: str) -> list:
    fig_dir = os.path.join(out_dir, "figures")
    os.makedirs(fig_dir, exist_ok=True)
    stats = json.load(open(os.path.join(out_dir, "stats", "dataset_stats.json")))
    prov = [fig_specimens(out_dir, fig_dir), fig_quality_tiers(out_dir, fig_dir),
            fig_templates(out_dir, fig_dir), fig_ocr_quality(stats, fig_dir),
            fig_phash(stats, fig_dir)]
    with open(os.path.join(fig_dir, "figure_provenance.json"), "w") as fh:
        json.dump(prov, fh, indent=1)
    return prov
