# Decisions log — dataset construction

Every non-obvious choice, with the reason and the alternative that was rejected.
Written so that a reviewer's "why did you do X?" can be answered from a file
rather than from memory.

---

### D1. Categories C2–C4 are re-rendered from a modified record, not pixel-edited
**Alternative rejected:** edit the rendered image (retype a digit, splice a
character).
**Reason:** a pixel edit leaves a pixel-level trace. The visual branch would then
detect C2–C4 through that trace, the structural branch's contribution would look
redundant, and the incremental-value measurement RQ2 and RQ3 exist to make would
be measuring an artefact of dataset construction. Re-rendering makes the field
*content* the only distinguishing evidence, which is the condition the research
question presupposes.
**Cost:** the corpus cannot be built by tampering with an existing image corpus;
the templates had to be authored.

### D2. Layouts are format-faithful and design-unfaithful
**Alternative rejected:** reproduce the actual Aadhaar and PAN card designs.
**Reason:** the validators operate on field structure, not on visual design, so
design fidelity buys nothing the study measures — and a faithful replica corpus
of two national identity documents, published on GitHub, is a misuse hazard and
an ethics-committee objection with no scientific compensation.
**Cost:** a visual detector trained here is not directly transferable to real
cards. Stated as a limitation; the study makes relative, not absolute, claims.

### D3. Aadhaar receives a C3 category even though it has no semantic rule
**Alternative rejected:** omit C3 from the Aadhaar arm.
**Reason:** omitting it leaves the two document types with different category
sets, so any RQ5 difference is confounded with a difference in dataset design.
Injecting the same *class* of corruption (Latin/Devanagari name disagreement) and
letting the Aadhaar validator miss it makes RQ5 a like-for-like comparison in
which the difference is attributable to validation capability.
**Cost:** an extra category whose expected outcome is a miss, which must be
explained rather than assumed.

### D4. OCR whitelists are flat over the field's character class, not position-aware
**Alternative rejected:** letters at PAN positions 1–5 and 10, digits at 6–9.
**Reason:** a position-aware whitelist constrains the extractor with exactly the
format the validator then checks, making the format check partly self-fulfilling
and inflating the apparent quality of the structural branch. Measured effect: the
dominant residual PAN errors are 0↔O and I↔1, precisely the confusions a
position-aware whitelist would remove.
**Cost:** the PAN false-positive rate is high (12.7% even on clean captures). That
is the honest number, and it is what RQ6 exists to report.

### D5. OCR output is parsed, not corrected
**Reason:** the gap between validator behaviour on ground-truth text and on
extracted text *is* the RQ4 measurement. Any repair step — character
substitution, dictionary lookup, checksum-guided correction — moves the
measurement towards the ground-truth condition and destroys the comparison.
**What "parsing" means, exactly:** whitespace removal for the two identifier
fields (which are printed in groups on the card) and whitespace normalisation for
name fields. Nothing else.

### D6. Splits are grouped by person identifier and allocated by largest deficit
**Alternative rejected:** image-level random split; per-stratum integer flooring.
**Reason:** an image-level split puts one identity's genuine and forged documents
on opposite sides of the partition, letting a model recognise the identity rather
than the forgery. Per-stratum flooring of a 70/15/15 target across 27 strata
systematically starves the two minority splits — measured, before the fix, at
64/9/27 instead of 70/15/15 — because the floor error does not average out. A
running largest-deficit rule gives exact global proportions and proportional
representation within every stratum.

### D7. The near-duplicate leakage audit is reported as a diagnostic, not a gate
**Alternative rejected:** report a threshold-based PASS.
**Reason:** running the audit showed it cannot do the job here. Every document
shares one of six layouts, which dominates the DCT band a perceptual hash is
built from. A 64-bit hash produced only 5,878 distinct values for 10,800 images
and collided across persons, categories and splits. A 256-bit hash separates
images but not identities (AUC 0.954; 1.7% of different-person pairs closer than
the median same-document pair). Reporting a PASS on a measure with that overlap
would be reporting a number that means nothing. The leakage verdict rests on the
four exact audits, which cannot saturate.

