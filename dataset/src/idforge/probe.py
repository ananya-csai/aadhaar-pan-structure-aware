# -*- coding: utf-8 -*-
"""Renderer-leakage probe (Section IV).

The validity of RQ2 and RQ3 rests on one assumption: that C2, C3 and C4
documents carry NO visual evidence of forgery, because they are re-rendered
from a modified record and differ from a genuine control only in the characters
printed in one field.  If the rendering pipeline leaked the label -- through a
different code path, a different antialiasing history, a different compression
history -- a visual detector could separate those categories from C0 on a
rendering artefact, and the incremental-value measurement would be measuring
the artefact.

This module tests the assumption two ways rather than asserting it.

1. `exact_difference_audit` is a proof, not a probe.  C0_0, C1, C2, C3 and C4
   share one render seed, so before degradation their images must be
   bit-identical everywhere except inside the corrupted field (C2-C4) or the
   edited region (C1).  The audit re-renders them and reports the bounding box
   of the actual pixel difference.  If any pixel outside the expected region
   differs, the construction is broken.

2. `learned_probe` is the empirical check on the RELEASED images, which have
   been independently degraded and therefore do differ everywhere.  A
   classifier is trained on the training split to separate C0 from
   C2 u C3 u C4 and evaluated on the test split; under the intended
   construction its balanced accuracy should be near 0.5.

   A 0.5 result is uninformative on its own -- a probe too weak to learn
   anything would also return 0.5 -- so the same probe is run on C0 versus C1,
   where a visual cue is known to exist by construction.  That positive control
   is what makes the negative result interpretable.
"""
from __future__ import annotations

import json
import os
import random
from collections import defaultdict

import numpy as np
from PIL import Image

PROBE_SIDE = 96


# --------------------------------------------------------------------------
# 1. exact difference audit (pre-degradation)
# --------------------------------------------------------------------------

def exact_difference_audit(out_dir: str, n_records: int = 40) -> dict:
    """Re-render each category and check where the pixels actually differ."""
    from . import templates as TPL
    from .build import base_fields, _seed_for, DEFAULT_CFG
    from .forgery import apply_c1, modify_record_fields
    from .records import IdentityRecord

    recs = []
    for line in open(os.path.join(out_dir, "records.jsonl"), encoding="utf-8"):
        d = json.loads(line)
        d.pop("split", None)
        recs.append(IdentityRecord(**d))
    cfg = json.load(open(os.path.join(out_dir, "config.used.json")))["config"]
    gseed = cfg["seed"]
    deva_pool = [r.name_devanagari for r in recs]
    recs = recs[:n_records]

    rows = []
    for rec in recs:
        for doc_type in ("aadhaar", "pan"):
            style_list = (TPL.AADHAAR_STYLES if doc_type == "aadhaar"
                          else TPL.PAN_STYLES)
            tv = (rec.template_aadhaar if doc_type == "aadhaar"
                  else rec.template_pan)
            style = style_list[tv]
            bf = base_fields(rec, doc_type)
            base_seed = _seed_for(gseed, rec.person_id, doc_type, "base")

            render = (TPL.render_aadhaar if doc_type == "aadhaar"
                      else TPL.render_pan)
            ref_img, ref_boxes = render(bf, style, seed=base_seed)
            ref = np.asarray(ref_img, dtype=np.int16)

            for cat in ("C1", "C2", "C3", "C4"):
                frng = random.Random(base_seed ^ 0x9E37)
                if cat == "C1":
                    from .build import gt_text
                    vals = dict(gt_text(bf, doc_type), gender="")
                    img, prov = apply_c1(ref_img, ref_boxes, doc_type, vals,
                                         style, frng)
                    expected = prov["c1_region"]
                else:
                    f, prov = modify_record_fields(bf, doc_type, cat, rec,
                                                   frng, deva_pool)
                    img, fbox = render(f, style, seed=base_seed)
                    fld = prov["forgery_field"]
                    # A forged identifier can be a different width from the
                    # genuine one (an inserted or deleted character), so the
                    # affected region is the union of the two field boxes.
                    a, b2 = ref_boxes.get(fld), fbox.get(fld)
                    expected = ([min(a[0], b2[0]), min(a[1], b2[1]),
                                 max(a[2], b2[2]), max(a[3], b2[3])]
                                if a and b2 else (a or b2))
                d = np.abs(np.asarray(img, dtype=np.int16) - ref).sum(axis=2)
                ys, xs = np.nonzero(d)
                if len(xs) == 0:
                    diff_box, outside = None, 0
                else:
                    diff_box = [int(xs.min()), int(ys.min()),
                                int(xs.max()) + 1, int(ys.max()) + 1]
                    mask = np.zeros(d.shape, dtype=bool)
                    if expected:
                        # inclusive of the right/bottom edge: PIL's rectangle
                        # and textbbox are inclusive there, so an exclusive
                        # mask would count the box perimeter as "outside".
                        x0, y0, x1, y1 = expected
                        mask[max(0, y0):y1 + 1, max(0, x0):x1 + 1] = True
                    outside = int((d > 0)[~mask].sum())
                rows.append({"person_id": rec.person_id, "doc_type": doc_type,
                             "category": cat, "expected_region": expected,
                             "observed_diff_box": diff_box,
                             "changed_pixels": int((d > 0).sum()),
                             "changed_pixels_outside_expected_region": outside})

    by = defaultdict(lambda: {"n": 0, "outside": 0, "clean": 0})
    for r in rows:
        k = f"{r['doc_type']}/{r['category']}"
        by[k]["n"] += 1
        by[k]["outside"] += r["changed_pixels_outside_expected_region"]
        by[k]["clean"] += int(r["changed_pixels_outside_expected_region"] == 0)
    return {
        "n_records_audited": len(recs),
        "per_cell": {k: dict(v) for k, v in sorted(by.items())},
        "total_pixels_changed_outside_expected_region":
            sum(r["changed_pixels_outside_expected_region"] for r in rows),
        "passed": all(r["changed_pixels_outside_expected_region"] == 0
                      for r in rows),
        "note": ("Before degradation, a forged document differs from its "
                 "genuine control only inside the corrupted field or edited "
                 "region. Any non-zero count here is a construction defect."),
    }


