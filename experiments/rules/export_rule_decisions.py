"""Roadmap Step 12 (rule side): export rule decisions with the failing checks for all
10,800 images, and compute mechanism-aware recall (DECISIONS.md Section 6).

Source: dataset/data/v1/manifest.jsonl (tracked since the freeze commit 976eade).
It must agree with the tracked manifest.csv on every shared field, or the script stops.

Checks the validators report (the strict PAN variant is a sensitivity analysis
and is not part of the primary rule):
  Aadhaar: format_check, checksum_check
  PAN:     format_check, category_check, semantic_check

Mechanism-aware detection (Section 6):
  eligible = expected_rule == FAIL  (Aadhaar C2, PAN C2, PAN C3)
  match    = Aadhaar C2: format_check or checksum_check failed
             PAN C2:     format_check or category_check failed
             PAN C3:     semantic_check failed
  A flagged eligible image whose failing checks do not include the matching one
  is counted as over-attribution. Aadhaar C3 is reported separately as an
  expected miss.

    python experiments/rules/export_rule_decisions.py
Writes experiments/rules/rule_decisions.csv and mechanism_aware_recall.md/.json.
"""
import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
JSONL = ROOT / "dataset" / "data" / "v1" / "manifest.jsonl"
CSV = ROOT / "dataset" / "data" / "v1" / "manifest.csv"
OUT = ROOT / "experiments" / "rules"
CHECKS = {"aadhaar": ("format_check", "checksum_check"),
          "pan": ("format_check", "category_check", "semantic_check")}
MATCH = {("aadhaar", "C2"): {"format_check", "checksum_check"},
         ("pan", "C2"): {"format_check", "category_check"},
         ("pan", "C3"): {"semantic_check"}}
SHARED = ("split", "doc_type", "forgery_category", "label", "expected_rule",
          "rule_gt_verdict", "rule_ocr_verdict", "person_id", "quality_tier")


def wilson(k, n, z=1.959963985):
    if n == 0:
        return None
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(100 * (c - h), 1), round(100 * (c + h), 1)]


def failed(detail, doc):
    return sorted(c for c in CHECKS[doc] if detail.get(c) == "FAIL")


def main():
    raw = JSONL.read_bytes()
    rows = [json.loads(l) for l in raw.decode("utf-8").splitlines()]
    with CSV.open(newline="", encoding="utf-8-sig") as f:
        man = {r["image_id"]: r for r in csv.DictReader(f)}
    if len(rows) != 10800 or {r["image_id"] for r in rows} != set(man):
        raise SystemExit("STOP: manifest.jsonl and manifest.csv cover different images")
    for r in rows:
        m = man[r["image_id"]]
        for k in SHARED:
            if str(r[k]) != m[k]:
                raise SystemExit(f"STOP: {r['image_id']} {k}: jsonl={r[k]} csv={m[k]}")
        for cond in ("gt", "ocr"):
            fc = failed(r[f"rule_{cond}_detail"], r["doc_type"])
            if bool(fc) != (r[f"rule_{cond}_verdict"] == "FAIL"):
                raise SystemExit(f"STOP: {r['image_id']}: {cond} verdict disagrees with its checks")

    OUT.mkdir(parents=True, exist_ok=True)
    out_rows, cells = [], defaultdict(lambda: defaultdict(int))
    for r in sorted(rows, key=lambda x: x["image_id"]):
        key = (r["doc_type"], r["forgery_category"])
        eligible = r["expected_rule"] == "FAIL"
        row = {k: r[k] for k in ("image_id", "split", "doc_type", "forgery_category", "label",
                                 "quality_tier", "expected_rule", "forgery_field")}
        row["forgery_field"] = row["forgery_field"] or ""
        row["eligible"] = int(eligible)
        for cond in ("gt", "ocr"):
            fc = failed(r[f"rule_{cond}_detail"], r["doc_type"])
            flag = int(bool(fc))
            match = int(eligible and bool(set(fc) & MATCH.get(key, set())))
            row[f"{cond}_decision"] = flag
            row[f"{cond}_failed_checks"] = "|".join(fc)
            row[f"{cond}_mechanism_match"] = match
            row[f"{cond}_reason"] = r[f"rule_{cond}_detail"].get("reason", "")
            c = cells[(r["split"], cond, *key)]
            c["n"] += 1
            c["flagged"] += flag
            c["match"] += match
            c["over"] += int(eligible and flag and not match)
        out_rows.append(row)

    with (OUT / "rule_decisions.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out_rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(out_rows)

    # Hash with LF line endings so Windows (CRLF) and Linux checkouts give the same value.
    summary = {"manifest_jsonl_sha256_lf": hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest(),
               "cells": {}}
    lines = ["# Mechanism-aware recall (rule branch)", "",
             "Eligible images are those the rules are designed to catch. *Flagged* counts any FAIL; "
             "*mechanism-aware* counts a FAIL from the check tied to the corrupted field; "
             "*over-attribution* counts a FAIL from a different check only. 95% Wilson intervals.", ""]
    for split in ("test", "val", "train"):
        lines += [f"## {split} split", "",
                  "| Text | Cell | n | Flagged % | Mechanism-aware % [95% CI] | Over-attribution n |",
                  "|---|---|---|---|---|---|"]
        for cond in ("gt", "ocr"):
            for key in (("aadhaar", "C2"), ("pan", "C2"), ("pan", "C3"), ("aadhaar", "C3")):
                c = cells[(split, cond, *key)]
                n = c["n"]
                rec = {"n": n, "flagged": c["flagged"], "mechanism_aware": c["match"],
                       "over_attribution": c["over"],
                       "mechanism_aware_recall": round(c["match"] / n, 4) if n else None,
                       "ci95": wilson(c["match"], n)}
                summary["cells"][f"{split}/{cond}/{key[0]}/{key[1]}"] = rec
                note = " (expected miss)" if key == ("aadhaar", "C3") else ""
                lines.append(f"| {cond.upper()} | {key[0]} {key[1]}{note} | {n} | "
                             f"{100 * c['flagged'] / n:.1f} | {100 * c['match'] / n:.1f} {wilson(c['match'], n)} | "
                             f"{c['over']} |")
        lines.append("")
    (OUT / "mechanism_aware_recall.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (OUT / "mechanism_aware_recall.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    print(f"PASS: wrote {len(out_rows)} rows to experiments/rules/rule_decisions.csv")


if __name__ == "__main__":
    main()
