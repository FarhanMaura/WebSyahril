import streamlit as st
import pandas as pd
import numpy as np
import io
import os
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as gg

from database import (
    init_database,
    fetch_indicator_data_from_db,
    save_clustering_results_to_db,
    save_simulation_results_to_db,
    log_export_to_db,
    get_current_db_status
)
from auth_helper import (
    init_auth_session,
    render_login_page,
    render_sidebar_user_badge,
    render_pimpinan_role_explainer
)
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
from dss_simulator import simulate_bansos_allocation

# Page configuration
st.set_page_config(
    page_title="DSS Pemetaan Bansos Palembang - K-Means Clustering",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Database and Auth Session (with persistent refresh restoration)
init_database()
init_auth_session()

# Global Custom CSS Styling
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
}

.main-header {
    background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
    padding: 22px 30px;
    border-radius: 16px;
    color: white;
    margin-bottom: 18px;
    box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.35);
    border: 1px solid rgba(255, 255, 255, 0.12);
}

.main-header h1 {
    font-size: 22px;
    font-weight: 800;
    margin: 0 0 4px 0;
    background: linear-gradient(90deg, #38BDF8, #818CF8, #C084FC);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.main-header p {
    font-size: 13px;
    color: #94A3B8;
    margin: 0;
}

.author-badge {
    display: inline-block;
    background: rgba(255, 255, 255, 0.08);
    padding: 5px 14px;
    border-radius: 20px;
    font-size: 12px;
    color: #E2E8F0;
    margin-top: 8px;
    border: 1px solid rgba(255, 255, 255, 0.18);
}

.role-banner-admin {
    background: linear-gradient(90deg, #1E3A8A 0%, #2563EB 100%);
    color: white;
    padding: 12px 18px;
    border-radius: 12px;
    font-weight: 700;
    font-size: 13px;
    margin-bottom: 16px;
    box-shadow: 0 4px 15px rgba(37, 99, 235, 0.2);
}

.role-banner-pimpinan {
    background: linear-gradient(90deg, #064E3B 0%, #059669 100%);
    color: white;
    padding: 12px 18px;
    border-radius: 12px;
    font-weight: 700;
    font-size: 13px;
    margin-bottom: 16px;
    box-shadow: 0 4px 15px rgba(5, 150, 105, 0.2);
}

.metric-card {
    background: white;
    border-radius: 14px;
    padding: 16px 18px;
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
    margin-bottom: 4px;
}

.metric-value {
    font-size: 24px;
    font-weight: 800;
    color: #0F172A;
}

.policy-card {
    background: #FFFFFF;
    border-radius: 14px;
    padding: 18px 20px;
    border: 1px solid #E2E8F0;
    margin-bottom: 14px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.03);
}

.stTabs [data-baseweb="tab-list"] {
    gap: 6px;
}

.stTabs [data-baseweb="tab"] {
    height: 46px;
    border-radius: 12px;
    padding: 0 16px;
    font-weight: 600;
    color: #475569;
}

.stTabs [aria-selected="true"] {
    background-color: #0F172A !important;
    color: white !important;
}
</style>""", unsafe_allow_html=True)

# Main Application Header
st.markdown("""<div class="main-header">
<h1>🗺️ DSS Pemetaan Wilayah Penerima Bantuan Sosial Kota Palembang</h1>
<p>Sistem Pendukung Keputusan Berbasis Algoritma <b>K-Means Clustering</b> Menggunakan Data Resmi BPS & Bagian Kesra Kota Palembang</p>
<div class="author-badge">
🎓 <b>M. Syahril</b> (NIM: 221420089) | Teknik Informatika Universitas Bina Darma Palembang
</div>
</div>""", unsafe_allow_html=True)

# Check Authentication
if not st.session_state.get('authenticated', False):
    render_login_page()
    st.stop()

# Authenticated User Info
current_user = st.session_state.get('user_info') or {}
user_role = current_user.get('role', 'Admin / Petugas Kesra')
is_admin = 'Admin' in user_role
user_display_name = current_user.get('nama_lengkap', 'User')

# Primary Dataset Loader (Direct & Fresh)
def load_primary_data():
    try:
        df_db = fetch_indicator_data_from_db(tahun=2025)
        if len(df_db) > 0:
            return df_db
    except Exception:
        pass
    file_path = os.path.join(os.path.dirname(__file__), 'data', 'palembang_bps_data_2025_2026.csv')
    if os.path.exists(file_path):
        df_csv = pd.read_csv(file_path)
        for col in INDICATORS:
            if col in df_csv.columns:
                df_csv[col] = pd.to_numeric(df_csv[col], errors='coerce')
        return df_csv
    file_path_alt = os.path.join(os.path.dirname(__file__), 'data', 'palembang_bps_data.csv')
    df_alt = pd.read_csv(file_path_alt)
    for col in INDICATORS:
        if col in df_alt.columns:
            df_alt[col] = pd.to_numeric(df_alt[col], errors='coerce')
    return df_alt

# Sidebar Controls
with st.sidebar:
    st.header("⚙️ Control Panel")
    render_sidebar_user_badge()
    
    st.markdown("---")
    st.subheader("📂 Sumber Data")
    
    data_mode = st.radio(
        "Pilihan Dataset:",
        [
            "📊 Dataset Resmi 18 Kecamatan Palembang (Terkini)",
            "📁 Unggah File Kustom (.csv / .xlsx)"
        ],
        index=0
    )
    
    df_input = None
    if "Resmi" in data_mode:
        df_input = load_primary_data()
        st.success("✅ Terkoneksi: Dataset Resmi 18 Kecamatan")
    else:
        uploaded_file = st.file_uploader("Unggah File Data:", type=["csv", "xlsx"])
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
            st.info("Memuat dataset bawaan...")
            df_input = load_primary_data()

    st.markdown("---")
    st.subheader("🎯 Parameter K-Means")
    n_clusters = st.slider("Jumlah Cluster (K):", min_value=2, max_value=6, value=3, step=1)
    
    available_cols = [c for c in df_input.columns if c not in ['Kecamatan', 'Cluster', 'Skor_Kerentanan', 'Kategori_Prioritas']]
    selected_indicators = st.multiselect(
        "Atribut Indikator Klasterisasi:",
        options=available_cols,
        default=[c for c in INDICATORS if c in available_cols]
    )

    st.markdown("---")
    st.markdown("📥 **Unduh File Master:**")
    excel_path = os.path.join(os.path.dirname(__file__), 'data', 'Data_Statistik_BPS_Kesra_Palembang_2025_2026.xlsx')
    if os.path.exists(excel_path):
        with open(excel_path, 'rb') as f_ex:
            st.download_button(
                label="📄 Master Data Kesra Palembang (.xlsx)",
                data=f_ex.read(),
                file_name="Data_Statistik_BPS_Kesra_Palembang.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

    default_csv = load_primary_data().to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📋 Download Template CSV",
        data=default_csv,
        file_name="template_data_palembang.csv",
        mime="text/csv",
        use_container_width=True
    )
    
    st.markdown("---")
    st.caption(f"Backend DB: {get_current_db_status()}")

# Validate Input Data
if df_input is None or len(df_input) == 0:
    st.error("Data tidak ditemukan! Silakan periksa kembali dataset.")
    st.stop()

if 'Kecamatan' not in df_input.columns:
    st.error("Dataset wajib memiliki kolom 'Kecamatan'.")
    st.stop()

if not selected_indicators:
    st.warning("Pilih minimal 1 indikator pada panel samping!")
    st.stop()

# Execute Clustering Engine
model_results = run_kmeans_clustering(df_input, n_clusters=n_clusters, feature_cols=selected_indicators)
df_result = model_results['df_result']
elbow_df = compute_elbow_and_silhouette_range(df_input, max_k=8, feature_cols=selected_indicators)

# Count clusters
c0_count = len(df_result[df_result['Cluster'] == 0])
c1_count = len(df_result[df_result['Cluster'] == 1])
c2_count = len(df_result[df_result['Cluster'] == 2]) if n_clusters > 2 else 0
sil_score = model_results['silhouette_score']

# Role Banner
if is_admin:
    st.markdown("""<div class="role-banner-admin">
👨‍💻 <b>PORTAL ADMIN / PETUGAS KESRA</b> &mdash; Wewenang: Pengolahan Dataset, Eksekusi K-Means, Matriks Euclidean & Uji Validasi Ilmiah
</div>""", unsafe_allow_html=True)
else:
    st.markdown("""<div class="role-banner-pimpinan">
🏛️ <b>PORTAL PIMPINAN / PENGAMBIL KEPUTUSAN</b> &mdash; Wewenang: Dashboard Eksekutif, Peta Spasial, Simulator Alokasi Anggaran DSS & Laporan Resmi
</div>""", unsafe_allow_html=True)
    render_pimpinan_role_explainer()

# Key Metric Cards Row
m1, m2, m3, m4, m5 = st.columns(5)

with m1:
    st.markdown(f"""<div class="metric-card">
<div class="metric-title">Total Wilayah</div>
<div class="metric-value">{len(df_result)} <span style="font-size:13px; color:#64748B;">Kecamatan</span></div>
</div>""", unsafe_allow_html=True)

with m2:
    st.markdown(f"""<div class="metric-card" style="border-left: 4px solid #EF4444;">
<div class="metric-title">Prioritas Tinggi (Darurat)</div>
<div class="metric-value" style="color: #EF4444;">{c0_count} <span style="font-size:13px;">Kec.</span></div>
</div>""", unsafe_allow_html=True)

with m3:
    st.markdown(f"""<div class="metric-card" style="border-left: 4px solid #F59E0B;">
<div class="metric-title">Prioritas Sedang</div>
<div class="metric-value" style="color: #D97706;">{c1_count} <span style="font-size:13px;">Kec.</span></div>
</div>""", unsafe_allow_html=True)

with m4:
    st.markdown(f"""<div class="metric-card" style="border-left: 4px solid #10B981;">
<div class="metric-title">Prioritas Rendah (Mandiri)</div>
<div class="metric-value" style="color: #059669;">{c2_count} <span style="font-size:13px;">Kec.</span></div>
</div>""", unsafe_allow_html=True)

with m5:
    st.markdown(f"""<div class="metric-card" style="border-left: 4px solid #3B82F6;">
<div class="metric-title">Silhouette Score</div>
<div class="metric-value" style="color: #2563EB;">{sil_score:.3f}</div>
</div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# =============================================================================
# ROLE 1: ADMIN / PETUGAS KESRA VIEW
# =============================================================================
if is_admin:
    adm_tab1, adm_tab2, adm_tab3, adm_tab4, adm_tab5, adm_tab6 = st.tabs([
        "📁 1. Manajemen Dataset",
        "🚀 2. Eksekusi K-Means",
        "📐 3. Iterasi & Matriks Euclidean",
        "🧪 4. Uji Validasi Ilmiah",
        "🗺️ 5. Peta Geospasial",
        "📊 6. Radar & Sebaran Klaster"
    ])

    # ADMIN TAB 1: DATASET MANAGEMENT
    with adm_tab1:
        st.subheader("📁 Data Statistik 18 Kecamatan Kota Palembang")
        st.caption("Data sekunder indikator kemiskinan dan kesejahteraan sosial BPS & Bagian Kesra Kota Palembang.")
        st.dataframe(df_input, use_container_width=True)
        
        st.markdown("---")
        st.subheader("📊 Statistik Deskriptif Variabel Terpilih")
        st.dataframe(df_input[selected_indicators].describe().T.style.format("{:,.2f}"), use_container_width=True)

    # ADMIN TAB 2: K-MEANS ENGINE
    with adm_tab2:
        st.subheader("🚀 Engine Pemrosesan K-Means Clustering")
        st.write("Hasil pengelompokan 18 kecamatan menggunakan algoritma K-Means dengan pembobotan *Composite Vulnerability Index (CVI)*.")
        
        col_act1, col_act2, col_act3 = st.columns([1, 1, 1.5])
        with col_act1:
            st.info(f"**Jumlah Klaster (K)**: {n_clusters}")
        with col_act2:
            st.info(f"**Iterasi Konvergensi**: {model_results['iterations_count']} kali")
        with col_act3:
            if st.button("💾 Simpan Hasil Klasterisasi ke Database", type="primary", use_container_width=True):
                save_clustering_results_to_db(df_result, "Terkini", user_display_name)
                st.success("✅ Hasil klasterisasi berhasil diarsipkan ke tabel `hasil_clustering` di database!")

        st.markdown("---")
        st.subheader("📋 Tabel Hasil Klasterisasi & Urutan Prioritas")
        cols_to_show = ['Kecamatan', 'Cluster', 'Kategori_Prioritas', 'Skor_Kerentanan'] + selected_indicators
        st.dataframe(
            df_result[cols_to_show].sort_values(by='Skor_Kerentanan', ascending=False)
            .style.background_gradient(cmap='YlOrRd', subset=['Skor_Kerentanan']),
            use_container_width=True
        )

    # ADMIN TAB 3: EUCLIDEAN DISTANCE MATRIX
    with adm_tab3:
        st.subheader("📐 Transparansi Matematis: Matriks Jarak Euclidean d(x, c)")
        st.caption("Menghitung jarak Euclidean multidimensi dari setiap vektor kecamatan terhadap setiap titik centroid klaster.")
        
        show_cols = ['Kecamatan', 'Kategori_Prioritas', 'Skor_Kerentanan'] + [f'Jarak_Ke_Centroid_{c}' for c in range(n_clusters)] + ['Jarak_Terdekat_d_min']
        df_show = df_result[show_cols].sort_values(by='Skor_Kerentanan', ascending=False)
        st.dataframe(
            df_show.style.background_gradient(cmap='YlOrRd', subset=['Skor_Kerentanan']),
            use_container_width=True,
            height=380
        )
        
        st.markdown("---")
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.subheader("📍 Nilai Centroid Akhir (Skala Asli)")
            st.dataframe(model_results['cluster_summary'], use_container_width=True)
        with col_c2:
            st.subheader("📊 Nilai Centroid Ter-Normalisasi (0 - 1)")
            st.dataframe(model_results['centroids_scaled'], use_container_width=True)

        with st.expander("🔍 Lihat Detail Normalisasi Min-Max [0, 1]"):
            st.latex(r"X_{scaled} = \frac{X - X_{min}}{X_{max} - X_{min}}")
            st.dataframe(model_results['df_scaled'], use_container_width=True)

    # ADMIN TAB 4: SCIENTIFIC VALIDATION
    with adm_tab4:
        st.subheader("🧪 Pembuktian Ilmiah K Optimal & Validasi Model")
        st.write("Metrik evaluasi matematis untuk membuktikan struktur pemisahan klaster optimal.")
        
        col_e1, col_e2 = st.columns(2)
        with col_e1:
            elbow_fig = plot_elbow_chart(elbow_df, selected_k=n_clusters)
            st.plotly_chart(elbow_fig, use_container_width=True)
            st.info(f"💡 **Metode Elbow:** Titik siku terbaik pada K={n_clusters} dengan WCSS = {model_results['wcss_inertia']:.2f}")
            
        with col_e2:
            sil_fig = plot_silhouette_chart(elbow_df, selected_k=n_clusters)
            st.plotly_chart(sil_fig, use_container_width=True)
            st.success(f"💡 **Silhouette Score (K={n_clusters}): {sil_score:.4f}**\n\nMenunjukkan struktur pemisahan klaster yang kuat.")

        st.markdown("---")
        st.subheader("📐 Ringkasan 3 Metrik Validasi Akademis")
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.metric("Silhouette Score (Pemisahan)", f"{sil_score:.4f}")
        with col_m2:
            st.metric("Davies-Bouldin Index (Kerapatan)", f"{model_results['davies_bouldin_score']:.4f}")
        with col_m3:
            st.metric("Calinski-Harabasz Index (Sebaran)", f"{model_results['calinski_harabasz_score']:.1f}")

        st.markdown("---")
        st.subheader("📊 Tabel Evaluasi Rentang K (1 - 8)")
        st.dataframe(elbow_df.style.highlight_max(subset=['Silhouette_Score'], color='#D1FAE5'), use_container_width=True)

    # ADMIN TAB 5: SPATIAL MAP
    with adm_tab5:
        col_m1, col_m2 = st.columns([1.2, 0.8])
        with col_m1:
            st.subheader("🗺️ Peta Tematik Geospasial Palembang")
            folium_map = create_palembang_map(df_result)
            st_folium(folium_map, width="100%", height=480)
        with col_m2:
            st.subheader("📊 Distribusi Indikator")
            sel_feat = st.selectbox("Pilih Indikator Visualisasi:", options=selected_indicators, index=0)
            st.plotly_chart(plot_cluster_bar(df_result, feature=sel_feat), use_container_width=True)

    # ADMIN TAB 6: RADAR & SCATTER
    with adm_tab6:
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            st.subheader("📌 Radar Profile Antar Klaster")
            st.plotly_chart(plot_radar_summary(model_results['cluster_summary'], selected_indicators), use_container_width=True)
        with col_r2:
            st.subheader("🔍 Scatter Plot Hubungan Indikator")
            scat_x = st.selectbox("Sumbu X:", options=selected_indicators, index=min(0, len(selected_indicators)-1))
            scat_y = st.selectbox("Sumbu Y:", options=selected_indicators, index=min(1, len(selected_indicators)-1))
            st.plotly_chart(plot_scatter_2d(df_result, scat_x, scat_y), use_container_width=True)

# =============================================================================
# ROLE 2: PIMPINAN / PENGAMBIL KEPUTUSAN VIEW
# =============================================================================
else:
    pim_tab1, pim_tab2, pim_tab3, pim_tab4, pim_tab5, pim_tab6 = st.tabs([
        "🏛️ 1. Dashboard Eksekutif",
        "🗺️ 2. Peta Spasial Palembang",
        "💰 3. Simulator Alokasi Bansos (DSS)",
        "🔍 4. Profiler Per-Kecamatan",
        "📊 5. Karakteristik Klaster",
        "📥 6. Unduh Laporan Resmi"
    ])

    # PIMPINAN TAB 1: EXECUTIVE DASHBOARD
    with pim_tab1:
        st.subheader("🏛️ Ringkasan Zonasi & Rekomendasi Kebijakan Bansos")
        
        col_pol1, col_pol2, col_pol3 = st.columns(3)
        c0_list = df_result[df_result['Cluster'] == 0]['Kecamatan'].tolist()
        c1_list = df_result[df_result['Cluster'] == 1]['Kecamatan'].tolist()
        c2_list = df_result[df_result['Cluster'] == 2]['Kecamatan'].tolist()
        
        with col_pol1:
            st.markdown(f"""<div class="policy-card" style="border-top: 5px solid #EF4444;">
<div style="font-size: 16px; font-weight: 800; color: #EF4444; margin-bottom: 6px;">
🔴 Prioritas Tinggi / Darurat ({len(c0_list)} Kecamatan)
</div>
<div style="font-size: 13px; color: #1E293B; margin-bottom: 10px;">
<b>Wilayah:</b> {', '.join(c0_list)}
</div>
<div style="font-size: 12px; color: #64748B; line-height: 1.5;">
<b>Rekomendasi Kebijakan:</b> Alokasikan pagu 60%. Penyaluran Bansos Tunai Utama (PKH/BPNT), sembako darurat, dan padat karya tunai.
</div>
</div>""", unsafe_allow_html=True)
            
        with col_pol2:
            st.markdown(f"""<div class="policy-card" style="border-top: 5px solid #F59E0B;">
<div style="font-size: 16px; font-weight: 800; color: #D97706; margin-bottom: 6px;">
🟡 Prioritas Sedang / Waspada ({len(c1_list)} Kecamatan)
</div>
<div style="font-size: 13px; color: #1E293B; margin-bottom: 10px;">
<b>Wilayah:</b> {', '.join(c1_list)}
</div>
<div style="font-size: 12px; color: #64748B; line-height: 1.5;">
<b>Rekomendasi Kebijakan:</b> Alokasikan pagu 30%. Bantuan kuota bersyarat, pelatihan keterampilan vokasi, dan pembinaan UMKM.
</div>
</div>""", unsafe_allow_html=True)
            
        with col_pol3:
            st.markdown(f"""<div class="policy-card" style="border-top: 5px solid #10B981;">
<div style="font-size: 16px; font-weight: 800; color: #059669; margin-bottom: 6px;">
🟢 Prioritas Rendah / Mandiri ({len(c2_list)} Kecamatan)
</div>
<div style="font-size: 13px; color: #1E293B; margin-bottom: 10px;">
<b>Wilayah:</b> {', '.join(c2_list)}
</div>
<div style="font-size: 12px; color: #64748B; line-height: 1.5;">
<b>Rekomendasi Kebijakan:</b> Alokasikan pagu 10%. Program pemberdayaan kemandirian ekonomi & alokasi tanggap darurat terbatas.
</div>
</div>""", unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("📊 Urutan Wilayah Berdasarkan Skor Kerentanan Tertinggi (CVI)")
        fig_cvi_rank = px.bar(
            df_result.sort_values(by='Skor_Kerentanan', ascending=True),
            y='Kecamatan',
            x='Skor_Kerentanan',
            orientation='h',
            color='Kategori_Prioritas',
            color_discrete_map={
                'Prioritas Tinggi (Darurat)': '#EF4444',
                'Prioritas Sedang (Waspada)': '#F59E0B',
                'Prioritas Rendah (Mandiri)': '#10B981'
            },
            title='<b>Tingkat Kerentanan Komposit (CVI) 18 Kecamatan Kota Palembang</b>'
        )
        st.plotly_chart(fig_cvi_rank, use_container_width=True)

    # PIMPINAN TAB 2: SPATIAL MAP
    with pim_tab2:
        col_m_left, col_m_right = st.columns([1.2, 0.8])
        with col_m_left:
            st.subheader("🗺️ Peta Tematik Geospasial Palembang")
            st.caption("Peta interaktif berbasis koordinat 18 kecamatan. Klik lingkaran marker untuk rincian data.")
            folium_map = create_palembang_map(df_result)
            st_folium(folium_map, width="100%", height=480)
            
        with col_m_right:
            st.subheader("📊 Analisis Distribusi Indikator")
            sel_f = st.selectbox("Pilih Indikator Ditampilkan:", options=selected_indicators, index=0)
            st.plotly_chart(plot_cluster_bar(df_result, feature=sel_f), use_container_width=True)

    # PIMPINAN TAB 3: DSS BUDGET & QUOTA SIMULATOR
    with pim_tab3:
        st.subheader("💰 Simulator Sistem Pendukung Keputusan (DSS) Alokasi Bansos")
        st.write("Pimpinan memasukkan total anggaran (Rp) dan target kuota (KK). Sistem menghitung distribusi yang adil dan proporsional sesuai tingkat kerentanan.")
        
        sim_col1, sim_col2 = st.columns(2)
        with sim_col1:
            budget_input = st.number_input(
                "Total Pagu Anggaran Bansos Kota Palembang (Rp):",
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
        
        col_pie1, col_pie2 = st.columns(2)
        with col_pie1:
            pie_budget = px.pie(
                df_simulated,
                names='Kategori_Prioritas',
                values='Alokasi_Anggaran_Rp',
                title='<b>Distribusi Alokasi Anggaran (Rp) Per Klaster</b>',
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
                title='<b>Distribusi Kuota Penerima (KK) Per Klaster</b>',
                color='Kategori_Prioritas',
                color_discrete_map={
                    'Prioritas Tinggi (Darurat)': '#EF4444',
                    'Prioritas Sedang (Waspada)': '#F59E0B',
                    'Prioritas Rendah (Mandiri)': '#10B981'
                }
            )
            st.plotly_chart(pie_quota, use_container_width=True)
            
        st.subheader("📋 Tabel Rekomendasi Alokasi Dana & Kuota Per Kecamatan")
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

        if st.button("💾 Arsipkan Hasil Simulasi Ini ke Database", type="primary"):
            save_simulation_results_to_db(df_simulated, "Terkini", budget_input, quota_input, user_display_name)
            st.success("✅ Skenario simulasi berhasil diarsipkan ke tabel `simulasi_alokasi_bansos` di database!")

    # PIMPINAN TAB 4: PROFILER PER KECAMATAN
    with pim_tab4:
        st.subheader("🔍 Profiler & Inspector 18 Kecamatan")
        selected_kec_inspect = st.selectbox("Pilih Kecamatan Ditinjau:", options=df_result['Kecamatan'].unique())
        kec_data = df_result[df_result['Kecamatan'] == selected_kec_inspect].iloc[0]
        
        p_col1, p_col2, p_col3, p_col4 = st.columns(4)
        with p_col1:
            st.metric("Status Zonasi", kec_data['Kategori_Prioritas'])
        with p_col2:
            st.metric("Skor Kerentanan (CVI)", f"{kec_data['Skor_Kerentanan']:.4f}")
        with p_col3:
            st.metric("Jumlah Penduduk Miskin", f"{kec_data['Jumlah_Penduduk_Miskin']:,} jiwa")
        with p_col4:
            st.metric("Skor IPM", kec_data['IPM'])
            
        st.markdown("---")
        st.subheader(f"📌 Profil Indikator Kec. {selected_kec_inspect} vs Rata-Rata Kota Palembang")
        df_city_avg = df_input[selected_indicators].mean()
        comp_df = pd.DataFrame({
            'Indikator': [c.replace('_', ' ') for c in selected_indicators],
            'Nilai Kecamatan': [kec_data[c] for c in selected_indicators],
            'Rata-Rata Kota Palembang': [df_city_avg[c] for c in selected_indicators]
        })
        st.dataframe(comp_df, use_container_width=True)
        
        st.info(f"""
        💡 **Rekomendasi Kebijakan untuk Kecamatan {selected_kec_inspect}:**
        - **Kategori Prioritas**: {kec_data['Kategori_Prioritas']}
        - **Intervensi Utama**: Penanganan tingkat pengangguran ({kec_data['Tingkat_Pengangguran']}%) dan peningkatan alokasi bansos PKH/BPNT secara bertahap.
        """)

    # PIMPINAN TAB 5: RADAR PROFILE
    with pim_tab5:
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            st.subheader("📌 Karakteristik Multi-Dimensi Antar Klaster")
            st.plotly_chart(plot_radar_summary(model_results['cluster_summary'], selected_indicators), use_container_width=True)
        with col_r2:
            st.subheader("🔍 Scatter Plot Hubungan Antar Indikator")
            scat_x = st.selectbox("Sumbu X:", options=selected_indicators, index=min(0, len(selected_indicators)-1))
            scat_y = st.selectbox("Sumbu Y:", options=selected_indicators, index=min(1, len(selected_indicators)-1))
            st.plotly_chart(plot_scatter_2d(df_result, scat_x, scat_y), use_container_width=True)

    # PIMPINAN TAB 6: EXECUTIVE EXPORT
    with pim_tab6:
        st.subheader("📥 Pusat Unduhan Laporan Eksekutif Resmi (.xlsx)")
        st.write("Unduh berkas laporan hasil analisis klasterisasi K-Means yang lengkap dengan multi-sheet untuk dasar penetapan Surat Keputusan (SK) Walikota.")
        
        col_xp1, col_xp2 = st.columns(2)
        with col_xp1:
            excel_data = export_results_to_excel(df_result, model_results['cluster_summary'], elbow_df, model_results)
            if st.download_button(
                label="📊 Unduh Laporan Eksekutif Lengkap (.xlsx)",
                data=excel_data,
                file_name="Laporan_Eksekutif_Bansos_Palembang.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            ):
                log_export_to_db("Excel", "Laporan_Eksekutif_Bansos_Palembang.xlsx", "Terkini", user_display_name)
                
        with col_xp2:
            if os.path.exists(excel_path):
                with open(excel_path, 'rb') as f_ex:
                    st.download_button(
                        label="🏛️ Unduh Master Data Statistik Kesra (.xlsx)",
                        data=f_ex.read(),
                        file_name="Data_Statistik_BPS_Kesra_Palembang.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
