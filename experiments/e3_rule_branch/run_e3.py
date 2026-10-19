"""E3: rule-only branch on the TEST split, scored by experiments/evaluate.py (roadmap Step 5).

The rule branch has no learned parameters or thresholds, so scoring it on test
does not tune anything. Rule decisions are the frozen verdicts in the manifest:
    rule_gt_verdict  (ground-truth text)  and  rule_ocr_verdict  (OCR text).
Decision = 1 when the verdict is FAIL.

    python experiments/e3_rule_branch/run_e3.py
Writes predictions and reports to experiments/e3_rule_branch/results/.
"""
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments"))
import evaluate as E  # noqa: E402

OUT = ROOT / "experiments" / "e3_rule_branch" / "results"


def main():
    manifest = E.load_manifest()
    OUT.mkdir(parents=True, exist_ok=True)
    ids = sorted(i for i, r in manifest.items() if r["split"] == "test")
    for name, col in (("rules_gt", "rule_gt_verdict"), ("rules_ocr", "rule_ocr_verdict")):
        pred = OUT / f"{name}_test_predictions.csv"
        with pred.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f, lineterminator="\n")
            w.writerow(["image_id", "decision"])
            for i in ids:
                w.writerow([i, int(manifest[i][col] == "FAIL")])
        E.main(["--pred", str(pred), "--split", "test", "--name", name,
                "--out", str(OUT), "--bootstrap", "10000", "--seed", "0"])


if __name__ == "__main__":
    main()
