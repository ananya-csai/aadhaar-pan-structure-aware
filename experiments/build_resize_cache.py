"""Build an aspect-preserving, white-padded PNG resize cache of the frozen corpus.

    python experiments/build_resize_cache.py                       # 384x256 (sensitivity arm)
    python experiments/build_resize_cache.py --width 768 --height 512   # primary arm (Amendment A1)
"""
import argparse
import csv
from pathlib import Path

from PIL import Image, ImageOps

# Run this script from the repository root.
ROOT = Path.cwd()
DATASET_DIR = ROOT / "dataset" / "data" / "v1"
MANIFEST = DATASET_DIR / "manifest.csv"

# Set in main() from --width/--height. Defaults reproduce the committed 384x256 cache.
TARGET_WIDTH = 384
TARGET_HEIGHT = 256
CACHE_DIR = ROOT / "experiments" / "cache" / f"{TARGET_WIDTH}x{TARGET_HEIGHT}"
METADATA = CACHE_DIR / "cache_manifest.csv"
BACKGROUND = (255, 255, 255)


def resize_and_pad(source_path, output_path):
    """Preserve aspect ratio and center the image on a white canvas."""
    with Image.open(source_path) as opened:
        image = ImageOps.exif_transpose(opened).convert("RGB")

    original_width, original_height = image.size

    scale = min(
        TARGET_WIDTH / original_width,
        TARGET_HEIGHT / original_height,
    )

    new_width = max(1, round(original_width * scale))
    new_height = max(1, round(original_height * scale))

    image = image.resize(
        (new_width, new_height),
        Image.Resampling.LANCZOS,
    )

    canvas = Image.new(
        "RGB",
        (TARGET_WIDTH, TARGET_HEIGHT),
        BACKGROUND,
    )

    left = (TARGET_WIDTH - new_width) // 2
    top = (TARGET_HEIGHT - new_height) // 2

    canvas.paste(image, (left, top))
    canvas.save(output_path, format="PNG", optimize=False)

    return original_width, original_height, new_width, new_height


def main():
    global TARGET_WIDTH, TARGET_HEIGHT, CACHE_DIR, METADATA
    ap = argparse.ArgumentParser()
    ap.add_argument("--width", type=int, default=384)
    ap.add_argument("--height", type=int, default=256)
    args = ap.parse_args()
    TARGET_WIDTH, TARGET_HEIGHT = args.width, args.height
    CACHE_DIR = ROOT / "experiments" / "cache" / f"{TARGET_WIDTH}x{TARGET_HEIGHT}"
    METADATA = CACHE_DIR / "cache_manifest.csv"

    if not MANIFEST.is_file():
        raise FileNotFoundError(
            f"Manifest not found: {MANIFEST}\n"
            "Run this script from the repository root."
        )

    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    with MANIFEST.open("r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        required = {
            "image_id", "file", "split",
            "doc_type", "forgery_category", "label",
        }

        missing_columns = required - set(reader.fieldnames or [])
        if missing_columns:
            raise ValueError(
                f"Manifest is missing columns: {sorted(missing_columns)}"
            )

        rows = list(reader)

    if not rows:
        raise ValueError("The manifest contains no image records.")

    image_ids = [row["image_id"] for row in rows]
    if len(image_ids) != len(set(image_ids)):
        raise ValueError("Duplicate image_id values found in manifest.")

    metadata_rows = []
    errors = []

    for index, row in enumerate(rows, start=1):
        # Manifest paths are relative to dataset/data/v1 and use Windows
        # separators; normalise them so the script also runs on Linux/macOS.
        source_path = DATASET_DIR / Path(row["file"].replace("\\", "/"))
        output_path = CACHE_DIR / f"{row['image_id']}.png"

        try:
            if not source_path.is_file():
                raise FileNotFoundError(f"Source image missing: {source_path}")

            original_w, original_h, resized_w, resized_h = (
                resize_and_pad(source_path, output_path)
            )

            # Verify the cached image has exactly the target dimensions.
            with Image.open(output_path) as cached:
                if cached.size != (TARGET_WIDTH, TARGET_HEIGHT):
                    raise ValueError(
                        f"Incorrect cached dimensions: {cached.size}"
                    )
                if cached.mode != "RGB":
                    raise ValueError(f"Unexpected image mode: {cached.mode}")

            metadata_rows.append({
                "image_id": row["image_id"],
                "source_file": row["file"],
                "cached_file": output_path.relative_to(ROOT).as_posix(),
                "split": row["split"],
                "doc_type": row["doc_type"],
                "forgery_category": row["forgery_category"],
                "label": row["label"],
                "original_width": original_w,
                "original_height": original_h,
                "resized_width": resized_w,
                "resized_height": resized_h,
                "canvas_width": TARGET_WIDTH,
                "canvas_height": TARGET_HEIGHT,
            })

        except Exception as exc:
            errors.append(f"{row.get('image_id', '?')}: {exc}")

        if index % 500 == 0 or index == len(rows):
            print(f"Processed {index}/{len(rows)} manifest records")

    # Write metadata only after all images have been processed successfully.
    if errors:
        print(f"\nFAILED: {len(errors)} image(s) had errors.")
        for error in errors[:20]:
            print(" -", error)
        raise RuntimeError(
            "Cache incomplete. Fix the errors and rerun the script."
        )

    columns = [
        "image_id", "source_file", "cached_file", "split",
        "doc_type", "forgery_category", "label",
        "original_width", "original_height",
        "resized_width", "resized_height",
        "canvas_width", "canvas_height",
    ]

    with METADATA.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(metadata_rows)

    print("\nPASS: Resize cache created successfully.")
    print(f"Manifest records: {len(rows)}")
    print(f"Cached images:    {len(metadata_rows)}")
    print(f"Canvas:           {TARGET_WIDTH} x {TARGET_HEIGHT}")
    print(f"Image format:     PNG, RGB")
    print(f"Cache directory:  {CACHE_DIR}")
    print(f"Metadata file:    {METADATA}")


if __name__ == "__main__":
    main()
