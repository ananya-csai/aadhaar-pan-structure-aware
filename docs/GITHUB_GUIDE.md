# Putting this on GitHub — and what to cite in the paper

Your supervisor's requirement ("a repository for every technical artefact, kept
as a record") and the paper's requirement (a reviewer must be able to reproduce
the dataset) are satisfied by the same repository, but they pull in slightly
different directions. The record wants everything; the paper wants one exact,
citable state. Handle both by **committing only what regenerates the data**, and
**tagging plus archiving** the state that produced the numbers in the paper.

---

## 1. Decide the repository shape first

Use **one repository for the whole project**, not one per artefact. Reviewers
follow one link; your supervisor sees one commit history; and the dataset code,
the model code and the analysis notebooks stay version-locked to each other.

```
aadhaar-pan-structure-aware/     <- the repository
├── dataset/                     <- what you have now (this idforge tree)
├── models/                      <- Section V: visual branch, fusion
├── experiments/                 <- Section VI-VII: run configs, result tables
├── analysis/                    <- notebooks, statistical tests, plots
├── paper/                       <- .tex, generated tables, figures
└── docs/                        <- datasheet, decisions log
```

Move the current tree into `dataset/` when you add the model code. Do it *before*
you have collaborators and history to rewrite.

**Public or private?** Private until submission; public at submission. Two
reasons to go public rather than keep it private and email a zip: reviewers of
applied venues increasingly check, and a public commit history is far stronger
evidence of your own work than a folder of files.

**If the venue is double-blind**, do not put your names in the repository during
review. Serve an anonymised mirror through <https://anonymous.4open.science>,
which takes a GitHub URL and gives back an anonymous one, and put that link in
the submitted paper. Swap it for the real URL in the camera-ready.

---

## 2. What to commit, and what never to commit

**Commit:** all source, `configs/`, `tests/`, `requirements.txt`, `Makefile`,
`README.md`, `docs/`, `LICENSE`, the font binaries in `assets/fonts/` (13 MB —
they are what makes rendering reproducible), and the generated LaTeX tables and
macros in `paper/generated/`.

**Never commit:** `data/`. The corpus is ~0.9 GiB of JPEGs that the seed already
determines. Git keeps every version of every file forever, so committing it once
makes the repository permanently ~1 GB to clone, and committing it twice makes
it 2 GB. The `.gitignore` in this repository already excludes it.

This is not a shortcut — it is the stronger claim. "The images are a
deterministic function of this commit and this seed" is a better reproducibility
statement than "here are some images."

**Git LFS:** you do not need it for this repository. The largest committed file
is a 3.7 MB font. Set LFS up only if you later commit model checkpoints, and if
you do, remember the free LFS quota is 1 GB of storage and 1 GB/month of
bandwidth — a public repo with a popular checkpoint can exhaust it.

---

## 3. Creating and pushing the repository

### With the GitHub web interface

1. Go to <https://github.com/new>.
2. Name it `aadhaar-pan-structure-aware`. Set it **Private** for now. Do **not**
   let GitHub add a README, `.gitignore` or licence — you already have them.
3. On your machine:

```bash
cd path/to/idforge
git init
git branch -M main
git add .
git status                      # <- READ THIS. Confirm no data/ files are staged.
git commit -m "Dataset construction pipeline for Section IV"
git remote add origin https://github.com/<your-username>/aadhaar-pan-structure-aware.git
git push -u origin main
```

`git status` before the first commit is the step people skip and regret. If you
see anything under `data/`, stop and fix `.gitignore` first — removing a large
file from history later means rewriting it.

### With the GitHub CLI (faster)

```bash
gh auth login
cd path/to/idforge
git init && git branch -M main && git add . && git commit -m "Dataset construction pipeline for Section IV"
gh repo create aadhaar-pan-structure-aware --private --source=. --push
```

### Authentication

GitHub does not accept account passwords over HTTPS. Either use the GitHub CLI
(which handles it), or create a **fine-grained personal access token** at
Settings → Developer settings → Personal access tokens, with Contents:
read/write on this repository, and paste it when Git asks for a password.

---

## 4. Making the repository readable to a reviewer

A reviewer spends about ninety seconds deciding whether your artefact is
credible. Give them, in this order:

1. **A README that starts with what it is and what it is not.** Yours does; the
   ethics statement is deliberately first, because that is the first question an
   identity-document paper raises.
