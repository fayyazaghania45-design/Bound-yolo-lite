# BOUND × YOLO (Lite)

Aplikasi desktop open-source untuk belajar & training YOLO ringan — dengan
pilihan integrasi ke BOUND DSL — dirancang agar tetap bisa dijalankan di
laptop dengan spesifikasi rendah (tanpa GPU dedicated).

## Kenapa proyek ini ada

Tidak semua orang punya laptop dengan spesifikasi tinggi untuk belajar dan
training YOLO. Proyek ini memilih model YOLO paling ringan (YOLOv8n),
resolusi & batch kecil, transfer learning (freeze sebagian backbone), dan
export ke ONNX untuk inference — supaya proses belajar tetap bisa dilakukan
di laptop biasa.

## Dua mode

- **YOLO Biasa** — training & deteksi objek, tanpa BOUND. Cocok untuk belajar
  dasar computer vision.
- **YOLO + BOUND** — hasil deteksi disambungkan ke aturan yang ditulis di
  BOUND DSL (`.bound`), lalu (opsional) diteruskan ke hardware lewat MQTT.

## Struktur proyek

```
bound_yolo_lite/
├── main.py                  # entry point, sidebar & routing halaman
├── core/
│   ├── config.py            # path penyimpanan lokal + default training ringan
│   └── state.py             # status aplikasi (mode aktif, model aktif, dst)
├── ui/
│   ├── sidebar.py
│   ├── dashboard_page.py     # pilih mode
│   ├── training_page.py      # dataset, training, riwayat model
│   ├── bound_docs_page.py     # dokumentasi BOUND
│   ├── bound_editor_page.py   # tulis & validasi file .bound
│   └── connectivity_page.py   # setup MQTT ke hardware
├── vision_engine/
│   ├── trainer.py            # training YOLOv8n versi ringan
│   ├── detector.py           # load model & jalankan deteksi
│   └── dataset_utils.py       # validasi struktur dataset
├── bound_engine/
│   └── bridge.py              # jembatan hasil deteksi YOLO <-> BOUND DSL
└── storage/                   # dataset, model, & script .bound tersimpan lokal
```

## Status pengembangan (per bagian)

Semua struktur file sudah ada (skeleton lengkap), tapi belum semua logika
final — supaya kalau ada bug, jelas letaknya di lapisan mana:

| Bagian | Status |
|---|---|
| UI shell + navigasi | ✅ Jalan (belum ada bug lapisan ini) |
| Dashboard (pilih mode) | ✅ Jalan |
| Training Manager (UI) | ✅ Jalan, **belum dites** dengan dataset & training asli |
| `vision_engine/trainer.py` | ⚠️ Belum dites — tes dulu dengan dataset kecil (2-3 class) |
| `vision_engine/detector.py` | ⚠️ Belum dites |
| BOUND Docs | ⚠️ Isi teks masih placeholder — **wajib diganti** dengan grammar BOUND asli sebelum publish |
| BOUND Editor (UI) | ✅ Jalan (buka/simpan/tulis file .bound) |
| `bound_engine/bridge.py` | ⚠️ Placeholder — import `bound_dsl.parser`/`bound_dsl.engine` perlu disesuaikan dengan nama modul asli di package `bound-dsl` kamu |
| Connectivity (MQTT) | ✅ UI jalan, koneksi MQTT belum dites ke broker sungguhan |

## Cara menjalankan

```bash
pip install -r requirements.txt
pip install -e /path/ke/package/bound-dsl   # package BOUND DSL kamu sendiri
python main.py
```

## Batasan yang perlu jujur disampaikan ke pengguna

- Training tetap butuh waktu di laptop tanpa GPU — sudah diringankan
  (imgsz 320, batch 4, freeze backbone), tapi bukan instan.
- Tetap ada spesifikasi minimum wajar (disarankan: RAM 8GB, CPU 4-core) —
  bukan "jalan di semua laptop apapun".
- Pengguna tetap harus menyiapkan/label dataset sendiri untuk object custom;
  ini bagian yang tidak bisa disingkat oleh software.

## Urutan disarankan untuk lanjut mengisi logika

1. Tes `vision_engine/trainer.py` + `dataset_utils.py` pakai dataset kecil
2. Tes `vision_engine/detector.py` pakai model hasil training di atas
3. Sambungkan `bound_engine/bridge.py` ke package `bound-dsl` asli (ganti import placeholder)
4. Lengkapi konten `ui/bound_docs_page.py` dengan grammar & contoh asli
5. Tes `ui/connectivity_page.py` ke broker Mosquitto lokal