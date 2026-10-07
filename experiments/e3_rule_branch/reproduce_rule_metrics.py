import pandas as pd


MANIFEST = "dataset/data/v1/manifest.csv"


def calculate_metrics(df, verdict_column):
    actual_fail = df["expected_rule"] == "FAIL"
    predicted_fail = df[verdict_column] == "FAIL"

    tp = (actual_fail & predicted_fail).sum()
    tn = (~actual_fail & ~predicted_fail).sum()
    fp = (~actual_fail & predicted_fail).sum()
    fn = (actual_fail & ~predicted_fail).sum()

    precision = tp / (tp + fp) if (tp + fp) else 0
    recall = tp / (tp + fn) if (tp + fn) else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0
    fpr = fp / (fp + tn) if (fp + tn) else 0

    return {
        "n": len(df),
        "TP": tp,
        "TN": tn,
        "FP": fp,
        "FN": fn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "fpr": fpr,
    }


def print_metrics(label, results):
    print(f"\n{label}")
    print("-" * 60)
    print(f"N:         {results['n']}")
    print(f"TP:        {results['TP']}")
    print(f"TN:        {results['TN']}")
    print(f"FP:        {results['FP']}")
    print(f"FN:        {results['FN']}")
    print(f"Precision: {results['precision']:.4f}")
    print(f"Recall:    {results['recall']:.4f}")
    print(f"F1:        {results['f1']:.4f}")
    print(f"FPR:       {results['fpr']:.4f}")


def main():
    df = pd.read_csv(MANIFEST)
    test = df[df["split"] == "test"].copy()

    print(f"Test samples: {len(test)}")

    # Overall
    for name, column in [
        ("Ground-truth rules", "rule_gt_verdict"),
        ("OCR rules", "rule_ocr_verdict"),
    ]:
        print_metrics(name, calculate_metrics(test, column))

    # By document type
    print("\n\n===== BY DOCUMENT TYPE =====")

    for doc_type in sorted(test["doc_type"].unique()):
        subset = test[test["doc_type"] == doc_type]

        print(f"\n### {doc_type.upper()}")

        for name, column in [
            ("Ground-truth", "rule_gt_verdict"),
            ("OCR", "rule_ocr_verdict"),
        ]:
            print_metrics(name, calculate_metrics(subset, column))

    # By forgery category
    print("\n\n===== BY FORGERY CATEGORY =====")

    for category in sorted(test["forgery_category"].unique()):
        subset = test[test["forgery_category"] == category]

        print(f"\n### {category}")

        for name, column in [
            ("Ground-truth", "rule_gt_verdict"),
            ("OCR", "rule_ocr_verdict"),
        ]:
            print_metrics(name, calculate_metrics(subset, column))


if __name__ == "__main__":
    main()