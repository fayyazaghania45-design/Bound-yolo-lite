"""
main.py
Entry point aplikasi BOUND x YOLO (lite).

Jalankan dengan:
    python main.py

Struktur navigasi: sidebar kiri -> ganti frame konten kanan.
Transisi antar halaman sengaja ringan (langsung swap frame), bukan animasi
berat, biar tetap lancar di laptop spek rendah — target utama aplikasi ini.
"""

import customtkinter as ctk

from core.config import ensure_storage_dirs
from ui.sidebar import Sidebar
from ui.dashboard_page import DashboardPage
from ui.training_page import TrainingPage
from ui.bound_docs_page import BoundDocsPage
from ui.bound_editor_page import BoundEditorPage
from ui.connectivity_page import ConnectivityPage

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("BOUND x YOLO — Lite")
        self.geometry("1000x680")
        self.minsize(820, 560)

        ensure_storage_dirs()

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = Sidebar(self, on_navigate=self.show_page)
        self.sidebar.grid(row=0, column=0, sticky="nsw")

        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.grid(row=0, column=1, sticky="nsew", padx=16, pady=16)

        # Registry halaman: lazy-loaded (dibuat pas pertama diakses),
        # biar startup app cepat walau nanti jumlah halaman bertambah.
        self._page_classes = {
            "dashboard": DashboardPage,
            "training": TrainingPage,
            "bound_docs": BoundDocsPage,
            "bound_editor": BoundEditorPage,
            "connectivity": ConnectivityPage,
        }
        self._page_instances = {}
        self._current_page_key = None

        self.show_page("dashboard")

    def show_page(self, key: str):
        if key == self._current_page_key:
            return

        for widget in self.content.winfo_children():
            widget.pack_forget()

        if key not in self._page_instances:
            page_class = self._page_classes[key]
            self._page_instances[key] = page_class(self.content)

        self._page_instances[key].pack(fill="both", expand=True)
        self.sidebar.set_active(key)
        self._current_page_key = key


if __name__ == "__main__":
    app = App()
    app.mainloop()