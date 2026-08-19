import os
import html
import subprocess
import glob
import shutil

WIDTH = 1280
HEIGHT = 880
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

def esc(text):
    return html.escape(str(text))

def base_layout(active_tab=0):
    """
    Generates the exact low-fidelity wireframe blueprint (kotak-kotak polosan skripsi)
    100% matched with the actual Streamlit DSS application (app.py) and Skripsi M. Syahril.
    """
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" width="{WIDTH}" height="{HEIGHT}">')
    svg.append('<defs>')
    svg.append('  <style>')
    svg.append('    text { font-family: "Arial", "Helvetica", sans-serif; }')
    svg.append('    .box { fill: #F4F4F4; stroke: #000000; stroke-width: 1.8; }')
    svg.append('    .box-white { fill: #FFFFFF; stroke: #000000; stroke-width: 1.4; }')
    svg.append('    .box-active { fill: #DCDCDC; stroke: #000000; stroke-width: 2.0; font-weight: bold; }')
    svg.append('    .line { stroke: #000000; stroke-width: 1.4; }')
    svg.append('    .lbl-title { font-size: 12px; font-weight: bold; fill: #000000; text-anchor: middle; }')
    svg.append('    .lbl-header { font-size: 15.5px; font-weight: bold; fill: #000000; text-anchor: middle; letter-spacing: 0.5px; }')
    svg.append('    .lbl-sub { font-size: 9.5px; font-weight: bold; fill: #000000; text-anchor: middle; }')
    svg.append('    .lbl-left { font-size: 10px; font-weight: bold; fill: #000000; }')
    svg.append('    .lbl-small { font-size: 8.5px; fill: #000000; }')
    svg.append('  </style>')
    svg.append('</defs>')

    # 1. Canvas Outer Border
    svg.append(f'<rect x="2" y="2" width="{WIDTH-4}" height="{HEIGHT-4}" fill="#FFFFFF" stroke="#000000" stroke-width="2.5"/>')

    # 2. Main Application Header Box (Exact app.py)
    hdr_h = 75
    svg.append(f'<rect x="2" y="2" width="{WIDTH-4}" height="{hdr_h}" class="box"/>')
    svg.append(f'<text x="{WIDTH/2}" y="24" class="lbl-header">HEADER SISTEM</text>')
    svg.append(f'<text x="{WIDTH/2}" y="42" font-size="13px" font-weight="bold" fill="#000000" text-anchor="middle">DSS PEMETAAN WILAYAH PENERIMA BANTUAN SOSIAL KOTA PALEMBANG</text>')
    svg.append(f'<text x="{WIDTH/2}" y="57" font-size="9.5px" fill="#444444" text-anchor="middle">Sistem Pendukung Keputusan Berbasis Algoritma K-Means Clustering Menggunakan Data Pemutakhiran Bagian Kesra &amp; BPS Kota Palembang</text>')
    svg.append(f'<text x="{WIDTH/2}" y="70" font-size="9px" font-weight="bold" fill="#000000" text-anchor="middle">[ BADGE: M. Syahril (NIM: 221420089) | Mitra Data: Bagian Kesra &amp; BPS Kota Palembang ]</text>')

    # 3. Horizontal Navigation Bar (6 Tabs - Exact app.py)
    nav_y = 77
    nav_h = 34
    tabs = [
        "DASHBOARD & PETA",
        "SIMULATOR DSS",
        "ANALISIS TREN",
        "PROFILER KECAMATAN",
        "MATRIKS EUCLIDEAN",
        "VALIDASI & EXPORT"
    ]
    tab_w = (WIDTH - 4) / 6
    for i, tname in enumerate(tabs):
        tx = 2 + i * tab_w
        cls = "box-active" if i == active_tab else "box-white"
        svg.append(f'<rect x="{tx}" y="{nav_y}" width="{tab_w}" height="{nav_h}" class="{cls}"/>')
        fw = "bold" if i == active_tab else "normal"
        svg.append(f'<text x="{tx+tab_w/2}" y="{nav_y+21}" font-size="10.5" font-weight="{fw}" fill="#000000" text-anchor="middle">{tname}</text>')

    # 4. Left Sidebar (w=246, y=111, h=HEIGHT-113 - Exact app.py)
    sb_y = 111
    sb_w = 246
    sb_h = HEIGHT - sb_y - 2
    svg.append(f'<rect x="2" y="{sb_y}" width="{sb_w}" height="{sb_h}" class="box"/>')
    svg.append(f'<text x="{2+sb_w/2}" y="{sb_y+22}" class="lbl-title">SIDEBAR / CONTROL PANEL</text>')
    svg.append(f'<line x1="12" y1="{sb_y+30}" x2="{sb_w-8}" y2="{sb_y+30}" class="line"/>')

    # Sidebar 1: Pilih Edisi Data / Sumber Data (Radio)
    svg.append(f'<rect x="10" y="{sb_y+38}" width="{sb_w-18}" height="95" class="box-white"/>')
    svg.append(f'<text x="{2+sb_w/2}" y="{sb_y+54}" class="lbl-sub">PILIH SUMBER DATA</text>')
    svg.append(f'<text x="18" y="{sb_y+72}" class="lbl-small">[ o ] Data 2025/2026 (Pemutakhiran)</text>')
    svg.append(f'<text x="18" y="{sb_y+90}" class="lbl-small">[   ] Data 2023/2024 (Data Historis)</text>')
    svg.append(f'<text x="18" y="{sb_y+108}" class="lbl-small">[   ] Upload File CSV/Excel Custom</text>')
    svg.append(f'<text x="18" y="{sb_y+124}" font-size="8px" fill="#222222">[ STATUS: DATA 2025/2026 AKTIF ]</text>')

    # Sidebar 2: Unduh Master File Data Sekunder (Download Buttons)
    svg.append(f'<rect x="10" y="{sb_y+140}" width="{sb_w-18}" height="120" class="box-white"/>')
    svg.append(f'<text x="{2+sb_w/2}" y="{sb_y+156}" class="lbl-sub">UNDUH MASTER DATA SEKUNDER</text>')
    svg.append(f'<rect x="16" y="{sb_y+164}" width="{sb_w-30}" height="22" class="box"/>')
    svg.append(f'<text x="{2+sb_w/2}" y="{sb_y+178}" font-size="8.5px" font-weight="bold" fill="#000000" text-anchor="middle">[ Master Data Kesra 2025 (.xlsx) ]</text>')
    svg.append(f'<rect x="16" y="{sb_y+192}" width="{sb_w-30}" height="22" class="box"/>')
    svg.append(f'<text x="{2+sb_w/2}" y="{sb_y+206}" font-size="8.5px" font-weight="bold" fill="#000000" text-anchor="middle">[ Master Data Kesra 2023 (.xlsx) ]</text>')
    svg.append(f'<rect x="16" y="{sb_y+220}" width="{sb_w-30}" height="22" class="box"/>')
    svg.append(f'<text x="{2+sb_w/2}" y="{sb_y+234}" font-size="8.5px" font-weight="bold" fill="#000000" text-anchor="middle">[ Download Template CSV ]</text>')

    # Sidebar 3: Parameter K-Means (Slider K)
    svg.append(f'<rect x="10" y="{sb_y+268}" width="{sb_w-18}" height="68" class="box-white"/>')
    svg.append(f'<text x="{2+sb_w/2}" y="{sb_y+285}" class="lbl-sub">PARAMETER K-MEANS</text>')
    svg.append(f'<text x="{2+sb_w/2}" y="{sb_y+302}" class="lbl-small">Jumlah Cluster (K) = 3</text>')
    svg.append(f'<line x1="24" y1="{sb_y+315}" x2="{sb_w-22}" y2="{sb_y+315}" class="line"/>')
    svg.append(f'<circle cx="{62}" cy="{sb_y+315}" r="4" fill="#000000"/>')
    svg.append(f'<text x="24" y="{sb_y+327}" font-size="7.5px">K=2</text>')
    svg.append(f'<text x="{sb_w-22}" y="{sb_y+327}" font-size="7.5px" text-anchor="end">K=6</text>')

    # Sidebar 4: Atribut Terpilih (7 Indikator Resmi Skripsi M. Syahril / Table 3.2)
    svg.append(f'<rect x="10" y="{sb_y+344}" width="{sb_w-18}" height="255" class="box-white"/>')
    svg.append(f'<text x="{2+sb_w/2}" y="{sb_y+360}" class="lbl-sub">ATRIBUT TERPILIH (INDIKATOR BPS)</text>')
    svg.append(f'<text x="18" y="{sb_y+376}" font-size="8px" fill="#444444">Pilih Atribut Klasterisasi (Multiselect):</text>')
    
    # 7 REAL SKRIPSI INDICATORS (Table 3.2 Skripsi M. Syahril)
    ind_tags = [
        "[ x ] Jumlah Penduduk Miskin",
        "[ x ] Tingkat Pengangguran",
        "[ x ] Pendapatan Rata-Rata",
        "[ x ] Kepadatan Penduduk",
        "[ x ] Akses Fasilitas Publik",
        "[ x ] Jumlah KK Penerima Bansos",
        "[ x ] Indeks Pemb. Manusia (IPM)"
    ]
    for idx, itag in enumerate(ind_tags):
        ty = sb_y + 386 + idx * 28
        svg.append(f'<rect x="16" y="{ty}" width="{sb_w-30}" height="22" class="box"/>')
        svg.append(f'<text x="22" y="{ty+15}" font-size="8.5px" font-weight="bold" fill="#000000">{itag}</text>')

    # Sidebar 5: Info Peneliti & Pembimbing
    info_y = HEIGHT - 152
    svg.append(f'<rect x="10" y="{info_y}" width="{sb_w-18}" height="138" class="box-white"/>')
    svg.append(f'<text x="{2+sb_w/2}" y="{info_y+18}" class="lbl-sub">INFORMASI PENELITI</text>')
    svg.append(f'<text x="{2+sb_w/2}" y="{info_y+36}" font-size="9.5px" font-weight="bold" fill="#000000" text-anchor="middle">M. Syahril</text>')
    svg.append(f'<text x="{2+sb_w/2}" y="{info_y+50}" class="lbl-small" text-anchor="middle">NIM: 221420089</text>')
    svg.append(f'<text x="{2+sb_w/2}" y="{info_y+64}" class="lbl-small" text-anchor="middle">Program Studi Sistem Informasi</text>')
    svg.append(f'<text x="{2+sb_w/2}" y="{info_y+78}" class="lbl-small" text-anchor="middle">Fakultas Ilmu Komputer</text>')
    svg.append(f'<text x="{2+sb_w/2}" y="{info_y+92}" class="lbl-small" text-anchor="middle">Universitas Bina Darma</text>')
    svg.append(f'<text x="{2+sb_w/2}" y="{info_y+115}" font-size="8px" fill="#555555" text-anchor="middle">[ Mitra: Bagian Kesra Setda Palembang ]</text>')

    # Main Area coordinates
    main_x = 250
    main_w = WIDTH - main_x - 4
    main_y = sb_y + 4

    # Top 5 KPI Metrics Cards Row (Exact app.py)
    kpi_h = 50
    kpi_w = (main_w - 20) / 5
    kpi_items = [
        ("TOTAL WILAYAH (2025/2026)", "18 Kec."),
        ("PRIORITAS TINGGI (DARURAT)", "4 Kec."),
        ("PRIORITAS SEDANG", "8 Kec."),
        ("PRIORITAS RENDAH (MANDIRI)", "6 Kec."),
        ("SILHOUETTE SCORE", "0.542")
    ]
    for i, (ktitle, kval) in enumerate(kpi_items):
        kx = main_x + 4 + i * (kpi_w + 3)
        svg.append(f'<rect x="{kx}" y="{main_y}" width="{kpi_w}" height="{kpi_h}" class="box-white"/>')
        svg.append(f'<text x="{kx+kpi_w/2}" y="{main_y+18}" font-size="8.5" font-weight="bold" fill="#000000" text-anchor="middle">{ktitle}</text>')
        svg.append(f'<text x="{kx+kpi_w/2}" y="{main_y+38}" font-size="12" font-weight="bold" fill="#000000" text-anchor="middle">[ {kval} ]</text>')

    content_y = main_y + kpi_h + 6
    content_h = HEIGHT - content_y - 6
    return svg, main_x, main_w, content_y, content_h

