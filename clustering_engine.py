import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans, kmeans_plusplus
from sklearn.metrics import (
    silhouette_score,
    silhouette_samples,
    davies_bouldin_score,
    calinski_harabasz_score
)

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

INDICATOR_METADATA = {
    'Jumlah_Penduduk_Miskin': {
        'label': 'Jumlah Penduduk Miskin (Jiwa)',
        'unit': 'Jiwa',
        'type': 'High (Makin Tinggi = Makin Rentan)',
        'desc': 'Jumlah penduduk berpenghasilan di bawah garis kemiskinan BPS per kapita'
    },
    'Tingkat_Pengangguran': {
        'label': 'Tingkat Pengangguran Terbuka (%)',
        'unit': '%',
        'type': 'High (Makin Tinggi = Makin Rentan)',
        'desc': 'Persentase angkatan kerja aktif yang belum memperoleh pekerjaan'
    },
    'Pendapatan_Rata_Rata': {
        'label': 'Pendapatan Rata-Rata (Rp/Bulan)',
        'unit': 'Rp',
        'type': 'Low (Makin Tinggi = Makin Sejahtera)',
        'desc': 'Estimasi rata-rata pendapatan keluarga / per kapita bulanan'
    },
    'Kepadatan_Penduduk': {
        'label': 'Kepadatan Penduduk (Jiwa/Km²)',
        'unit': 'Jiwa/Km²',
        'type': 'High (Makin Tinggi = Makin Rentan)',
        'desc': 'Rasio konsentrasi kepadatan penduduk terhadap luas wilayah kecamatan'
    },
    'Akses_Fasilitas_Publik': {
        'label': 'Akses Fasilitas Publik (Skor 0-100)',
        'unit': 'Skor',
        'type': 'Low (Makin Tinggi = Makin Sejahtera)',
        'desc': 'Indeks ketersediaan dan keterjangkauan faskes, sekolah, dan sanitasi'
    },
    'Jumlah_KK_Penerima_Bansos': {
        'label': 'Jumlah KK Penerima Bansos (KK)',
        'unit': 'KK',
        'type': 'High (Makin Tinggi = Makin Rentan)',
        'desc': 'Jumlah kepala keluarga terdaftar sebagai penerima bansos eksisting'
    },
    'IPM': {
        'label': 'Indeks Pembangunan Manusia (IPM)',
        'unit': 'Poin',
        'type': 'Low (Makin Tinggi = Makin Sejahtera)',
        'desc': 'Capaian komposit pembangunan manusia (kesehatan, pendidikan, standar hidup)'
    }
}

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

def load_kesra_excel_data(file_source):
    """
    Robust reader for Kesra / BPS Palembang Excel format.
    Automatically detects header row, ignores top formal government header rows,
    filters out summary rows ('RATA-RATA', 'TOTAL', etc.),
    and maps column headers to official INDICATORS.
    """
    try:
        if isinstance(file_source, str) and not os.path.exists(file_source):
            return None
            
        df_raw = pd.read_excel(file_source, header=None)
        header_row_idx = None
        for idx, row in df_raw.iterrows():
            row_vals = [str(v).strip().lower() for v in row.values if pd.notna(v)]
            if any('kecamatan' in v for v in row_vals):
                header_row_idx = idx
                break
                
        if header_row_idx is not None:
            df = pd.read_excel(file_source, skiprows=header_row_idx)
        else:
            df = pd.read_excel(file_source)
            
        # Drop unnamed columns
        df = df.loc[:, ~df.columns.str.contains('^Unnamed', na=False)]
        
        # Identify Kecamatan column
        kec_col = None
        for col in df.columns:
            if 'kecamatan' in str(col).strip().lower():
                kec_col = col
                break
                
        if kec_col is None:
            return None
            
        if kec_col != 'Kecamatan':
            df = df.rename(columns={kec_col: 'Kecamatan'})
            
        # Exclude summary/aggregate rows
        exclude_keywords = ['rata-rata', 'total', 'jumlah', 'keseluruhan', 'provinsi']
        df = df[df['Kecamatan'].notna()].copy()
        df = df[~df['Kecamatan'].astype(str).str.lower().apply(lambda x: any(kw in x for kw in exclude_keywords))]
        
        if 'No' in df.columns:
            df = df.drop(columns=['No'])
            
        # Map column names to standard INDICATORS
        col_mapping = {}
        for col in df.columns:
            col_lower = str(col).lower()
            if 'miskin' in col_lower:
                col_mapping[col] = 'Jumlah_Penduduk_Miskin'
            elif 'pengangguran' in col_lower:
                col_mapping[col] = 'Tingkat_Pengangguran'
            elif 'pendapatan' in col_lower:
                col_mapping[col] = 'Pendapatan_Rata_Rata'
            elif 'kepadatan' in col_lower:
                col_mapping[col] = 'Kepadatan_Penduduk'
            elif 'fasilitas' in col_lower:
                col_mapping[col] = 'Akses_Fasilitas_Publik'
            elif 'kk' in col_lower or 'bansos' in col_lower:
                col_mapping[col] = 'Jumlah_KK_Penerima_Bansos'
            elif 'ipm' in col_lower:
                col_mapping[col] = 'IPM'
                
        df = df.rename(columns=col_mapping)
        
        # Defensive numeric conversion
        for ind in INDICATORS:
            if ind in df.columns:
                df[ind] = pd.to_numeric(df[ind], errors='coerce')
                
        return df.reset_index(drop=True)
    except Exception as e:
        print(f"Error loading Excel data: {e}")
        return None

