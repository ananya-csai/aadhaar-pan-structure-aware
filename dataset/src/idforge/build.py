# -*- coding: utf-8 -*-
"""Single entry point that regenerates the entire dataset (Section IV-I).

    python -m idforge.build --config configs/dataset_v1.yaml --out data/v1

Everything downstream of the global seed is deterministic: identifiers, names,
template assignment, forgery choices, degradation draws and the split
assignment.  Re-running with the same config and the same library versions
reproduces the corpus bit-for-bit.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import multiprocessing as mp
import os
import random
import shutil
import sys
import time
from collections import defaultdict

import numpy as np
from PIL import Image

from . import templates as TPL
from .degrade import TIERS, degrade
from .forgery import CATEGORIES, EXPECTED_RULE, apply_c1, modify_record_fields
from .ocr import crop_field, parse_field, run_batch, cer, FIELD_CFG
from .phash import phash64
from .records import make_records
from .splits import assign_splits
from .validators import validate_aadhaar, validate_pan

DOC_TYPES = ("aadhaar", "pan")
OCR_FIELDS = {"aadhaar": ["aadhaar_number", "name", "dob"],
              "pan": ["pan_number", "name", "father_name", "dob"]}

DEFAULT_CFG = {
    "n_persons": 300,
    "seed": 20260828,
    "stratum_weights": [1, 1, 1],
    "honorific_rate": 0.18,
    "initial_first_p5_from_lead": 0.35,
    "tiers": list(TIERS),
    "jpeg_dir_quality": None,
    "workers": max(1, (os.cpu_count() or 2)),
    "version": "v1",
}


def _seed_for(global_seed: int, *parts) -> int:
    """A stable seed derived from the global seed and a tuple of identifiers.

    Python's built-in hash() is salted per interpreter process (PYTHONHASHSEED),
    so using it here would make every render and every degradation draw differ
    between runs AND between worker processes within a run -- silently, since
    the corpus would still look correct.  A cryptographic digest is used instead
    so that the reproducibility claim of Section IV-I actually holds.
    """
    m = hashlib.blake2b(digest_size=8)
    m.update(str(global_seed).encode())
    for p in parts:
        m.update(b"\x1f")
        m.update(str(p).encode("utf-8"))
    return int.from_bytes(m.digest(), "big") & 0x7FFFFFFF


def base_fields(rec, doc_type: str) -> dict:
    if doc_type == "aadhaar":
        return dict(name_latin=rec.extra["printed_name_latin"],
                    name_devanagari=rec.name_devanagari,
                    dob=rec.dob, gender=rec.gender, aadhaar=rec.aadhaar,
                    photo_seed=rec.photo_seed)
    return dict(pan=rec.pan,
                name_latin=rec.extra["printed_name_latin"].upper(),
                father_name_latin=rec.father_name_latin.upper(),
                dob=rec.dob, photo_seed=rec.photo_seed)


def gt_text(fields: dict, doc_type: str) -> dict:
    """The ground-truth value of every extracted field for a given render."""
    if doc_type == "aadhaar":
        return {"aadhaar_number": fields["aadhaar"],
                "name": fields["name_latin"], "dob": fields["dob"]}
    return {"pan_number": fields["pan"], "name": fields["name_latin"],
            "father_name": fields["father_name_latin"], "dob": fields["dob"]}


def rule_verdict(doc_type: str, txt: dict) -> tuple:
    if doc_type == "aadhaar":
        r = validate_aadhaar(txt.get("aadhaar_number", ""))
        return r.overall, r.as_dict()
    r = validate_pan(txt.get("pan_number", ""), txt.get("name", ""))
    return r.overall, r.as_dict()


# --------------------------------------------------------------------------
# pre-flight: validators against ground-truth text, before rendering at scale
# --------------------------------------------------------------------------

def preflight(records, cfg) -> dict:
    rng = random.Random(cfg["seed"] ^ 0xBEEF)
    deva_pool = [r.name_devanagari for r in records]
    counts = defaultdict(lambda: defaultdict(int))
    problems = []
    for rec in records:
        for doc_type in DOC_TYPES:
            bf = base_fields(rec, doc_type)
            for cat in CATEGORIES:
                if cat in ("C0", "C1"):
                    f = bf
                else:
                    f, _ = modify_record_fields(bf, doc_type, cat, rec, rng, deva_pool)
                v, _ = rule_verdict(doc_type, gt_text(f, doc_type))
                counts[(doc_type, cat)][v] += 1
                want = EXPECTED_RULE[(doc_type, cat)]
                if v != want:
                    problems.append((rec.person_id, doc_type, cat, v, want))
    return {"counts": {f"{k[0]}/{k[1]}": dict(v) for k, v in counts.items()},
            "violations": problems[:50],
            "n_violations": len(problems)}


# --------------------------------------------------------------------------
# worker
# --------------------------------------------------------------------------

_WORK = {}


def _init(cfg, splits, out, deva_pool):
    _WORK["cfg"] = cfg
    _WORK["splits"] = splits
    _WORK["out"] = out
    _WORK["deva"] = deva_pool


def _ocr_task(t):
    fld, st, paths = t
    return (fld, st), run_batch(paths, fld)


def _process_person(rec):
    cfg, splits, out = _WORK["cfg"], _WORK["splits"], _WORK["out"]
    deva_pool = _WORK["deva"]
    gseed = cfg["seed"]
    split = splits[rec.person_id]
    rows, crops = [], []

    for doc_type in DOC_TYPES:
        style_list = TPL.AADHAAR_STYLES if doc_type == "aadhaar" else TPL.PAN_STYLES
        tv = rec.template_aadhaar if doc_type == "aadhaar" else rec.template_pan
        style = style_list[tv]
        bf = base_fields(rec, doc_type)

        # Render-seed policy (Section IV-A).  C0_0, C1, C2, C3 and C4 all share
        # ONE base render seed, so the guilloche phase, photograph, signature
        # and placeholder block are IDENTICAL across them and the only pixels
        # that can differ are those of the corrupted field (C2-C4) or the
        # edited region (C1).  That turns "these categories carry no visual
        # trace" from a statistical claim into a checkable one -- see
        # idforge.probe.exact_difference_audit.  C0_1, the second control, is
        # drawn with an independent seed so that the corpus is not reduced to a
        # single background per person.
        base_seed = _seed_for(gseed, rec.person_id, doc_type, "base")
        alt_seed = _seed_for(gseed, rec.person_id, doc_type, "alt")
        slots = [("C0", 0), ("C0", 1), ("C1", 0), ("C2", 0), ("C3", 0), ("C4", 0)]
        for cat, ci in slots:
            doc_id = f"{rec.person_id}_{doc_type}_{cat}{ci if cat=='C0' else ''}"
            rseed = alt_seed if (cat == "C0" and ci == 1) else base_seed
            frng = random.Random(rseed ^ 0x9E37)

            if cat in ("C0", "C1"):
                fields, prov = dict(bf), {"forgery_field": None,
                                          "forgery_detail": None,
                                          "gt_value": None, "forged_value": None}
            else:
                fields, prov = modify_record_fields(bf, doc_type, cat, rec,
                                                    frng, deva_pool)

            if doc_type == "aadhaar":
                img, boxes = TPL.render_aadhaar(fields, style, seed=rseed)
            else:
                img, boxes = TPL.render_pan(fields, style, seed=rseed)

            if cat == "C1":
                vals = gt_text(fields, doc_type)
                vals["gender"] = ""
                img, c1prov = apply_c1(img, boxes, doc_type, vals, style, frng)
                prov.update(c1prov)

            truth = gt_text(fields, doc_type)
            gt_verdict, gt_detail = rule_verdict(doc_type, truth)

            for tier in cfg["tiers"]:
                dseed = _seed_for(gseed, rec.person_id, doc_type, cat, ci, tier)
                dimg, dboxes, drec = degrade(img, tier, dseed, boxes)
                image_id = f"{doc_id}_{tier}"
                rel = os.path.join("images", split, doc_type, image_id + ".jpg")
                path = os.path.join(out, rel)
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "wb") as fh:
                    fh.write(drec["jpeg_bytes"])

                for fld in OCR_FIELDS[doc_type]:
                    cp = os.path.join(out, "_crops", f"{image_id}__{fld}.png")
                    os.makedirs(os.path.dirname(cp), exist_ok=True)
                    crop_field(dimg, dboxes[fld]).save(cp)
                    crops.append((cp, fld, image_id))

                rows.append({
                    "image_id": image_id,
                    "document_id": doc_id,
                    "person_id": rec.person_id,
                    "split": split,
                    "doc_type": doc_type,
                    "forgery_category": cat,
                    "control_index": ci if cat == "C0" else None,
                    "label": 0 if cat == "C0" else 1,
                    "quality_tier": tier,
                    "template_variant": tv,
                    "naming_stratum": rec.naming_stratum,
                    "pan_fifth_source": rec.pan_fifth_source,
                    "honorific": rec.honorific,
                    "gender": rec.gender,
                    "aadhaar_gt": rec.aadhaar if doc_type == "aadhaar" else "",
                    "pan_gt": rec.pan if doc_type == "pan" else "",
                    "printed_values": truth,
                    "boxes": dboxes,
                    "width": dimg.width, "height": dimg.height,
                    "render_seed": rseed, "degrade_seed": dseed,
                    "jpeg_q_capture": drec.get("jpeg_q"),
                    "bytes": len(drec["jpeg_bytes"]),
                    "motion_blur": drec.get("motion_blur"),
                    "phash": phash64(dimg),
                    "rule_gt_verdict": gt_verdict,
                    "rule_gt_detail": gt_detail,
                    "expected_rule": EXPECTED_RULE[(doc_type, cat)],
                    "file": rel,
                    **prov,
                })
    return rows, crops


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/v1")
    ap.add_argument("--n-persons", type=int, default=None)
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--workers", type=int, default=None)
    ap.add_argument("--skip-ocr", action="store_true")
    ap.add_argument("--config", default=None)
    a = ap.parse_args(argv)

    cfg = dict(DEFAULT_CFG)
    if a.config and os.path.exists(a.config):
        cfg.update(_read_cfg(a.config))
    for k, v in (("n_persons", a.n_persons), ("seed", a.seed), ("workers", a.workers)):
        if v is not None:
            cfg[k] = v

    out = a.out
    os.makedirs(out, exist_ok=True)
    t0 = time.time()

    print(f"[1/7] generating {cfg['n_persons']} identity records "
          f"(seed={cfg['seed']})", flush=True)
    records = make_records(cfg["n_persons"], cfg["seed"], cfg)

    print("[2/7] assigning grouped stratified splits", flush=True)
    splits = assign_splits(records, cfg["seed"] ^ 0x51D)

    print("[3/7] pre-flight: validators against ground-truth text", flush=True)
    pf = preflight(records, cfg)
    print("       ", json.dumps(pf["counts"]), flush=True)
    if pf["n_violations"]:
        print("GENERATOR DEFECT: expected rule outcomes violated:", flush=True)
        for v in pf["violations"]:
            print("   ", v)
        sys.exit(2)
    print("        all expected rule outcomes hold", flush=True)

    print(f"[4/7] rendering, forging, degrading "
          f"({cfg['n_persons'] * 2 * 6 * len(cfg['tiers'])} images), "
          f"{cfg['workers']} worker(s)", flush=True)
    deva_pool = [r.name_devanagari for r in records]
    rows, crops = [], []
    if cfg["workers"] > 1:
        with mp.Pool(cfg["workers"], initializer=_init,
                     initargs=(cfg, splits, out, deva_pool)) as pool:
            for i, (rr, cc) in enumerate(pool.imap_unordered(_process_person,
                                                             records, chunksize=4)):
                rows += rr
                crops += cc
                if (i + 1) % 25 == 0:
                    print(f"        {i+1}/{len(records)} persons "
                          f"({time.time()-t0:.0f}s)", flush=True)
    else:
        _init(cfg, splits, out, deva_pool)
        for i, rec in enumerate(records):
            rr, cc = _process_person(rec)
            rows += rr
            crops += cc
            if (i + 1) % 25 == 0:
                print(f"        {i+1}/{len(records)} persons", flush=True)

    rows.sort(key=lambda r: r["image_id"])

    ocr_map = {}
    if not a.skip_ocr:
        print(f"[5/7] per-field OCR ({len(crops)} crops)", flush=True)
        byfield = defaultdict(list)
        for cp, fld, iid in crops:
            byfield[fld].append((cp, iid))
        CH = 400
        tasks = []
        for fld, items in byfield.items():
            for st in range(0, len(items), CH):
                tasks.append((fld, st, [p for p, _ in items[st:st + CH]]))
        results, done = {}, 0
        if cfg["workers"] > 1:
            with mp.Pool(cfg["workers"]) as pool:
                for key, res in pool.imap_unordered(_ocr_task, tasks, chunksize=1):
                    results[key] = res
                    done += 1
                    if done % 10 == 0 or done == len(tasks):
                        print(f"        OCR batch {done}/{len(tasks)}", flush=True)
        else:
            for t in tasks:
                key, res = _ocr_task(t)
                results[key] = res
        for fld, items in byfield.items():
            for st in range(0, len(items), CH):
                for (cp, iid), raw in zip(items[st:st + CH], results[(fld, st)]):
                    ocr_map.setdefault(iid, {})[fld] = {
                        "raw": raw, "parsed": parse_field(fld, raw)}
        shutil.rmtree(os.path.join(out, "_crops"), ignore_errors=True)

    print("[6/7] validators on OCR-extracted text", flush=True)
    for r in rows:
        o = ocr_map.get(r["image_id"], {})
        r["ocr"] = {k: v["raw"] for k, v in o.items()}
        parsed = {k: v["parsed"] for k, v in o.items()}
        r["ocr_parsed"] = parsed
        if parsed:
            v, det = rule_verdict(r["doc_type"], parsed)
            r["rule_ocr_verdict"] = v
            r["rule_ocr_detail"] = det
            r["ocr_exact"] = {k: int(parsed.get(k, "") ==
                                     parse_field(k, r["printed_values"][k]))
                              for k in r["printed_values"]}
            r["ocr_cer"] = {k: cer(parse_field(k, r["printed_values"][k]),
                                   parsed.get(k, ""))
                            for k in r["printed_values"]}
        else:
            r["rule_ocr_verdict"] = None
            r["rule_ocr_detail"] = None

    print("[7/7] writing manifest and records", flush=True)
    with open(os.path.join(out, "manifest.jsonl"), "w") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(os.path.join(out, "records.jsonl"), "w", encoding="utf-8") as fh:
        for rec in records:
            d = rec.as_dict()
            d["split"] = splits[rec.person_id]
            fh.write(json.dumps(d, ensure_ascii=False) + "\n")
    with open(os.path.join(out, "splits.json"), "w") as fh:
        json.dump(splits, fh, indent=1)
    with open(os.path.join(out, "config.used.json"), "w") as fh:
        json.dump({"config": cfg, "preflight": pf["counts"],
                   "build_seconds": round(time.time() - t0, 1)}, fh, indent=1)

    # flat CSV for convenience
    import csv
    cols = ["image_id", "document_id", "person_id", "split", "doc_type",
            "forgery_category", "control_index", "label", "quality_tier",
            "template_variant", "naming_stratum", "pan_fifth_source",
            "forgery_field", "forgery_detail", "c1_op", "c1_field",
            "rule_gt_verdict", "rule_ocr_verdict", "expected_rule",
            "width", "height", "jpeg_q_capture", "phash", "file"]
    with open(os.path.join(out, "manifest.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)

    print(f"done in {time.time()-t0:.0f}s -> {out}", flush=True)
    return 0


def _read_cfg(path: str) -> dict:
    """Minimal key: value reader so the build needs no YAML dependency."""
    cfg = {}
    for line in open(path, encoding="utf-8"):
        line = line.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        k, v = line.split(":", 1)
        v = v.strip()
        if v.startswith("["):
            cfg[k.strip()] = json.loads(v.replace("'", '"'))
        elif v.lower() in ("true", "false"):
            cfg[k.strip()] = v.lower() == "true"
        else:
            try:
                cfg[k.strip()] = int(v)
            except ValueError:
                try:
                    cfg[k.strip()] = float(v)
                except ValueError:
                    cfg[k.strip()] = v.strip('"\'')
    return cfg


if __name__ == "__main__":
    sys.exit(main())
