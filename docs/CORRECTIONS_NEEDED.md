# Corrections the rest of the paper needs, after the Section IV rebuild

Ordered by severity. Items 1–3 are factual or logical defects in the current
draft; 4–8 are consistency edits.

---

## 1. The negligible-coincidence claim in Section IV-B is false — remove it

The draft says the expected number of coincidences between generated Aadhaar
identifiers and issued ones "is negligible at the scale used here."

It is not. Measured on the built corpus:

| | Aadhaar | PAN |
|---|---|---|
| distinct generated identifiers | 1,083 | 1,200 |
| identifier space (as generated) | 8×10¹⁰ | ≈4.6×10¹⁰ |
| assumed issued population | ~1.4×10⁹ | ~8×10⁸ |
| per-identifier coincidence probability | **1.8 %** | **1.8 %** |
| expected coincidences | **≈19** | **≈21** |
| P(at least one) | ≈1.0 | ≈1.0 |

The issued populations occupy roughly 2 % of their spaces. Coincidence is
arithmetically unavoidable for any corpus that generates checksum-valid numbers,
and a reviewer can do this calculation in thirty seconds.

**The fix is not to bury it — it is to change the argument.** The replacement
Section IV-B reports the numbers and moves the safety case to *non-linkage*: a
bare identifier attached to a generated name, a generated date of birth and a
procedurally drawn placeholder is not information about any identifiable person,
and nothing was ever resolved against a service. That argument does not need
non-coincidence to hold, so it is strictly stronger. Section IV-J is rewritten to
match.

## 2. Two TODOs in the draft rest on a source that does not say what is assumed

The draft has `[TODO: Verify the admissible leading-digit range against [21]]`
and `[TODO: Confirm k]`.

What the primary source actually says: the UIDAI numbering scheme document
specifies a 12-digit number of 11 digits plus one Verhoeff check digit — a
**10¹¹** space — and states no leading-digit restriction. The "does not begin
with 0 or 1" rule is a widely implemented convention (it is in the open-source
`python-stdnum` validator, among others) with no authoritative UIDAI statement
behind it that could be located.

The replacement text treats it as a **convention, not a specification**:
generation honours it (giving the smaller and therefore more conservative
8×10¹⁰ space for the coincidence bound), validation does not enforce it (Section
III-A checks length and checksum only, as written). Reference [21] needs its
title/authors/year confirmed against the archived copy —
*A UID Numbering Scheme*, Kanakia, Nadhamuni and Sarma, UIDAI, May 2010.

## 3. Table IV's category set is inconsistent with Table III's asymmetry

The draft says every record gets "one instance of each of the four forgery
categories" for both document types, but Table III states Aadhaar has no
cross-field semantic rule — so Aadhaar C3 has nothing to be a forgery *of*.
Either the cells are unbalanced or C3 means something different for Aadhaar.

**Resolution adopted:** Aadhaar C3 injects the same *class* of semantic
corruption (the Latin and Devanagari name lines are made to disagree) and the
Aadhaar validator is expected to **miss** it, because no implemented rule reads
the Devanagari line. This keeps the cells balanced and makes RQ5 a like-for-like
comparison: PAN detects this class, Aadhaar cannot, and the difference is
attributable to validation capability rather than to dataset design. Table IV in
the replacement section records `miss` for Aadhaar C3 explicitly.

## 4. Section IV-F cites Augraphy [22] as the degradation tool — it is not

The pipeline is now written in-repository on NumPy/OpenCV so the corpus
reproduces with no dependency beyond those. [22] is retained as a citation for
"libraries implementing a comparable chain", which is accurate and is how the
replacement text uses it. If you prefer to keep Augraphy as the actual tool, the
code has a documented insertion point, but you lose the zero-dependency
reproduction claim.

## 5. Section IV-A says "parameterised HTML templates"

They are parameterised vector layouts rasterised directly, which is what gives
exact field bounding boxes as a rendering by-product. Text corrected.

## 6. C4 recall is not interpretable on its own — Section VII needs to say so

Because the rule branch also fails on genuine documents through OCR error
(19.1 % on PAN overall), a rule-branch failure on a C4 document is an
OCR-induced false alarm, **not** detection of the fabrication. On ground-truth
text the C4 flag rate is 0.0 % as designed; on OCR text it is 19.1 % for PAN.
Any Section VII table reporting per-category recall must report the
ground-truth-text verdict alongside it, or the C4 negative control will read as
partial success.

## 7. RQ6 now has a measured answer — reconcile Sections VI and VII with it

The rule branch's false-positive rate on genuine documents, from OCR error alone
(it is 0 % on ground-truth text by construction):

| | clean | mild | severe | all |
|---|---|---|---|---|
| Aadhaar | 0.3 % | 0.3 % | 11.5 % | **4.1 %** |
| PAN | 13.3 % | 12.0 % | 31.8 % | **19.1 %** |

The PAN number is recovered exactly on only 85.5 % of *clean* captures, against
99.7 % for the Aadhaar number, because a PAN mixes letters and digits and the
dominant errors are 0↔O, I↔1 and J→I. This inverts a claim implicit in Section
III-C: the asymmetry that favours PAN (more independent checks available) is
*also* a liability, because more rules on a harder-to-extract field produce more
ways to fail on a genuine document. That is a real finding and belongs in the
Discussion.

## 8. Smaller items

* Section III-B's permissive-versus-strict gap now has a number: on ground-truth
  text the strict variant fails on **9.0 %** of genuine PANs overall, **29.3 %**
  within the initial-first stratum, and **93.1 %** of records whose fifth
  character derives from the leading abbreviated token. The permissive rule
  never fails on ground truth. This is the empirical justification for the
  choice the draft currently argues for only in prose.
* The near-duplicate leakage audit of Table V cannot be reported as a PASS. Run
  on this corpus, a 64-bit perceptual hash produces 5,900 distinct values for
  10,800 images and collides across persons, categories and splits; even at 256
  bits the same-document and different-person distance distributions overlap
  (AUC 0.954). It is reported as a **diagnostic**, and the leakage verdict rests
  on the four exact audits — identity, identifier, printed values, augmentation
  — all of which pass. Table V gains a "printed values" row.
* Section V-C should record that only the English Tesseract model is used, so
  the Devanagari line is not extracted, and that the second-engine robustness
  check promised in the draft is not yet performed.
* Citation keys in the replacement `.tex` are `ref1`…`ref26` matching your
  current numbering. If your `\bibitem` labels differ, substitute them.
