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

def plot_cluster_bar(df_result: pd.DataFrame, feature: str = 'Jumlah_Penduduk_Miskin'):
    """Generates bar chart comparing kecamatan values colored by cluster."""
    df_sorted = df_result.sort_values(by=feature, ascending=True)
    
    colors = [CLUSTER_COLORS.get(c, '#9CA3AF') for c in df_sorted['Cluster']]
    
    fig = gg.Figure()
    fig.add_trace(gg.Bar(
        y=df_sorted['Kecamatan'],
        x=df_sorted[feature],
        orientation='h',
        marker=dict(color=colors),
        text=df_sorted[feature].apply(lambda x: f"{x:,.0f}" if isinstance(x, (int, float)) and x > 100 else f"{x:.1f}"),
        textposition='outside'
    ))
    
    clean_title = feature.replace('_', ' ')
    fig.update_layout(
        title=dict(text=f'<b>Perbandingan {clean_title} Per Kecamatan</b>', font=dict(size=16)),
        xaxis=dict(title=clean_title),
        yaxis=dict(title='Kecamatan'),
        template='plotly_white',
        height=550,
        margin=dict(l=40, r=40, t=60, b=40)
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

def create_palembang_map(df_result: pd.DataFrame):
    """Generates an interactive Folium Map centered on Palembang without bottom attribution/logo text."""
    m = folium.Map(
        location=[-2.990, 104.755],
        zoom_start=12,
        tiles='CartoDB positron',
        attr='',
        control_scale=False
    )
    # Completely remove Leaflet bottom attribution & logo text
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
