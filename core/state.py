"""
core/state.py
Menyimpan status aplikasi yang dipakai bersama oleh semua halaman:
- mode aktif ("yolo_only" atau "yolo_bound")
- model YOLO yang sedang dipilih/aktif
- callback sederhana biar halaman lain otomatis update kalau state berubah
  (biar gak perlu library state-management berat, cukup observer pattern simple)
"""

from typing import Callable, Optional


class AppState:
    MODE_YOLO_ONLY = "yolo_only"
    MODE_YOLO_BOUND = "yolo_bound"

    def __init__(self):
        self.mode: str = self.MODE_YOLO_ONLY
        self.active_model_path: Optional[str] = None
        self.active_bound_script_path: Optional[str] = None
        self._listeners: list[Callable[[], None]] = []

    def on_change(self, callback: Callable[[], None]):
        """Halaman lain daftar di sini biar tahu kalau state berubah."""
        self._listeners.append(callback)

    def _notify(self):
        for cb in self._listeners:
            cb()

    def set_mode(self, mode: str):
        assert mode in (self.MODE_YOLO_ONLY, self.MODE_YOLO_BOUND)
        self.mode = mode
        self._notify()

    def set_active_model(self, model_path: str):
        self.active_model_path = model_path
        self._notify()

    def set_active_bound_script(self, script_path: str):
        self.active_bound_script_path = script_path
        self._notify()

    def is_bound_active(self) -> bool:
        return self.mode == self.MODE_YOLO_BOUND


# Satu instance global dipakai seluruh app (cukup untuk skala desktop app single-window)
app_state = AppState()