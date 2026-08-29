# -*- coding: utf-8 -*-
"""Card templates and renderer (Section IV-A).

Design commitments, all enforced here rather than checked afterwards:

* No official emblem, seal, hologram or authority name is reproduced.  A
  geometric placeholder mark and a fictitious authority name are used instead.
  The layouts are FORMAT-faithful (field set, field order, identifier grouping)
  and deliberately DESIGN-unfaithful.
* A low-opacity SYNTHETIC SPECIMEN overlay is composited onto every render
  BEFORE any forgery operation, and is drawn identically for every forgery
  category, so it cannot act as a class-correlated cue.
* Every drawn field returns its exact bounding box.  These boxes are the
  ground-truth crops used for per-field OCR in Section IV-G; obtaining them as
  a by-product of rendering is why the templates are authored rather than
  obtained.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from .photos import render_photo, render_signature
from .identifiers import format_aadhaar

CARD_W, CARD_H = 1012, 638

from .fontpaths import resolve as _resolve_fonts

FONTS = _resolve_fonts()

_font_cache: dict = {}


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    key = (name, size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(FONTS[name], size)
    return _font_cache[key]


@dataclass
class TemplateStyle:
    variant: int
    accent: tuple
    band_h: int
    paper: tuple
    latin: str
    latin_b: str
    deva: str
    number_font: str
    photo_left: bool
    label_above: bool
    guilloche_freq: float
    corner_r: int


AADHAAR_STYLES = [
    TemplateStyle(0, (28, 74, 122), 92, (250, 249, 245), "sans", "sans_b", "deva",
                  "mono_b", True, False, 1.00, 26),
    TemplateStyle(1, (122, 46, 42), 78, (247, 248, 250), "carlito", "carlito_b", "deva_s",
                  "libmono_b", False, True, 1.35, 18),
    TemplateStyle(2, (26, 92, 82), 104, (252, 250, 246), "serif", "serif_b", "deva",
                  "dvsans_b", True, True, 0.80, 34),
]

PAN_STYLES = [
    TemplateStyle(0, (18, 62, 108), 86, (249, 247, 240), "sans", "sans_b", "deva",
                  "libmono_b", False, False, 1.15, 22),
    TemplateStyle(1, (96, 66, 20), 70, (252, 251, 247), "carlito", "carlito_b", "deva_s",
                  "mono_b", True, True, 0.90, 30),
    TemplateStyle(2, (58, 44, 104), 96, (246, 248, 246), "serif", "serif_b", "deva",
                  "dvsans_b", False, True, 1.45, 16),
]


# --------------------------------------------------------------------------
# background
# --------------------------------------------------------------------------

def _guilloche(w: int, h: int, accent: tuple, paper: tuple, freq: float,
               seed: int) -> Image.Image:
    """A light interference pattern standing in for a security background."""
    rng = np.random.default_rng(seed)
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    x /= w
    y /= h
    ph = rng.uniform(0, 6.283, size=4)
    p = (np.sin(2 * math.pi * freq * (11 * x + 3 * y) + ph[0])
         + np.sin(2 * math.pi * freq * (7 * x - 9 * y) + ph[1])
         + 0.6 * np.sin(2 * math.pi * freq * (17 * x + 15 * y) + ph[2])
         + 0.4 * np.sin(2 * math.pi * freq * (23 * y) + ph[3]))
    p = (p - p.min()) / (np.ptp(p) + 1e-6)
    a = np.asarray(paper, dtype=np.float32)[None, None, :]
    b = np.asarray(accent, dtype=np.float32)[None, None, :]
    mix = (0.045 + 0.045 * p)[..., None]
    arr = a * (1 - mix) + b * mix
    # faint paper grain
    arr += rng.normal(0, 1.1, arr.shape)
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


def _placeholder_emblem(d: ImageDraw.ImageDraw, cx: int, cy: int, r: int,
                        colour: tuple) -> None:
    """A geometric mark that stands in for, and does not resemble, any official
    emblem."""
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=colour, width=max(2, r // 9))
    for k in range(6):
        a = k * math.pi / 3
        d.line([(cx + 0.30 * r * math.cos(a), cy + 0.30 * r * math.sin(a)),
                (cx + 0.78 * r * math.cos(a), cy + 0.78 * r * math.sin(a))],
               fill=colour, width=max(2, r // 10))
    d.ellipse([cx - r // 4, cy - r // 4, cx + r // 4, cy + r // 4], fill=colour)


_overlay_cache: dict = {}


def _specimen_layer(w: int, h: int, alpha: int) -> Image.Image:
    key = (w, h, alpha)
    if key in _overlay_cache:
        return _overlay_cache[key]
    layer = Image.new("RGBA", (w * 2, h * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    f = font("sans_b", 46)
    txt = "SYNTHETIC SPECIMEN  •  NOT A GOVERNMENT DOCUMENT  •  RESEARCH USE ONLY   "
    tw = d.textlength(txt, font=f)
    for row in range(-2, 8):
        d.text((-int(0.35 * tw) + (row % 2) * 120, row * 150), txt * 2,
               font=f, fill=(90, 90, 100, alpha))
    layer = layer.rotate(-24, resample=Image.BICUBIC, expand=False)
    layer = layer.crop((w // 2, h // 2, w // 2 + w, h // 2 + h))
    _overlay_cache[key] = layer
    return layer


def _specimen_overlay(im: Image.Image, alpha: int = 30) -> Image.Image:
    """Permanent, category-invariant SYNTHETIC SPECIMEN watermark.

    The layer is identical for every image, so it carries no information about
    document type, forgery category or quality tier."""
    w, h = im.size
    out = im.convert("RGBA")
    out.alpha_composite(_specimen_layer(w, h, alpha))
    return out.convert("RGB")


# --------------------------------------------------------------------------
# field drawing
# --------------------------------------------------------------------------

def _draw_value(d, xy, text, fnt, fill):
    x, y = xy
    d.text((x, y), text, font=fnt, fill=fill)
    l, t, r, b = d.textbbox((x, y), text, font=fnt)
    return [int(l), int(t), int(r), int(b)]


def _pad(box, px, py, w, h):
    return [max(0, int(box[0] - px)), max(0, int(box[1] - py)),
            min(w, int(box[2] + px)), min(h, int(box[3] + py))]


# --------------------------------------------------------------------------
# Aadhaar-format card
# --------------------------------------------------------------------------

def render_aadhaar(fields: dict, style: TemplateStyle, seed: int,
                   jitter: bool = False) -> tuple:
    """Render an Aadhaar-format specimen.

    `fields` supplies: name_latin, name_devanagari, dob, gender, aadhaar
    (12 digits, unformatted), photo_seed.
    Returns (PIL.Image, {field_name: [x0,y0,x1,y1]}).
    """
    import random as _r
    rng = _r.Random(seed)
    jx = (lambda: rng.randint(-3, 3)) if jitter else (lambda: 0)

    im = _guilloche(CARD_W, CARD_H, style.accent, style.paper,
                    style.guilloche_freq, seed)
    d = ImageDraw.Draw(im)
    ac = style.accent

    # header band
    d.rectangle([0, 0, CARD_W, style.band_h], fill=ac)
    _placeholder_emblem(d, 58, style.band_h // 2, style.band_h // 2 - 12,
                        (255, 255, 255))
    d.text((116, style.band_h // 2 - 32), "SPECIMEN IDENTITY AUTHORITY",
           font=font(style.latin_b, 30), fill=(255, 255, 255))
    d.text((116, style.band_h // 2 + 3), "नमूना पहचान प्राधिकरण  •  Aadhaar-format specimen",
           font=font(style.deva, 22), fill=(232, 236, 242))

    boxes = {}
    ph_w, ph_h = 208, 260
    top = style.band_h + 30
    if style.photo_left:
        ph_x, text_x = 40, 40 + ph_w + 34
    else:
        ph_x, text_x = CARD_W - 40 - ph_w, 40
    photo = render_photo(fields["photo_seed"], (ph_w, ph_h))
    im.paste(photo, (ph_x, top))
    d.rectangle([ph_x - 2, top - 2, ph_x + ph_w + 1, top + ph_h + 1],
                outline=(120, 120, 128), width=2)
    boxes["photo"] = [ph_x, top, ph_x + ph_w, top + ph_h]

    text_w = CARD_W - text_x - (ph_w + 74 if style.photo_left else 74)
    y = top - 4
    lab = font(style.latin, 21)
    labd = font(style.deva, 21)

    # name, Devanagari then Latin (as printed on the real document)
    # Vertical advances below are FIXED, never derived from the measured extent
    # of the text just drawn.  A layout that advanced by the glyph bounding box
    # would shift every field below a longer or taller name, and that reflow
    # would be a visual cue for the C3 script-mismatch category -- a rendering
    # artefact leaking the label.  See idforge.probe.exact_difference_audit.
    dfnt = font(style.deva, 33)
    b = _draw_value(d, (text_x, y), fields["name_devanagari"], dfnt, (24, 24, 28))
    boxes["name_devanagari"] = _pad(b, 6, 3, CARD_W, CARD_H)
    y += 55

    d.text((text_x, y), "Name / नाम", font=labd, fill=ac)
    y += 27
    b = _draw_value(d, (text_x + jx(), y), fields["name_latin"],
                    font(style.latin_b, 35), (18, 18, 22))
    boxes["name"] = _pad(b, 8, 3, CARD_W, CARD_H)
    y += 66

    # DOB
    if style.label_above:
        d.text((text_x, y), "Date of Birth / जन्म तिथि", font=labd, fill=ac)
        y += 26
        b = _draw_value(d, (text_x + jx(), y), fields["dob"],
                        font(style.latin_b, 31), (18, 18, 22))
    else:
        d.text((text_x, y + 4), "DOB / जन्म तिथि :", font=labd, fill=ac)
        off = int(d.textlength("DOB / जन्म तिथि :", font=labd)) + 14
        b = _draw_value(d, (text_x + off + jx(), y), fields["dob"],
                        font(style.latin_b, 31), (18, 18, 22))
    boxes["dob"] = _pad(b, 8, 3, CARD_W, CARD_H)
    y += (26 + 47) if style.label_above else 47

    # gender
    gtext = "MALE / पुरुष" if fields["gender"] == "M" else "FEMALE / महिला"
    if style.label_above:
        d.text((text_x, y), "Gender / लिंग", font=labd, fill=ac)
        y += 26
        b = _draw_value(d, (text_x + jx(), y), gtext, font(style.deva, 31), (18, 18, 22))
    else:
        d.text((text_x, y + 4), "Gender / लिंग :", font=labd, fill=ac)
        off = int(d.textlength("Gender / लिंग :", font=labd)) + 14
        b = _draw_value(d, (text_x + off + jx(), y), gtext, font(style.deva, 31),
                        (18, 18, 22))
    boxes["gender"] = _pad(b, 8, 3, CARD_W, CARD_H)

    # number strip
    strip_h = 96
    d.rectangle([0, CARD_H - strip_h, CARD_W, CARD_H], fill=(255, 255, 255))
    d.line([(0, CARD_H - strip_h), (CARD_W, CARD_H - strip_h)], fill=ac, width=3)
    num = format_aadhaar(fields["aadhaar"])
    nf = font(style.number_font, 52)
    nw = d.textlength(num, font=nf)
    nx = int((CARD_W - nw) / 2) + jx()
    b = _draw_value(d, (nx, CARD_H - strip_h + 22), num, nf, (16, 16, 20))
    boxes["aadhaar_number"] = _pad(b, 12, 6, CARD_W, CARD_H)

    # QR-like placeholder block (not an encoding of anything)
    qr = _fake_qr(seed, 118)
    qx, qy = CARD_W - 150, CARD_H - strip_h - 148
    im.paste(qr, (qx, qy))
    boxes["qr_placeholder"] = [qx, qy, qx + 118, qy + 118]

    im = _round_corners(im, style.corner_r)
    im = _specimen_overlay(im)
    return im, boxes


def _fake_qr(seed: int, n: int) -> Image.Image:
    """A random binary block occupying the QR position.  It encodes nothing and
    is not scannable; it exists so the layout has the right visual mass."""
    rng = np.random.default_rng(seed ^ 0xA1B2)
    g = (rng.random((21, 21)) < 0.5).astype(np.uint8) * 255
    g[:7, :7] = 0; g[1:6, 1:6] = 255; g[2:5, 2:5] = 0
    g[:7, -7:] = 0; g[1:6, -6:-1] = 255; g[2:5, -5:-2] = 0
    g[-7:, :7] = 0; g[-6:-1, 1:6] = 255; g[-5:-2, 2:5] = 0
    im = Image.fromarray(255 - g).convert("RGB").resize((n, n), Image.NEAREST)
    return im


def _round_corners(im: Image.Image, r: int) -> Image.Image:
    if r <= 0:
        return im
    w, h = im.size
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, w - 1, h - 1], radius=r, fill=255)
    out = Image.new("RGB", (w, h), (255, 255, 255))
    out.paste(im, (0, 0), mask)
    return out


# --------------------------------------------------------------------------
# PAN-format card
# --------------------------------------------------------------------------

def render_pan(fields: dict, style: TemplateStyle, seed: int,
               jitter: bool = False) -> tuple:
    """Render a PAN-format specimen.

    `fields`: pan, name_latin, father_name_latin, dob, photo_seed.
    """
    import random as _r
    rng = _r.Random(seed)
    jx = (lambda: rng.randint(-3, 3)) if jitter else (lambda: 0)

    im = _guilloche(CARD_W, CARD_H, style.accent, style.paper,
                    style.guilloche_freq, seed)
    d = ImageDraw.Draw(im)
    ac = style.accent

    d.rectangle([0, 0, CARD_W, style.band_h], fill=ac)
    _placeholder_emblem(d, 56, style.band_h // 2, style.band_h // 2 - 10,
                        (255, 255, 255))
    d.text((112, style.band_h // 2 - 30), "SPECIMEN TAX IDENTIFICATION AUTHORITY",
           font=font(style.latin_b, 27), fill=(255, 255, 255))
    d.text((112, style.band_h // 2 + 2), "नमूना कर पहचान प्राधिकरण  •  PAN-format specimen",
           font=font(style.deva, 21), fill=(230, 234, 240))

    boxes = {}
    ph_w, ph_h = 190, 238
    top = style.band_h + 126
    if style.photo_left:
        ph_x, text_x = 42, 42 + ph_w + 30
    else:
        ph_x, text_x = CARD_W - 42 - ph_w, 42
    photo = render_photo(fields["photo_seed"], (ph_w, ph_h))
    im.paste(photo, (ph_x, top))
    d.rectangle([ph_x - 2, top - 2, ph_x + ph_w + 1, top + ph_h + 1],
                outline=(120, 120, 128), width=2)
    boxes["photo"] = [ph_x, top, ph_x + ph_w, top + ph_h]

    # PAN number is printed prominently under the band
    y = style.band_h + 12
    d.text((42, y), "Permanent Account Number", font=font(style.latin, 24), fill=ac)
    nf = font(style.number_font, 54)
    b = _draw_value(d, (42 + jx(), y + 28), fields["pan"], nf, (16, 16, 20))
    boxes["pan_number"] = _pad(b, 12, 5, CARD_W, CARD_H)

    lab = font(style.latin, 22)
    labd = font(style.deva, 22)
    y = top - 2

    def row(key, label, value, fsize=31):
        nonlocal y
        if style.label_above:
            d.text((text_x, y), label, font=labd, fill=ac)
            y += 26
            bb = _draw_value(d, (text_x + jx(), y), value,
                             font(style.latin_b, fsize), (18, 18, 22))
        else:
            d.text((text_x, y + 4), label + " :", font=labd, fill=ac)
            off = int(d.textlength(label + " :", font=labd)) + 12
            bb = _draw_value(d, (text_x + off + jx(), y), value,
                             font(style.latin_b, fsize), (18, 18, 22))
        boxes[key] = _pad(bb, 8, 3, CARD_W, CARD_H)
        y += (26 + fsize + 20) if style.label_above else (fsize + 20)

    row("name", "Name / नाम", fields["name_latin"])
    row("father_name", "Father's Name / पिता का नाम", fields["father_name_latin"], 29)
    row("dob", "Date of Birth / जन्म तिथि", fields["dob"], 29)

    # signature strip
    sig_w, sig_h = 300, 88
    sx = text_x
    sy = min(CARD_H - sig_h - 52, y + 6)
    im.paste(render_signature(fields["photo_seed"], (sig_w, sig_h)), (sx, sy))
    d.line([(sx, sy + sig_h + 2), (sx + sig_w, sy + sig_h + 2)],
           fill=(120, 120, 128), width=2)
    d.text((sx, sy + sig_h + 8), "Signature / हस्ताक्षर", font=font(style.deva, 19),
           fill=(90, 90, 98))
    boxes["signature"] = [sx, sy, sx + sig_w, sy + sig_h]

    im = _round_corners(im, style.corner_r)
    im = _specimen_overlay(im)
    return im, boxes
