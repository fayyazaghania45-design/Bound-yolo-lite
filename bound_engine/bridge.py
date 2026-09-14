"""
bound_engine/bridge.py
Menyambungkan output vision_engine.detector.detect() ke BOUND DSL engine ASLI
(package `bound-dsl`, class BoundDSLParser + BoundInterpreter — sesuai kode
guardian_standalone.py & simulate_test.py dari proyek AGV arm).

CATATAN PENTING soal detections_to_context():
Struktur context di sini ("device" -> "vision" -> ...) DISAMAKAN dengan pola
yang sudah dipakai di guardian_standalone.py/simulate_test.py, supaya
konsisten. TAPI nama field persis di bawah "vision" (mis. "sudut_barang",
"barang_terdeteksi_di_gripper") itu spesifik buat rules/agv_arm.bound yang
LAMA -- belum tentu sama dengan field yang mau dibaca di contoh_agv_arm.bound
yang baru (untuk deteksi class YOLO). Field "class_name_terdeteksi" dan
"confidence_terdeteksi" di bawah masih PENAMAAN SEMENTARA -- perlu dicek ulang
begitu ada isi rules/agv_arm.bound (atau file .bound yang mau dipakai)
supaya nama field-nya cocok dengan yang dibaca WHEN.
"""

import os
import tempfile
from pathlib import Path
from typing import Any, Callable, Optional


def validate_bound_script(script_text: str) -> tuple[bool, str]:
    """
    Cek apakah kode .bound valid, dipanggil dari tombol "Validasi" di
    halaman BOUND Editor.

    BoundDSLParser butuh PATH ke file (lihat guardian_standalone.py:
    `BoundDSLParser(RULES_PATH)` lalu `.parse_file()`), bukan string
    langsung -- jadi di sini ditulis dulu ke file temporary.
    """
    tmp_path = None
    try:
        # Lazy import: app tetap bisa dibuka walau 'bound-dsl' belum ter-install,
        # error baru muncul di halaman ini pas divalidasi -- bukan bikin app
        # crash total pas start.
        from bound_dsl import BoundDSLParser

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".bound", delete=False, encoding="utf-8"
        ) as tmp:
            tmp.write(script_text)
            tmp_path = tmp.name

        parser = BoundDSLParser(tmp_path)
        parser.parse_file()
        return True, ""
    except ImportError:
        return False, "Package 'bound-dsl' belum ter-install di environment ini."
    except Exception as e:  # noqa: BLE001 - ditampilkan langsung ke user di UI
        return False, str(e)
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)


def detections_to_context(detections: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Ubah hasil detect() YOLO jadi context dict, mengikuti struktur
    "device" -> "vision" yang sudah dipakai di proyek AGV arm.

    TODO: konfirmasi ulang nama field di bawah "vision" begini setelah
    lihat isi rules/agv_arm.bound (atau .bound baru) yang sebenarnya --
    field di bawah ini masih tebakan penamaan, bukan hasil konfirmasi.
    """
    if not detections:
        return {"device": {"vision": {"objek_terdeteksi": False}}}

    best = max(detections, key=lambda d: d["confidence"])
    return {
        "device": {
            "vision": {
                "objek_terdeteksi": True,
                "class_name_terdeteksi": best["class_name"],
                "confidence_terdeteksi": best["confidence"],
                "bbox": best["bbox"],
            }
        }
    }


def run_rules_on_detection(
    bound_script_path: str,
    detections: list[dict[str, Any]],
    action_handlers: Optional[dict[str, Callable]] = None,
    publish_fn: Optional[Callable] = None,
) -> dict[str, Any]:
    """
    Jalankan file .bound ASLI terhadap hasil deteksi YOLO saat ini,
    pakai BoundDSLParser + BoundInterpreter yang sesungguhnya.

    action_handlers: dict {"NAMA_AKSI": handler(args, context, executor)} --
        didaftarkan ke interpreter sebelum dijalankan, sama seperti
        interpreter.register_action(...) di guardian_standalone.py.
        Kalau None, tidak ada aksi hardware yang terdaftar (dry run --
        rule tetap dievaluasi, tapi gak ada efek ke hardware).
    publish_fn: fungsi publish MQTT (topic, payload), dipakai kalau ada
        aksi yang manggil ex.publish_fn(...). Default: dry run, tidak
        publish kemana-mana.
    """
    from bound_dsl import BoundDSLParser, BoundInterpreter  # lazy import, lihat catatan di validate_bound_script()

    parser = BoundDSLParser(bound_script_path)
    parsed = parser.parse_file()

    def _default_publish(topic, payload):
        pass  # dry run -- tidak publish ke MQTT sungguhan

    interpreter = BoundInterpreter(publish_fn=publish_fn or _default_publish)

    for name, handler in (action_handlers or {}).items():
        interpreter.register_action(name, handler)

    context = detections_to_context(detections)
    fired = interpreter.run(parsed, context, stop_on_first_fire=True)

    return {
        "fired_rule": fired,
        "current_step": context.get("current_step"),
        "context": context,
    }