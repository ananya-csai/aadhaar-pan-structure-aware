"""Verhoeff decimal check-digit scheme.

Reference: J. Verhoeff, "Error Detecting Decimal Codes", Ph.D. dissertation,
Mathematical Centre, Amsterdam, 1969, Mathematical Centre Tract 29.

The tables below are reproduced exactly as used by the validator, so that the
checksum computation reported in the paper is fully auditable.

Notation follows Section III-A of the paper: an Aadhaar string is 1-indexed,
n = n_1 n_2 ... n_12, where n_1 is the leftmost digit and n_12 the check digit.
The recurrence iterates i = 0..11 with i = 0 selecting n_12.
"""
from __future__ import annotations

# Multiplication table D over the dihedral group D_5 (10 x 10).
D = (
    (0, 1, 2, 3, 4, 5, 6, 7, 8, 9),
    (1, 2, 3, 4, 0, 6, 7, 8, 9, 5),
    (2, 3, 4, 0, 1, 7, 8, 9, 5, 6),
    (3, 4, 0, 1, 2, 8, 9, 5, 6, 7),
    (4, 0, 1, 2, 3, 9, 5, 6, 7, 8),
    (5, 9, 8, 7, 6, 0, 4, 3, 2, 1),
    (6, 5, 9, 8, 7, 1, 0, 4, 3, 2),
    (7, 6, 5, 9, 8, 2, 1, 0, 4, 3),
    (8, 7, 6, 5, 9, 3, 2, 1, 0, 4),
    (9, 8, 7, 6, 5, 4, 3, 2, 1, 0),
)

# Permutation table P (8 x 10), applied cyclically by digit position.
P = (
    (0, 1, 2, 3, 4, 5, 6, 7, 8, 9),
    (1, 5, 7, 6, 2, 8, 3, 0, 9, 4),
    (5, 8, 0, 3, 7, 9, 6, 1, 4, 2),
    (8, 9, 1, 6, 0, 4, 3, 5, 2, 7),
    (9, 4, 5, 3, 1, 2, 6, 8, 7, 0),
    (4, 2, 8, 6, 5, 7, 3, 9, 0, 1),
    (2, 7, 9, 3, 8, 0, 6, 4, 1, 5),
    (7, 0, 4, 6, 9, 1, 3, 2, 5, 8),
)

# Inverse table over D_5.  Used only for GENERATING a check digit; it plays no
# part in validation (Section III-A, footnote 1).
INV = (0, 4, 3, 2, 1, 5, 6, 7, 8, 9)


def verhoeff_check(number: str) -> bool:
    """Return True iff `number` (a digit string) is Verhoeff-consistent.

    Implements Algorithm 1 of the paper.  The final digit is treated as the
    check digit.  Raises ValueError on non-digit input.
    """
    if not number.isdigit():
        raise ValueError("verhoeff_check expects a digit string")
    c = 0
    n = len(number)
    for i, digit in enumerate(reversed(number)):
        c = D[c][P[i % 8][int(digit)]]
    del n
    return c == 0


def verhoeff_digit(payload: str) -> str:
    """Return the Verhoeff check digit for `payload` (the digits preceding it)."""
    if not payload.isdigit():
        raise ValueError("verhoeff_digit expects a digit string")
    c = 0
    for i, digit in enumerate(reversed(payload)):
        c = D[c][P[(i + 1) % 8][int(digit)]]
    return str(INV[c])


def append_verhoeff(payload: str) -> str:
    """Return `payload` with its Verhoeff check digit appended."""
    return payload + verhoeff_digit(payload)
