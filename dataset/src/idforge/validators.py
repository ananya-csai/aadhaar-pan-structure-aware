# -*- coding: utf-8 -*-
"""Deterministic structural and semantic validators (Section III).

These modules operate on text fields and require no training.  They are
implemented exactly as specified by the equations, algorithms and tables of
Section III, and are exercised against hand-constructed inputs in tests/.

Result vocabulary
-----------------
PASS     the rule evaluated TRUE
FAIL     the rule evaluated FALSE (internal inconsistency, NOT confirmed forgery)
SKIPPED  the rule was not applicable because the evidence it needs is absent
N/A      the rule does not exist for this document type

SKIPPED is load-bearing.  Absence of evidence is recorded as absence, not as
inconsistency; a validator that reported a failure when it had no name to
compare against would manufacture false positives out of extraction failure.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, asdict

from .checksums import verhoeff_check
from .identifiers import PAN_CATEGORIES

PASS, FAIL, SKIPPED, NA = "PASS", "FAIL", "SKIPPED", "N/A"

HONORIFICS = {
    "shri", "sri", "smt", "smt.", "km", "kum", "ms", "mr", "mrs", "dr",
    "late", "shrimati", "sushri",
}

_ALPHA_TOKEN = re.compile(r"[A-Za-z]+")
PAN_PATTERN = re.compile(r"^[A-Z]{5}[0-9]{4}[A-Z]$")


@dataclass
class AadhaarResult:
    format_check: str
    checksum_check: str
    overall: str            # PASS if both non-FAIL, else FAIL
    reason: str

    def as_dict(self):
        return asdict(self)


def validate_aadhaar(text: str) -> AadhaarResult:
    """Section III-A / Algorithm 1 / Figure 2."""
    s = "" if text is None else text
    if len(s) != 12 or not s.isdigit():
        return AadhaarResult(
            FAIL, SKIPPED, FAIL,
            f"format: expected exactly 12 decimal digits, extracted {len(s)} "
            f"character(s) ('{s[:24]}')")
    if not verhoeff_check(s):
        return AadhaarResult(
            PASS, FAIL, FAIL,
            "checksum: the twelfth digit is not the Verhoeff check digit of the "
            "preceding eleven")
    return AadhaarResult(PASS, PASS, PASS,
                         "format and Verhoeff checksum are internally consistent; "
                         "this does not establish authenticity")


def tokens(name: str) -> list:
    """TOKENS(name): alphabetic tokens after honorific removal.

    Single-letter abbreviated forms are retained, so that an initial-first name
    such as 'V. Lakshmi' contributes its leading letter to the initial set.
    """
    if not name:
        return []
    out = []
    for t in _ALPHA_TOKEN.findall(name):
        if t.lower() in HONORIFICS:
            continue
        out.append(t)
    return out


@dataclass
class PanResult:
    format_check: str
    category_check: str
    semantic_check: str          # permissive rule, equation (2)
    semantic_strict: str         # sensitivity analysis variant
    overall: str
    category: str
    reason: str

    def as_dict(self):
        return asdict(self)


def validate_pan(pan: str, name: str) -> PanResult:
    """Section III-B / equation (2) / Algorithm 2 / Figure 3.

    The tenth character is NOT validated: its generating algorithm is not
    public, so no external system can verify it.  It is recorded as
    inapplicable rather than omitted silently.
    """
    p = "" if pan is None else pan
    if not PAN_PATTERN.match(p):
        return PanResult(FAIL, SKIPPED, SKIPPED, SKIPPED, FAIL, "",
                         "format: expected the pattern AAAAA9999A, extracted "
                         f"'{p[:24]}'")
    p4 = p[3]
    if p4 not in PAN_CATEGORIES:
        return PanResult(PASS, FAIL, SKIPPED, SKIPPED, FAIL, p4,
                         f"category: '{p4}' at position 4 is not a defined "
                         "taxpayer-category code")
    p5 = p[4]
    T = tokens(name)
    if not T:
        return PanResult(PASS, PASS, SKIPPED, SKIPPED, PASS, p4,
                         "cross-field: no usable name field was recovered, so "
                         "the fifth-character rule was not applicable")
    if p4 == "P":
        I = {t[0].upper() for t in T}
        strict_ok = (p5 == T[-1][0].upper())
    else:
        I = {T[0][0].upper()}
        strict_ok = (p5 in I)
    perm_ok = p5 in I
    sem = PASS if perm_ok else FAIL
    semstrict = PASS if strict_ok else FAIL
    if perm_ok:
        reason = (f"cross-field: '{p5}' at position 5 matches the initial of a "
                  f"token in the extracted name field ({'/'.join(sorted(I))})")
    else:
        reason = (f"cross-field: '{p5}' at position 5 matches no initial of any "
                  f"token in the extracted name field ({'/'.join(sorted(I))})")
    return PanResult(PASS, PASS, sem, semstrict, PASS if perm_ok else FAIL,
                     p4, reason)


def fuse_document(doc_type: str, aadhaar_res=None, pan_res=None) -> str:
    """Rule-branch verdict for one document: FAIL if any applicable rule failed."""
    r = aadhaar_res if doc_type == "aadhaar" else pan_res
    return r.overall
