"""Amendment A6 (DECISIONS.md Section 20): score the fresh set with the five frozen
`tiles` checkpoints. GPU laptop only (needs the checkpoints and the images).

    python experiments/fresh/score_fresh_visual.py --corpus dataset/data/fresh_20261021

For each seed it first re-scores the first 40 v1 test images, in the same order and
batches as at training time, and stops unless the document logits reproduce the
committed scores_test.csv. This proves that the checkpoint and the preprocessing
are the frozen ones. It then scores every fresh image exactly as train_tiles.py
scored v1 (fp16 autocast, 15 tiles, document score = max tile logit).

Writes experiments/fresh/visual/tiles_seed<k>.csv and experiments/fresh/visual/summary.json.
"""
import argparse
import csv
import hashlib
import json
import platform
import sys
from pathlib import Path

import torch
import torchvision

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments" / "e2_visual"))
from tiles import CANVAS_H, CANVAS_W, GRID, TILE, TileImageSet  # noqa: E402
from train_tiles import build_model, score_images, write_scores  # noqa: E402

RUNS = ROOT / "experiments" / "e2_visual" / "runs" / "native_tiles"
V1 = ROOT / "dataset" / "data" / "v1"
OUT = ROOT / "experiments" / "fresh" / "visual"
N_CHECK, TOL = 40, 0.01


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


class CorpusTiles(TileImageSet):
    """TileImageSet reading images of an arbitrary corpus folder (v1 or fresh)."""

    def __init__(self, corpus, rows):
        super().__init__(ROOT, rows)
        self.corpus = Path(corpus)
        with (self.corpus / "manifest.csv").open(newline="", encoding="utf-8-sig") as f:
            self.files = {r["image_id"]: r["file"].replace("\\", "/") for r in csv.DictReader(f)}

    def canvas(self, i):
        import numpy as np
        from PIL import Image
        path = self.corpus / self.files[self.rows[i]["image_id"]]
        with Image.open(path) as im:
            im = im.convert("RGB")
            w, h = im.size
            if w > CANVAS_W or h > CANVAS_H:
                raise ValueError(f"{path}: {w}x{h} exceeds the {CANVAS_W}x{CANVAS_H} canvas")
            c = Image.new("RGB", (CANVAS_W, CANVAS_H), (255, 255, 255))
            c.paste(im, (0, 0))
        return np.asarray(c, dtype=np.uint8)


def manifest_rows(corpus, split=None):
    with (Path(corpus) / "manifest.csv").open(newline="", encoding="utf-8-sig") as f:
        rows = [r for r in csv.DictReader(f) if split is None or r["split"] == split]
    return sorted(rows, key=lambda r: r["image_id"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", required=True)
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    corpus = (ROOT / a.corpus).resolve() if not Path(a.corpus).is_absolute() else Path(a.corpus)
    if corpus == V1.resolve():
        sys.exit("STOP: --corpus is the v1 corpus.")
    if not torch.cuda.is_available():
        sys.exit("STOP: CUDA is not available.")
    if (OUT / "summary.json").exists():
        sys.exit(f"STOP: {OUT} already holds scores. The fresh set is scored once.")
    OUT.mkdir(parents=True, exist_ok=True)
    dev = torch.device("cuda")

    fresh_rows = manifest_rows(corpus)
    for r in fresh_rows:
        if not (corpus / r["file"].replace("\\", "/")).is_file():
            sys.exit(f"STOP: missing image {r['file']}")
    check_rows = manifest_rows(V1, "test")[:N_CHECK]

    summary = {"corpus": corpus.relative_to(ROOT).as_posix() if corpus.is_relative_to(ROOT) else str(corpus),
               "n_images": len(fresh_rows), "tile": TILE, "n_tiles": len(GRID), "seeds": {},
               "env": dict(python=platform.python_version(), platform=platform.platform(),
                           torch=torch.__version__, torchvision=torchvision.__version__,
                           cuda=torch.version.cuda, gpu=torch.cuda.get_device_properties(0).name)}
    for seed in range(5):
        run = RUNS / f"seed{seed}"
        ckpt = run / "best.pt"
        if not ckpt.is_file():
            sys.exit(f"STOP: {ckpt} not found.")
        model = build_model()
        model.load_state_dict(torch.load(ckpt, map_location=dev, weights_only=True))
        model.to(dev)

        with (run / "scores_test.csv").open(newline="", encoding="utf-8") as f:
            committed = {r["image_id"]: float(r["logit"]) for r in csv.DictReader(f)}
        ids, tl, _ = score_images(model, CorpusTiles(V1, check_rows), a.workers, dev)
        diff = max(abs(float(z.max()) - committed[i]) for i, z in zip(ids, tl))
        print(f"seed {seed}: v1 self-check on {len(ids)} test images, max |logit diff| = {diff:.5f}")
        if diff > TOL:
            sys.exit(f"STOP: seed {seed} does not reproduce its committed v1 test logits "
                     f"(max diff {diff:.4f} > {TOL}). Do not continue; report this.")

        ids, tl, _ = score_images(model, CorpusTiles(corpus, fresh_rows), a.workers, dev)
        if sorted(ids) != [r["image_id"] for r in fresh_rows]:
            sys.exit("STOP: scored images do not match the fresh manifest.")
        path = OUT / f"tiles_seed{seed}.csv"
        summary["seeds"][str(seed)] = {"checkpoint_sha256": sha(ckpt), "self_check_max_diff": diff,
                                       "scores_sha256": write_scores(path, fresh_rows, ids, tl)}
        print(f"seed {seed}: scored {len(ids)} fresh images -> {path.relative_to(ROOT)}")
        del model
        torch.cuda.empty_cache()

    (OUT / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print("PASS: all five seeds reproduced v1 and scored the fresh set. Commit experiments/fresh/visual/.")


if __name__ == "__main__":
    main()
