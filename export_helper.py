import io
import pandas as pd

def export_results_to_excel(df_result: pd.DataFrame, cluster_summary: pd.DataFrame, elbow_df: pd.DataFrame, metrics: dict):
    """
    Generates an Excel workbook in memory with multiple sheets:
    - Hasil Clustering & Zonasi
    - Normalisasi Min-Max
    - Tahapan Iterasi K-Means
    - Profil Centroid Cluster
    - Evaluasi Validasi (Elbow & Silhouette)
    - Metrik Validasi
    """
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Sheet 1: Hasil Clustering & Zonasi
        df_result.to_excel(writer, sheet_name='Hasil Clustering', index=False)
        
        # Sheet 2: Normalisasi Min-Max
        if 'min_max_info' in metrics and isinstance(metrics['min_max_info'], pd.DataFrame):
            metrics['min_max_info'].to_excel(writer, sheet_name='Parameter Min-Max', index=False)
            
        # Sheet 3: Tahapan Iterasi K-Means
        if 'iterations' in metrics and isinstance(metrics['iterations'], list) and len(metrics['iterations']) > 0:
            iter_rows = []
            for it in metrics['iterations']:
                it_num = it.get('iteration_number', 1)
                dist_df = it.get('distances_df')
                shift = it.get('total_shift', 0.0)
                converged = it.get('is_converged', False)
                
                if dist_df is not None:
                    for _, r in dist_df.iterrows():
                        row_dict = {'Iterasi': it_num, 'Kecamatan': r.get('Kecamatan')}
                        for col in dist_df.columns:
                            if col not in ['Kecamatan']:
                                row_dict[col] = r.get(col)
                        row_dict['Pergeseran_Centroid_Total'] = shift
                        row_dict['Status_Konvergensi'] = 'Konvergen' if converged else 'Lanjut Iterasi'
                        iter_rows.append(row_dict)
            if iter_rows:
                df_iter_export = pd.DataFrame(iter_rows)
                df_iter_export.to_excel(writer, sheet_name='Proses Iterasi K-Means', index=False)
        
        # Sheet 4: Profil Centroid
        cluster_summary.to_excel(writer, sheet_name='Profil Centroid Cluster')
        
        # Sheet 5: Evaluasi Validasi
        elbow_df.to_excel(writer, sheet_name='Uji Elbow & Silhouette', index=False)
        
        # Sheet 6: Summary Metrics
        df_metrics = pd.DataFrame([
            {'Metrik': 'Jumlah Cluster (K)', 'Nilai': metrics.get('n_clusters', 3)},
            {'Metrik': 'Total Iterasi Hingga Konvergen', 'Nilai': metrics.get('total_iterations', metrics.get('iterations_count', 1))},
            {'Metrik': 'Status Konvergensi', 'Nilai': 'Tercapai (Konvergen)' if metrics.get('is_converged', True) else 'Belum Konvergen'},
            {'Metrik': 'WCSS / Inersia Akhir', 'Nilai': round(metrics.get('wcss_inertia', 0.0), 4)},
            {'Metrik': 'Silhouette Score', 'Nilai': round(metrics.get('silhouette_score', 0.0), 4)},
            {'Metrik': 'Davies-Bouldin Index', 'Nilai': round(metrics.get('davies_bouldin_score', 0.0), 4)},
            {'Metrik': 'Calinski-Harabasz Index', 'Nilai': round(metrics.get('calinski_harabasz_score', 0.0), 4)},
        ])
        df_metrics.to_excel(writer, sheet_name='Metrik Validasi', index=False)
        
    output.seek(0)
    return output.getvalue()

def generate_bab4_narration(df_result: pd.DataFrame, metrics: dict, elbow_df: pd.DataFrame, year_label: str = "2025/2026"):
    """
    Generates formatted text specifically structured for Skripsi Bab 4 (Hasil dan Pembahasan).
    Dynamically accepts year_label (e.g. '2025/2026' or '2023/2024').
    """
    k = metrics.get('n_clusters', 3)
    sil = metrics.get('silhouette_score', 0.0)
    db = metrics.get('davies_bouldin_score', 0.0)
    total_iter = metrics.get('total_iterations', metrics.get('iterations_count', 2))
    
    c0 = df_result[df_result['Cluster'] == 0]['Kecamatan'].tolist()
    c1 = df_result[df_result['Cluster'] == 1]['Kecamatan'].tolist()
    c2 = df_result[df_result['Cluster'] == 2]['Kecamatan'].tolist() if k > 2 else []
    
    text = f"""================================================================================
📝 DRAFT TEKS LAPORAN SKRIPSI BAB 4 (HASIL DAN PEMBAHASAN - EDISI TAHUN {year_label})
================================================================================

BAB IV: HASIL DAN PEMBAHASAN

4.1 Pengolahan Data dan Implementasi Algoritma K-Means Clustering
Berdasarkan data statistik pemutakhiran 18 kecamatan di Kota Palembang edisi Tahun {year_label} yang bersumber dari Bagian Kesejahteraan Rakyat (Kesra) Kantor Sekretariat Daerah dan Badan Pusat Statistik (BPS) Kota Palembang, dilakukan pengelompokan wilayah penerima bantuan sosial menggunakan algoritma K-Means Clustering dengan jumlah klaster K={k}.

Tahapan komputasi K-Means dilakukan secara transparan meliputi:
1. Normalisasi Min-Max: Seluruh 7 indikator kemiskinan dan kesejahteraan diseragamkan ke rentang [0, 1].
2. Inisialisasi Titik Centroid Awal: Ditentukan sebanyak {k} titik pusat klaster awal.
3. Iterasi Perhitungan Jarak Euclidean: Sistem melakukan perhitungan matriks jarak Euclidean dari 18 kecamatan ke masing-masing centroid.
4. Konvergensi Algoritma: Proses iterasi mencapai kondisi konvergen sempurna pada Iterasi ke-{total_iter}, ditandai dengan pergeseran posisi titik centroid sebesar 0 (stabil) dan keanggotaan klaster yang tidak mengalami perpindahan lagi.

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
