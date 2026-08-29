# -*- coding: utf-8 -*-
"""Generator invariants that must hold before any image is rendered."""
import random, sys, os, string, collections
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from idforge.checksums import verhoeff_check
from idforge.identifiers import (generate_aadhaar, generate_pan, break_aadhaar_checksum,
                                 break_pan_structure, PAN_CATEGORIES, AADHAAR_LEADING_DIGITS)
from idforge.records import make_records
from idforge.validators import validate_aadhaar, validate_pan, tokens, PASS, FAIL
from idforge.forgery import modify_record_fields, EXPECTED_RULE
from idforge.splits import assign_splits, RATIOS
from idforge.degrade import degrade, TIERS
from idforge import templates as TPL

fails = []
def ck(label, got, want):
    ok = got == want
    if not ok: fails.append(f"{label}: {got!r} != {want!r}")
    print(("PASS " if ok else "FAIL ") + label + (f"  -> {got!r}" if not ok else ""))

rng = random.Random(3)
A = [generate_aadhaar(rng) for _ in range(3000)]
ck("generated Aadhaar are 12 digits", all(len(a) == 12 and a.isdigit() for a in A), True)
ck("generated Aadhaar are Verhoeff-consistent", all(verhoeff_check(a) for a in A), True)
ck("generated Aadhaar honour the leading-digit convention",
   all(a[0] in AADHAAR_LEADING_DIGITS for a in A), True)
ck("C2 Aadhaar corruption always breaks the checksum",
   any(verhoeff_check(break_aadhaar_checksum(a, rng)) for a in A), False)
ck("C2 Aadhaar corruption preserves length",
   all(len(break_aadhaar_checksum(a, rng)) == 12 for a in A[:500]), True)

P = [generate_pan(rng, "P", "S") for _ in range(1000)]
ck("generated PAN validate structurally",
   all(validate_pan(p, "Ananya Shukla").overall == PASS for p in P), True)
ck("C2 PAN corruption always fails a structural rule",
   all(validate_pan(break_pan_structure(p, rng)[0], "Ananya Shukla").overall == FAIL
       for p in P), True)

recs = make_records(400, 20260828, {})
ck("every record's PAN is consistent with its printed name",
   all(validate_pan(r.pan, r.extra["printed_name_latin"]).overall == PASS for r in recs), True)
ck("every record's Aadhaar validates",
   all(validate_aadhaar(r.aadhaar).overall == PASS for r in recs), True)
ck("person identifiers are unique", len({r.person_id for r in recs}), 400)
ck("Aadhaar identifiers are unique within the corpus", len({r.aadhaar for r in recs}), 400)
ck("PAN identifiers are unique within the corpus", len({r.pan for r in recs}), 400)
ck("all three naming strata are populated",
   len({r.naming_stratum for r in recs}), 3)
ck("all template variants are used",
   len({r.template_aadhaar for r in recs}) * len({r.template_pan for r in recs}), 9)

# every forgery category produces the rule outcome the experiment assumes
deva = [r.name_devanagari for r in recs]
from idforge.build import base_fields, gt_text, rule_verdict
bad = []
for r in recs:
    for dt in ("aadhaar", "pan"):
        bf = base_fields(r, dt)
        for cat in ("C0", "C1", "C2", "C3", "C4"):
            f = bf if cat in ("C0", "C1") else modify_record_fields(bf, dt, cat, r, rng, deva)[0]
            v, _ = rule_verdict(dt, gt_text(f, dt))
            if v != EXPECTED_RULE[(dt, cat)]:
                bad.append((r.person_id, dt, cat, v))
ck(f"expected rule outcome holds for all {len(recs)*10} record/category cells", bad, [])

# C1 must be value-preserving
img, boxes = TPL.render_aadhaar(base_fields(recs[0], "aadhaar"), TPL.AADHAAR_STYLES[0], 5)
from idforge.forgery import apply_c1
seen = set()
for i in range(60):
    im2, prov = apply_c1(img, boxes, "aadhaar",
                         dict(gt_text(base_fields(recs[0], "aadhaar"), "aadhaar"), gender=""),
                         TPL.AADHAAR_STYLES[0], random.Random(i))
    seen.add(prov["c1_op"])
    ck_size = im2.size == img.size
ck("C1 exercises every operation", len(seen), 5)
ck("C1 preserves image dimensions", ck_size, True)

# splits
sp = assign_splits(recs, 7)
n = len(recs)
c = collections.Counter(sp.values())
ck("split proportions are exact to within one person",
   all(abs(c[k] - RATIOS[k] * n) <= 1 for k in RATIOS), True)
ck("every person is assigned exactly once", len(sp), n)

# degradation determinism
o1, b1, r1 = degrade(img, "severe", 123, boxes)
o2, b2, r2 = degrade(img, "severe", 123, boxes)
ck("degradation is deterministic under a fixed seed",
   (np.asarray(o1).tobytes() == np.asarray(o2).tobytes(), b1 == b2), (True, True))
o3, _, _ = degrade(img, "severe", 124, boxes)
ck("a different seed gives a different degradation",
   np.asarray(o1).tobytes() != np.asarray(o3).tobytes(), True)
ck("boxes stay inside the degraded image",
   all(0 <= v[0] <= v[2] <= o1.width and 0 <= v[1] <= v[3] <= o1.height
       for v in b1.values()), True)

print()
if fails: print("FAILURES:"); [print(" ", f) for f in fails]; sys.exit(1)
print("all generator checks passed")

# --- seed stability (this caught a real defect: Python's hash() is salted) ----
import subprocess, json as _json
code = ("import sys;sys.path.insert(0,'src');"
        "from idforge.build import _seed_for;"
        "print(_seed_for(20260828,'P000001','aadhaar','C2',0,'severe'))")
outs = set()
for salt in ("0", "1", "12345"):
    env = dict(os.environ, PYTHONHASHSEED=salt)
    outs.add(subprocess.run([sys.executable, "-c", code], capture_output=True,
                            text=True, env=env,
                            cwd=os.path.join(os.path.dirname(__file__), "..")
                            ).stdout.strip())
ck("per-artefact seeds are stable across PYTHONHASHSEED", len(outs), 1)
if fails:
    print("FAILURES:"); [print(" ", f) for f in fails]; sys.exit(1)
print("all generator checks passed (including seed stability)")
