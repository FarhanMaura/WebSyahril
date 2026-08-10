import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, silhouette_samples, davies_bouldin_score, calinski_harabasz_score

# 7 Official Indicators from Table 3.2 / Table 7 of Skripsi Document
INDICATORS = [
    'Jumlah_Penduduk_Miskin',
    'Tingkat_Pengangguran',
    'Pendapatan_Rata_Rata',
    'Kepadatan_Penduduk',
    'Akses_Fasilitas_Publik',
    'Jumlah_KK_Penerima_Bansos',
    'IPM'
]

# Indicators where HIGHER value means HIGHER vulnerability (Need Bansos)
HIGH_VULNERABILITY_INDICATORS = [
    'Jumlah_Penduduk_Miskin',
    'Tingkat_Pengangguran',
    'Kepadatan_Penduduk',
    'Jumlah_KK_Penerima_Bansos'
]

# Indicators where HIGHER value means LOWER vulnerability (More prosperous)
LOW_VULNERABILITY_INDICATORS = [
    'Pendapatan_Rata_Rata',
    'Akses_Fasilitas_Publik',
    'IPM'
]

def preprocess_data(df: pd.DataFrame, feature_cols: list = None):
    """
    Normalizes data using Min-Max Scaling [0, 1] per Formula:
    X_scaled = (X - X_min) / (X_max - X_min)
    """
    if feature_cols is None:
        feature_cols = [c for c in INDICATORS if c in df.columns]
    
    scaler = MinMaxScaler()
    scaled_array = scaler.fit_transform(df[feature_cols])
    df_scaled = pd.DataFrame(scaled_array, columns=feature_cols, index=df.index)
    return df_scaled, scaler, feature_cols

def calculate_vulnerability_index(df_scaled: pd.DataFrame):
    """
    Calculates Composite Vulnerability Index (CVI) per row (0.0 to 1.0).
    Inverts low vulnerability attributes (Pendapatan, Akses, IPM).
    """
    cvi_series = pd.Series(0.0, index=df_scaled.index)
    count = 0
    
    for col in df_scaled.columns:
        if col in HIGH_VULNERABILITY_INDICATORS:
            cvi_series += df_scaled[col]
            count += 1
        elif col in LOW_VULNERABILITY_INDICATORS:
            cvi_series += (1.0 - df_scaled[col])
            count += 1
        else:
            cvi_series += df_scaled[col]
            count += 1
            
    if count > 0:
        cvi_series /= count
    return cvi_series

