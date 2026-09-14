"""
ui/bound_editor_page.py
Editor teks sederhana untuk menulis file .bound langsung dari dashboard.
Belum ada syntax highlighting canggih di versi awal ini (TODO fase lanjut) —
untuk sekarang fokus: bisa tulis, validasi grammar, simpan, dan pilih jadi
script aktif yang dipakai mode "YOLO + BOUND".
"""

import tkinter.filedialog as fd
from pathlib import Path

import customtkinter as ctk

from bound_engine import bridge
from core.config import BOUND_SCRIPTS_DIR
from core.state import app_state

PLACEHOLDER_SCRIPT = """\
# Tulis aturan BOUND kamu di sini.
# Contoh (sesuaikan dengan grammar asli BOUND kamu):
#
# WHEN class_name == "kotak_merah" AND confidence > 0.7
#     MOVE(10, 20)
#     GRAB()
"""


class BoundEditorPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.current_file_path = None

        ctk.CTkLabel(
            self, text="✍️ BOUND Editor", font=ctk.CTkFont(size=22, weight="bold")
        ).pack(anchor="w", padx=20, pady=(20, 10))

        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", padx=20)

        ctk.CTkButton(toolbar, text="Buka File .bound", command=self._open_file).pack(side="left", padx=(0, 8))
        ctk.CTkButton(toolbar, text="Simpan", command=self._save_file).pack(side="left", padx=(0, 8))
        ctk.CTkButton(toolbar, text="✅ Validasi", command=self._validate).pack(side="left", padx=(0, 8))
        ctk.CTkButton(toolbar, text="🔗 Jadikan Script Aktif", command=self._set_active).pack(side="left")

        self.textbox = ctk.CTkTextbox(self, font=ctk.CTkFont(family="Consolas", size=13))
        self.textbox.pack(fill="both", expand=True, padx=20, pady=16)
        self.textbox.insert("1.0", PLACEHOLDER_SCRIPT)

        self.status_label = ctk.CTkLabel(self, text="", text_color="gray70")
        self.status_label.pack(anchor="w", padx=20, pady=(0, 12))

    def _open_file(self):
        path = fd.askopenfilename(
            initialdir=str(BOUND_SCRIPTS_DIR), filetypes=[("BOUND script", "*.bound")]
        )
        if not path:
            return
        self.current_file_path = path
        self.textbox.delete("1.0", "end")
        self.textbox.insert("1.0", Path(path).read_text())
        self.status_label.configure(text=f"Membuka: {path}")

    def _save_file(self):
        if not self.current_file_path:
            path = fd.asksaveasfilename(
                initialdir=str(BOUND_SCRIPTS_DIR), defaultextension=".bound"
            )
            if not path:
                return
            self.current_file_path = path
        Path(self.current_file_path).write_text(self.textbox.get("1.0", "end"))
        self.status_label.configure(text=f"Tersimpan: {self.current_file_path}")

    def _validate(self):
        script_text = self.textbox.get("1.0", "end")
        valid, error = bridge.validate_bound_script(script_text)
        if valid:
            self.status_label.configure(text="✅ Valid.", text_color="#4CAF50")
        else:
            self.status_label.configure(text=f"❌ {error}", text_color="#E05555")

    def _set_active(self):
        if not self.current_file_path:
            self.status_label.configure(text="Simpan file dulu sebelum dijadikan script aktif.")
            return
        app_state.set_active_bound_script(self.current_file_path)
        self.status_label.configure(text="Script ini sekarang aktif untuk mode YOLO + BOUND.")