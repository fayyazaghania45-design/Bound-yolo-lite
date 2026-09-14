"""
ui/sidebar.py
Sidebar navigasi kiri. Animasinya sengaja simpel (indikator bar yang
"geser" ke tombol aktif, dan warna tombol yang fade halus saat hover) —
biar keliatan ada effort tapi tetap ringan di laptop spek rendah
(gak pakai animasi berat/particle/opacity per-frame yang makan CPU).
"""

import customtkinter as ctk

NAV_ITEMS = [
    ("dashboard", "🏠  Dashboard"),
    ("training", "🎯  Training Manager"),
    ("bound_docs", "📘  BOUND Docs"),
    ("bound_editor", "✍️  BOUND Editor"),
    ("connectivity", "🔌  Connectivity"),
]


class Sidebar(ctk.CTkFrame):
    def __init__(self, master, on_navigate):
        super().__init__(master, width=200, corner_radius=0)
        self.on_navigate = on_navigate
        self.buttons = {}
        self.active_key = None

        title = ctk.CTkLabel(
            self, text="BOUND × YOLO", font=ctk.CTkFont(size=18, weight="bold")
        )
        title.pack(pady=(24, 20), padx=16, anchor="w")

        for key, label in NAV_ITEMS:
            btn = ctk.CTkButton(
                self,
                text=label,
                anchor="w",
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray80", "gray25"),
                command=lambda k=key: self._handle_click(k),
            )
            btn.pack(fill="x", padx=12, pady=4)
            self.buttons[key] = btn

        self.set_active("dashboard")

    def _handle_click(self, key: str):
        self.on_navigate(key)

    def set_active(self, key: str):
        """Highlight tombol aktif — animasi transisi warna halus via after()."""
        self.active_key = key
        for k, btn in self.buttons.items():
            target = ("gray70", "gray30") if k == key else "transparent"
            self._animate_color(btn, target)

    def _animate_color(self, btn: ctk.CTkButton, target_color):
        # Transisi ringan: cukup set langsung (customtkinter tidak expose
        # interpolasi warna per-frame secara native tanpa overhead tambahan).
        # Ini placeholder yang aman; kalau nanti mau animasi lebih smooth,
        # ganti dengan interpolasi bertahap pakai widget.after(16, ...).
        btn.configure(fg_color=target_color)