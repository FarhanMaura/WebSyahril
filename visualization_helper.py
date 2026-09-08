import plotly.express as px
import plotly.graph_objects as gg
import plotly.io as pio
import pandas as pd
import numpy as np
import folium
from folium import plugins

# Force reliable JSON serializer for Plotly (prevents Windows file lock/orjson circular import issues)
pio.json.config.default_engine = 'json'

# Coordinates for Palembang 18 Kecamatan
KECAMATAN_COORDS = {
    'Ilir Timur I': (-2.980, 104.755),
    'Ilir Timur II': (-2.970, 104.775),
    'Ilir Timur III': (-2.965, 104.765),
    'Ilir Barat I': (-2.985, 104.730),
    'Ilir Barat II': (-2.995, 104.745),
    'Seberang Ulu I': (-3.010, 104.760),
    'Seberang Ulu II': (-3.020, 104.780),
    'Bukit Kecil': (-2.988, 104.750),
    'Gandus': (-3.000, 104.700),
    'Kertapati': (-3.035, 104.740),
    'Plaju': (-3.015, 104.810),
    'Sako': (-2.935, 104.790),
    'Sematang Borang': (-2.920, 104.820),
    'Sukarami': (-2.925, 104.740),
    'Alang-Alang Lebar': (-2.910, 104.710),
    'Kalidoni': (-2.955, 104.810),
    'Kemuning': (-2.950, 104.750),
    'Jakabaring': (-3.030, 104.770)
}

CLUSTER_COLORS = {
    0: '#EF4444', # Red
    1: '#F59E0B', # Yellow / Orange
    2: '#10B981', # Green
    3: '#3B82F6', # Blue
    4: '#8B5CF6'  # Purple
}

CLUSTER_NAMES = {
    0: 'Prioritas Tinggi (Darurat)',
    1: 'Prioritas Sedang (Waspada)',
    2: 'Prioritas Rendah (Mandiri)'
}

def plot_elbow_chart(elbow_df: pd.DataFrame, selected_k: int = 3):
    """Generates the Elbow Method line plot."""
    fig = gg.Figure()
    
    fig.add_trace(gg.Scatter(
        x=elbow_df['K'],
        y=elbow_df['WCSS'],
        mode='lines+markers',
        marker=dict(size=10, color='#3B82F6'),
        line=dict(color='#3B82F6', width=3),
        name='WCSS'
    ))
    
    # Highlight selected K
    sel_wcss = elbow_df[elbow_df['K'] == selected_k]['WCSS'].values
    if len(sel_wcss) > 0:
        fig.add_trace(gg.Scatter(
            x=[selected_k],
            y=sel_wcss,
            mode='markers',
            marker=dict(size=16, color='#EF4444', symbol='diamond'),
            name=f'Titik Optimal K={selected_k}'
        ))
        
    fig.update_layout(
        title=dict(text=f'<b>Metode Elbow (Uji K Optimal)</b> - Titik Siku di K={selected_k}', font=dict(size=16)),
        xaxis=dict(title='Jumlah Cluster (K)', dtick=1),
        yaxis=dict(title='Within-Cluster Sum of Squares (WCSS)'),
        hovermode='x unified',
        template='plotly_white',
        margin=dict(l=40, r=40, t=60, b=40)
    )
    return fig

def plot_silhouette_chart(elbow_df: pd.DataFrame, selected_k: int = 3):
    """Generates Silhouette Score across K range."""
    fig = gg.Figure()
    
    fig.add_trace(gg.Scatter(
        x=elbow_df['K'][1:],
        y=elbow_df['Silhouette_Score'][1:],
        mode='lines+markers',
        marker=dict(size=10, color='#10B981'),
        line=dict(color='#10B981', width=3),
        name='Silhouette Score'
    ))
    
    sel_sil = elbow_df[elbow_df['K'] == selected_k]['Silhouette_Score'].values
    if len(sel_sil) > 0:
        fig.add_trace(gg.Scatter(
            x=[selected_k],
            y=sel_sil,
            mode='markers',
            marker=dict(size=16, color='#EF4444', symbol='star'),
            name=f'K={selected_k} (Score: {sel_sil[0]:.3f})'
        ))
        
    fig.update_layout(
        title=dict(text='<b>Evaluasi Silhouette Score Per K</b>', font=dict(size=16)),
        xaxis=dict(title='Jumlah Cluster (K)', dtick=1),
        yaxis=dict(title='Nilai Silhouette Score (0 hingga 1)'),
        template='plotly_white',
        margin=dict(l=40, r=40, t=60, b=40)
    )
    return fig

