import pandas as pd
import numpy as np

def simulate_bansos_allocation(df_result: pd.DataFrame, total_budget_rp: float = 5000000000.0, total_quota_kk: int = 10000):
    """
    DSS Allocation Simulator:
    Distributes total budget (Rp) and total quota (KK) among 18 kecamatan
    weighted by their Cluster Priority & Composite Vulnerability Score (CVI).
    
    Default weighting distribution:
    - Cluster 0 (Prioritas Tinggi): 60% of total pool
    - Cluster 1 (Prioritas Sedang): 30% of total pool
    - Cluster 2 (Prioritas Rendah): 10% of total pool
    """
    df_sim = df_result.copy()
    
    # Weights per cluster
    weights = {0: 0.60, 1: 0.30, 2: 0.10}
    
    df_sim['Cluster_Weight'] = df_sim['Cluster'].map(lambda c: weights.get(c, 0.10))
    
    # Sub-weight within each cluster proportional to Skor_Kerentanan
    cluster_cvi_sums = df_sim.groupby('Cluster')['Skor_Kerentanan'].transform('sum')
    df_sim['Relative_CVI_Weight'] = df_sim['Skor_Kerentanan'] / np.where(cluster_cvi_sums > 0, cluster_cvi_sums, 1.0)
    
    # Combined allocation weight
    df_sim['Final_Weight'] = df_sim['Cluster_Weight'] * df_sim['Relative_CVI_Weight']
    df_sim['Final_Weight'] /= df_sim['Final_Weight'].sum()
    
    # Allocated Budget & Quota per Kecamatan
    df_sim['Alokasi_Anggaran_Rp'] = (df_sim['Final_Weight'] * total_budget_rp).round(0)
    df_sim['Alokasi_Kuota_KK'] = (df_sim['Final_Weight'] * total_quota_kk).round(0).astype(int)
    
    # Average bantuan per KK in Rp
    df_sim['Nilai_Bantuan_Per_KK'] = (df_sim['Alokasi_Anggaran_Rp'] / np.where(df_sim['Alokasi_Kuota_KK'] > 0, df_sim['Alokasi_Kuota_KK'], 1)).round(0)
    
    return df_sim

def compare_yearly_trends(df_2023: pd.DataFrame, df_2025: pd.DataFrame):
    """
    Compares 2023/2024 vs 2025/2026 data per kecamatan to analyze shifts.
    """
    merged = pd.merge(
        df_2023[['Kecamatan', 'Jumlah_Penduduk_Miskin', 'Tingkat_Pengangguran', 'IPM']],
        df_2025[['Kecamatan', 'Jumlah_Penduduk_Miskin', 'Tingkat_Pengangguran', 'IPM']],
        on='Kecamatan',
        suffixes=('_2023', '_2025')
    )
    
    merged['Perubahan_Penduduk_Miskin'] = merged['Jumlah_Penduduk_Miskin_2025'] - merged['Jumlah_Penduduk_Miskin_2023']
    merged['Persen_Perubahan_Miskin'] = ((merged['Perubahan_Penduduk_Miskin'] / merged['Jumlah_Penduduk_Miskin_2023']) * 100).round(2)
    merged['Perubahan_IPM'] = (merged['IPM_2025'] - merged['IPM_2023']).round(2)
    
    return merged
