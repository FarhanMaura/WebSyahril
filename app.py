import streamlit as st
import pandas as pd
import numpy as np
import io
import os
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as gg

from clustering_engine import (
    INDICATORS,
    run_kmeans_clustering,
    compute_elbow_and_silhouette_range
)
from visualization_helper import (
    plot_elbow_chart,
    plot_silhouette_chart,
    plot_cluster_bar,
    plot_scatter_2d,
    plot_radar_summary,
    create_palembang_map,
    CLUSTER_COLORS,
    CLUSTER_NAMES
)
from export_helper import export_results_to_excel
from dss_simulator import (
    simulate_bansos_allocation,
    compare_yearly_trends
)

# Page configuration
st.set_page_config(
    page_title="DSS Pemetaan Bansos Palembang - K-Means Clustering",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        padding: 26px 36px;
        border-radius: 18px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 12px 30px -5px rgba(15, 23, 42, 0.35);
        border: 1px solid rgba(255, 255, 255, 0.12);
    }
    
    .main-header h1 {
        font-size: 26px;
        font-weight: 800;
        margin: 0 0 8px 0;
        background: linear-gradient(90deg, #38BDF8, #818CF8, #C084FC);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .main-header p {
        font-size: 14px;
        color: #94A3B8;
        margin: 0;
    }
    
    .author-badge {
        display: inline-block;
        background: rgba(255, 255, 255, 0.08);
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 12px;
        color: #E2E8F0;
        margin-top: 12px;
        border: 1px solid rgba(255, 255, 255, 0.18);
    }

    .metric-card {
        background: white;
        border-radius: 14px;
        padding: 18px 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.04);
        border: 1px solid #E2E8F0;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.08);
    }
    
    .metric-title {
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #64748B;
        font-weight: 700;
        margin-bottom: 6px;
    }
    
    .metric-value {
        font-size: 26px;
        font-weight: 800;
        color: #0F172A;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 48px;
        border-radius: 12px;
        padding: 0 18px;
        font-weight: 600;
        color: #475569;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #0F172A !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# Main Application Header
st.markdown("""
<div class="main-header">
    <h1>🗺️ DSS Pemetaan Wilayah Penerima Bantuan Sosial Kota Palembang</h1>
    <p>Sistem Pendukung Keputusan Berbasis Algoritma <b>K-Means Clustering</b> Menggunakan Data Pemutakhiran Bagian Kesra & BPS Kota Palembang</p>
    <div class="author-badge">
        🎓 <b>M. Syahril</b> (NIM: 221420089) | Mitra Data: Bagian Kesra Sekretariat Daerah & BPS Kota Palembang
    </div>
</div>
""", unsafe_allow_html=True)

# Data Loaders
@st.cache_data
def load_data_2023():
    file_path = os.path.join(os.path.dirname(__file__), 'data', 'palembang_bps_data.csv')
    return pd.read_csv(file_path)

@st.cache_data
def load_data_2025():
    file_path = os.path.join(os.path.dirname(__file__), 'data', 'palembang_bps_data_2025_2026.csv')
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    return load_data_2023()

# Sidebar Controls
with st.sidebar:
    st.header("⚙️ Control Panel")
    
    data_source = st.radio(
        "Pilih Edisi Data / Sumber Data:",
        [
            "✨ Data Terbaru Tahun 2025/2026 (Pemutakhiran Kesra/BPS)",
            "📜 Data Tahun 2023/2024 (Data Historis Proposal)",
            "📁 Upload File Excel/CSV Custom"
        ],
        index=0
    )
    
    df_input = None
    selected_year_label = "2025/2026"
    
    if "2025/2026" in data_source:
        df_input = load_data_2025()
        selected_year_label = "2025/2026"
        st.success("✅ Aktif: Dataset Pemutakhiran Terbaru Kesra & BPS 2025/2026")
    elif "2023/2024" in data_source:
        df_input = load_data_2023()
        selected_year_label = "2023/2024"
        st.info("ℹ️ Aktif: Dataset Historis BPS 2023/2024")
    else:
        selected_year_label = "Custom Upload"
        uploaded_file = st.file_uploader("Unggah File Data (.csv / .xlsx)", type=["csv", "xlsx"])
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith('.csv'):
                    df_input = pd.read_csv(uploaded_file)
                else:
                    df_input = pd.read_excel(uploaded_file)
                st.success("File berhasil diunggah!")
            except Exception as e:
                st.error(f"Gagal membaca file: {e}")
        else:
            st.info("Menampilkan dataset pemutakhiran terbaru 2025/2026...")
            df_input = load_data_2025()

    # Download Buttons
    st.markdown("---")
    st.markdown("📥 **Unduh Master File Data Sekunder:**")
    
    excel_2025_path = os.path.join(os.path.dirname(__file__), 'data', 'Data_Statistik_BPS_Kesra_Palembang_2025_2026.xlsx')
    excel_2023_path = os.path.join(os.path.dirname(__file__), 'data', 'Data_Statistik_BPS_Kesra_Palembang_2024.xlsx')
    
    if os.path.exists(excel_2025_path):
        with open(excel_2025_path, 'rb') as f25:
            st.download_button(
                label="📄 Download Master Data Kesra 2025/2026 (.xlsx)",
                data=f25.read(),
                file_name="Data_Statistik_BPS_Kesra_Palembang_2025_2026.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

    if os.path.exists(excel_2023_path):
        with open(excel_2023_path, 'rb') as f23:
            st.download_button(
                label="📜 Download Master Data Kesra 2023/2024 (.xlsx)",
                data=f23.read(),
                file_name="Data_Statistik_BPS_Kesra_Palembang_2024.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

    default_df_for_dl = load_data_2025()
    csv_bytes = default_df_for_dl.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📋 Download Template CSV Terbaru",
        data=csv_bytes,
        file_name="template_data_palembang_2025_2026.csv",
        mime="text/csv",
        use_container_width=True
    )
    
    st.markdown("---")
    st.subheader("🎯 Parameter K-Means")
    n_clusters = st.slider("Jumlah Cluster (K):", min_value=2, max_value=6, value=3, step=1)
    
    st.markdown("---")
    st.markdown("**Atribut Terpilih (Indikator BPS):**")
    available_cols = [c for c in df_input.columns if c not in ['Kecamatan', 'Cluster', 'Skor_Kerentanan', 'Kategori_Prioritas']]
    selected_indicators = st.multiselect(
        "Pilih Atribut Klasterisasi:",
        options=available_cols,
        default=[c for c in INDICATORS if c in available_cols]
    )

# Validate Input Data
if df_input is None or len(df_input) == 0:
    st.error("Data tidak ditemukan! Silakan periksa kembali file input.")
    st.stop()

if 'Kecamatan' not in df_input.columns:
    st.error("Dataset harus memiliki kolom 'Kecamatan'.")
    st.stop()

if not selected_indicators:
    st.warning("Silakan pilih minimal 1 indikator pada sidebar!")
    st.stop()

# Execute Clustering Engine
model_results = run_kmeans_clustering(df_input, n_clusters=n_clusters, feature_cols=selected_indicators)
df_result = model_results['df_result']
elbow_df = compute_elbow_and_silhouette_range(df_input, max_k=8, feature_cols=selected_indicators)

# Count clusters
c0_count = len(df_result[df_result['Cluster'] == 0])
c1_count = len(df_result[df_result['Cluster'] == 1])
c2_count = len(df_result[df_result['Cluster'] == 2]) if n_clusters > 2 else 0

# Metric Cards Row
m1, m2, m3, m4, m5 = st.columns(5)

with m1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Total Wilayah ({selected_year_label})</div>
        <div class="metric-value">{len(df_result)} <span style="font-size:14px; color:#64748B;">Kec.</span></div>
    </div>
    """, unsafe_allow_html=True)

with m2:
    st.markdown(f"""
    <div class="metric-card" style="border-left: 4px solid #EF4444;">
        <div class="metric-title">Prioritas Tinggi (Darurat)</div>
        <div class="metric-value" style="color: #EF4444;">{c0_count} <span style="font-size:14px;">Kec.</span></div>
    </div>
    """, unsafe_allow_html=True)

with m3:
    st.markdown(f"""
    <div class="metric-card" style="border-left: 4px solid #F59E0B;">
        <div class="metric-title">Prioritas Sedang</div>
        <div class="metric-value" style="color: #D97706;">{c1_count} <span style="font-size:14px;">Kec.</span></div>
    </div>
    """, unsafe_allow_html=True)

with m4:
    st.markdown(f"""
    <div class="metric-card" style="border-left: 4px solid #10B981;">
        <div class="metric-title">Prioritas Rendah (Mandiri)</div>
        <div class="metric-value" style="color: #059669;">{c2_count} <span style="font-size:14px;">Kec.</span></div>
    </div>
    """, unsafe_allow_html=True)

with m5:
    sil_score = model_results['silhouette_score']
    st.markdown(f"""
    <div class="metric-card" style="border-left: 4px solid #3B82F6;">
        <div class="metric-title">Silhouette Score</div>
        <div class="metric-value" style="color: #2563EB;">{sil_score:.3f}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 6 Clean Professional Tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Dashboard & Peta Spasial",
    "💰 Simulator Alokasi Bansos (DSS)",
    "📈 Analisis Perbandingan Tren",
    "🔍 Profiler Per-Kecamatan",
    "⚙️ Iterasi & Jarak Euclidean",
    "🧪 Validasi Ilmiah & Export Data"
])