2. **Tests that run in one command and pass.** `make test`. This is the single
   highest-value item: it shows the Verhoeff implementation is checked against
   the published worked examples and exhaustively against the two error classes
   the algorithm guarantees, and that every forgery category produces the rule
   outcome the experiment assumes.
3. **A `CITATION.cff`** (included) so GitHub renders a "Cite this repository"
   button.
4. **A short decisions log** in `docs/`. Every non-obvious choice with its
   reason — flat versus position-aware OCR whitelist, re-render versus pixel-edit
   for C2–C4, why the near-duplicate audit is diagnostic. When a reviewer asks
   "why did you do X", you paste from this file instead of reconstructing the
   reasoning six months later. This is also exactly the "record" your supervisor
   is asking for.

Add a CI workflow so the tests run on every push and the badge shows green:

```yaml
# .github/workflows/tests.yml
name: tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: {python-version: "3.11"}
      - run: sudo apt-get update && sudo apt-get install -y tesseract-ocr
      - run: pip install -r requirements.txt
      - run: make test
```

---

## 5. Archiving the built corpus and getting a DOI

A GitHub URL is not a citable artefact: branches move and repositories can be
deleted. Journals and the better conferences increasingly expect a DOI.

**Zenodo** is the standard route and is free.

1. Sign in to <https://zenodo.org> with your GitHub account.
2. Under **GitHub** in your Zenodo settings, flip the switch **on** for this
   repository.
3. Back on GitHub, create a release: **Releases → Draft a new release**, tag
   `v1.0-dataset`, title it, and attach the corpus archive as a release asset.

```bash
cd data
zip -r -q aadhaar-pan-synthetic-v1.zip v1
sha256sum aadhaar-pan-synthetic-v1.zip > aadhaar-pan-synthetic-v1.zip.sha256
```

4. Publishing the release makes Zenodo mint a DOI automatically and archive the
   repository state.

**Size limits to know before you start.** A single GitHub release asset may be up
to 2 GB, so the ~0.9 GiB archive fits. Zenodo's default per-record limit is
50 GB. If you later exceed a limit, split by split (`train.zip`, `val.zip`,
`test.zip`) rather than compressing harder — JPEGs do not compress further, so
your zip will be roughly the size of the directory.

**Always publish the checksum** next to the archive. It is what lets someone
verify they got the same corpus you did.

---

## 6. What goes in the paper

In the reproducibility statement, cite three things, not one:

> The dataset generation code, configuration and manifest are available at
> `https://github.com/<user>/aadhaar-pan-structure-aware` (commit `abc1234`).
> The built corpus is archived at `https://doi.org/10.5281/zenodo.XXXXXXX`.
> Generation used Tesseract 5.3.4 and the Python versions pinned in
> `requirements.txt`.

Why all three: the URL locates it, **the commit hash pins the exact code** (a URL
alone does not — `main` moves), the DOI guarantees the artefact outlives the
repository, and the Tesseract version is the one dependency `requirements.txt`
cannot pin because it is a system binary, and it directly determines every OCR
number in Section IV.

Get the commit hash with:

```bash
git rev-parse --short HEAD
```

Tag the state that produced the submitted numbers, so you can return to it after
you keep working:

```bash
git tag -a v1.0-paper-submission -m "State producing the Section IV numbers"
git push origin v1.0-paper-submission
```

---

## 7. Working habits that will save you later

* **Commit small and often, with messages that say why.** `git commit -m "Use
  256-bit pHash: the 64-bit hash collides across persons on a templated corpus"`
  is a record. `git commit -m "fix"` is not. Your supervisor's requirement is
  really a request for a legible history.
* **Never rebuild the dataset into the same directory while an experiment is
  running against it.** Build to `data/v2`, compare, then switch.
* **When a number in the paper changes, it should be because the data changed.**
  `scripts/export_latex.py` writes every Section IV numeral into
  `paper/generated/numbers.tex` straight from the corpus, so the two cannot drift
  apart. Do not hand-edit that file; regenerate it.
* **Record the Tesseract version in the release notes.** It is the one thing
  `requirements.txt` cannot capture, and it moves your OCR numbers.
* **Branch for anything experimental.** `git switch -c ocr-second-engine`. If it
  works, merge; if not, the history shows you tried, which is itself part of the
  record.
