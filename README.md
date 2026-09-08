# 🗺️ DSS Pemetaan Wilayah Penerima Bantuan Sosial Kota Palembang (K-Means Clustering)

Project Skripsi: **M. Syahril (NIM: 221420089)**  
Program Studi Teknik Informatika - Universitas Bina Darma Palembang  
Mitra Data: Bagian Kesejahteraan Rakyat (Kesra) Setda & BPS Kota Palembang  

---

## 📌 Ringkasan Sistem
Aplikasi **Decision Support System (DSS)** berbasis web interaktif ini dirancang untuk memetakan **18 Kecamatan di Kota Palembang** ke dalam **3 Zona Prioritas Penyaluran Bantuan Sosial (Bansos)** secara objektif dan saintifik menggunakan **Algoritma K-Means Clustering** serta pembobotan *Composite Vulnerability Index (CVI)*.

### 🎨 Pengelompokan Wilayah:
- 🔴 **Cluster 0 (Prioritas Tinggi / Darurat)**: Wilayah paling rentan (Kertapati, Gandus, Seberang Ulu I, Seberang Ulu II). Memperoleh porsi bantuan utama (60% pagu).
- 🟡 **Cluster 1 (Prioritas Sedang / Waspada)**: Wilayah dengan tingkat kerentanan menengah (30% pagu).
- 🟢 **Cluster 2 (Prioritas Rendah / Mandiri)**: Wilayah relatif sejahtera dan mandiri (10% pagu).

---

## 👥 Dua Aktor Sistem (Sesuai Usecase Diagram Gambar 3.1)

Sistem membedakan hak akses dan menu kerja secara spesifik untuk 2 peran pengguna:

| Peran Aktor | Username / Password | Hak Akses & Fitur Utama |
|---|---|---|
| 👨‍💻 **Admin / Petugas Kesra** | `admin` / `admin123` | • Memilih & Mengunggah Dataset BPS (CSV/Excel)<br>• Menjalankan Engine Pemrosesan K-Means<br>• Matriks Jarak Euclidean & Iterasi $d(x, c)$<br>• Pengujian Validasi Ilmiah (Elbow, Silhouette, DBI, CHI)<br>• **Peta Geospasial (Peta Lama)**: Peta tematik standar 18 kecamatan & distribusi indikator<br>• **Peta & Grafik Kelayakan Bansos (Peta Baru)**: Peta geospasial kelayakan, filter status bansos, bar ranking CVI Kesra, donut proporsi, kuadran kesesuaian & tabel audit<br>• Analisis Tren Multi-Tahun (2023 vs 2025)<br>• Generator Teks Skripsi Bab 4 Otomatis<br>• Live Database Inspector SQLite |
| 🏛️ **Pimpinan / Pengambil Keputusan** | `pimpinan` / `pimpinan123` | • Dashboard Ringkasan Eksekutif Zonasi Wilayah<br>• Transparansi Alur Iterasi K-Means<br>• **Peta Spasial (Peta Lama)**: Peta sebaran spasial standar & grafik indikator<br>• **Peta & Grafik Kelayakan Bansos (Peta Baru)**: Analisis spasial & grafik kelayakan penerima bantuan Kesra<br>• **Simulator Alokasi Anggaran Bansos (DSS Core)** (Input Anggaran Rp & Kuota KK)<br>• Profiler & Deep Dive Komparasi 18 Kecamatan<br>• Radar Chart Karakteristik Klaster<br>• Pusat Download Laporan Eksekutif (.xlsx) |

---

## 🗄️ Database Relasional (SQLite: `bansos_palembang.db`)

Sistem menggunakan **SQLite** sebagai basis data relasional lokal yang mengimplementasikan rancangan **Entity Relationship Diagram (ERD)** pada Bab 3 Skripsi:
1. `USERS`: Autentikasi dan hak akses aktor sistem (Admin vs Pimpinan).
2. `KECAMATAN`: Data master 18 kecamatan dan koordinat geospasial (Latitude, Longitude).
3. `DATA_INDIKATOR_BPS`: Data 7 indikator statistik kemiskinan dan kesejahteraan BPS.
4. `KLASTER_PRIORITAS`: Master kategori klaster, bobot persentase, dan rekomendasi intervensi.
5. `HASIL_CLUSTERING`: Riwayat hasil klasterisasi K-Means, skor CVI, dan jarak ke centroid.
6. `SIMULASI_ALOKASI_BANSOS`: Arsip hasil perhitungan simulator alokasi anggaran dan kuota KK.
7. `LAPORAN_EXPORT`: Log audit berkas laporan yang digenerate oleh pengguna.

---

## 🚀 Cara Menjalankan Website (Running Locally)

### 1. Prasyarat System
- Python 3.10 / 3.11 / 3.12 telah terinstall di komputer.

### 2. Install Dependensi (Sekali saja)
Buka terminal / Command Prompt di folder proyek ini (`d:\websyahril`), lalu jalankan:
```bash
pip install -r requirements.txt
```

### 3. Jalankan Aplikasi Web
Jalankan perintah berikut di terminal:
```bash
streamlit run app.py
```
Website akan otomatis terbuka di browser Anda pada alamat: `http://localhost:8501`.

---

## 📂 Struktur Folder Proyek
```
d:\websyahril\
├── app.py                     # Entry point utama dashboard Streamlit UI
├── auth_helper.py             # Modul Autentikasi & Multi-Aktor (Admin vs Pimpinan)
├── database.py                # Database SQLite Engine (ERD Schema & CRUD)
├── clustering_engine.py       # Engine AI (MinMax Scaling, K-Means, CVI, Elbow & Silhouette)
├── visualization_helper.py    # Modul Grafik Plotly & Peta Tematik Spasial Folium
├── dss_simulator.py           # Engine DSS Simulasi Alokasi Dana Rp & Kuota KK
├── export_helper.py           # Modul Ekspor Excel Multi-Sheet & Draft Teks Bab 4
├── requirements.txt           # File daftar library dependency Python
├── data/
│   ├── bansos_palembang.db    # Database SQLite Utama
│   ├── palembang_bps_data.csv # Dataset BPS 2023/2024
│   ├── palembang_bps_data_2025_2026.csv # Dataset Pemutakhiran Kesra 2025/2026
│   └── *.xlsx                 # File Master Data Statistik & Hasil Clustering
└── README.md                  # Dokumentasi Proyek
```
