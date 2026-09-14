"""
ui/training_page.py
Halaman untuk:
- pilih folder dataset
- mulai training (jalan di thread terpisah biar UI gak freeze)
- lihat progress bar animasi
- lihat & retrain model yang sudah tersimpan lokal

TODO (tahap isi logika):
- [ ] tes threading training dengan dataset kecil dulu
- [ ] sambungkan progress_callback dari trainer.py ke progress bar di sini
"""

import threading
import tkinter.filedialog as fd
from pathlib import Path

import customtkinter as ctk

from core.config import MODELS_DIR, TRAINING_PROFILES, detect_recommended_profile
from core.state import app_state
from vision_engine import dataset_utils, detector, trainer


class TrainingPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.dataset_path = None

        ctk.CTkLabel(
            self, text="Training Manager", font=ctk.CTkFont(size=22, weight="bold")
        ).pack(pady=(20, 6), anchor="w", padx=20)

        self.mode_label = ctk.CTkLabel(self, text="", text_color="gray70")
        self.mode_label.pack(anchor="w", padx=20, pady=(0, 16))
        app_state.on_change(self._refresh_mode_label)
        self._refresh_mode_label()

        # --- Pilih profil training (biar app ini bisa dipakai laptop lemah MAUPUN kencang) ---
        recommended = detect_recommended_profile()
        self.selected_profile = recommended  # dilacak manual, bukan cuma lewat StringVar,
        # supaya gak ketuker/gak ke-update kalau ada perilaku CTkOptionMenu yang gak konsisten
        # antar versi customtkinter.

        profile_row = ctk.CTkFrame(self, fg_color="transparent")
        profile_row.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkLabel(profile_row, text="Profil Training:").pack(side="left", padx=(0, 10))

        profile_menu = ctk.CTkOptionMenu(
            profile_row,
            values=list(TRAINING_PROFILES.keys()),
            command=self._on_profile_change,
        )
        profile_menu.set(recommended)  # tampilkan pilihan awal di dropdown
        profile_menu.pack(side="left")

        ctk.CTkLabel(
            self, text=f"💡 Disarankan untuk laptop ini: '{recommended}' "
                       f"({TRAINING_PROFILES[recommended]['label']}) — "
                       "kamu tetap bisa ganti manual di atas.",
            text_color="gray60", font=ctk.CTkFont(size=12),
        ).pack(anchor="w", padx=20, pady=(0, 10))

        # --- Pilih dataset ---
        dataset_row = ctk.CTkFrame(self, fg_color="transparent")
        dataset_row.pack(fill="x", padx=20, pady=6)

        self.dataset_label = ctk.CTkLabel(dataset_row, text="Belum ada dataset dipilih")
        self.dataset_label.pack(side="left", padx=(0, 12))

        ctk.CTkButton(
            dataset_row, text="Pilih Folder Dataset", command=self._pick_dataset
        ).pack(side="left")

        # --- Progress & tombol mulai ---
        self.progress_bar = ctk.CTkProgressBar(self)
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x", padx=20, pady=(20, 6))

        self.status_label = ctk.CTkLabel(self, text="", text_color="gray70")
        self.status_label.pack(anchor="w", padx=20)

        self.start_button = ctk.CTkButton(
            self, text="🚀 Mulai Training", command=self._start_training
        )
        self.start_button.pack(padx=20, pady=16, anchor="w")

        # --- Riwayat model tersimpan ---
        ctk.CTkLabel(
            self, text="Model Tersimpan (lokal di laptop ini)",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(anchor="w", padx=20, pady=(20, 6))

        self.models_list_frame = ctk.CTkScrollableFrame(self, height=160)
        self.models_list_frame.pack(fill="x", padx=20, pady=(0, 20))
        self._refresh_models_list()

    def _on_profile_change(self, chosen: str):
        self.selected_profile = chosen

    def _refresh_mode_label(self):
        mode_text = (
            "Mode aktif: YOLO + BOUND"
            if app_state.is_bound_active()
            else "Mode aktif: YOLO Biasa"
        )
        self.mode_label.configure(text=mode_text)

    def _pick_dataset(self):
        path = fd.askdirectory(title="Pilih folder dataset")
        if not path:
            return
        valid, problems = dataset_utils.validate_dataset_structure(path)
        if not valid:
            self.dataset_label.configure(
                text=f"Dataset tidak valid: {problems[0]}", text_color="#E05555"
            )
            return
        self.dataset_path = path
        self.dataset_label.configure(text=f"Dataset: {path}", text_color="gray90")

    def _start_training(self):
        if not self.dataset_path:
            self.status_label.configure(text="Pilih dataset dulu ya.")
            return

        self.start_button.configure(state="disabled")
        self.status_label.configure(text="Training dimulai... (jangan tutup app)")

        def _progress(epoch, total):
            self.progress_bar.set(epoch / total)
            self.status_label.configure(text=f"Epoch {epoch}/{total}")

        def _run():
            try:
                data_yaml = f"{self.dataset_path}/data.yaml"
                save_dir = trainer.train_model(
                    dataset_yaml_path=data_yaml,
                    profile_key=self.selected_profile,
                    progress_callback=_progress,
                )
                self.status_label.configure(text=f"Selesai! Tersimpan di: {save_dir}")
            except Exception as e:  # noqa: BLE001 - ditampilkan ke user
                self.status_label.configure(text=f"Training gagal: {e}")
            finally:
                self.start_button.configure(state="normal")
                self._refresh_models_list()

        threading.Thread(target=_run, daemon=True).start()

    def _refresh_models_list(self):
        for widget in self.models_list_frame.winfo_children():
            widget.destroy()

        models = trainer.list_saved_models()
        if not models:
            ctk.CTkLabel(
                self.models_list_frame, text="Belum ada model tersimpan.", text_color="gray60"
            ).pack(anchor="w", pady=4)
            return

        for name in models:
            row = ctk.CTkFrame(self.models_list_frame, fg_color="transparent")
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=name).pack(side="left", padx=(4, 12))
            ctk.CTkButton(row, text="Pakai Model Ini", width=110,
                          command=lambda n=name: app_state.set_active_model(n)).pack(side="left", padx=(0, 6))
            ctk.CTkButton(row, text="🎥 Tes pakai Kamera", width=150,
                          command=lambda n=name: self._test_with_camera(n)).pack(side="left")

    def _test_with_camera(self, model_name: str):
        """
        Buka jendela kamera terpisah (native OpenCV window) buat tes model
        secara live. Dijalankan di thread terpisah biar app utama gak freeze
        selama jendela kamera terbuka. Keluar dari jendela kamera dengan
        menekan 'Q' atau menutup jendelanya langsung.
        """
        onnx_path = Path(MODELS_DIR) / model_name / "weights" / "best.onnx"
        pt_path = Path(MODELS_DIR) / model_name / "weights" / "best.pt"
        model_path = onnx_path if onnx_path.exists() else pt_path

        if not model_path.exists():
            self.status_label.configure(
                text=f"Model belum lengkap (tidak ada best.onnx/best.pt) di {model_name}",
                text_color="#E05555",
            )
            return

        self.status_label.configure(text=f"Membuka kamera pakai model: {model_name}...")

        def _run_camera():
            try:
                model = detector.load_model(str(model_path))
                detector.run_webcam_preview(model)
                self.status_label.configure(text="Jendela kamera ditutup.")
            except Exception as e:  # noqa: BLE001 - ditampilkan ke user
                self.status_label.configure(text=f"Gagal buka kamera: {e}")

        threading.Thread(target=_run_camera, daemon=True).start()