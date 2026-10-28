"""E2 visual baseline, variant `tiles` (Amendment A2, DECISIONS.md Section 14).

ResNet-50 (IMAGENET1K_V2, one-logit head) trained on 256 x 256 tiles of the
original, un-resized images (see tiles.py). Document score = max tile logit.

Same as variant `base` wherever possible: plain BCE, no augmentation, AdamW
lr 1e-4 / weight decay 1e-4, 1 warm-up epoch then cosine decay over 30 epochs,
fp16 autocast, batch 32, early stopping on DOCUMENT-level validation PR-AUC
(C0 vs C1) with patience 5.

Per epoch the training set is all positive tiles plus NEG_RATIO times as many
negative tiles drawn afresh (seeded) from all negative tiles of train C0/C1.

    python experiments/e2_visual/train_tiles.py --dry-run          # 1-2 minute code check, no outputs kept
    python experiments/e2_visual/train_tiles.py --seed 0
    python experiments/e2_visual/train_tiles.py --seed 0 --run-name native_tiles_rerun   # Step 21

Step 21 re-run (DECISIONS.md Section 23): --run-name native_tiles_rerun writes to
runs/native_tiles_rerun/seed<k>/ and does NOT score the test split (validation and
training scores only). Training is otherwise identical.

Outputs in experiments/e2_visual/runs/native_tiles/seed<k>/:
  config.json, epochs.jsonl, best.pt (git-ignored), summary.json,
  scores_trainval.csv and the SEALED scores_test.csv. Each scores file has the
  document logit (max over tiles), the index of the highest tile and all 15
  tile logits.
"""

import argparse
import csv
import hashlib
import json
import math
import platform
import random
import shutil
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torchvision

sys.path.insert(0, str(Path(__file__).resolve().parent))
from data import read_index  # noqa: E402
from metrics import average_precision, roc_auc  # noqa: E402
from tiles import GRID, TileImageSet, TileTrainSet, read_regions, training_tiles  # noqa: E402
from train import check_gates, seed_everything, worker_init  # noqa: E402

ROOT = Path.cwd()
BATCH = 32
IMG_BATCH = 4            # images per scoring batch (= 60 tiles)
NEG_RATIO = 8
ALL_CATS = ("C0", "C1", "C2", "C3", "C4")
# read_index needs a cache manifest only to cross-check metadata; the 768x512 one is used.
INDEX_SIZE = "768x512"


def build_model():
    model = torchvision.models.resnet50(weights=torchvision.models.ResNet50_Weights.IMAGENET1K_V2)
    model.fc = torch.nn.Linear(model.fc.in_features, 1)
    return model


@torch.no_grad()
def score_images(model, ds, workers, dev):
    model.eval()
    loader = torch.utils.data.DataLoader(ds, batch_size=IMG_BATCH, shuffle=False,
                                         num_workers=workers, pin_memory=True)
    ids, tile_logits, labels = [], [], []
    for x, y, iid in loader:                                   # x: (B, 15, 3, 256, 256)
        b, t = x.shape[:2]
        with torch.autocast(device_type="cuda", dtype=torch.float16):
            z = model(x.view(b * t, *x.shape[2:]).to(dev, non_blocking=True)).squeeze(1)
        tile_logits.append(z.float().view(b, t).cpu().numpy())
        labels.append(y.numpy())
        ids.extend(iid)
    tl = np.concatenate(tile_logits)
    return ids, tl, np.concatenate(labels)


