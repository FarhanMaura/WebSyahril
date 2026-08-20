import streamlit as st
from database import authenticate_user, get_user_by_username, get_current_db_status

def init_auth_session():
    """Initializes session state and restores session from query params if page was hard refreshed."""
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False
    if 'user_info' not in st.session_state:
        st.session_state['user_info'] = None

    # Persistent session restoration on browser refresh (F5 / Ctrl+R)
    if not st.session_state['authenticated']:
        saved_user = st.query_params.get("user", None)
        if saved_user:
            user = get_user_by_username(saved_user)
            if user:
                st.session_state['authenticated'] = True
                st.session_state['user_info'] = user

def login_user(username, password):
    """Attempts login against database and sets persistent query parameter."""
    user = authenticate_user(username, password)
    if user:
        st.session_state['authenticated'] = True
        st.session_state['user_info'] = user
        st.query_params["user"] = user['username']
        return True
    return False

def logout_user():
    """Clears authentication session state and query parameters."""
    st.session_state['authenticated'] = False
    st.session_state['user_info'] = None
    try:
        st.query_params.clear()
    except Exception:
        pass
    st.rerun()

def render_login_page():
    """Renders a stunning modern login portal with zero indentation markdown errors."""
    db_status = get_current_db_status()
    
    # Custom CSS without code block indentation bugs
    st.markdown("""<style>
.login-card {
    background: #FFFFFF;
    padding: 28px 32px;
    border-radius: 18px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
    border: 1px solid #E2E8F0;
}
.dark-card {
    background: #0F172A;
    color: white;
    padding: 28px 32px;
    border-radius: 18px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
    border: 1px solid #1E293B;
}
.actor-badge-adm {
    display: inline-block;
    background: #EFF6FF;
    color: #1D4ED8;
    border: 1px solid #BFDBFE;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 700;
    margin-bottom: 8px;
}
.actor-badge-pim {
    display: inline-block;
    background: #ECFDF5;
    color: #047857;
    border: 1px solid #A7F3D0;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 700;
    margin-bottom: 8px;
}
.info-row {
    background: #F8FAFC;
    border-radius: 12px;
    padding: 14px 18px;
    margin-bottom: 12px;
    border: 1px solid #E2E8F0;
}
</style>""", unsafe_allow_html=True)

    col1, col2 = st.columns([1.1, 0.9], gap="large")

    with col1:
        st.markdown("""<div class="login-card">
<h3 style="margin: 0 0 6px 0; color: #0F172A; font-weight: 800;">🔐 Portal Masuk Sistem DSS Bansos</h3>
<p style="font-size: 13px; color: #64748B; margin: 0 0 20px 0;">Silakan autentikasi sesuai peran aktor untuk membuka wewenang sistem.</p>
</div>""", unsafe_allow_html=True)

        with st.form("login_form"):
            username_input = st.text_input("👤 Username", placeholder="Ketik admin atau pimpinan")
            password_input = st.text_input("🔑 Password", type="password", placeholder="Ketik kata sandi")
            submit_btn = st.form_submit_button("🚀 Masuk ke Sistem", use_container_width=True, type="primary")

            if submit_btn:
                if login_user(username_input, password_input):
                    st.success("✅ Autentikasi berhasil! Mengalihkan ke dashboard...")
                    st.rerun()
                else:
                    st.error("❌ Username atau Password salah! Periksa kembali kredensial Anda.")

        st.markdown("---")
        st.markdown("⚡ **Tombol Quick-Login Demo (1-Klik untuk Sidang / Demo):**")
        qcol1, qcol2 = st.columns(2)
        with qcol1:
            if st.button("👨‍💻 Masuk sbg Admin Kesra", use_container_width=True):
                login_user("admin", "admin123")
                st.rerun()
        with qcol2:
            if st.button("🏛️ Masuk sbg Pimpinan", use_container_width=True):
                login_user("pimpinan", "pimpinan123")
                st.rerun()

        st.caption(f"Status Koneksi: {db_status}")

    with col2:
        st.markdown("""<div class="login-card" style="background: #F8FAFC;">
<h4 style="margin: 0 0 14px 0; color: #0F172A; font-weight: 800;">👥 Hak Akses Aktor Sistem (Sesuai Usecase Diagram)</h4>

<div class="info-row">
<span class="actor-badge-adm">AKTOR 1: Admin / Petugas Kesra</span>
<div style="font-size: 13px; font-weight: 700; color: #1E293B; margin-bottom: 4px;">Fokus: Manajemen Data & Engine K-Means AI</div>
<div style="font-size: 12px; color: #475569; line-height: 1.6;">
• Kelola & Upload Dataset BPS (CSV/Excel)<br>
• Konfigurasi parameter K & Pemrosesan Klasterisasi K-Means<br>
• Analisis Jarak Euclidean multidimensi d(x, c)<br>
• Uji Validasi Ilmiah (Elbow WCSS, Silhouette Score, DBI, CHI)<br>
• Sinkronisasi & Arsip Hasil ke Database
</div>
<div style="font-size: 11px; color: #2563EB; font-weight: 600; margin-top: 6px;">Kredensial: admin / admin123</div>
</div>

<div class="info-row" style="margin-bottom: 0;">
<span class="actor-badge-pim">AKTOR 2: Pimpinan / Pengambil Keputusan</span>
<div style="font-size: 13px; font-weight: 700; color: #1E293B; margin-bottom: 4px;">Fokus: Rekomendasi Kebijakan & Simulasi Anggaran DSS</div>
<div style="font-size: 12px; color: #475569; line-height: 1.6;">
• <b>Pejabat Berwenang:</b> Kabag Kesra (H. Sodikin, S.Ag., M.Si.) & Wali Kota Palembang (Drs. H. Ratu Dewa, M.Si.)<br>
• Telaah Dashboard Eksekutif Zonasi Wilayah Darurat Bansos<br>
• Eksplorasi Peta Tematik Geospasial 18 Kecamatan Palembang<br>
• <b>Simulator Alokasi Anggaran (Rp) & Kuota (KK) Bansos</b><br>
• Profiler Detail Komparasi Kecamatan vs Rata-Rata Kota<br>
• Unduh Laporan Eksekutif Resmi Multi-Sheet (.xlsx)
</div>
<div style="font-size: 11px; color: #059669; font-weight: 600; margin-top: 6px;">Kredensial: pimpinan / pimpinan123</div>
</div>

</div>""", unsafe_allow_html=True)

