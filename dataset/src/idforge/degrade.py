# -*- coding: utf-8 -*-
"""Built-in capture/print-scan degradation pipeline (Section IV-F).

Three quality tiers -- clean, mild, severe -- are applied to every rendered
document.  The pipeline is written against NumPy/OpenCV/Pillow only, so it has
no external dependency and reproduces bit-for-bit from a seed on any platform
with the same library versions.

Ordering matters and is fixed:
  geometry (single composed homography)  ->  illumination and shadow  ->
  optical blur  ->  moire  ->  sensor noise  ->  chromatic shift  ->  JPEG

Degradation is applied AFTER forgery injection, so a C1 pixel edit is subject
to exactly the same degradation as the surrounding document and cannot be
identified by the absence of capture artefacts.  The tier is drawn from an
identical distribution for every forgery category, so image quality cannot act
as a class-correlated cue.
"""
from __future__ import annotations

import io
import math

import cv2
import numpy as np
from PIL import Image

TIERS = ("clean", "mild", "severe")

PARAMS = {
    "clean":  dict(scale=(0.92, 1.00), persp=0.0020, rot=0.30, blur=(0.0, 0.5),
                   illum=0.05, shadow=0.00, moire=0.00, noise=(0.8, 2.0),
                   chroma=0.0, jpeg=(90, 96)),
    "mild":   dict(scale=(0.70, 0.90), persp=0.0110, rot=1.30, blur=(0.45, 0.95),
                   illum=0.16, shadow=0.10, moire=0.05, noise=(2.0, 4.5),
                   chroma=0.4, jpeg=(70, 86)),
    "severe": dict(scale=(0.50, 0.70), persp=0.0240, rot=2.50, blur=(0.80, 1.60),
                   illum=0.28, shadow=0.22, moire=0.12, noise=(3.5, 7.0),
                   chroma=1.0, jpeg=(45, 65)),
}


def _homography(w: int, h: int, p: dict, rng: np.random.Generator):
    s = rng.uniform(*p["scale"])
    ow, oh = int(round(w * s)), int(round(h * s))
    src = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
    j = p["persp"]
    dst = np.float32([
        [rng.uniform(0, j) * w,          rng.uniform(0, j) * h],
        [w - rng.uniform(0, j) * w,      rng.uniform(0, j) * h],
        [w - rng.uniform(0, j) * w,      h - rng.uniform(0, j) * h],
        [rng.uniform(0, j) * w,          h - rng.uniform(0, j) * h],
    ])
    Hp = cv2.getPerspectiveTransform(src, dst)
    th = math.radians(rng.uniform(-p["rot"], p["rot"]))
    c, sn = math.cos(th), math.sin(th)
    cx, cy = w / 2.0, h / 2.0
    R = np.array([[c, -sn, cx - c * cx + sn * cy],
                  [sn, c, cy - sn * cx - c * cy],
                  [0, 0, 1]], dtype=np.float64)
    S = np.array([[s, 0, 0], [0, s, 0], [0, 0, 1]], dtype=np.float64)
    return S @ R @ Hp, ow, oh


def _map_box(H: np.ndarray, box, ow: int, oh: int):
    x0, y0, x1, y1 = box
    pts = np.float32([[x0, y0], [x1, y0], [x1, y1], [x0, y1]]).reshape(-1, 1, 2)
    out = cv2.perspectiveTransform(pts, H).reshape(-1, 2)
    nx0, ny0 = out[:, 0].min(), out[:, 1].min()
    nx1, ny1 = out[:, 0].max(), out[:, 1].max()
    return [int(max(0, math.floor(nx0))), int(max(0, math.floor(ny0))),
            int(min(ow, math.ceil(nx1))), int(min(oh, math.ceil(ny1)))]