def plot_cluster_bar(df_result: pd.DataFrame, feature: str = 'Jumlah_KK_Penerima_Bansos'):
    """Generates bar chart comparing kecamatan values colored by cluster."""
    df_sorted = df_result.sort_values(by=feature, ascending=True)
    
    colors = [CLUSTER_COLORS.get(c, '#9CA3AF') for c in df_sorted['Cluster']]
    
    def format_bar_val(x):
        if not isinstance(x, (int, float)) or pd.isna(x):
            return str(x)
        if feature == 'Jumlah_KK_Penerima_Bansos':
            return f"<b>{int(x):,} KK</b>"
        elif feature == 'Jumlah_Penduduk_Miskin':
            return f"<b>{int(x):,} Jiwa</b>"
        elif feature == 'Pendapatan_Rata_Rata':
            return f"<b>Rp {int(x):,}</b>"
        elif feature == 'Tingkat_Pengangguran':
            return f"<b>{x:.1f}%</b>"
        elif x > 100:
            return f"<b>{x:,.0f}</b>"
        else:
            return f"<b>{x:.1f}</b>"

    val_max = df_sorted[feature].max() if not df_sorted.empty else 100

    fig = gg.Figure()
    fig.add_trace(gg.Bar(
        y=df_sorted['Kecamatan'],
        x=df_sorted[feature],
        orientation='h',
        marker=dict(color=colors),
        text=df_sorted[feature].apply(format_bar_val),
        textposition='outside',
        cliponaxis=False,
        textfont=dict(color='#0F172A', size=11.5, family='Plus Jakarta Sans, Arial')
    ))
    
    clean_title = feature.replace('_', ' ')
    fig.update_layout(
        title=dict(text=f'<b>Perbandingan {clean_title} Per Kecamatan</b>', font=dict(size=15)),
        xaxis=dict(title=clean_title, range=[0, val_max * 1.25]),
        yaxis=dict(title='', tickfont=dict(size=12, color='#0F172A', family='Plus Jakarta Sans, Arial')),
        template='plotly_white',
        height=600,
        margin=dict(l=20, r=40, t=60, b=40)
    )
    return fig

def plot_scatter_2d(df_result: pd.DataFrame, x_col: str, y_col: str):
    """2D Scatter plot for cluster distribution."""
    fig = px.scatter(
        df_result,
        x=x_col,
        y=y_col,
        color='Kategori_Prioritas',
        hover_name='Kecamatan',
        size='Jumlah_Penduduk_Miskin',
        color_discrete_map={
            'Prioritas Tinggi (Darurat)': '#EF4444',
            'Prioritas Sedang (Waspada)': '#F59E0B',
            'Prioritas Rendah (Mandiri)': '#10B981'
        },
        title=f'<b>Distribusi Klaster: {x_col.replace("_"," ")} vs {y_col.replace("_"," ")}</b>'
    )
    fig.update_traces(marker=dict(line=dict(width=1, color='DarkSlateGrey')))
    fig.update_layout(template='plotly_white', height=500)
    return fig

def plot_radar_summary(cluster_summary: pd.DataFrame, feature_cols: list):
    """Radar chart comparing cluster profile centroids."""
    summary_norm = cluster_summary[feature_cols].copy()
    for col in feature_cols:
        c_min = summary_norm[col].min()
        c_max = summary_norm[col].max()
        if c_max > c_min:
            summary_norm[col] = (summary_norm[col] - c_min) / (c_max - c_min)
        else:
            summary_norm[col] = 0.5

    fig = gg.Figure()
    categories = [c.replace('_', ' ') for c in feature_cols]
    
    for cluster_id in cluster_summary.index:
        r_vals = summary_norm.loc[cluster_id, feature_cols].tolist()
        r_vals.append(r_vals[0])
        cats = categories + [categories[0]]
        
        c_name = CLUSTER_NAMES.get(cluster_id, f'Cluster {cluster_id}')
        color = CLUSTER_COLORS.get(cluster_id, '#9CA3AF')
        
        fig.add_trace(gg.Scatterpolar(
            r=r_vals,
            theta=cats,
            fill='toself',
            name=c_name,
            line=dict(color=color, width=2)
        ))
        
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        title=dict(text='<b>Profil Karakteristik Indikator Per Klaster (Radar Chart)</b>', font=dict(size=16)),
        template='plotly_white',
        height=500
    )
    return fig

