"""
tools/prepare_dataset.py
Menyusun dataset mentah jadi struktur folder yang dibutuhkan Training Manager
(images/train, images/val, labels/train, labels/val, data.yaml).

STRUKTUR INPUT YANG DIHARAPKAN (flat, karena satu foto bisa berisi
LEBIH DARI SATU objek/class sekaligus):

    raw_dataset/
        images/
            foto1.jpg
            foto2.jpg
            ...
        labels/
            foto1.txt   <- hasil label dari labelImg (format YOLO)
            foto2.txt
            ...
        classes.txt     <- dibuat OTOMATIS oleh labelImg, satu nama class per baris

Nama class TIDAK lagi diambil dari nama folder (karena satu foto bisa
punya banyak class sekaligus) -- diambil dari classes.txt yang sudah
otomatis dibuat labelImg selama proses labeling, urutannya HARUS sama
dengan urutan index di file .txt label (baris ke-0 di classes.txt = class
index 0, dst).

Kalau foto belum ada file .txt pasangannya (belum di-label di labelImg),
foto itu otomatis DILEWATI (dilaporkan di akhir), bukan bikin error.

CARA PAKAI:
    python tools/prepare_dataset.py --raw raw_dataset --out dataset_saya

Setelah selesai, folder --out itu yang dipilih di Training Manager
lewat tombol "Pilih Folder Dataset".
"""

import argparse
import random
import shutil
from pathlib import Path

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}


def read_classes(raw_dir: Path) -> list[str]:
    classes_file = raw_dir / "classes.txt"
    if not classes_file.exists():
        raise FileNotFoundError(
            f"classes.txt tidak ditemukan di {raw_dir}. "
            "File ini otomatis dibuat labelImg selama proses labeling -- "
            "pastikan kamu sudah menyelesaikan minimal 1 label dulu."
        )
    lines = [line.strip() for line in classes_file.read_text(encoding="utf-8-sig").splitlines()]
    return [line for line in lines if line]


def prepare_dataset(raw_dir: str, out_dir: str, val_ratio: float = 0.2, seed: int = 42):
    raw_dir = Path(raw_dir)
    out_dir = Path(out_dir)

    class_names = read_classes(raw_dir)
    if not class_names:
        raise ValueError(f"classes.txt di {raw_dir} kosong.")

    images_dir = raw_dir / "images"
    labels_dir = raw_dir / "labels"

    for sub in ["images/train", "images/val", "labels/train", "labels/val"]:
        (out_dir / sub).mkdir(parents=True, exist_ok=True)

    random.seed(seed)

    all_images = [
        p for p in images_dir.rglob("*")
        if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
    ]
    random.shuffle(all_images)

    usable = []
    skipped_no_label = []
    for img_path in all_images:
        label_path = labels_dir / (img_path.stem + ".txt")
        if not label_path.exists():
            skipped_no_label.append(str(img_path))
            continue
        usable.append((img_path, label_path))

    n_val = max(1, int(len(usable) * val_ratio)) if usable else 0
    val_items = usable[:n_val]
    train_items = usable[n_val:]

    for split_name, items in (("train", train_items), ("val", val_items)):
        for img_path, label_path in items:
            shutil.copy(img_path, out_dir / "images" / split_name / img_path.name)
            shutil.copy(label_path, out_dir / "labels" / split_name / label_path.name)

    yaml_lines = ["train: images/train", "val: images/val", "names:"]
    for idx, name in enumerate(class_names):
        yaml_lines.append(f"  {idx}: {name}")
    (out_dir / "data.yaml").write_text("\n".join(yaml_lines) + "\n")

    print("\n=== Selesai ===")
    print(f"Class terdeteksi ({len(class_names)}): {', '.join(class_names)}")
    print(f"Total foto dipakai: {len(usable)} (train={len(train_items)}, val={len(val_items)})")

    if skipped_no_label:
        print(f"\n[DILEWATI] {len(skipped_no_label)} foto belum punya label .txt, contoh:")
        for path in skipped_no_label[:5]:
            print(f"    - {path}")
        if len(skipped_no_label) > 5:
            print(f"    ... dan {len(skipped_no_label) - 5} lainnya")

    print(f"\nDataset siap dipakai di: {out_dir}")
    print("Buka Training Manager di aplikasi, lalu pilih folder ini.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Susun dataset mentah jadi format YOLO siap training.")
    parser.add_argument("--raw", required=True, help="Folder dataset mentah (images/, labels/, classes.txt)")
    parser.add_argument("--out", required=True, help="Folder output dataset siap training")
    parser.add_argument("--val-ratio", type=float, default=0.2, help="Proporsi data validasi (default 0.2)")
    args = parser.parse_args()

    prepare_dataset(args.raw, args.out, val_ratio=args.val_ratio)