# ==============================================================================
# TAB 1: DASHBOARD & PETA SPASIAL (Exact app.py: Map + Bar on top, Radar + Scatter on bot)
# ==============================================================================
def make_wireframe_tab1():
    svg, mx, mw, cy, ch = base_layout(active_tab=0)
    
    # Top Row: Peta Spasial (Left 56%) + Bar Chart Distribusi (Right 44%)
    top_h = ch * 0.51
    map_w = (mw - 10) * 0.56
    bar_w = mw - map_w - 14
    rx = mx + map_w + 10
    
    # 1. Peta Spasial Folium
    svg.append(f'<rect x="{mx+4}" y="{cy}" width="{map_w}" height="{top_h}" class="box"/>')
    svg.append(f'<text x="{mx+4+map_w/2}" y="{cy+20}" class="lbl-title">PETA TEMATIK ZONASI PRIORITAS (DATA 2025/2026)</text>')
    svg.append(f'<text x="{mx+4+map_w/2}" y="{cy+34}" class="lbl-small">(FOLIUM / LEAFLET MAP - 18 KECAMATAN KOTA PALEMBANG)</text>')
    
    # Map area placeholder
    svg.append(f'<rect x="{mx+14}" y="{cy+42}" width="{map_w-20}" height="{top_h-88}" class="box-white"/>')
    svg.append(f'<text x="{mx+4+map_w/2}" y="{cy+42+(top_h-88)/2+5}" class="lbl-header" fill="#666666">[ AREA PETA SPASIAL &amp; MARKER ZONASI KLASTER ]</text>')
    
    # Map Legend
    leg_y = cy + top_h - 40
    svg.append(f'<rect x="{mx+14}" y="{leg_y}" width="{map_w-20}" height="32" class="box-white"/>')
    svg.append(f'<text x="{mx+4+map_w/2}" y="{leg_y+13}" class="lbl-sub">LEGENDA ZONASI PRIORITAS BANSOS</text>')
    svg.append(f'<text x="{mx+4+map_w/2}" y="{leg_y+26}" font-size="8.5px" fill="#000000" text-anchor="middle">[ ■ ] Prioritas Tinggi (Darurat)   |   [ ■ ] Prioritas Sedang (Waspada)   |   [ ■ ] Prioritas Rendah (Mandiri)</text>')

    # 2. Bar Chart Distribusi Indikator
    svg.append(f'<rect x="{rx}" y="{cy}" width="{bar_w}" height="{top_h}" class="box"/>')
    svg.append(f'<text x="{rx+bar_w/2}" y="{cy+20}" class="lbl-title">ANALISIS DISTRIBUSI INDIKATOR</text>')
    svg.append(f'<rect x="{rx+12}" y="{cy+28}" width="{bar_w-24}" height="24" class="box-white"/>')
    svg.append(f'<text x="{rx+bar_w/2}" y="{cy+44}" class="lbl-sub">Pilih Indikator Visualisasi: [ DROPDOWN ▾ ]</text>')
    svg.append(f'<rect x="{rx+12}" y="{cy+58}" width="{bar_w-24}" height="{top_h-70}" class="box-white"/>')
    svg.append(f'<text x="{rx+bar_w/2}" y="{cy+58+(top_h-70)/2+5}" class="lbl-header" fill="#666666">[ PLOTLY BAR CHART DISTRIBUSI ]</text>')

    # Bottom Row: Radar Profile (Left 50%) + Scatter Plot (Right 50%)
    bot_y = cy + top_h + 6
    bot_h = ch - top_h - 6
    bot_w = (mw - 14) / 2
    
    # 3. Radar Profile Per Klaster
    svg.append(f'<rect x="{mx+4}" y="{bot_y}" width="{bot_w}" height="{bot_h}" class="box"/>')
    svg.append(f'<text x="{mx+4+bot_w/2}" y="{bot_y+20}" class="lbl-title">RADAR PROFILE PER KLASTER</text>')
    svg.append(f'<text x="{mx+4+bot_w/2}" y="{bot_y+34}" class="lbl-small">(Perbandingan Rata-rata 7 Indikator Sosial-Ekonomi Antar-Klaster)</text>')
    svg.append(f'<rect x="{mx+14}" y="{bot_y+42}" width="{bot_w-20}" height="{bot_h-52}" class="box-white"/>')
    svg.append(f'<text x="{mx+4+bot_w/2}" y="{bot_y+42+(bot_h-52)/2+5}" class="lbl-header" fill="#666666">[ SPIDER / RADAR CHART SUMMARY ]</text>')

    # 4. Scatter Plot Hubungan Indikator (EXACT APP.PY TAB 1 BOTTOM RIGHT)
    rx2 = mx + 4 + bot_w + 6
    svg.append(f'<rect x="{rx2}" y="{bot_y}" width="{bot_w}" height="{bot_h}" class="box"/>')
    svg.append(f'<text x="{rx2+bot_w/2}" y="{bot_y+20}" class="lbl-title">SCATTER PLOT HUBUNGAN INDIKATOR</text>')
    svg.append(f'<rect x="{rx2+12}" y="{bot_y+26}" width="{bot_w-24}" height="22" class="box-white"/>')
    svg.append(f'<text x="{rx2+bot_w/2}" y="{bot_y+40}" class="lbl-sub">Sumbu X: [ Indikator 1 ▾ ]   |   Sumbu Y: [ Indikator 2 ▾ ]</text>')
    svg.append(f'<rect x="{rx2+12}" y="{bot_y+52}" width="{bot_w-24}" height="{bot_h-62}" class="box-white"/>')
    svg.append(f'<text x="{rx2+bot_w/2}" y="{bot_y+52+(bot_h-62)/2+5}" class="lbl-header" fill="#666666">[ PLOTLY SCATTER PLOT 2D ]</text>')

    svg.append('</svg>')
    return '\n'.join(svg)

