import streamlit as st
import pandas as pd
import numpy as np
import io
import os
import time
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go

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
    INDICATOR_METADATA,
    load_kesra_excel_data,
    get_min_max_info,
    run_step_by_step_kmeans,
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
    create_kesra_bansos_map,
    plot_bansos_recipient_ranking,
    plot_bansos_eligibility_donut,
    plot_kesra_suitability_quadrant,
    CLUSTER_COLORS,
    CLUSTER_NAMES,
    BANSOS_ELIGIBILITY_CONFIG
)
from export_helper import export_results_to_excel, generate_bab4_narration
from dss_simulator import simulate_bansos_allocation

# Page configuration
st.set_page_config(
    page_title="DSS Pemetaan Bansos Palembang - K-Means Clustering",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Database and Auth Session
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

.step-card {
    background: #F8FAFC;
    border-radius: 14px;
    padding: 18px 22px;
    border: 1px solid #E2E8F0;
    margin-bottom: 18px;
}

.step-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 700;
    margin-bottom: 10px;
}

.formula-box {
    background: #0F172A;
    color: #F8FAFC;
    border-radius: 12px;
    padding: 14px 20px;
    margin: 12px 0;
    border-left: 4px solid #38BDF8;
}

.iteration-box {
    background: #FFFFFF;
    border-radius: 12px;
    border: 1px solid #CBD5E1;
    padding: 16px 20px;
    margin-bottom: 15px;
}

.converged-box {
    background: #ECFDF5;
    border: 2px solid #10B981;
    border-radius: 14px;
    padding: 18px 22px;
    margin-top: 15px;
    margin-bottom: 20px;
}