def degrade(img: Image.Image, tier: str, seed: int, boxes: dict | None = None):
    """Return (degraded PIL image, mapped boxes, applied-parameter record)."""
    assert tier in PARAMS, tier
    p = PARAMS[tier]
    rng = np.random.default_rng(seed)
    w, h = img.size
    a = np.asarray(img.convert("RGB"))[:, :, ::-1]        # to BGR for cv2

    H, ow, oh = _homography(w, h, p, rng)
    a = cv2.warpPerspective(a, H, (ow, oh), flags=cv2.INTER_AREA,
                            borderMode=cv2.BORDER_REPLICATE)
    a = a.astype(np.float32)

    rec = {"tier": tier, "out_w": ow, "out_h": oh}

    # illumination gradient
    if p["illum"] > 0:
        ang = rng.uniform(0, 2 * math.pi)
        yy, xx = np.mgrid[0:oh, 0:ow].astype(np.float32)
        g = (math.cos(ang) * (xx / ow - 0.5) + math.sin(ang) * (yy / oh - 0.5))
        a *= (1.0 + p["illum"] * g)[..., None]

    # cast shadow across part of the card
    if p["shadow"] > 0 and rng.random() < 0.65:
        ang = rng.uniform(0, 2 * math.pi)
        yy, xx = np.mgrid[0:oh, 0:ow].astype(np.float32)
        d = (math.cos(ang) * (xx / ow - rng.uniform(0.2, 0.8))
             + math.sin(ang) * (yy / oh - rng.uniform(0.2, 0.8)))
        m = 1.0 / (1.0 + np.exp(-d * rng.uniform(8, 22)))
        a *= (1.0 - p["shadow"] * m)[..., None]

    # optical blur (isotropic, occasionally motion)
    b = rng.uniform(*p["blur"])
    if b > 0.05:
        k = int(2 * round(3 * b) + 1)
        a = cv2.GaussianBlur(a, (k, k), b)
    if tier == "severe" and rng.random() < 0.25:
        L = int(rng.integers(5, 10))
        ker = np.zeros((L, L), np.float32)
        ker[L // 2, :] = 1.0 / L
        M = cv2.getRotationMatrix2D((L / 2 - 0.5, L / 2 - 0.5),
                                    float(rng.uniform(0, 180)), 1.0)
        ker = cv2.warpAffine(ker, M, (L, L))
        ker /= max(ker.sum(), 1e-6)
        a = cv2.filter2D(a, -1, ker)
        rec["motion_blur"] = L

    # moire / screen-rephotograph interference
    if p["moire"] > 0 and rng.random() < 0.55:
        yy, xx = np.mgrid[0:oh, 0:ow].astype(np.float32)
        f = rng.uniform(0.25, 0.85)
        th = rng.uniform(0, math.pi)
        m = np.sin(2 * math.pi * f * (xx * math.cos(th) + yy * math.sin(th)))
        a *= (1.0 + p["moire"] * m)[..., None]

    # sensor noise
    a += rng.normal(0, rng.uniform(*p["noise"]), a.shape)

    # chromatic shift
    if p["chroma"] > 0:
        sh = int(round(rng.uniform(0, p["chroma"])))
        if sh:
            a[:, :, 0] = np.roll(a[:, :, 0], sh, axis=1)
            a[:, :, 2] = np.roll(a[:, :, 2], -sh, axis=1)

    a = np.clip(a, 0, 255).astype(np.uint8)[:, :, ::-1]     # back to RGB
    out = Image.fromarray(a)

    q = int(rng.integers(p["jpeg"][0], p["jpeg"][1] + 1))
    buf = io.BytesIO()
    out.save(buf, "JPEG", quality=q, subsampling=2 if tier == "severe" else 0)
    jpeg_bytes = buf.getvalue()
    buf.seek(0)
    out = Image.open(buf).convert("RGB")
    out.load()
    rec["jpeg_q"] = q
    # The released file is exactly these bytes.  Writing them verbatim rather
    # than re-encoding the decoded array avoids adding a second, artificial
    # compression stage on top of the simulated capture compression, which would
    # both inflate storage and contaminate any double-compression cue the visual
    # branch might legitimately learn from category C1.
    rec["jpeg_bytes"] = jpeg_bytes

    nb = None
    if boxes is not None:
        nb = {k: _map_box(H, v, ow, oh) for k, v in boxes.items()}
    return out, nb, rec
