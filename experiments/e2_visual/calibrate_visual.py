"""Roadmap Steps 11 and 13: check every visual run, calibrate each seed, build the
5-seed ensemble and choose the visual-only operating point. VALIDATION ONLY.

For each model (`tiles` = visual branch, `base` = E-vis comparison):
  1. Check every run: summary.json present, scores_trainval.csv hash matches,
     exactly the 9,180 train+val image_ids, labels/splits/categories match the
     manifest, no duplicates, finite logits. scores_test.csv is NOT opened; only
     its recorded hash is copied into the output so Step 15 can prove it is
     the same file.
  2. Temperature scaling per seed: one scalar T fitted by minimising the
     negative log-likelihood of validation C0 vs C1 labels (DECISIONS.md
     Section 4). Expected calibration error (10 equal-width bins) is reported
     before and after.
  3. Ensemble: mean of the 5 calibrated probabilities (Section 5).
  4. Operating point: the threshold on the ensemble probability that
     maximises validation C1 recall subject to validation C0 FPR <= 5%.

Writes experiments/e2_visual/frozen/<model>_calibration.json,
<model>_ensemble_trainval.csv and <model>_reliability.csv.

    python experiments/e2_visual/calibrate_visual.py
"""

import csv
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import minimize_scalar

sys.path.insert(0, str(Path(__file__).resolve().parent))
from metrics import average_precision, roc_auc  # noqa: E402

ROOT = Path.cwd()
RUNS = ROOT / "experiments" / "e2_visual" / "runs"
OUT = ROOT / "experiments" / "e2_visual" / "frozen"
MODELS = {"tiles": RUNS / "native_tiles", "base": RUNS / "768x512"}
SEEDS = (0, 1, 2, 3, 4)
TARGET_FPR = 0.05
N_BINS = 10


def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))


def nll(z, y, t):
    p = np.clip(sigmoid(z / t), 1e-12, 1 - 1e-12)
    return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))


def fit_temperature(z, y):
    res = minimize_scalar(lambda lt: nll(z, y, np.exp(lt)), bounds=(-4.0, 4.0), method="bounded",
                          options={"xatol": 1e-6})
    if not res.success:
        raise RuntimeError("temperature fit failed")
    t = float(np.exp(res.x))
    if t > 50 or t < 0.02:
        raise RuntimeError(f"temperature {t} hit the search bound")
    return t


def ece(p, y, bins=N_BINS):
    edges = np.linspace(0, 1, bins + 1)
    idx = np.clip(np.digitize(p, edges[1:-1]), 0, bins - 1)
    rows, total = [], 0.0
    for b in range(bins):
        m = idx == b
        if m.any():
            conf, acc = float(p[m].mean()), float(y[m].mean())
            total += m.mean() * abs(conf - acc)
            rows.append((b, int(m.sum()), conf, acc))
        else:
            rows.append((b, 0, float("nan"), float("nan")))
    return float(total), rows


def operating_point(p, y, target=TARGET_FPR):
    """Threshold t (flag if p >= t) maximising recall with FPR <= target."""
    neg, pos = np.sort(p[y == 0])[::-1], p[y == 1]
    k = int(np.floor(target * len(neg)))          # at most k negatives may be flagged
    if k >= len(neg):
        t = float(neg.min())
    else:
        # Strictly above the (k+1)-th highest negative score, placed halfway to the
        # next higher score of any image, so that last-digit floating-point
        # differences between machines cannot flip an image across the threshold.
        above = p[p > neg[k]]
        t = float((neg[k] + above.min()) / 2) if above.size else float(np.nextafter(neg[k], 1.0))
    fpr = float((p[y == 0] >= t).mean())
    rec = float((pos >= t).mean())
    assert fpr <= target + 1e-12
    return float(t), fpr, rec


def load_manifest():
    with (ROOT / "dataset" / "data" / "v1" / "manifest.csv").open(newline="", encoding="utf-8-sig") as f:
        return {r["image_id"]: r for r in csv.DictReader(f)}