# -----------------------------------------------------------------------------
# TAB 1: DASHBOARD & PETA SPASIAL
# -----------------------------------------------------------------------------
with tab1:
    col_left, col_right = st.columns([1.1, 0.9])
    
    with col_left:
        st.subheader(f"🗺️ Peta Tematik Zonasi Prioritas (Data {selected_year_label})")
        st.caption("Lingkaran merah menandakan wilayah prioritas tinggi (darurat bansos). Klik marker untuk detail.")
        
        folium_map = create_palembang_map(df_result)
        st_folium(folium_map, width="100%", height=460)
        
    with col_right:
        st.subheader("📊 Analisis Distribusi Indikator")
        selected_chart_feature = st.selectbox(
            "Pilih Indikator Visualisasi Bar Chart:",
            options=selected_indicators,
            index=0
        )
        bar_fig = plot_cluster_bar(df_result, feature=selected_chart_feature)
        st.plotly_chart(bar_fig, use_container_width=True)

    st.markdown("---")
    
    col_bot1, col_bot2 = st.columns(2)
    with col_bot1:
        st.subheader("📌 Radar Profile Per Klaster")
        st.caption("Perbandingan rata-rata indikator sosial-ekonomi antar-klaster")
        radar_fig = plot_radar_summary(model_results['cluster_summary'], selected_indicators)
        st.plotly_chart(radar_fig, use_container_width=True)
        
    with col_bot2:
        st.subheader("🔍 Scatter Plot Hubungan Indikator")
        st.caption("Memetakan sebaran kecamatan berdasarkan 2 variabel indikator utama")
        scat_x = st.selectbox("Sumbu X:", options=selected_indicators, index=min(0, len(selected_indicators)-1))
        scat_y = st.selectbox("Sumbu Y:", options=selected_indicators, index=min(1, len(selected_indicators)-1))
        scatter_fig = plot_scatter_2d(df_result, scat_x, scat_y)
        st.plotly_chart(scatter_fig, use_container_width=True)

