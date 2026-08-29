# -*- coding: utf-8 -*-
"""Dataset characterisation (Section IV composition, OCR quality, audits).

IMPORTANT SCOPE NOTE.  Everything computed here characterises the DATASET and
the rule branch operating on it.  None of it is a detection result for the
hybrid system: no visual model is trained here, and no fusion is performed.
Numbers produced by this module belong in Section IV and, where they concern
OCR degradation and rule-branch false positives, are the inputs that Sections
VI-B and VII-D/VII-F will build on.  They are NOT Section VII results.
"""
from __future__ import annotations

import json
import math
import os
from collections import Counter, defaultdict

import numpy as np

from .leakage import (audit_augmentation, audit_identifier, audit_identity,
                      audit_near_duplicate, audit_printed_values,
                      audit_template)
from .identifiers import (AADHAAR_PAYLOAD_SPACE, PAN_SPACE_CONSTRAINED,
                          coincidence_bound)
from .ocr import parse_field

TIER_ORDER = ["clean", "mild", "severe"]
CATS = ["C0", "C1", "C2", "C3", "C4"]


def wilson(k: int, n: int, z: float = 1.959963985) -> tuple:
    """Wilson score interval; correct at the small per-cell counts used here."""
    if n == 0:
        return (float("nan"), float("nan"), float("nan"))
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (p, max(0.0, c - h), min(1.0, c + h))


def _fmt_ci(k, n):
    p, lo, hi = wilson(k, n)
    if n == 0:
        return "-"
    return f"{100*p:.1f} [{100*lo:.1f}, {100*hi:.1f}]"


