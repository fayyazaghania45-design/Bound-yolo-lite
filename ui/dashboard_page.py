"""
ui/dashboard_page.py
Halaman pertama yang dilihat pengguna: pilih mode.
- Kartu "YOLO Biasa": training/pakai YOLO tanpa BOUND sama sekali
- Kartu "YOLO + BOUND": training YOLO lalu hasil deteksinya bisa
  disambungkan ke aturan yang ditulis di BOUND Editor
"""

import customtkinter as ctk

from core.state import app_state


class ModeCard(ctk.CTkFrame):
    """Kartu pilihan mode dengan efek hover ringan (border menyala saat disorot)."""

    def __init__(self, master, title, description, on_select, width=280, height=200):
        super().__init__(master, width=width, height=height, corner_radius=16,
                          border_width=2, border_color="gray30")
        self.on_select = on_select

        ctk.CTkLabel(
            self, text=title, font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(28, 8), padx=20)

        ctk.CTkLabel(
            self, text=description, font=ctk.CTkFont(size=13),
            wraplength=width - 40, justify="left", text_color="gray70",
        ).pack(pady=(0, 16), padx=20)

        ctk.CTkButton(self, text="Pilih mode ini", command=self.on_select).pack(pady=10)

        self.bind("<Enter>", lambda e: self.configure(border_color="#3B8ED0"))
        self.bind("<Leave>", lambda e: self.configure(border_color="gray30"))


class DashboardPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        ctk.CTkLabel(
            self, text="Mau mulai dari mana?",
            font=ctk.CTkFont(size=24, weight="bold"),
        ).pack(pady=(30, 10))

        ctk.CTkLabel(
            self,
            text="Kamu bisa belajar & training YOLO dulu tanpa BOUND,\n"
                 "atau langsung coba integrasi YOLO ke aturan BOUND.",
            text_color="gray70",
        ).pack(pady=(0, 30))

        cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        cards_frame.pack(pady=10)

        ModeCard(
            cards_frame,
            title="🎯 YOLO Biasa",
            description="Training & coba deteksi objek pakai YOLO ringan, "
                         "tanpa perlu mikirin BOUND dulu. Cocok buat belajar dasar.",
            on_select=lambda: self._select_mode(app_state.MODE_YOLO_ONLY),
        ).grid(row=0, column=0, padx=16)

        ModeCard(
            cards_frame,
            title="🔗 YOLO + BOUND",
            description="Hasil deteksi YOLO disambungkan ke aturan yang kamu tulis "
                         "sendiri di BOUND Editor. Cocok buat proyek hardware.",
            on_select=lambda: self._select_mode(app_state.MODE_YOLO_BOUND),
        ).grid(row=0, column=1, padx=16)

    def _select_mode(self, mode: str):
        app_state.set_mode(mode)
        # TODO: nanti bisa auto-pindah ke halaman Training Manager setelah pilih mode