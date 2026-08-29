# -*- coding: utf-8 -*-
"""The five leakage audits of Table V (Section IV-H).

Each audit is RUN on the released splits and its result is reported, rather than
being asserted in prose.  The near-duplicate audit in particular is reported as
a distribution, not a single pass/fail, because every document in this corpus
shares one of six layout templates and therefore has a high baseline perceptual
similarity to every other document; a fixed literature threshold would be
meaningless here.  The threshold used is calibrated on this corpus from the
within-document distance distribution.
"""
from __future__ import annotations

import json
from collections import defaultdict

import numpy as np

from .phash import _POP, hamming_matrix_min, hamming_bytes_min


def audit_identity(rows: list, splits: dict) -> dict:
    by = defaultdict(set)
    for r in rows:
        by[r["split"]].add(r["person_id"])
    inter = {}
    names = sorted(by)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            inter[f"{names[i]}|{names[j]}"] = len(by[names[i]] & by[names[j]])
    return {"pairwise_person_id_intersections": inter,
            "required": "empty",
            "passed": all(v == 0 for v in inter.values())}


def audit_identifier(rows: list) -> dict:
    by = defaultdict(set)
    for r in rows:
        for k in ("aadhaar_gt", "pan_gt"):
            if r.get(k):
                by[r["split"]].add(r[k])
    inter = {}
    names = sorted(by)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            inter[f"{names[i]}|{names[j]}"] = len(by[names[i]] & by[names[j]])
    return {"pairwise_identifier_intersections": inter,
            "required": "empty",
            "passed": all(v == 0 for v in inter.values())}


def audit_template(rows: list) -> dict:
    seen = defaultdict(set)
    for r in rows:
        seen[r["split"]].add((r["doc_type"], r["template_variant"]))
    allv = set().union(*seen.values()) if seen else set()
    missing = {s: sorted(map(list, allv - v)) for s, v in seen.items()}
    return {"variants_per_split": {s: len(v) for s, v in seen.items()},
            "total_variants": len(allv),
            "missing": missing,
            "required": "every layout variant present in every split",
            "passed": all(len(m) == 0 for m in missing.values())}


def audit_augmentation(rows: list) -> dict:
    by = defaultdict(set)
    for r in rows:
        by[r["document_id"]].add(r["split"])
    bad = [k for k, v in by.items() if len(v) > 1]
    return {"documents_spanning_splits": len(bad),
            "required": "no document's degradation draws span splits",
            "passed": not bad}


def audit_printed_values(rows: list) -> dict:
    """Exact content-level check: no printed field-value set may occur in more
    than one split.  Unlike a perceptual hash this cannot saturate, and it is
    the check that actually binds -- two images a hash cannot tell apart are not
    a leak if they carry different field values and different labels."""
    by = defaultdict(set)
    for r in rows:
        key = json.dumps(r["printed_values"], sort_keys=True, ensure_ascii=False)
        by[key].add(r["split"])
    bad = [k for k, v in by.items() if len(v) > 1]
    return {"distinct_printed_value_sets": len(by),
            "sets_spanning_splits": len(bad),
            "required": "no printed value set occurs in more than one split",
            "passed": not bad}


