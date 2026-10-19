"""Roadmap Step 12: recovery analysis — which images each branch catches.

For every image, joins the frozen visual decision with the rule decision (GT text
and OCR text) and counts: both, visual only, rules only, neither. Reported by
document type x category (C0 = false positives) and, for C1, by edit group.

Reads the prediction files written by experiments/score_frozen.py, so it can only
run on a split that has been scored:
    python experiments/rules/recovery.py --split val     # now
    python experiments/rules/recovery.py --split test    # after Step 15
Writes experiments/results/<split>/recovery.md and recovery.csv.
"""
import argparse
import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FINE = {"local_recompression", "resample_patch"}
OUTCOMES = ("both", "visual_only", "rules_only", "neither")


def read(path):
    with path.open(newline="", encoding="utf-8") as f:
        return {r["image_id"]: int(r["decision"]) for r in csv.DictReader(f)}


def outcome(v, r):
    return OUTCOMES[0] if v and r else OUTCOMES[1] if v else OUTCOMES[2] if r else OUTCOMES[3]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", required=True, choices=["val", "test"])
    a = ap.parse_args()
    res = ROOT / "experiments" / "results" / a.split
    if not (res / "visual_predictions.csv").is_file():
        raise SystemExit(f"STOP: {res} has no predictions; run score_frozen.py --split {a.split} first.")
    with (ROOT / "dataset" / "data" / "v1" / "manifest.csv").open(newline="", encoding="utf-8-sig") as f:
        man = {r["image_id"]: r for r in csv.DictReader(f) if r["split"] == a.split}
    vis = read(res / "visual_predictions.csv")
    if set(vis) != set(man):
        raise SystemExit("STOP: visual predictions do not cover the split exactly.")

    rows, lines = [], [f"# Recovery analysis ({a.split} split)", "",
                       "Counts of images by which branch flags them. Visual = frozen `tiles` ensemble at t_v. "
                       "On C0 every flag is a false positive.", ""]
    for cond in ("GT", "OCR"):
        rules = read(res / f"rules_{cond}_predictions.csv")
        groups = {}
        for i, m in man.items():
            keys = [(m["doc_type"], m["forgery_category"])]
            if m["forgery_category"] == "C1":
                keys.append((m["doc_type"], "C1-fine" if m["c1_op"] in FINE else "C1-coarse"))
            for k in keys:
                groups.setdefault(k, Counter())[outcome(vis[i], rules[i])] += 1
        lines += [f"## Rules on {cond} text", "",
                  "| Document | Group | n | Both | Visual only | Rules only | Neither |",
                  "|---|---|---|---|---|---|---|"]
        order = ["C0", "C1", "C1-fine", "C1-coarse", "C2", "C3", "C4"]
        for doc in ("aadhaar", "pan"):
            for g in order:
                c = groups[(doc, g)]
                n = sum(c.values())
                rows.append({"split": a.split, "text": cond, "doc_type": doc, "group": g, "n": n,
                             **{o: c[o] for o in OUTCOMES}})
                lines.append(f"| {doc} | {g} | {n} | " + " | ".join(str(c[o]) for o in OUTCOMES) + " |")
        lines.append("")
    with (res / "recovery.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    (res / "recovery.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
