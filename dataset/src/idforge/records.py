# -*- coding: utf-8 -*-
"""Identity-record generation (Section IV-C).

A *record* is generated before any document is rendered, so that every
downstream artefact -- both card types, all forgery categories, all quality
tiers -- inherits the same person identifier.  This is what makes the grouped
split of Section IV-H possible.
"""
from __future__ import annotations

import random
from dataclasses import dataclass, asdict, field

from . import names as N
from .identifiers import generate_aadhaar, generate_pan

N_TEMPLATE_VARIANTS = 3


@dataclass
class IdentityRecord:
    person_id: str
    gender: str                 # "M" | "F"
    naming_stratum: str
    honorific: str              # "" if none
    name_latin: str             # as printed, honorific excluded
    name_devanagari: str
    name_tokens: list           # alphabetic tokens after honorific removal
    surname: str                # "" if the stratum has none
    dob: str                    # DD/MM/YYYY
    father_name_latin: str
    aadhaar: str
    pan: str
    pan_category: str
    pan_fifth: str
    pan_fifth_source: str       # surname | mononym | leading_initial | given_name
    photo_seed: int
    template_aadhaar: int
    template_pan: int
    extra: dict = field(default_factory=dict)

    def as_dict(self) -> dict:
        return asdict(self)


def _dob(rng: random.Random) -> str:
    year = rng.randint(1955, 2005)
    month = rng.randint(1, 12)
    day = rng.randint(1, 28)
    return f"{day:02d}/{month:02d}/{year}"


def make_record(index: int, rng: random.Random, cfg: dict) -> IdentityRecord:
    gender = "M" if rng.random() < 0.5 else "F"
    given_l, given_d = rng.choice(N.MALE_GIVEN if gender == "M" else N.FEMALE_GIVEN)
    stratum = rng.choices(
        N.STRATA, weights=cfg.get("stratum_weights", [1, 1, 1]), k=1
    )[0]

    honorific = ""
    if rng.random() < cfg.get("honorific_rate", 0.18):
        honorific = rng.choice(N.HONORIFICS_M if gender == "M" else N.HONORIFICS_F)
    hon_d = N.DEVANAGARI_HONORIFIC.get(honorific, "")

    surname = ""
    if stratum == N.SURNAME_LAST:
        sur_l, sur_d = rng.choice(N.SURNAMES)
        surname = sur_l
        name_latin = f"{given_l} {sur_l}"
        name_deva = f"{given_d} {sur_d}"
        tokens = [given_l, sur_l]
        fifth, fifth_src = sur_l[0].upper(), "surname"
    elif stratum == N.INITIAL_FIRST:
        lead = rng.choice(N.INITIAL_LETTERS)
        name_latin = f"{lead}. {given_l}"
        name_deva = f"{N.DEVANAGARI_INITIAL[lead]}. {given_d}"
        tokens = [lead, given_l]
        # Which token the tax record treated as the surname is genuinely
        # ambiguous for this stratum.  `initial_first_p5_from_lead` is a
        # MODELLING ASSUMPTION, not a measurement; results conditioned on
        # pan_fifth_source are assumption-free (see docs/DATASHEET.md).
        if rng.random() < cfg.get("initial_first_p5_from_lead", 0.35):
            fifth, fifth_src = lead, "leading_initial"
        else:
            fifth, fifth_src = given_l[0].upper(), "given_name"
    else:  # MONONYMIC
        name_latin = given_l
        name_deva = given_d
        tokens = [given_l]
        fifth, fifth_src = given_l[0].upper(), "mononym"

    father_given, _ = rng.choice(N.MALE_GIVEN)
    father_name = f"{father_given} {surname}".strip() if surname else father_given

    rec = IdentityRecord(
        person_id=f"P{index:06d}",
        gender=gender,
        naming_stratum=stratum,
        honorific=honorific,
        name_latin=name_latin,
        name_devanagari=(f"{hon_d} {name_deva}".strip() if hon_d else name_deva),
        name_tokens=tokens,
        surname=surname,
        dob=_dob(rng),
        father_name_latin=father_name,
        aadhaar=generate_aadhaar(rng),
        pan=generate_pan(rng, "P", fifth),
        pan_category="P",
        pan_fifth=fifth,
        pan_fifth_source=fifth_src,
        photo_seed=rng.randrange(2 ** 31),
        template_aadhaar=rng.randrange(N_TEMPLATE_VARIANTS),
        template_pan=rng.randrange(N_TEMPLATE_VARIANTS),
    )
    # Printed name including honorific, which is what the renderer draws and
    # therefore what OCR sees.
    rec.extra["printed_name_latin"] = (
        f"{honorific} {name_latin}".strip() if honorific else name_latin
    )
    return rec


def make_records(n: int, seed: int, cfg: dict) -> list:
    rng = random.Random(seed)
    return [make_record(i, rng, cfg) for i in range(n)]
