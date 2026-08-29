# Sample images from the corpus

These are committed to the repository so you can see what the dataset looks like without running anything. They are a hand-picked **28 images out of 10,800**; the full corpus is not committed (see [why](../dataset/README.md#9-reproducibility-and-why-data-is-not-committed)) and is regenerated from the code with one command.

> Every image here is synthetic. No real Aadhaar or PAN document, image or number was collected or used at any stage. The emblem is a placeholder, the issuing authority is fictitious, and every image carries a permanent SYNTHETIC SPECIMEN overlay. See [DATASHEET.md](DATASHEET.md).

---

## 1. The five forgery categories

One synthetic identity record rendered into all five categories, at the clean capture tier. Aadhaar-format first, then PAN-format. C2, C3 and C4 are **re-rendered from a modified record**, not pixel-edited, so they carry no visual trace at all — the only difference from C0 is the characters printed in one field.

### AADHAAR-format

| category | image | what changed |
|---|---|---|
| **C0** | <img src="samples/P000000_aadhaar_C00_clean.jpg" width="340"> | nothing — unmodified control |
| **C1** | <img src="samples/P000000_aadhaar_C1_clean.jpg" width="340"> | pixel edit (`field_displacement`), every printed value still valid |
| **C2** | <img src="samples/P000000_aadhaar_C2_clean.jpg" width="340"> | `859198193914` → `859168193914` |
| **C3** | <img src="samples/P000000_aadhaar_C3_clean.jpg" width="340"> | `किरण कुलकर्णी` → `पी. वरुण` |
| **C4** | <img src="samples/P000000_aadhaar_C4_clean.jpg" width="340"> | `859198193914` → `565501705056` |

### PAN-format

| category | image | what changed |
|---|---|---|
| **C0** | <img src="samples/P000000_pan_C00_clean.jpg" width="340"> | nothing — unmodified control |
| **C1** | <img src="samples/P000000_pan_C1_clean.jpg" width="340"> | pixel edit (`local_recompression`), every printed value still valid |
| **C2** | <img src="samples/P000000_pan_C2_clean.jpg" width="340"> | `TNZPK5344W` → `TNZIK5344W` |
| **C3** | <img src="samples/P000000_pan_C3_clean.jpg" width="340"> | `TNZPK5344W` → `TNZPO5344W` |
| **C4** | <img src="samples/P000000_pan_C4_clean.jpg" width="340"> | `TNZPK5344W` → `NYCPK6501M` |

## 2. The three capture-quality tiers

Every document is captured at three simulated quality tiers. Degradation is applied *after* forgery injection and drawn from the same distribution for every category, so image quality cannot act as a class cue.

| tier | Aadhaar | PAN |
|---|---|---|
| **clean** |  |  |
| **mild** | <img src="samples/P000000_aadhaar_C00_mild.jpg" width="330"> | <img src="samples/P000000_pan_C00_mild.jpg" width="330"> |
| **severe** | <img src="samples/P000000_aadhaar_C00_severe.jpg" width="330"> | <img src="samples/P000000_pan_C00_severe.jpg" width="330"> |

## 3. The six layout variants

Three templates per document type, differing in typeface pairing, accent colour, label placement, photograph side and background pattern density. Every variant appears in every split, which is one of the five leakage audits.

| variant | Aadhaar | PAN |
|---|---|---|
| **0** | <img src="samples/P000002_aadhaar_C00_clean.jpg" width="330"> | <img src="samples/P000002_pan_C00_clean.jpg" width="330"> |
| **1** | <img src="samples/P000003_aadhaar_C00_clean.jpg" width="330"> | <img src="samples/P000006_pan_C00_clean.jpg" width="330"> |
| **2** |  |  |

## 4. Genuine documents the rule branch wrongly flagged

These are the most useful images in the repository. Each is an **unmodified, genuine** synthetic document (category C0) that the deterministic validator accepted on ground-truth text and *rejected* after OCR — a false positive caused entirely by extraction error, not by anything wrong with the document.

Corpus-wide this happens on **4.1%** of genuine Aadhaar documents and **18.9%** of genuine PAN documents. The PAN rate is an order of magnitude higher because a PAN mixes letters and digits, so `0`/`O` and `I`/`1` confusions break the format rule. This is the cost side of structural validation and the reason the study measures it explicitly.

| document | tier | why the validator rejected it |
|---|---|---|
| <img src="samples/P000018_pan_C00_clean.jpg" width="300"> | clean | format: expected the pattern AAAAA9999A, extracted 'HUVPSO0964U' |
| <img src="samples/P000023_pan_C00_clean.jpg" width="300"> | clean | format: expected the pattern AAAAA9999A, extracted 'XAKPA06120' |
| <img src="samples/P000023_pan_C00_mild.jpg" width="300"> | mild | format: expected the pattern AAAAA9999A, extracted 'XAKPA06120' |
| <img src="samples/P000023_pan_C01_clean.jpg" width="300"> | clean | format: expected the pattern AAAAA9999A, extracted 'XAKPA06120' |
| <img src="samples/P000023_pan_C01_mild.jpg" width="300"> | mild | format: expected the pattern AAAAA9999A, extracted 'XAKPA06120' |
| <img src="samples/P000025_pan_C00_clean.jpg" width="300"> | clean | format: expected the pattern AAAAA9999A, extracted 'DHYPS4349I1' |
| <img src="samples/P000025_pan_C01_clean.jpg" width="300"> | clean | format: expected the pattern AAAAA9999A, extracted 'DHYPS4349I1' |
| <img src="samples/P000027_pan_C01_mild.jpg" width="300"> | mild | format: expected the pattern AAAAA9999A, extracted 'TICPBO562C' |
| <img src="samples/P000045_aadhaar_C00_clean.jpg" width="300"> | clean | format: expected exactly 12 decimal digits, extracted 13 character(s) ('2979823971537') |
| <img src="samples/P000045_aadhaar_C01_clean.jpg" width="300"> | clean | format: expected exactly 12 decimal digits, extracted 13 character(s) ('2979523971537') |

## 5. The paper figures

Generated directly from the corpus; `figure_provenance.json` in the dataset output records which `image_id` every panel came from.

**All five categories, both formats**

![All five categories, both formats](samples/fig_specimens.png)

**The three capture tiers**

![The three capture tiers](samples/fig_quality_tiers.png)

**The six layout variants**

![The six layout variants](samples/fig_templates.png)

**Per-field OCR exact-match by tier, 95% CIs**

![Per-field OCR exact-match by tier, 95% CIs](samples/fig_ocr_quality.png)

**Perceptual-hash distance distributions**

![Perceptual-hash distance distributions](samples/fig_phash_leakage.png)

---

## Finding specific images yourself

The full index of all 10,800 images is committed as [`dataset/data/v1/manifest.csv`](../dataset/data/v1/manifest.csv). Open it in a spreadsheet, or:

```python
import pandas as pd
m = pd.read_csv('dataset/data/v1/manifest.csv')

# genuine documents the rule branch wrongly flagged after OCR
m[(m.forgery_category=='C0') & (m.rule_ocr_verdict=='FAIL')]

# every PAN whose cross-field rule failed on ground-truth text
m[(m.doc_type=='pan') & (m.rule_gt_verdict=='FAIL')]
```

The `file` column gives the path each image will have once you regenerate the corpus with `make dataset`.
