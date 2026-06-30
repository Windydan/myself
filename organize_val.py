from pathlib import Path
import json
import shutil
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--val-dir", required=True, help="flat val directory")
    parser.add_argument("--val-txt", required=True, help="val.txt with filename and label")
    parser.add_argument("--class-index", required=True, help="imagenet_class_index.json")
    parser.add_argument("--move", action="store_true", help="move files instead of copy")
    args = parser.parse_args()

    val_dir = Path(args.val_dir).expanduser()
    val_txt = Path(args.val_txt).expanduser()
    class_index = Path(args.class_index).expanduser()

    if not val_dir.exists():
        raise FileNotFoundError(f"val dir not found: {val_dir}")
    if not val_txt.exists():
        raise FileNotFoundError(f"val.txt not found: {val_txt}")
    if not class_index.exists():
        raise FileNotFoundError(f"class index not found: {class_index}")

    with class_index.open("r", encoding="utf-8") as f:
        data = json.load(f)

    # json key: 0-based class id -> synset
    idx_to_synset = {}
    for k in sorted(data.keys(), key=int):
        synset, _ = data[k]
        idx_to_synset[int(k) + 1] = synset  # convert to 1-based label in val.txt

    records = []
    with val_txt.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            fname, label = line.split()
            records.append((fname, int(label)))

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


'''
python organize_imagenet_val.py \
  --val-dir ~/OOD/IIM-SMCM/data/ood/imagenet/val \
  --val-txt ~/OOD/NegPrompt/data/ImageNet1K/protocols/val.txt \
  --class-index ~/OOD/NegPrompt/data/ImageNet1K/protocols/imagenet_class_index.json \
  --move
'''