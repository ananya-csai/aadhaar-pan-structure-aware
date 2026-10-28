"""Roadmap Steps 16-17: planned analyses E-vis, E6, E7, E8, E9/E12 and the
statistics for Section VII (DECISIONS.md Section 22).

Everything is computed from committed files; nothing is fitted or thresholded:
  dataset/data/v1/manifest.csv, manifest.jsonl     labels, strata, OCR exactness
  experiments/rules/rule_decisions.csv             failing check per image
  experiments/results/<split>/*_predictions.csv    frozen A4-era systems
  experiments/results/<A5 dir>/*_predictions.csv   A5 per-check fusion (post-hoc)
  experiments/e2_visual/runs/*/seed*/scores_*.csv  per-seed logits (E-vis)

Statistics: person-clustered bootstrap, B = 10,000, seed 0. One set of
replicates per split is shared by every metric, so differences are paired.
Two-sided p = 2 min(P(d <= 0), P(d >= 0)); reported as "< 1e-4" when no
replicate crosses 0. Holm correction within each family of Section 22.

    python experiments/analysis/step16_analyses.py --split val
    python experiments/analysis/step16_analyses.py --split test
Writes experiments/results/analysis/<split>/analysis.json and report.md.
"""

import argparse
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments" / "e2_visual"))
from metrics import roc_auc  # noqa: E402

MAN_CSV = ROOT / "dataset" / "data" / "v1" / "manifest.csv"
MAN_JSONL = ROOT / "dataset" / "data" / "v1" / "manifest.jsonl"
RULES = ROOT / "experiments" / "rules" / "rule_decisions.csv"
RUNS = ROOT / "experiments" / "e2_visual" / "runs"
B, SEED = 10_000, 0
DOCS = ("aadhaar", "pan")
CATS = ("C0", "C1", "C2", "C3", "C4")
TIERS = ("clean", "mild", "severe")
FINE = ("local_recompression", "resample_patch")
COARSE = ("font_substitution", "field_displacement", "patch_splice")
OPS = FINE + COARSE
TIED = {("aadhaar", "C2"): {"format_check", "checksum_check"},
        ("pan", "C2"): {"format_check", "category_check"},
        ("pan", "C3"): {"semantic_check"}}

A5_DIR = {"val": "val_A5", "test": "test_posthoc_A5"}
SYSTEMS = {  # name -> (directory key, file stem)
    "visual": ("main", "visual"),
    "base": ("main", "visual_base_comparison"),
    "rules_GT": ("main", "rules_GT"), "rules_OCR": ("main", "rules_OCR"),
    "OR_GT": ("main", "OR_GT"), "AND_GT": ("main", "AND_GT"),
    "OR_OCR": ("main", "OR_OCR"), "AND_OCR": ("main", "AND_OCR"),
    "A4_GT": ("main", "logistic_GT"), "A4_OCR": ("main", "logistic_OCR"),
    "A4_OCR@rules": ("main", "logistic_OCR_at_FPR_of_rules_OCR"),
    "A4_OCR@OR": ("main", "logistic_OCR_at_FPR_of_OR_OCR"),
    "A5_GT": ("a5", "perCheck_GT"), "A5_OCR": ("a5", "perCheck_OCR"),
    "A5_OCR@rules": ("a5", "perCheck_OCR_at_FPR_of_rules_OCR"),
    "A5_OCR@OR": ("a5", "perCheck_OCR_at_FPR_of_OR_OCR"),
}