def compute(rows: list, records: list, out_dir: str) -> dict:
    S = {}

    # ---------------- composition -------------------------------------
    comp = defaultdict(int)
    for r in rows:
        comp[(r["doc_type"], r["forgery_category"], r["quality_tier"])] += 1
    S["totals"] = {
        "persons": len({r["person_id"] for r in rows}),
        "documents": len({r["document_id"] for r in rows}),
        "images": len(rows),
        "images_genuine": sum(1 for r in rows if r["label"] == 0),
        "images_forged": sum(1 for r in rows if r["label"] == 1),
    }
    S["composition"] = {f"{a}/{b}/{c}": n for (a, b, c), n in sorted(comp.items())}
    S["composition_by_cell"] = {
        f"{d}/{c}": sum(comp[(d, c, t)] for t in TIER_ORDER)
        for d in ("aadhaar", "pan") for c in CATS}
    S["split_sizes"] = dict(Counter(r["split"] for r in rows))
    S["split_persons"] = {s: len({r["person_id"] for r in rows if r["split"] == s})
                          for s in sorted({r["split"] for r in rows})}
    S["naming_strata_persons"] = dict(Counter(r.naming_stratum for r in records))
    S["pan_fifth_source_persons"] = dict(Counter(r.pan_fifth_source for r in records))
    S["template_variants"] = dict(Counter(
        f"{r['doc_type']}/v{r['template_variant']}" for r in rows))
    S["honorific_rate_persons"] = round(
        sum(1 for r in records if r.honorific) / max(1, len(records)), 4)

    # ---------------- storage -----------------------------------------
    tot = 0
    per_tier = defaultdict(list)
    for r in rows:
        p = os.path.join(out_dir, r["file"])
        if os.path.exists(p):
            sz = os.path.getsize(p)
            tot += sz
            per_tier[r["quality_tier"]].append(sz)
    S["storage"] = {
        "total_bytes": tot, "total_gib": round(tot / 2 ** 30, 3),
        "mean_kib_by_tier": {t: round(np.mean(v) / 1024, 1)
                             for t, v in per_tier.items()},
        "mean_pixels_by_tier": {
            t: int(np.mean([r["width"] * r["height"] for r in rows
                            if r["quality_tier"] == t])) for t in TIER_ORDER},
    }

    # ---------------- rule branch on GROUND-TRUTH text ------------------
    gt = defaultdict(Counter)
    for r in rows:
        gt[(r["doc_type"], r["forgery_category"])][r["rule_gt_verdict"]] += 1
    S["rule_on_ground_truth"] = {f"{a}/{b}": dict(c) for (a, b), c in sorted(gt.items())}

    # ---------------- OCR quality --------------------------------------
    ex = defaultdict(lambda: [0, 0])
    ce = defaultdict(list)
    empty = defaultdict(lambda: [0, 0])
    for r in rows:
        if not r.get("ocr_parsed"):
            continue
        for fld, ok in r["ocr_exact"].items():
            k = (r["doc_type"], fld, r["quality_tier"])
            ex[k][0] += ok
            ex[k][1] += 1
            ce[k].append(r["ocr_cer"][fld])
            empty[k][0] += int(r["ocr_parsed"].get(fld, "") == "")
            empty[k][1] += 1
    S["ocr"] = {}
    for k in sorted(ex):
        kk = "/".join(k)
        p, lo, hi = wilson(ex[k][0], ex[k][1])
        S["ocr"][kk] = {
            "n": ex[k][1],
            "exact_match_pct": round(100 * p, 2),
            "ci95": [round(100 * lo, 2), round(100 * hi, 2)],
            "mean_cer_pct": round(100 * float(np.mean(ce[k])), 3),
            "empty_extraction_pct": round(100 * empty[k][0] / max(1, empty[k][1]), 2),
        }

    # character confusions on the two identifier fields
    conf = Counter()
    for r in rows:
        if not r.get("ocr_parsed"):
            continue
        for fld in ("aadhaar_number", "pan_number"):
            if fld not in r["printed_values"]:
                continue
            ref = parse_field(fld, r["printed_values"][fld])
            hyp = r["ocr_parsed"].get(fld, "")
            if len(ref) == len(hyp):
                for a, b in zip(ref, hyp):
                    if a != b:
                        conf[f"{a}->{b}"] += 1
    S["identifier_character_confusions_top20"] = dict(conf.most_common(20))

    # ---------------- rule branch on OCR text --------------------------
    ocrv = defaultdict(Counter)
    for r in rows:
        if r.get("rule_ocr_verdict"):
            ocrv[(r["doc_type"], r["forgery_category"], r["quality_tier"])][
                r["rule_ocr_verdict"]] += 1
    S["rule_on_ocr"] = {"/".join(k): dict(v) for k, v in sorted(ocrv.items())}

    # verdict flips attributable to OCR
    flips = defaultdict(lambda: Counter())
    for r in rows:
        if not r.get("rule_ocr_verdict"):
            continue
        a, b = r["rule_gt_verdict"], r["rule_ocr_verdict"]
        key = (r["doc_type"], r["forgery_category"], r["quality_tier"])
        if a == b:
            flips[key]["stable"] += 1
        elif a == "PASS" and b == "FAIL":
            flips[key]["ocr_induced_failure"] += 1
        else:
            flips[key]["ocr_masked_failure"] += 1
    S["ocr_induced_verdict_flips"] = {"/".join(k): dict(v)
                                      for k, v in sorted(flips.items())}

    # ---------------- RQ6 input: false positives on genuine documents ---
    fp = {}
    for dt in ("aadhaar", "pan"):
        for t in TIER_ORDER + ["ALL"]:
            sel = [r for r in rows if r["doc_type"] == dt and r["label"] == 0
                   and r.get("rule_ocr_verdict")
                   and (t == "ALL" or r["quality_tier"] == t)]
            k = sum(1 for r in sel if r["rule_ocr_verdict"] == "FAIL")
            fp[f"{dt}/{t}"] = {"n": len(sel), "fp": k, "pct_ci": _fmt_ci(k, len(sel))}
    S["rule_false_positive_on_genuine_ocr"] = fp

    fp_gt = {}
    for dt in ("aadhaar", "pan"):
        sel = [r for r in rows if r["doc_type"] == dt and r["label"] == 0]
        k = sum(1 for r in sel if r["rule_gt_verdict"] == "FAIL")
        fp_gt[dt] = {"n": len(sel), "fp": k, "pct_ci": _fmt_ci(k, len(sel))}
    S["rule_false_positive_on_genuine_groundtruth"] = fp_gt

    fp_ns = {}
    for ns in sorted({r["naming_stratum"] for r in rows}):
        sel = [r for r in rows if r["doc_type"] == "pan" and r["label"] == 0
               and r["naming_stratum"] == ns and r.get("rule_ocr_verdict")]
        k = sum(1 for r in sel if r["rule_ocr_verdict"] == "FAIL")
        fp_ns[ns] = {"n": len(sel), "fp": k, "pct_ci": _fmt_ci(k, len(sel))}
    S["pan_false_positive_by_naming_stratum_ocr"] = fp_ns

    # ---------------- permissive vs strict semantic rule ----------------
    ps = {}
    for key, sel_fn in (
        ("ALL", lambda r: True),
        ("surname_last", lambda r: r["naming_stratum"] == "surname_last"),
        ("initial_first", lambda r: r["naming_stratum"] == "initial_first"),
        ("mononymic", lambda r: r["naming_stratum"] == "mononymic"),
        ("p5src:leading_initial", lambda r: r["pan_fifth_source"] == "leading_initial"),
        ("p5src:given_name", lambda r: r["pan_fifth_source"] == "given_name"),
    ):
        for src in ("gt", "ocr"):
            fld = "rule_gt_detail" if src == "gt" else "rule_ocr_detail"
            sel = [r for r in rows if r["doc_type"] == "pan" and r["label"] == 0
                   and sel_fn(r) and r.get(fld)]
            perm = sum(1 for r in sel if r[fld].get("semantic_check") == "FAIL")
            strict = sum(1 for r in sel if r[fld].get("semantic_strict") == "FAIL")
            skip = sum(1 for r in sel if r[fld].get("semantic_check") == "SKIPPED")
            ps[f"{key}/{src}"] = {
                "n": len(sel),
                "permissive_fail_pct_ci": _fmt_ci(perm, len(sel)),
                "strict_fail_pct_ci": _fmt_ci(strict, len(sel)),
                "skipped_pct_ci": _fmt_ci(skip, len(sel)),
            }
    S["pan_semantic_permissive_vs_strict_on_genuine"] = ps

    # ---------------- detection ceiling of the rule branch --------------
    ceil = {}
    for dt in ("aadhaar", "pan"):
        for c in CATS:
            for src, fld in (("gt", "rule_gt_verdict"), ("ocr", "rule_ocr_verdict")):
                sel = [r for r in rows if r["doc_type"] == dt
                       and r["forgery_category"] == c and r.get(fld)]
                k = sum(1 for r in sel if r[fld] == "FAIL")
                ceil[f"{dt}/{c}/{src}"] = {"n": len(sel), "flagged": k,
                                           "pct_ci": _fmt_ci(k, len(sel))}
    S["rule_flag_rate_by_category"] = ceil

    # ---------------- leakage audits -----------------------------------
    S["leakage"] = {
        "identity": audit_identity(rows, None),
        "identifier": audit_identifier(rows),
        "template": audit_template(rows),
        "augmentation": audit_augmentation(rows),
        "printed_values": audit_printed_values(rows),
        "near_duplicate": audit_near_duplicate(rows),
    }
    # The near-duplicate audit is diagnostic, not gating (see leakage.py).
    S["leakage_gating_checks"] = ["identity", "identifier", "template",
                                  "augmentation", "printed_values"]
    S["leakage_all_passed"] = all(S["leakage"][k]["passed"]
                                  for k in S["leakage_gating_checks"])

    # ---------------- coincidence with issued numbers -------------------
    n_a = len({r["forged_value"] or r["aadhaar_gt"] for r in rows
               if r["doc_type"] == "aadhaar"} - {""})
    n_p = len({r["forged_value"] or r["pan_gt"] for r in rows
               if r["doc_type"] == "pan"} - {""})
    S["coincidence"] = {
        "note": ("Expected number of GENERATED identifiers that coincide with an "
                 "issued one under uniform sampling.  No identifier was resolved "
                 "against any service; see docs/DATASHEET.md."),
        "aadhaar": {str(m): coincidence_bound(n_a, m, AADHAAR_PAYLOAD_SPACE)
                    for m in (1.0e9, 1.42e9)},
        "pan": {str(m): coincidence_bound(n_p, m, PAN_SPACE_CONSTRAINED)
                for m in (7.0e8, 8.0e8)},
        "n_distinct_aadhaar_strings": n_a,
        "n_distinct_pan_strings": n_p,
    }
    return S


