# Structure-Aware Forgery Detection for Aadhaar and PAN

Code, dataset generator and paper source for

> **Structure-Aware Forgery Detection for Aadhaar and PAN: A Controlled Study
> of Visual, Structural, and Semantic Evidence Fusion**
> Ananya Shukla, Soham Phulwaria, Dinesh Saini — Manipal University Jaipur

The study measures how much a deterministic, document-specific consistency
check adds to a visual forgery detector for two Indian identity-document
formats — and what that addition costs in false positives on genuine
documents.

---

## Read this first

**Nothing in this repository is a real identity document, and nothing here can
be used as one.**

* Every identifier, name, date of birth, photograph and signature is
  **synthetic**. No real Aadhaar or PAN document, image or number was
  collected, downloaded, purchased or processed at any stage.
* No generated identifier was submitted to, resolved through, or checked
  against any UIDAI, Income Tax Department or third-party identity service.
* The card layouts are deliberately **format-faithful and design-unfaithful**:
  they reproduce the *field structure* of the two documents, because that is
  what the study measures, and reproduce **no** official emblem, seal,
  hologram, colour scheme or authority name. A geometric placeholder mark and a
  fictitious authority name are used instead, and every image carries a
  permanent `SYNTHETIC SPECIMEN` overlay.
* Structural validity is explicitly shown here **not** to establish
  authenticity. Forgery category C4 exists to demonstrate exactly that.

The full ethical statement, including a quantitative treatment of accidental
coincidence between generated and issued identifiers, is in
[`docs/DATASHEET.md`](docs/DATASHEET.md).

---

## Look at the dataset without running anything

**→ [`docs/SAMPLES.md`](docs/SAMPLES.md)** — a rendered gallery of the corpus:
all five forgery categories in both formats, the three capture-quality tiers,
the six layout variants, and ten *genuine* documents that the validator wrongly
rejected after OCR.

The complete index of all 10,800 images is committed as
[`dataset/data/v1/manifest.csv`](dataset/data/v1/manifest.csv), and the full
characterisation report is
[`dataset/data/v1/stats/REPORT.md`](dataset/data/v1/stats/REPORT.md).

---

## What is in the corpus

| | |
|---|---|
| synthetic identity records | 300 |
| documents | 3,600 (2 formats × 6 documents per record) |
| images | 10,800 (each document at 3 capture-quality tiers) |
| genuine (C0) / forged (C1–C4) | 3,600 / 7,200 |
| split, by person | 210/45/45 persons — 7,560/1,620/1,620 images |
| on disk when built | 0.874 GiB |
| build time | ~17 min on two cores |

**Forgery categories.** C0 unmodified control · C1 post-render pixel edit that
leaves every printed value valid · C2 structurally invalid identifier · C3
semantically inconsistent field pair · C4 fabricated identifier that satisfies
every rule. C2, C3 and C4 are produced by **re-rendering from a modified
record**, never by editing a rendered image, so the only evidence
distinguishing them from a genuine document is the content of the fields. That
construction is verified exactly, not assumed: before degradation a forged
document differs from its control in **0 pixels** outside the corrupted field,
across 320 comparisons.

---

## Two results the corpus already establishes

Neither requires a trained detector. Both are in
[`dataset/data/v1/stats/REPORT.md`](dataset/data/v1/stats/REPORT.md).

**1. Structural validation carries a real false-positive cost on genuine
documents, from OCR error alone.** On ground-truth text the rate is zero by
construction, so every one of these is an extraction failure:

| | clean | mild | severe | all |
|---|---|---|---|---|
| Aadhaar | 0.3% | 0.3% | 11.7% | **4.1%** |
| PAN | 12.7% | 12.2% | 31.8% | **18.9%** |

**2. The document type with *more* validation rules is the one that fails more
often on genuine documents.** PAN supports format, category and cross-field
checks where Aadhaar supports only format and checksum — but a PAN mixes
letters and digits, so it is recovered exactly on only
85.2% of clean captures against
99.8% for an Aadhaar
number, dominated by `0`/`O` and `I`/`1` confusions. More rules on a
harder-to-extract field means more ways to reject a genuine document.

---

## Repository layout

```
dataset/      the corpus generator — this is the finished part
  src/idforge/    Verhoeff, validators, templates, forgery, degradation, OCR,
                  splits, leakage audits, statistics, figures
  tests/          34 validator cases + generator invariants + seed stability
  data/v1/        manifest, splits, statistics and figures (images excluded)
docs/         SAMPLES.md, DATASHEET.md, DECISIONS.md, GITHUB_GUIDE.md
paper/        LaTeX source, auto-generated tables, figures
models/       Section V: visual branch and fusion            (not started)
experiments/  Sections VI–VII: run configs and result tables (not started)
analysis/     notebooks and statistical tests                (not started)
```

## Reproducing the corpus

```bash
cd dataset
pip install -r requirements.txt
make test                    # ~1 min, no images produced — run this first
bash scripts/build_all.sh    # ~25 min: corpus, audits, figures, LaTeX tables
```

You also need **Tesseract 5.x** on the PATH (`tesseract --version`). Fonts are
committed, so nothing else is required. Full step-by-step instructions,
including Windows, are in [`dataset/README.md`](dataset/README.md).

The build is deterministic: same config and same seed reproduce the corpus
bit-for-bit, on any platform, with any number of worker processes. That is
tested rather than asserted — see `tests/test_generators.py`.

## Citing

See [`CITATION.cff`](CITATION.cff). When citing the dataset, cite the
repository URL **and** the commit hash **and** the Tesseract version, because a
URL alone does not pin the code and `requirements.txt` cannot pin a system
binary that determines every OCR number reported.

## Licence

Code: MIT ([`LICENSE`](LICENSE)). Bundled fonts keep their own licences
(`dataset/assets/fonts/LICENSES.md`). Generated images and manifests: CC BY
4.0, subject to the use restrictions in [`docs/DATASHEET.md`](docs/DATASHEET.md).