# ==============================================================================
# TAB 2: SIMULATOR ALOKASI BANSOS (DSS) (Exact app.py: 2 Inputs, 2 Pies, Table)
# ==============================================================================
def make_wireframe_tab2():
    svg, mx, mw, cy, ch = base_layout(active_tab=1)
    
    # Subheader Banner
    banner_h = 42
    svg.append(f'<rect x="{mx+4}" y="{cy}" width="{mw-8}" height="{banner_h}" class="box"/>')
    svg.append(f'<text x="{mx+mw/2}" y="{cy+18}" class="lbl-title">SIMULATOR SISTEM PENDUKUNG KEPUTUSAN (DSS) ALOKASI BANSOS</text>')
    svg.append(f'<text x="{mx+mw/2}" y="{cy+34}" class="lbl-small">Simulasi pembagian pagu anggaran (Rp) dan kuota penerima (KK) secara proporsional berdasar bobot prioritas klaster.</text>')

    # Row 1: 2 Number Inputs (Pagu & Kuota)
    r1_y = cy + banner_h + 6
    r1_h = 60
    inp_w = (mw - 14) / 2
    
    # Input 1: Pagu Anggaran
    svg.append(f'<rect x="{mx+4}" y="{r1_y}" width="{inp_w}" height="{r1_h}" class="box"/>')
    svg.append(f'<text x="{mx+4+inp_w/2}" y="{r1_y+18}" class="lbl-title">TOTAL PAGU ANGGARAN BANSOS (RP)</text>')
    svg.append(f'<rect x="{mx+16}" y="{r1_y+26}" width="{inp_w-24}" height="26" class="box-white"/>')
    svg.append(f'<text x="{mx+4+inp_w/2}" y="{r1_y+43}" class="lbl-sub">[ FIELD INPUT NOMINAL ANGGARAN (RP 5.000.000.000) ]</text>')

    # Input 2: Kuota Penerima KK
    rx2 = mx + 4 + inp_w + 6
    svg.append(f'<rect x="{rx2}" y="{r1_y}" width="{inp_w}" height="{r1_h}" class="box"/>')
    svg.append(f'<text x="{rx2+inp_w/2}" y="{r1_y+18}" class="lbl-title">TOTAL KUOTA KEPALA KELUARGA (KK)</text>')
    svg.append(f'<rect x="{rx2+12}" y="{r1_y+26}" width="{inp_w-24}" height="26" class="box-white"/>')
    svg.append(f'<text x="{rx2+inp_w/2}" y="{r1_y+43}" class="lbl-sub">[ FIELD INPUT KUOTA KEPALA KELUARGA (10.000 KK) ]</text>')

    # Row 2: 2 Pie Charts (Anggaran & Kuota KK)
    r2_y = r1_y + r1_h + 6
    r2_h = 160
    
    # Pie 1: Anggaran
    svg.append(f'<rect x="{mx+4}" y="{r2_y}" width="{inp_w}" height="{r2_h}" class="box"/>')
    svg.append(f'<text x="{mx+4+inp_w/2}" y="{r2_y+20}" class="lbl-title">DISTRIBUSI ALOKASI ANGGARAN PER KLASTER</text>')
    svg.append(f'<rect x="{mx+16}" y="{r2_y+28}" width="{inp_w-24}" height="{r2_h-38}" class="box-white"/>')
    svg.append(f'<text x="{mx+4+inp_w/2}" y="{r2_y+28+(r2_h-38)/2+5}" class="lbl-header" fill="#777777">[ PLOTLY PIE CHART ALOKASI ANGGARAN ]</text>')

    # Pie 2: Kuota KK
    svg.append(f'<rect x="{rx2}" y="{r2_y}" width="{inp_w}" height="{r2_h}" class="box"/>')
    svg.append(f'<text x="{rx2+inp_w/2}" y="{r2_y+20}" class="lbl-title">DISTRIBUSI KUOTA KK PENERIMA PER KLASTER</text>')
    svg.append(f'<rect x="{rx2+12}" y="{r2_y+28}" width="{inp_w-24}" height="{r2_h-38}" class="box-white"/>')
    svg.append(f'<text x="{rx2+inp_w/2}" y="{r2_y+28+(r2_h-38)/2+5}" class="lbl-header" fill="#777777">[ PLOTLY PIE CHART KUOTA PENERIMA KK ]</text>')

    # Row 3: Tabel Hasil Rekomendasi Alokasi Per Kecamatan
    tbl_y = r2_y + r2_h + 6
    tbl_h = ch - (tbl_y - cy) - 2
    svg.append(f'<rect x="{mx+4}" y="{tbl_y}" width="{mw-8}" height="{tbl_h}" class="box"/>')
    svg.append(f'<text x="{mx+mw/2}" y="{tbl_y+22}" class="lbl-title">TABEL HASIL REKOMENDASI ALOKASI PER KECAMATAN</text>')
    
    t_box_y = tbl_y + 30
    svg.append(f'<rect x="{mx+12}" y="{t_box_y}" width="{mw-24}" height="{tbl_h-40}" class="box-white"/>')
    svg.append(f'<rect x="{mx+12}" y="{t_box_y}" width="{mw-24}" height="26" class="box"/>')
    cols = ["KECAMATAN", "KATEGORI_PRIORITAS", "SKOR_KERENTANAN", "ALOKASI_ANGGARAN_RP", "ALOKASI_KUOTA_KK", "NILAI_BANTUAN_PER_KK"]
    cw = (mw - 24) / len(cols)
    for idx, cname in enumerate(cols):
        cx = mx + 12 + idx * cw
        svg.append(f'<text x="{cx+cw/2}" y="{t_box_y+17}" class="lbl-sub">{cname}</text>')
        if idx > 0:
            svg.append(f'<line x1="{cx}" y1="{t_box_y}" x2="{cx}" y2="{t_box_y+tbl_h-40}" class="line"/>')
            
    svg.append(f'<text x="{mx+mw/2}" y="{t_box_y+26+(tbl_h-66)/2+6}" class="lbl-header" fill="#777777">[ BARIS DATA HASIL SIMULASI ALOKASI BANSOS 18 KECAMATAN ]</text>')

    svg.append('</svg>')
    return '\n'.join(svg)