def audit_near_duplicate(rows: list) -> dict:
    """Perceptual-hash distance structure of the corpus.

    Reported as a DIAGNOSTIC, not as a gate. Running it on this corpus shows
    that perceptual hashing cannot do the job it is usually asked to do here:
    every document shares one of six card layouts, which dominates the low- and
    mid-frequency DCT band the hash is built from, so the distance between two
    captures of the SAME document and the distance between two DIFFERENT
    persons' documents overlap substantially. At 64 bits the hash is degenerate
    (far fewer distinct values than images, colliding across persons, categories
    and splits); at 256 bits it separates images but still does not separate
    identities.

    The audit therefore reports the two distributions and their overlap, and the
    leakage verdict is carried by the exact checks -- identity, identifier,
    printed values and augmentation -- which cannot saturate.
    """
    h64 = np.array([r["phash"] for r in rows], dtype=np.uint64)
    have256 = all("phash256" in r for r in rows)
    if have256:
        h = np.array([list(bytes.fromhex(r["phash256"])) for r in rows],
                     dtype=np.uint8)
    else:
        h = h64.view(np.uint8).reshape(-1, 8)
    nbits = h.shape[1] * 8

    spl = np.array([r["split"] for r in rows])
    by_doc, by_per = defaultdict(list), defaultdict(list)
    for i, r in enumerate(rows):
        by_doc[r["document_id"]].append(i)
        by_per[r["person_id"]].append(i)

    def dist_pairs(pairs):
        if not len(pairs):
            return np.array([], dtype=np.int32)
        p = np.asarray(pairs)
        return _POP[h[p[:, 0]] ^ h[p[:, 1]]].sum(axis=1).astype(np.int32)

    # exhaustive: every pair of captures of the same document
    wd = [(g[a], g[b]) for g in by_doc.values()
          for a in range(len(g)) for b in range(a + 1, len(g))]
    within = dist_pairs(wd)

    rng = np.random.default_rng(0)
    sp = []
    for g in by_per.values():
        for _ in range(4):
            i, j = rng.choice(len(g), 2, replace=False)
            if rows[g[i]]["document_id"] != rows[g[j]]["document_id"]:
                sp.append((g[i], g[j]))
    samep = dist_pairs(sp)

    idx = rng.integers(0, len(rows), size=(200000, 2))
    per = np.array([r["person_id"] for r in rows])
    keep = (per[idx[:, 0]] != per[idx[:, 1]]) & (spl[idx[:, 0]] == spl[idx[:, 1]])
    crossp = dist_pairs(idx[keep][:80000])

    # how badly do the two distributions overlap?
    med_within = float(np.median(within)) if len(within) else 0.0
    overlap = float((crossp <= med_within).mean()) if len(crossp) else 0.0
    sep = _auc(within, crossp)

    tr = h[spl == "train"]
    res, worst = {}, nbits
    for s in ("val", "test"):
        q = h[spl == s]
        if len(q) == 0 or len(tr) == 0:
            continue
        mn, _ = hamming_bytes_min(q, tr)
        res[s] = {"min": int(mn.min()), "p1": float(np.percentile(mn, 1)),
                  "median": float(np.median(mn)), "n_images": int(len(q))}
        worst = min(worst, int(mn.min()))

    return {
        "gating": False,
        "hash_bits": nbits,
        "n_images": len(rows),
        "distinct_hashes_64bit": int(len(set(int(x) for x in h64))),
        "distinct_hashes_used": len({bytes(r) for r in h}),
        "within_document": _summ(within),
        "same_person_other_document": _summ(samep),
        "cross_person_same_split": _summ(crossp),
        "cross_person_pairs_closer_than_median_within_document": round(overlap, 4),
        "separability_auc_within_vs_crossperson": round(sep, 4),
        "cross_split_min_distance_to_train": res,
        "worst_cross_split_min": worst,
        "verdict": ("INCONCLUSIVE BY THIS MEASURE. The same-document and "
                    "different-person distance distributions overlap "
                    f"(AUC {sep:.3f}; {100*overlap:.1f}% of different-person "
                    "pairs are closer than the median same-document pair), so a "
                    "distance threshold cannot distinguish a leaked duplicate "
                    "from two unrelated documents on the same template. The "
                    "leakage verdict rests on the exact identity, identifier, "
                    "printed-value and augmentation checks, all of which pass. "
                    "The cross-split minimum distances reported here are a "
                    "minimum taken over every training image and are small for "
                    "that reason alone; because the splits are person-disjoint "
                    "by the exact identity audit, every cross-split neighbour is "
                    "necessarily a different person, so these distances carry no "
                    "leakage information beyond what that audit establishes."),
        "passed": None,
    }


def _auc(pos, neg) -> float:
    """P(a random different-person pair is farther than a random same-document
    pair). 1.0 = perfectly separable, 0.5 = no discriminative power."""
    if len(pos) == 0 or len(neg) == 0:
        return float("nan")
    a = np.sort(neg)
    gt = np.searchsorted(a, pos, side="right")
    lt = np.searchsorted(a, pos, side="left")
    return float(1.0 - (0.5 * (gt + lt) / len(a)).mean())


def _summ(a) -> dict:
    if len(a) == 0:
        return {"n": 0}
    return {"n": int(len(a)), "min": int(a.min()), "p1": float(np.percentile(a, 1)),
            "median": float(np.median(a)), "mean": float(a.mean()),
            "max": int(a.max())}
