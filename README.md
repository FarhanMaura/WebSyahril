# 🗺️ DSS Pemetaan Wilayah Penerima Bantuan Sosial Kota Palembang (K-Means Clustering)

Project Skripsi: **M. Syahril (NIM: 221420089)**  
Program Studi Teknik Informatika - Universitas Bina Darma Palembang  

---

## 📌 Ringkasan Sistem
Aplikasi **Dashboard System Support (DSS)** berbasis web ini dirancang untuk memetakan **18 Kecamatan di Kota Palembang** ke dalam **3 Zona Prioritas Penyaluran Bantuan Sosial (Bansos)** secara otomatis berbasis data statistik resmi BPS dan Dinas Sosial Kota Palembang menggunakan **Algoritma K-Means Clustering**.

### 🎨 Pengelompokan Wilayah:
- 🔴 **Cluster 0 (Prioritas Tinggi / Darurat)**: Wilayah paling rentan (Kertapati, Gandus, Seberang Ulu I, Seberang Ulu II). Harus diprioritaskan dapet bansos duluan.
- 🟡 **Cluster 1 (Prioritas Sedang / Waspada)**: Wilayah dengan tingkat kesejahteraan menengah.
- 🟢 **Cluster 2 (Prioritas Rendah / Mandiri)**: Wilayah relatif sejahtera dan mandiri (Bukit Kecil, Ilir Timur I, II, III).

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
├── clustering_engine.py       # Engine AI (MinMax Normalization, K-Means, Elbow & Silhouette)
├── visualization_helper.py    # Modul Grafik Plotly & Peta Tematik Folium Palembang
├── export_helper.py           # Modul Ekspor Excel & Draft Teks Laporan Skripsi Bab 4
├── requirements.txt           # File daftar library dependency Python
├── data/
│   └── palembang_bps_data.csv # Dataset bawaan 18 Kecamatan Palembang (7 Indikator BPS)
└── README.md                  # Panduan penggunaan proyek
```

---

## 🔥 Fitur Utama Web Dashboard:
1. **Interactive Folium Map**: Peta Palembang interaktif dengan marker warna zonasi (Merah, Kuning, Hijau) dan popup data detail per kecamatan.
2. **Dynamic K-Means Parameter Controls**: Slider penyesuaian jumlah klaster $K$ dan pemilih indikator pada sidebar.
3. **Dual Data Input**:
   - Pilihan menggunakan **Dataset BPS Palembang Bawaan** (langsung jalan 100%).
   - Fitur **Upload Custom File Excel/CSV** jika ada pembaruan data dari BPS/Dinsos.
   - Tombol **Download Template CSV**.
4. **Pembuktian Ilmiah (Uji K Optimal)**:
   - **Grafik Metode Elbow (WCSS)**.
   - **Grafik & Nilai Silhouette Score** (Validasi kecocokan klaster).
   - Metrik Tambahan: *Davies-Bouldin Index* & *Calinski-Harabasz Index*.
5. **Amunisi Laporan Skripsi Bab 4**:
   - Draft narasi ilmiah Bab 4 otomatis yang tinggal di-copy paste ke MS Word.
   - Tombol **Export Laporan Lengkap (.xlsx)** dengan multi-sheet (Hasil Cluster, Profil Centroid, Metrik Validasi).
