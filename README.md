# Structure-Aware Forgery Detection for Aadhaar and PAN

Code, dataset generator, experiment records and paper source for

> **Structure-Aware Forgery Detection for Aadhaar and Permanent Account Number
> Cards: A Controlled Study of Visual, Structural, and Semantic Evidence Fusion**
>
> Ananya Shukla<sup>†</sup> ([ORCID](https://orcid.org/0009-0004-9412-5580)),
> Soham Phulwaria<sup>†</sup> ([ORCID](https://orcid.org/0009-0001-8071-1480)),
> Dinesh Kumar Saini ([ORCID](https://orcid.org/0000-0002-5140-1731))
> — Manipal University Jaipur, India
>
> <sup>†</sup> Equal contribution; shared first authorship.

**Status:** experiments complete; manuscript prepared for journal submission
([`paper/`](paper/)).

The study measures how much deterministic, document-specific consistency
checks (the Verhoeff check digit of an Aadhaar number; the format, category
and name-initial rules of a PAN) add to a visual forgery detector, how much of
that gain survives real OCR, and what it costs in false positives on genuine
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

## Main results

Test split scored once, under a protocol frozen on validation data
([`DECISIONS.md`](DECISIONS.md)); 5% false-positive budget.

| | Recall (all forged) | FPR (genuine) |
|---|---|---|
| Visual branch alone (tile ResNet-50) | 13.4% | 4.8% |
| Visual + rules, ground-truth text (A4) | 48.8% | 4.8% |
| Visual + rules, OCR text (A4) | 21.9% | 4.1% |
| Visual + rules, OCR text, one weight per check (A5, post-hoc) | 36.1% | 5.0% |

* With OCR text the rules alone flag 10.9% of genuine documents. Most of
  these are PAN format failures caused by character misreads (41 of the 270
  genuine PANs in the test split).
* A5 was designed after the test run, so it was confirmed on a fresh,
  pre-registered set of 90 unseen people: +12.6 points of recall over A4
  (95% CI [11.2, 14.1]), with no measurable increase in false positives
  ([`experiments/fresh/`](experiments/fresh/)).
* Fabricated identifiers that pass every rule (C4) are flagged only at about
  each system's false-positive rate: a passed checksum is not evidence of
  authenticity.

Full tables: [`experiments/results/`](experiments/results/).

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

| | |
|---|---|
| synthetic identity records | 300 |
| documents | 3,600 (2 formats × 6 documents per record) |
| images | 10,800 (each document at 3 capture-quality tiers) |
| genuine (C0) / forged (C1–C4) | 3,600 / 7,200 |
| split, by person | 210/45/45 persons — 7,560/1,620/1,620 images |
| fresh confirmation set | 90 further persons, 3,240 images (seed 20261021) |

**Forgery categories.** C0 unmodified control · C1 post-render pixel edit that
leaves every printed value valid · C2 structurally invalid identifier · C3
semantically inconsistent field pair · C4 fabricated identifier that satisfies
every rule. C2, C3 and C4 are produced by **re-rendering from a modified
record**, never by editing a rendered image, so the only evidence
distinguishing them from a genuine document is the content of the fields.
Before degradation a forged document differs from its control in **0 pixels**
outside the corrupted field, across 320 comparisons.

---

## Repository layout

```
dataset/        corpus generator (idforge): Verhoeff, validators, templates,
                forgery injection, capture simulation, OCR, grouped splits,
                leakage audits; tests; manifests and statistics (no images)
experiments/    every experiment in the paper: visual branch (e2_visual),
                rule branch (e3_rule_branch, rules), fusion, fresh set,
                analyses, frozen parameters, results and run logs
paper/          paper source: jfs/ (current journal version), wiley/ (master
                text), IEEE version, generated tables, figures
docs/           DATASHEET, SAMPLES, REPRODUCIBILITY, dataset DECISIONS,
                ROADMAP, literature-search record; archive/ holds old notes
DECISIONS.md    the experiment protocol and every amendment to it (frozen)
CITATION.cff    how to cite the code, data and paper
```

`experiments/README.md` maps each folder to the section of the paper it
supports.

## Reproducing

* **Corpus:**

  ```bash
  cd dataset
  pip install -r requirements.txt
  make test                    # ~1 min, no images produced — run this first
  bash scripts/build_all.sh    # ~25 min: corpus, audits, figures, LaTeX tables
  ```

  You also need **Tesseract 5.x** on the PATH (`tesseract --version`). Fonts
  are committed. Full instructions, including Windows, are in
  [`dataset/README.md`](dataset/README.md).
* **Experiments and every number in the paper:**
  [`docs/REPRODUCIBILITY.md`](docs/REPRODUCIBILITY.md) gives the commands, the
  four levels of reproduction (scoring, inference, corpus, training) and the
  SHA-256 digest of every frozen file. CI re-scores the validation split with
  the frozen parameters on every push and checks that the paper tables
  regenerate exactly.
* **Paper:** see [`paper/README.md`](paper/README.md).

## AI assistance

During the preparation of this work, the authors used Claude (Anthropic) to
assist with drafting and language editing of the manuscript and analysis
scripting. Claude was also used to help optimise code and to debug problems
that came up in the code. The authors designed the study, made all
methodological decisions, ran the experiments, and reviewed, revised and
verified all text, code and results themselves. The authors take full
responsibility for the content of this work.

Commits whose message ends with `Co-Authored-By: Claude` were made with this
assistance, which is why Claude appears in the repository's contributor
graph. The same use is declared in the paper.

## Citing

See [`CITATION.cff`](CITATION.cff). When citing the dataset, cite the
repository URL **and** the commit hash **and** the Tesseract version, because a
URL alone does not pin the code and `requirements.txt` cannot pin a system
binary that determines every OCR number reported.

## Licence

Code: MIT ([`LICENSE`](LICENSE)). Bundled fonts keep their own licences
(`dataset/assets/fonts/LICENSES.md`). Generated images and manifests: CC BY
4.0, subject to the use restrictions in [`docs/DATASHEET.md`](docs/DATASHEET.md).
