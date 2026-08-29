# -*- coding: utf-8 -*-
"""Procedural synthetic portrait placeholders (Section IV-C).

No real photograph, and no generative face model, is used anywhere in this
dataset.  Each placeholder is a deterministic procedural drawing seeded by the
person identifier.  The placeholder occupies the photograph slot so that the
card layout is complete and the visual branch sees a realistic amount of
non-text image content, but it is not a face and no biometric claim is made.

The photograph chain is deliberately identical across forgery categories, so
the photograph cannot act as a class-correlated cue.
"""
from __future__ import annotations

import math
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

SKIN = [(232, 197, 168), (216, 176, 145), (196, 152, 118), (172, 128, 96),
        (146, 105, 78), (120, 86, 64)]
HAIR = [(28, 24, 22), (44, 32, 26), (62, 44, 32), (90, 70, 52), (140, 140, 142)]
GARMENT = [(46, 62, 92), (92, 46, 52), (58, 84, 66), (120, 108, 76), (48, 48, 54),
           (140, 62, 92), (70, 70, 120), (150, 120, 60)]
BACKDROP = [(228, 232, 238), (222, 226, 220), (236, 230, 222), (214, 220, 228),
            (240, 240, 240), (206, 214, 210)]


def render_photo(seed: int, size=(240, 300)) -> Image.Image:
    rng = random.Random(seed)
    w, h = size
    ss = 2                                   # supersample for smooth edges
    W, H = w * ss, h * ss
    base = rng.choice(BACKDROP)
    im = Image.new("RGB", (W, H), base)
    d = ImageDraw.Draw(im)

    # backdrop vignette
    grad = np.linspace(1.06, 0.88, H, dtype=np.float32)[:, None]
    arr = np.asarray(im, dtype=np.float32) * grad[..., None]
    im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(im)

    skin = rng.choice(SKIN)
    hair = rng.choice(HAIR)
    garment = rng.choice(GARMENT)

    cx = W // 2 + rng.randint(-int(0.03 * W), int(0.03 * W))
    head_w = int(W * rng.uniform(0.44, 0.52))
    head_h = int(head_w * rng.uniform(1.22, 1.34))
    head_cy = int(H * rng.uniform(0.40, 0.45))

    # shoulders / garment
    sh_top = head_cy + head_h // 2 - int(0.02 * H)
    sh_w = int(W * rng.uniform(0.92, 1.12))
    d.ellipse([cx - sh_w // 2, sh_top, cx + sh_w // 2, sh_top + int(H * 0.90)],
              fill=garment)
    # neck
    d.rounded_rectangle(
        [cx - head_w // 6, head_cy + head_h // 3, cx + head_w // 6, sh_top + int(0.05 * H)],
        radius=int(0.02 * W), fill=tuple(max(0, c - 18) for c in skin))

    # head
    d.ellipse([cx - head_w // 2, head_cy - head_h // 2,
               cx + head_w // 2, head_cy + head_h // 2], fill=skin)
    # ears
    er = int(head_w * 0.10)
    for sx in (-1, 1):
        d.ellipse([cx + sx * head_w // 2 - er, head_cy - er,
                   cx + sx * head_w // 2 + er, head_cy + er], fill=skin)

    # hair
    style = rng.randrange(3)
    top = head_cy - head_h // 2
    if style == 0:                                   # short
        d.chord([cx - head_w // 2 - 2, top - int(0.02 * H),
                 cx + head_w // 2 + 2, head_cy], 180, 360, fill=hair)
    elif style == 1:                                 # longer, framing
        d.ellipse([cx - head_w // 2 - int(0.03 * W), top - int(0.03 * H),
                   cx + head_w // 2 + int(0.03 * W), head_cy + int(head_h * 0.55)],
                  fill=hair)
        d.ellipse([cx - head_w // 2 + int(0.02 * W), top + int(head_h * 0.16),
                   cx + head_w // 2 - int(0.02 * W), head_cy + head_h // 2], fill=skin)
    else:                                            # receded
        d.chord([cx - head_w // 2, top + int(0.03 * H),
                 cx + head_w // 2, head_cy - int(head_h * 0.10)], 180, 360, fill=hair)

    # features
    eye_y = head_cy - int(head_h * 0.06)
    eye_dx = int(head_w * 0.19)
    eye_w = int(head_w * 0.115)
    eye_h = int(head_h * 0.048)
    for sx in (-1, 1):
        ex = cx + sx * eye_dx
        d.ellipse([ex - eye_w, eye_y - eye_h, ex + eye_w, eye_y + eye_h],
                  fill=(250, 248, 245))
        d.ellipse([ex - eye_h, eye_y - eye_h, ex + eye_h, eye_y + eye_h],
                  fill=(52, 40, 34))
        d.arc([ex - eye_w, eye_y - int(eye_h * 3.1), ex + eye_w, eye_y - int(eye_h * 0.2)],
              200, 340, fill=hair, width=max(1, int(0.006 * W)))
    # nose
    d.line([(cx, eye_y + int(head_h * 0.04)), (cx - int(head_w * 0.03), head_cy + int(head_h * 0.16))],
           fill=tuple(max(0, c - 34) for c in skin), width=max(1, int(0.008 * W)))
    # mouth
    mw = int(head_w * 0.17)
    d.arc([cx - mw, head_cy + int(head_h * 0.20), cx + mw, head_cy + int(head_h * 0.34)],
          10, 170, fill=(150, 92, 88), width=max(1, int(0.010 * W)))

    im = im.resize((w, h), Image.LANCZOS)
    im = im.filter(ImageFilter.GaussianBlur(rng.uniform(0.2, 0.6)))
    # mild photographic sensor noise
    a = np.asarray(im, dtype=np.float32)
    a += np.random.default_rng(seed).normal(0, rng.uniform(1.2, 3.0), a.shape)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def render_signature(seed: int, size=(300, 90)) -> Image.Image:
    """A procedural ink stroke for the PAN signature strip."""
    rng = random.Random(seed ^ 0x5EED)
    w, h = size
    ss = 2
    im = Image.new("RGB", (w * ss, h * ss), (255, 255, 255))
    d = ImageDraw.Draw(im)
    x = int(0.06 * w * ss)
    y0 = int(0.62 * h * ss)
    pts = []
    phase = rng.uniform(0, 6.28)
    amp = rng.uniform(0.16, 0.28) * h * ss
    freq = rng.uniform(2.2, 4.0)
    n = 220
    for i in range(n):
        t = i / (n - 1)
        px = x + t * (0.88 * w * ss)
        py = y0 - amp * math.sin(phase + freq * 6.28 * t) * (1 - 0.5 * t) \
             - rng.uniform(-2, 2) * ss
        pts.append((px, py))
    d.line(pts, fill=(18, 24, 92), width=max(2, int(0.020 * h * ss)), joint="curve")
    d.line([(x, y0 + int(0.16 * h * ss)), (x + int(0.30 * w * ss), y0 - int(0.22 * h * ss))],
           fill=(18, 24, 92), width=max(2, int(0.016 * h * ss)))
    im = im.resize((w, h), Image.LANCZOS)
    return im