def check_run(run, manifest):
    summ = json.loads((run / "summary.json").read_text(encoding="utf-8"))
    path = run / "scores_trainval.csv"
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    if sha != summ["scores_trainval_sha256"]:
        raise ValueError(f"{path}: hash differs from summary.json")
    if not (run / "scores_test.csv").is_file():
        raise ValueError(f"{run}: scores_test.csv missing")
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    ids = [r["image_id"] for r in rows]
    expected = {i for i, r in manifest.items() if r["split"] in ("train", "val")}
    if len(ids) != len(set(ids)) or set(ids) != expected:
        raise ValueError(f"{path}: image_ids are not exactly the 9,180 train+val images")
    for r in rows:
        mr = manifest[r["image_id"]]
        for col in ("split", "doc_type", "forgery_category", "label"):
            if r[col] != mr[col]:
                raise ValueError(f"{path}: {r['image_id']} {col} mismatch")
        if not np.isfinite(float(r["logit"])):
            raise ValueError(f"{path}: non-finite logit for {r['image_id']}")
    logits = {r["image_id"]: float(r["logit"]) for r in rows}
    return logits, summ


def main():
    manifest = load_manifest()
    OUT.mkdir(parents=True, exist_ok=True)
    trainval_ids = sorted(i for i, r in manifest.items() if r["split"] in ("train", "val"))
    val_ids = [i for i in trainval_ids if manifest[i]["split"] == "val"
               and manifest[i]["forgery_category"] in ("C0", "C1")]
    y_val = np.array([int(manifest[i]["label"]) for i in val_ids])

    for model, folder in MODELS.items():
        seeds, probs = [], []
        for s in SEEDS:
            run = folder / f"seed{s}"
            logits, summ = check_run(run, manifest)
            z_val = np.array([logits[i] for i in val_ids])
            t = fit_temperature(z_val, y_val)
            e_before, _ = ece(sigmoid(z_val), y_val)
            e_after, _ = ece(sigmoid(z_val / t), y_val)
            probs.append(np.array([sigmoid(logits[i] / t) for i in trainval_ids]))
            seeds.append(dict(seed=s, temperature=t,  # full precision: test scoring reuses it exactly
                              val_nll_before=round(nll(z_val, y_val, 1.0), 5),
                              val_nll_after=round(nll(z_val, y_val, t), 5),
                              val_ece_before=round(e_before, 5), val_ece_after=round(e_after, 5),
                              val_pr_auc=round(average_precision(y_val, z_val), 5),
                              val_auroc=round(roc_auc(y_val, z_val), 5),
                              best_epoch=summ["best_epoch"],
                              scores_trainval_sha256=summ["scores_trainval_sha256"],
                              scores_test_sha256=summ["scores_test_sha256"]))
            print(f"[{model}] seed {s}: T={t:.3f}  ECE {e_before:.3f} -> {e_after:.3f}")

        ens = np.mean(probs, axis=0)
        pos = {iid: k for k, iid in enumerate(trainval_ids)}
        p_val = np.array([ens[pos[i]] for i in val_ids])
        thr, fpr, rec = operating_point(p_val, y_val)
        e_ens, rel = ece(p_val, y_val)
        result = dict(model=model, seeds=seeds,
                      ensemble=dict(rule="mean of temperature-scaled probabilities over seeds 0-4",
                                    val_pr_auc=round(average_precision(y_val, p_val), 5),
                                    val_auroc=round(roc_auc(y_val, p_val), 5),
                                    val_ece=round(e_ens, 5)),
                      operating_point=dict(rule="max val C1 recall s.t. val C0 FPR <= 0.05",
                                           threshold=thr, val_fpr=round(fpr, 5),
                                           val_c1_recall=round(rec, 5),
                                           n_val_c0=int((y_val == 0).sum()),
                                           n_val_c1=int((y_val == 1).sum())),
                      note="Validation only. scores_test.csv files were not opened.")
        (OUT / f"{model}_calibration.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
        with (OUT / f"{model}_ensemble_trainval.csv").open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f, lineterminator="\n")
            w.writerow(["image_id", "split", "doc_type", "forgery_category", "label", "prob"])
            for iid, p in zip(trainval_ids, ens):
                r = manifest[iid]
                w.writerow([iid, r["split"], r["doc_type"], r["forgery_category"], r["label"],
                            f"{p:.6f}"])
        with (OUT / f"{model}_reliability.csv").open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f, lineterminator="\n")
            w.writerow(["bin", "n", "mean_confidence", "observed_c1_rate"])
            w.writerows(rel)
        print(f"[{model}] ensemble val PR-AUC {result['ensemble']['val_pr_auc']:.3f}, "
              f"AUROC {result['ensemble']['val_auroc']:.3f}; operating point t={thr:.4f}: "
              f"val FPR {fpr:.3f}, val C1 recall {rec:.3f}\n")
    print(f"PASS: wrote calibration, ensemble and reliability files to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
