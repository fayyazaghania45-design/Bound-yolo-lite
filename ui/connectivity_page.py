"""
ui/connectivity_page.py
Form untuk menyambungkan aplikasi ke hardware proyek pengguna sendiri,
lewat MQTT (broker + topic). Ini yang bikin app-nya bukan cuma buat belajar,
tapi bisa dipakai nyata untuk proyek AGV/robot/dsb milik pengguna.

TODO (tahap isi logika):
- [ ] tes koneksi ke broker Mosquitto lokal dulu sebelum broker publik
- [ ] tentukan format payload publish (JSON hasil detect + status BOUND)
"""

import customtkinter as ctk


class ConnectivityPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.client = None

        ctk.CTkLabel(
            self, text="🔌 Connectivity", font=ctk.CTkFont(size=22, weight="bold")
        ).pack(anchor="w", padx=20, pady=(20, 6))

        ctk.CTkLabel(
            self,
            text="Sambungkan hasil deteksi YOLO / BOUND ke hardware proyekmu sendiri.",
            text_color="gray70",
        ).pack(anchor="w", padx=20, pady=(0, 20))

        form = ctk.CTkFrame(self, fg_color="transparent")
        form.pack(anchor="w", padx=20)

        self.host_entry = self._labeled_entry(form, "Broker MQTT (host)", "localhost", 0)
        self.port_entry = self._labeled_entry(form, "Port", "1883", 1)
        self.topic_entry = self._labeled_entry(form, "Topic publish", "bound/agv_arm/detections", 2)

        self.status_label = ctk.CTkLabel(self, text="Belum terhubung.", text_color="gray70")
        self.status_label.pack(anchor="w", padx=20, pady=(16, 6))

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(anchor="w", padx=20)
        ctk.CTkButton(btn_row, text="Connect", command=self._connect).pack(side="left", padx=(0, 8))
        ctk.CTkButton(btn_row, text="Disconnect", command=self._disconnect).pack(side="left")

    def _labeled_entry(self, parent, label, default, row):
        ctk.CTkLabel(parent, text=label).grid(row=row, column=0, sticky="w", pady=6, padx=(0, 12))
        entry = ctk.CTkEntry(parent, width=240)
        entry.insert(0, default)
        entry.grid(row=row, column=1, pady=6)
        return entry

    def _connect(self):
        try:
            import paho.mqtt.client as mqtt
        except ImportError:
            self.status_label.configure(
                text="Package 'paho-mqtt' belum ter-install.", text_color="#E05555"
            )
            return

        host = self.host_entry.get()
        port = int(self.port_entry.get())

        self.client = mqtt.Client()
        try:
            self.client.connect(host, port, keepalive=10)
            self.status_label.configure(
                text=f"Terhubung ke {host}:{port}", text_color="#4CAF50"
            )
        except Exception as e:  # noqa: BLE001 - ditampilkan ke user
            self.status_label.configure(text=f"Gagal connect: {e}", text_color="#E05555")

    def _disconnect(self):
        if self.client:
            self.client.disconnect()
            self.client = None
        self.status_label.configure(text="Terputus.", text_color="gray70")