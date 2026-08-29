# -*- coding: utf-8 -*-
"""Forgery taxonomy C0-C4 (Section IV-E).

The design commitment that matters most for the experimental claim: categories
C2, C3 and C4 are produced by RE-RENDERING the document from a modified identity
record, not by editing a rendered image.  The resulting images therefore share
the fonts, antialiasing, guilloche phase and compression history of a genuine
render, and the only evidence distinguishing them from C0 is the CONTENT of the
fields.  Producing them by pixel editing would introduce a visual artefact, let
the visual branch detect them through that artefact, and invalidate the
incremental-value measurement RQ2 and RQ3 are designed to make.

C1 is the only category in which pixels are modified after rendering, and every
C1 operation is VALUE-PRESERVING: the printed strings are unchanged, so the rule
branch is expected to pass and only the visual branch has anything to detect.
"""
from __future__ import annotations

import io
import random
import string

import numpy as np
from PIL import Image, ImageDraw

from . import templates as T
from .identifiers import (break_aadhaar_checksum, break_pan_structure,
                          generate_aadhaar, generate_pan)

CATEGORIES = ("C0", "C1", "C2", "C3", "C4")
CATEGORY_DESC = {
    "C0": "unmodified render (control)",
    "C1": "post-render, value-preserving pixel edit",
    "C2": "re-render with a structurally invalid identifier",
    "C3": "re-render with a semantically inconsistent field pair",
    "C4": "re-render with a structurally valid but fabricated identifier",
}

C1_OPS = ("font_substitution", "field_displacement", "patch_splice",
          "local_recompression", "resample_patch")


# --------------------------------------------------------------------------
# C1: value-preserving pixel edits
# --------------------------------------------------------------------------

def _text_fields(doc_type: str) -> list:
    return (["name", "dob", "gender", "aadhaar_number"] if doc_type == "aadhaar"
            else ["pan_number", "name", "father_name", "dob"])


def apply_c1(img: Image.Image, boxes: dict, doc_type: str, values: dict,
             style, rng: random.Random) -> tuple:
    """Apply one value-preserving pixel edit.  Returns (image, provenance)."""
    op = rng.choice(C1_OPS)
    im = img.copy()
    fields = [f for f in _text_fields(doc_type) if f in boxes]
    field = rng.choice(fields)
    box = boxes[field]
    prov = {"c1_op": op, "c1_field": field, "c1_region": list(box)}

    if op == "font_substitution":
        # redraw the SAME string in a different family/weight at the same origin
        d = ImageDraw.Draw(im)
        bg = _local_bg(im, box)
        d.rectangle(box, fill=bg)
        alt = rng.choice(["dvsans_b", "serif_b", "carlito_b", "sans_b", "libmono_b"])
        txt = values.get(field, "")
        size = max(14, int((box[3] - box[1]) * 0.74))
        fnt = T.font(alt, size)
        org = (box[0] + 6, box[1] + 4)
        d.text(org, txt, font=fnt, fill=(18, 18, 22))
        nb = d.textbbox(org, txt, font=fnt)
        prov["c1_region"] = _union(box, [int(v) for v in nb])
        prov["c1_detail"] = alt

    elif op == "field_displacement":
        dx = rng.choice([-1, 1]) * rng.randint(5, 11)
        dy = rng.choice([-1, 1]) * rng.randint(3, 8)
        patch = im.crop(tuple(box))
        d = ImageDraw.Draw(im)
        d.rectangle(box, fill=_local_bg(im, box))
        im.paste(patch, (box[0] + dx, box[1] + dy))
        prov["c1_region"] = _union(box, [box[0] + dx, box[1] + dy,
                                         box[2] + dx, box[3] + dy])
        prov["c1_detail"] = f"dx={dx},dy={dy}"

    elif op == "patch_splice":
        # copy-move of a background region: no glyph is altered, so the printed
        # values are unchanged, but a duplicated region is introduced.
        w, h = im.size
        pw, ph = rng.randint(70, 150), rng.randint(40, 90)
        sx, sy = _blank_region(im, pw, ph, rng)
        tx, ty = _blank_region(im, pw, ph, rng)
        for _ in range(8):
            if abs(sx - tx) + abs(sy - ty) > 120:
                break
            tx, ty = _blank_region(im, pw, ph, rng)
        im.paste(im.crop((sx, sy, sx + pw, sy + ph)), (tx, ty))
        prov["c1_region"] = [tx, ty, tx + pw, ty + ph]
        prov["c1_detail"] = f"src=({sx},{sy})"
        prov["c1_field"] = "background"

    elif op == "local_recompression":
        pad = 12
        reg = (max(0, box[0] - pad), max(0, box[1] - pad),
               min(im.width, box[2] + pad), min(im.height, box[3] + pad))
        patch = im.crop(reg)
        buf = io.BytesIO()
        patch.save(buf, "JPEG", quality=rng.randint(18, 34))
        buf.seek(0)
        im.paste(Image.open(buf).convert("RGB"), (reg[0], reg[1]))
        prov["c1_region"] = list(reg)
        prov["c1_detail"] = "single-region low-quality recompression"

    else:  # resample_patch
        pad = 10
        reg = (max(0, box[0] - pad), max(0, box[1] - pad),
               min(im.width, box[2] + pad), min(im.height, box[3] + pad))
        patch = im.crop(reg)
        f = rng.choice([0.94, 0.96, 1.04, 1.07])
        rs = patch.resize((max(2, int(patch.width * f)), max(2, int(patch.height * f))),
                          Image.BICUBIC).resize(patch.size, Image.BICUBIC)
        im.paste(rs, (reg[0], reg[1]))
        prov["c1_region"] = list(reg)
        prov["c1_detail"] = f"rescale={f}"

    return im, prov


