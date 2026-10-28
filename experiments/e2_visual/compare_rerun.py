"""Step 21: compare a clean-environment re-run of one tile seed with the original run
(DECISIONS.md Section 23).

    python experiments/e2_visual/compare_rerun.py --seed 0

Pass rule (fixed before the re-run):
  1. same training configuration (every config.json key except commit, env);
  2. same edit-region file (c1_regions_sha256) and the frozen corpus (checked
     separately with dataset/scripts/corpus_checksum.py --verify, logged);
  3. best validation AUROC and PR-AUC inside the range of the five original
     seeds (min..max of their summary.json values).
Bit-identical scores are NOT expected (fp16, non-deterministic GPU kernels) and are
not part of the rule; their agreement is reported for information.

Writes runs/native_tiles_rerun/seed<k>/comparison.md and .json; validation only.
"""
import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments" / "e2_visual"))
from metrics import average_precision, roc_auc  # noqa: E402

RUNS = ROOT / "experiments" / "e2_visual" / "runs"
MANIFEST = ROOT / "dataset" / "data" / "v1" / "manifest.csv"


def load(run):
    cfg = json.loads((run / "config.json").read_text(encoding="utf-8"))
    summ = json.loads((run / "summary.json").read_text(encoding="utf-8"))
    epochs = [json.loads(l) for l in (run / "epochs.jsonl").read_text(encoding="utf-8").splitlines() if l]
    with (run / "scores_trainval.csv").open(newline="", encoding="utf-8") as f:
        scores = {r["image_id"]: float(r["logit"]) for r in csv.DictReader(f)}
    return cfg, summ, epochs, scores


