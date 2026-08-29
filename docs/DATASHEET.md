# Datasheet — Aadhaar/PAN structural forgery benchmark, v1

Following the *Datasheets for Datasets* structure (Gebru et al.). Written to be
answerable to a reviewer or an ethics committee, not to reassure.

---

## 1. Motivation

**Why was the dataset created?** No public corpus pairs Aadhaar- or PAN-format
document images with *field-level structural ground truth* — that is, with a
record of which identifier was printed, whether it is checksum-consistent, and
whether the fifth PAN character agrees with the printed name. Without that
ground truth the incremental value of structural and semantic validation over
visual forgery detection cannot be measured, because there is nothing to measure
it against. Existing synthetic identity-document corpora (MIDV-2020, IDNet,
SIDTD) exist for exactly this reason but do not cover these two formats or their
format-specific rules.

**Who created it?** The authors of the paper, at Manipal University Jaipur.
No external funding is associated with the dataset.

---

## 2. Composition

**What do instances represent?** A rendered image of a synthetic
identity-document specimen, together with the ground-truth text of every printed
field, the field bounding boxes, the OCR extraction of those fields, and the
output of the deterministic validators on both.

**How many instances?** 300 synthetic persons → 3,600 documents → 10,800 images
at the released configuration.

**Does the dataset contain data that might be considered confidential, or that
relates to identifiable people?** No. Every name is a recombination of common
Indian given names and surnames from an authored corpus; every date of birth,
photograph, signature and identifier is generated. No real document, image or
number was collected, downloaded, purchased or processed at any stage. No
generated identifier was submitted to or verified against any government or
third-party identity service.

### 2.1 Coincidence with issued identifiers — stated plainly

A synthetic identifier that is *format- and checksum-valid* can, by arithmetic
necessity, coincide with an identifier that has actually been issued. This is
not a defect that can be engineered away; it follows from the density of the
issued population within the identifier space, and it applies to every synthetic
identity-document corpus that generates checksum-valid numbers.

The numbers, computed by `idforge.identifiers.coincidence_bound` and reported in
`stats/dataset_stats.json`:

* The Aadhaar payload space under the leading-digit convention this generator
  honours is 8 × 10¹⁰. Against an issued population of order 1.4 × 10⁹, the
  probability that any one generated identifier coincides with an issued one is
  approximately **1.8 %**.
* The PAN space, constrained as the generator constrains it (three free letters,
  one of ten category letters, one name-determined letter, four digits, one free
  letter), is about 4.6 × 10¹⁰. Against an issued population of order
  7–8 × 10⁸, the per-identifier coincidence probability is likewise of order
  **1.7 %**.

At the scale of this corpus that means **on the order of ten** generated Aadhaar
strings and **ten** generated PAN strings can be expected to coincide with an
issued identifier, and the probability that *at least one* does is
indistinguishable from 1.

**Claiming that such coincidence is negligible would be false, and this datasheet
does not claim it.** The argument that the release is safe rests on
**non-linkage**, not on non-coincidence:

1. A bare identifier string, with no association to a real person, is not
   information about any identifiable person. In this corpus every identifier is
   printed alongside a *generated* name, a *generated* date of birth and a
   *procedurally drawn* photograph, none of which belongs to any human being. A
   coincident number therefore appears in the dataset attached to a person who
   does not exist.
2. No identifier was ever resolved, queried or verified, so the dataset contains
   no information about whether any given string is issued, and none about any
   holder.
3. The images cannot function as documents: they carry a fictitious authority
   name, no official emblem, and a permanent specimen overlay.
4. The expected coincidence count is reported rather than suppressed, so a user
   of the dataset can reason about it themselves.

A user who nonetheless wishes to eliminate coincidence entirely can regenerate
with a reduced identifier space or an explicit exclusion list; the generator is
a single function (`identifiers.generate_aadhaar` / `generate_pan`).

### 2.2 What ground truth is provided

