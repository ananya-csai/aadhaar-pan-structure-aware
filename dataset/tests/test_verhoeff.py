# -*- coding: utf-8 -*-
"""Verhoeff implementation: worked examples and the two stated guarantees."""
import random, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from idforge.checksums import verhoeff_check, verhoeff_digit, append_verhoeff

fails = []
def ck(label, got, want):
    ok = got == want
    if not ok: fails.append(f"{label}: {got!r} != {want!r}")
    print(("PASS " if ok else "FAIL ") + label)

ck("worked example, accepted", verhoeff_check("499785203517"), True)
ck("worked example, interior digit altered", verhoeff_check("499786203517"), False)
ck("worked example, fabricated payload accepted", verhoeff_check("789456123005"), True)
ck("generation matches the worked example", append_verhoeff("49978520351"), "499785203517")
ck("generation matches the fabricated example", append_verhoeff("78945612300"), "789456123005")

rng = random.Random(11)
pool = ["".join(rng.choice("0123456789") for _ in range(11)) for _ in range(4000)]
ck("round trip", all(verhoeff_check(append_verhoeff(p)) for p in pool), True)

miss = tot = 0
for p in pool[:1200]:
    n = append_verhoeff(p)
    for i in range(12):
        for d in "0123456789":
            if d == n[i]: continue
            tot += 1
            miss += verhoeff_check(n[:i] + d + n[i+1:])
ck(f"every single-digit substitution detected ({tot} trials)", miss, 0)

miss = tot = 0
for p in pool[:1200]:
    n = append_verhoeff(p)
    for i in range(11):
        if n[i] == n[i+1]: continue
        m = list(n); m[i], m[i+1] = m[i+1], m[i]; tot += 1
        miss += verhoeff_check("".join(m))
ck(f"every adjacent transposition detected ({tot} trials)", miss, 0)

# The check digit itself carries no information about authenticity: for every
# 11-digit payload there is exactly one accepted 12th digit.
ok = True
for p in pool[:400]:
    acc = [d for d in "0123456789" if verhoeff_check(p + d)]
    ok &= (acc == [verhoeff_digit(p)])
ck("exactly one check digit is accepted per payload", ok, True)

print()
if fails: print("FAILURES:"); [print(" ", f) for f in fails]; sys.exit(1)
print("all Verhoeff checks passed")
