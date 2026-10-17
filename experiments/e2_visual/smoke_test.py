"""E2 pre-training checks (roadmap Steps 8, 9 and 11; DECISIONS.md Section 10).

Stages, in order. The script stops at the first failure.
  A  environment record (GPU, VRAM, versions)
  B  loader checks on train/val (test is counted from the manifest, never loaded)
  C  batch-size probe at the cache size: largest of 32/16/8 that trains under AMP
  D  one real batch: forward, backward, finite loss and gradients
  E  tiny-overfit: 25 C0 + 25 C1 fixed train images; must reach >= 96% accuracy

Writes experiments/e2_visual/logs/smoke_<size>.json (commit it).

    python experiments/e2_visual/smoke_test.py --size 768x512
    python experiments/e2_visual/smoke_test.py --size 768x512 --loader-only   # no GPU needed
"""

import argparse
import json
import platform
import random
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np
import torch
import torchvision

sys.path.insert(0, str(Path(__file__).resolve().parent))
from data import (IMAGENET_MEAN, IMAGENET_STD, make_dataset, parse_size,  # noqa: E402
                  read_index)

ROOT = Path.cwd()
LOG_DIR = ROOT / "experiments" / "e2_visual" / "logs"
PRIMARY = ("C0", "C1")
BATCH_CANDIDATES = (32, 16, 8)
EFFECTIVE_BATCH = 32


def fail(msg, log, path):
    log["result"] = "FAIL"
    log["failure"] = msg
    path.write_text(json.dumps(log, indent=2), encoding="utf-8")
    print(f"\nFAIL: {msg}\nLog: {path}")
    sys.exit(1)


def build_model(weights_name):
    weights = torchvision.models.ResNet50_Weights[weights_name]
    model = torchvision.models.resnet50(weights=weights)
    model.fc = torch.nn.Linear(model.fc.in_features, 1)        # one-logit head
    return model