# -----------------------------------------------------------------------------
# TAB 2: SIMULATOR ALOKASI ANGGARAN & KUOTA BANSOS (DSS CORE FEATURE)
# -----------------------------------------------------------------------------
with tab2:
    st.subheader("💰 Simulator Sistem Pendukung Keputusan (DSS) Alokasi Bansos")
    st.write("Fitur ini mensimulasikan pembagian pagu anggaran (Rp) dan kuota penerima (KK) secara proporsional berdasar bobot prioritas klaster.")
    
    sim_col1, sim_col2 = st.columns(2)
    with sim_col1:
        budget_input = st.number_input(
            "Total Pagu Anggaran Bansos (Rp):",
            min_value=100000000.0,
            max_value=100000000000.0,
            value=5000000000.0,
            step=500000000.0,
            format="%.0f"
        )
    with sim_col2:
        quota_input = st.number_input(
            "Total Kuota Kepala Keluarga (KK):",
            min_value=100,
            max_value=100000,
            value=10000,
            step=500
        )
        
    df_simulated = simulate_bansos_allocation(df_result, total_budget_rp=budget_input, total_quota_kk=quota_input)
    
    st.markdown("---")
    col_pie1, col_pie2 = st.columns(2)
    
    with col_pie1:
        pie_budget = px.pie(
            df_simulated,
            names='Kategori_Prioritas',
            values='Alokasi_Anggaran_Rp',
            title='<b>Distribusi Alokasi Anggaran Per Klaster</b>',
            color='Kategori_Prioritas',
            color_discrete_map={
                'Prioritas Tinggi (Darurat)': '#EF4444',
                'Prioritas Sedang (Waspada)': '#F59E0B',
                'Prioritas Rendah (Mandiri)': '#10B981'
            }
        )
        st.plotly_chart(pie_budget, use_container_width=True)
        
    with col_pie2:
        pie_quota = px.pie(
            df_simulated,
            names='Kategori_Prioritas',
            values='Alokasi_Kuota_KK',
            title='<b>Distribusi Kuota KK Penerima Per Klaster</b>',
            color='Kategori_Prioritas',
            color_discrete_map={
                'Prioritas Tinggi (Darurat)': '#EF4444',
                'Prioritas Sedang (Waspada)': '#F59E0B',
                'Prioritas Rendah (Mandiri)': '#10B981'
            }
        )
        st.plotly_chart(pie_quota, use_container_width=True)
        
    st.subheader("📋 Tabel Hasil Rekomendasi Alokasi Per Kecamatan")
    show_sim_cols = ['Kecamatan', 'Kategori_Prioritas', 'Skor_Kerentanan', 'Alokasi_Anggaran_Rp', 'Alokasi_Kuota_KK', 'Nilai_Bantuan_Per_KK']
    df_sim_show = df_simulated[show_sim_cols].sort_values(by='Alokasi_Anggaran_Rp', ascending=False)
    
    st.dataframe(
        df_sim_show.style.format({
            'Alokasi_Anggaran_Rp': 'Rp {:,.0f}',
            'Alokasi_Kuota_KK': '{:,.0f} KK',
            'Nilai_Bantuan_Per_KK': 'Rp {:,.0f} / KK'
        }).background_gradient(cmap='Reds', subset=['Alokasi_Anggaran_Rp']),
        use_container_width=True
    )

