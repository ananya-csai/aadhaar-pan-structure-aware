# -*- coding: utf-8 -*-
"""Synthetic Aadhaar and PAN identifier generation (Section IV-B).

No identifier produced here was submitted to, resolved through, or checked
against any UIDAI or Income Tax Department service.  See `coincidence_bound`
for the quantitative statement about accidental coincidence with issued
numbers, and docs/DATASHEET.md for the ethical discussion that follows from it.
"""
from __future__ import annotations

import random
import string

from .checksums import append_verhoeff, verhoeff_check

# --------------------------------------------------------------------------
# Aadhaar
# --------------------------------------------------------------------------

# The UIDAI numbering scheme specifies a 12-digit number consisting of an
# 11-digit body and one Verhoeff check digit, i.e. a nominal 10**11 payload
# space.  A widely implemented convention -- reflected, for example, in the
# open-source python-stdnum validator -- additionally holds that issued numbers
# do not begin with 0 or 1.  We could not locate an authoritative UIDAI
# statement of that restriction, so it is treated here as a convention rather
# than as a specification: generation honours it (giving a smaller, and
# therefore more conservative, payload space for the coincidence bound), and
# validation does NOT enforce it (Section III-A checks length and checksum only).
AADHAAR_LEADING_DIGITS = "23456789"
AADHAAR_PAYLOAD_SPACE = len(AADHAAR_LEADING_DIGITS) * 10 ** 10  # 8e10


def generate_aadhaar(rng: random.Random) -> str:
    """Return a 12-digit Verhoeff-consistent Aadhaar-format identifier."""
    payload = rng.choice(AADHAAR_LEADING_DIGITS) + "".join(
        rng.choice("0123456789") for _ in range(10)
    )
    return append_verhoeff(payload)


def break_aadhaar_checksum(number: str, rng: random.Random) -> str:
    """Alter one interior digit so the Verhoeff check fails (category C2).

    The check digit itself and the leading digit are left alone, so the result
    remains a plausible 12-digit string that fails only on the checksum.
    """
    assert len(number) == 12
    for _ in range(64):
        pos = rng.randrange(1, 11)          # interior digits n_2 .. n_11
        new = rng.choice([d for d in "0123456789" if d != number[pos]])
        cand = number[:pos] + new + number[pos + 1:]
        if not verhoeff_check(cand):
            return cand
    raise RuntimeError("could not break checksum")  # unreachable for Verhoeff


def format_aadhaar(number: str) -> str:
    """Group as 4-4-4 for printing, as on an Aadhaar card."""
    return f"{number[0:4]} {number[4:8]} {number[8:12]}"


# --------------------------------------------------------------------------
# PAN
# --------------------------------------------------------------------------

# Table II of the paper: fourth-character taxpayer category codes.
PAN_CATEGORIES = {
    "P": "Individual",
    "C": "Company",
    "H": "Hindu Undivided Family (HUF)",
    "F": "Firm",
    "A": "Association of Persons (AOP)",
    "T": "Trust",
    "B": "Body of Individuals (BOI)",
    "L": "Local Authority",
    "J": "Artificial Juridical Person",
    "G": "Government",
}

# Effective PAN space under the constraints this generator applies:
# three free letters, one category letter, one name-determined letter,
# four digits and one free letter.
PAN_SPACE_CONSTRAINED = (26 ** 3) * len(PAN_CATEGORIES) * 1 * (10 ** 4) * 26
# Nominal space if no position carried meaning:
PAN_SPACE_NOMINAL = (26 ** 5) * (10 ** 4) * 26


def generate_pan(rng: random.Random, category: str, fifth: str) -> str:
    """Return a 10-character PAN-format identifier.

    `category` is the fourth character p4 (must be a key of PAN_CATEGORIES);
    `fifth` is p5, supplied by the caller from the associated name so that the
    cross-field rule of Section III-B holds by construction.

    The tenth character is sampled uniformly.  Its generating algorithm is not
    public (Section III-B), so this study neither reproduces nor validates it;
    the sampled letter is therefore arbitrary and must not be read as a check
    digit.
    """
    assert category in PAN_CATEGORIES, category
    assert len(fifth) == 1 and fifth in string.ascii_uppercase, fifth
    head = "".join(rng.choice(string.ascii_uppercase) for _ in range(3))
    digits = "".join(rng.choice("0123456789") for _ in range(4))
    tail = rng.choice(string.ascii_uppercase)
    return head + category + fifth + digits + tail


def break_pan_structure(pan: str, rng: random.Random) -> tuple[str, str]:
    """Introduce a structural (format or category) fault, for category C2.

    Returns (corrupted_pan, fault_kind) where fault_kind is one of
    'format_letter_slot', 'format_digit_slot', 'format_length', 'category'.
    """
    kind = rng.choice(
        ["format_letter_slot", "format_digit_slot", "format_length", "category"]
    )
    p = list(pan)
    if kind == "format_letter_slot":
        # a digit where the pattern requires a letter (positions 1-3 or 10)
        pos = rng.choice([0, 1, 2, 9])
        p[pos] = rng.choice("0123456789")
    elif kind == "format_digit_slot":
        # a letter where the pattern requires a digit (positions 6-9)
        pos = rng.randrange(5, 9)
        p[pos] = rng.choice(string.ascii_uppercase)
    elif kind == "format_length":
        if rng.random() < 0.5:
            del p[rng.randrange(0, 10)]                       # 9 characters
        else:
            p.insert(rng.randrange(0, 11), rng.choice(string.ascii_uppercase))
    else:  # category
        bad = [c for c in string.ascii_uppercase if c not in PAN_CATEGORIES]
        p[3] = rng.choice(bad)
    return "".join(p), kind


# --------------------------------------------------------------------------
# Coincidence with issued numbers
# --------------------------------------------------------------------------

def coincidence_bound(n_generated: int, issued_population: int, space: int) -> dict:
    """Expected number of generated identifiers that coincide with an issued one.

    Under uniform sampling from `space` with `issued_population` numbers issued,
    the per-identifier coincidence probability is issued/space and the expected
    number of coincidences over `n_generated` draws is n*issued/space.
    """
    p = issued_population / space
    return {
        "n_generated": n_generated,
        "issued_population": issued_population,
        "space": space,
        "p_single": p,
        "expected_coincidences": n_generated * p,
        "p_at_least_one": 1.0 - (1.0 - p) ** n_generated,
    }
