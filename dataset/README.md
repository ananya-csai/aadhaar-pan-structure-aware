# idforge — a controlled synthetic benchmark for Aadhaar- and PAN-format document forgery

Dataset construction code for the paper

> **Structure-Aware Forgery Detection for Aadhaar and PAN: A Controlled Study of
> Visual, Structural, and Semantic Evidence Fusion**
> Ananya Shukla, Soham Phulwaria, Dinesh Saini — Manipal University Jaipur

This repository is the reproducible implementation of **Section IV, Dataset
Construction**. It generates the corpus, the forgery categories, the quality
tiers, the OCR extraction, the train/validation/test partition, the leakage
audits and the figures used in the paper.

---

## 1. Read this before anything else

**Nothing here is a real identity document, and nothing here can be used as one.**

* Every identifier, name, date of birth, photograph and signature is
  **synthetic**. No real Aadhaar or PAN document, image or number was collected,
  downloaded, purchased or processed at any stage.
* No generated identifier was submitted to, resolved through, or checked against
  any UIDAI, Income Tax Department or third-party identity service.
* The card layouts are deliberately **format-faithful and design-unfaithful**.
  They reproduce the *field structure* of the two documents — which fields
  exist, in what order, with what identifier grouping — because that is what the
  study measures. They do **not** reproduce any official emblem, seal, hologram,
  colour scheme or authority name. A geometric placeholder mark and a fictitious
  authority name are used instead.
* Every rendered image carries a permanent low-opacity
  `SYNTHETIC SPECIMEN • NOT A GOVERNMENT DOCUMENT • RESEARCH USE ONLY` overlay,
  composited **before** any forgery operation and drawn identically for every
  category so that it cannot act as a class cue.
* Structural validity is explicitly shown **not** to establish authenticity
  (forgery category C4 exists precisely to demonstrate this). Nothing in this
  repository should be read as an authenticity oracle.

See [`docs/DATASHEET.md`](docs/DATASHEET.md) for the full ethical statement,
including the quantitative treatment of accidental coincidence between generated
and issued identifiers.

---

## 2. What the corpus contains

At the released configuration (`configs/dataset_v1.yaml`, `n_persons: 300`):

| | |
|---|---|
| identity records (persons) | 300 |
| documents | 3,600 (300 × 2 document types × 6 documents) |
| images | 10,800 (each document at 3 quality tiers) |
| genuine images (C0) | 3,600 |
| forged images (C1–C4) | 7,200 |
| on disk | ≈ 1.5 GiB |

Each person contributes one Aadhaar-format record and one PAN-format record.
Each record is rendered into six documents — two unmodified controls and one
instance of each of four forgery categories — and each document is captured at
three quality tiers.

### Forgery categories

| cat | construction | visual branch | rule branch |
|---|---|---|---|
| **C0** | unmodified render (control) | pass | pass |
| **C1** | post-render **value-preserving** pixel edit: font substitution, field displacement, copy-move patch splice, localised recompression, patch resampling | detect | pass |
| **C2** | **re-render** with a structurally invalid identifier (Aadhaar interior digit altered so the Verhoeff check fails; PAN format or taxpayer-category character broken) | miss | detect |
| **C3** | **re-render** with a semantically inconsistent field pair (PAN: fifth character matches no name-token initial. Aadhaar: Latin and Devanagari name lines disagree) | miss | detect (PAN only) |
| **C4** | **re-render** with a freshly fabricated identifier carrying a correctly generated check digit and a consistent fifth character | miss | miss |

C2, C3 and C4 are produced by **re-rendering the document from a modified
identity record**, never by editing a rendered image. They therefore share the
fonts, antialiasing, guilloche phase and compression history of a genuine
render, and the only evidence distinguishing them from C0 is the *content* of
the fields. Producing them by pixel editing would introduce a visual artefact,
let the visual branch detect them through that artefact, and invalidate the
incremental-value measurement the study exists to make.

**C4 is a deliberate negative control**: both branches are expected to miss it.
It converts the "a passed checksum does not prove authenticity" limitation from
an assertion into a measurement.

**Aadhaar C3 is a deliberate asymmetry control.** Aadhaar supports no
cross-field semantic rule (Table III of the paper), so the same *class* of
corruption is injected and the Aadhaar validator is expected to miss it. This is
what makes RQ5 a like-for-like comparison: PAN detects this class, Aadhaar
cannot, and the difference is attributable to validation capability rather than
to dataset design.

### Quality tiers