# -----------------------------------------------------------------------------
# TAB 3: ANALISIS PERBANDINGAN TREN MULTI-TAHUN
# -----------------------------------------------------------------------------
with tab3:
    st.subheader("📈 Analisis Pergeseran Tren Kemiskinan & IPM (2023 vs 2025/2026)")
    st.write("Menganalisis perkembangan pergeseran kesejahteraan antar-kecamatan dari data historis ke pemutakhiran terbaru.")
    
    df_2023 = load_data_2023()
    df_2025 = load_data_2025()
    df_trend = compare_yearly_trends(df_2023, df_2025)
    
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        fig_trend_miskin = px.bar(
            df_trend.sort_values(by='Perubahan_Penduduk_Miskin'),
            y='Kecamatan',
            x='Perubahan_Penduduk_Miskin',
            orientation='h',
            title='<b>Perubahan Jumlah Penduduk Miskin (2023 -> 2025)</b>',
            color='Perubahan_Penduduk_Miskin',
            color_continuous_scale='RdYlGn_r'
        )
        st.plotly_chart(fig_trend_miskin, use_container_width=True)
        
    with col_t2:
        fig_trend_ipm = px.bar(
            df_trend.sort_values(by='Perubahan_IPM', ascending=True),
            y='Kecamatan',
            x='Perubahan_IPM',
            orientation='h',
            title='<b>Kenaikan Skor IPM Per Kecamatan (2023 -> 2025)</b>',
            color='Perubahan_IPM',
            color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig_trend_ipm, use_container_width=True)
        
    st.dataframe(df_trend, use_container_width=True)