def _union(a, b):
    return [min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3])]


def _local_bg(im: Image.Image, box) -> tuple:
    """Median colour of a thin frame just outside `box`, used to erase cleanly."""
    x0, y0, x1, y1 = box
    pad = 6
    a = np.asarray(im.crop((max(0, x0 - pad), max(0, y0 - pad),
                            min(im.width, x1 + pad), min(im.height, y1 + pad))))
    if a.size == 0:
        return (250, 250, 248)
    ring = np.concatenate([a[:3].reshape(-1, 3), a[-3:].reshape(-1, 3),
                           a[:, :3].reshape(-1, 3), a[:, -3:].reshape(-1, 3)])
    return tuple(int(v) for v in np.median(ring, axis=0))


def _blank_region(im: Image.Image, pw: int, ph: int, rng: random.Random):
    """Pick a low-variance (text-free) location, so no glyph is overwritten."""
    w, h = im.size
    best, bestv = (10, 10), 1e18
    a = np.asarray(im.convert("L"), dtype=np.float32)
    for _ in range(14):
        x = rng.randint(4, max(5, w - pw - 4))
        y = rng.randint(4, max(5, h - ph - 4))
        v = float(a[y:y + ph, x:x + pw].std())
        if v < bestv:
            best, bestv = (x, y), v
    return best


# --------------------------------------------------------------------------
# C2 / C3 / C4: record modification, then re-render
# --------------------------------------------------------------------------

def modify_record_fields(base: dict, doc_type: str, category: str,
                         rec, rng: random.Random, deva_pool: list) -> tuple:
    """Return (modified render-field dict, provenance dict).

    `base` is the field dict that would produce C0.  Nothing outside the named
    field is touched, so the modified render differs from C0 only in the content
    of that field.
    """
    f = dict(base)
    prov = {"forgery_field": None, "forgery_detail": None,
            "gt_value": None, "forged_value": None}

    if category == "C2":
        if doc_type == "aadhaar":
            bad = break_aadhaar_checksum(rec.aadhaar, rng)
            prov.update(forgery_field="aadhaar_number", forgery_detail="verhoeff_break",
                        gt_value=rec.aadhaar, forged_value=bad)
            f["aadhaar"] = bad
        else:
            bad, kind = break_pan_structure(rec.pan, rng)
            prov.update(forgery_field="pan_number", forgery_detail=kind,
                        gt_value=rec.pan, forged_value=bad)
            f["pan"] = bad

    elif category == "C3":
        if doc_type == "pan":
            # p5 set to a letter matching no token initial of the printed name.
            from .validators import tokens
            init = {t[0].upper() for t in tokens(base["name_latin"])}
            cand = [c for c in string.ascii_uppercase if c not in init]
            new5 = rng.choice(cand)
            bad = rec.pan[:4] + new5 + rec.pan[5:]
            prov.update(forgery_field="pan_number",
                        forgery_detail=f"p5 {rec.pan[4]}->{new5}, name initials "
                                       f"{{{','.join(sorted(init))}}}",
                        gt_value=rec.pan, forged_value=bad)
            f["pan"] = bad
        else:
            # Aadhaar has no implemented cross-field rule (Table III).  The same
            # CLASS of corruption is injected anyway -- the Devanagari and Latin
            # renderings of the name are made to disagree -- so that RQ5 compares
            # like with like: PAN detects this class, Aadhaar cannot, and the
            # difference is attributable to validation capability rather than to
            # dataset design.  Expected rule-branch outcome: MISS.
            alt = rng.choice([d for d in deva_pool if d != rec.name_devanagari])
            prov.update(forgery_field="name_devanagari",
                        forgery_detail="script_mismatch (no implemented Aadhaar "
                                       "semantic rule; expected rule-branch miss)",
                        gt_value=rec.name_devanagari, forged_value=alt)
            f["name_devanagari"] = alt

    elif category == "C4":
        if doc_type == "aadhaar":
            new = generate_aadhaar(rng)
            while new == rec.aadhaar:
                new = generate_aadhaar(rng)
            prov.update(forgery_field="aadhaar_number",
                        forgery_detail="fabricated payload, valid check digit",
                        gt_value=rec.aadhaar, forged_value=new)
            f["aadhaar"] = new
        else:
            new = generate_pan(rng, "P", rec.pan_fifth)
            while new == rec.pan:
                new = generate_pan(rng, "P", rec.pan_fifth)
            prov.update(forgery_field="pan_number",
                        forgery_detail="fabricated identifier, valid format, "
                                       "category and cross-field consistency",
                        gt_value=rec.pan, forged_value=new)
            f["pan"] = new

    return f, prov


# Expected rule-branch outcome per (document type, category) on GROUND-TRUTH
# text.  Asserted during the build; any deviation is a generator defect, not an
# experimental result (Section IV-E).
EXPECTED_RULE = {
    ("aadhaar", "C0"): "PASS", ("aadhaar", "C1"): "PASS",
    ("aadhaar", "C2"): "FAIL", ("aadhaar", "C3"): "PASS",
    ("aadhaar", "C4"): "PASS",
    ("pan", "C0"): "PASS", ("pan", "C1"): "PASS",
    ("pan", "C2"): "FAIL", ("pan", "C3"): "FAIL",
    ("pan", "C4"): "PASS",
}