# Families of DECISIONS.md Section 22. Each entry: (id, label, kind, args).
#   kind "rate": difference of a flag rate between systems a and b on a mask
#   kind "ddelta": difference between document types of Delta = rate(a) - rate(b)
FAMILIES = {
    "F1 (RQ1, E-vis)": [
        ("1a", "C1 fine-trace recall: tiles - whole card", "rate", ("visual", "base", "c1_fine")),
        ("1b", "C1 coarse recall: tiles - whole card", "rate", ("visual", "base", "c1_coarse")),
    ],
    "F3 (RQ3)": [
        ("3a", "recall: A4-GT - visual (5% FPR)", "rate", ("A4_GT", "visual", "forged")),
        ("3b", "recall: A4-OCR - visual (5% FPR)", "rate", ("A4_OCR", "visual", "forged")),
        ("3c", "recall: A4-OCR - rules-OCR (matched FPR)", "rate", ("A4_OCR@rules", "rules_OCR", "forged")),
        ("3d", "recall: A4-OCR - OR-OCR (matched FPR)", "rate", ("A4_OCR@OR", "OR_OCR", "forged")),
    ],
    "F4 (RQ4)": [
        ("4a", "recall: A4-GT - A4-OCR (5% FPR)", "rate", ("A4_GT", "A4_OCR", "forged")),
        ("4b", "rule-coverage recall: rules-GT - rules-OCR", "rate", ("rules_GT", "rules_OCR", "eligible")),
        ("4c", "FPR: rules-OCR - rules-GT", "rate", ("rules_OCR", "rules_GT", "c0")),
    ],
    "F5 (RQ5)": [
        ("5a", "Delta_GT(Aadhaar) - Delta_GT(PAN)", "ddelta", ("A4_GT", "visual")),
        ("5b", "Delta_OCR(Aadhaar) - Delta_OCR(PAN)", "ddelta", ("A4_OCR", "visual")),
    ],
    "F6 (RQ6)": [
        ("6a", "rules-OCR FPR: PAN - Aadhaar", "docdiff", ("rules_OCR", "c0")),
        ("6b", "rules-OCR FPR: severe - clean", "tierdiff", ("rules_OCR",)),
    ],
}
POSTHOC = [
    ("Pa", "recall: A5-OCR - A4-OCR (5% FPR)", "rate", ("A5_OCR", "A4_OCR", "forged")),
    ("Pb", "FPR: A5-OCR - A4-OCR (5% FPR)", "rate", ("A5_OCR", "A4_OCR", "c0")),
    ("Pc", "recall: A5-GT - A4-GT (5% FPR)", "rate", ("A5_GT", "A4_GT", "forged")),
]