# Configuration for Kesra Social Assistance Eligibility
BANSOS_ELIGIBILITY_CONFIG = {
    0: {
        'status': '🔴 Prioritas 1 (Wajib Terima Bansos)',
        'short_badge': 'WAJIB TERIMA BANSOS',
        'badge_color': '#EF4444',
        'pagu_pct': '60%',
        'kesesuaian_kesra': 'Sangat Mendesak (Beban kemiskinan, pengangguran & kerentanan tertinggi)',
        'rekomendasi': 'Bansos Tunai PKH, BPNT, Beras Cadangan Pangan Pemerintah (CPP) 10kg, & Padat Karya Tunai Kesra'
    },
    1: {
        'status': '🟡 Prioritas 2 (Penerima Bansos Bersyarat)',
        'short_badge': 'BANSOS BERSYARAT',
        'badge_color': '#F59E0B',
        'pagu_pct': '30%',
        'kesesuaian_kesra': 'Waspada (Beban kerentanan dan pengangguran tingkat menengah)',
        'rekomendasi': 'Pelatihan Vokasi Kerja, Bantuan Modal Bergulir UMKM, & Bansos Bersyarat'
    },
    2: {
        'status': '🟢 Prioritas 3 (Wilayah Mandiri / Terbatas)',
        'short_badge': 'MANDIRI / MINIMAL',
        'badge_color': '#10B981',
        'pagu_pct': '10%',
        'kesesuaian_kesra': 'Mandiri (Indikator kesejahteraan, daya beli, dan IPM relatif tinggi)',
        'rekomendasi': 'Pembinaan UMKM Mandiri, Pemberdayaan Usaha, & Kuota Tanggap Darurat Bencana'
    }
}

def create_palembang_map(df_result: pd.DataFrame):
    """
    [PETA LAMA] Generates the classic interactive Folium Map centered on Palembang.
    Displays standard fixed-radius circles colored by cluster.
    """
    # Base Map centered on Palembang with free, watermark-free tiles
    m = folium.Map(
        location=[-2.990, 104.755],
        zoom_start=12,
        tiles=None,
        control_scale=False
    )
    folium.TileLayer(
        tiles='https://tile.openstreetmap.org/{z}/{x}/{y}.png',
        attr='&copy; OpenStreetMap contributors',
        name='🗺️ OpenStreetMap (Default)',
        control=True
    ).add_to(m)
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}',
        attr='Tiles &copy; Esri',
        name='🏙️ Light Gray Canvas (Minimalis)',
        control=True
    ).add_to(m)
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Tiles &copy; Esri &mdash; Maxar, Earthstar Geographics',
        name='🛰️ Citra Satelit (Esri Imagery)',
        control=True
    ).add_to(m)
    folium.LayerControl(position='topright').add_to(m)
    m.options['attributionControl'] = False
    
    for _, row in df_result.iterrows():
        kec = row['Kecamatan']
        cluster_id = int(row['Cluster'])
        c_name = row['Kategori_Prioritas']
        color = CLUSTER_COLORS.get(cluster_id, 'gray')
        
        coords = KECAMATAN_COORDS.get(kec, (-2.990, 104.755))
        
        popup_html = f"""
        <div style="font-family: Arial, sans-serif; width: 220px;">
            <h4 style="margin: 0 0 5px 0; color: #1E293B;">Kec. {kec}</h4>
            <span style="background-color: {color}; color: white; padding: 3px 8px; border-radius: 12px; font-weight: bold; font-size: 11px;">
                {c_name}
            </span>
            <hr style="margin: 8px 0; border: 0; border-top: 1px solid #E2E8F0;">
            <table style="width: 100%; font-size: 11px; color: #334155;">
                <tr><td><b>Penduduk Miskin:</b></td><td>{row.get('Jumlah_Penduduk_Miskin', 0):,} jiwa</td></tr>
                <tr><td><b>Pengangguran:</b></td><td>{row.get('Tingkat_Pengangguran', 0)} %</td></tr>
                <tr><td><b>Pendapatan:</b></td><td>Rp {row.get('Pendapatan_Rata_Rata', 0):,}/bln</td></tr>
                <tr><td><b>IPM:</b></td><td>{row.get('IPM', 0)}</td></tr>
            </table>
        </div>
        """
        
        folium.CircleMarker(
            location=coords,
            radius=12 + (cluster_id == 0) * 4,
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=f"<b>Kec. {kec}</b> ({c_name})",
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.75,
            weight=2
        ).add_to(m)
        
    return m