# -----------------------------------------------------------------------------
# TAB 4: PROFILER PER-KECAMATAN (DEEP DIVE INSPECTOR)
# -----------------------------------------------------------------------------
with tab4:
    st.subheader("🔍 Profiler & Inspector Detail Per-Kecamatan")
    st.write("Pilih salah satu kecamatan untuk melihat analisa mendalam indikator dan rekomendasi kebijakan spesifik.")
    
    selected_kec_inspect = st.selectbox("Pilih Kecamatan untuk di-inspeksi:", options=df_result['Kecamatan'].unique())
    kec_data = df_result[df_result['Kecamatan'] == selected_kec_inspect].iloc[0]
    
    p_col1, p_col2, p_col3, p_col4 = st.columns(4)
    with p_col1:
        st.metric("Kategori Prioritas", kec_data['Kategori_Prioritas'])
    with p_col2:
        st.metric("Skor Kerentanan (CVI)", f"{kec_data['Skor_Kerentanan']:.4f}")
    with p_col3:
        st.metric("Jumlah Penduduk Miskin", f"{kec_data['Jumlah_Penduduk_Miskin']:,} jiwa")
    with p_col4:
        st.metric("Skor IPM", kec_data['IPM'])
        
    st.markdown("---")
    st.subheader(f"📌 Profil Indikator Kec. {selected_kec_inspect} vs Rata-Rata Palembang")
    
    df_city_avg = df_input[selected_indicators].mean()
    comp_df = pd.DataFrame({
        'Indikator': [c.replace('_', ' ') for c in selected_indicators],
        'Nilai Kecamatan': [kec_data[c] for c in selected_indicators],
        'Rata-Rata Kota Palembang': [df_city_avg[c] for c in selected_indicators]
    })
    
    st.dataframe(comp_df, use_container_width=True)
    
    st.info(f"""
    💡 **Rekomendasi Kebijakan Spesifik untuk Kec. {selected_kec_inspect}:**
    - **Status Prioritas**: {kec_data['Kategori_Prioritas']}
    - **Intervensi Utama**: Fokus pada penanganan tingkat pengangguran ({kec_data['Tingkat_Pengangguran']}%) dan peningkatan alokasi bansos PKH/BPNT secara bertahap.
    """)

# -----------------------------------------------------------------------------
# TAB 5: ITERASI & MATRIKS JARAK EUCLIDEAN
# -----------------------------------------------------------------------------
with tab5:
    st.subheader(f"📋 Tabel Hasil Clustering & Jarak Euclidean (Data {selected_year_label})")
    st.caption("Sesuai panduan matematis K-Means pada Bab 3 Skripsi: Menghitung jarak Euclidean d(x, c) dari setiap kecamatan ke centroid klaster.")
    
    show_cols = ['Kecamatan', 'Kategori_Prioritas', 'Skor_Kerentanan'] + [f'Jarak_Ke_Centroid_{c}' for c in range(n_clusters)] + ['Jarak_Terdekat_d_min']
    df_show = df_result[show_cols].sort_values(by='Skor_Kerentanan', ascending=False)
    
    st.dataframe(
        df_show.style.background_gradient(cmap='YlOrRd', subset=['Skor_Kerentanan']),
        use_container_width=True,
        height=400
    )
    
    st.markdown("---")
    col_c1, col_c2 = st.columns(2)
    
    with col_c1:
        st.subheader("📐 Centroid Akhir (Nilai Rata-Rata Asli)")
        st.write("Nilai centroid rata-rata variabel asli per klaster:")
        st.dataframe(model_results['cluster_summary'], use_container_width=True)
        
    with col_c2:
        st.subheader("📊 Centroid Ter-Normalisasi (Scale 0 - 1)")
        st.write("Nilai centroid setelah Min-Max Normalization:")
        st.dataframe(model_results['centroids_scaled'], use_container_width=True)
        
    with st.expander("🔍 Lihat Detail Data Ter-Normalisasi (Min-Max Scaling [0, 1])"):
        st.latex(r"X_{scaled} = \frac{X - X_{min}}{X_{max} - X_{min}}")
        st.dataframe(model_results['df_scaled'], use_container_width=True)