# ==============================================================================
# TAB 3: ANALISIS PERBANDINGAN TREN (Exact app.py: 2 Bar Charts + df_trend Table)
# ==============================================================================
def make_wireframe_tab3():
    svg, mx, mw, cy, ch = base_layout(active_tab=2)
    
    # Subheader Banner
    banner_h = 42
    svg.append(f'<rect x="{mx+4}" y="{cy}" width="{mw-8}" height="{banner_h}" class="box"/>')
    svg.append(f'<text x="{mx+mw/2}" y="{cy+18}" class="lbl-title">ANALISIS PERGESERAN TREN KEMISKINAN &amp; IPM (2023 vs 2025/2026)</text>')
    svg.append(f'<text x="{mx+mw/2}" y="{cy+34}" class="lbl-small">Menganalisis perkembangan pergeseran kesejahteraan antar-kecamatan dari data historis ke pemutakhiran terbaru.</text>')

    # Row 1: 2 Horizontal Bar Charts
    r1_y = cy + banner_h + 6
    r1_h = 240
    chart_w = (mw - 14) / 2
    
    # Chart 1: Perubahan Jumlah Penduduk Miskin
    svg.append(f'<rect x="{mx+4}" y="{r1_y}" width="{chart_w}" height="{r1_h}" class="box"/>')
    svg.append(f'<text x="{mx+4+chart_w/2}" y="{r1_y+22}" class="lbl-title">PERUBAHAN JUMLAH PENDUDUK MISKIN (2023 ➔ 2025)</text>')
    svg.append(f'<rect x="{mx+14}" y="{r1_y+32}" width="{chart_w-20}" height="{r1_h-44}" class="box-white"/>')
    svg.append(f'<text x="{mx+4+chart_w/2}" y="{r1_y+32+(r1_h-44)/2+5}" class="lbl-header" fill="#777777">[ PLOTLY HORIZONTAL BAR CHART Δ MISKIN ]</text>')

    # Chart 2: Kenaikan Skor IPM
    rx2 = mx + 4 + chart_w + 6
    svg.append(f'<rect x="{rx2}" y="{r1_y}" width="{chart_w}" height="{r1_h}" class="box"/>')
    svg.append(f'<text x="{rx2+chart_w/2}" y="{r1_y+22}" class="lbl-title">KENAIKAN SKOR IPM PER KECAMATAN (2023 ➔ 2025)</text>')
    svg.append(f'<rect x="{rx2+12}" y="{r1_y+32}" width="{chart_w-20}" height="{r1_h-44}" class="box-white"/>')
    svg.append(f'<text x="{rx2+chart_w/2}" y="{r1_y+32+(r1_h-44)/2+5}" class="lbl-header" fill="#777777">[ PLOTLY HORIZONTAL BAR CHART Δ IPM ]</text>')

    # Row 2: Tabel Matriks Perbandingan Tren Multi-Tahun (df_trend)
    tbl_y = r1_y + r1_h + 6
    tbl_h = ch - (tbl_y - cy) - 2
    svg.append(f'<rect x="{mx+4}" y="{tbl_y}" width="{mw-8}" height="{tbl_h}" class="box"/>')
    svg.append(f'<text x="{mx+mw/2}" y="{tbl_y+22}" class="lbl-title">TABEL DATA KOMPARASI PERKEMBANGAN TREN MULTI-TAHUN</text>')
    
    t_box_y = tbl_y + 30
    svg.append(f'<rect x="{mx+12}" y="{t_box_y}" width="{mw-24}" height="{tbl_h-40}" class="box-white"/>')
    svg.append(f'<rect x="{mx+12}" y="{t_box_y}" width="{mw-24}" height="26" class="box"/>')
    cols = ["KECAMATAN", "MISKIN 2023", "MISKIN 2025", "Δ MISKIN", "IPM 2023", "IPM 2025", "Δ IPM"]
    cw = (mw - 24) / len(cols)
    for idx, cname in enumerate(cols):
        cx = mx + 12 + idx * cw
        svg.append(f'<text x="{cx+cw/2}" y="{t_box_y+17}" class="lbl-sub">{cname}</text>')
        if idx > 0:
            svg.append(f'<line x1="{cx}" y1="{t_box_y}" x2="{cx}" y2="{t_box_y+tbl_h-40}" class="line"/>')
            
    svg.append(f'<text x="{mx+mw/2}" y="{t_box_y+26+(tbl_h-66)/2+6}" class="lbl-header" fill="#777777">[ BARIS DATA KOMPARASI HISTORIS 2023 vs PEMUTAKHIRAN 2025 ]</text>')

    svg.append('</svg>')
    return '\n'.join(svg)

