# -*- coding: utf-8 -*-
"""64-bit DCT perceptual hash, used by the near-duplicate leakage audit.

Implemented locally rather than taken from a library so that the dataset build
has no dependency beyond NumPy/OpenCV/Pillow.
"""
from __future__ import annotations

import cv2
import numpy as np
from PIL import Image


def phash64(img: Image.Image) -> int:
    a = np.asarray(img.convert("L").resize((32, 32), Image.LANCZOS), dtype=np.float32)
    d = cv2.dct(a)[:8, :8]
    v = d.flatten()
    med = np.median(v[1:])            # exclude the DC term from the threshold
    bits = (v > med).astype(np.uint64)
    out = np.uint64(0)
    for b in bits:
        out = np.uint64(out << np.uint64(1)) | np.uint64(b)
    return int(out)


def phash256(img: Image.Image) -> bytes:
    """A 256-bit variant (16x16 DCT band) returned as 32 bytes.

    The 64-bit hash keeps only the eight lowest DCT frequencies per axis, which
    on a corpus where every image is one of six card layouts are dominated by
    the layout itself: measured on the released corpus, the 64-bit hash produces
    only about 5.9k distinct values for 10.8k images and collides across
    different persons. The 256-bit variant retains enough mid-frequency
    structure to separate identities, and is what the near-duplicate audit uses.
    """
    a = np.asarray(img.convert("L").resize((64, 64), Image.LANCZOS), dtype=np.float32)
    d = cv2.dct(a)[:16, :16]
    v = d.flatten()
    med = np.median(v[1:])
    bits = (v > med).astype(np.uint8)
    return np.packbits(bits).tobytes()


_POP = np.array([bin(i).count("1") for i in range(256)], dtype=np.uint8)


def hamming_bytes_min(a: np.ndarray, b: np.ndarray, chunk: int = 256):
    """Minimum Hamming distance from every row of `a` to any row of `b`.

    `a`, `b` are (n, k) uint8 arrays of packed hash bytes."""
    best = np.full(len(a), 1 << 15, dtype=np.int32)
    arg = np.zeros(len(a), dtype=np.int64)
    for s in range(0, len(a), chunk):
        e = min(s + chunk, len(a))
        x = a[s:e][:, None, :] ^ b[None, :, :]
        d = _POP[x].sum(axis=2).astype(np.int32)
        j = d.argmin(axis=1)
        best[s:e] = d[np.arange(e - s), j]
        arg[s:e] = j
    return best, arg


def hamming_matrix_min(a: np.ndarray, b: np.ndarray, chunk: int = 512):
    """Minimum Hamming distance from every row of `a` to any row of `b`.

    `a`, `b` are uint64 arrays of hashes.  Returns (min_per_a, argmin_per_a).
    """
    a8 = a.view(np.uint8).reshape(-1, 8)
    b8 = b.view(np.uint8).reshape(-1, 8)
    best = np.full(len(a), 65, dtype=np.int16)
    arg = np.zeros(len(a), dtype=np.int64)
    for s in range(0, len(a), chunk):
        e = min(s + chunk, len(a))
        x = a8[s:e][:, None, :] ^ b8[None, :, :]
        d = _POP[x].sum(axis=2).astype(np.int16)
        j = d.argmin(axis=1)
        best[s:e] = d[np.arange(e - s), j]
        arg[s:e] = j
    return best, arg
