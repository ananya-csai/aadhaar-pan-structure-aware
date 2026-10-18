"""E2 visual baseline: ResNet-50, C0 vs C1 (roadmap Step 10; DECISIONS.md Sections 2, 3, 5, 13).

One run = one canvas size + one seed + one variant.

Variant "base" follows DECISIONS.md Section 13:
  IMAGENET1K_V2 weights, one-logit head, plain BCE, no augmentation,
  AdamW (lr 1e-4, weight decay 1e-4), 1 warm-up epoch then cosine decay,
  fp16 autocast, effective batch 32 via gradient accumulation,
  at most 30 epochs, early stopping on validation PR-AUC with patience 5.
Variant "reg" (Amendment A2) is identical except: trace-preserving augmentation
  (integer-pixel shift up to +-16 px with white fill; per-image contrast x[0.9, 1.1]
  and brightness +-0.05; no resampling, blurring or re-compression), dropout 0.5 before the head,
  and weight decay 0.05.

Guards (the run refuses to start otherwise):
  * DECISIONS.md has no unfilled [[FILL ...]] fields;
  * tag protocol-e2-final exists and is an ancestor of HEAD;
  * no modified tracked files (so the recorded commit is the code that ran);
  * the run folder has no completed run in it.

Outputs in experiments/e2_visual/runs/<size>/seed<k>/ (base) or
experiments/e2_visual/runs/<size>_<variant>/seed<k>/ (other variants):
  config.json           settings, commit, environment, cache hash
  epochs.jsonl          per-epoch train loss, val PR-AUC, val AUROC, lr, time
  best.pt               best checkpoint (git-ignored, ~95 MB)
  scores_trainval.csv   logit of the best checkpoint for every train/val image (C0-C4)
  scores_test.csv       the same for test images -- SEALED: do not open before Step 15
  summary.json          best epoch, best val metrics, runtime, SHA-256 of both score files

    python experiments/e2_visual/train.py --size 768x512 --seed 0
    python experiments/e2_visual/train.py --size 768x512 --seed 0 --variant reg
"""

import argparse
import csv
import hashlib
import json
import math
import platform
import random
import shutil
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torchvision

sys.path.insert(0, str(Path(__file__).resolve().parent))
from data import IMAGENET_MEAN, IMAGENET_STD, make_dataset  # noqa: E402
from metrics import average_precision, roc_auc  # noqa: E402

ROOT = Path.cwd()
EFFECTIVE_BATCH = 32
PRIMARY = ("C0", "C1")
ALL_CATS = ("C0", "C1", "C2", "C3", "C4")


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)


def check_gates():
    text = (ROOT / "DECISIONS.md").read_text(encoding="utf-8")
    if "[[FILL" in text:
        sys.exit("STOP: DECISIONS.md still has [[FILL ...]] fields. Record the approval first.")
    if git("rev-parse", "-q", "--verify", "refs/tags/protocol-e2-final").returncode != 0:
        sys.exit("STOP: tag protocol-e2-final does not exist.")
    if git("merge-base", "--is-ancestor", "protocol-e2-final", "HEAD").returncode != 0:
        sys.exit("STOP: HEAD does not contain the protocol-e2-final commit.")
    dirty = git("status", "--porcelain", "--untracked-files=no").stdout.strip()
    if dirty:
        sys.exit(f"STOP: tracked files are modified; commit or revert them first:\n{dirty}")
    return git("rev-parse", "HEAD").stdout.strip()


