# 🗺️ DOKUMENTASI & ANALISIS DETAIL SISTEM PENDUKUNG KEPUTUSAN (DSS) PEMETAAN BANTUAN SOSIAL KOTA PALEMBANG

**Penulis / Pengembang:** M. Syahril (NIM: 221420089)  
**Program Studi:** Teknik Informatika, Universitas Bina Darma Palembang  
**Mitra Data:** Bagian Kesejahteraan Rakyat (Kesra) Sekretariat Daerah & Badan Pusat Statistik (BPS) Kota Palembang  
**Metode AI:** Algoritma *K-Means Clustering* & *Composite Vulnerability Index (CVI)*  

---

## 📋 DAFTAR ISI
1. [Ringkasan Eksekutif & Latar Belakang](#1-ringkasan-eksekutif--latar-belakang)
2. [Arsitektur Sistem & Tech Stack](#2-arsitektur-sistem--tech-stack)
3. [Struktur Data & Indikator Penilaian](#3-struktur-data--indikator-penilaian)
4. [Landasan Matematika & Metodologi AI](#4-landasan-matematika--metodologi-ai)
5. [Bedah Kode Sumber & Analisis Modul](#5-bedah-kode-sumber--analisis-modul)
6. [Fitur Utama & Analisis 6 Tab Utama](#6-fitur-utama--analisis-6-tab-utama)
7. [Simulasi Alokasi Anggaran & Rekomendasi Kebijakan](#7-simulasi-alokasi-anggaran--rekomendasi-kebijakan)
8. [Metrik Validasi Ilmiah & Pengujian Model](#8-metrik-validasi-ilmiah--pengujian-model)
9. [Panduan Penggunaan & Pengoperasian](#9-panduan-penggunaan--pengoperasian)

---

## 1. 🎯 RINGKASAN EKSEKUTIF & LATAR BELAKANG

Aplikasi **DSS Pemetaan Bansos Palembang** ini adalah sistem pendukung keputusan (*Decision Support System*) berbasis web interaktif yang dikembangkan untuk mengelompokkan **18 Kecamatan di Kota Palembang** ke dalam zonasi prioritas penyaluran Bantuan Sosial (Bansos). 

Tujuan utama sistem ini adalah mengatasi tantangan **ketidaktepatan sasaran** dan **subjektivitas alokasi anggaran bansos** dengan menerapkan pendekatan statistik saintifik berbasis algoritma *K-Means Clustering*. Dengan memanfaatkan data sekunder resmi dari BPS dan Bagian Kesra Kota Palembang, sistem ini mampu secara objektif mengelompokkan wilayah ke dalam 3 Tingkat Prioritas:
- 🔴 **Prioritas Tinggi (Darurat)**: Wilayah dengan tingkat kerentanan sosial-ekonomi paling tinggi (penduduk miskin tinggi, pengangguran tinggi, IPM rendah, pendapatan rendah).
- 🟡 **Prioritas Sedang (Waspada)**: Wilayah dengan tingkat kesejahteraan kelas menengah.
- 🟢 **Prioritas Rendah (Mandiri)**: Wilayah relatif sejahtera dengan kapasitas ekonomi mandiri (IPM tinggi, akses fasilitas baik).

---

## 2. 🏗️ ARSITEKTUR SISTEM & TECH STACK

Aplikasi ini dibangun menggunakan arsitektur modular Python dengan memanfaatkan pustaka (*libraries*) modern data science dan visualisasi spasial:

```
                  ┌──────────────────────────────────────────────┐
                  │          USER INTERFACE (Streamlit)          │
                  │                   app.py                     │
                  └──────────────────────┬───────────────────────┘
                                         │
       ┌─────────────────────────────────┼─────────────────────────────────┐
       ▼                                 ▼                                 ▼
┌──────────────┐                ┌────────────────┐                ┌────────────────┐
│ Data Layer   │                │ Analytics AI   │                │ Visual & Export│
├──────────────┤                ├────────────────┤                ├────────────────┤
│ • CSV/Excel  │                │ • MinMax Scale │                │ • Folium Map   │
│ • 2023 vs    │ ─────────────► │ • K-Means      │ ─────────────► │ • Plotly Charts│
│   2025 Data  │                │ • CVI Weighting│                │ • OpenPyXL     │
│ (data/)      │                │(clustering_eng)│                │ (vis & export) │
└──────────────┘                └────────────────┘                └────────────────┘
```

### Stack Teknologi:
1. **Bahasa Pemrograman**: Python 3.10+
2. **Framework Web**: `streamlit` (Rendering antarmuka pengguna interaktif dan responsif)
3. **Engine Machine Learning & Statistik**: `scikit-learn` (`KMeans`, `MinMaxScaler`, `silhouette_score`, `davies_bouldin_score`, `calinski_harabasz_score`)
4. **Manipulasi Data**: `pandas`, `numpy`
5. **Visualisasi Interaktif**: 
   - `plotly` (Horizontal Bar Chart, 2D Scatter Plot, Radar Summary Chart, Line Charts untuk Elbow & Silhouette)
   - `folium` & `streamlit-folium` (Peta spasial interaktif zonasi Palembang berbasis tile CartoDB Positron)
6. **Ekspor Laporan**: `openpyxl` (Generator laporan Excel multi-sheet otomatis)

---

## 3. 📊 STRUKTUR DATA & INDIKATOR PENILAIAN

Sistem memproses dataset 18 kecamatan Kota Palembang berdasarkan **7 Indikator Utama BPS/Kesra**:

| No | Nama Indikator | Kode Kolom | Sifat Terhadap Kerentanan | Deskripsi |
|---|---|---|---|---|
| 1 | Jumlah Penduduk Miskin | `Jumlah_Penduduk_Miskin` | **High (Positif)** | Jumlah jiwa berpendapatan di bawah garis kemiskinan |
| 2 | Tingkat Pengangguran | `Tingkat_Pengangguran` | **High (Positif)** | Persentase angkatan kerja yang tidak memiliki pekerjaan (%) |
| 3 | Pendapatan Rata-Rata | `Pendapatan_Rata_Rata` | **Low (Invers/Negatif)** | Estimasi pendapatan bulanan per kapita/RT (Rp) |
| 4 | Kepadatan Penduduk | `Kepadatan_Penduduk` | **High (Positif)** | Jumlah jiwa per $km^2$ |
| 5 | Akses Fasilitas Publik | `Akses_Fasilitas_Publik` | **Low (Invers/Negatif)** | Skor indeks jangkauan fasilitas kesehatan & pendidikan (0-100) |
| 6 | Jumlah KK Penerima Bansos | `Jumlah_KK_Penerima_Bansos` | **High (Positif)** | Data eksisting jumlah KK penerima bantuan |
| 7 | Indeks Pembangunan Manusia | `IPM` | **Low (Invers/Negatif)** | Indeks komposit kualitas hidup BPS |

### Edisi Dataset yang Disediakan:
1. **Dataset 2025/2026 (`palembang_bps_data_2025_2026.csv`)**: Data pemutakhiran terbaru Bagian Kesra & BPS.
2. **Dataset 2023/2024 (`palembang_bps_data.csv`)**: Data historis proposal awal skripsi.
3. **Custom Upload**: Pengguna dapat mengunggah file CSV/Excel eksternal secara fleksibel.

---

## 4. 📐 LANDASAN MATEMATIKA & METODOLOGI AI

### 4.1 Min-Max Normalization
Sebelum proses clustering, seluruh nilai atribut disamakan skalanya ke rentang $[0, 1]$ agar variabel ber-skala besar (seperti pendapatan Rp 4.000.000) tidak mendominasi variabel ber-skala kecil (seperti pengangguran 4.2%):
$$X_{scaled} = \frac{X - X_{min}}{X_{max} - X_{min}}$$

### 4.2 Formulasi Jarak Euclidean (Euclidean Distance)
Metode K-Means mengukur kedekatan setiap vektor data kecamatan $x_i$ terhadap centroid klaster $c_j$ menggunakan jarak Euclidean multidimensi:
$$d(x_i, c_j) = \sqrt{\sum_{k=1}^{n} (x_{ik} - c_{jk})^2}$$

### 4.3 Composite Vulnerability Index (CVI) & Inversi Atribut
Untuk menentukan urutan prioritas klaster secara otomatis (sehingga Cluster 0 selalu menjadi "Prioritas Tinggi/Darurat"), sistem menghitung Skor Kerentanan Komposit (CVI):
- Atribut Kerentanan Tinggi ($H$): langsung ditambahkan ($x_{scaled}$)
- Atribut Kerentanan Rendah ($L$): diinversikan terlebih dahulu ($1.0 - x_{scaled}$)
$$CVI = \frac{1}{N} \left( \sum_{h \in H} x_h + \sum_{l \in L} (1.0 - x_l) \right)$$

---

## 5. 🔍 BEDAH KODE SUMBER & ANALISIS MODUL

Berikut penjelasan mendalam mengenai 5 file utama dalam repositori:

### 1. `app.py` (Main Dashboard Controller)
- **Fungsi Utama**: Mengatur konfigurasi halaman Streamlit, mengelola state aplikasi, memuat CSS kustom (Plus Jakarta Sans font, gradient header, metric cards), mengolah input dari sidebar, dan menyajikan 6 Tab utama.
- **Logika Kunci**:
  - `load_data_2023()` & `load_data_2025()`: Fungsi pemuat data ber-cache (`@st.cache_data`) untuk performa tinggi.
  - Penanganan dinamis pilihan dataset (2025/2026, 2023/2024, atau Custom File Upload).
  - Integrasi komponen interaktif `st_folium` dan `st.plotly_chart`.

### 2. `clustering_engine.py` (Core ML Engine)
- **Fungsi Utama**: Mengeksekusi pengolahan data saintifik.
- **Fungsi Penting**:
  - `preprocess_data()`: Mengaplikasikan `MinMaxScaler` dari `scikit-learn`.
  - `calculate_vulnerability_index()`: Mengalkulasi skor CVI untuk mengurutkan prioritas klaster secara konsisten.
  - `run_kmeans_clustering()`: Melatih model `KMeans(n_clusters=K, random_state=42)`, menghitung matriks jarak Euclidean, mengurutkan label klaster berdasarkan CVI, serta menghitung metrik validasi (*Silhouette Score*, *Davies-Bouldin Index*, *Calinski-Harabasz Index*).
  - `compute_elbow_and_silhouette_range()`: Melakukan perulangan $K = 1 \dots 8$ untuk menghasilkan data evaluasi grafik Elbow (WCSS) dan Silhouette.

### 3. `dss_simulator.py` (Decision Support Simulator Engine)
- **Fungsi Utama**: Mensimulasikan alokasi anggaran (Rp) dan kuota (KK) penerima bantuan sosial secara proporsional.
- **Logika Kunci**:
  - `simulate_bansos_allocation()`: Menerapkan skema pembobotan bertingkat:
    - Bobot Klaster: Prioritas Tinggi = 60%, Prioritas Sedang = 30%, Prioritas Rendah = 10%.
    - Bobot Sub-Kecamatan: Dihitung proporsional terhadap skor CVI masing-masing kecamatan di dalam klasternya.
  - `compare_yearly_trends()`: Menganalisis pergeseran data 2023 vs 2025 (menghitung `Perubahan_Penduduk_Miskin` dan `Perubahan_IPM`).

### 4. `visualization_helper.py` (Spatial & Graphical Renderer)
- **Fungsi Utama**: Menyediakan visualisasi data tingkat lanjut.
- **Komponen Penting**:
  - `KECAMATAN_COORDS`: Kamus koordinat geospasial (Latitude, Longitude) untuk 18 Kecamatan Kota Palembang.
  - `create_palembang_map()`: Membangun peta tematik interaktif Folium dengan CartoDB Positron tiles, marker melingkar ber-radius dinamis, popup ringkasan data, dan bebas dari logo/teks attribution bawah.
  - `plot_elbow_chart()` & `plot_silhouette_chart()`: Grafik Plotly untuk validasi titik siku optimal.
  - `plot_radar_summary()`: Chart radar untuk membandingkan profil centroid 7 indikator antar-klaster.
  - `plot_cluster_bar()` & `plot_scatter_2d()`: Chart distribusi sebaran kecamatan.

### 5. `export_helper.py` (Report Generator)
- **Fungsi Utama**: Menyediakan fitur pengunduhan laporan formal.
- **Komponen**:
  - `export_results_to_excel()`: Membuat file `.xlsx` multi-sheet (*Hasil Clustering*, *Profil Centroid Cluster*, *Uji Elbow & Silhouette*, *Metrik Validasi*).
  - `generate_bab4_narration()`: Menghasilkan draft narasi ilmiah Bab 4 Skripsi otomatis yang terformat dan siap digunakan untuk penulisan karya ilmiah.

---

## 6. 🖥️ FITUR UTAMA & ANALISIS 6 TAB UTAMA

Dashboard web ini dibagi menjadi 6 tab utama yang komprehensif:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│ [Tab 1: Peta & Dash] [Tab 2: Simulator DSS] [Tab 3: Tren Multi-Tahun]           │
│ [Tab 4: Profiler Kec] [Tab 5: Euclidean Matrix] [Tab 6: Validasi & Export]      │
└─────────────────────────────────────────────────────────────────────────────────┘
```

1. **📊 Tab 1: Dashboard & Peta Spasial**
   - Menyajikan Peta Tematik Interaktif Palembang (Folium Map).
   - Menampilkan Horizontal Bar Chart distribusi indikator per kecamatan.
   - Radar Chart profil 7 indikator antar-klaster.
   - 2D Scatter Plot sebaran variabel.

2. **💰 Tab 2: Simulator Alokasi Bansos (DSS Core Feature)**
   - Fitur simulasi alokasi Pagu Anggaran (Rp) dan Kuota Kepala Keluarga (KK).
   - Pie chart distribusi alokasi anggaran dan kuota per klaster.
   - Tabel rekomendasi alokasi nominal per kecamatan dan estimasi nilai bantuan per KK (Rp/KK).

3. **📈 Tab 3: Analisis Perbandingan Tren Multi-Tahun**
   - Menampilkan grafik pergeseran kemiskinan dan kenaikan IPM antara data 2023/2024 vs 2025/2026.
   - Membantu pengambil keputusan melihat efektivitas kebijakan bansos dari tahun ke tahun.

4. **🔍 Tab 4: Profiler Per-Kecamatan (Deep Dive Inspector)**
   - Pengguna dapat memilih 1 dari 18 kecamatan untuk melihat perbandingan indikator lokal vs rata-rata kota.
   - Memberikan rekomendasi intervensi kebijakan yang spesifik per kecamatan.

5. **⚙️ Tab 5: Iterasi & Matriks Jarak Euclidean**
   - Transparansi matematis penuh: Menampilkan tabel Min-Max Normalization, matriks jarak Euclidean dari tiap kecamatan ke seluruh centroid ($d_0, d_1, d_2$), dan jarak terdekat ($d_{min}$).
   - Menyajikan nilai centroid asli dan centroid ter-normalisasi.

6. **🧪 Tab 6: Validasi Ilmiah & Export Data**
   - Grafik Metode Elbow (WCSS) & Silhouette Score.
   - Penilaian akademis: *Silhouette Score*, *Davies-Bouldin Index (DBI)*, dan *Calinski-Harabasz Index (CHI)*.
   - Tabel evaluasi $K=1 \dots 8$.
   - Tombol pengunduhan laporan Excel (`.xlsx`) dan draft narasi Skripsi Bab 4.

---

## 7. 💡 SIMULASI ALOKASI ANGGARAN & REKOMENDASI KEBIJAKAN

Contoh skenario simulasi dengan **Total Pagu Anggaran = Rp 5.000.000.000** dan **Total Kuota = 10.000 KK**:

- **Klaster Prioritas Tinggi (60% Anggaran / Rp 3,0 Miliar & 6.000 KK)**:
  - Dialokasikan ke kecamatan seperti **Kertapati, Gandus, Seberang Ulu I, Seberang Ulu II**.
  - Rekomendasi: Penyaluran Bansos Tunai (PKH/BPNT), program penanggulangan pengangguran, dan perbaikan infrastruktur publik.
- **Klaster Prioritas Sedang (30% Anggaran / Rp 1,5 Miliar & 3.000 KK)**:
  - Dialokasikan ke kecamatan seperti **Plaju, Sematang Borang, Jakabaring, IB II, Sukarami, Sako**.
  - Rekomendasi: Bantuan kuota bersyarat dan pelatihan keterampilan kerja.
- **Klaster Prioritas Rendah (10% Anggaran / Rp 500 Juta & 1.000 KK)**:
  - Dialokasikan ke kecamatan seperti **Bukit Kecil, IT I, IT II, IT III, IB I, Kalidoni, Kemuning, Alang-Alang Lebar**.
  - Rekomendasi: Program pemberdayaan UMKM dan alokasi bantuan darurat terbatas.

---

## 8. 🧪 METRIK VALIDASI ILMIAH & PENGUJIAN MODEL

Berdasarkan pengujian pada dataset pemutakhiran 2025/2026 dengan $K=3$:
- **Silhouette Score**: $\approx 0.45 - 0.55$ (Menunjukkan struktur pemisahan klaster yang kuat / *strong cluster structure*).
- **Metode Elbow**: Menunjukkan titik siku terjelas (*elbow point*) pada $K=3$.
- **Davies-Bouldin Index (DBI)**: Nilai rendah mengonfirmasi kerapatan internal klaster yang baik dan separasi yang jelas antar-klaster.

---

## 9. 🚀 PANDUAN PENGGUNAAN & PENGOPERASIAN

### Langkah 1: Instalasi Dependensi
Pastikan Python 3.10+ telah terinstall, lalu jalankan perintah berikut pada terminal di folder proyek (`d:\websyahril`):
```bash
pip install -r requirements.txt
```

### Langkah 2: Menjalankan Dashboard
Jalankan aplikasi dengan perintah Streamlit:
```bash
streamlit run app.py
```
Aplikasi web akan otomatis terbuka di browser pada alamat: `http://localhost:8501`.

---

## 📌 KESIMPULAN

Aplikasi **DSS Pemetaan Bansos Palembang** karya M. Syahril ini merupakan solusi digital inovatif, saintifik, dan transparan. Sistem ini tidak hanya memenuhi standar akademik karya ilmiah skripsi, tetapi juga siap diimplementasikan sebagai sistem pendukung keputusan nyata bagi Pemerintah Kota Palembang (Bagian Kesra & Dinas Sosial) dalam mewujudkan efisiensi dan ketepatan sasaran penyaluran bantuan sosial.