# ----------------------------------------------------------------- loading
def load(split):
    with open(MAN_CSV, newline="", encoding="utf-8-sig") as f:
        man = {r["image_id"]: r for r in csv.DictReader(f) if r["split"] == split}
    ocr = {}
    with open(MAN_JSONL, encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            if r["image_id"] in man:
                ocr[r["image_id"]] = r["ocr_exact"]
    with open(RULES, newline="", encoding="utf-8") as f:
        rules = {r["image_id"]: r for r in csv.DictReader(f) if r["split"] == split}
    ids = sorted(man)
    if set(ids) != set(rules) or set(ids) != set(ocr):
        sys.exit("STOP: manifest, rule decisions and OCR records disagree on the split's images")
    dirs = {"main": ROOT / "experiments" / "results" / split,
            "a5": ROOT / "experiments" / "results" / A5_DIR[split]}
    preds, scores = {}, {}
    for name, (d, stem) in SYSTEMS.items():
        with open(dirs[d] / f"{stem}_predictions.csv", newline="", encoding="utf-8") as f:
            rows = {r["image_id"]: r for r in csv.DictReader(f)}
        if set(rows) != set(ids) or len(rows) != len(ids):
            sys.exit(f"STOP: {stem} does not cover exactly the {split} images")
        dec = np.array([int(rows[i]["decision"]) for i in ids])
        if not np.isin(dec, (0, 1)).all():
            sys.exit(f"STOP: {stem} has non-binary decisions")
        preds[name] = dec
        if rows[ids[0]].get("score", "") != "":
            scores[name] = np.array([float(rows[i]["score"]) for i in ids])
    return man, ocr, rules, ids, preds, scores


def seed_logits(model_dir, split, ids):
    """Per-seed document logits for E-vis (scores_test.csv or scores_trainval.csv)."""
    fname = "scores_test.csv" if split == "test" else "scores_trainval.csv"
    out = []
    for s in range(5):
        with open(RUNS / model_dir / f"seed{s}" / fname, newline="", encoding="utf-8") as f:
            z = {r["image_id"]: float(r["logit"]) for r in csv.DictReader(f)}
        out.append(np.array([z[i] for i in ids]))
    return out


# --------------------------------------------------------------- bootstrap
class Boot:
    """Person-clustered bootstrap with one shared set of replicates."""

    def __init__(self, persons):
        self.keys = sorted(set(persons))
        index = {p: k for k, p in enumerate(self.keys)}
        self.pidx = np.array([index[p] for p in persons])
        rng = np.random.default_rng(SEED)
        P = len(self.keys)
        draws = rng.integers(0, P, size=(B, P))
        self.W = np.zeros((B, P))
        for b in range(B):
            self.W[b] = np.bincount(draws[b], minlength=P)

    def per_person(self, x):
        return np.bincount(self.pidx, weights=x.astype(float), minlength=len(self.keys))

    def rate(self, flag, mask):
        """Point value and replicates of mean(flag[mask])."""
        num, den = self.per_person(flag * mask), self.per_person(mask)
        if den.sum() == 0:
            return None, None
        reps_den = self.W @ den
        with np.errstate(invalid="ignore", divide="ignore"):
            reps = (self.W @ num) / reps_den
        return num.sum() / den.sum(), reps

    def auroc(self, y, s):
        """Point AUROC and replicates (weighted Mann-Whitney, ties count 1/2)."""
        u, inv = np.unique(s, return_inverse=True)
        U = len(u)
        Wimg = self.W[:, self.pidx]                      # B x N image weights
        pos_u = np.zeros((B, U))
        neg_u = np.zeros((B, U))
        for k in np.flatnonzero(y == 1):
            pos_u[:, inv[k]] += Wimg[:, k]
        for k in np.flatnonzero(y == 0):
            neg_u[:, inv[k]] += Wimg[:, k]
        below = np.cumsum(neg_u, axis=1) - neg_u
        num = (pos_u * (below + 0.5 * neg_u)).sum(axis=1)
        reps = num / (pos_u.sum(axis=1) * neg_u.sum(axis=1))
        return roc_auc(y, s), reps


def ci(reps):
    r = reps[np.isfinite(reps)]
    return [float(np.percentile(r, 2.5)), float(np.percentile(r, 97.5))]


def pval(d):
    d = d[np.isfinite(d)]
    return float(min(1.0, 2 * min((d <= 0).mean(), (d >= 0).mean())))


def holm(ps):
    order = np.argsort(ps)
    m, adj, running = len(ps), [0.0] * len(ps), 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (m - rank) * ps[i]))
        adj[i] = running
    return adj


def fmt_p(p):
    return "< 1e-4" if p == 0 else (f"{p:.4f}" if p < 0.01 else f"{p:.3f}")


def pct(x):
    return None if x is None else round(100 * float(x), 1)