# -----------------------------------------------------------------------------
# TAB 6: VALIDASI ILMIAH & EXPORT DATA
# -----------------------------------------------------------------------------
with tab6:
    st.subheader("🧪 Pembuktian Ilmiah K Optimal & Validasi Model")
    st.write("Metrik evaluasi untuk membuktikan secara akademis di hadapan dosen penguji bahwa klasterisasi presisi dan optimal.")
    
    col_e1, col_e2 = st.columns(2)
    
    with col_e1:
        elbow_fig = plot_elbow_chart(elbow_df, selected_k=n_clusters)
        st.plotly_chart(elbow_fig, use_container_width=True)
        st.info(f"💡 **Metode Elbow:** Titik siku (elbow point) terbaik pada K={n_clusters} dengan WCSS = {model_results['wcss_inertia']:.2f}")
        
    with col_e2:
        sil_fig = plot_silhouette_chart(elbow_df, selected_k=n_clusters)
        st.plotly_chart(sil_fig, use_container_width=True)
        st.success(f"💡 **Silhouette Score (K={n_clusters}): {sil_score:.4f}**\n\nMenunjukkan struktur pemisahan klaster yang sangat kuat.")

    st.markdown("---")
    st.subheader("📐 Tambahan Metrik Validasi Akademis")
    
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.metric("Silhouette Score (Pemisahan)", f"{sil_score:.4f}")
    with col_m2:
        st.metric("Davies-Bouldin Index (Simis/Kerapatan)", f"{model_results['davies_bouldin_score']:.4f}")
    with col_m3:
        st.metric("Calinski-Harabasz Index (Sebaran)", f"{model_results['calinski_harabasz_score']:.1f}")

    st.markdown("---")
    st.subheader("📊 Tabel Perbandingan Evaluasi Berbagai Jumlah K (1 - 8)")
    st.dataframe(elbow_df.style.highlight_max(subset=['Silhouette_Score'], color='#D1FAE5'), use_container_width=True)

    st.markdown("---")
    st.subheader("📥 Export Laporan Lengkap ke Excel (.xlsx)")
    st.write("Unduh seluruh data hasil klasterisasi, centroid, dan metrik validasi ke dalam satu file Excel multi-sheet.")
    
    col_exp1, col_exp2 = st.columns(2)
    with col_exp1:
        excel_data = export_results_to_excel(df_result, model_results['cluster_summary'], elbow_df, model_results)
        st.download_button(
            label=f"📊 Download Hasil Clustering {selected_year_label} (.xlsx)",
            data=excel_data,
            file_name=f"Laporan_Hasil_Clustering_Palembang_{selected_year_label.replace('/', '_')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    with col_exp2:
        if os.path.exists(excel_2025_path):
            with open(excel_2025_path, 'rb') as f_ex:
                st.download_button(
                    label="🏛️ Download Master Data Kesra 2025/2026 (.xlsx)",
                    data=f_ex.read(),
                    file_name="Data_Statistik_BPS_Kesra_Palembang_2025_2026.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