def rank(x):
    order = np.argsort(x, kind="mergesort")
    r = np.empty(len(x))
    r[order] = np.arange(len(x))
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=0, choices=[0, 1, 2, 3, 4])
    a = ap.parse_args()
    orig_dir, new_dir = RUNS / "native_tiles" / f"seed{a.seed}", RUNS / "native_tiles_rerun" / f"seed{a.seed}"
    c0, s0, e0, z0 = load(orig_dir)
    c1, s1, e1, z1 = load(new_dir)

    ignore = {"commit", "env"}
    cfg_diff = {k: (c0.get(k), c1.get(k)) for k in sorted((set(c0) | set(c1)) - ignore) if c0.get(k) != c1.get(k)}
    env_diff = {k: (c0["env"].get(k), c1["env"].get(k)) for k in sorted(set(c0["env"]) | set(c1["env"]))
                if c0["env"].get(k) != c1["env"].get(k)}

    seeds = [json.loads((RUNS / "native_tiles" / f"seed{k}" / "summary.json").read_text(encoding="utf-8"))
             for k in range(5)]
    auc_rng = (min(s["best_val_auroc"] for s in seeds), max(s["best_val_auroc"] for s in seeds))
    ap_rng = (min(s["best_val_pr_auc"] for s in seeds), max(s["best_val_pr_auc"] for s in seeds))

    with MANIFEST.open(newline="", encoding="utf-8-sig") as f:
        man = {r["image_id"]: r for r in csv.DictReader(f)}
    val = sorted(i for i, r in man.items() if r["split"] == "val" and r["forgery_category"] in ("C0", "C1"))
    if not set(val) <= set(z1) or not set(val) <= set(z0):
        sys.exit("STOP: score files do not cover the validation C0/C1 images")
    y = np.array([int(man[i]["label"]) for i in val])
    v0, v1 = np.array([z0[i] for i in val]), np.array([z1[i] for i in val])
    re_auc, re_ap = roc_auc(y, v1), average_precision(y, v1)
    allv = sorted(i for i, r in man.items() if r["split"] == "val")
    w0, w1 = np.array([z0[i] for i in allv]), np.array([z1[i] for i in allv])

    checks = {
        "config identical (except commit/env)": not cfg_diff,
        "edit regions identical": c0["c1_regions_sha256"] == c1["c1_regions_sha256"],
        f"val AUROC in [{auc_rng[0]:.3f}, {auc_rng[1]:.3f}]": auc_rng[0] <= s1["best_val_auroc"] <= auc_rng[1],
        f"val PR-AUC in [{ap_rng[0]:.3f}, {ap_rng[1]:.3f}]": ap_rng[0] <= s1["best_val_pr_auc"] <= ap_rng[1],
        "summary metrics recomputed from scores": abs(re_auc - s1["best_val_auroc"]) < 1e-4
                                                  and abs(re_ap - s1["best_val_pr_auc"]) < 1e-4,
    }
    passed = all(checks.values())
    res = {
        "seed": a.seed, "passed": passed, "checks": checks, "config_differences": cfg_diff,
        "environment_differences": env_diff,
        "original": {k: s0[k] for k in ("best_epoch", "epochs_run", "minutes", "best_val_auroc", "best_val_pr_auc")},
        "rerun": {k: s1[k] for k in ("best_epoch", "epochs_run", "minutes", "best_val_auroc", "best_val_pr_auc")},
        "five_seed_range": {"auroc": auc_rng, "pr_auc": ap_rng},
        "agreement_val_all_categories": {
            "n": len(allv),
            "pearson": float(np.corrcoef(w0, w1)[0, 1]),
            "spearman": float(np.corrcoef(rank(w0), rank(w1))[0, 1]),
            "max_abs_logit_diff": float(np.abs(w0 - w1).max()),
            "bit_identical_scores": s0["scores_trainval_sha256"] == s1["scores_trainval_sha256"]},
        "epochs": [{"epoch": e["epoch"], "orig_val_pr_auc": e["val_pr_auc"],
                    "rerun_val_pr_auc": (e1[i]["val_pr_auc"] if i < len(e1) else None)}
                   for i, e in enumerate(e0)] + [{"epoch": e["epoch"], "orig_val_pr_auc": None,
                                                  "rerun_val_pr_auc": e["val_pr_auc"]} for e in e1[len(e0):]],
    }
    (new_dir / "comparison.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
    o, r = res["original"], res["rerun"]
    g = res["agreement_val_all_categories"]
    L = [f"# Step 21 re-run, tiles seed {a.seed}: {'PASS' if passed else 'FAIL'}", "",
         "| | Original | Re-run |", "|---|---|---|",
         f"| best epoch / epochs run | {o['best_epoch']} / {o['epochs_run']} | {r['best_epoch']} / {r['epochs_run']} |",
         f"| minutes | {o['minutes']} | {r['minutes']} |",
         f"| val AUROC (C0 vs C1) | {o['best_val_auroc']:.3f} | {r['best_val_auroc']:.3f} |",
         f"| val PR-AUC (C0 vs C1) | {o['best_val_pr_auc']:.3f} | {r['best_val_pr_auc']:.3f} |", "",
         "## Checks", ""] + [f"- {'PASS' if v else 'FAIL'}: {k}" for k, v in checks.items()] + [
         "", f"Config differences: {cfg_diff or 'none'}", f"Environment differences: {env_diff or 'none'}", "",
         f"Validation logits, all {g['n']} images: Pearson {g['pearson']:.3f}, Spearman {g['spearman']:.3f}, "
         f"max |diff| {g['max_abs_logit_diff']:.2f}, bit-identical: {g['bit_identical_scores']} "
         "(not expected; not part of the rule).", "",
         "| Epoch | original val PR-AUC | re-run val PR-AUC |", "|---|---|---|"] + [
         f"| {e['epoch']} | {e['orig_val_pr_auc']} | {e['rerun_val_pr_auc']} |" for e in res["epochs"]]
    (new_dir / "comparison.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L[:12]))
    print("PASS" if passed else "FAIL")


if __name__ == "__main__":
    main()