def write_scores(path, rows, ids, tl):
    by_id = {r["image_id"]: r for r in rows}
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["image_id", "split", "doc_type", "forgery_category", "label", "logit",
                    "top_tile"] + [f"tile{k}" for k in range(len(GRID))])
        for iid, z in zip(ids, tl):
            r = by_id[iid]
            w.writerow([iid, r["split"], r["doc_type"], r["forgery_category"], r["label"],
                        f"{float(z.max()):.6f}", int(z.argmax())] + [f"{float(v):.6f}" for v in z])
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, choices=[0, 1, 2, 3, 4])
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--run-name", default="native_tiles", choices=["native_tiles", "native_tiles_rerun"],
                    help="native_tiles_rerun = Step 21 reproduction run; the test split is not scored")
    ap.add_argument("--dry-run", action="store_true",
                    help="20 training steps + scoring 40 val images; checks the code, keeps nothing")
    a = ap.parse_args()
    if a.seed is None and not a.dry_run:
        sys.exit("give --seed (or --dry-run)")
    seed = 0 if a.dry_run else a.seed

    cfg = dict(variant="tiles", seed=seed, weights="IMAGENET1K_V2", lr=1e-4, weight_decay=1e-4,
               warmup_epochs=1, max_epochs=30, patience=5, batch=BATCH, grad_accumulation=1,
               neg_ratio=NEG_RATIO, tile=256, stride=192, canvas="1024x640, top-left, white pad, no resize",
               pos_rule="tile holds >= 25% of edit region; 0 < overlap < 25% ignored",
               doc_score="max tile logit", loss="BCEWithLogits, unweighted", augmentation="none",
               amp="float16 autocast + GradScaler",
               early_stop_metric="document-level val PR-AUC (C0 vs C1)",
               lr_schedule="linear warm-up over epoch 1, then cosine to 0 at max_epochs (per step)")
    commit = None if a.dry_run else check_gates()
    if not torch.cuda.is_available():
        sys.exit("STOP: CUDA is not available.")

    run = ROOT / "experiments" / "e2_visual" / "runs" / a.run_name / f"seed{seed}"
    score_test = a.run_name == "native_tiles"
    if not a.dry_run:
        if (run / "summary.json").exists():
            sys.exit(f"STOP: {run} already holds a completed run. Runs are never overwritten.")
        if run.exists():
            shutil.rmtree(run)
        run.mkdir(parents=True)

    regions_path = ROOT / "experiments" / "e2_visual" / "c1_regions.csv"
    dev = torch.device("cuda")
    props = torch.cuda.get_device_properties(0)
    cfg.update(commit=commit,
               c1_regions_sha256=hashlib.sha256(regions_path.read_bytes()).hexdigest(),
               env=dict(python=platform.python_version(), platform=platform.platform(),
                        torch=torch.__version__, torchvision=torchvision.__version__,
                        cuda=torch.version.cuda, gpu=props.name,
                        vram_gb=round(props.total_memory / 2**30, 2)))
    print(json.dumps(cfg, indent=2))
    if not a.dry_run:
        (run / "config.json").write_text(json.dumps(cfg, indent=2), encoding="utf-8")

    seed_everything(seed)
    regions = read_regions(ROOT)
    train_rows = read_index(ROOT, INDEX_SIZE, ("train",), ("C0", "C1"))
    val_rows = read_index(ROOT, INDEX_SIZE, ("val",), ("C0", "C1"))
    items = training_tiles(train_rows, regions)
    pos = [it for it in items if it[2] == 1]
    neg = [it for it in items if it[2] == 0]
    n_neg = min(len(neg), NEG_RATIO * len(pos))
    print(f"train tiles: {len(pos)} positive, {len(neg)} negative pool; {n_neg} negatives per epoch")
    rng = random.Random(seed)
    val_ds = TileImageSet(ROOT, val_rows if not a.dry_run else val_rows[:20] + val_rows[-20:])

    model = build_model().to(dev)
    opt = torch.optim.AdamW(model.parameters(), lr=cfg["lr"], weight_decay=cfg["weight_decay"])
    scaler = torch.amp.GradScaler("cuda")
    loss_fn = torch.nn.BCEWithLogitsLoss()
    steps_per_epoch = (len(pos) + n_neg) // BATCH
    total_steps = steps_per_epoch * cfg["max_epochs"]
    warmup = steps_per_epoch * cfg["warmup_epochs"]
    sched = torch.optim.lr_scheduler.LambdaLR(
        opt, lambda s: (s + 1) / warmup if s < warmup else
        0.5 * (1 + math.cos(math.pi * (s - warmup) / max(1, total_steps - warmup))))

    best_ap, best_auc, best_epoch, since_best = -1.0, None, 0, 0
    t_start = time.time()
    for epoch in range(1, cfg["max_epochs"] + 1):
        epoch_items = pos + rng.sample(neg, n_neg)
        loader = torch.utils.data.DataLoader(
            TileTrainSet(ROOT, train_rows, epoch_items), batch_size=BATCH, shuffle=True,
            drop_last=True, num_workers=a.workers, pin_memory=True, worker_init_fn=worker_init,
            generator=torch.Generator().manual_seed(seed * 1000 + epoch))
        model.train()
        t0 = time.time()
        total, n = 0.0, 0
        for i, (x, y) in enumerate(loader):
            if a.dry_run and i == 20:
                break
            x, y = x.to(dev, non_blocking=True), y.to(dev, non_blocking=True)
            opt.zero_grad(set_to_none=True)
            with torch.autocast(device_type="cuda", dtype=torch.float16):
                logits = model(x).squeeze(1)
            loss = loss_fn(logits.float(), y)
            if not torch.isfinite(loss):
                sys.exit(f"STOP: non-finite loss at epoch {epoch}, batch {i}.")
            scaler.scale(loss).backward()
            scaler.step(opt)
            scaler.update()
            sched.step()
            total += float(loss.detach()) * len(y)
            n += len(y)

        ids, tl, yv = score_images(model, val_ds, a.workers, dev)
        doc = tl.max(axis=1)
        val_ap, val_auc = average_precision(yv, doc), roc_auc(yv, doc)
        rec = dict(epoch=epoch, train_loss=round(total / n, 5), val_pr_auc=round(val_ap, 5),
                   val_auroc=round(val_auc, 5), lr_end=opt.param_groups[0]["lr"],
                   sec=round(time.time() - t0, 1))
        print(json.dumps(rec), flush=True)
        if a.dry_run:
            peak = torch.cuda.max_memory_reserved() / 2**30
            print(f"\nDRY RUN PASS: training steps, scoring of {len(ids)} val images "
                  f"({tl.shape[1]} tiles each) and metrics all ran. Peak GPU memory {peak:.2f} GB "
                  f"of {props.total_memory / 2**30:.2f} GB. Nothing was saved.")
            return
        with (run / "epochs.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")
        if val_ap > best_ap:
            best_ap, best_auc, best_epoch, since_best = val_ap, val_auc, epoch, 0
            torch.save(model.state_dict(), run / "best.pt")
        else:
            since_best += 1
            if since_best >= cfg["patience"]:
                print(f"early stop: no val PR-AUC gain for {cfg['patience']} epochs")
                break

    model.load_state_dict(torch.load(run / "best.pt", map_location=dev, weights_only=True))
    trainval_rows = read_index(ROOT, INDEX_SIZE, ("train", "val"), ALL_CATS)
    ids, tl, _ = score_images(model, TileImageSet(ROOT, trainval_rows), a.workers, dev)
    sha_tv = write_scores(run / "scores_trainval.csv", trainval_rows, ids, tl)
    if score_test:
        test_rows = read_index(ROOT, INDEX_SIZE, ("test",), ALL_CATS)
        ids_t, tl_t, _ = score_images(model, TileImageSet(ROOT, test_rows), a.workers, dev)
        sha_t = write_scores(run / "scores_test.csv", test_rows, ids_t, tl_t)
        if len(set(ids) | set(ids_t)) != 10800:
            sys.exit("STOP: did not score exactly 10,800 distinct images.")
    else:
        ids_t, sha_t = [], None
        if len(set(ids)) != 9180:
            sys.exit("STOP: did not score exactly 9,180 train/val images.")
    summary = dict(best_epoch=best_epoch, best_val_pr_auc=round(best_ap, 5),
                   best_val_auroc=round(best_auc, 5), epochs_run=epoch,
                   minutes=round((time.time() - t_start) / 60, 1),
                   scores_trainval_sha256=sha_tv, scores_test_sha256=sha_t,
                   n_trainval_scored=len(ids), n_test_scored=len(ids_t))
    (run / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print("\nDONE", json.dumps(summary, indent=2))
    if score_test:
        print("Do not open scores_test.csv before Step 15.")
    else:
        print("Step 21 re-run: compare with  python experiments/e2_visual/compare_rerun.py --seed", seed)


if __name__ == "__main__":
    main()
