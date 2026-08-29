# -*- coding: utf-8 -*-
"""Hand-constructed cases from Section III-D, run before any rendering."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from idforge.checksums import verhoeff_check, append_verhoeff
from idforge.validators import validate_aadhaar, validate_pan, tokens, PASS, FAIL, SKIPPED

FAILS = []
def check(label, got, want):
    ok = got == want
    if not ok:
        FAILS.append(f"{label}: got {got!r} want {want!r}")
    print(("PASS " if ok else "FAIL ") + label + f"  -> {got!r}")

# --- Aadhaar, Section III-D -------------------------------------------------
check("A1 checksum-consistent payload accepted",
      validate_aadhaar("499785203517").overall, PASS)
check("A2 one interior digit altered rejected",
      validate_aadhaar("499786203517").overall, FAIL)
check("A2 rejected at the checksum stage, not the format stage",
      validate_aadhaar("499786203517").format_check, PASS)
check("A3 malformed non-12-digit input rejected at format stage",
      validate_aadhaar("49978520351").format_check, FAIL)
check("A3 checksum not evaluated for malformed input",
      validate_aadhaar("49978520351").checksum_check, SKIPPED)
check("A4 independently fabricated payload with valid check digit ACCEPTED",
      validate_aadhaar("789456123005").overall, PASS)
check("A5 non-numeric rejected", validate_aadhaar("4997B5203517").format_check, FAIL)
check("A6 empty rejected", validate_aadhaar("").format_check, FAIL)

# --- PAN, Section III-D -----------------------------------------------------
check("P1 Individual with consistent surname initial",
      validate_pan("ABCPS1234K", "Ananya Shukla").overall, PASS)
check("P2 same number, p5 altered -> semantic fail",
      validate_pan("ABCPZ1234K", "Ananya Shukla").semantic_check, FAIL)
check("P2 format still passes", validate_pan("ABCPZ1234K", "Ananya Shukla").format_check, PASS)
check("P2 category still passes", validate_pan("ABCPZ1234K", "Ananya Shukla").category_check, PASS)
check("P3 unrecognised category code",
      validate_pan("ABCXS1234K", "Ananya Shukla").category_check, FAIL)
check("P3 semantic skipped after category fail",
      validate_pan("ABCXS1234K", "Ananya Shukla").semantic_check, SKIPPED)
check("P4 Company, p5 matches first char of entity name",
      validate_pan("ABCCS1234K", "Shukla Traders Private Limited").semantic_check, PASS)
check("P5 Company, p5 altered",
      validate_pan("ABCCZ1234K", "Shukla Traders Private Limited").semantic_check, FAIL)
check("P6 no recoverable name field -> SKIPPED, not FAIL",
      validate_pan("ABCPS1234K", "").semantic_check, SKIPPED)
check("P6 overall PASS when name is absent",
      validate_pan("ABCPS1234K", "").overall, PASS)
check("P7 initial-first 'V. Lakshmi', p5=V permissive PASS",
      validate_pan("ABCPV1234K", "V. Lakshmi").semantic_check, PASS)
check("P7 initial-first 'V. Lakshmi', p5=V strict FAIL",
      validate_pan("ABCPV1234K", "V. Lakshmi").semantic_strict, FAIL)
check("P8 initial-first 'V. Lakshmi', p5=L both PASS",
      validate_pan("ABCPL1234K", "V. Lakshmi").semantic_check, PASS)
check("P8 strict also PASS",
      validate_pan("ABCPL1234K", "V. Lakshmi").semantic_strict, PASS)
check("P9 honorific stripped: 'Smt. Ananya Shukla'",
      validate_pan("ABCPS1234K", "Smt. Ananya Shukla").semantic_strict, PASS)
check("P9 honorific is not counted as a token initial",
      validate_pan("ABCPS1234K", "Smt. Ananya Shukla").semantic_check, PASS)
check("P10 mononymic 'Rajesh'", validate_pan("ABCPR1234K", "Rajesh").semantic_check, PASS)
check("P11 format fail: 9 characters",
      validate_pan("ABCPS1234", "Rajesh").format_check, FAIL)
check("P12 format fail: digit in a letter slot",
      validate_pan("A2CPS1234K", "Rajesh").format_check, FAIL)
check("P13 format fail: letter in a digit slot",
      validate_pan("ABCPSI234K", "Rajesh").format_check, FAIL)
check("P14 lower-case input is not silently accepted",
      validate_pan("abcps1234k", "Rajesh").format_check, FAIL)

# --- tokenisation -----------------------------------------------------------
check("T1", tokens("Smt. Ananya Shukla"), ["Ananya", "Shukla"])
check("T2", tokens("V. Lakshmi"), ["V", "Lakshmi"])
check("T3", tokens("Rajesh"), ["Rajesh"])
check("T4", tokens(""), [])
check("T5", tokens("Dr. Shri  K.  Subramanian"), ["K", "Subramanian"])

# --- the second stated limitation: a passed checksum is not authenticity -----
fabricated = append_verhoeff("78945612300")
check("L1 fabricated payload receives a valid check digit", verhoeff_check(fabricated), True)
check("L1 and the validator accepts it", validate_aadhaar(fabricated).overall, PASS)

print()
if FAILS:
    print("FAILED CHECKS:"); [print(" ", f) for f in FAILS]; sys.exit(1)
print("all validator checks passed")