### D8. The degradation pipeline is written in-repository rather than taken from a library
**Alternative rejected:** Augraphy.
**Reason:** the corpus must reproduce from a fresh checkout with no dependency
beyond NumPy, OpenCV and Pillow, and every applied parameter must be recordable
per image in the manifest. Augraphy is cited as implementing a comparable chain;
it is not what produced this corpus, and the paper says so.

### D9. The released JPEG is the capture-simulation output, not a re-encoding
**Reason:** re-encoding the decoded array at a fixed quality layers a second,
artificial compression stage on top of the simulated capture compression. That
inflates storage roughly threefold and, worse, would contaminate any
double-compression cue a visual branch might legitimately learn from category C1,
which uses localised recompression as one of its operations.

### D10. Font binaries are committed to the repository
**Reason:** glyph rasterisation depends on the exact font file. A build that
picked up whatever face the host system provided would not reproduce the released
corpus, so "reproducible from code" would be false on Windows and macOS. 13 MB is
a small price. All four families are freely redistributable.

### D11. Photographs are procedural placeholders, not generated faces
**Alternative rejected:** a face-generation model.
**Reason:** face-level attacks are out of scope (the paper treats face morphing as
orthogonal), so a face buys nothing the study measures, while introducing a
generative-model dependency, a licensing question and a synthetic-face ethics
question. The placeholder occupies the photograph slot so the layout is complete
and the visual branch sees realistic non-text content, and it is drawn identically
across categories so it cannot act as a class cue.

### D12. Coincidence with issued identifiers is reported, not claimed negligible
**Alternative rejected:** the earlier draft's claim that coincidence is negligible
at this scale.
**Reason:** it is arithmetically false. At ~1.8% per identifier and ~1,100
identifiers per document type, roughly twenty coincidences are expected and the
probability of at least one is indistinguishable from 1. The safety argument is
non-linkage — a bare identifier attached to a generated name, date of birth and
placeholder photograph is not information about any identifiable person, and
nothing was ever resolved against a service — and that argument does not need
non-coincidence to hold.

### D13. `initial_first_p5_from_lead` is declared as a modelling assumption
**Reason:** for an initial-first name such as "V. Lakshmi", which token the tax
record treated as the surname is genuinely ambiguous, and no data on the
prevalence was available. The parameter is exposed in the config, recorded per
record as `pan_fifth_source`, and every reported result is given both
conditionally on that field (assumption-free) and at corpus level (conditional on
the assumption), with the distinction stated.

### D14. Only Individual-category PANs appear in the image corpus
**Reason:** a company or trust is not a person with an Aadhaar, a photograph and a
date of birth, so including non-Individual PANs would break the one-person /
one-Aadhaar / one-PAN record model that the grouped split depends on. The
non-Individual branch of Algorithm 2 is covered by unit tests instead. Stated as
a limitation.

### D15. Per-artefact seeds use a cryptographic digest, not Python's `hash()`
**How it was found:** a check that rebuilt the same three persons with one worker
and with two workers and compared the JPEG bytes. They differed, and both
differed from the released corpus — silently, because the corpus still *looked*
correct.
**Cause:** the seed for each render and each degradation draw was derived with
Python's built-in `hash()` on strings, which is salted per interpreter process
via `PYTHONHASHSEED`. Every run, and every worker process within a run, therefore
produced different pixels from the same nominal seed.
**Fix:** derive seeds with `hashlib.blake2b` over the identifier tuple.
`tests/test_generators.py` now runs the seed function under three different
`PYTHONHASHSEED` values and requires identical output, so the defect cannot
return.
**Why it is recorded:** the reproducibility claim in Section IV-I would have been
false, and nothing in the dataset would have revealed it. This is the argument for
testing reproducibility rather than asserting it.
