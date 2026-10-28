# Literature search record (paper Section II-E)

Run on **28 Oct 2026** with `crossref_search.py` in this folder.

## Protocol

- **Source:** Crossref REST API (`query.bibliographic`), which indexes DOI-registered journal articles, proceedings papers, book chapters and preprints from IEEE, ACM, Springer, Elsevier and most other publishers. arXiv is not indexed by Crossref; Semantic Scholar and OpenAlex were rate-limited from the search machine on that day and were not used.
- **Queries:** every combination of the three term groups below (4 × 4 × 4 = 64 queries).
  - G1: Aadhaar, PAN card, Indian identity document, identity document
  - G2: forgery, tampering, verification, OCR
  - G3: checksum, structural validation, semantic consistency, field consistency
- **Filters:** publication date 2015-01-01 to 2026-10-28; types journal-article, proceedings-article, book-chapter, posted-content.
- **Cut-off:** the 40 most relevant records per query, by Crossref's own relevance ranking. Crossref matching is loose, so most returned records are off-topic; the cut-off bounds the screening effort and is a limitation.
- **Supplementary search (not systematic):** a general web search on the same day for preprints and work outside Crossref. It added Kumar et al., *Field-Localized Forgery Detection for Digital Identity Documents*, arXiv:2605.09089 (cited). It also found Kubam, *Agentic AI Microservice Framework for Deepfake and Document Fraud Detection in KYC Pipelines*, arXiv:2601.06241 (also published in JISEM 2024). That one was assessed and not cited: generic IDs, no check-digit or cross-field rules, no OCR oracle.

## Counts

| Stage | Count |
|---|---|
| Records returned (64 × 40) | 2,560 (`raw.jsonl`) |
| Distinct works (by DOI) | 573 (`records.csv`) |
| Included on title | 68: 12 Aadhaar/PAN, 13 other identity documents, 43 other official, financial or legal documents |
| Of which preprints (`posted-content`) | 7 |
| Assessed beyond the title (abstract or full text) | 8, including 5 of the 12 Aadhaar/PAN works |

Every decision is in `screening.csv` (`decision`, `assessed_in_detail`).

**Inclusion:** forgery detection or field-level verification for identity or official documents.
**Exclusion:** presentation attacks, biometric-only manipulation, non-document imagery, non-technical work.

## Not yet assessed — open item for the authors

The full texts of these Aadhaar/PAN works were not accessible from the search machine. The paper makes no claim about the checks they apply. Reading them with institutional access would let the authors strengthen or correct the gap statement in Section II-B:

| Index | Work | DOI |
|---|---|---|
| 130 | Patil, Khan, Mollah, NetraAadhaar, IEEE Access 2025 | 10.1109/access.2025.3563786 |
| 135 | Khan et al., Automated Identity Verification: From Aadhaar to Instant Virtual PAN Issuance, 2026 | 10.1109/aimlcps68702.2026.11542414 |
| 137 | A et al., Automatic Aadhaar Card and Smart Card Verification using Image Processing Techniques, ICSCDS 2025 | 10.1109/icscds65426.2025.11167138 |
| 236 | Hamza, Kavitha, Patil, Decentralized PAN Card Forgery and Tampering Detection…, CCIS 2026 (cited) | 10.1007/978-3-032-17840-4_17 |
| 293 | Lalsudhesh et al., PAN Card Tampering Detection using ML Techniques, ICICI 2024 (cited) | 10.1109/icici62254.2024.00059 |
| 320 | Enhancing PAN Card Security with OCR-Based Information Extraction and Face Recognition, ICDSAAI 2025 | 10.1109/icdsaai65575.2025.11011855 |
| 353 | Arora, Ishwar, Verma, Pan card tempering detection: a combined OCR and CNN methodology, CRC 2025 (cited) | 10.1201/9781003593034-62 |

## Re-running

    python docs/literature_search/crossref_search.py

Crossref's index and relevance ranking change over time, so a re-run will not return exactly the same records. The committed `raw.jsonl` is the record of this search.