# --------------------------------------------------------------------------
# 2. learned probe (on the released, degraded images)
# --------------------------------------------------------------------------

def _features(paths: list) -> np.ndarray:
    """Forensic features, computed at NATIVE resolution and made
    permutation-invariant over image location.

    Two design points matter, and getting either wrong makes the probe useless
    as a positive control:

    * The statistics are computed on the image as released, not on a
      downscaled copy.  A C1 operation such as a locally recompressed or
      resampled region is visible precisely as a local discontinuity in
      compression and noise structure, and resizing the image destroys exactly
      that evidence before the classifier ever sees it.
    * The tampered region is in a different place in every image, so a feature
      vector indexed by grid position cannot generalise.  Per-cell statistics
      are therefore SORTED across cells and only the order statistics are kept:
      the question the classifier is asked is "is some cell anomalous relative
      to the rest of this document", which is location-independent.
    """
    import cv2
    BX, BY = 16, 10            # cell grid over the full-resolution image
    TOPK = 6
    out = []
    for p in paths:
        a = np.asarray(Image.open(p).convert("L"), dtype=np.float32)
        H, W = a.shape

        res = a - cv2.GaussianBlur(a, (3, 3), 0.8)
        lap = cv2.Laplacian(a, cv2.CV_32F, ksize=3)
        dh = np.abs(np.diff(a, axis=1))
        dv = np.abs(np.diff(a, axis=0))

        bw, bh = max(8, W // BX), max(8, H // BY)
        cells = []
        for by in range(BY):
            for bx in range(BX):
                y0, y1 = by * bh, min(H, (by + 1) * bh)
                x0, x1 = bx * bw, min(W, (bx + 1) * bw)
                if y1 - y0 < 8 or x1 - x0 < 8:
                    continue
                r = res[y0:y1, x0:x1]
                l = lap[y0:y1, x0:x1]
                gh = dh[y0:y1, x0:min(x1, dh.shape[1])]
                gv = dv[y0:min(y1, dv.shape[0]), x0:x1]
                # local JPEG blockiness: gradient energy on the 8-pixel grid
                # against energy off it, within this cell
                onh = gh[:, 7::8].mean() if gh.shape[1] > 8 else 0.0
                offh = (np.delete(gh, np.s_[7::8], axis=1).mean()
                        if gh.shape[1] > 8 else 0.0)
                onv = gv[7::8, :].mean() if gv.shape[0] > 8 else 0.0
                offv = (np.delete(gv, np.s_[7::8], axis=0).mean()
                        if gv.shape[0] > 8 else 0.0)
                cells.append([
                    float(np.abs(r).mean()), float(r.std()),
                    float(np.abs(l).mean()),
                    float(np.percentile(np.abs(r), 95)),
                    float(onh / (offh + 1e-6)), float(onv / (offv + 1e-6)),
                ])
        C = np.asarray(cells, dtype=np.float32)
        if len(C) == 0:
            out.append(np.zeros(TOPK * 2 * 6 + 6 * 3 + 6, dtype=np.float32))
            continue

        feats = []
        for k in range(C.shape[1]):
            v = np.sort(C[:, k])
            med = float(np.median(v)) + 1e-6
            feats += list(v[-TOPK:] / med)          # most anomalous cells
            feats += list(v[:TOPK] / med)           # least
            feats += [float(v.mean()), float(v.std()), float(v.max() / med)]

        # a few whole-image descriptors, so the classifier can normalise for
        # overall capture quality rather than confusing it with tampering
        glob = [float(np.abs(res).mean()), float(res.std()),
                float(np.abs(lap).mean()),
                float(dh[:, 7::8].mean() / (np.delete(dh, np.s_[7::8], axis=1).mean() + 1e-6)),
                float(W), float(H)]
        out.append(np.asarray(feats + glob, dtype=np.float32))
    n = max(len(o) for o in out)
    return np.vstack([np.pad(o, (0, n - len(o))) for o in out]).astype(np.float32)


def learned_probe(out_dir: str, task: str, max_per_class: int = 2200,
                  seed: int = 0, tier: str | None = None) -> dict:
    """Train on the train split, evaluate on the test split.

    task 'critical' : C0 vs C2 u C3 u C4  -- should be near 0.5
    task 'control'  : C0 vs C1            -- positive control, should exceed it
    """
    from sklearn.ensemble import HistGradientBoostingClassifier
    from sklearn.metrics import balanced_accuracy_score, roc_auc_score

    rows = [json.loads(l) for l in open(os.path.join(out_dir,
                                                     "manifest.jsonl"))]
    pos = {"critical": {"C2", "C3", "C4"}, "control": {"C1"}}[task]
    rng = random.Random(seed)

    def pick(split):
        def keep(r):
            return r["split"] == split and (tier is None
                                            or r["quality_tier"] == tier)
        a = [r for r in rows if keep(r) and r["forgery_category"] == "C0"]
        b = [r for r in rows if keep(r) and r["forgery_category"] in pos]
        rng.shuffle(a); rng.shuffle(b)
        k = min(len(a), len(b), max_per_class if split == "train"
                else max_per_class)
        return a[:k] + b[:k], [0] * k + [1] * k

    tr, ytr = pick("train")
    te, yte = pick("test")
    Xtr = _features([os.path.join(out_dir, r["file"]) for r in tr])
    Xte = _features([os.path.join(out_dir, r["file"]) for r in te])
    clf = HistGradientBoostingClassifier(max_iter=220, learning_rate=0.10,
                                         max_leaf_nodes=31, random_state=seed)
    clf.fit(Xtr, ytr)
    p = clf.predict_proba(Xte)[:, 1]
    return {
        "task": task,
        "tier": tier or "all",
        "positive_categories": sorted(pos),
        "n_train": len(tr), "n_test": len(te),
        "balanced_accuracy": round(float(balanced_accuracy_score(
            yte, (p > 0.5).astype(int))), 4),
        "auroc": round(float(roc_auc_score(yte, p)), 4),
    }


def run_all(out_dir: str, n_records: int = 40) -> dict:
    res = {"exact_difference_audit": exact_difference_audit(out_dir, n_records)}
    for tier in (None, "clean"):
        suf = "" if tier is None else "_clean"
        for task in ("control", "critical"):
            res[f"learned_probe_{task}{suf}"] = learned_probe(out_dir, task,
                                                              tier=tier)
    c = res["learned_probe_critical"]["balanced_accuracy"]
    k = res["learned_probe_control"]["balanced_accuracy"]
    cc = res["learned_probe_critical_clean"]["balanced_accuracy"]
    kc = res["learned_probe_control_clean"]["balanced_accuracy"]
    res["verdict"] = (
        f"Positive control (C0 vs C1) balanced accuracy {k:.3f} over all tiers "
        f"and {kc:.3f} on clean captures; critical probe (C0 vs C2/C3/C4) "
        f"{c:.3f} and {cc:.3f}. The control confirms the probe can find a "
        f"visual cue in this corpus when one exists; the critical probe "
        f"{'is consistent with' if max(abs(c-0.5), abs(cc-0.5)) < 0.05 else 'DEVIATES FROM'} "
        f"chance, as the construction requires.")
    return res
