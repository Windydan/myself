from pathlib import Path
import json
import shutil
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--val-dir", required=True)
    parser.add_argument("--val-txt", required=True)
    parser.add_argument("--class-index", required=True)
    parser.add_argument("--move", action="store_true")
    args = parser.parse_args()

    val_dir = Path(args.val-dir).expanduser()
    val_txt = Path(args.val_txt).expanduser()
    class_index = Path(args.class_index).expanduser()

    with class_index.open("r", encoding="utf-8") as f:
        data = json.load(f)

    idx_to_synset_0 = {int(k): v[0] for k, v in data.items()}
    idx_to_synset_1 = {int(k) + 1: v[0] for k, v in data.items()}

    records = []
    with val_txt.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            fname, label = line.split()
            records.append((fname, int(label)))

    labels = [label for _, label in records]
    use_one_based = min(labels) == 1

    idx_to_synset = idx_to_synset_1 if use_one_based else idx_to_synset_0

    op = shutil.move if args.move else shutil.copy2

    for fname, label in records:
        src = val_dir / fname
        if not src.exists():
            raise FileNotFoundError(f"image not found: {src}")

        synset = idx_to_synset[label]
        target_dir = val_dir / synset
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / fname
        op(str(src), str(target))

    print(f"Done. Organized {len(records)} images into folders under {val_dir}")


if __name__ == "__main__":
    main()