"""
ui/bound_docs_page.py
Halaman dokumentasi statis tentang BOUND DSL, buat temen-temen yang belum
pernah dengar BOUND sama sekali.

TODO PENTING: isi teks di bawah masih penjelasan UMUM/rangka.
Ganti/lengkapi dengan grammar & contoh ASLI dari file .bound proyek AGV arm
kamu (misal contoh MOVE(10,20), field WHEN, dst) sebelum di-publish.
"""

import customtkinter as ctk

DOCS_SECTIONS = [
    (
        "Apa itu BOUND?",
        "BOUND adalah bahasa aturan (DSL - Domain Specific Language) yang kamu "
        "rancang untuk menghubungkan hasil sensor/vision (seperti YOLO) dengan "
        "aksi pada sistem fisik, secara deterministik dan step-by-step — "
        "tidak ada langkah yang terlewat atau random.",
    ),
    (
        "Kenapa bukan pakai Python biasa saja?",
        "Karena aturan yang ditulis di BOUND dipisahkan dari kode program utama: "
        "orang yang menulis aturan (misal 'kalau terdeteksi kotak merah, angkat "
        "lengan') tidak perlu paham pemrograman Python secara detail.",
    ),
    (
        "Struktur dasar file .bound",
        "Secara umum, satu file .bound berisi bagian WHEN (kondisi) dan aksi yang "
        "dijalankan kalau kondisi terpenuhi. TODO: lengkapi dengan contoh grammar "
        "asli kamu di sini (DOMAIN/SENSOR/RULE/WHEN, dst).",
    ),
    (
        "Contoh sederhana (placeholder)",
        "WHEN class_name == \"kotak_merah\" AND confidence > 0.7\n"
        "    MOVE(10, 20)\n"
        "    GRAB()\n\n"
        "TODO: ganti contoh ini dengan sintaks resmi dari grammar BOUND kamu.",
    ),
    (
        "Menyambungkan ke YOLO",
        "Di mode 'YOLO + BOUND', tiap objek yang terdeteksi YOLO otomatis jadi "
        "variabel yang bisa dicek di WHEN (contoh: class_name, confidence). "
        "Kamu tidak perlu menulis kode Python tambahan untuk ini.",
    ),
]


class BoundDocsPage(ctk.CTkScrollableFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        ctk.CTkLabel(
            self, text="📘 Belajar BOUND", font=ctk.CTkFont(size=22, weight="bold")
        ).pack(anchor="w", padx=20, pady=(20, 16))

        for title, body in DOCS_SECTIONS:
            ctk.CTkLabel(
                self, text=title, font=ctk.CTkFont(size=16, weight="bold")
            ).pack(anchor="w", padx=20, pady=(14, 4))

            ctk.CTkLabel(
                self, text=body, justify="left", wraplength=640, text_color="gray80",
                font=ctk.CTkFont(family="Consolas") if "\n" in body else None,
            ).pack(anchor="w", padx=20)