`clean`, `mild`, `severe` — a seeded print/scan/capture chain (perspective
homography, illumination gradient, cast shadow, optical and motion blur, moiré,
sensor noise, chromatic shift, JPEG). Degradation is applied **after** forgery
injection, so C1 pixel edits are subject to the same degradation as the
surrounding document, and every forgery category receives an identical tier
distribution so image quality cannot act as a class cue.

---

## 3. Quick start

```bash
git clone <your-repo-url> idforge
cd idforge
pip install -r requirements.txt
make test                      # ~1 min, no images produced
make sample                    # ~30 s, a 6-person corpus in data/sample
bash scripts/build_all.sh      # ~25 min: corpus, audits, figures, LaTeX tables
```

`scripts/build_all.sh` runs the four stages in order — build, perceptual hashing,
statistics and figures, LaTeX export. `make dataset` and `make report` run the
first and third individually.

On Windows, `make` may not be available — use the equivalent commands in
Section 5.

---

## 4. Installing the prerequisites (detailed)

### 4.1 Windows 10 / 11

**Step 1 — Python 3.11 or newer.**
Download from <https://www.python.org/downloads/windows/>. During installation
tick **"Add python.exe to PATH"**. Verify in a new PowerShell window:

```powershell
python --version
```

**Step 2 — Git.**
Download from <https://git-scm.com/download/win> and install with the defaults.
Verify:

```powershell
git --version
```

**Step 3 — Tesseract OCR.**
Download the Windows installer from the UB Mannheim build:
<https://github.com/UB-Mannheim/tesseract/wiki>. Install to the default
location (`C:\Program Files\Tesseract-OCR`) and tick the option to add it to
PATH if the installer offers it. If it does not, add it manually:

```powershell
[Environment]::SetEnvironmentVariable(
  "Path", $env:Path + ";C:\Program Files\Tesseract-OCR", "User")
```

Close and reopen PowerShell, then verify — this must print `tesseract 5.x`:

```powershell
tesseract --version
```

If it prints anything else, the rest of the pipeline will run but every OCR
result will be empty. Do not proceed until this works.

**Step 4 — Python packages.**

```powershell
cd path\to\idforge
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

If PowerShell refuses to run the activation script, run
`Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` first.

**Step 5 — fonts.** Nothing to do. The thirteen font files the renderer needs
are committed to `assets/fonts/` precisely so that you do not depend on what
Windows happens to have installed. See `assets/fonts/LICENSES.md`.

### 4.2 Ubuntu / Debian

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git tesseract-ocr
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
tesseract --version    # must be 5.x
```

### 4.3 macOS

```bash
brew install python git tesseract
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

---

## 5. Running the pipeline

Every command below is run from the repository root, with the virtual
environment active.

### 5.1 Tests first (always)

```powershell
# Windows
$env:PYTHONPATH="src"; python tests\test_verhoeff.py
$env:PYTHONPATH="src"; python tests\test_validators.py
$env:PYTHONPATH="src"; python tests\test_generators.py
```

```bash
# Linux / macOS
make test
```

These verify the Verhoeff implementation against the worked examples in Section
III-D, exhaustively confirm that every single-digit substitution and every
adjacent transposition is caught, run the thirty-four hand-constructed validator
cases, and confirm that every forgery category produces the rule outcome the
experiment assumes. **If any test fails, stop.** A generator defect would appear
in the results as an experimental finding.

### 5.2 A quick look before committing 40 minutes

```powershell
$env:PYTHONPATH="src"; python -m idforge.build --out data\sample --n-persons 6
$env:PYTHONPATH="src"; python -m idforge.report --out data\sample
```

This produces 216 images in about 30 seconds. Open
`data\sample\figures\fig_specimens.png` to see what the corpus looks like.

### 5.3 The full corpus

```powershell
$env:PYTHONPATH="src"; python -m idforge.build --config configs\dataset_v1.yaml --out data\v1
$env:PYTHONPATH="src"; python -m idforge.report --out data\v1
```

Expect roughly 40 minutes on two cores and about 1.5 GiB of output. Add
`--workers 4` (or however many cores you have) to speed it up; the number of
workers does **not** change the output, because every random draw is seeded from
the person identifier rather than from execution order.

The build prints a seven-stage progress log. Stage 3 is the important one: it
runs every validator against the ground-truth text of every document *before*
anything is rendered, and aborts with exit code 2 if any category fails to
produce its expected rule outcome.

---

## 6. Looking at the dataset on your own machine

**The images are ordinary JPEG files.** No special viewer is needed — File
Explorer, Preview, `eog`, anything.

```
data/v1/images/<split>/<doc_type>/<image_id>.jpg
```

for example

```
data/v1/images/train/aadhaar/P000042_aadhaar_C2_severe.jpg
data/v1/images/test/pan/P000117_pan_C00_clean.jpg
```

The `image_id` encodes everything: `P000042` is the person, `aadhaar` the
document type, `C2` the forgery category (`C00` and `C01` are the two unmodified
controls), `severe` the quality tier.

**To find specific examples**, filter `manifest.csv` in Excel or with pandas:

```python
import pandas as pd
m = pd.read_csv("data/v1/manifest.csv")