def get_min_max_info(df_raw: pd.DataFrame, feature_cols: list = None):
    """
    Summarizes Min, Max, and Range for each indicator to clearly explain Min-Max Normalization.
    """
    if feature_cols is None:
        feature_cols = [c for c in INDICATORS if c in df_raw.columns]
        
    records = []
    for col in feature_cols:
        series = pd.to_numeric(df_raw[col], errors='coerce').dropna()
        col_min = float(series.min()) if len(series) > 0 else 0.0
        col_max = float(series.max()) if len(series) > 0 else 1.0
        col_range = col_max - col_min
        col_mean = float(series.mean()) if len(series) > 0 else 0.0
        meta = INDICATOR_METADATA.get(col, {})
        
        records.append({
            'Indikator': col,
            'Label_Resmi': meta.get('label', col),
            'Satuan': meta.get('unit', '-'),
            'Sifat': meta.get('type', '-'),
            'Nilai_Min': col_min,
            'Nilai_Max': col_max,
            'Rentang (Max - Min)': col_range,
            'Rata_Rata': round(col_mean, 2)
        })
    return pd.DataFrame(records)

def preprocess_data(df: pd.DataFrame, feature_cols: list = None):
    """
    Normalizes data using Min-Max Scaling [0, 1] per Formula:
    X_scaled = (X - X_min) / (X_max - X_min)
    """
    if feature_cols is None:
        feature_cols = [c for c in INDICATORS if c in df.columns]
    
    # Defensive type conversion to float
    df_features = df[feature_cols].copy()
    for col in feature_cols:
        df_features[col] = pd.to_numeric(df_features[col], errors='coerce').fillna(0.0)

    scaler = MinMaxScaler()
    scaled_array = scaler.fit_transform(df_features)
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