Per image: printed field values, field bounding boxes in the degraded image's
coordinate frame, forgery category, the specific field corrupted and its before
and after values, the C1 edit operation and its region (localisation ground
truth), quality tier, template variant, naming stratum, person identifier,
render and degradation seeds, perceptual hash, and validator output on both
ground-truth and OCR text.

---

## 3. Collection process

Not collected — generated. The generation procedure is the code in this
repository; `configs/dataset_v1.yaml` and the global seed determine the corpus
completely.

**Enforced rather than checked:** three design constraints are enforced by the
generation procedure rather than verified afterwards — no real document is used
at any stage; the templates are authored, so exact field bounding boxes are a
by-product of rendering; and the visually undetectable categories are produced
by re-rendering from a modified record rather than by editing pixels.

**Verified before rendering:** every validator is run against the ground-truth
text of every generated document before the corpus is rendered at scale,
requiring that C0 and C1 pass without exception, C2 fail without exception, C3
fail without exception for PAN and pass without exception for Aadhaar, and C4
pass without exception. Any deviation aborts the build as a generator defect. It
is not reported as an experimental result.

---

## 4. Preprocessing, cleaning, labelling

**OCR output is stored raw.** A minimal, documented *parsing* step is applied
before the validators see a string — whitespace removal for the two identifier
fields, whitespace normalisation for name fields — and nothing else. No
character substitution, dictionary lookup, checksum-guided repair or
confidence-based rejection is applied, because the gap between validator
behaviour on ground-truth text and on OCR text *is* the RQ4 measurement, and
repairing the output would destroy it.

**Splits are grouped by person identifier**, stratified over naming stratum and
both template-variant assignments. An image-level split would place one
identity's genuine and forged documents on opposite sides of the partition and
let a model recognise the identity rather than the forgery.

**Five leakage modes are audited and the audit is reported**, not asserted:
identity, identifier, template coverage, near-duplicate and augmentation. The
near-duplicate audit is reported as a distance *distribution* with a threshold
calibrated on this corpus, because every document here shares one of six layout
templates and so has a high baseline perceptual similarity to every other; a
fixed literature threshold would be meaningless.

---

## 5. Uses

**Intended use.** Evaluation of *forgery detection* — specifically, measuring the
incremental detection value of document-specific structural and semantic
consistency evidence over visual analysis, and how much of that value survives
real OCR error.

**Uses that are out of scope and unsupported.**

* **Authenticity verification.** The dataset shows the opposite: category C4
  consists of structurally valid fabricated identifiers that both branches are
  expected to miss.
* **Absolute performance claims.** The renders are format-faithful but not
  design-faithful, and the degradation is simulated. The corpus supports
  relative comparison between evidence sources, not statements about
  operational accuracy.
* **Face or biometric analysis.** The photograph slot holds a procedurally drawn
  placeholder, not a face.
* **Training or evaluating any system intended to produce documents.** The
  released artefacts are intended to support evaluation of forgery *detection*
  and are not sufficient to produce a document capable of passing any
  operational verification process.

---

## 6. Distribution and maintenance

The **code** is distributed via the Git repository. The **built corpus** should
be distributed as a versioned archive with a DOI, cited together with the commit
hash that produced it, since a commit hash alone does not pin the Tesseract
binary version. `config.used.json` in the dataset directory records the
configuration and the build time; `requirements.txt` pins the Python libraries;
the Tesseract version must be recorded manually with the release.

---

## 7. Known limitations

See Section 10 of the README. The two that most constrain what the paper may
claim:

* the synthetic-to-real gap, which bounds the study to relative rather than
  absolute conclusions; and
* `initial_first_p5_from_lead`, a modelling assumption governing how often an
  initial-first record's PAN fifth character derives from the leading
  abbreviated token. Results conditioned on `pan_fifth_source` are independent
  of it; corpus-level false-positive rates for the strict rule variant are not,
  and must be reported as a function of it.