def write_reports(S: dict, out_dir: str) -> None:
    os.makedirs(os.path.join(out_dir, "stats"), exist_ok=True)
    with open(os.path.join(out_dir, "stats", "dataset_stats.json"), "w") as fh:
        json.dump(S, fh, indent=1, default=str)

    L = []
    A = L.append
    A("# Dataset v1 — characterisation report\n")
    A("Everything in this report characterises the DATASET and the rule branch "
      "operating on it. No visual model is trained and no fusion is performed "
      "here, so none of these numbers is a detection result for the hybrid "
      "system.\n")
    t = S["totals"]
    A(f"- persons: **{t['persons']}**   documents: **{t['documents']}**   "
      f"images: **{t['images']}**")
    A(f"- genuine images (C0): **{t['images_genuine']}**   forged (C1-C4): "
      f"**{t['images_forged']}**")
    A(f"- on disk: **{S['storage']['total_gib']} GiB**\n")

    A("## Composition (images per document type x forgery category)\n")
    A("| category | aadhaar | pan |")
    A("|---|---|---|")
    for c in CATS:
        A(f"| {c} | {S['composition_by_cell'][f'aadhaar/{c}']} | "
          f"{S['composition_by_cell'][f'pan/{c}']} |")
    A("")
    A(f"Split sizes (images): {S['split_sizes']}  ")
    A(f"Split sizes (persons): {S['split_persons']}  ")
    A(f"Naming strata (persons): {S['naming_strata_persons']}  ")
    A(f"PAN fifth-character source (persons): {S['pan_fifth_source_persons']}\n")

    A("## OCR field extraction quality (exact match %, 95% Wilson CI)\n")
    A("| document | field | tier | n | exact match % [95% CI] | mean CER % | empty % |")
    A("|---|---|---|---|---|---|---|")
    for k, v in S["ocr"].items():
        dt, fld, tier = k.split("/")
        A(f"| {dt} | {fld} | {tier} | {v['n']} | {v['exact_match_pct']:.1f} "
          f"[{v['ci95'][0]:.1f}, {v['ci95'][1]:.1f}] | {v['mean_cer_pct']:.2f} | "
          f"{v['empty_extraction_pct']:.1f} |")
    A("")

    A("## Rule-branch flag rate by forgery category\n")
    A("A FAIL here means an applicable rule evaluated FALSE. On C0 it is a false "
      "positive; on C4 it is expected to be a miss by construction, so any FAIL "
      "on C4 is an OCR-induced false alarm rather than detection of the "
      "fabrication.\n")
    A("| document | category | ground-truth text | OCR text |")
    A("|---|---|---|---|")
    for dt in ("aadhaar", "pan"):
        for c in CATS:
            g = S["rule_flag_rate_by_category"][f"{dt}/{c}/gt"]
            o = S["rule_flag_rate_by_category"][f"{dt}/{c}/ocr"]
            A(f"| {dt} | {c} | {g['pct_ci']} | {o['pct_ci']} |")
    A("")

    A("## Rule-branch false-positive rate on genuine documents (RQ6 input)\n")
    A("| document | tier | n | FP | FP % [95% CI] |")
    A("|---|---|---|---|---|")
    for k, v in S["rule_false_positive_on_genuine_ocr"].items():
        dt, tier = k.split("/")
        A(f"| {dt} | {tier} | {v['n']} | {v['fp']} | {v['pct_ci']} |")
    A("")

    A("## PAN cross-field rule: permissive vs strict, genuine documents only\n")
    A("| subset | source | n | permissive FAIL % | strict FAIL % | SKIPPED % |")
    A("|---|---|---|---|---|---|")
    for k, v in S["pan_semantic_permissive_vs_strict_on_genuine"].items():
        sub, src = k.rsplit("/", 1)
        A(f"| {sub} | {src} | {v['n']} | {v['permissive_fail_pct_ci']} | "
          f"{v['strict_fail_pct_ci']} | {v['skipped_pct_ci']} |")
    A("")

    A("## Leakage audit (Table V)\n")
    A("| leakage mode | required | result |")
    A("|---|---|---|")
    lk = S["leakage"]
    A(f"| identity | empty person-id intersection | "
      f"{lk['identity']['pairwise_person_id_intersections']} — "
      f"{'PASS' if lk['identity']['passed'] else 'FAIL'} |")
    A(f"| identifier | empty identifier intersection | "
      f"{lk['identifier']['pairwise_identifier_intersections']} — "
      f"{'PASS' if lk['identifier']['passed'] else 'FAIL'} |")
    A(f"| template | every variant in every split | "
      f"{lk['template']['variants_per_split']} of "
      f"{lk['template']['total_variants']} — "
      f"{'PASS' if lk['template']['passed'] else 'FAIL'} |")
    A("| near-duplicate | (diagnostic, not gating) | see below |")
    A(f"| augmentation | degradation draws confined to one split | "
      f"{lk['augmentation']['documents_spanning_splits']} documents span splits — "
      f"{'PASS' if lk['augmentation']['passed'] else 'FAIL'} |")
    A(f"| printed values (exact) | no field-value set in two splits | "
      f"{lk['printed_values']['sets_spanning_splits']} of "
      f"{lk['printed_values']['distinct_printed_value_sets']} span splits — "
      f"{'PASS' if lk['printed_values']['passed'] else 'FAIL'} |")
    A("")
    nd = lk["near_duplicate"]
    A(f"Near-duplicate audit uses a {nd['hash_bits']}-bit perceptual hash. "
      f"The 64-bit hash yields only {nd['distinct_hashes_64bit']} distinct values "
      f"for {nd['n_images']} images and is not usable here; the "
      f"{nd['hash_bits']}-bit hash yields {nd['distinct_hashes_used']}. "
      f"Median distance between two captures of the same document: "
      f"{nd['within_document']['median']:.0f} bits; between different persons: "
      f"{nd['cross_person_same_split']['median']:.0f} bits.")
    A("")

    A("## Coincidence with issued identifiers\n")
    ca = S["coincidence"]
    A(f"Distinct generated Aadhaar strings: {ca['n_distinct_aadhaar_strings']}; "
      f"PAN strings: {ca['n_distinct_pan_strings']}.\n")
    A("| document | assumed issued population | P(single coincidence) | "
      "expected coincidences | P(at least one) |")
    A("|---|---|---|---|---|")
    for dt in ("aadhaar", "pan"):
        for m, v in ca[dt].items():
            A(f"| {dt} | {float(m):.3g} | {v['p_single']:.5f} | "
              f"{v['expected_coincidences']:.2f} | {v['p_at_least_one']:.4f} |")
    A("")
    with open(os.path.join(out_dir, "stats", "REPORT.md"), "w") as fh:
        fh.write("\n".join(L))