# every PAN document whose cross-field rule failed on ground-truth text
m[(m.doc_type == "pan") & (m.rule_gt_verdict == "FAIL")].head()

# genuine documents the rule branch wrongly flagged after OCR — the RQ6 cases
m[(m.forgery_category == "C0") & (m.rule_ocr_verdict == "FAIL")]

# side-by-side: one person's genuine and C2 Aadhaar at the clean tier
m[(m.person_id == "P000042") & (m.doc_type == "aadhaar")
  & (m.quality_tier == "clean")][["image_id", "forgery_category", "file"]]
```

**The paper figures** are written to `data/v1/figures/` as both PDF (for
`\includegraphics`) and PNG (for quick viewing):

| file | shows |
|---|---|
| `fig_specimens` | one person's Aadhaar and PAN across all five categories, with the modified region boxed |
| `fig_quality_tiers` | one document at clean / mild / severe |
| `fig_templates` | the three layout variants per document type |
| `fig_ocr_quality` | field exact-match rate by quality tier, with 95% CIs |
| `fig_phash_leakage` | the perceptual-hash distance structure behind the near-duplicate audit |

`figures/figure_provenance.json` records exactly which `image_id`s each figure
was drawn from, so any panel in the paper can be traced back to a file.

**The characterisation report** is `data/v1/stats/REPORT.md` (readable Markdown)
and `data/v1/stats/dataset_stats.json` (machine-readable).

---

## 7. Directory layout

```
idforge/
├── README.md
├── Makefile
├── requirements.txt
├── configs/
│   └── dataset_v1.yaml          # the released configuration
├── assets/fonts/                # the exact font binaries used to render
├── src/idforge/
│   ├── checksums.py             # Verhoeff D, P and inverse tables; §III-A
│   ├── identifiers.py           # Aadhaar and PAN synthesis; coincidence bound
│   ├── names.py                 # name corpus, three naming strata, Devanagari
│   ├── records.py               # identity-record generation; §IV-C
│   ├── photos.py                # procedural photograph and signature placeholders
│   ├── fontpaths.py             # deterministic font resolution
│   ├── templates.py             # card layouts, specimen overlay, field bboxes
│   ├── forgery.py               # categories C0–C4; §IV-E
│   ├── degrade.py               # quality tiers; §IV-F
│   ├── ocr.py                   # per-field Tesseract extraction; §IV-G
│   ├── validators.py            # the validators of §III-A and §III-B
│   ├── phash.py                 # 64-bit DCT perceptual hash
│   ├── splits.py                # grouped stratified partition; §IV-H
│   ├── leakage.py               # the five audits of Table V
│   ├── stats.py                 # characterisation report
│   ├── figures.py               # paper figures
│   ├── build.py                 # entry point: python -m idforge.build
│   └── report.py                # entry point: python -m idforge.report
├── tests/
│   ├── test_verhoeff.py
│   ├── test_validators.py
│   └── test_generators.py
└── docs/
    └── DATASHEET.md
