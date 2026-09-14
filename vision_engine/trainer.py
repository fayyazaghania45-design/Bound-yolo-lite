"""
vision_engine/trainer.py
Wrapper training YOLO yang didesain untuk laptop spek rendah:
- pakai YOLOv8n (nano)
- resolusi & batch kecil
- freeze sebagian backbone (transfer learning, bukan training dari nol)
- export ke ONNX setelah training biar inference-nya juga ringan

Catatan: fungsi di sini SENGAJA dipisah dari UI, biar bisa dites sendiri
lewat terminal sebelum disambungkan ke tombol "Mulai Training" di dashboard.

TODO (tahap isi logika):
- [ ] tes training_dry_run() dulu pakai dataset kecil (2-3 class, <50 gambar)
- [ ] pastikan callback progress kepanggil tiap epoch buat progress bar UI
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional

from core.config import MODELS_DIR, TRAINING_PROFILES, DEFAULT_PROFILE_KEY


def train_model(
    dataset_yaml_path: str,
    profile_key: str = DEFAULT_PROFILE_KEY,
    run_name: Optional[str] = None,
    progress_callback: Optional[Callable[[int, int], None]] = None,
) -> str:
    """
    Melatih model YOLO sesuai profil yang dipilih user.

    profile_key: salah satu dari core.config.TRAINING_PROFILES
                 ("ringan" / "seimbang" / "performa_tinggi")
    dataset_yaml_path: path ke file data.yaml (format standar Ultralytics:
                        train/val path + daftar nama class)
    progress_callback: dipanggil sebagai progress_callback(epoch_ke, total_epoch),
                        supaya UI bisa update progress bar tanpa nge-block UI thread.

    Return: path folder hasil training (berisi best.pt, dsb).
    """
    # Import di dalam fungsi (lazy import) supaya app tetap bisa dibuka
    # walau ultralytics belum ter-install (misal saat baru scaffold seperti sekarang).
    from ultralytics import YOLO

    profile = TRAINING_PROFILES[profile_key]
    epochs = profile["epochs"]
    imgsz = profile["imgsz"]
    batch = profile["batch"]
    freeze_backbone_layers = profile["freeze_backbone_layers"]

    run_name = run_name or f"{profile_key}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    save_dir = Path(MODELS_DIR) / run_name
    os.makedirs(save_dir, exist_ok=True)

    model = YOLO(profile["model_base"])

    # Freeze layer awal backbone -> fine-tune lebih cepat & lebih hemat memori
    # dibanding training semua layer dari nol. Profil "performa_tinggi" pakai
    # freeze_backbone_layers=0, artinya training penuh tanpa freeze.
    freeze_layers = [f"model.{i}." for i in range(freeze_backbone_layers)]

    # NOTE: callback progress Ultralytics disambungkan lewat 'on_train_epoch_end'.
    # Ini placeholder aman: kalau progress_callback None, training tetap jalan tanpa error.
    def _on_epoch_end(trainer):
        if progress_callback:
            progress_callback(trainer.epoch + 1, epochs)

    if progress_callback:
        model.add_callback("on_train_epoch_end", _on_epoch_end)

    model.train(
        data=dataset_yaml_path,
        epochs=epochs,
        imgsz=imgsz,
        batch=batch,
        freeze=freeze_layers,
        workers=profile["workers"],
        project=str(MODELS_DIR),
        name=run_name,
        exist_ok=True,
        # Augmentasi berat & cache RAM cuma dimatikan di profil "ringan" —
        # profil performa tinggi boleh pakai augmentasi penuh buat akurasi lebih baik.
        mosaic=0.0 if profile_key == "ringan" else 1.0,
        cache=False if profile_key == "ringan" else True,
    )

    best_pt = save_dir / "weights" / "best.pt"

    # Export ke ONNX supaya inference nanti ringan & cepat di CPU low-end.
    if best_pt.exists():
        model_trained = YOLO(str(best_pt))
        model_trained.export(format="onnx", imgsz=imgsz)

    return str(save_dir)


def list_saved_models() -> list[str]:
    """Daftar semua hasil training yang tersimpan lokal (untuk halaman Training Manager)."""
    if not Path(MODELS_DIR).exists():
        return []
    return sorted(
        [d.name for d in Path(MODELS_DIR).iterdir() if d.is_dir()],
        reverse=True,
    )