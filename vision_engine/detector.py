"""
vision_engine/detector.py
Load model hasil training (prioritas ONNX biar ringan di CPU) dan jalankan deteksi.
Dipakai baik di mode "YOLO biasa" maupun mode "YOLO + BOUND"
(bedanya cuma di mode BOUND, hasil detect() ini diteruskan ke bound_engine).
"""

from pathlib import Path
from typing import Any, Optional


def load_model(model_path: str):
    """
    model_path: path ke best.onnx (disarankan) atau best.pt
    ONNX lebih disarankan untuk inference di laptop tanpa GPU yang kuat.
    """
    from ultralytics import YOLO

    if not Path(model_path).exists():
        raise FileNotFoundError(f"Model tidak ditemukan: {model_path}")
    return YOLO(model_path)


def detect(model, frame) -> list[dict[str, Any]]:
    """
    Jalankan deteksi pada satu frame (numpy array dari OpenCV, BGR).

    Return: list of dict, tiap dict:
        {
            "class_name": str,
            "confidence": float,
            "bbox": (x1, y1, x2, y2),
        }
    Format ini yang nanti dibaca oleh bound_engine.bridge sebagai variabel
    di ekspresi WHEN pada file .bound (contoh: WHEN class_name == "kotak_merah").
    """
    results = model.predict(frame, verbose=False)
    detections = []
    for r in results:
        for box in r.boxes:
            cls_id = int(box.cls[0])
            detections.append(
                {
                    "class_name": model.names[cls_id],
                    "confidence": float(box.conf[0]),
                    "bbox": tuple(box.xyxy[0].tolist()),
                }
            )
    return detections


def run_webcam_preview(model, camera_index: int = 0, window_title: str = "Tes Deteksi (tekan Q untuk keluar)",
                        stop_flag: Optional[dict] = None):
    """
    Buka webcam, jalankan deteksi live, gambar kotak + label di tiap frame,
    tampilkan di jendela terpisah (native OpenCV window, bukan bagian dari
    jendela customtkinter). Dipanggil dari tombol "🎥 Tes pakai Kamera"
    di Training Manager.

    Dijalankan di THREAD TERPISAH dari UI utama (dipanggil lewat
    threading.Thread di training_page.py), supaya app utama gak freeze
    selama jendela kamera terbuka.

    stop_flag: dict {"stop": False} -- kalau nilainya diubah jadi True dari
    luar (misal user klik tombol "Stop" di UI), loop ini berhenti juga,
    selain lewat tombol Q / menutup jendela kamera.
    """
    import cv2

    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        raise RuntimeError(
            f"Tidak bisa buka kamera index {camera_index}. "
            "Pastikan kamera tidak sedang dipakai aplikasi lain."
        )

    try:
        while True:
            if stop_flag is not None and stop_flag.get("stop"):
                break

            ok, frame = cap.read()
            if not ok:
                break

            detections = detect(model, frame)
            for d in detections:
                x1, y1, x2, y2 = [int(v) for v in d["bbox"]]
                label = f"{d['class_name']} {d['confidence']:.2f}"
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, label, (x1, max(y1 - 8, 0)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            cv2.imshow(window_title, frame)

            # tekan 'q' di jendela kamera buat keluar, atau tutup jendelanya langsung
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
            if cv2.getWindowProperty(window_title, cv2.WND_PROP_VISIBLE) < 1:
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()