# ==============================================================================
# TAB 4: PROFILER PER-KECAMATAN (Exact app.py: Dropdown, 4 Metrics, comp_df Table, Info Box)
# ==============================================================================
def make_wireframe_tab4():
    svg, mx, mw, cy, ch = base_layout(active_tab=3)
    
    # Subheader Banner
    banner_h = 42
    svg.append(f'<rect x="{mx+4}" y="{cy}" width="{mw-8}" height="{banner_h}" class="box"/>')
    svg.append(f'<text x="{mx+mw/2}" y="{cy+18}" class="lbl-title">PROFILER &amp; INSPECTOR DETAIL PER-KECAMATAN</text>')
    svg.append(f'<text x="{mx+mw/2}" y="{cy+34}" class="lbl-small">Pilih salah satu kecamatan untuk melihat analisa mendalam indikator dan rekomendasi kebijakan spesifik.</text>')

    # Row 1: Selectbox Dropdown Kecamatan
    r1_y = cy + banner_h + 6
    r1_h = 46
    svg.append(f'<rect x="{mx+4}" y="{r1_y}" width="{mw-8}" height="{r1_h}" class="box"/>')
    svg.append(f'<text x="{mx+18}" y="{r1_y+28}" class="lbl-left">PILIH KECAMATAN UNTUK DI-INSPEKSI:</text>')
    svg.append(f'<rect x="{mx+300}" y="{r1_y+10}" width="{mw-320}" height="26" class="box-white"/>')
    svg.append(f'<text x="{mx+315}" y="{r1_y+27}" class="lbl-left">[ DROPDOWN DAFTAR 18 KECAMATAN ▾ ]</text>')

    # Row 2: 4 Key District Metric Cards
    r2_y = r1_y + r1_h + 6
    r2_h = 58
    cw4 = (mw - 22) / 4
    cards = [
        ("KATEGORI PRIORITAS", "[ STATUS PRIORITAS KLASTER ]"),
        ("SKOR KERENTANAN (CVI)", "[ NILAI SKOR CVI ]"),
        ("JUMLAH PENDUDUK MISKIN", "[ TOTAL JIWA MISKIN ]"),
        ("SKOR IPM KECAMATAN", "[ NILAI SKOR IPM ]")
    ]
    for i, (ctitle, cval) in enumerate(cards):
        cx = mx + 4 + i * (cw4 + 4)
        svg.append(f'<rect x="{cx}" y="{r2_y}" width="{cw4}" height="{r2_h}" class="box-white"/>')
        svg.append(f'<text x="{cx+cw4/2}" y="{r2_y+20}" font-size="9px" font-weight="bold" fill="#000000" text-anchor="middle">{ctitle}</text>')
        svg.append(f'<text x="{cx+cw4/2}" y="{r2_y+42}" font-size="11px" font-weight="bold" fill="#000000" text-anchor="middle">{cval}</text>')

    # Row 3: Tabel Komparasi Indikator Kecamatan vs Rata-Rata Kota (7 Indikator Resmi Skripsi)
    tbl_y = r2_y + r2_h + 6
    tbl_h = 245
    svg.append(f'<rect x="{mx+4}" y="{tbl_y}" width="{mw-8}" height="{tbl_h}" class="box"/>')
    svg.append(f'<text x="{mx+mw/2}" y="{tbl_y+22}" class="lbl-title">PROFIL INDIKATOR KECAMATAN TERPILIH vs RATA-RATA KOTA PALEMBANG</text>')
    
    t_box_y = tbl_y + 30
    svg.append(f'<rect x="{mx+12}" y="{t_box_y}" width="{mw-24}" height="{tbl_h-40}" class="box-white"/>')
    svg.append(f'<rect x="{mx+12}" y="{t_box_y}" width="{mw-24}" height="26" class="box"/>')
    cols = ["INDIKATOR SOSIAL-EKONOMI (BPS)", "NILAI KECAMATAN TERPILIH", "RATA-RATA KOTA PALEMBANG"]
    cw = (mw - 24) / len(cols)
    for idx, cname in enumerate(cols):
        cx = mx + 12 + idx * cw
        svg.append(f'<text x="{cx+cw/2}" y="{t_box_y+17}" class="lbl-sub">{cname}</text>')
        if idx > 0:
            svg.append(f'<line x1="{cx}" y1="{t_box_y}" x2="{cx}" y2="{t_box_y+tbl_h-40}" class="line"/>')
            
    svg.append(f'<text x="{mx+mw/2}" y="{t_box_y+26+(tbl_h-66)/2+6}" class="lbl-header" fill="#777777">[ BARIS DATA 7 INDIKATOR SOSIAL-EKONOMI BPS ]</text>')

    # Row 4: Info Alert Box Rekomendasi Kebijakan Spesifik
    rec_y = tbl_y + tbl_h + 6
    rec_h = ch - (rec_y - cy) - 2
    svg.append(f'<rect x="{mx+4}" y="{rec_y}" width="{mw-8}" height="{rec_h}" class="box"/>')
    svg.append(f'<text x="{mx+18}" y="{rec_y+22}" class="lbl-left">💡 REKOMENDASI KEBIJAKAN SPESIFIK UNTUK KECAMATAN TERPILIH:</text>')
    svg.append(f'<rect x="{mx+16}" y="{rec_y+30}" width="{mw-32}" height="{rec_h-40}" class="box-white"/>')
    svg.append(f'<text x="{mx+30}" y="{rec_y+52}" class="lbl-left">- STATUS PRIORITAS : [ PRIORITAS TINGGI / SEDANG / RENDAH ]</text>')
    svg.append(f'<text x="{mx+30}" y="{rec_y+72}" class="lbl-left">- INTERVENSI UTAMA : [ FOKUS PENANGANAN PENGANGGURAN &amp; PENINGKATAN BANSOS PKH/BPNT ]</text>')

    svg.append('</svg>')
    return '\n'.join(svg)

