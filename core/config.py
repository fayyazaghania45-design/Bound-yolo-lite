"""
core/config.py
Semua path penyimpanan lokal aplikasi ada di sini.
Kalau nanti mau ganti lokasi penyimpanan (misal ke folder Documents),
cukup ubah BASE_DIR di file ini.
"""

import os
from pathlib import Path

# Folder utama tempat semua data aplikasi disimpan di laptop pengguna.
# Default: folder "storage" di sebelah main.py, biar portable (gampang di-zip/di-share).
BASE_DIR = Path(__file__).resolve().parent.parent / "storage"

MODELS_DIR = BASE_DIR / "models"          # hasil training YOLO (biasa & yang dipakai bareng BOUND)
DATASETS_DIR = BASE_DIR / "datasets"      # dataset gambar untuk training
BOUND_SCRIPTS_DIR = BASE_DIR / "bound_scripts"  # file .bound yang ditulis user

# Tiga profil training. App ini SATU untuk semua orang — bedanya cuma profil
# yang dipakai. Laptop pas-pasan -> "ringan". Laptop kencang/ada GPU -> boleh
# pilih "performa_tinggi" biar hasil model lebih akurat, bukan dibatasi terus.
TRAINING_PROFILES = {
    "ringan": {
        "label": "Ringan (laptop pas-pasan, tanpa GPU)",
        "model_base": "yolov8n.pt",
        "imgsz": 320,
        "batch": 4,
        "epochs": 50,
        "freeze_backbone_layers": 10,
        "workers": 2,
    },
    "seimbang": {
        "label": "Seimbang (laptop menengah)",
        "model_base": "yolov8s.pt",
        "imgsz": 480,
        "batch": 8,
        "epochs": 80,
        "freeze_backbone_layers": 5,
        "workers": 4,
    },
    "performa_tinggi": {
        "label": "Performa Tinggi (laptop kencang / ada GPU)",
        "model_base": "yolov8m.pt",
        "imgsz": 640,
        "batch": 16,
        "epochs": 100,
        "freeze_backbone_layers": 0,  # gak freeze sama sekali, training penuh
        "workers": 8,
    },
}

# Dipakai kalau user belum pilih profil manual sama sekali.
DEFAULT_PROFILE_KEY = "ringan"

# Dipertahankan biar training_page.py & trainer.py lama tetap kompatibel.
LIGHT_TRAINING_DEFAULTS = TRAINING_PROFILES[DEFAULT_PROFILE_KEY]


def detect_recommended_profile() -> str:
    """
    Deteksi kasar kemampuan laptop, buat SARAN profil ke user
    (bukan otomatis dipaksa pindah — user tetap yang pilih akhirnya).
    """
    try:
        import torch

        if torch.cuda.is_available():
            gpu_mem_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            if gpu_mem_gb >= 6:
                return "performa_tinggi"
            return "seimbang"
    except ImportError:
        pass

    try:
        import psutil

        ram_gb = psutil.virtual_memory().total / (1024**3)
        if ram_gb >= 16:
            return "seimbang"
    except ImportError:
        pass

    return "ringan"


def ensure_storage_dirs():
    """Pastikan semua folder penyimpanan ada. Dipanggil sekali saat app start."""
    for d in (MODELS_DIR, DATASETS_DIR, BOUND_SCRIPTS_DIR):
        os.makedirs(d, exist_ok=True)