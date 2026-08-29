# -*- coding: utf-8 -*-
"""Grouped, stratified train/validation/test partitioning (Section IV-H).

Splits are made at the level of the PERSON IDENTIFIER, not the image and not the
document.  An image-level split would place one identity's genuine and forged
documents on opposite sides of the partition, allowing a model to recognise the
identity rather than the forgery -- the leakage this design exists to prevent.

Stratification is over person-level attributes only (naming stratum and the two
template-variant assignments), because those are the attributes whose absence
from a split would bias the analyses of Section VII.
"""
from __future__ import annotations

import random
from collections import defaultdict

RATIOS = {"train": 0.70, "val": 0.15, "test": 0.15}
SPLITS = ("train", "val", "test")


def assign_splits(records: list, seed: int) -> dict:
    """Assign each person to a split.

    Allocation is a streaming largest-deficit rule rather than per-stratum
    integer flooring.  Flooring a 70/15/15 target inside every small stratum
    systematically starves the two minority splits and dumps every remainder
    into one of them; with 27 strata that error does not average out.  Here a
    running global count is kept and each person goes to whichever split is
    furthest below its target share, so both the global proportions and the
    per-stratum representation come out right.
    """
    rng = random.Random(seed)
    strata = defaultdict(list)
    for r in records:
        strata[(r.naming_stratum, r.template_aadhaar, r.template_pan)].append(r.person_id)

    assigned = {s: 0 for s in SPLITS}
    total = 0
    out = {}
    for key in sorted(strata):
        ids = sorted(strata[key])
        rng.shuffle(ids)
        for pid in ids:
            total += 1
            deficits = [(RATIOS[s] * total - assigned[s], s) for s in SPLITS]
            deficits.sort(key=lambda t: (-t[0], t[1]))
            s = deficits[0][1]
            out[pid] = s
            assigned[s] += 1
    return out
