# -*- coding: utf-8 -*-
"""Per-field OCR extraction (Section IV-G).

Fields are cropped to the ground-truth bounding boxes recorded at render time
and mapped through the degradation homography, then read individually with
Tesseract [18] under a character whitelist appropriate to the field type.

Raw extraction output is stored without correction.  A minimal, explicitly
documented PARSING step is applied before the validators see the string:

  aadhaar_number : all whitespace removed (the card prints 4-4-4 groups)
  pan_number     : all whitespace removed, upper-cased
  name fields    : leading/trailing whitespace removed, internal runs collapsed

Nothing else is done.  In particular no character substitution, dictionary
lookup, checksum-guided repair or confidence-based rejection is applied,
because the gap between validator behaviour on ground-truth text and on this
output IS the RQ4 measurement, and repairing the output would destroy it.

Tesseract is invoked in list mode (one process per field type per chunk) rather
than once per crop; this is a speed optimisation only and does not change the
per-crop result.
"""
from __future__ import annotations

import os
import re
import subprocess
import tempfile

import cv2
import numpy as np
from PIL import Image

# field -> (tesseract psm, whitelist)
FIELD_CFG = {
    "aadhaar_number": ("7", "0123456789 "),
    "pan_number":     ("7", "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"),
    "name":           ("7", "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                            "abcdefghijklmnopqrstuvwxyz .'"),
    "father_name":    ("7", "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                            "abcdefghijklmnopqrstuvwxyz .'"),
    "dob":            ("7", "0123456789/"),
}

TARGET_H = 48          # crops are scaled so glyph height suits Tesseract
# Padding is asymmetric: horizontal slack helps Tesseract find the line, but
# vertical slack pulls the ascenders of the NEXT printed line into a --psm 7
# single-line crop, which caused spurious insertions and empty extractions.
PAD_X, PAD_Y = 5, 2


def crop_field(img: Image.Image, box) -> Image.Image:
    x0, y0, x1, y1 = box
    x0 = max(0, x0 - PAD_X); y0 = max(0, y0 - PAD_Y)
    x1 = min(img.width, x1 + PAD_X); y1 = min(img.height, y1 + PAD_Y)
    if x1 - x0 < 4 or y1 - y0 < 4:
        return Image.new("L", (8, 8), 255)
    c = img.crop((x0, y0, x1, y1)).convert("L")
    a = np.asarray(c)
    h = a.shape[0]
    if h < TARGET_H:
        s = TARGET_H / h
        a = cv2.resize(a, (max(1, int(round(a.shape[1] * s))), TARGET_H),
                       interpolation=cv2.INTER_CUBIC)
    a = cv2.copyMakeBorder(a, 8, 8, 8, 8, cv2.BORDER_REPLICATE)
    return Image.fromarray(a)


def run_batch(crop_paths: list, field: str, tessdata_prefix: str | None = None) -> list:
    """Run Tesseract once over a list of crop images; return one string each."""
    if not crop_paths:
        return []
    psm, wl = FIELD_CFG[field]
    with tempfile.TemporaryDirectory() as td:
        lst = os.path.join(td, "list.txt")
        with open(lst, "w") as fh:
            fh.write("\n".join(crop_paths) + "\n")
        out = os.path.join(td, "out")
        cmd = ["tesseract", lst, out, "-l", "eng", "--psm", psm, "--oem", "1",
               "-c", f"tessedit_char_whitelist={wl}",
               "-c", "load_system_dawg=0", "-c", "load_freq_dawg=0"]
        env = dict(os.environ)
        if tessdata_prefix:
            env["TESSDATA_PREFIX"] = tessdata_prefix
        subprocess.run(cmd, check=True, capture_output=True, env=env)
        with open(out + ".txt", encoding="utf-8", errors="replace") as fh:
            raw = fh.read()
    pages = raw.split("\f")
    if pages and pages[-1].strip() == "":
        pages = pages[:-1]
    # Tesseract emits one page per input image, in order.
    res = [p.strip("\n") for p in pages]
    while len(res) < len(crop_paths):
        res.append("")
    return res[: len(crop_paths)]


_WS = re.compile(r"\s+")


def parse_field(field: str, raw: str) -> str:
    """Minimal documented parsing.  No error correction."""
    if field == "aadhaar_number":
        return _WS.sub("", raw)
    if field == "pan_number":
        return _WS.sub("", raw).upper()
    return _WS.sub(" ", raw).strip()


def cer(ref: str, hyp: str) -> float:
    """Character error rate (Levenshtein / len(ref))."""
    if not ref:
        return 0.0 if not hyp else 1.0
    m, n = len(ref), len(hyp)
    prev = list(range(n + 1))
    for i in range(1, m + 1):
        cur = [i] + [0] * n
        ri = ref[i - 1]
        for j in range(1, n + 1):
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1,
                         prev[j - 1] + (ri != hyp[j - 1]))
        prev = cur
    return prev[n] / m