def run_step_by_step_kmeans(df_raw: pd.DataFrame, n_clusters: int = 3, feature_cols: list = None, random_state: int = 42, max_iter: int = 50, tol: float = 1e-4):
    """
    Executes a fully transparent, step-by-step K-Means algorithm tracking:
    - Step 1: Raw Excel Data & Min-Max stats
    - Step 2: Min-Max Normalized Data [0, 1]
    - Step 3: Initial Centroids Selection (Iteration 0)
    - Step 4: Full Per-Iteration History (Distances, Assignments, New Centroids, Shifts, Convergence)
    - Step 5: Scientific Validation Metrics (Elbow WCSS, Silhouette, DBI, CHI)
    - Step 6: Final Prioritized Clustering (High/Darurat, Medium/Waspada, Low/Mandiri) using CVI.
    """
    if feature_cols is None:
        feature_cols = [c for c in INDICATORS if c in df_raw.columns]
        
    # Step 1: Min-Max Summary
    min_max_info = get_min_max_info(df_raw, feature_cols)
    
    # Step 2: Normalization
    df_scaled, scaler, feature_cols = preprocess_data(df_raw, feature_cols)
    X = df_scaled.values
    N, M = X.shape
    kecamatan_names = df_raw['Kecamatan'].tolist() if 'Kecamatan' in df_raw.columns else [f"Wilayah_{i+1}" for i in range(N)]
    
    # Step 3: Initial Centroids Selection (K-Means++ Deterministic)
    init_centroids_scaled, init_indices = kmeans_plusplus(X, n_clusters=n_clusters, random_state=random_state)
    init_centroids_unscaled = scaler.inverse_transform(init_centroids_scaled)
    
    df_init_scaled = pd.DataFrame(init_centroids_scaled, columns=feature_cols)
    df_init_scaled.index = [f"Centroid {i}" for i in range(n_clusters)]
    
    df_init_unscaled = pd.DataFrame(init_centroids_unscaled, columns=feature_cols)
    df_init_unscaled.index = [f"Centroid {i}" for i in range(n_clusters)]
    
    # Step 4: Iteration Tracking Loop
    current_centroids = init_centroids_scaled.copy()
    iterations_history = []
    prev_labels = None
    converged_iteration = None
    
    for iter_idx in range(1, max_iter + 1):
        # Euclidean distance: d(xi, cj) = sqrt(sum((xik - cjk)^2))
        diff = X[:, np.newaxis, :] - current_centroids[np.newaxis, :, :]
        distances = np.linalg.norm(diff, axis=2) # shape (N, K)
        
        # Cluster assignment: argmin d(xi, c)
        cluster_labels = np.argmin(distances, axis=1)
        min_distances = np.min(distances, axis=1)
        
        # Distance table for this iteration
        iter_dist_dict = {'Kecamatan': kecamatan_names}
        for k in range(n_clusters):
            iter_dist_dict[f'Jarak_Ke_C{k}'] = distances[:, k].round(4)
        iter_dist_dict['Jarak_Terdekat_d_min'] = min_distances.round(4)
        iter_dist_dict['Klaster_Sementara'] = [f"Cluster {l}" for l in cluster_labels]
        df_iter_dist = pd.DataFrame(iter_dist_dict)
        
        # Members per cluster
        members_per_cluster = {}
        counts_per_cluster = {}
        for k in range(n_clusters):
            k_members = [kecamatan_names[i] for i in range(N) if cluster_labels[i] == k]
            members_per_cluster[k] = k_members
            counts_per_cluster[k] = len(k_members)
            
        # Update centroids: mean of assigned points
        new_centroids = np.zeros_like(current_centroids)
        for k in range(n_clusters):
            pts = X[cluster_labels == k]
            if len(pts) > 0:
                new_centroids[k] = pts.mean(axis=0)
            else:
                new_centroids[k] = current_centroids[k]
                
        # Centroid shift
        shift_per_cluster = np.linalg.norm(new_centroids - current_centroids, axis=1)
        total_shift = float(np.sum(shift_per_cluster))
        
        # Convergence check
        labels_unchanged = (prev_labels is not None) and np.array_equal(prev_labels, cluster_labels)
        is_converged = (total_shift < tol) or labels_unchanged
        
        # Store iteration state
        centroids_end_unscaled = scaler.inverse_transform(new_centroids)
        df_new_scaled = pd.DataFrame(new_centroids, columns=feature_cols)
        df_new_scaled.index = [f"Centroid {k}" for k in range(n_clusters)]
        df_new_unscaled = pd.DataFrame(centroids_end_unscaled, columns=feature_cols)
        df_new_unscaled.index = [f"Centroid {k}" for k in range(n_clusters)]
        
        iter_record = {
            'iteration_number': iter_idx,
            'centroids_start_scaled': pd.DataFrame(current_centroids, columns=feature_cols, index=[f"Centroid {k}" for k in range(n_clusters)]),
            'centroids_start_unscaled': pd.DataFrame(scaler.inverse_transform(current_centroids), columns=feature_cols, index=[f"Centroid {k}" for k in range(n_clusters)]),
            'distances_df': df_iter_dist,
            'cluster_labels': cluster_labels.copy(),
            'cluster_members': members_per_cluster,
            'cluster_counts': counts_per_cluster,
            'centroids_end_scaled': df_new_scaled,
            'centroids_end_unscaled': df_new_unscaled,
            'shift_per_cluster': {f"Centroid {k}": round(float(shift_per_cluster[k]), 5) for k in range(n_clusters)},
            'total_shift': round(total_shift, 5),
            'is_converged': is_converged
        }
        iterations_history.append(iter_record)
        
        prev_labels = cluster_labels.copy()
        current_centroids = new_centroids.copy()
        
        if is_converged:
            converged_iteration = iter_idx
            break
            
    if converged_iteration is None:
        converged_iteration = len(iterations_history)
        
    # Calculate Composite Vulnerability Index (CVI)
    cvi = calculate_vulnerability_index(df_scaled)
    
    # Priority Ordering based on CVI
    final_raw_labels = iterations_history[-1]['cluster_labels']
    df_temp = pd.DataFrame({'raw_cluster': final_raw_labels, 'cvi': cvi})
    cluster_cvi_mean = df_temp.groupby('raw_cluster')['cvi'].mean().sort_values(ascending=False)
    
    mapping = {old_label: new_label for new_label, old_label in enumerate(cluster_cvi_mean.index)}
    ordered_labels = np.array([mapping[l] for l in final_raw_labels])
    
    final_raw_centroids_scaled = current_centroids
    ordered_centroids_scaled = np.zeros_like(final_raw_centroids_scaled)
    for old_idx, new_idx in mapping.items():
        ordered_centroids_scaled[new_idx] = final_raw_centroids_scaled[old_idx]
        
    ordered_centroids_unscaled = scaler.inverse_transform(ordered_centroids_scaled)
    df_centroids_unscaled = pd.DataFrame(ordered_centroids_unscaled, columns=feature_cols)
    df_centroids_unscaled.index.name = 'Cluster'
    
    # Compute final ordered Euclidean distances
    final_diff = X[:, np.newaxis, :] - ordered_centroids_scaled[np.newaxis, :, :]
    ordered_distances = np.linalg.norm(final_diff, axis=2)
    
    # Final Results DataFrame
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
    
    for c_idx in range(n_clusters):
        df_result[f'Jarak_Ke_Centroid_{c_idx}'] = ordered_distances[:, c_idx].round(4)
    df_result['Jarak_Terdekat_d_min'] = ordered_distances.min(axis=1).round(4)
    
    # Scientific Validation Metrics
    n_distinct_labels = len(np.unique(ordered_labels))
    if 1 < n_distinct_labels < len(df_raw):
        try:
            sil_score = float(silhouette_score(df_scaled, ordered_labels))
            sil_samples = silhouette_samples(df_scaled, ordered_labels)
            db_score = float(davies_bouldin_score(df_scaled, ordered_labels))
            ch_score = float(calinski_harabasz_score(df_scaled, ordered_labels))
        except Exception:
            sil_score = 0.0
            sil_samples = np.zeros(len(df_raw))
            db_score = 0.0
            ch_score = 0.0
    else:
        sil_score, sil_samples, db_score, ch_score = 0.0, np.zeros(len(df_raw)), 0.0, 0.0
        
    # Final WCSS (Inertia) = sum of squared distances to closest centroid
    final_wcss = float(np.sum((ordered_distances.min(axis=1)) ** 2))
    
    class SimpleKMeansWrapper:
        def __init__(self, inertia, n_iter, cluster_centers):
            self.inertia_ = inertia
            self.n_iter_ = n_iter
            self.cluster_centers_ = cluster_centers
            
    kmeans_wrapper = SimpleKMeansWrapper(final_wcss, converged_iteration, ordered_centroids_scaled)
    elbow_df = compute_elbow_and_silhouette_range(df_raw, max_k=min(8, len(df_raw)-1), feature_cols=feature_cols)
    
    return {
        'df_result': df_result,
        'df_raw': df_raw,
        'min_max_info': min_max_info,
        'df_scaled': df_scaled,
        'feature_cols': feature_cols,
        'scaler': scaler,
        'n_clusters': n_clusters,
        'initial_centroids_scaled': df_init_scaled,
        'initial_centroids_unscaled': df_init_unscaled,
        'initial_indices': init_indices,
        'iterations': iterations_history,
        'total_iterations': converged_iteration,
        'is_converged': True,
        'silhouette_score': sil_score,
        'silhouette_samples': sil_samples,
        'davies_bouldin_score': db_score,
        'calinski_harabasz_score': ch_score,
        'cluster_summary': df_centroids_unscaled,
        'centroids_scaled': pd.DataFrame(ordered_centroids_scaled, columns=feature_cols),
        'wcss_inertia': final_wcss,
        'iterations_count': converged_iteration,
        'kmeans_model': kmeans_wrapper,
        'elbow_df': elbow_df
    }

