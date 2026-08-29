# -*- coding: utf-8 -*-
"""Font resolution.

Font files are bundled in `assets/fonts/` and resolved from there first.  This
is not a convenience: glyph rasterisation depends on the exact font binary, so
a build that picked up whatever face the host operating system happened to
provide would not reproduce the released corpus.  System locations are searched
only as a fallback, and an explicit error is raised rather than silently
substituting a different face.
"""
from __future__ import annotations

import os

_HERE = os.path.dirname(os.path.abspath(__file__))
BUNDLED = os.path.abspath(os.path.join(_HERE, "..", "..", "assets", "fonts"))

FILES = {
    "sans":      "LiberationSans-Regular.ttf",
    "sans_b":    "LiberationSans-Bold.ttf",
    "serif":     "LiberationSerif-Regular.ttf",
    "serif_b":   "LiberationSerif-Bold.ttf",
    "libmono_b": "LiberationMono-Bold.ttf",
    "dvsans":    "DejaVuSans.ttf",
    "dvsans_b":  "DejaVuSans-Bold.ttf",
    "mono_b":    "DejaVuSansMono-Bold.ttf",
    "carlito":   "Carlito-Regular.ttf",
    "carlito_b": "Carlito-Bold.ttf",
    "deva":      "FreeSerif.ttf",
    "deva_b":    "FreeSerifBold.ttf",
    "deva_s":    "FreeSans.ttf",
}

_SYSTEM_DIRS = [
    "/usr/share/fonts/truetype/liberation", "/usr/share/fonts/truetype/dejavu",
    "/usr/share/fonts/truetype/crosextra", "/usr/share/fonts/truetype/freefont",
    "/usr/share/fonts/liberation", "/usr/share/fonts/dejavu",
    "/Library/Fonts", os.path.expanduser("~/Library/Fonts"),
    "C:/Windows/Fonts",
]


def resolve() -> dict:
    out = {}
    missing = []
    for key, fn in FILES.items():
        p = os.path.join(BUNDLED, fn)
        if os.path.exists(p):
            out[key] = p
            continue
        for d in _SYSTEM_DIRS:
            q = os.path.join(d, fn)
            if os.path.exists(q):
                out[key] = q
                break
        else:
            missing.append(fn)
    if missing:
        raise FileNotFoundError(
            "Missing font file(s): " + ", ".join(missing) +
            f"\nExpected them in {BUNDLED}. These files are committed to the "
            "repository; if you are working from a partial checkout, run "
            "'git lfs pull' or re-clone. Substituting a different face would "
            "change every rendered pixel and break reproduction of the released "
            "corpus.")
    return out
