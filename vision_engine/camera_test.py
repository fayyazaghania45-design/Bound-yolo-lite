import cv2

from detector import load_model, detect


MODEL_PATH = r"D:\Bound_yolo_lite\storage\models\ringan_20260913_123318\weights\best.onnx"


def main():
    print("Memuat model YOLO...")

    model = load_model(MODEL_PATH)

    print("Model berhasil dimuat.")
    print("Membuka kamera...")

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Kamera tidak bisa dibuka.")
        return

    print("Kamera aktif.")
    print("Arahkan objek dataset ke kamera.")
    print("Tekan Q untuk keluar.")

    while True:
        ret, frame = cap.read()

        if not ret:
            print("Gagal membaca frame kamera.")
            break

        detections = detect(model, frame)

        for item in detections:
            x1, y1, x2, y2 = map(int, item["bbox"])

            class_name = item["class_name"]
            confidence = item["confidence"]

            label = f"{class_name} {confidence:.2f}"

            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                2,
            )

            cv2.putText(
                frame,
                label,
                (x1, max(y1 - 10, 20)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2,
            )

        cv2.imshow(
            "BOUND x YOLO - Camera Test",
            frame,
        )

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()