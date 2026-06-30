from pathlib import Path
import argparse
import json
import shutil


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--val-dir", required=True, help="flat ImageNet val directory")
    parser.add_argument("--val-txt", required=True, help="mapping file: filename label")
    parser.add_argument("--class-index", required=True, help="imagenet_class_index.json")
    parser.add_argument("--out-dir", default="", help="organized output dir; defaults to val-dir")
    parser.add_argument("--move", action="store_true", help="move files instead of copy")
    args = parser.parse_args()

    val_dir = Path(args.val_dir).expanduser()
    val_txt = Path(args.val_txt).expanduser()
    class_index = Path(args.class_index).expanduser()
    out_dir = Path(args.out_dir).expanduser() if args.out_dir else val_dir

    if not val_dir.exists():
        raise FileNotFoundError(f"val dir not found: {val_dir}")
    if not val_txt.exists():
        raise FileNotFoundError(f"val.txt not found: {val_txt}")
    if not class_index.exists():
        raise FileNotFoundError(f"class index not found: {class_index}")

    with class_index.open("r", encoding="utf-8") as f:
        data = json.load(f)

    idx_to_synset = {int(k): v[0] for k, v in data.items()}

    records = []
    with val_txt.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            fname, label = line.split()
            records.append((fname, int(label)))

    op = shutil.move if args.move else shutil.copy2
    total = 0
    skipped = 0

    for fname, label in records:
        synset = idx_to_synset[label]
        src = val_dir / fname
        target_dir = out_dir / synset
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / fname

        if target.exists():
            skipped += 1
            continue

        if src.exists():
            op(str(src), str(target))
            total += 1
            continue

        raise FileNotFoundError(
            f"image not found: {src}. It may have already been organized; expected target: {target}"
        )

    print(f"Done. Organized {total} images into folders under {out_dir}; skipped {skipped} existing files.")


if __name__ == "__main__":
    main()