# ==============================================================================
# TAB 5: ITERASI & MATRIKS EUCLIDEAN (Exact app.py: df_show, 2 Centroid tables, Expander)
# ==============================================================================
def make_wireframe_tab5():
    svg, mx, mw, cy, ch = base_layout(active_tab=4)
    
    # Subheader Banner
    banner_h = 42
    svg.append(f'<rect x="{mx+4}" y="{cy}" width="{mw-8}" height="{banner_h}" class="box"/>')
    svg.append(f'<text x="{mx+mw/2}" y="{cy+18}" class="lbl-title">TABEL HASIL CLUSTERING &amp; JARAK EUCLIDEAN (DATA 2025/2026)</text>')
    svg.append(f'<text x="{mx+mw/2}" y="{cy+34}" class="lbl-small">Menghitung jarak Euclidean d(x, c) dari setiap kecamatan ke centroid klaster sesuai tahapan K-Means.</text>')

    # Row 1: Tabel Matriks Jarak Euclidean Lengkap (df_show)
    tbl_y = cy + banner_h + 6
    tbl_h = 280
    svg.append(f'<rect x="{mx+4}" y="{tbl_y}" width="{mw-8}" height="{tbl_h}" class="box"/>')
    svg.append(f'<text x="{mx+mw/2}" y="{tbl_y+22}" class="lbl-title">MATRIKS JARAK EUCLIDEAN d(x, c) TIAP KECAMATAN KE CENTROID</text>')
    
    t_box_y = tbl_y + 30
    svg.append(f'<rect x="{mx+12}" y="{t_box_y}" width="{mw-24}" height="{tbl_h-40}" class="box-white"/>')
    svg.append(f'<rect x="{mx+12}" y="{t_box_y}" width="{mw-24}" height="26" class="box"/>')
    cols = ["KECAMATAN", "KATEGORI_PRIORITAS", "SKOR_KERENTANAN", "JARAK_KE_CENTROID_0", "JARAK_KE_CENTROID_1", "JARAK_KE_CENTROID_2", "JARAK_TERDEKAT_d_min"]
    cw = (mw - 24) / len(cols)
    for idx, cname in enumerate(cols):
        cx = mx + 12 + idx * cw
        svg.append(f'<text x="{cx+cw/2}" y="{t_box_y+17}" class="lbl-sub">{cname}</text>')
        if idx > 0:
            svg.append(f'<line x1="{cx}" y1="{t_box_y}" x2="{cx}" y2="{t_box_y+tbl_h-40}" class="line"/>')
            
    svg.append(f'<text x="{mx+mw/2}" y="{t_box_y+26+(tbl_h-66)/2+6}" class="lbl-header" fill="#777777">[ BARIS DATA MATRIKS JARAK EUCLIDEAN 18 KECAMATAN ]</text>')

    # Row 2: 2 Tables of Centroids (cluster_summary & centroids_scaled)
    r2_y = tbl_y + tbl_h + 6
    r2_h = 160
    bot_w = (mw - 14) / 2
    
    # Centroid 1: Asli
    svg.append(f'<rect x="{mx+4}" y="{r2_y}" width="{bot_w}" height="{r2_h}" class="box"/>')
    svg.append(f'<text x="{mx+4+bot_w/2}" y="{r2_y+20}" class="lbl-title">CENTROID AKHIR (NILAI RATA-RATA ASLI)</text>')
    svg.append(f'<rect x="{mx+14}" y="{r2_y+28}" width="{bot_w-20}" height="{r2_h-38}" class="box-white"/>')
    svg.append(f'<text x="{mx+4+bot_w/2}" y="{r2_y+28+(r2_h-38)/2+5}" font-size="11.5px" font-weight="bold" fill="#777777" text-anchor="middle">[ TABEL CENTROID RATA-RATA VARIABEL ASLI ]</text>')

    # Centroid 2: Normalized Scaled
    rx2 = mx + 4 + bot_w + 6
    svg.append(f'<rect x="{rx2}" y="{r2_y}" width="{bot_w}" height="{r2_h}" class="box"/>')
    svg.append(f'<text x="{rx2+bot_w/2}" y="{r2_y+20}" class="lbl-title">CENTROID TER-NORMALISASI (SCALE 0 - 1)</text>')
    svg.append(f'<rect x="{rx2+12}" y="{r2_y+28}" width="{bot_w-20}" height="{r2_h-38}" class="box-white"/>')
    svg.append(f'<text x="{rx2+bot_w/2}" y="{r2_y+28+(r2_h-38)/2+5}" font-size="11.5px" font-weight="bold" fill="#777777" text-anchor="middle">[ TABEL CENTROID MIN-MAX NORMALISASI ]</text>')

    # Row 3: Expander Detail Normalisasi Min-Max
    exp_y = r2_y + r2_h + 6
    exp_h = ch - (exp_y - cy) - 2
    svg.append(f'<rect x="{mx+4}" y="{exp_y}" width="{mw-8}" height="{exp_h}" class="box"/>')
    svg.append(f'<text x="{mx+18}" y="{exp_y+22}" class="lbl-left">🔍 EXPANDER: DETAIL DATA TER-NORMALISASI (MIN-MAX SCALING [0, 1])</text>')
    svg.append(f'<text x="{mx+18}" y="{exp_y+42}" font-size="10px" font-weight="bold" fill="#000000">Formula Min-Max: X_scaled = (X - X_min) / (X_max - X_min)   |   [ TABEL DATA NORMALISASI df_scaled ]</text>')

    svg.append('</svg>')
    return '\n'.join(svg)

