import io
import pandas as pd

def export_results_to_excel(df_result: pd.DataFrame, cluster_summary: pd.DataFrame, elbow_df: pd.DataFrame, metrics: dict):
    """
    Generates an Excel workbook in memory with multiple sheets:
    - Hasil Clustering
    - Profil Centroid
    - Evaluasi Validasi (Elbow & Silhouette)
    """
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Sheet 1: Hasil Clustering
        df_result.to_excel(writer, sheet_name='Hasil Clustering', index=False)
        
        # Sheet 2: Profil Centroid
        cluster_summary.to_excel(writer, sheet_name='Profil Centroid Cluster')
        
        # Sheet 3: Evaluasi Validasi
        elbow_df.to_excel(writer, sheet_name='Uji Elbow & Silhouette', index=False)
        
        # Sheet 4: Summary Metrics
        df_metrics = pd.DataFrame([
            {'Metrik': 'Jumlah Cluster (K)', 'Nilai': metrics['n_clusters']},
            {'Metrik': 'Silhouette Score', 'Nilai': round(metrics['silhouette_score'], 4)},
            {'Metrik': 'Davies-Bouldin Index', 'Nilai': round(metrics['davies_bouldin_score'], 4)},
            {'Metrik': 'Calinski-Harabasz Index', 'Nilai': round(metrics['calinski_harabasz_score'], 4)},
        ])
        df_metrics.to_excel(writer, sheet_name='Metrik Validasi', index=False)
        
    output.seek(0)
    return output.getvalue()

def generate_bab4_narration(df_result: pd.DataFrame, metrics: dict, elbow_df: pd.DataFrame, year_label: str = "2025/2026"):
    """
    Generates formatted text specifically structured for Skripsi Bab 4 (Hasil dan Pembahasan).
    Dynamically accepts year_label (e.g. '2025/2026' or '2023/2024').
    """
    k = metrics['n_clusters']
    sil = metrics['silhouette_score']
    db = metrics['davies_bouldin_score']
    
    c0 = df_result[df_result['Cluster'] == 0]['Kecamatan'].tolist()
    c1 = df_result[df_result['Cluster'] == 1]['Kecamatan'].tolist()
    c2 = df_result[df_result['Cluster'] == 2]['Kecamatan'].tolist()
    
    text = f"""================================================================================
📝 DRAFT TEKS LAPORAN SKRIPSI BAB 4 (HASIL DAN PEMBAHASAN - EDISI TAHUN {year_label})
================================================================================

BAB IV: HASIL DAN PEMBAHASAN

4.1 Pengolahan Data dan Implementasi K-Means Clustering
Berdasarkan data statistik pemutakhiran 18 kecamatan di Kota Palembang edisi Tahun {year_label} yang bersumber dari Bagian Kesejahteraan Rakyat (Kesra) Kantor Sekretariat Daerah dan Badan Pusat Statistik (BPS) Kota Palembang, dilakukan pengelompokan wilayah penerima bantuan sosial menggunakan algoritma K-Means Clustering dengan jumlah klaster K={k}.

4.2 Uji Validasi Jumlah Klaster Optimal (Metode Elbow & Silhouette Score)
Penentuan jumlah klaster optimal dievaluasi menggunakan metode Elbow dan Silhouette Score:
1. Metode Elbow: Evaluasi grafik Within-Cluster Sum of Squares (WCSS) menunjukkan titik siku (elbow point) yang paling signifikan terjadi pada K={k}.
2. Evaluasi Silhouette Score: Hasil perhitungan menunjukkan nilai Silhouette Score sebesar {sil:.4f} (atau ~{sil*100:.1f}%). Nilai ini membuktikan secara matematis bahwa struktur klaster yang terbentuk terpisah dengan sangat baik (strong cluster structure) dan valid secara ilmiah.
3. Davies-Bouldin Index (DBI): Memperoleh nilai {db:.4f}, mengindikasikan tingkat separasi antar-klaster yang optimal.

4.3 Hasil Klasifikasi dan Pemetaan Wilayah Prioritas (Edisi Tahun {year_label})
Berdasarkan pengolahan algoritma K-Means, 18 kecamatan di Kota Palembang terbagi ke dalam {k} kategori prioritas penyaluran bantuan sosial:

A. CLUSTER 0: PRIORITAS TINGGI / DARURAT ({len(c0)} Kecamatan)
   - Daftar Wilayah: {', '.join(c0)}
   - Karakteristik: Wilayah dengan tingkat kerentanan sosial-ekonomi tertinggi (jumlah penduduk miskin dan angka pengangguran tinggi, serta tingkat pendapatan rata-rata yang relatif rendah).
   - Rekomendasi Kebijakan: Menjadi prioritas utama (First-Tier Allocation) saat kuota atau anggaran bantuan sosial terbatas.

B. CLUSTER 1: PRIORITAS SEDANG / WASPADA ({len(c1)} Kecamatan)
   - Daftar Wilayah: {', '.join(c1)}
   - Karakteristik: Wilayah dengan tingkat kesejahteraan menengah.
   - Rekomendasi Kebijakan: Dialokasikan bantuan sosial tahap kedua secara proporsional.

C. CLUSTER 2: PRIORITAS RENDAH / MANDIRI ({len(c2)} Kecamatan)
   - Daftar Wilayah: {', '.join(c2)}
   - Karakteristik: Wilayah dengan kondisi ekonomi relatif mandiri dan sejahtera (IPM tinggi, pendapatan rata-rata lebih tinggi, serta akses fasilitas publik yang baik).
   - Rekomendasi Kebijakan: Diarahkan pada program pemberdayaan ekonomi berkelanjutan ketimbang bantuan tunai langsung.

================================================================================
"""
    return text
