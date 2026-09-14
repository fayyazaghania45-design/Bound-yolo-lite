"""
vision_engine/dataset_utils.py
Cek struktur dataset sebelum training, biar error "dataset salah format"
ketahuan dari awal (di UI), bukan di tengah proses training yang lama.

Struktur dataset yang diharapkan (format standar Ultralytics YOLO):

    dataset_name/
        images/
            train/
            val/
        labels/
            train/
            val/
        data.yaml
"""

from pathlib import Path


def validate_dataset_structure(dataset_dir: str) -> tuple[bool, list[str]]:
    """
    Return (valid: bool, masalah: list[str])
    Dipanggil sebelum tombol "Mulai Training" aktif di UI.
    """
    dataset_dir = Path(dataset_dir)
    problems = []

    required = [
        "images/train",
        "images/val",
        "labels/train",
        "labels/val",
        "data.yaml",
    ]

    for rel_path in required:
        if not (dataset_dir / rel_path).exists():
            problems.append(f"Tidak ditemukan: {rel_path}")

    train_images = list((dataset_dir / "images/train").glob("*")) if (dataset_dir / "images/train").exists() else []
    if len(train_images) == 0:
        problems.append("Folder images/train kosong — belum ada data training.")

    return (len(problems) == 0, problems)


def list_classes_from_yaml(data_yaml_path: str) -> list[str]:
    """Baca daftar nama class dari data.yaml (dipakai untuk ditampilkan di UI)."""
    import yaml

    with open(data_yaml_path, "r") as f:
        data = yaml.safe_load(f)
    return data.get("names", [])