def run_kmeans_clustering(df_raw: pd.DataFrame, n_clusters: int = 3, feature_cols: list = None):
    """
    Standard entrypoint executing K-Means with full step-by-step tracing.
    Ensures backwards compatibility with all previous callers.
    """
    return run_step_by_step_kmeans(df_raw, n_clusters=n_clusters, feature_cols=feature_cols)

def compute_elbow_and_silhouette_range(df_raw: pd.DataFrame, max_k: int = 8, feature_cols: list = None):
    """
    Computes WCSS (Inertia), Silhouette Score, DBI, and CH Index for K = 1 to max_k.
    """
    df_scaled, _, feature_cols = preprocess_data(df_raw, feature_cols)
    max_k = min(max_k, len(df_raw) - 1)
    k_range = list(range(1, max_k + 1))
    wcss = []
    silhouettes = []
    dbi_list = []
    ch_list = []
    
    for k in k_range:
        km = KMeans(n_clusters=k, random_state=42, n_init=10, max_iter=300)
        labels = km.fit_predict(df_scaled)
        wcss.append(float(km.inertia_))
        
        n_unique_l = len(np.unique(labels))
        if 1 < n_unique_l < len(df_raw):
            try:
                score = float(silhouette_score(df_scaled, labels))
                db = float(davies_bouldin_score(df_scaled, labels))
                ch = float(calinski_harabasz_score(df_scaled, labels))
            except Exception:
                score, db, ch = 0.0, 0.0, 0.0
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