```

`data/` is **not** committed. See Section 9.

---

## 8. Manifest schema

`manifest.jsonl` — one JSON object per image. `manifest.csv` is a flattened
subset for spreadsheet use.

| field | meaning |
|---|---|
| `image_id` | unique; `<person>_<doctype>_<category>_<tier>` |
| `document_id` | groups the three quality tiers of one document |
| `person_id` | **the split unit** |
| `split` | `train` / `val` / `test` |
| `doc_type` | `aadhaar` / `pan` |
| `forgery_category` | `C0`–`C4` |
| `control_index` | 0 or 1 for the two C0 controls, else null |
| `label` | 0 genuine, 1 forged |
| `quality_tier` | `clean` / `mild` / `severe` |
| `template_variant` | 0–2 |
| `naming_stratum` | `surname_last` / `initial_first` / `mononymic` |
| `pan_fifth_source` | which name token the PAN fifth character came from |
| `printed_values` | ground-truth text of every extracted field |
| `boxes` | field bounding boxes **in the degraded image's coordinates** |
| `ocr`, `ocr_parsed` | raw and minimally parsed Tesseract output |
| `ocr_exact`, `ocr_cer` | per-field exact match and character error rate |
| `rule_gt_verdict`, `rule_gt_detail` | validator output on ground-truth text |
| `rule_ocr_verdict`, `rule_ocr_detail` | validator output on OCR text |
| `expected_rule` | the outcome the design requires; asserted at build time |
| `forgery_field`, `gt_value`, `forged_value` | what was changed, for C2–C4 |
| `c1_op`, `c1_field`, `c1_region`, `c1_detail` | localisation ground truth for C1 |
| `render_seed`, `degrade_seed`, `jpeg_q_capture`, `phash` | provenance |

`boxes` being in degraded coordinates is what makes the RQ4 comparison possible:
the same field can be read from ground truth and from OCR of the *same* pixels.

---

## 9. Reproducibility, and why `data/` is not committed

Everything downstream of `seed` in the config is deterministic: identifiers,
names, template assignment, forgery choices, degradation draws and the split
assignment. Re-running with the same config and the pinned library versions
reproduces the corpus bit-for-bit, on any platform, with any number of workers.

This is tested, not asserted. Every per-artefact seed is derived with a
cryptographic digest rather than Python's `hash()`, which is salted per process
and would otherwise make each worker — and each run — produce different pixels
from the same nominal seed. `tests/test_generators.py` runs the seed function
under three `PYTHONHASHSEED` values and requires identical output. To check the
whole pipeline yourself:

```bash
PYTHONPATH=src python3 -m idforge.build --out /tmp/a --n-persons 3 --workers 1 --skip-ocr
PYTHONPATH=src python3 -m idforge.build --out /tmp/b --n-persons 3 --workers 2 --skip-ocr
diff -r /tmp/a/images /tmp/b/images && echo "bit-exact"
```

The images are therefore **derived artefacts**, and committing 1.5 GiB of
derived JPEGs to Git would be a mistake: Git stores every version forever, the
repository would become unusable to clone, and the images add nothing that the
seed does not already determine. What is committed is everything needed to
*produce* them.

For archival release, publish the built corpus as a versioned archive with a DOI
(Zenodo, or a GitHub Release) and cite that DOI alongside the commit hash. See
`docs/DATASHEET.md`.

If any of the pinned library versions differ on your machine, the *content* of
the dataset — values, labels, splits, ground truth — is unchanged, because it
derives from the seed rather than from the pixels; only the least significant
bits of the JPEG encoding may move.

---

## 9a. Verifying your rebuild against the released corpus

`dataset/data/v1/CORPUS_SHA256.txt` holds a deterministic hash over every image
in the corpus the paper reports on — each file's path and its exact bytes, in
sorted path order. After rebuilding:

```bash
python3 scripts/corpus_checksum.py data/v1 --verify
```

A match proves your images are byte-identical to the ones behind every number
in Section IV, without anyone having to transfer a gigabyte. A mismatch is
usually a library version differing from `requirements.txt`: the dataset
*content* — values, labels, splits, ground truth — still derives from the seed
and is unaffected, but the JPEG encoding can move by a few least-significant
bits.

## 10. Known limitations

Stated here rather than discovered by a reviewer.

1. **Synthetic-to-real gap.** The renders are format-faithful but not
   design-faithful, and the degradation chain is simulated rather than measured
   from real captures. A visual detector trained on this corpus may be either
   trivially strong or trivially weak relative to operational conditions. The
   corpus supports the *relative* comparison the paper makes; it does not
   support absolute performance claims.
2. **The photograph placeholder is not a face.** Face-level attacks such as
   morphing are out of scope and are not represented.
3. **Only Individual-category PANs appear in the image corpus.** The
   non-Individual branch of Algorithm 2 is covered by unit tests, not by images.
4. **No Devanagari OCR.** Only the English Tesseract model is used, so the
   Aadhaar C3 script-mismatch corruption is unreadable by the pipeline by
   construction — which is the intended negative control, but it also means the
   Aadhaar semantic gap is demonstrated rather than closed.
5. **`initial_first_p5_from_lead` is a modelling assumption, not a
   measurement.** It sets how often an initial-first record's PAN fifth
   character derives from the leading abbreviated token. Any result conditioned
   on `pan_fifth_source` is independent of it; corpus-level rates are not.
6. **The name corpus is authored, not sampled from a census.** It covers common
   Indian given names and surnames with reasonable regional spread, but it is
   not a representative sample of the population's name distribution.

---

## 11. Licence

Code: MIT (see `LICENSE`). Bundled fonts keep their own licences
(`assets/fonts/LICENSES.md`). Generated images and manifests: CC BY 4.0, subject
to the use restrictions in `docs/DATASHEET.md`.
