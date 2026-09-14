"""
tools/test_detection.py
Skrip kecil buat tes model hasil training bisa beneran deteksi objek,
sebelum dipakai lewat aplikasi. Belum ada tombol UI buat ini di app,
jadi dijalankan manual lewat terminal dulu.

CARA PAKAI:
    python tools/test_detection.py --model storage/models/NAMA_MODEL/weights/best.onnx --image path/ke/foto_tes.jpg
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from vision_engine.detector import load_model, detect


def main():
    parser = argparse.ArgumentParser(description="Tes deteksi pakai model hasil training.")
    parser.add_argument("--model", required=True, help="Path ke file best.onnx atau best.pt")
    parser.add_argument("--image", required=True, help="Path ke foto yang mau dites")
    args = parser.parse_args()

    print(f"Load model dari: {args.model}")
    model = load_model(args.model)

    import cv2
    frame = cv2.imread(args.image)
    if frame is None:
        print(f"Gagal baca gambar: {args.image}")
        return

    print(f"Menjalankan deteksi pada: {args.image}")
    results = detect(model, frame)

    if not results:
        print("\nTidak ada objek terdeteksi.")
        return

    print(f"\n=== {len(results)} objek terdeteksi ===")
    for r in results:
        print(f"  - {r['class_name']} (confidence: {r['confidence']:.2f}) bbox={r['bbox']}")


if __name__ == "__main__":
    main()