def render_sidebar_user_badge():
    """Renders active user identity and logout button in sidebar."""
    user = st.session_state.get('user_info')
    if not user:
        return
    
    role = user.get('role', 'Pengguna')
    is_admin = 'Admin' in role
    badge_bg = '#EFF6FF' if is_admin else '#ECFDF5'
    badge_color = '#1D4ED8' if is_admin else '#047857'
    role_icon = '👨‍💻' if is_admin else '🏛️'

    st.sidebar.markdown(f"""<div style="background: {badge_bg}; border-radius: 14px; padding: 14px 16px; border: 1px solid rgba(0,0,0,0.06); margin-bottom: 16px;">
<div style="font-size: 11px; font-weight: 800; text-transform: uppercase; color: {badge_color}; margin-bottom: 4px;">
{role_icon} LOGGED IN AS:
</div>
<div style="font-size: 14px; font-weight: 800; color: #0F172A;">
{user.get('nama_lengkap', 'User')}
</div>
<div style="font-size: 11px; color: #047857; font-weight: 600; margin-top: 2px;">
{user.get('jabatan', '')}
</div>
<div style="font-size: 11px; color: #64748B; margin-top: 2px;">
{user.get('instansi', 'Pemerintah Kota Palembang')}
</div>
</div>""", unsafe_allow_html=True)

    if st.sidebar.button("🚪 Keluar (Logout)", use_container_width=True):
        logout_user()

def render_pimpinan_role_explainer():
    """Renders an executive guide banner with real Palembang leadership info."""
    st.markdown("""<div style="background: linear-gradient(135deg, #064E3B 0%, #065F46 100%); color: white; padding: 22px 26px; border-radius: 16px; margin-bottom: 22px; box-shadow: 0 10px 25px -5px rgba(6, 78, 59, 0.3);">
<div style="font-size: 18px; font-weight: 800; margin-bottom: 6px;">
🏛️ Portal Pengambilan Keputusan Eksekutif Pemerintah Kota Palembang
</div>
<div style="font-size: 13px; color: #A7F3D0; margin-bottom: 10px;">
Pejabat Pembuat Kebijakan: <b>Wali Kota Palembang (Drs. H. Ratu Dewa, M.Si.)</b> & <b>Kabag Kesra Setda (H. Sodikin, S.Ag., M.Si.)</b>
</div>
<div style="font-size: 13px; color: #E2E8F0; line-height: 1.6;">
Sistem Pendukung Keputusan (DSS) ini dirancang untuk memastikan penyaluran bantuan sosial <b>tepat sasaran, transparan, dan berbasis data ilmiah</b>:
<br>
1. <b>Zonasi Darurat & Prioritas:</b> Mengidentifikasi kecamatan paling rentan secara spasial untuk mendapatkan kuota alokasi utama.
<br>
2. <b>Simulasi Pagu Dana & Kuota Penerima:</b> Pimpinan memasukkan total anggaran (Rp) dan kuota (KK), sistem secara otomatis menghitung pembagian nominal yang proporsional dan berkeadilan.
<br>
3. <b>Penetapan Kebijakan Resmi:</b> Seluruh kalkulasi dapat langsung diekspor ke format Excel resmi (.xlsx) sebagai lampiran dasar penetapan Surat Keputusan (SK) Walikota.
</div>
</div>""", unsafe_allow_html=True)