# ------------------------------------------------------------------- main
def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", required=True, choices=["val", "test"])
    a = ap.parse_args(argv)
    man, ocr, rules, ids, preds, scores = load(a.split)
    m = [man[i] for i in ids]
    y = np.array([int(r["label"]) for r in m])
    cat = np.array([r["forgery_category"] for r in m])
    doc = np.array([r["doc_type"] for r in m])
    tier = np.array([r["quality_tier"] for r in m])
    op = np.array([r["c1_op"] for r in m])
    naming = np.array([r["naming_stratum"] for r in m])
    fifth = np.array([r["pan_fifth_source"] for r in m])
    eligible = np.array([r["expected_rule"] == "FAIL" for r in m])
    persons = [r["person_id"] for r in m]
    bt = Boot(persons)

    masks = {"forged": y == 1, "c0": cat == "C0", "eligible": eligible,
             "c1": cat == "C1", "c1_fine": (cat == "C1") & np.isin(op, FINE),
             "c1_coarse": (cat == "C1") & np.isin(op, COARSE)}
    for c in CATS:
        masks[c] = cat == c
    for d in DOCS:
        masks[f"forged/{d}"] = (y == 1) & (doc == d)
        masks[f"c0/{d}"] = (cat == "C0") & (doc == d)
        for c in CATS:
            masks[f"{d}/{c}"] = (cat == c) & (doc == d)
    for t in TIERS:
        masks[f"c0/{t}"] = (cat == "C0") & (tier == t)
        masks[f"c1/{t}"] = (cat == "C1") & (tier == t)
        masks[f"forged/{t}"] = (y == 1) & (tier == t)
        for d in DOCS:
            masks[f"c0/{d}/{t}"] = (cat == "C0") & (doc == d) & (tier == t)
    for o in OPS:
        masks[f"c1/{o}"] = (cat == "C1") & (op == o)

    res = {"split": a.split, "n_images": len(ids), "n_persons": len(bt.keys), "B": B, "seed": SEED,
           "counts": {k: int(v.sum()) for k, v in masks.items()}}

    # ---- per-system table with CIs
    tab = {}
    for name, f in preds.items():
        row = {}
        for key in ("forged", "c0", "eligible", "c1", "c1_fine", "c1_coarse", *CATS,
                    "forged/aadhaar", "forged/pan", "c0/aadhaar", "c0/pan",
                    *[f"{d}/{c}" for d in DOCS for c in CATS],
                    *[f"c0/{t}" for t in TIERS], *[f"c1/{t}" for t in TIERS],
                    *[f"c1/{o}" for o in OPS]):
            v, reps = bt.rate(f, masks[key])
            row[key] = {"value": pct(v), "ci": [round(100 * x, 1) for x in ci(reps)]}
        tp = int(((y == 1) & (f == 1)).sum()); fp = int(((y == 0) & (f == 1)).sum())
        fn = int(((y == 1) & (f == 0)).sum()); tn = int(((y == 0) & (f == 0)).sum())
        prec = tp / (tp + fp) if tp + fp else None
        rec = tp / (tp + fn)
        row["confusion"] = {"TP": tp, "FP": fp, "TN": tn, "FN": fn}
        row["precision"] = pct(prec)
        row["f1"] = None if prec is None or prec + rec == 0 else round(2 * prec * rec / (prec + rec), 3)
        row["fnr"] = pct(1 - rec)
        if name in scores:
            row["auroc_forged_vs_c0"] = round(roc_auc(y, scores[name]), 3)
        tab[name] = row
    res["systems"] = tab

    # ---- Delta and rho (Section III, eq. delta)
    dr = {}
    for tag, fuse in (("GT", "A4_GT"), ("OCR", "A4_OCR"), ("OCR_A5", "A5_OCR")):
        for key in ("forged", "forged/aadhaar", "forged/pan"):
            v1, r1 = bt.rate(preds[fuse], masks[key])
            v0, r0 = bt.rate(preds["visual"], masks[key])
            dr[f"Delta_{tag}/{key}"] = {"value": pct(v1 - v0), "ci": [round(100 * x, 1) for x in ci(r1 - r0)],
                                        "reps": r1 - r0}
    for tag in ("OCR", "OCR_A5"):
        for key in ("forged", "forged/aadhaar", "forged/pan"):
            num, den = dr[f"Delta_{tag}/{key}"], dr[f"Delta_GT/{key}"]
            reps = num["reps"] / den["reps"]
            dr[f"rho_{tag}/{key}"] = {"value": round(num["value"] / den["value"], 3),
                                      "ci": [round(x, 3) for x in ci(reps)]}
    res["delta_rho"] = {k: {kk: vv for kk, vv in v.items() if kk != "reps"} for k, v in dr.items()}

    # ---- families
    def comparison(kind, args):
        if kind == "rate":
            sa, sb, key = args
            va, ra = bt.rate(preds[sa], masks[key])
            vb, rb = bt.rate(preds[sb], masks[key])
            return va - vb, ra - rb
        if kind == "ddelta":
            fuse, vis = args
            out = []
            for d in DOCS:
                v1, r1 = bt.rate(preds[fuse], masks[f"forged/{d}"])
                v0, r0 = bt.rate(preds[vis], masks[f"forged/{d}"])
                out.append((v1 - v0, r1 - r0))
            return out[0][0] - out[1][0], out[0][1] - out[1][1]
        if kind == "docdiff":
            sname, base = args
            vp, rp = bt.rate(preds[sname], masks[f"{base}/pan"])
            va, ra = bt.rate(preds[sname], masks[f"{base}/aadhaar"])
            return vp - va, rp - ra
        if kind == "tierdiff":
            (sname,) = args
            vs, rs = bt.rate(preds[sname], masks["c0/severe"])
            vc, rc = bt.rate(preds[sname], masks["c0/clean"])
            return vs - vc, rs - rc
        raise ValueError(kind)

    fam_out = {}
    for fam, comps in FAMILIES.items():
        rows = []
        for cid, label, kind, args in comps:
            v, d = comparison(kind, args)
            row = {"id": cid, "label": label, "diff": pct(v),
                   "ci": [round(100 * x, 1) for x in ci(d)], "p": pval(d)}
            if kind == "rate" and args[2] in ("forged", "c1_fine", "c1_coarse"):
                fv, fd = comparison("rate", (args[0], args[1], "c0"))
                row["fpr_diff"], row["fpr_ci"] = pct(fv), [round(100 * x, 1) for x in ci(fd)]
            rows.append(row)
        for r, p in zip(rows, holm([r["p"] for r in rows])):
            r["p_holm"] = p
        fam_out[fam] = rows
    post = []
    for cid, label, kind, args in POSTHOC:
        v, d = comparison(kind, args)
        post.append({"id": cid, "label": label, "diff": pct(v),
                     "ci": [round(100 * x, 1) for x in ci(d)], "p": pval(d)})
    res["families"] = fam_out
    res["posthoc_A5"] = post

    # ---- E-vis: threshold-free and per seed
    evis = {}
    for key in ("c1", "c1_fine", "c1_coarse", *[f"c1/{t}" for t in TIERS], *[f"c1/{o}" for o in OPS]):
        sel = masks[key] | masks["c0"]
        yy = y[sel]
        if key.startswith("c1/") and key[3:] in TIERS:     # compare with C0 of the same tier
            sel = masks[key] | masks[f"c0/{key[3:]}"]
            yy = y[sel]
        sub = Boot.__new__(Boot)
        sub.keys, sub.pidx, sub.W = bt.keys, bt.pidx[sel], bt.W
        row = {}
        for name in ("visual", "base"):
            v, reps = sub.auroc(yy, scores[name][sel])
            row[name] = {"auroc": round(v, 3), "ci": [round(x, 3) for x in ci(reps)], "reps": reps}
        dd = row["visual"]["reps"] - row["base"]["reps"]
        row["diff"] = {"auroc": round(row["visual"]["auroc"] - row["base"]["auroc"], 3),
                       "ci": [round(x, 3) for x in ci(dd)], "p": pval(dd)}
        for name in ("visual", "base"):
            row[name].pop("reps")
        evis[key] = row
    seeds = {}
    for name, d in (("tiles", "native_tiles"), ("base", "768x512")):
        z = seed_logits(d, a.split, ids)
        per = {}
        for key in ("c1", "c1_fine", "c1_coarse"):
            sel = masks[key] | masks["c0"]
            vals = [roc_auc(y[sel], zz[sel]) for zz in z]
            per[key] = {"per_seed": [round(v, 3) for v in vals],
                        "mean": round(float(np.mean(vals)), 3), "sd": round(float(np.std(vals, ddof=1)), 3)}
        seeds[name] = per
    evis["per_seed_auroc"] = seeds
    bound = {}
    for c in ("C2", "C3", "C4"):
        sel = masks[c] | masks["c0"]
        sub = Boot.__new__(Boot)
        sub.keys, sub.pidx, sub.W = bt.keys, bt.pidx[sel], bt.W
        v, reps = sub.auroc(y[sel], scores["visual"][sel])
        bound[c] = {"auroc": round(v, 3), "ci": [round(x, 3) for x in ci(reps)]}
    evis["visual_bounding_check"] = bound
    res["E_vis"] = evis

    # ---- E6: GT vs OCR rule verdicts
    gt = np.array([int(rules[i]["gt_decision"]) for i in ids])
    oc = np.array([int(rules[i]["ocr_decision"]) for i in ids])
    if not (np.array_equal(gt, preds["rules_GT"]) and np.array_equal(oc, preds["rules_OCR"])):
        sys.exit("STOP: rule_decisions.csv disagrees with the rules prediction files")
    e6 = {}
    for grp, gmask in (("C0", cat == "C0"), ("C1", cat == "C1"), ("C2", cat == "C2"),
                       ("C3", cat == "C3"), ("C4", cat == "C4")):
        for d in DOCS:
            for t in (*TIERS, "all"):
                mm = gmask & (doc == d) & ((tier == t) if t != "all" else True)
                e6[f"{grp}/{d}/{t}"] = {
                    "n": int(mm.sum()),
                    "stable_pass": int((mm & (gt == 0) & (oc == 0)).sum()),
                    "stable_fail": int((mm & (gt == 1) & (oc == 1)).sum()),
                    "ocr_induced": int((mm & (gt == 0) & (oc == 1)).sum()),
                    "ocr_masked": int((mm & (gt == 1) & (oc == 0)).sum())}
    res["E6"] = e6

    # ---- E8: C0 false positives of rules-OCR (and fusion) by stratum
    c0 = cat == "C0"
    id_field = {"aadhaar": "aadhaar_number", "pan": "pan_number"}
    idok = np.array([int(ocr[i][id_field[man[i]["doc_type"]]]) for i in ids])
    name_ok = np.array([int(ocr[i]["name"]) for i in ids])
    e8 = {"identifier_field": id_field}
    for sname in ("rules_OCR", "A4_OCR", "A5_OCR", "visual"):
        rows = {}
        f = preds[sname]
        cells = {f"{d}/{t}": c0 & (doc == d) & (tier == t) for d in DOCS for t in TIERS}
        cells |= {f"pan/naming={s}": c0 & (doc == "pan") & (naming == s) for s in sorted(set(naming))}
        cells |= {f"pan/fifth={s}": c0 & (doc == "pan") & (fifth == s) for s in sorted(set(fifth[doc == "pan"]))}
        cells |= {f"{d}/id_read_exact={v}": c0 & (doc == d) & (idok == v) for d in DOCS for v in (1, 0)}
        cells |= {f"pan/name_read_exact={v}": c0 & (doc == "pan") & (name_ok == v) for v in (1, 0)}
        for k, mm in cells.items():
            v, reps = bt.rate(f, mm)
            rows[k] = {"n": int(mm.sum()), "fpr": pct(v),
                       "ci": [round(100 * x, 1) for x in ci(reps)] if v is not None else None}
        e8[sname] = rows
    chk = Counter((doc[k], rules[i]["ocr_failed_checks"]) for k, i in enumerate(ids) if c0[k] and oc[k])
    e8["rules_OCR_failing_check_on_C0"] = {f"{d}/{c}": n for (d, c), n in sorted(chk.items())}
    res["E8"] = e8

    # ---- E9/E12: explanations of eligible images
    e9 = {}
    for (d, c), tied in TIED.items():
        mm = (doc == d) & (cat == c)
        for cond, col in (("GT", "gt_failed_checks"), ("OCR", "ocr_failed_checks")):
            fl = gt if cond == "GT" else oc
            failed = [set(filter(None, rules[i][col].split(";"))) for i in ids]
            mech = np.array([bool(failed[k] & tied) for k in range(len(ids))]).astype(int)
            over = (fl == 1) & (mech == 0)
            v, reps = bt.rate(mech, mm)
            vf, repsf = bt.rate(fl, mm)
            flagged = mm & (fl == 1)
            other = Counter(";".join(sorted(failed[k])) for k in np.flatnonzero(flagged & (mech == 0)))
            e9[f"{d}/{c}/{cond}"] = {
                "n": int(mm.sum()), "flagged": pct(vf), "flagged_ci": [round(100 * x, 1) for x in ci(repsf)],
                "mechanism_aware": pct(v), "mechanism_aware_ci": [round(100 * x, 1) for x in ci(reps)],
                "over_attribution_n": int((over & mm).sum()),
                "share_of_flags_correct": pct(mech[flagged].mean()) if flagged.any() else None,
                "over_attributed_to": dict(other)}
    res["E9_E12"] = e9

    # ---- recovery among visually missed forgeries (RQ2)
    rec = {}
    for cond, fl in (("GT", gt), ("OCR", oc)):
        for c in ("C2", "C3", "C4"):
            for d in DOCS:
                mm = (cat == c) & (doc == d) & (preds["visual"] == 0)
                v, reps = bt.rate(fl, mm)
                rec[f"{cond}/{d}/{c}"] = {"visual_missed": int(mm.sum()), "rules_catch": int((fl[mm] == 1).sum()),
                                          "pct": pct(v), "ci": [round(100 * x, 1) for x in ci(reps)]}
    res["rules_on_visual_misses"] = rec

    out = ROOT / "experiments" / "results" / "analysis" / a.split
    out.mkdir(parents=True, exist_ok=True)
    (out / "analysis.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    (out / "report.md").write_text(report(res), encoding="utf-8")
    print(f"wrote {out.relative_to(ROOT)}/analysis.json and report.md")


# ----------------------------------------------------------------- report
def report(r):
    L = [f"# Step 16-17 analyses — {r['split']} split",
         "",
         f"{r['n_images']} images, {r['n_persons']} people. Person-clustered bootstrap, B = {r['B']}, "
         f"seed {r['seed']}, shared replicates (paired). Percentages. Families and Holm correction: "
         "DECISIONS.md Section 22.", ""]
    s = r["systems"]
    L += ["## Systems", "",
          "| System | Recall [95% CI] | FPR [95% CI] | Precision | F1 | C1 | C2 | C3 | C4 |",
          "|---|---|---|---|---|---|---|---|---|"]
    for n, v in s.items():
        L.append(f"| {n} | {v['forged']['value']} {v['forged']['ci']} | {v['c0']['value']} {v['c0']['ci']} | "
                 f"{v['precision']} | {v['f1']} | " + " | ".join(str(v[c]['value']) for c in CATS[1:]) + " |")
    L += ["", "## Flag rate by document type and category", "",
          "| System | " + " | ".join(f"{d} {c}" for d in DOCS for c in CATS) + " |",
          "|---|" + "---|" * 10]
    for n, v in s.items():
        L.append(f"| {n} | " + " | ".join(str(v[f'{d}/{c}']['value']) for d in DOCS for c in CATS) + " |")
    L += ["", "## Delta and rho", "", "| Quantity | Value | 95% CI |", "|---|---|---|"]
    for k, v in r["delta_rho"].items():
        L.append(f"| {k} | {v['value']} | {v['ci']} |")
    L += ["", "## Families (Holm within family)", ""]
    for fam, rows in r["families"].items():
        L += [f"### {fam}", "", "| ID | Comparison | Diff | 95% CI | p | p (Holm) | FPR diff [CI] |",
              "|---|---|---|---|---|---|---|"]
        for x in rows:
            fd = f"{x['fpr_diff']:+.1f} {x['fpr_ci']}" if "fpr_diff" in x else ""
            L.append(f"| {x['id']} | {x['label']} | {x['diff']:+.1f} | {x['ci']} | {fmt_p(x['p'])} | "
                     f"{fmt_p(x['p_holm'])} | {fd} |")
        L.append("")
    L += ["### Post-hoc (A5; not in any family)", "", "| ID | Comparison | Diff | 95% CI | p |", "|---|---|---|---|---|"]
    for x in r["posthoc_A5"]:
        L.append(f"| {x['id']} | {x['label']} | {x['diff']:+.1f} | {x['ci']} | {fmt_p(x['p'])} |")
    e = r["E_vis"]
    L += ["", "## E-vis (RQ1): AUROC against C0", "", "| Subset | Tiles [CI] | Whole card [CI] | Diff [CI] | p |",
          "|---|---|---|---|---|"]
    for k, v in e.items():
        if k in ("per_seed_auroc", "visual_bounding_check"):
            continue
        L.append(f"| {k} | {v['visual']['auroc']} {v['visual']['ci']} | {v['base']['auroc']} {v['base']['ci']} | "
                 f"{v['diff']['auroc']:+.3f} {v['diff']['ci']} | {fmt_p(v['diff']['p'])} |")
    L += ["", "Per-seed AUROC (mean ± SD over 5 seeds):", ""]
    for name, per in e["per_seed_auroc"].items():
        L.append(f"- {name}: " + "; ".join(f"{k} {v['mean']} ± {v['sd']} {v['per_seed']}" for k, v in per.items()))
    L += ["", "Visual bounding check (should be near 0.5): " +
          "; ".join(f"{c} vs C0 {v['auroc']} {v['ci']}" for c, v in e["visual_bounding_check"].items()), ""]
    L += ["## E6 (RQ4): rule verdicts, GT vs OCR text", "",
          "| Cell | n | stable pass | stable fail | OCR-induced | OCR-masked |", "|---|---|---|---|---|---|"]
    for k, v in r["E6"].items():
        L.append(f"| {k} | {v['n']} | {v['stable_pass']} | {v['stable_fail']} | {v['ocr_induced']} | {v['ocr_masked']} |")
    L += ["", "## E8 (RQ6): C0 false-positive rate by stratum", ""]
    for sname in ("rules_OCR", "A4_OCR", "A5_OCR", "visual"):
        L += [f"### {sname}", "", "| Cell | n | FPR | 95% CI |", "|---|---|---|---|"]
        for k, v in r["E8"][sname].items():
            L.append(f"| {k} | {v['n']} | {v['fpr']} | {v['ci']} |")
        L.append("")
    L.append("Failing check on flagged C0 (rules-OCR): " +
             ", ".join(f"{k} {n}" for k, n in r["E8"]["rules_OCR_failing_check_on_C0"].items()))
    L += ["", "## E9/E12 (RQ2): explanations on images the rules target", "",
          "| Cell | n | Flagged [CI] | Mechanism-aware [CI] | Over-attribution n | Correct share of flags | Over-attributed to |",
          "|---|---|---|---|---|---|---|"]
    for k, v in r["E9_E12"].items():
        L.append(f"| {k} | {v['n']} | {v['flagged']} {v['flagged_ci']} | {v['mechanism_aware']} {v['mechanism_aware_ci']} | "
                 f"{v['over_attribution_n']} | {v['share_of_flags_correct']} | {v['over_attributed_to']} |")
    L += ["", "## Rules on forgeries the visual branch misses (RQ2)", "",
          "| Cell | visual missed | rules catch | % [CI] |", "|---|---|---|---|"]
    for k, v in r["rules_on_visual_misses"].items():
        L.append(f"| {k} | {v['visual_missed']} | {v['rules_catch']} | {v['pct']} {v['ci']} |")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    main()