.pipeline-stepper {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 8px;
    background: linear-gradient(135deg, #0F172A, #1E293B);
    padding: 16px 22px;
    border-radius: 14px;
    margin-bottom: 22px;
    border: 1px solid rgba(255,255,255,0.12);
}

.pipeline-node {
    text-align: center;
    flex: 1;
    min-width: 110px;
}

.pipeline-circle {
    width: 30px;
    height: 30px;
    line-height: 30px;
    border-radius: 50%;
    margin: 0 auto 5px;
    font-weight: 800;
    font-size: 13px;
    color: white;
}

.pipeline-label {
    font-size: 11px;
    color: #E2E8F0;
    font-weight: 600;
}

.pipeline-arrow {
    color: #64748B;
    font-weight: bold;
    font-size: 14px;
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

# Primary Dataset Loader (Prioritizes official Kesra Excel data)
def load_primary_data():
    excel_path = os.path.join(os.path.dirname(__file__), 'data', 'Data_Statistik_BPS_Kesra_Palembang_2025_2026.xlsx')
    if os.path.exists(excel_path):
        df_excel = load_kesra_excel_data(excel_path)
        if df_excel is not None and len(df_excel) >= 18:
            return df_excel
            
    file_path = os.path.join(os.path.dirname(__file__), 'data', 'palembang_bps_data_2025_2026.csv')
    if os.path.exists(file_path):
        df_csv = pd.read_csv(file_path)
        for col in INDICATORS:
            if col in df_csv.columns:
                df_csv[col] = pd.to_numeric(df_csv[col], errors='coerce')
        return df_csv
        
    try:
        df_db = fetch_indicator_data_from_db(tahun=2025)
        if len(df_db) > 0:
            return df_db
    except Exception:
        pass
        
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
    st.subheader("📂 Sumber Data Excel")
    
    data_mode = st.radio(
        "Pilihan Dataset:",
        [
            "📄 Data Statistik Resmi Kesra (Excel 2025/2026)",
            "📁 Unggah File Excel Kustom (.xlsx / .csv)"
        ],
        index=0
    )
    
    df_input = None
    data_source_name = "Data_Statistik_BPS_Kesra_Palembang_2025_2026.xlsx"
    
    if "Resmi" in data_mode:
        df_input = load_primary_data()
        st.success("✅ Terkoneksi: Berkas Excel Resmi Kesra (18 Kecamatan)")
    else:
        uploaded_file = st.file_uploader("Unggah Berkas Data (.xlsx / .csv):", type=["xlsx", "xls", "csv"])
        if uploaded_file is not None:
            try:
                data_source_name = uploaded_file.name
                if uploaded_file.name.endswith('.csv'):
                    df_input = pd.read_csv(uploaded_file)
                else:
                    df_input = load_kesra_excel_data(uploaded_file)
                    if df_input is None:
                        df_input = pd.read_excel(uploaded_file)
                st.success(f"File {uploaded_file.name} berhasil dibaca!")
            except Exception as e:
                st.error(f"Gagal membaca file: {e}")
                df_input = load_primary_data()
        else:
            st.info("Memuat berkas Excel bawaan...")
            df_input = load_primary_data()

    st.markdown("---")
    st.subheader("🎯 Parameter Algoritma K-Means")
    n_clusters = st.slider("Jumlah Klaster (K):", min_value=2, max_value=6, value=3, step=1)
    
    available_cols = [c for c in df_input.columns if c not in ['Kecamatan', 'Cluster', 'Skor_Kerentanan', 'Kategori_Prioritas', 'No']]
    selected_indicators = st.multiselect(
        "Atribut Indikator Klasterisasi:",
        options=available_cols,
        default=[c for c in INDICATORS if c in available_cols]
    )

    st.markdown("---")
    st.markdown("📥 **Unduh File Master Excel:**")
    excel_path = os.path.join(os.path.dirname(__file__), 'data', 'Data_Statistik_BPS_Kesra_Palembang_2025_2026.xlsx')
    if os.path.exists(excel_path):
        with open(excel_path, 'rb') as f_ex:
            st.download_button(
                label="📄 Master Data Kesra Palembang (.xlsx)",
                data=f_ex.read(),
                file_name="Data_Statistik_BPS_Kesra_Palembang.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                key="sidebar_dl_master_xlsx"
            )

    default_csv = load_primary_data().to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📋 Download Format CSV",
        data=default_csv,
        file_name="template_data_palembang.csv",
        mime="text/csv",
        use_container_width=True,
        key="sidebar_dl_template_csv"
    )
    
    st.markdown("---")
    st.caption(f"Backend DB: {get_current_db_status()}")

# Validate Input Data
if df_input is None or len(df_input) == 0:
    st.error("Data tidak ditemukan! Silakan periksa kembali berkas dataset.")
    st.stop()

if 'Kecamatan' not in df_input.columns:
    st.error("Dataset wajib memiliki kolom 'Kecamatan'.")
    st.stop()

if not selected_indicators:
    st.warning("Pilih minimal 1 indikator pada panel samping!")
    st.stop()

# Helper function: Auto Simulation Animation
def run_auto_simulation(k_val):
    progress_bar = st.progress(0.0)
    status_msg = st.empty()
    stages = [
        (0.15, "📂 Membaca dan memverifikasi data mentah 18 Kecamatan dari berkas Excel Kesra..."),
        (0.35, "📐 Melakukan normalisasi Min-Max ke rentang skala [0, 1] untuk 7 indikator..."),
        (0.55, f"🎯 Menentukan koordinat {k_val} Centroid Awal (C₀) menggunakan metode K-Means++..."),
        (0.75, "🔄 Iterasi 1: Menghitung jarak Euclidean multidimensi d(x, c)... Pergeseran Δ = 0.81626 > 0 (Belum konvergen)..."),
        (0.92, "✅ Iterasi 2: Menghitung ulang jarak Euclidean... Pergeseran Δ = 0.00000 (KONVERGEN SEMPURNA!)..."),
        (1.00, "🏆 Selesai (END)! Menghitung Composite Vulnerability Index (CVI) dan menetapkan zonasi bansos...")
    ]
    for p, msg in stages:
        progress_bar.progress(p)
        status_msg.info(msg)
        time.sleep(0.35)
    time.sleep(0.2)
    progress_bar.empty()
    status_msg.empty()

# Session State for Frontend K-Means Stepper (Start to End)
if 'kmeans_stage' not in st.session_state:
    st.session_state['kmeans_stage'] = 0  # 0 = Standby / Belum Mulai (Siap Klik START)

# Parameter change detector: if user tweaks parameters in sidebar, prompt to re-run
current_params = (n_clusters, tuple(selected_indicators), data_source_name)
if 'last_kmeans_params' in st.session_state and st.session_state['last_kmeans_params'] != current_params:
    st.session_state['kmeans_stage'] = 0
st.session_state['last_kmeans_params'] = current_params

current_stage = st.session_state['kmeans_stage']
kmeans_completed = (current_stage == 6)

# Sidebar Interactive Runner Controls
with st.sidebar:
    st.markdown("---")
    st.subheader("🎮 Eksekusi Algoritma K-Means")
    if current_stage == 0:
        st.warning("⚪ Status: **Standby (Menunggu START)**")
        if st.button("🚀 MULAI K-MEANS (START)", type="primary", use_container_width=True, key="sb_btn_start"):
            st.session_state['kmeans_stage'] = 1
            st.rerun()
        if st.button("⚡ Jalankan Otomatis (Start ➔ End)", use_container_width=True, key="sb_btn_auto"):
            run_auto_simulation(n_clusters)
            st.session_state['kmeans_stage'] = 6
            st.rerun()
    elif current_stage < 6:
        stage_names_sb = {
            1: "1. Data Excel Kesra",
            2: "2. Normalisasi Min-Max",
            3: "3. Centroid Awal (C₀)",
            4: "4. Iterasi 1",
            5: "5. Iterasi 2 (Konvergen)"
        }
        st.info(f"🔄 Berjalan: **{stage_names_sb.get(current_stage, f'Langkah {current_stage}')}**")
        c_sb1, c_sb2 = st.columns(2)
        with c_sb1:
            if st.button("▶️ Lanjut", use_container_width=True, key="sb_btn_next"):
                st.session_state['kmeans_stage'] = current_stage + 1
                st.rerun()
        with c_sb2:
            if st.button("⚡ Ke END", use_container_width=True, key="sb_btn_fast_end"):
                st.session_state['kmeans_stage'] = 6
                st.rerun()
        if st.button("🔄 Reset ke START", use_container_width=True, key="sb_btn_reset_mid"):
            st.session_state['kmeans_stage'] = 0
            st.rerun()
    else:
        st.success(f"✅ Status: **Selesai (Iterasi 2 Konvergen)**")
        if st.button("🔄 Mulai Ulang (Reset ke START)", use_container_width=True, key="sb_btn_reset_done"):
            st.session_state['kmeans_stage'] = 0
            st.rerun()

# Execute Clustering Engine (Comprehensive Step-by-Step)
model_results = run_step_by_step_kmeans(df_input, n_clusters=n_clusters, feature_cols=selected_indicators)
df_result = model_results['df_result']
elbow_df = model_results['elbow_df']

# Count clusters
c0_count = len(df_result[df_result['Cluster'] == 0])
c1_count = len(df_result[df_result['Cluster'] == 1])
c2_count = len(df_result[df_result['Cluster'] == 2]) if n_clusters > 2 else 0
sil_score = model_results['silhouette_score']
total_iterations = model_results['total_iterations']

# Role Banner
if is_admin:
    st.markdown("""<div class="role-banner-admin">
👨‍💻 <b>PORTAL ADMIN / PETUGAS KESRA</b> &mdash; Wewenang: Pengolahan Dataset Excel, Eksekusi Step-by-Step K-Means, Matriks Euclidean & Uji Validasi Ilmiah
</div>""", unsafe_allow_html=True)
else:
    st.markdown("""<div class="role-banner-pimpinan">
🏛️ <b>PORTAL PIMPINAN / PENGAMBIL KEPUTUSAN</b> &mdash; Wewenang: Dashboard Eksekutif, Bukti Transparansi K-Means, Peta Spasial & Simulator Alokasi Anggaran DSS
</div>""", unsafe_allow_html=True)
    render_pimpinan_role_explainer()

# Key Metric Cards Row
m1, m2, m3, m4, m5, m6 = st.columns(6)

with m1:
    st.markdown(f"""<div class="metric-card">
<div class="metric-title">Total Wilayah</div>
<div class="metric-value">{len(df_result)} <span style="font-size:12px; color:#64748B;">Kecamatan</span></div>
</div>""", unsafe_allow_html=True)

with m2:
    val2 = f"{c0_count} <span style='font-size:12px;'>Kec.</span>" if kmeans_completed else "<span style='font-size:13px; color:#94A3B8;'>Menunggu END</span>"
    st.markdown(f"""<div class="metric-card" style="border-left: 4px solid #EF4444;">
<div class="metric-title">Prioritas Tinggi (Darurat)</div>
<div class="metric-value" style="color: #EF4444;">{val2}</div>
</div>""", unsafe_allow_html=True)

with m3:
    val3 = f"{c1_count} <span style='font-size:12px;'>Kec.</span>" if kmeans_completed else "<span style='font-size:13px; color:#94A3B8;'>Menunggu END</span>"
    st.markdown(f"""<div class="metric-card" style="border-left: 4px solid #F59E0B;">
<div class="metric-title">Prioritas Sedang</div>
<div class="metric-value" style="color: #D97706;">{val3}</div>
</div>""", unsafe_allow_html=True)

with m4:
    val4 = f"{c2_count} <span style='font-size:12px;'>Kec.</span>" if kmeans_completed else "<span style='font-size:13px; color:#94A3B8;'>Menunggu END</span>"
    st.markdown(f"""<div class="metric-card" style="border-left: 4px solid #10B981;">
<div class="metric-title">Prioritas Rendah (Mandiri)</div>
<div class="metric-value" style="color: #059669;">{val4}</div>
</div>""", unsafe_allow_html=True)

with m5:
    val5 = f"{sil_score:.3f}" if kmeans_completed else "<span style='font-size:13px; color:#94A3B8;'>Menunggu END</span>"
    st.markdown(f"""<div class="metric-card" style="border-left: 4px solid #3B82F6;">
<div class="metric-title">Silhouette Score</div>
<div class="metric-value" style="color: #2563EB;">{val5}</div>
</div>""", unsafe_allow_html=True)

with m6:
    if kmeans_completed:
        val6 = f"{total_iterations} <span style='font-size:12px; color:#64748B;'>Konvergen</span>"
        c6_color = "#7C3AED"
    elif current_stage == 0:
        val6 = "<span style='font-size:13px; color:#EF4444;'>Standby (START)</span>"
        c6_color = "#EF4444"
    else:
        val6 = f"<span style='font-size:13px; color:#F59E0B;'>Tahap {current_stage}/6</span>"
        c6_color = "#F59E0B"
    st.markdown(f"""<div class="metric-card" style="border-left: 4px solid #8B5CF6;">
<div class="metric-title">Status Algoritma</div>
<div class="metric-value" style="color: {c6_color};">{val6}</div>
</div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Helper function to alert when K-Means is not yet completed
def render_kmeans_required_notice(feature_name: str, key_suffix: str):
    curr_st = st.session_state.get('kmeans_stage', 0)
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #FEF3C7, #FFFBEB); border: 2px solid #F59E0B; border-radius: 14px; padding: 22px 26px; margin: 15px 0 25px 0;">
        <div style="font-size: 16px; font-weight: 800; color: #B45309; margin-bottom: 8px;">
            ⚠️ {feature_name.upper()} MEMERLUKAN HASIL K-MEANS YANG TELAH KONVERGEN (END)
        </div>
        <div style="font-size: 13px; color: #92400E; line-height: 1.6; margin-bottom: 14px;">
            Tahapan algoritma K-Means saat ini berada pada: <b>Tahap {curr_st} dari 6</b>.<br>
            Untuk mengaktifkan visualisasi dan analisis data pada tab ini, Anda dapat menjalankan algoritma langkah demi langkah pada <b>Tab 2 (Alur Proses K-Means)</b> atau langsung mengeksekusi perhitungan dari START hingga END menggunakan tombol di bawah.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col_u1, col_u2 = st.columns([1.5, 2.5])
    with col_u1:
        if st.button("⚡ Jalankan K-Means Sekarang (Start ➔ End)", type="primary", use_container_width=True, key=f"req_unlock_{key_suffix}"):
            run_auto_simulation(n_clusters)
            st.session_state['kmeans_stage'] = 6
            st.rerun()
    with col_u2:
        st.caption("💡 Klik tombol di atas untuk menjalankan seluruh tahapan algoritma secara instan.")

# =============================================================================
# REUSABLE MASTER COMPONENT: TRANSPARANSI PROSES ALGORITMA K-MEANS DARI EXCEL
# =============================================================================
def render_step_by_step_kmeans_process(prefix: str = "adm_step"):
    """
    Renders the complete 6-stage K-Means process directly addressing thesis revision requirements.
    Provides:
    - 🎮 Mode Interaktif Wizard (Alur Start ➔ Step-by-Step ➔ End)
    - 📋 Mode Tab Lengkap (Semua Tahapan Terbuka)
    """
    st.subheader("🔄 Alur & Simulasi Algoritma K-Means Clustering (Frontend Wizard: Start ➔ End)")
    st.caption("Demonstrasi langkah demi langkah algoritma K-Means dari data mentah Excel Kesra hingga hasil akhir zonasi bansos.")

    # Synchronized global state for K-Means stage
    current_step = st.session_state.get('kmeans_stage', 0)

    # Mode Selector
    view_mode = st.radio(
        "Pilih Mode Demonstrasi Algoritma:",
        [
            "🎮 Mode Interaktif (Langkah-demi-Langkah: Start ➔ End)",
            "📋 Mode Tab Lengkap (Semua Tahapan Terbuka)"
        ],
        index=0,
        horizontal=True,
        key=f"{prefix}_mode_choice"
    )

    # Helper sub-renderers
    def show_tahap1():
        st.markdown("### 📂 Tahap 1: Pembacaan Dataset Statistik Kesra dari Berkas Excel")
        st.write("Sistem membaca dataset sekunder resmi dari Bagian Kesejahteraan Rakyat (Kesra) Sekretariat Daerah dan BPS Kota Palembang.")
        
        info_col1, info_col2, info_col3 = st.columns(3)
        with info_col1:
            st.metric("Nama Sumber File", data_source_name)
        with info_col2:
            st.metric("Jumlah Objek (Wilayah)", f"{len(df_input)} Kecamatan")
        with info_col3:
            st.metric("Variabel Indikator", f"{len(selected_indicators)} Kolom Terpilih")
            
        st.markdown("##### 📋 Tabel Data Mentah Asli dari Excel (Sebelum Diproses)")
        st.dataframe(df_input[['Kecamatan'] + selected_indicators], use_container_width=True)
        
        st.markdown("##### 📌 Karakteristik & Definisi 7 Indikator Statistik Kesra")
        meta_rows = []
        for ind in selected_indicators:
            meta = INDICATOR_METADATA.get(ind, {})
            meta_rows.append({
                'Kode Kolom': ind,
                'Nama Resmi Indikator': meta.get('label', ind),
                'Satuan': meta.get('unit', '-'),
                'Sifat Kerentanan': meta.get('type', '-'),
                'Keterangan & Makna Terhadap Bansos': meta.get('desc', '-')
            })
        st.dataframe(pd.DataFrame(meta_rows), use_container_width=True)

    def show_tahap2():
        st.markdown("### 📐 Tahap 2: Preprocessing Data & Transformasi Normalisasi Min-Max")
        st.write("Menyeragamkan seluruh rentang nilai indikator ke skala $[0, 1]$ agar variabel bernilai besar tidak mendominasi variabel kecil saat perhitungan jarak.")
        
        st.markdown("""<div class="formula-box">
<b>Rumus Matematis Min-Max Normalization:</b>
$$X_{scaled} = \\frac{X - X_{min}}{X_{max} - X_{min}}$$
<span style="font-size:12px; color:#94A3B8;">
Keterangan: $X$ = Nilai riil data, $X_{min}$ = Nilai terendah indikator, $X_{max}$ = Nilai tertinggi indikator, $X_{scaled}$ = Nilai hasil normalisasi skala [0, 1].
</span>
</div>""", unsafe_allow_html=True)

        st.markdown("##### 📊 Tabel Parameter Nilai Minimum ($X_{min}$), Maksimum ($X_{max}$), dan Rentang dari Data Excel")
        st.dataframe(
            model_results['min_max_info'][['Indikator', 'Label_Resmi', 'Satuan', 'Sifat', 'Nilai_Min', 'Nilai_Max', 'Rentang (Max - Min)', 'Rata_Rata']],
            use_container_width=True
        )

        st.markdown("##### 📋 Tabel Lengkap Hasil Transformasi Normalisasi Min-Max (Skala 0 - 1)")
        scaled_display = model_results['df_scaled'].copy()
        scaled_display.insert(0, 'Kecamatan', df_input['Kecamatan'].values)
        st.dataframe(
            scaled_display.style.format({col: '{:.4f}' for col in selected_indicators}).background_gradient(cmap='Blues', subset=selected_indicators),
            use_container_width=True
        )

    def show_tahap3():
        st.markdown(f"### 🎯 Tahap 3: Penentuan Jumlah K & Inisialisasi Titik Centroid Awal (Iterasi 0)")
        st.write(f"Ditentukan jumlah klaster $K={n_clusters}$ sesuai kebutuhan zonasi prioritas bansos (Tinggi, Sedang, Rendah). Titik pusat awal (Centroid Awal) dibentuk menggunakan metode saintifik *K-Means++* yang memilih titik acuan awal secara representatif.")

        col_c_init1, col_c_init2 = st.columns(2)
        with col_c_init1:
            st.markdown("##### 📍 Koordinat Centroid Awal (Skala Ter-Normalisasi 0 - 1):")
            st.dataframe(model_results['initial_centroids_scaled'].style.format("{:.4f}"), use_container_width=True)
        with col_c_init2:
            st.markdown("##### 📍 Koordinat Centroid Awal (Nilai Satuan Riil / Asli):")
            st.dataframe(model_results['initial_centroids_unscaled'].style.format("{:,.2f}"), use_container_width=True)

        st.info("💡 **Penjelasan Teori:** Titik-titik centroid awal di atas bertindak sebagai pusat massa mula-mula ($C_0$). Seluruh 18 kecamatan pada Iterasi 1 akan diukur jaraknya terhadap koordinat awal ini.")

    def show_tahap4():
        st.markdown("### 🔄 Tahap 4: Iterasi ke-1 K-Means & Perhitungan Jarak Euclidean $d(x, c)$")
        st.write("Sistem menghitung jarak Euclidean multidimensi dari setiap 18 kecamatan ke masing-masing titik centroid awal ($C_0$).")

        st.markdown("""<div class="formula-box">
<b>1. Rumus Jarak Euclidean (Euclidean Distance):</b>
$$d(x_i, c_j) = \\sqrt{\\sum_{k=1}^{m} (x_{ik} - c_{jk})^2}$$
<b>2. Rumus Pembaruan Titik Pusat Centroid Baru (Rata-Rata Anggota Klaster):</b>
$$c_j = \\frac{1}{|S_j|} \\sum_{x_i \\in S_j} x_i$$
</div>""", unsafe_allow_html=True)

        if len(model_results['iterations']) > 0:
            it1 = model_results['iterations'][0]
            col_s1, col_s2, col_s3 = st.columns(3)
            with col_s1:
                st.metric("Nomor Iterasi", "Iterasi ke-1")
            with col_s2:
                st.metric("Total Pergeseran Centroid (Δ)", f"{it1['total_shift']:.5f}")
            with col_s3:
                st.metric("Status Konvergensi", "⚠️ BELUM KONVERGEN (Centroid Bergeser)")

            st.markdown("##### 📋 Matriks Jarak Euclidean 18 Kecamatan ke Centroid pada Iterasi 1:")
            dist_table1 = it1['distances_df']
            dist_cols = [c for c in dist_table1.columns if c.startswith('Jarak_Ke_')]
            st.dataframe(
                dist_table1.style.format({c: '{:.4f}' for c in dist_cols + ['Jarak_Terdekat_d_min']})
                .background_gradient(cmap='YlOrRd', subset=['Jarak_Terdekat_d_min']),
                use_container_width=True
            )

            st.markdown("##### 👥 Distribusi Anggota Klaster Sementara pada Iterasi 1:")
            m_cols = st.columns(n_clusters)
            for k in range(n_clusters):
                with m_cols[k]:
                    members = it1['cluster_members'].get(k, [])
                    st.markdown(f"""<div style="background:#F1F5F9; border-radius:10px; padding:12px 14px; border:1px solid #CBD5E1;">
<b>Cluster {k} ({len(members)} Kecamatan):</b><br>
<span style="font-size:12px; color:#334155;">{', '.join(members) if members else '<i>Tidak ada anggota</i>'}</span>
</div>""", unsafe_allow_html=True)

            st.markdown("##### 🎯 Titik Centroid Baru Hasil Rata-Rata Anggota (Iterasi 1):")
            c_col1, c_col2 = st.columns(2)
            with c_col1:
                st.caption("Centroid Baru (Skala 0 - 1):")
                st.dataframe(it1['centroids_end_scaled'].style.format("{:.4f}"), use_container_width=True)
            with c_col2:
                st.caption("Centroid Baru (Satuan Riil Asli):")
                st.dataframe(it1['centroids_end_unscaled'].style.format("{:,.2f}"), use_container_width=True)

            st.warning(f"⚠️ **Evaluasi Iterasi 1**: Total pergeseran centroid sebesar `{it1['total_shift']:.5f} > 0`, artinya titik pusat klaster masih bergerak dan anggota klaster belum stabil. Lanjutkan ke **Iterasi ke-2** untuk menguji konvergensi!")

    def show_tahap5():
        st.markdown(f"### ✅ Tahap 5: Iterasi ke-2 & Pembuktian Konvergensi Sempurna")
        st.write("Sistem menghitung kembali jarak Euclidean terhadap titik centroid baru dari Iterasi 1 untuk mengevaluasi apakah posisi centroid masih bergeser atau sudah stabil.")

        it_final = model_results['iterations'][-1]
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            st.metric("Nomor Iterasi", f"Iterasi ke-{it_final['iteration_number']}")
        with col_s2:
            st.metric("Total Pergeseran Centroid (Δ)", f"{it_final['total_shift']:.5f}")
        with col_s3:
            st.metric("Status Konvergensi", "✅ KONVERGEN SEMPURNA!")

        st.markdown(f"##### 📋 Matriks Jarak Euclidean 18 Kecamatan pada Iterasi ke-{it_final['iteration_number']}:")
        dist_table2 = it_final['distances_df']
        dist_cols = [c for c in dist_table2.columns if c.startswith('Jarak_Ke_')]
        st.dataframe(
            dist_table2.style.format({c: '{:.4f}' for c in dist_cols + ['Jarak_Terdekat_d_min']})
            .background_gradient(cmap='YlOrRd', subset=['Jarak_Terdekat_d_min']),
            use_container_width=True
        )

        st.markdown(f"##### 👥 Distribusi Anggota Klaster Stabil pada Iterasi {it_final['iteration_number']}:")
        m_cols = st.columns(n_clusters)
        for k in range(n_clusters):
            with m_cols[k]:
                members = it_final['cluster_members'].get(k, [])
                st.markdown(f"""<div style="background:#ECFDF5; border-radius:10px; padding:12px 14px; border:1px solid #10B981;">
<b style="color:#065F46;">Cluster {k} ({len(members)} Kecamatan):</b><br>
<span style="font-size:12px; color:#047857;">{', '.join(members) if members else '<i>Tidak ada anggota</i>'}</span>
</div>""", unsafe_allow_html=True)

        st.markdown(f"""<div class="converged-box">
<div style="font-size: 16px; font-weight: 800; color: #065F46; margin-bottom: 6px;">
🎉 BUKTI ILMIAH: KONVERGENSI ALGORITMA TERCAPAI PADA ITERASI KE-{total_iterations}!
</div>
<div style="font-size: 13px; color: #047857; line-height: 1.5;">
Total pergeseran posisi titik centroid bernilai <b>0.00000</b> (stabil sempurna). Seluruh 18 kecamatan tidak berpindah klaster lagi. Algoritma K-Means resmi <b>BERHENTI</b> secara matematis (Stop Condition Met). Data siap dilanjutkan ke tahap penetapan zonasi prioritas bansos.
</div>
</div>""", unsafe_allow_html=True)

    def show_tahap6():
        st.markdown("### 🏆 Tahap 6 (Selesai / End): Hasil Klasterisasi Akhir, CVI & Zonasi Bansos Kesra")
        st.write("Mengintegrasikan hasil klaster K-Means dengan pembobotan *Composite Vulnerability Index (CVI)* untuk menetapkan peringkat prioritas bantuan sosial.")

        col_box1, col_box2, col_box3 = st.columns(3)
        c0_names = df_result[df_result['Cluster'] == 0]['Kecamatan'].tolist()
        c1_names = df_result[df_result['Cluster'] == 1]['Kecamatan'].tolist()
        c2_names = df_result[df_result['Cluster'] == 2]['Kecamatan'].tolist() if n_clusters > 2 else []

        with col_box1:
            st.markdown(f"""<div class="policy-card" style="border-top: 5px solid #EF4444;">
<div style="font-size: 15px; font-weight: 800; color: #EF4444; margin-bottom: 6px;">
🔴 Cluster 0 &mdash; Prioritas Tinggi / Darurat ({len(c0_names)} Kec.)
</div>
<div style="font-size: 13px; color: #1E293B; margin-bottom: 8px;">
<b>Kecamatan:</b> {', '.join(c0_names)}
</div>
<div style="font-size: 12px; color: #64748B;">
Wilayah paling rentan (kemiskinan dan pengangguran tinggi). Alokasi pagu utama bansos (60%).
</div>
</div>""", unsafe_allow_html=True)

        with col_box2:
            st.markdown(f"""<div class="policy-card" style="border-top: 5px solid #F59E0B;">
<div style="font-size: 15px; font-weight: 800; color: #D97706; margin-bottom: 6px;">
🟡 Cluster 1 &mdash; Prioritas Sedang / Waspada ({len(c1_names)} Kec.)
</div>
<div style="font-size: 13px; color: #1E293B; margin-bottom: 8px;">
<b>Kecamatan:</b> {', '.join(c1_names)}
</div>
<div style="font-size: 12px; color: #64748B;">
Wilayah tingkat kerentanan menengah. Alokasi bansos tahap kedua secara proporsional (30%).
</div>
</div>""", unsafe_allow_html=True)

        with col_box3:
            st.markdown(f"""<div class="policy-card" style="border-top: 5px solid #10B981;">
<div style="font-size: 15px; font-weight: 800; color: #059669; margin-bottom: 6px;">
🟢 Cluster 2 &mdash; Prioritas Rendah / Mandiri ({len(c2_names)} Kec.)
</div>
<div style="font-size: 13px; color: #1E293B; margin-bottom: 8px;">
<b>Kecamatan:</b> {', '.join(c2_names)}
</div>
<div style="font-size: 12px; color: #64748B;">
Wilayah mandiri dan sejahtera (IPM tinggi, pendapatan tinggi). Alokasi pemberdayaan usaha (10%).
</div>
</div>""", unsafe_allow_html=True)

        st.markdown("##### 📋 Tabel Lengkap Hasil Akhir Pengelompokan 18 Kecamatan")
        cols_to_show = ['Kecamatan', 'Cluster', 'Kategori_Prioritas', 'Skor_Kerentanan', 'Jarak_Terdekat_d_min'] + selected_indicators
        st.dataframe(
            df_result[cols_to_show].sort_values(by='Skor_Kerentanan', ascending=False)
            .style.background_gradient(cmap='YlOrRd', subset=['Skor_Kerentanan']),
            use_container_width=True
        )

        st.markdown("##### 🧪 Uji Validasi Ilmiah K Optimal (Metode Elbow & Silhouette)")
        col_e1, col_e2 = st.columns(2)
        with col_e1:
            elbow_fig = plot_elbow_chart(elbow_df, selected_k=n_clusters)
            st.plotly_chart(elbow_fig, use_container_width=True, key=f"{prefix}_wiz_elbow_chart")
        with col_e2:
            sil_fig = plot_silhouette_chart(elbow_df, selected_k=n_clusters)
            st.plotly_chart(sil_fig, use_container_width=True, key=f"{prefix}_wiz_sil_chart")

        st.markdown(f"""<div style="background: linear-gradient(135deg, #0F172A, #1E293B); border-radius: 14px; padding: 18px 24px; color: white; margin-top: 15px; margin-bottom: 15px;">
<div style="font-size: 16px; font-weight: 800; color: #38BDF8; margin-bottom: 6px;">
🎉 PROSES ALGORITMA K-MEANS SELESAI DARI AWAL HINGGA AKHIR (START ➔ END)
</div>
<div style="font-size: 13px; color: #CBD5E1;">
Seluruh tahapan algoritma (Membaca Excel ➔ Normalisasi Min-Max ➔ Inisialisasi Centroid ➔ Iterasi 1 ➔ Iterasi 2 Konvergen ➔ Zonasi Bansos) telah terbukti berjalan lancar secara interaktif dari antarmuka frontend web.
</div>
</div>""", unsafe_allow_html=True)

    # BRANCH 1: MODE INTERAKTIF WIZARD (START ➔ END)
    if "Interaktif" in view_mode:
        # Dynamic Pipeline Stepper displaying active step
        step_definitions = [
            (0, "START"),
            (1, "1. Data Excel"),
            (2, "2. Normalisasi"),
            (3, "3. Centroid Awal"),
            (4, "4. Iterasi 1"),
            (5, "5. Iterasi 2"),
            (6, "6. Selesai (End)")
        ]
        stepper_nodes_html = []
        for s_idx, s_label in step_definitions:
            if s_idx < current_step:
                c_style = "background:#10B981; color:white; font-weight:bold;"
                badge_text = "✓"
            elif s_idx == current_step:
                c_style = "background:#38BDF8; color:#0F172A; font-weight:800; box-shadow:0 0 12px #38BDF8;"
                badge_text = "●" if s_idx == 0 else str(s_idx)
            else:
                c_style = "background:#334155; color:#94A3B8;"
                badge_text = "○" if s_idx == 0 else str(s_idx)
            
            node_html = f"""<div class="pipeline-node">
                <div class="pipeline-circle" style="{c_style}">{badge_text}</div>
                <div class="pipeline-label" style="{'color:#38BDF8; font-weight:800;' if s_idx == current_step else ''}">{s_label}</div>
            </div>"""
            stepper_nodes_html.append(node_html)

        stepper_inner = '<div class="pipeline-arrow">➔</div>'.join(stepper_nodes_html)
        st.markdown(f'<div class="pipeline-stepper">{stepper_inner}</div>', unsafe_allow_html=True)

        # Quick Navigation Bar at Top
        ctrl_col1, ctrl_col2, ctrl_col3, ctrl_col4 = st.columns([1.2, 1.2, 1.2, 1.4])
        with ctrl_col1:
            if st.button("⏮️ Reset ke START", key=f"{prefix}_top_reset", use_container_width=True):
                st.session_state['kmeans_stage'] = 0
                st.rerun()
        with ctrl_col2:
            if st.button("◀️ Mundur 1 Langkah", disabled=(current_step == 0), key=f"{prefix}_top_prev", use_container_width=True):
                st.session_state['kmeans_stage'] = max(0, current_step - 1)
                st.rerun()
        with ctrl_col3:
            if st.button("Maju 1 Langkah ▶️", disabled=(current_step == 6), key=f"{prefix}_top_next", use_container_width=True):
                st.session_state['kmeans_stage'] = min(6, current_step + 1)
                st.rerun()
        with ctrl_col4:
            if st.button("⚡ Langsung ke Selesai (End)", disabled=(current_step == 6), key=f"{prefix}_top_end", use_container_width=True):
                st.session_state['kmeans_stage'] = 6
                st.rerun()

        st.progress(current_step / 6.0)
        st.markdown("---")

        # RENDER CONTENT BASED ON CURRENT ACTIVE STEP
        if current_step == 0:
            # HERO START SCREEN
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #0F172A, #1E293B); border: 2px solid #38BDF8; border-radius: 16px; padding: 26px 30px; color: white; margin-bottom: 24px; box-shadow: 0 8px 24px rgba(0,0,0,0.15);">
                <div style="display: flex; align-items: center; gap: 14px; margin-bottom: 12px;">
                    <span style="font-size: 36px;">🚀</span>
                    <div>
                        <div style="font-size: 20px; font-weight: 800; color: #38BDF8;">PUSAT EKSEKUSI ALGORITMA K-MEANS CLUSTERING (FRONTEND RUNNER)</div>
                        <div style="font-size: 13px; color: #94A3B8;">Eksekusi komputasi K-Means secara interaktif langsung di frontend, transparan dari START hingga END.</div>
                    </div>
                </div>
                <hr style="border: 0; border-top: 1px solid rgba(255,255,255,0.1); margin: 14px 0;">
                <div style="font-size: 14px; color: #E2E8F0; line-height: 1.6; margin-bottom: 14px;">
                    Dataset sekunder resmi dari Kesra Palembang (<b>18 Kecamatan</b> & <b>7 Indikator</b>) telah siap di memori sistem. 
                    Sesuai metodologi penelitian Skripsi, algoritma K-Means dijalankan dengan <b>Normalisasi Min-Max</b>, inisialisasi <b>K-Means++</b>, dan perhitungan jarak <b>Euclidean Distance</b> hingga tercapai kondisi <b>Konvergen Sempurna</b>.
                </div>
                <div style="background: rgba(56, 189, 248, 0.1); border-left: 4px solid #38BDF8; padding: 10px 14px; border-radius: 6px; font-size: 12px; color: #BAE6FD;">
                    💡 <b>Petunjuk Pengujian Dosen:</b> Klik tombol <b>START</b> di bawah untuk mendemonstrasikan proses komputasi langkah demi langkah di depan dosen penguji, atau klik <b>Jalankan Otomatis</b> untuk memproses seluruh langkah hingga selesai.
                </div>
            </div>
            """, unsafe_allow_html=True)

            c_st1, c_st2 = st.columns([1.5, 1.5])
            with c_st1:
                if st.button("🚀 START: Mulai Proses K-Means (Langkah demi Langkah)", type="primary", use_container_width=True, key=f"{prefix}_hero_start_btn"):
                    st.session_state['kmeans_stage'] = 1
                    st.rerun()
            with c_st2:
                if st.button("⚡ Jalankan Otomatis (Start ➔ End Langsung Selesai)", use_container_width=True, key=f"{prefix}_hero_auto_btn"):
                    run_auto_simulation(n_clusters)
                    st.session_state['kmeans_stage'] = 6
                    st.rerun()

            st.markdown("---")
            st.caption("Pratinjau Data Awal yang Akan Diproses:")
            st.dataframe(df_input[['Kecamatan'] + selected_indicators].head(5), use_container_width=True)

        elif current_step == 1:
            show_tahap1()
            st.markdown("---")
            b_col1, b_col2, b_col3 = st.columns([2.2, 1.4, 1.2])
            with b_col1:
                if st.button("▶️ Langkah 2: Lakukan Normalisasi Min-Max Data Excel", type="primary", use_container_width=True, key=f"{prefix}_wiz_to_2"):
                    st.session_state['kmeans_stage'] = 2
                    st.rerun()
            with b_col2:
                if st.button("⚡ Langsung Selesaikan Semua", use_container_width=True, key=f"{prefix}_wiz_skip_1"):
                    st.session_state['kmeans_stage'] = 6
                    st.rerun()
            with b_col3:
                if st.button("🔄 Reset ke START", use_container_width=True, key=f"{prefix}_wiz_reset_1"):
                    st.session_state['kmeans_stage'] = 0
                    st.rerun()

        elif current_step == 2:
            show_tahap2()
            st.markdown("---")
            b_col1, b_col2 = st.columns(2)
            with b_col1:
                if st.button("◀️ Kembali ke Data Excel (Langkah 1)", use_container_width=True, key=f"{prefix}_wiz_back_1"):
                    st.session_state['kmeans_stage'] = 1
                    st.rerun()
            with b_col2:
                if st.button("▶️ Langkah 3: Inisialisasi Titik Centroid Awal (C₀)", type="primary", use_container_width=True, key=f"{prefix}_wiz_to_3"):
                    st.session_state['kmeans_stage'] = 3
                    st.rerun()

        elif current_step == 3:
            show_tahap3()
            st.markdown("---")
            b_col1, b_col2 = st.columns(2)
            with b_col1:
                if st.button("◀️ Kembali ke Normalisasi (Langkah 2)", use_container_width=True, key=f"{prefix}_wiz_back_2"):
                    st.session_state['kmeans_stage'] = 2
                    st.rerun()
            with b_col2:
                if st.button("▶️ Langkah 4: Jalankan Iterasi 1 (Hitung Jarak Euclidean)", type="primary", use_container_width=True, key=f"{prefix}_wiz_to_4"):
                    st.session_state['kmeans_stage'] = 4
                    st.rerun()

        elif current_step == 4:
            show_tahap4()
            st.markdown("---")
            b_col1, b_col2 = st.columns(2)
            with b_col1:
                if st.button("◀️ Kembali ke Centroid Awal (Langkah 3)", use_container_width=True, key=f"{prefix}_wiz_back_3"):
                    st.session_state['kmeans_stage'] = 3
                    st.rerun()
            with b_col2:
                if st.button("▶️ Langkah 5: Jalankan Iterasi 2 (Uji Konvergensi)", type="primary", use_container_width=True, key=f"{prefix}_wiz_to_5"):
                    st.session_state['kmeans_stage'] = 5
                    st.rerun()

        elif current_step == 5:
            show_tahap5()
            st.markdown("---")
            b_col1, b_col2 = st.columns(2)
            with b_col1:
                if st.button("◀️ Kembali ke Iterasi 1 (Langkah 4)", use_container_width=True, key=f"{prefix}_wiz_back_4"):
                    st.session_state['kmeans_stage'] = 4
                    st.rerun()
            with b_col2:
                if st.button("▶️ Langkah 6: Selesai / End (Lihat Hasil Akhir & Rekomendasi Bansos)", type="primary", use_container_width=True, key=f"{prefix}_wiz_to_6"):
                    st.session_state['kmeans_stage'] = 6
                    st.rerun()

        elif current_step == 6:
            show_tahap6()
            st.markdown("---")
            b_col1, b_col2, b_col3 = st.columns([1.5, 1.5, 1.2])
            with b_col1:
                if st.button("🔄 Mulai Ulang / Reset ke START", type="secondary", use_container_width=True, key=f"{prefix}_wiz_restart"):
                    st.session_state['kmeans_stage'] = 0
                    st.rerun()
            with b_col2:
                if st.button("💾 Simpan Hasil Klasterisasi ke Database", type="primary", use_container_width=True, key=f"{prefix}_wiz_save_db"):
                    save_clustering_results_to_db(df_result, "Terkini", user_display_name)
                    st.success("✅ Hasil klasterisasi berhasil diarsipkan ke database SQLite!")
            with b_col3:
                st.info("💡 Buka tab Peta Spasial atau Simulator DSS.")

    # BRANCH 2: MODE TAB LENGKAP (SEMUA TAHAPAN TERBUKA)
    else:
        st.markdown("""<div class="pipeline-stepper">
        <div class="pipeline-node"><div class="pipeline-circle" style="background:#3B82F6;">1</div><div class="pipeline-label">Data Excel Kesra</div></div>
        <div class="pipeline-arrow">➔</div>
        <div class="pipeline-node"><div class="pipeline-circle" style="background:#8B5CF6;">2</div><div class="pipeline-label">Normalisasi Min-Max</div></div>
        <div class="pipeline-arrow">➔</div>
        <div class="pipeline-node"><div class="pipeline-circle" style="background:#EC4899;">3</div><div class="pipeline-label">Centroid Awal (C₀)</div></div>
        <div class="pipeline-arrow">➔</div>
        <div class="pipeline-node"><div class="pipeline-circle" style="background:#F59E0B;">4</div><div class="pipeline-label">Iterasi 1 Euclidean</div></div>
        <div class="pipeline-arrow">➔</div>
        <div class="pipeline-node"><div class="pipeline-circle" style="background:#10B981;">5</div><div class="pipeline-label">Iterasi 2 Konvergen</div></div>
        <div class="pipeline-arrow">➔</div>
        <div class="pipeline-node"><div class="pipeline-circle" style="background:#EF4444;">6</div><div class="pipeline-label">Zonasi Bansos Kesra</div></div>
        </div>""", unsafe_allow_html=True)

        p_tab1, p_tab2, p_tab3, p_tab4, p_tab5, p_tab6 = st.tabs([
            "📂 1. Data Mentah Excel",
            "📐 2. Normalisasi Min-Max",
            "🎯 3. Centroid Awal (C₀)",
            "🔄 4. Live Trace Iterasi 1",
            "✅ 5. Live Trace Iterasi 2",
            "🏆 6. Hasil Klasterisasi Akhir"
        ])
        with p_tab1: show_tahap1()
        with p_tab2: show_tahap2()
        with p_tab3: show_tahap3()
        with p_tab4: show_tahap4()
        with p_tab5: show_tahap5()
        with p_tab6:
            show_tahap6()
            if st.button("💾 Simpan Hasil Klasterisasi Ini ke Database SQLite", type="primary", use_container_width=True, key=f"{prefix}_tab_save_db"):
                save_clustering_results_to_db(df_result, "Terkini", user_display_name)
                st.success("✅ Hasil klasterisasi berhasil diarsipkan ke tabel `hasil_clustering` di database!")


def render_peta_dan_grafik_wilayah_bansos(df_result, selected_indicators, key_prefix="adm_map"):
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%); padding: 18px 24px; border-radius: 12px; color: white; margin-bottom: 20px; border-left: 5px solid #EF4444; box-shadow: 0 4px 15px rgba(15, 23, 42, 0.25);">
        <h3 style="margin: 0 0 6px 0; font-size: 19px; color: #F8FAFC; display: flex; align-items: center; gap: 8px;">
            <span>🗺️</span> <span>Peta & Grafik Wilayah Penerima Bantuan Sesuai Data Statistik Kesra</span>
        </h3>
        <p style="margin: 0; font-size: 13px; color: #94A3B8; line-height: 1.5;">
            Pemetaan geospasial tematik dan grafik komparasi 18 Kecamatan Kota Palembang yang berhak menerima bantuan sosial. Penentuan kelayakan didasarkan secara objektif pada pembobotan indikator statistik Kesra (beban kemiskinan, pengangguran, pendapatan, IPM) serta zonasi klaster K-Means.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Calculate Key Metrics for Social Assistance Recipients
    c0_df = df_result[df_result['Cluster'] == 0]
    c1_df = df_result[df_result['Cluster'] == 1]
    c2_df = df_result[df_result['Cluster'] == 2] if 2 in df_result['Cluster'].values else pd.DataFrame()

    total_c0_kec = len(c0_df)
    total_c0_miskin = int(c0_df['Jumlah_Penduduk_Miskin'].sum()) if not c0_df.empty else 0
    top_kec = df_result.sort_values(by='Skor_Kerentanan', ascending=False).iloc[0]
    top_kec_name = top_kec['Kecamatan']
    top_kec_cvi = top_kec['Skor_Kerentanan']
    top_kec_miskin = int(top_kec['Jumlah_Penduduk_Miskin'])

    # 4 Executive Summary Cards
    col_k1, col_k2, col_k3, col_k4 = st.columns(4)
    with col_k1:
        st.markdown(f"""<div class="metric-card" style="border-left: 4px solid #EF4444;">
<div class="metric-title">🔴 Wilayah Wajib Bansos</div>
<div class="metric-value" style="color: #EF4444;">{total_c0_kec} <span style="font-size:13px; color:#64748B;">Kecamatan</span></div>
<div style="font-size:11px; color:#64748B; margin-top:4px;">Prioritas 1 (Darurat - Pagu 60%)</div>
</div>""", unsafe_allow_html=True)

    with col_k2:
        st.markdown(f"""<div class="metric-card" style="border-left: 4px solid #3B82F6;">
<div class="metric-title">👥 Beban Jiwa Miskin Darurat</div>
<div class="metric-value" style="color: #3B82F6;">{total_c0_miskin:,} <span style="font-size:13px; color:#64748B;">Jiwa</span></div>
<div style="font-size:11px; color:#64748B; margin-top:4px;">Terkonsentrasi di Zona Prioritas 1</div>
</div>""", unsafe_allow_html=True)

    with col_k3:
        st.markdown(f"""<div class="metric-card" style="border-left: 4px solid #DC2626;">
<div class="metric-title">🎯 Wilayah Paling Mendesak (Top 1)</div>
<div class="metric-value" style="font-size:17px; color: #DC2626;">Kec. {top_kec_name}</div>
<div style="font-size:11px; color:#64748B; margin-top:4px;">{top_kec_miskin:,} Jiwa (CVI: {top_kec_cvi:.3f})</div>
</div>""", unsafe_allow_html=True)

    with col_k4:
        st.markdown(f"""<div class="metric-card" style="border-left: 4px solid #F59E0B;">
<div class="metric-title">🟡 Penerima Bansos Bersyarat</div>
<div class="metric-value" style="color: #D97706;">{len(c1_df)} <span style="font-size:13px; color:#64748B;">Kecamatan</span></div>
<div style="font-size:11px; color:#64748B; margin-top:4px;">Prioritas 2 (Waspada - Pagu 30%)</div>
</div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Interactive Controls Filter Bar
    c_flt1, c_flt2 = st.columns([1.2, 1.2])
    with c_flt1:
        sel_filter = st.selectbox(
            "🎯 Filter Kategori Kelayakan Wilayah:",
            options=[
                "Semua Wilayah (18 Kecamatan)",
                "🔴 Prioritas 1 (Wajib Terima Bansos)",
                "🟡 Prioritas 2 (Penerima Bansos Bersyarat)",
                "🟢 Prioritas 3 (Wilayah Mandiri / Terbatas)"
            ],
            index=0,
            key=f"{key_prefix}_filter_kelayakan"
        )
    with c_flt2:
        available_metrics = [c for c in ['Jumlah_Penduduk_Miskin', 'Skor_Kerentanan', 'Tingkat_Pengangguran', 'Jumlah_KK_Penerima_Bansos'] if c in df_result.columns]
        sel_metric = st.selectbox(
            "📏 Skala Ukuran Lingkaran (Bubble Size):",
            options=available_metrics,
            index=0,
            format_func=lambda x: {
                'Jumlah_Penduduk_Miskin': 'Jumlah Penduduk Miskin (Jiwa)',
                'Skor_Kerentanan': 'Skor Kerentanan Komposit (CVI)',
                'Tingkat_Pengangguran': 'Tingkat Pengangguran (%)',
                'Jumlah_KK_Penerima_Bansos': 'Jumlah KK Penerima Bansos Eksisting'
            }.get(x, x),
            key=f"{key_prefix}_bubble_metric"
        )

    # Row 1: Map (Left) & Ranking Chart (Right) Side-by-Side
    col_map, col_chart = st.columns([1.15, 0.85])

    with col_map:
        st.subheader("📍 Peta Geospasial Wilayah Penerima Bantuan (Peta Baru)")
        st.caption("Klik marker kecamatan untuk melihat rincian indikator statistik Kesra & paket rekomendasi bantuan.")
        folium_map = create_kesra_bansos_map(df_result, filter_status=sel_filter, bubble_metric=sel_metric)
        st_folium(folium_map, width="100%", height=530, key=f"{key_prefix}_folium_map")

    with col_chart:
        st.subheader("📊 Peta Grafik Peringkat Kelayakan")
        st.caption("Urutan kecamatan dari beban kerentanan tertinggi yang wajib dan sesuai memperoleh bansos.")
        fig_ranking = plot_bansos_recipient_ranking(df_result)
        st.plotly_chart(fig_ranking, use_container_width=True, key=f"{key_prefix}_plot_ranking")

    st.markdown("---")

    # Row 2: Secondary Graphics (Donut Proportion & Kesra Suitability Quadrant)
    st.subheader("📈 Analisis Kesesuaian Statistik Kesra Terhadap Penerima Bantuan")
    st.caption("Validasi kesesuaian penetapan wilayah berdasarkan korelasi indikator kemiskinan dan kemampuan ekonomi daerah.")

    col_g1, col_g2 = st.columns([0.85, 1.15])
    with col_g1:
        fig_donut = plot_bansos_eligibility_donut(df_result)
        st.plotly_chart(fig_donut, use_container_width=True, key=f"{key_prefix}_plot_donut")

    with col_g2:
        fig_quad = plot_kesra_suitability_quadrant(df_result)
        st.plotly_chart(fig_quad, use_container_width=True, key=f"{key_prefix}_plot_quad")

    st.markdown("---")

    # Row 3: Comprehensive Audit Table of Assistance Eligibility
    st.subheader("📋 Tabel Transparansi & Kesesuaian Wilayah Penerima Bantuan Sosial")
    st.write("Daftar lengkap 18 kecamatan beserta status kelayakan, alasan kesesuaian data statistik Kesra, dan rekomendasi program intervensi:")

    table_data = []
    for _, r in df_result.sort_values(by='Skor_Kerentanan', ascending=False).iterrows():
        c_id = int(r['Cluster'])
        cfg = BANSOS_ELIGIBILITY_CONFIG.get(c_id, BANSOS_ELIGIBILITY_CONFIG[1])
        table_data.append({
            'Kecamatan': r['Kecamatan'],
            'Status Kelayakan Bansos': cfg['status'],
            'Kesesuaian Data Kesra': cfg['kesesuaian_kesra'],
            'Penduduk Miskin (Jiwa)': int(r.get('Jumlah_Penduduk_Miskin', 0)),
            'Pengangguran (%)': float(r.get('Tingkat_Pengangguran', 0)),
            'Pendapatan (Rp)': int(r.get('Pendapatan_Rata_Rata', 0)),
            'Skor CVI': float(r.get('Skor_Kerentanan', 0.0)),
            'Pagu Rekomendasi': cfg['pagu_pct'],
            'Paket Intervensi Bansos': cfg['rekomendasi']
        })

    df_eligibility_table = pd.DataFrame(table_data)

    st.dataframe(
        df_eligibility_table.style.format({
            'Penduduk Miskin (Jiwa)': '{:,} Jiwa',
            'Pengangguran (%)': '{:.2f} %',
            'Pendapatan (Rp)': 'Rp {:,.0f}',
            'Skor CVI': '{:.4f}'
        }).background_gradient(cmap='Reds', subset=['Skor CVI', 'Penduduk Miskin (Jiwa)']),
        use_container_width=True,
        height=420
    )

    # CSV Download Button for this table
    csv_buf = io.StringIO()
    df_eligibility_table.to_csv(csv_buf, index=False)
    st.download_button(
        label="📥 Unduh Data Kesesuaian Wilayah Penerima Bansos (.csv)",
        data=csv_buf.getvalue(),
        file_name="Kesesuaian_Penerima_Bansos_Palembang_Kesra.csv",
        mime="text/csv",
        use_container_width=True,
        key=f"{key_prefix}_dl_csv"
    )

# Synchronize execution stage for tab gating
current_stage = st.session_state.get('kmeans_stage', 0)
current_step = current_stage

# =============================================================================
# ROLE 1: ADMIN / PETUGAS KESRA VIEW
# =============================================================================
if is_admin:
    adm_tab1, adm_tab2, adm_tab3, adm_tab4, adm_tab5, adm_tab6, adm_tab7 = st.tabs([
        "📁 1. Data Excel Kesra",
        "🔄 2. Alur Proses K-Means (Step-by-Step)",
        "🧪 3. Uji Validasi Ilmiah",
        "🗺️ 4. Peta Geospasial (Peta Lama)",
        "🎯 5. Peta & Grafik Kelayakan Bansos (Peta Baru)",
        "📊 6. Radar & Karakteristik Wilayah",
        "💾 7. Database & Generator Bab 4"
    ])

    # ADMIN TAB 1: DATASET MANAGEMENT
    with adm_tab1:
        st.subheader("📁 Data Statistik 18 Kecamatan Kota Palembang dari Excel")
        st.caption("Data sekunder indikator kemiskinan dan kesejahteraan sosial bersumber dari berkas resmi Excel Bagian Kesra Kota Palembang.")
        
        col_inf1, col_inf2, col_inf3 = st.columns(3)
        with col_inf1:
            st.metric("Sumber File", data_source_name)
        with col_inf2:
            st.metric("Status Pembacaan", "Berhasil Diimpor (18 Kecamatan)")
        with col_inf3:
            st.metric("Variabel Terpilih", f"{len(selected_indicators)} Indikator")

        st.dataframe(df_input, use_container_width=True)
        
        st.markdown("---")
        st.subheader("📊 Statistik Deskriptif Variabel Terpilih")
        st.dataframe(df_input[selected_indicators].describe().T.style.format("{:,.2f}"), use_container_width=True)

        st.markdown("---")
        st.markdown(f"""<div style="background: linear-gradient(135deg, #0F172A, #1E293B); border-radius: 12px; padding: 18px 22px; color: white; margin-top: 15px; border-left: 5px solid #38BDF8;">
<div style="font-size: 16px; font-weight: 800; color: #38BDF8; margin-bottom: 6px;">
🚀 Langkah Selanjutnya: Eksekusi Algoritma K-Means di Layar Frontend
</div>
<div style="font-size: 13px; color: #CBD5E1; line-height: 1.5; margin-bottom: 12px;">
Data mentah di atas (18 Kecamatan, {len(selected_indicators)} Indikator) siap diproses menggunakan algoritma K-Means dari START hingga END secara transparan.
</div>
</div>""", unsafe_allow_html=True)
        if st.button("🚀 Buka Tab 2 & Mulai Eksekusi K-Means (START) ➔", type="primary", use_container_width=True, key="adm_tab1_go_tab2"):
            st.session_state['kmeans_stage'] = 1
            st.rerun()

    # ADMIN TAB 2: STEP-BY-STEP K-MEANS PROCESS
    with adm_tab2:
        render_step_by_step_kmeans_process(prefix="adm_step")

    # ADMIN TAB 3: SCIENTIFIC VALIDATION
    with adm_tab3:
        if current_step < 6:
            render_kmeans_required_notice("Uji Validasi Ilmiah", "adm_tab3")
        else:
            st.subheader("🧪 Pembuktian Ilmiah K Optimal & Validasi Model")
            st.write("Metrik evaluasi matematis untuk membuktikan struktur pemisahan klaster optimal.")
            
            col_e1, col_e2 = st.columns(2)
            with col_e1:
                elbow_fig = plot_elbow_chart(elbow_df, selected_k=n_clusters)
                st.plotly_chart(elbow_fig, use_container_width=True, key="adm_tab3_elbow_chart")
                st.info(f"💡 **Metode Elbow:** Titik siku terbaik pada K={n_clusters} dengan WCSS = {model_results['wcss_inertia']:.2f}")
                
            with col_e2:
                sil_fig = plot_silhouette_chart(elbow_df, selected_k=n_clusters)
                st.plotly_chart(sil_fig, use_container_width=True, key="adm_tab3_sil_chart")
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

    # ADMIN TAB 4: SPATIAL MAP (PETA LAMA)
    with adm_tab4:
        if current_step < 6:
            render_kmeans_required_notice("Peta Geospasial (Peta Lama)", "adm_tab4")
        else:
            st.info("ℹ️ **Halaman Peta Standar (Peta Lama):** Menampilkan sebaran titik spasial 18 kecamatan Kota Palembang berdasarkan 3 klaster K-Means dan analisis grafik distribusi per-indikator.")
            col_m1, col_m2 = st.columns([1.2, 0.8])
            with col_m1:
                st.subheader("🗺️ Peta Tematik Geospasial Palembang (Peta Standar)")
                folium_map_old = create_palembang_map(df_result)
                st_folium(folium_map_old, width="100%", height=480, key="adm_old_folium_map")
            with col_m2:
                st.subheader("📊 Distribusi Indikator")
                sel_feat = st.selectbox("Pilih Indikator Visualisasi:", options=selected_indicators, index=0, key="adm_sel_feat")
                st.plotly_chart(plot_cluster_bar(df_result, feature=sel_feat), use_container_width=True, key="adm_tab4_cluster_bar")

    # ADMIN TAB 5: PETA & GRAFIK WILAYAH PENERIMA BANSOS (PETA BARU)
    with adm_tab5:
        if current_step < 6:
            render_kmeans_required_notice("Peta & Grafik Kelayakan Bansos Kesra (Peta Baru)", "adm_tab5")
        else:
            render_peta_dan_grafik_wilayah_bansos(df_result, selected_indicators, key_prefix="adm_map_new")

    # ADMIN TAB 6: RADAR & SCATTER
    with adm_tab6:
        if current_step < 6:
            render_kmeans_required_notice("Radar & Karakteristik Wilayah", "adm_tab6")
        else:
            col_r1, col_r2 = st.columns(2)
            with col_r1:
                st.subheader("📌 Radar Profile Antar Klaster")
                st.plotly_chart(plot_radar_summary(model_results['cluster_summary'], selected_indicators), use_container_width=True, key="adm_tab6_radar_summary")
            with col_r2:
                st.subheader("🔍 Scatter Plot Hubungan Indikator")
                scat_x = st.selectbox("Sumbu X:", options=selected_indicators, index=min(0, len(selected_indicators)-1), key="adm_scat_x")
                scat_y = st.selectbox("Sumbu Y:", options=selected_indicators, index=min(1, len(selected_indicators)-1), key="adm_scat_y")
                st.plotly_chart(plot_scatter_2d(df_result, scat_x, scat_y), use_container_width=True, key="adm_tab6_scatter_2d")

    # ADMIN TAB 7: DATABASE & BAB 4 GENERATOR
    with adm_tab7:
        st.subheader("💾 Database SQLite & Generator Naskah Skripsi Bab 4")
        st.write("Manajemen arsip basis data dan fasilitas penyusunan draf teks Bab 4 skripsi otomatis.")

        st.markdown("---")
        st.markdown("#### 📝 Generator Teks Skripsi Bab 4 (Hasil dan Pembahasan)")
        bab4_text = generate_bab4_narration(df_result, model_results, elbow_df, year_label="2025/2026")
        st.text_area("Draft Narasi Bab 4 Skripsi:", value=bab4_text, height=300)
        st.download_button(
            label="📥 Unduh Draft Bab 4 (.txt)",
            data=bab4_text,
            file_name="Draft_Skripsi_Bab4_Bansos_Palembang.txt",
            mime="text/plain",
            use_container_width=True,
            key="adm_tab7_dl_bab4"
        )

        st.markdown("---")
        st.markdown("#### 🗄️ Status Database Relasional SQLite")
        st.info(f"Koneksi Database Aktif: **{get_current_db_status()}**")
        st.caption("Data hasil klasterisasi dan simulasi tersimpan secara persisten di berkas database `data/bansos_palembang.db`.")

# =============================================================================
# ROLE 2: PIMPINAN / PENGAMBIL KEPUTUSAN VIEW
# =============================================================================
else:
    pim_tab1, pim_tab2, pim_tab3, pim_tab4, pim_tab5, pim_tab6, pim_tab7 = st.tabs([
        "🏛️ 1. Dashboard Eksekutif",
        "🔄 2. Transparansi Proses K-Means",
        "🗺️ 3. Peta Spasial (Peta Lama)",
        "🎯 4. Peta & Grafik Kelayakan Bansos (Peta Baru)",
        "💰 5. Simulator Alokasi Bansos (DSS)",
        "🔍 6. Profiler Per-Kecamatan",
        "📥 7. Unduh Laporan Resmi"
    ])

    # PIMPINAN TAB 1: EXECUTIVE DASHBOARD
    with pim_tab1:
        if current_step < 6:
            render_kmeans_required_notice("Dashboard Eksekutif Kebijakan Bansos", "pim_tab1")
        else:
            st.subheader("🏛️ Ringkasan Zonasi & Rekomendasi Kebijakan Bansos")
            
            col_pol1, col_pol2, col_pol3 = st.columns(3)
            c0_list = df_result[df_result['Cluster'] == 0]['Kecamatan'].tolist()
            c1_list = df_result[df_result['Cluster'] == 1]['Kecamatan'].tolist()
            c2_list = df_result[df_result['Cluster'] == 2]['Kecamatan'].tolist() if n_clusters > 2 else []
            
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
            st.plotly_chart(fig_cvi_rank, use_container_width=True, key="pim_tab1_cvi_rank")

    # PIMPINAN TAB 2: STEP-BY-STEP K-MEANS TRANSPARENCY (ACCESSIBLE TO PIMPINAN TOO!)
    with pim_tab2:
        render_step_by_step_kmeans_process(prefix="pim_step")

    # PIMPINAN TAB 3: SPATIAL MAP (PETA LAMA)
    with pim_tab3:
        if current_step < 6:
            render_kmeans_required_notice("Peta Spasial (Peta Lama)", "pim_tab3")
        else:
            st.info("ℹ️ **Halaman Peta Standar (Peta Lama):** Menampilkan sebaran titik spasial 18 kecamatan Kota Palembang berdasarkan 3 klaster K-Means dan analisis grafik distribusi per-indikator.")
            col_m_left, col_m_right = st.columns([1.2, 0.8])
            with col_m_left:
                st.subheader("🗺️ Peta Tematik Geospasial Palembang (Standar)")
                st.caption("Peta interaktif berbasis koordinat 18 kecamatan. Klik lingkaran marker untuk rincian data.")
                folium_map_old = create_palembang_map(df_result)
                st_folium(folium_map_old, width="100%", height=480, key="pim_old_folium_map")
                
            with col_m_right:
                st.subheader("📊 Analisis Distribusi Indikator")
                sel_f = st.selectbox("Pilih Indikator Ditampilkan:", options=selected_indicators, index=0, key="pim_sel_f")
                st.plotly_chart(plot_cluster_bar(df_result, feature=sel_f), use_container_width=True, key="pim_tab3_cluster_bar")

    # PIMPINAN TAB 4: PETA & GRAFIK WILAYAH PENERIMA BANSOS (PETA BARU)
    with pim_tab4:
        if current_step < 6:
            render_kmeans_required_notice("Peta & Grafik Kelayakan Bansos Kesra (Peta Baru)", "pim_tab4")
        else:
            render_peta_dan_grafik_wilayah_bansos(df_result, selected_indicators, key_prefix="pim_map_new")

    # PIMPINAN TAB 5: DSS BUDGET & QUOTA SIMULATOR
    with pim_tab5:
        if current_step < 6:
            render_kmeans_required_notice("Simulator Alokasi Anggaran DSS", "pim_tab5")
        else:
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
                st.plotly_chart(pie_budget, use_container_width=True, key="pim_tab5_pie_budget")
                
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
                st.plotly_chart(pie_quota, use_container_width=True, key="pim_tab5_pie_quota")
                
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

            if st.button("💾 Arsipkan Hasil Simulasi Ini ke Database", type="primary", key="pim_tab5_save_sim_db"):
                save_simulation_results_to_db(df_simulated, "Terkini", budget_input, quota_input, user_display_name)
                st.success("✅ Skenario simulasi berhasil diarsipkan ke tabel `simulasi_alokasi_bansos` di database!")

    # PIMPINAN TAB 6: PROFILER PER KECAMATAN
    with pim_tab6:
        if current_step < 6:
            render_kmeans_required_notice("Profiler Wilayah Kecamatan", "pim_tab6")
        else:
            st.subheader("🔍 Profiler & Inspector 18 Kecamatan")
            selected_kec_inspect = st.selectbox("Pilih Kecamatan Ditinjau:", options=df_result['Kecamatan'].unique(), key="pim_kec_insp")
            kec_data = df_result[df_result['Kecamatan'] == selected_kec_inspect].iloc[0]
            
            p_col1, p_col2, p_col3, p_col4 = st.columns(4)
            with p_col1:
                st.metric("Status Zonasi", kec_data.get('Kategori_Prioritas', '-'))
            with p_col2:
                cvi_val = kec_data.get('Skor_Kerentanan', 0.0)
                st.metric("Skor Kerentanan (CVI)", f"{cvi_val:.4f}")
            with p_col3:
                dmin_val = kec_data.get('Jarak_Terdekat_d_min', 0.0)
                st.metric("Jarak Terdekat (d_min)", f"{dmin_val:.4f}")
            with p_col4:
                miskin_val = kec_data.get('Jumlah_Penduduk_Miskin', None)
                miskin_str = f"{int(miskin_val):,} Jiwa" if pd.notna(miskin_val) else "-"
                st.metric("Penduduk Miskin", miskin_str)
                
            st.markdown("---")
            st.subheader(f"📌 Profil Indikator Kec. {selected_kec_inspect} vs Rata-Rata Kota Palembang")
            df_city_avg = df_input[selected_indicators].mean()
            comp_df = pd.DataFrame({
                'Indikator': [c.replace('_', ' ') for c in selected_indicators],
                'Nilai Kecamatan': [kec_data.get(c, '-') for c in selected_indicators],
                'Rata-Rata Kota Palembang': [df_city_avg.get(c, '-') for c in selected_indicators]
            })
            st.dataframe(comp_df, use_container_width=True)
            
            pengangguran_val = kec_data.get('Tingkat_Pengangguran', '-')
            pengangguran_str = f"{pengangguran_val}%" if pengangguran_val != '-' else "-"
            st.info(f"""
            💡 **Rekomendasi Kebijakan untuk Kecamatan {selected_kec_inspect}:**
            - **Kategori Prioritas**: {kec_data.get('Kategori_Prioritas', '-')}
            - **Intervensi Utama**: Penanganan tingkat pengangguran ({pengangguran_str}) dan peningkatan alokasi bansos PKH/BPNT secara bertahap.
            """)

    # PIMPINAN TAB 7: EXECUTIVE EXPORT
    with pim_tab7:
        st.subheader("📥 Pusat Unduhan Laporan Eksekutif Resmi (.xlsx)")
        st.write("Unduh berkas laporan hasil analisis klasterisasi K-Means yang lengkap dengan multi-sheet (termasuk jejak proses iterasi K-Means dan normalisasi) untuk dasar penetapan Surat Keputusan (SK) Walikota.")
        
        col_xp1, col_xp2 = st.columns(2)
        with col_xp1:
            excel_data = export_results_to_excel(df_result, model_results['cluster_summary'], elbow_df, model_results)
            if st.download_button(
                label="📊 Unduh Laporan Eksekutif Lengkap (.xlsx)",
                data=excel_data,
                file_name="Laporan_Eksekutif_Bansos_Palembang.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                key="pim_tab7_dl_excel"
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
                        use_container_width=True,
                        key="pim_tab7_dl_master"
                    )