def create_kesra_bansos_map(
    df_result: pd.DataFrame,
    filter_status: str = "Semua Wilayah (18 Kecamatan)",
    bubble_metric: str = "Jumlah_Penduduk_Miskin"
):
    """
    [PETA BARU] Generates an advanced interactive Folium Map centered on Palembang showing:
    - Regions eligible for Kesra social assistance
    - Dynamic bubble markers scaled to poverty or vulnerability
    - Visual indicators (pulsing ring for priority 1)
    - Rich informative tooltip and popup with Kesra suitability & recommendations
    - Floating interactive map legend
    """
    # Filtering based on user selection
    df_map = df_result.copy()
    if "Prioritas 1" in filter_status:
        df_map = df_map[df_map['Cluster'] == 0]
    elif "Prioritas 2" in filter_status:
        df_map = df_map[df_map['Cluster'] == 1]
    elif "Prioritas 3" in filter_status:
        df_map = df_map[df_map['Cluster'] == 2]

    # Center map on Palembang with free, watermark-free tiles
    m = folium.Map(
        location=[-2.990, 104.755],
        zoom_start=12,
        tiles=None,
        control_scale=False
    )
    folium.TileLayer(
        tiles='https://tile.openstreetmap.org/{z}/{x}/{y}.png',
        attr='&copy; OpenStreetMap contributors',
        name='🗺️ OpenStreetMap (Default)',
        control=True
    ).add_to(m)
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}',
        attr='Tiles &copy; Esri',
        name='🏙️ Light Gray Canvas (Minimalis)',
        control=True
    ).add_to(m)
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Tiles &copy; Esri &mdash; Maxar, Earthstar Geographics',
        name='🛰️ Citra Satelit (Esri Imagery)',
        control=True
    ).add_to(m)
    folium.LayerControl(position='topright').add_to(m)
    m.options['attributionControl'] = False

    # Metric scaling bounds
    metric_col = bubble_metric if bubble_metric in df_result.columns else 'Jumlah_Penduduk_Miskin'
    metric_vals = pd.to_numeric(df_result[metric_col], errors='coerce').fillna(0)
    m_min = metric_vals.min()
    m_max = metric_vals.max()

    def calc_radius(val):
        if m_max > m_min:
            norm = (val - m_min) / (m_max - m_min)
            return 11 + (norm * 18) # 11px to 29px
        return 14

    for _, row in df_map.iterrows():
        kec = row['Kecamatan']
        cluster_id = int(row['Cluster'])
        cfg = BANSOS_ELIGIBILITY_CONFIG.get(cluster_id, BANSOS_ELIGIBILITY_CONFIG[1])
        color = cfg['badge_color']
        badge_text = cfg['short_badge']
        status_full = cfg['status']
        rekomendasi_text = cfg['rekomendasi']
        kesesuaian_kesra = cfg['kesesuaian_kesra']
        pagu_pct = cfg['pagu_pct']

        coords = KECAMATAN_COORDS.get(kec, (-2.990, 104.755))
        metric_val = row.get(metric_col, 0)
        radius = calc_radius(metric_val)

        # Highlight Priority 1 (Darurat / Wajib Bansos) with double outer halo ring
        if cluster_id == 0:
            folium.CircleMarker(
                location=coords,
                radius=radius + 10,
                color='#EF4444',
                fill=True,
                fill_color='#EF4444',
                fill_opacity=0.22,
                weight=1.5,
                dash_array='4, 4',
                interactive=False
            ).add_to(m)

        # Build Rich HTML Popup
        miskin_val = row.get('Jumlah_Penduduk_Miskin', 0)
        pengangguran_val = row.get('Tingkat_Pengangguran', 0)
        pendapatan_val = row.get('Pendapatan_Rata_Rata', 0)
        ipm_val = row.get('IPM', 0)
        cvi_val = row.get('Skor_Kerentanan', 0.0)
        kk_bansos_val = row.get('Jumlah_KK_Penerima_Bansos', 0)

        popup_html = f"""
        <div style="font-family: 'Plus Jakarta Sans', Arial, sans-serif; width: 275px; color: #1E293B; line-height: 1.4;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                <h4 style="margin: 0; font-size: 15px; font-weight: 800; color: #0F172A;">Kec. {kec}</h4>
                <span style="background-color: {color}; color: white; padding: 3px 8px; border-radius: 10px; font-weight: bold; font-size: 10px; letter-spacing: 0.5px;">
                    {badge_text}
                </span>
            </div>
            
            <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 8px; margin-bottom: 8px; font-size: 11px;">
                <div style="color: #64748B; font-weight: 600; margin-bottom: 2px;">STATUS KESESUAIAN KESRA:</div>
                <div style="color: #0F172A; font-weight: bold;">{status_full} ({pagu_pct})</div>
                <div style="color: #475569; font-size: 10px; margin-top: 2px;">{kesesuaian_kesra}</div>
            </div>

            <table style="width: 100%; font-size: 11px; border-collapse: collapse; margin-bottom: 8px;">
                <tr style="border-bottom: 1px solid #F1F5F9;">
                    <td style="padding: 3px 0; color: #64748B;">👥 Penduduk Miskin:</td>
                    <td style="padding: 3px 0; text-align: right; font-weight: bold; color: {color};">{miskin_val:,} Jiwa</td>
                </tr>
                <tr style="border-bottom: 1px solid #F1F5F9;">
                    <td style="padding: 3px 0; color: #64748B;">💼 Pengangguran:</td>
                    <td style="padding: 3px 0; text-align: right; font-weight: bold;">{pengangguran_val}%</td>
                </tr>
                <tr style="border-bottom: 1px solid #F1F5F9;">
                    <td style="padding: 3px 0; color: #64748B;">💵 Pendapatan Rata-rata:</td>
                    <td style="padding: 3px 0; text-align: right; font-weight: bold;">Rp {pendapatan_val:,}</td>
                </tr>
                <tr style="border-bottom: 1px solid #F1F5F9;">
                    <td style="padding: 3px 0; color: #64748B;">📊 Skor Kerentanan (CVI):</td>
                    <td style="padding: 3px 0; text-align: right; font-weight: bold; color: {color};">{cvi_val:.4f}</td>
                </tr>
                <tr style="border-bottom: 1px solid #F1F5F9;">
                    <td style="padding: 3px 0; color: #64748B;">🏠 KK Bansos Eksisting:</td>
                    <td style="padding: 3px 0; text-align: right; font-weight: bold;">{kk_bansos_val:,} KK</td>
                </tr>
                <tr>
                    <td style="padding: 3px 0; color: #64748B;">📈 IPM:</td>
                    <td style="padding: 3px 0; text-align: right; font-weight: bold;">{ipm_val}</td>
                </tr>
            </table>

            <div style="background: #EFF6FF; border-left: 3px solid #3B82F6; padding: 6px 8px; font-size: 10.5px; border-radius: 4px;">
                <b style="color: #1E40AF;">💡 Rekomendasi Bansos Kesra:</b><br>
                <span style="color: #1E3A8A;">{rekomendasi_text}</span>
            </div>
        </div>
        """

        metric_label = metric_col.replace('_', ' ')
        formatted_metric = f"{int(metric_val):,}" if metric_val > 100 else f"{metric_val:.2f}"
        tooltip_html = f"<b>Kec. {kec}</b> &bull; <span style='color:{color}; font-weight:bold;'>{badge_text}</span><br>{metric_label}: <b>{formatted_metric}</b>"

        folium.CircleMarker(
            location=coords,
            radius=radius,
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=tooltip_html,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.82,
            weight=2.5
        ).add_to(m)

    # Integrated Floating Map Legend
    legend_html = f"""
    <div style="
        position: fixed; 
        bottom: 25px; left: 25px; width: 255px; 
        background-color: rgba(255, 255, 255, 0.96);
        border: 1.5px solid #CBD5E1;
        border-radius: 12px;
        box-shadow: 0 10px 25px -5px rgba(0,0,0,0.22);
        z-index: 9999;
        font-family: Arial, sans-serif;
        font-size: 11px;
        color: #1E293B;
        padding: 12px 14px;
    ">
        <div style="font-weight: 800; font-size: 12px; margin-bottom: 8px; color: #0F172A; display:flex; align-items:center; gap:6px;">
            <span>🗺️</span> <span>Status Wilayah Penerima Bansos</span>
        </div>
        <div style="display:flex; align-items:center; margin-bottom: 6px;">
            <span style="display:inline-block; width:13px; height:13px; background:#EF4444; border-radius:50%; margin-right:8px; border:2px solid #B91C1C; flex-shrink:0;"></span>
            <div><b>Prioritas 1:</b> Wajib Bansos (Pagu 60%)</div>
        </div>
        <div style="display:flex; align-items:center; margin-bottom: 6px;">
            <span style="display:inline-block; width:13px; height:13px; background:#F59E0B; border-radius:50%; margin-right:8px; border:2px solid #D97706; flex-shrink:0;"></span>
            <div><b>Prioritas 2:</b> Bansos Bersyarat (Pagu 30%)</div>
        </div>
        <div style="display:flex; align-items:center; margin-bottom: 6px;">
            <span style="display:inline-block; width:13px; height:13px; background:#10B981; border-radius:50%; margin-right:8px; border:2px solid #059669; flex-shrink:0;"></span>
            <div><b>Prioritas 3:</b> Wilayah Mandiri (Pagu 10%)</div>
        </div>
        <div style="margin-top: 8px; padding-top: 6px; border-top: 1px dashed #E2E8F0; font-size: 10px; color: #64748B;">
            Ukuran lingkaran: <b>{metric_col.replace('_', ' ')}</b>
        </div>
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

    return m

def plot_bansos_recipient_ranking(df_result: pd.DataFrame):
    """
    Peta Grafik Bar Horizontal: Menampilkan seluruh kecamatan diurutkan berdasarkan
    kelayakan penerimaan bantuan sosial dari data statistik Kesra.
    Label angka KK penerima dan status diletakkan di luar bar agar terbaca sangat jelas & tajam.
    """
    df_sorted = df_result.sort_values(by='Skor_Kerentanan', ascending=True).copy()
    
    colors = [CLUSTER_COLORS.get(int(c), '#9CA3AF') for c in df_sorted['Cluster']]
    
    text_labels = []
    hover_texts = []
    for _, row in df_sorted.iterrows():
        c_id = int(row['Cluster'])
        cvi = row.get('Skor_Kerentanan', 0.0)
        kk_penerima = int(row.get('Jumlah_KK_Penerima_Bansos', row.get('Jumlah_Penduduk_Miskin', 0)))
        badge = "🔴 Wajib" if c_id == 0 else ("🟡 Bersyarat" if c_id == 1 else "🟢 Mandiri")
        
        # Label teks di luar bar: tebal, jelas, dan kontras tinggi
        text_labels.append(f" <b>{kk_penerima:,} KK</b> ({badge})")
            
        hover_texts.append(
            f"<b>Kecamatan {row['Kecamatan']}</b><br>"
            f"Status Kelayakan: <b>{badge}</b><br>"
            f"Jumlah Penerima Bansos: <b>{kk_penerima:,} KK</b><br>"
            f"Skor Kerentanan (CVI): <b>{cvi:.4f}</b>"
        )
            
    fig = gg.Figure()
    fig.add_trace(gg.Bar(
        y=df_sorted['Kecamatan'],
        x=df_sorted['Skor_Kerentanan'],
        orientation='h',
        marker=dict(
            color=colors,
            line=dict(color='rgba(15, 23, 42, 0.35)', width=1)
        ),
        text=text_labels,
        textposition='outside',
        cliponaxis=False,
        textfont=dict(size=12, family='Plus Jakarta Sans, Arial'),
        hovertext=hover_texts,
        hoverinfo='text'
    ))
    
    # Threshold indicator line for Priority 1 cut-off
    p1_rows = df_result[df_result['Cluster'] == 0]
    if not p1_rows.empty:
        p1_cvi_min = p1_rows['Skor_Kerentanan'].min()
        fig.add_vline(
            x=p1_cvi_min,
            line_width=2,
            line_dash="dash",
            line_color="#EF4444",
            annotation_text="Batas Wajib Bansos",
            annotation_position="bottom right",
            annotation_font=dict(color="#EF4444", size=10.5, family='Plus Jakarta Sans, Arial')
        )
        
    fig.update_layout(
        title=dict(
            text='<b>📊 Peta Grafik Peringkat Wilayah & Jumlah Penerima Bansos (KK)</b><br><span style="font-size:12px;">Menampilkan kuota penerima bantuan (KK) per wilayah sesuai data Kesra</span>',
            font=dict(size=14)
        ),
        xaxis=dict(
            title='Skor Indeks Kerentanan (CVI)',
            range=[0, max(df_sorted['Skor_Kerentanan'].max() * 1.55, 1.40)],
            tickfont=dict(size=11)
        ),
        yaxis=dict(
            title='',
            tickfont=dict(size=12, family='Plus Jakarta Sans, Arial')
        ),
        template='plotly_white',
        height=620,
        margin=dict(l=20, r=40, t=75, b=30)
    )
    return fig

def plot_bansos_eligibility_donut(df_result: pd.DataFrame):
    """
    Diagram Donut Proporsi Status Wilayah Penerima Bantuan Sosial Kesra.
    """
    summary_counts = df_result['Cluster'].value_counts().sort_index()
    labels = []
    values = []
    colors = []
    
    for c_id in [0, 1, 2]:
        if c_id in summary_counts:
            cnt = summary_counts[c_id]
            pct = (cnt / len(df_result)) * 100
            if c_id == 0:
                labels.append(f"🔴 Wajib Bansos ({cnt} Kec / {pct:.0f}%)")
                colors.append('#EF4444')
            elif c_id == 1:
                labels.append(f"🟡 Bantuan Bersyarat ({cnt} Kec / {pct:.0f}%)")
                colors.append('#F59E0B')
            else:
                labels.append(f"🟢 Wilayah Mandiri ({cnt} Kec / {pct:.0f}%)")
                colors.append('#10B981')
            values.append(cnt)
            
    fig = gg.Figure()
    fig.add_trace(gg.Pie(
        labels=labels,
        values=values,
        hole=0.58,
        marker=dict(colors=colors, line=dict(color='#FFFFFF', width=2)),
        textinfo='label+percent',
        textposition='inside',
        hoverinfo='label+value',
        insidetextfont=dict(size=11, color='white')
    ))
    
    fig.add_annotation(
        text=f"<b>{len(df_result)}</b><br><span style='font-size:11px; color:#64748B;'>Wilayah</span>",
        x=0.5, y=0.5,
        font=dict(size=18, family='Plus Jakarta Sans, Arial', color='#0F172A'),
        showarrow=False
    )
    
    fig.update_layout(
        title=dict(
            text='<b>🍩 Proporsi Status Kelayakan Wilayah</b><br><span style="font-size:12px; color:#64748B;">Distribusi kelayakan penerimaan bansos Kota Palembang</span>',
            font=dict(size=14)
        ),
        template='plotly_white',
        height=380,
        margin=dict(l=20, r=20, t=65, b=20),
        legend=dict(orientation='h', yanchor='bottom', y=-0.15, xanchor='center', x=0.5)
    )
    return fig

def plot_kesra_suitability_quadrant(df_result: pd.DataFrame):
    """
    Peta Kuadran Kesesuaian Bantuan: Hubungan Beban Kemiskinan (Jiwa) vs Pendapatan Rata-Rata.
    Membuktikan secara objektif posisi kelayakan tiap wilayah sesuai data statistik Kesra.
    """
    fig = gg.Figure()
    
    for c_id in [0, 1, 2]:
        sub = df_result[df_result['Cluster'] == c_id]
        if sub.empty:
            continue
            
        cfg = BANSOS_ELIGIBILITY_CONFIG.get(c_id, BANSOS_ELIGIBILITY_CONFIG[1])
        c_name = cfg['status']
        color = cfg['badge_color']
        
        # Calculate marker sizes
        sizes = [max(12, int(cvi * 26)) for cvi in sub['Skor_Kerentanan']]
        
        hover_texts = [
            f"<b>Kec. {row['Kecamatan']}</b><br>"
            f"Status: {c_name}<br>"
            f"Penduduk Miskin: {int(row.get('Jumlah_Penduduk_Miskin', 0)):,} Jiwa<br>"
            f"Pendapatan: Rp {int(row.get('Pendapatan_Rata_Rata', 0)):,}/bln<br>"
            f"Pengangguran: {row.get('Tingkat_Pengangguran', 0)}%<br>"
            f"Skor CVI: {row.get('Skor_Kerentanan', 0):.4f}"
            for _, row in sub.iterrows()
        ]
        
        fig.add_trace(gg.Scatter(
            x=sub['Pendapatan_Rata_Rata'],
            y=sub['Jumlah_Penduduk_Miskin'],
            mode='markers+text',
            marker=dict(
                size=sizes,
                color=color,
                line=dict(color='#1E293B', width=1.5),
                opacity=0.88
            ),
            text=sub['Kecamatan'],
            textposition='top center',
            textfont=dict(size=10, color='#1E293B'),
            name=c_name,
            hovertext=hover_texts,
            hoverinfo='text'
        ))
        
    # Median guidelines
    med_income = df_result['Pendapatan_Rata_Rata'].median()
    med_poor = df_result['Jumlah_Penduduk_Miskin'].median()
    
    fig.add_vline(x=med_income, line_width=1, line_dash='dot', line_color='#94A3B8')
    fig.add_hline(y=med_poor, line_width=1, line_dash='dot', line_color='#94A3B8')
    
    # Quadrant annotations
    fig.add_annotation(
        x=df_result['Pendapatan_Rata_Rata'].min() * 1.05,
        y=df_result['Jumlah_Penduduk_Miskin'].max() * 0.98,
        text="<b>⚠️ ZONA MERAH (WAJIB BANSOS)</b><br>Kemiskinan Tinggi, Pendapatan Rendah",
        showarrow=False,
        align='left',
        font=dict(color='#DC2626', size=9.5),
        bgcolor='rgba(254, 226, 226, 0.75)',
        bordercolor='#EF4444',
        borderwidth=1,
        borderpad=4
    )
    
    fig.add_annotation(
        x=df_result['Pendapatan_Rata_Rata'].max() * 0.95,
        y=df_result['Jumlah_Penduduk_Miskin'].min() * 1.05,
        text="<b>✅ ZONA HIJAU (MANDIRI)</b><br>Kemiskinan Rendah, Pendapatan Tinggi",
        showarrow=False,
        align='right',
        font=dict(color='#059669', size=9.5),
        bgcolor='rgba(209, 250, 229, 0.75)',
        bordercolor='#10B981',
        borderwidth=1,
        borderpad=4
    )
    
    fig.update_layout(
        title=dict(
            text='<b>🎯 Peta Kuadran Kesesuaian Bantuan: Beban Kemiskinan vs Pendapatan</b><br><span style="font-size:12px; color:#64748B;">Validasi korelasi indikator statistik Kesra terhadap penetapan zona penerima bantuan</span>',
            font=dict(size=14)
        ),
        xaxis=dict(title='Pendapatan Rata-Rata Penduduk (Rp/Bulan)', tickprefix='Rp '),
        yaxis=dict(title='Jumlah Penduduk Miskin (Jiwa)'),
        template='plotly_white',
        height=400,
        margin=dict(l=20, r=20, t=65, b=20),
        legend=dict(orientation='h', yanchor='bottom', y=-0.25, xanchor='center', x=0.5)
    )
    return fig