def run_kmeans_clustering(df_raw: pd.DataFrame, n_clusters: int = 3, feature_cols: list = None):
    """
    Executes K-Means Clustering on normalized data.
    Ensures Cluster 0 = High Priority (Highest Vulnerability / Darurat),
    Cluster 1 = Medium Priority (Waspada), Cluster 2 = Low Priority (Mandiri).
    """
    df_scaled, scaler, feature_cols = preprocess_data(df_raw, feature_cols)
    
    # K-Means execution per Skripsi methodology
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10, max_iter=300)
    raw_labels = kmeans.fit_predict(df_scaled)
    
    # Calculate Euclidean distance matrix from each point to each cluster centroid
    raw_centroids = kmeans.cluster_centers_
    distances = kmeans.transform(df_scaled) # Shape: (N, K)
    
    # Order clusters based on Composite Vulnerability Index (CVI)
    cvi = calculate_vulnerability_index(df_scaled)
    df_temp = pd.DataFrame({'raw_cluster': raw_labels, 'cvi': cvi})
    cluster_cvi_mean = df_temp.groupby('raw_cluster')['cvi'].mean().sort_values(ascending=False)
    
    # Mapping raw labels to ordered priority clusters (0 = High Priority, 1 = Med, 2 = Low...)
    mapping = {old_label: new_label for new_label, old_label in enumerate(cluster_cvi_mean.index)}
    ordered_labels = np.array([mapping[l] for l in raw_labels])
    
    # Re-order centroids and distance matrix columns to match ordered clusters
    ordered_centroids_scaled = np.zeros_like(raw_centroids)
    ordered_distances = np.zeros_like(distances)
    
    for old_idx, new_idx in mapping.items():
        ordered_centroids_scaled[new_idx] = raw_centroids[old_idx]
        ordered_distances[:, new_idx] = distances[:, old_idx]
        
    # Unscaled Centroids
    ordered_centroids_unscaled = scaler.inverse_transform(ordered_centroids_scaled)
    df_centroids_unscaled = pd.DataFrame(ordered_centroids_unscaled, columns=feature_cols)
    df_centroids_unscaled.index.name = 'Cluster'
    
    # Build Result DataFrame
    df_result = df_raw.copy()
    df_result['Cluster'] = ordered_labels
    df_result['Skor_Kerentanan'] = cvi.round(4)
    
    priority_labels = {
        0: 'Prioritas Tinggi (Darurat)',
        1: 'Prioritas Sedang (Waspada)',
        2: 'Prioritas Rendah (Mandiri)'
    }
    df_result['Kategori_Prioritas'] = df_result['Cluster'].map(
        lambda c: priority_labels.get(c, f'Prioritas Cluster {c+1}')
    )
    
    # Euclidean Distance columns for mathematical auditability (Bab 3/4 compliance)
    for c_idx in range(n_clusters):
        df_result[f'Jarak_Ke_Centroid_{c_idx}'] = ordered_distances[:, c_idx].round(4)
        
    # Minimum distance (d_min)
    df_result['Jarak_Terdekat_d_min'] = ordered_distances.min(axis=1).round(4)
    
    # Scientific Validation Metrics
    sil_score = float(silhouette_score(df_scaled, ordered_labels)) if n_clusters > 1 else 0.0
    sil_samples = silhouette_samples(df_scaled, ordered_labels) if n_clusters > 1 else np.zeros(len(df_raw))
    db_score = float(davies_bouldin_score(df_scaled, ordered_labels)) if n_clusters > 1 else 0.0
    ch_score = float(calinski_harabasz_score(df_scaled, ordered_labels)) if n_clusters > 1 else 0.0
    
    return {
        'df_result': df_result,
        'df_scaled': df_scaled,
        'feature_cols': feature_cols,
        'kmeans_model': kmeans,
        'scaler': scaler,
        'n_clusters': n_clusters,
        'silhouette_score': sil_score,
        'silhouette_samples': sil_samples,
        'davies_bouldin_score': db_score,
        'calinski_harabasz_score': ch_score,
        'cluster_summary': df_centroids_unscaled,
        'centroids_scaled': pd.DataFrame(ordered_centroids_scaled, columns=feature_cols),
        'wcss_inertia': float(kmeans.inertia_),
        'iterations_count': kmeans.n_iter_
    }

def compute_elbow_and_silhouette_range(df_raw: pd.DataFrame, max_k: int = 8, feature_cols: list = None):
    """
    Computes WCSS (Inertia), Silhouette Score, DBI, and CH Index for K = 1 to max_k.
    """
    df_scaled, _, feature_cols = preprocess_data(df_raw, feature_cols)
    k_range = list(range(1, max_k + 1))
    wcss = []
    silhouettes = []
    dbi_list = []
    ch_list = []
    
    for k in k_range:
        km = KMeans(n_clusters=k, random_state=42, n_init=10, max_iter=300)
        labels = km.fit_predict(df_scaled)
        wcss.append(float(km.inertia_))
        
        if k >= 2 and k < len(df_raw):
            score = float(silhouette_score(df_scaled, labels))
            db = float(davies_bouldin_score(df_scaled, labels))
            ch = float(calinski_harabasz_score(df_scaled, labels))
            silhouettes.append(score)
            dbi_list.append(db)
            ch_list.append(ch)
        else:
            silhouettes.append(0.0)
            dbi_list.append(0.0)
            ch_list.append(0.0)
            
    return pd.DataFrame({
        'K': k_range,
        'WCSS': wcss,
        'Silhouette_Score': silhouettes,
        'Davies_Bouldin_Index': dbi_list,
        'Calinski_Harabasz_Index': ch_list
    })