def seed_everything(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.benchmark = False


def worker_init(worker_id):
    s = torch.initial_seed() % 2**32
    np.random.seed(s)
    random.seed(s)


def batch_from_smoke_log(size):
    log = ROOT / "experiments" / "e2_visual" / "logs" / f"smoke_{size}.json"
    data = json.loads(log.read_text(encoding="utf-8"))
    if data.get("result") != "PASS":
        sys.exit(f"STOP: {log} is not a passing smoke test.")
    return int(data["stages"]["C_batch_probe"]["chosen_batch"])


VARIANTS = {
    "base": dict(weight_decay=1e-4, dropout=0.0, augmentation="none"),
    "reg": dict(weight_decay=0.05, dropout=0.5,
                augmentation="integer shift <=16 px (white fill); per-image contrast x[0.9,1.1], brightness +-0.05"),
}
MAX_SHIFT = 16


def build_model(weights_name, dropout):
    model = torchvision.models.resnet50(weights=torchvision.models.ResNet50_Weights[weights_name])
    head = torch.nn.Linear(model.fc.in_features, 1)
    model.fc = head if dropout == 0 else torch.nn.Sequential(torch.nn.Dropout(dropout), head)
    return model


def augment(x, gen):
    """Trace-preserving augmentation on a normalised batch (B,3,H,W) on the GPU.

    Shift: pad with white by MAX_SHIFT and crop back at a random integer offset,
    so pixels move but are never resampled. Photometric: one contrast factor and
    one brightness offset per image, applied to the whole image.
    """
    mean = torch.tensor(IMAGENET_MEAN, device=x.device).view(1, 3, 1, 1)
    std = torch.tensor(IMAGENET_STD, device=x.device).view(1, 3, 1, 1)
    raw = x * std + mean                                       # back to [0, 1]
    b, _, h, w = raw.shape
    padded = torch.nn.functional.pad(raw, (MAX_SHIFT,) * 4, value=1.0)
    offs = torch.randint(0, 2 * MAX_SHIFT + 1, (b, 2), device=x.device, generator=gen)
    raw = torch.stack([padded[i, :, offs[i, 0]:offs[i, 0] + h, offs[i, 1]:offs[i, 1] + w]
                       for i in range(b)])
    c = 1.0 + (torch.rand(b, 1, 1, 1, device=x.device, generator=gen) * 0.2 - 0.1)
    s = torch.rand(b, 1, 1, 1, device=x.device, generator=gen) * 0.1 - 0.05
    raw = ((raw - 0.5) * c + 0.5 + s).clamp(0.0, 1.0)
    return (raw - mean) / std


def eval_loader(ds, batch, workers, persistent=False):
    return torch.utils.data.DataLoader(ds, batch_size=batch, shuffle=False, num_workers=workers,
                                       pin_memory=True,
                                       persistent_workers=persistent and workers > 0)


@torch.no_grad()
def predict(model, loader, dev):
    model.eval()
    ids, logits, labels = [], [], []
    for x, y, iid in loader:
        with torch.autocast(device_type="cuda", dtype=torch.float16):
            out = model(x.to(dev, non_blocking=True)).squeeze(1)
        logits.append(out.float().cpu().numpy())
        labels.append(y.numpy())
        ids.extend(iid)
    return ids, np.concatenate(logits), np.concatenate(labels)


def write_scores(path, ds, ids, logits):
    by_id = {r["image_id"]: r for r in ds.rows}
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["image_id", "split", "doc_type", "forgery_category", "label", "logit"])
        for iid, z in zip(ids, logits):
            r = by_id[iid]
            w.writerow([iid, r["split"], r["doc_type"], r["forgery_category"], r["label"],
                        f"{float(z):.6f}"])
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--size", required=True, choices=["768x512", "384x256"])
    ap.add_argument("--seed", type=int, required=True, choices=[0, 1, 2, 3, 4])
    ap.add_argument("--variant", default="base", choices=sorted(VARIANTS))
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()

    v = VARIANTS[a.variant]
    cfg = dict(size=a.size, seed=a.seed, variant=a.variant, weights="IMAGENET1K_V2", lr=1e-4,
               weight_decay=v["weight_decay"], dropout=v["dropout"],
               warmup_epochs=1, max_epochs=30, patience=5, effective_batch=EFFECTIVE_BATCH,
               loss="BCEWithLogits, unweighted", augmentation=v["augmentation"],
               amp="float16 autocast + GradScaler", early_stop_metric="val PR-AUC (C0 vs C1)",
               lr_schedule="linear warm-up over epoch 1, then cosine to 0 at max_epochs (per optimizer step)",
               train_drop_last=True)
    commit = check_gates()
    if not torch.cuda.is_available():
        sys.exit("STOP: CUDA is not available.")
    batch = batch_from_smoke_log(a.size)
    if EFFECTIVE_BATCH % batch:
        sys.exit(f"STOP: batch {batch} does not divide {EFFECTIVE_BATCH}.")
    accum = EFFECTIVE_BATCH // batch
    cfg.update(batch=batch, grad_accumulation=accum, workers=a.workers)

    folder = a.size if a.variant == "base" else f"{a.size}_{a.variant}"
    run = ROOT / "experiments" / "e2_visual" / "runs" / folder / f"seed{a.seed}"
    if (run / "summary.json").exists():
        sys.exit(f"STOP: {run} already holds a completed run. Runs are never overwritten.")
    if run.exists():
        shutil.rmtree(run)                     # incomplete earlier attempt
    run.mkdir(parents=True)

    fp = ROOT / "experiments" / "cache_fingerprints" / f"{a.size}_SHA256.txt"
    cache_sha = fp.read_text(encoding="utf-8").splitlines()[0].split(": ", 1)[1]
    dev = torch.device("cuda")
    props = torch.cuda.get_device_properties(0)
    cfg.update(commit=commit, cache_sha256=cache_sha,
               env=dict(python=platform.python_version(), platform=platform.platform(),
                        torch=torch.__version__, torchvision=torchvision.__version__,
                        cuda=torch.version.cuda, cudnn=torch.backends.cudnn.version(),
                        gpu=props.name, vram_gb=round(props.total_memory / 2**30, 2)))
    (run / "config.json").write_text(json.dumps(cfg, indent=2), encoding="utf-8")
    print(json.dumps(cfg, indent=2))

    seed_everything(a.seed)
    train_ds = make_dataset(ROOT, a.size, ("train",), PRIMARY)
    val_ds = make_dataset(ROOT, a.size, ("val",), PRIMARY)
    loader = torch.utils.data.DataLoader(
        train_ds, batch_size=batch, shuffle=True, drop_last=True, num_workers=a.workers,
        pin_memory=True, persistent_workers=a.workers > 0, worker_init_fn=worker_init,
        generator=torch.Generator().manual_seed(a.seed))

    val_loader = eval_loader(val_ds, batch, a.workers, persistent=True)

    model = build_model(cfg["weights"], cfg["dropout"]).to(dev)
    aug_gen = torch.Generator(device="cuda").manual_seed(a.seed + 1000)
    opt = torch.optim.AdamW(model.parameters(), lr=cfg["lr"], weight_decay=cfg["weight_decay"])
    scaler = torch.amp.GradScaler("cuda")
    loss_fn = torch.nn.BCEWithLogitsLoss()
    steps_per_epoch = len(loader) // accum
    total_steps = steps_per_epoch * cfg["max_epochs"]
    warmup = steps_per_epoch * cfg["warmup_epochs"]

    def lr_factor(step):                   # step = optimizer steps already taken
        if step < warmup:
            return (step + 1) / warmup
        return 0.5 * (1 + math.cos(math.pi * (step - warmup) / max(1, total_steps - warmup)))

    sched = torch.optim.lr_scheduler.LambdaLR(opt, lr_factor)

    best_ap, best_epoch, since_best = -1.0, 0, 0
    t_start = time.time()
    for epoch in range(1, cfg["max_epochs"] + 1):
        model.train()
        t0 = time.time()
        total, n = 0.0, 0
        opt.zero_grad(set_to_none=True)
        usable = steps_per_epoch * accum   # whole accumulation groups only
        for i, (x, y, _) in enumerate(loader):
            if i >= usable:
                break
            x, y = x.to(dev, non_blocking=True), y.to(dev, non_blocking=True)
            if cfg["augmentation"] != "none":
                x = augment(x, aug_gen)
            with torch.autocast(device_type="cuda", dtype=torch.float16):
                logits = model(x).squeeze(1)
            loss = loss_fn(logits.float(), y)
            if not torch.isfinite(loss):
                sys.exit(f"STOP: non-finite loss at epoch {epoch}, batch {i}.")
            scaler.scale(loss / accum).backward()
            total += float(loss.detach()) * len(y)
            n += len(y)
            if (i + 1) % accum == 0:
                scaler.step(opt)
                scaler.update()
                opt.zero_grad(set_to_none=True)
                sched.step()

        ids, z, yv = predict(model, val_loader, dev)
        val_ap, val_auc = average_precision(yv, z), roc_auc(yv, z)
        rec = dict(epoch=epoch, train_loss=round(total / n, 5), val_pr_auc=round(val_ap, 5),
                   val_auroc=round(val_auc, 5), lr_end=opt.param_groups[0]["lr"],
                   sec=round(time.time() - t0, 1))
        with (run / "epochs.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")
        print(json.dumps(rec), flush=True)

        if val_ap > best_ap:               # strict: ties keep the earlier epoch
            best_ap, best_auc, best_epoch, since_best = val_ap, val_auc, epoch, 0
            torch.save(model.state_dict(), run / "best.pt")
        else:
            since_best += 1
            if since_best >= cfg["patience"]:
                print(f"early stop: no val PR-AUC gain for {cfg['patience']} epochs")
                break

    # Score every image with the best checkpoint. Test scores go to a separate, sealed file.
    model.load_state_dict(torch.load(run / "best.pt", map_location=dev, weights_only=True))
    trainval = make_dataset(ROOT, a.size, ("train", "val"), ALL_CATS)
    test = make_dataset(ROOT, a.size, ("test",), ALL_CATS)
    ids, z, _ = predict(model, eval_loader(trainval, batch, a.workers), dev)
    sha_tv = write_scores(run / "scores_trainval.csv", trainval, ids, z)
    ids_t, z_t, _ = predict(model, eval_loader(test, batch, a.workers), dev)
    sha_t = write_scores(run / "scores_test.csv", test, ids_t, z_t)
    if len(ids) + len(ids_t) != 10800 or len(set(ids) | set(ids_t)) != 10800:
        sys.exit("STOP: did not score exactly 10,800 distinct images.")

    summary = dict(best_epoch=best_epoch, best_val_pr_auc=round(best_ap, 5),
                   best_val_auroc=round(best_auc, 5), epochs_run=epoch,
                   minutes=round((time.time() - t_start) / 60, 1),
                   scores_trainval_sha256=sha_tv, scores_test_sha256=sha_t,
                   n_trainval_scored=len(ids), n_test_scored=len(ids_t))
    (run / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print("\nDONE", json.dumps(summary, indent=2))
    print("Do not open scores_test.csv before Step 15.")


if __name__ == "__main__":
    main()