def train_step(model, opt, scaler, x, y, loss_fn):
    opt.zero_grad(set_to_none=True)
    with torch.autocast(device_type="cuda", dtype=torch.float16):
        logits = model(x).squeeze(1)
        loss = loss_fn(logits.float(), y)
    scaler.scale(loss).backward()
    scaler.step(opt)
    scaler.update()
    return loss


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--size", default="768x512")
    ap.add_argument("--weights", default="IMAGENET1K_V2",
                    help="torchvision ResNet50_Weights name; record the final choice in DECISIONS.md")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--overfit-epochs", type=int, default=40)
    ap.add_argument("--lr", type=float, default=1e-4)
    ap.add_argument("--loader-only", action="store_true")
    a = ap.parse_args()

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOG_DIR / (f"smoke_{a.size}" + ("_loader" if a.loader_only else "") + ".json")
    log = {"size": a.size, "weights": a.weights, "seed": a.seed, "stages": {}}
    random.seed(a.seed)
    np.random.seed(a.seed)
    torch.manual_seed(a.seed)
    W, H = parse_size(a.size)

    # ---- A. environment ---------------------------------------------------
    env = {"python": platform.python_version(), "platform": platform.platform(),
           "torch": torch.__version__, "torchvision": torchvision.__version__,
           "cuda_available": torch.cuda.is_available(),
           "torch_cuda": torch.version.cuda,
           "cudnn": torch.backends.cudnn.version() if torch.cuda.is_available() else None}
    if torch.cuda.is_available():
        p = torch.cuda.get_device_properties(0)
        env.update(gpu=p.name, vram_gb=round(p.total_memory / 2**30, 2))
    log["stages"]["A_environment"] = env
    print("[A] environment:", json.dumps(env))
    if not a.loader_only and not torch.cuda.is_available():
        fail("CUDA not available. Fix the GPU environment before any training.", log, log_path)

    # ---- B. loader --------------------------------------------------------
    counts = {}
    persons = {}
    for split in ("train", "val", "test"):
        rows = read_index(ROOT, a.size, (split,), PRIMARY)
        counts[split] = dict(sorted(Counter(r["forgery_category"] for r in rows).items()))
        persons[split] = {r["person_id"] for r in rows}
    if persons["train"] & persons["val"] or persons["train"] & persons["test"] \
            or persons["val"] & persons["test"]:
        fail("a person_id occurs in more than one split", log, log_path)
    all_rows = read_index(ROOT, a.size, ("train", "val", "test"), ("C0", "C1", "C2", "C3", "C4"))
    if len(all_rows) != 10800:
        fail(f"expected 10,800 images across all splits, found {len(all_rows)}", log, log_path)

    train_ds = make_dataset(ROOT, a.size, ("train",), PRIMARY)
    val_ds = make_dataset(ROOT, a.size, ("val",), PRIMARY)

    # RGB order and normalisation: undo the normalisation and compare to the raw PIL pixels.
    for ds in (train_ds, val_ds):
        for i in (0, len(ds) // 2, len(ds) - 1):
            raw = ds.load_rgb(i).astype(np.float32) / 255.0
            x, y, _ = ds[i]
            if tuple(x.shape) != (3, H, W) or x.dtype != torch.float32:
                fail(f"tensor shape/dtype {tuple(x.shape)}/{x.dtype}, expected (3,{H},{W})/float32",
                     log, log_path)
            back = (x * torch.tensor(IMAGENET_STD).view(3, 1, 1)
                    + torch.tensor(IMAGENET_MEAN).view(3, 1, 1)).permute(1, 2, 0).numpy()
            err = float(np.abs(back - raw).max())
            if err > 1e-5:
                fail(f"normalisation/channel-order check failed (max error {err})", log, log_path)
            if float(y) not in (0.0, 1.0):
                fail(f"label {float(y)} is not 0/1", log, log_path)

    loader = torch.utils.data.DataLoader(train_ds, batch_size=8, shuffle=False,
                                         num_workers=a.workers)
    xb, yb, ids = next(iter(loader))
    if len(set(ids)) != len(ids):
        fail("duplicate image_id inside one batch", log, log_path)
    pos_frac = {s: round(c.get("C1", 0) / sum(c.values()), 4) for s, c in counts.items()}
    log["stages"]["B_loader"] = {"counts_C0_C1": counts, "c1_fraction": pos_frac,
                                 "persons": {s: len(v) for s, v in persons.items()},
                                 "train_len": len(train_ds), "val_len": len(val_ds),
                                 "batch_shape": list(xb.shape),
                                 "test_images_loaded": 0}
    print("[B] loader: PASS", json.dumps(log["stages"]["B_loader"]))
    if a.loader_only:
        log["result"] = "PASS (loader only)"
        log_path.write_text(json.dumps(log, indent=2), encoding="utf-8")
        print(f"\nPASS (loader only). Log: {log_path}")
        return

    dev = torch.device("cuda")
    loss_fn = torch.nn.BCEWithLogitsLoss()

    # ---- C. batch-size probe (memory only, never accuracy) ----------------
    chosen, probe = None, {}
    for bs in BATCH_CANDIDATES:
        model = opt = scaler = x = y = None
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()
        try:
            model = build_model(a.weights).to(dev).train()
            opt = torch.optim.AdamW(model.parameters(), lr=a.lr)
            scaler = torch.amp.GradScaler("cuda")
            x = torch.randn(bs, 3, H, W, device=dev)
            y = torch.randint(0, 2, (bs,), device=dev).float()
            train_step(model, opt, scaler, x, y, loss_fn)            # warm-up
            torch.cuda.synchronize()
            t0 = time.time()
            for _ in range(3):
                train_step(model, opt, scaler, x, y, loss_fn)
            torch.cuda.synchronize()
            sec_per_step = (time.time() - t0) / 3
            probe[bs] = {"fits": True,
                         "peak_gb": round(torch.cuda.max_memory_allocated() / 2**30, 2),
                         "sec_per_step": round(sec_per_step, 3)}
            chosen = bs
        except torch.cuda.OutOfMemoryError:
            probe[bs] = {"fits": False}
        finally:
            del model, opt, scaler, x, y
            torch.cuda.empty_cache()
        print(f"[C] batch {bs}: {probe[bs]}")
        if chosen is not None:
            break
    if chosen is None:
        fail("batch size 8 does not fit in GPU memory at this size", log, log_path)
    n_train = len(train_ds)
    log["stages"]["C_batch_probe"] = {
        "probe": probe, "chosen_batch": chosen,
        "grad_accumulation": EFFECTIVE_BATCH // chosen,
        "est_sec_per_epoch_compute_only": round(probe[chosen]["sec_per_step"] * n_train / chosen, 1)}
    print("[C] chosen:", json.dumps(log["stages"]["C_batch_probe"]))

    # ---- D. one real batch --------------------------------------------------
    model = build_model(a.weights).to(dev).train()
    opt = torch.optim.AdamW(model.parameters(), lr=a.lr)
    scaler = torch.amp.GradScaler("cuda")
    loader = torch.utils.data.DataLoader(train_ds, batch_size=chosen, shuffle=True,
                                         num_workers=a.workers,
                                         generator=torch.Generator().manual_seed(a.seed))
    xb, yb, _ = next(iter(loader))
    loss = train_step(model, opt, scaler, xb.to(dev), yb.to(dev), loss_fn)
    grads_ok = all(torch.isfinite(p.grad).all() for p in model.parameters() if p.grad is not None)
    if not torch.isfinite(loss) or not grads_ok:
        fail(f"non-finite loss ({float(loss)}) or gradients on a real batch", log, log_path)
    log["stages"]["D_real_batch"] = {"loss": round(float(loss), 4), "grads_finite": True}
    print("[D] real batch: PASS", log["stages"]["D_real_batch"])
    del model, opt, scaler

    # ---- E. tiny overfit ------------------------------------------------------
    rng = random.Random(a.seed)
    c0 = [i for i, r in enumerate(train_ds.rows) if r["forgery_category"] == "C0"]
    c1 = [i for i, r in enumerate(train_ds.rows) if r["forgery_category"] == "C1"]
    subset_idx = sorted(rng.sample(c0, 25) + rng.sample(c1, 25))
    subset = torch.utils.data.Subset(train_ds, subset_idx)
    torch.manual_seed(a.seed)
    model = build_model(a.weights).to(dev).train()
    opt = torch.optim.AdamW(model.parameters(), lr=a.lr)
    scaler = torch.amp.GradScaler("cuda")
    loader = torch.utils.data.DataLoader(subset, batch_size=min(chosen, 16), shuffle=True,
                                         num_workers=a.workers,
                                         generator=torch.Generator().manual_seed(a.seed))
    history = []
    for epoch in range(1, a.overfit_epochs + 1):
        total, n = 0.0, 0
        for xb, yb, _ in loader:
            loss = train_step(model, opt, scaler, xb.to(dev), yb.to(dev), loss_fn)
            if not torch.isfinite(loss):
                fail(f"loss became non-finite at overfit epoch {epoch}", log, log_path)
            total += float(loss) * len(yb)
            n += len(yb)
        history.append(round(total / n, 4))
        if epoch == 1 or epoch % 5 == 0:
            print(f"[E] epoch {epoch:3d}  train loss {history[-1]:.4f}")

    model.eval()
    correct = 0
    with torch.no_grad():
        for xb, yb, _ in torch.utils.data.DataLoader(subset, batch_size=min(chosen, 16),
                                                     num_workers=a.workers):
            with torch.autocast(device_type="cuda", dtype=torch.float16):
                logits = model(xb.to(dev)).squeeze(1).float()
            correct += int(((logits > 0).float().cpu() == yb).sum())
    acc = correct / len(subset)
    log["stages"]["E_tiny_overfit"] = {
        "n_images": len(subset), "image_ids": [train_ds.rows[i]["image_id"] for i in subset_idx],
        "epochs": a.overfit_epochs, "lr": a.lr, "batch": min(chosen, 16),
        "loss_history": history, "eval_mode_accuracy": acc}
    print(f"[E] eval-mode accuracy on the 50 images: {acc:.3f}")
    if acc < 0.96:
        fail("tiny-overfit did not reach 96% accuracy. Check labels, normalisation, "
             "learning rate and the optimizer before any long run.", log, log_path)

    log["result"] = "PASS"
    log_path.write_text(json.dumps(log, indent=2), encoding="utf-8")
    print(f"\nPASS: all pre-training checks. Log: {log_path}")


if __name__ == "__main__":
    main()