# ==============================================================================
# TAB 6: VALIDASI ILMIAH & EXPORT DATA (Exact app.py: Elbow, Sil, 3 Metrics, elbow_df Table, 2 Exports)
# ==============================================================================
def make_wireframe_tab6():
    svg, mx, mw, cy, ch = base_layout(active_tab=5)
    
    # Subheader Banner
    banner_h = 42
    svg.append(f'<rect x="{mx+4}" y="{cy}" width="{mw-8}" height="{banner_h}" class="box"/>')
    svg.append(f'<text x="{mx+mw/2}" y="{cy+18}" class="lbl-title">PEMBUKTIAN ILMIAH K OPTIMAL &amp; VALIDASI MODEL</text>')
    svg.append(f'<text x="{mx+mw/2}" y="{cy+34}" class="lbl-small">Metrik evaluasi untuk membuktikan secara akademis di hadapan dosen penguji bahwa klasterisasi presisi dan optimal.</text>')

    # Row 1: 2 Validation Charts (Elbow & Silhouette Curve)
    r1_y = cy + banner_h + 6
    r1_h = 165
    chart_w = (mw - 14) / 2
    
    # Chart 1: Elbow Method
    svg.append(f'<rect x="{mx+4}" y="{r1_y}" width="{chart_w}" height="{r1_h}" class="box"/>')
    svg.append(f'<text x="{mx+4+chart_w/2}" y="{r1_y+20}" class="lbl-title">GRAFIK METODE ELBOW (WCSS vs K = 1..8)</text>')
    svg.append(f'<rect x="{mx+14}" y="{r1_y+28}" width="{chart_w-20}" height="{r1_h-56}" class="box-white"/>')
    svg.append(f'<text x="{mx+4+chart_w/2}" y="{r1_y+28+(r1_h-56)/2+5}" class="lbl-header" fill="#777777">[ PLOTLY ELBOW CHART - TITIK SIKU K=3 ]</text>')
    svg.append(f'<rect x="{mx+14}" y="{r1_y+r1_h-24}" width="{chart_w-20}" height="18" class="box-white"/>')
    svg.append(f'<text x="{mx+4+chart_w/2}" y="{r1_y+r1_h-12}" font-size="8.5px" font-weight="bold" fill="#000000" text-anchor="middle">💡 Metode Elbow: Titik Siku Terbaik Pada K=3 (WCSS Optimal)</text>')

    # Chart 2: Silhouette Score Curve
    rx2 = mx + 4 + chart_w + 6
    svg.append(f'<rect x="{rx2}" y="{r1_y}" width="{chart_w}" height="{r1_h}" class="box"/>')
    svg.append(f'<text x="{rx2+chart_w/2}" y="{r1_y+20}" class="lbl-title">GRAFIK SILHOUETTE COEFFICIENT (K = 1..8)</text>')
    svg.append(f'<rect x="{rx2+12}" y="{r1_y+28}" width="{chart_w-20}" height="{r1_h-56}" class="box-white"/>')
    svg.append(f'<text x="{rx2+chart_w/2}" y="{r1_y+28+(r1_h-56)/2+5}" class="lbl-header" fill="#777777">[ PLOTLY SILHOUETTE SCORE CHART ]</text>')
    svg.append(f'<rect x="{rx2+12}" y="{r1_y+r1_h-24}" width="{chart_w-20}" height="18" class="box-white"/>')
    svg.append(f'<text x="{rx2+chart_w/2}" y="{r1_y+r1_h-12}" font-size="8.5px" font-weight="bold" fill="#000000" text-anchor="middle">💡 Silhouette Score (K=3): 0.5420 (Struktur Pemisahan Kuat)</text>')

    # Row 2: 3 Validation Metric Cards
    r2_y = r1_y + r1_h + 6
    r2_h = 52
    cw3 = (mw - 18) / 3
    svg.append(f'<rect x="{mx+4}" y="{r2_y}" width="{cw3}" height="{r2_h}" class="box-white"/>')
    svg.append(f'<text x="{mx+4+cw3/2}" y="{r2_y+18}" class="lbl-sub">SILHOUETTE SCORE (PEMISAHAN)</text>')
    svg.append(f'<text x="{mx+4+cw3/2}" y="{r2_y+38}" font-size="11.5px" font-weight="bold" fill="#000000" text-anchor="middle">[ 0.5420 - KUAT ]</text>')

    svg.append(f'<rect x="{mx+4+cw3+5}" y="{r2_y}" width="{cw3}" height="{r2_h}" class="box-white"/>')
    svg.append(f'<text x="{mx+4+cw3+5+cw3/2}" y="{r2_y+18}" class="lbl-sub">DAVIES-BOULDIN INDEX (KERAPATAN)</text>')
    svg.append(f'<text x="{mx+4+cw3+5+cw3/2}" y="{r2_y+38}" font-size="11.5px" font-weight="bold" fill="#000000" text-anchor="middle">[ 0.6120 - OPTIMAL &lt; 1.0 ]</text>')

    svg.append(f'<rect x="{mx+4+2*cw3+10}" y="{r2_y}" width="{cw3}" height="{r2_h}" class="box-white"/>')
    svg.append(f'<text x="{mx+4+2*cw3+10+cw3/2}" y="{r2_y+18}" class="lbl-sub">CALINSKI-HARABASZ INDEX (SEBARAN)</text>')
    svg.append(f'<text x="{mx+4+2*cw3+10+cw3/2}" y="{r2_y+38}" font-size="11.5px" font-weight="bold" fill="#000000" text-anchor="middle">[ 48.5 - TINGGI ]</text>')

    # Row 3: Tabel Perbandingan Evaluasi Berbagai K (elbow_df)
    r3_y = r2_y + r2_h + 6
    r3_h = 135
    svg.append(f'<rect x="{mx+4}" y="{r3_y}" width="{mw-8}" height="{r3_h}" class="box"/>')
    svg.append(f'<text x="{mx+mw/2}" y="{r3_y+18}" class="lbl-title">TABEL PERBANDINGAN EVALUASI BERBAGAI JUMLAH K (1 - 8)</text>')
    
    t_box_y = r3_y + 26
    svg.append(f'<rect x="{mx+12}" y="{t_box_y}" width="{mw-24}" height="{r3_h-34}" class="box-white"/>')
    svg.append(f'<rect x="{mx+12}" y="{t_box_y}" width="{mw-24}" height="22" class="box"/>')
    cols = ["K (KLASTER)", "WCSS_INERTIA", "SILHOUETTE_SCORE", "DAVIES_BOULDIN_SCORE", "CALINSKI_HARABASZ_SCORE"]
    cw = (mw - 24) / len(cols)
    for idx, cname in enumerate(cols):
        cx = mx + 12 + idx * cw
        svg.append(f'<text x="{cx+cw/2}" y="{t_box_y+15}" class="lbl-sub">{cname}</text>')
        if idx > 0:
            svg.append(f'<line x1="{cx}" y1="{t_box_y}" x2="{cx}" y2="{t_box_y+r3_h-34}" class="line"/>')
            
    svg.append(f'<text x="{mx+mw/2}" y="{t_box_y+22+(r3_h-56)/2+5}" font-size="11px" font-weight="bold" fill="#777777" text-anchor="middle">[ BARIS DATA EVALUASI METRIK K=1 SAMPAI K=8 ]</text>')

    # Row 4: Export Action Buttons (Excel .xlsx)
    r4_y = r3_y + r3_h + 6
    r4_h = ch - (r4_y - cy) - 2
    svg.append(f'<rect x="{mx+4}" y="{r4_y}" width="{mw-8}" height="{r4_h}" class="box"/>')
    svg.append(f'<text x="{mx+mw/2}" y="{r4_y+20}" class="lbl-title">EXPORT LAPORAN LENGKAP KE EXCEL (.XLSX)</text>')
    
    exp_btn_w = (mw - 36) / 2
    # Button 1
    svg.append(f'<rect x="{mx+16}" y="{r4_y+28}" width="{exp_btn_w}" height="32" class="box-white"/>')
    svg.append(f'<text x="{mx+16+exp_btn_w/2}" y="{r4_y+48}" font-size="10px" font-weight="bold" fill="#000000" text-anchor="middle">[ 📊 DOWNLOAD HASIL CLUSTERING 2025/2026 (.XLSX) ]</text>')
    # Button 2
    svg.append(f'<rect x="{mx+20+exp_btn_w}" y="{r4_y+28}" width="{exp_btn_w}" height="32" class="box-white"/>')
    svg.append(f'<text x="{mx+20+exp_btn_w+exp_btn_w/2}" y="{r4_y+48}" font-size="10px" font-weight="bold" fill="#000000" text-anchor="middle">[ 🏛️ DOWNLOAD MASTER DATA KESRA 2025/2026 (.XLSX) ]</text>')

    svg.append('</svg>')
    return '\n'.join(svg)

# ==============================================================================
# MASTER GENERATOR & PNG EXPORTER
# ==============================================================================
TABS_CONFIG = [
    ("wireframe_tab1_dashboard_peta", make_wireframe_tab1, "Tab 1: Dashboard & Peta Spasial"),
    ("wireframe_tab2_simulator_dss", make_wireframe_tab2, "Tab 2: Simulator Alokasi Bansos (DSS)"),
    ("wireframe_tab3_analisis_tren", make_wireframe_tab3, "Tab 3: Analisis Perbandingan Tren"),
    ("wireframe_tab4_profiler_kecamatan", make_wireframe_tab4, "Tab 4: Profiler Per-Kecamatan"),
    ("wireframe_tab5_matriks_euclidean", make_wireframe_tab5, "Tab 5: Iterasi & Matriks Jarak Euclidean"),
    ("wireframe_tab6_validasi_export", make_wireframe_tab6, "Tab 6: Validasi Ilmiah & Export Data")
]

def render_svg_to_png(svg_content, out_png_path):
    temp_html = "temp_render_wrapper.html"
    html_content = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ background: #ffffff; width: {WIDTH}px; height: {HEIGHT}px; overflow: hidden; }}
  svg {{ width: {WIDTH}px; height: {HEIGHT}px; display: block; }}
</style>
</head>
<body>
{svg_content}
</body>
</html>"""
    with open(temp_html, 'w', encoding='utf-8') as f:
        f.write(html_content)
        
    html_url = "file:///" + os.path.abspath(temp_html).replace("\\", "/")
    cmd = [
        CHROME_PATH,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--hide-scrollbars",
        f"--window-size={WIDTH},{HEIGHT}",
        f"--screenshot={out_png_path}",
        html_url
    ]
    subprocess.run(cmd, capture_output=True, text=True, timeout=20)
    if os.path.exists(temp_html):
        try:
            os.remove(temp_html)
        except:
            pass

def generate_all_wireframes(output_dir="d:/websyahril/wireframe"):
    os.makedirs(output_dir, exist_ok=True)
    root_dir = "d:/websyahril"
    
    print(f"Generating 100% accurate Web DSS low-fidelity wireframe blueprints...")
    
    for filename_base, builder_fn, desc in TABS_CONFIG:
        svg_content = builder_fn()
        
        # 1. Save SVG in wireframe/ and root
        wf_svg_path = os.path.join(output_dir, f"{filename_base}.svg")
        root_svg_path = os.path.join(root_dir, f"{filename_base}.svg")
        
        with open(wf_svg_path, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        with open(root_svg_path, 'w', encoding='utf-8') as f:
            f.write(svg_content)
            
        # 2. Render PNG in wireframe/
        wf_png_path1 = os.path.join(output_dir, f"{filename_base}.png")
        wf_png_path2 = os.path.join(output_dir, f"{filename_base} 1.png")
        
        render_svg_to_png(svg_content, wf_png_path1)
        shutil.copy2(wf_png_path1, wf_png_path2)
        
        print(f" [OK] {desc} -> {filename_base}.svg & {filename_base}.png")

if __name__ == "__main__":
    generate_all_wireframes()
