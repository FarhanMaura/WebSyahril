import os
import sqlite3
import pandas as pd
from datetime import datetime

# Try importing pymysql for MySQL support
try:
    import pymysql
    HAS_PYMYSQL = True
except ImportError:
    HAS_PYMYSQL = False

# MySQL Configuration (Default XAMPP / Laragon / Local MySQL)
MYSQL_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '',
    'database': 'dss_bansos_palembang'
}

SQLITE_PATH = os.path.join(os.path.dirname(__file__), 'data', 'bansos_palembang.db')

DB_MODE = "SQLITE"

def test_mysql_connection():
    """Checks if local MySQL server is accessible."""
    if not HAS_PYMYSQL:
        return False
    try:
        conn = pymysql.connect(
            host=MYSQL_CONFIG['host'],
            port=MYSQL_CONFIG['port'],
            user=MYSQL_CONFIG['user'],
            password=MYSQL_CONFIG['password'],
            connect_timeout=2
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_CONFIG['database']} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False

def get_db_connection():
    """Returns MySQL or SQLite connection dynamically using standard tuples."""
    global DB_MODE
    if test_mysql_connection():
        try:
            conn = pymysql.connect(
                host=MYSQL_CONFIG['host'],
                port=MYSQL_CONFIG['port'],
                user=MYSQL_CONFIG['user'],
                password=MYSQL_CONFIG['password'],
                database=MYSQL_CONFIG['database'],
                autocommit=True
            )
            DB_MODE = "MYSQL"
            return conn, "MYSQL"
        except Exception:
            pass
    
    # Fallback to SQLite
    os.makedirs(os.path.dirname(SQLITE_PATH), exist_ok=True)
    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    DB_MODE = "SQLITE"
    return conn, "SQLITE"

def init_database():
    """Creates tables in MySQL and SQLite and seeds initial data."""
    conn, mode = get_db_connection()
    cursor = conn.cursor()

    if mode == "MYSQL":
        # 1. USERS
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id_user INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(100) NOT NULL,
            nama_lengkap VARCHAR(150) NOT NULL,
            role VARCHAR(50) NOT NULL,
            jabatan VARCHAR(100),
            instansi VARCHAR(150) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB;
        """)

        # 2. KECAMATAN
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS kecamatan (
            kecamatan VARCHAR(50) PRIMARY KEY,
            latitude DOUBLE NOT NULL,
            longitude DOUBLE NOT NULL,
            luas_wilayah_km2 DOUBLE,
            keterangan TEXT
        ) ENGINE=InnoDB;
        """)

        # 3. DATA_INDIKATOR_BPS
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS data_indikator_bps (
            id_data INT AUTO_INCREMENT PRIMARY KEY,
            kecamatan VARCHAR(50) NOT NULL,
            tahun_data INT NOT NULL,
            jumlah_penduduk_miskin INT NOT NULL,
            tingkat_pengangguran DOUBLE NOT NULL,
            pendapatan_rata_rata BIGINT NOT NULL,
            kepadatan_penduduk DOUBLE NOT NULL,
            akses_fasilitas_publik DOUBLE NOT NULL,
            jumlah_kk_penerima_bansos INT NOT NULL,
            ipm DOUBLE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (kecamatan) REFERENCES kecamatan(kecamatan) ON DELETE CASCADE,
            UNIQUE KEY uk_kec_tahun (kecamatan, tahun_data)
        ) ENGINE=InnoDB;
        """)

        # 4. KLASTER_PRIORITAS
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS klaster_prioritas (
            id_cluster INT PRIMARY KEY,
            nama_cluster VARCHAR(50) NOT NULL,
            status_prioritas VARCHAR(50) NOT NULL,
            bobot_alokasi_persen DOUBLE NOT NULL,
            rekomendasi_intervensi TEXT NOT NULL,
            warna_map VARCHAR(20) NOT NULL
        ) ENGINE=InnoDB;
        """)

        # 5. HASIL_CLUSTERING
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS hasil_clustering (
            id_hasil INT AUTO_INCREMENT PRIMARY KEY,
            kecamatan VARCHAR(50) NOT NULL,
            tahun_data VARCHAR(20) NOT NULL,
            id_cluster INT NOT NULL,
            kategori_prioritas VARCHAR(50) NOT NULL,
            skor_kerentanan DOUBLE NOT NULL,
            jarak_ke_centroid_0 DOUBLE,
            jarak_ke_centroid_1 DOUBLE,
            jarak_ke_centroid_2 DOUBLE,
            jarak_terdekat_dmin DOUBLE,
            eksekusi_by VARCHAR(100),
            waktu_proses TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (kecamatan) REFERENCES kecamatan(kecamatan) ON DELETE CASCADE
        ) ENGINE=InnoDB;
        """)

        # 6. SIMULASI_ALOKASI_BANSOS
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS simulasi_alokasi_bansos (
            id_simulasi INT AUTO_INCREMENT PRIMARY KEY,
            kecamatan VARCHAR(50) NOT NULL,
            tahun_data VARCHAR(20) NOT NULL,
            total_pagu_anggaran_rp DOUBLE NOT NULL,
            total_kuota_kk INT NOT NULL,
            final_weight DOUBLE NOT NULL,
            alokasi_anggaran_rp DOUBLE NOT NULL,
            alokasi_kuota_kk INT NOT NULL,
            nilai_bantuan_per_kk DOUBLE NOT NULL,
            simulasi_by VARCHAR(100),
            waktu_simulasi TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB;
        """)

        # 7. LAPORAN_EXPORT
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS laporan_export (
            id_export INT AUTO_INCREMENT PRIMARY KEY,
            format_file VARCHAR(20) NOT NULL,
            nama_file VARCHAR(255) NOT NULL,
            tahun_data VARCHAR(20) NOT NULL,
            dibuat_oleh VARCHAR(100) NOT NULL,
            waktu_generate TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB;
        """)

        # Seed Default Users
        cursor.execute("SELECT COUNT(*) FROM users;")
        count = cursor.fetchone()[0]
        if count == 0:
            cursor.executemany("""
            INSERT INTO users (username, password, nama_lengkap, role, jabatan, instansi) VALUES (%s, %s, %s, %s, %s, %s)
            """, [
                ('admin', 'admin123', 'M. Syahril', 'Admin / Petugas Kesra', 'Staf Analis Data Kesra', 'Bagian Kesejahteraan Rakyat (Kesra) Setda Kota Palembang'),
                ('pimpinan', 'pimpinan123', 'H. Sodikin, S.Ag., M.Si. / Drs. H. Ratu Dewa, M.Si.', 'Pimpinan / Pengambil Keputusan', 'Kepala Bagian Kesra / Wali Kota Palembang', 'Pemerintah Kota Palembang')
            ])

        # Seed Kecamatan
        cursor.execute("SELECT COUNT(*) FROM kecamatan;")
        count = cursor.fetchone()[0]
        if count == 0:
            from visualization_helper import KECAMATAN_COORDS
            kec_data = [(k, v[0], v[1], '18 Kecamatan Resmi Kota Palembang') for k, v in KECAMATAN_COORDS.items()]
            cursor.executemany("""
            INSERT INTO kecamatan (kecamatan, latitude, longitude, keterangan) VALUES (%s, %s, %s, %s)
            """, kec_data)

        # Seed Klaster Prioritas
        cursor.execute("SELECT COUNT(*) FROM klaster_prioritas;")
        count = cursor.fetchone()[0]
        if count == 0:
            cursor.executemany("""
            INSERT INTO klaster_prioritas (id_cluster, nama_cluster, status_prioritas, bobot_alokasi_persen, rekomendasi_intervensi, warna_map) VALUES (%s, %s, %s, %s, %s, %s)
            """, [
                (0, 'Cluster 0', 'Prioritas Tinggi (Darurat)', 60.0, 'Penyaluran Bansos Tunai Langsung Utama (PKH/BPNT), padat karya tunai, dan intervensi darurat kemiskinan ekstrem.', '#EF4444'),
                (1, 'Cluster 1', 'Prioritas Sedang (Waspada)', 30.0, 'Bantuan kuota bersyarat, pelatihan ketenagakerjaan, pembinaan UMKM, dan monitoring kerentanan berkala.', '#F59E0B'),
                (2, 'Cluster 2', 'Prioritas Rendah (Mandiri)', 10.0, 'Program pemberdayaan kemandirian ekonomi, fasilitasi kredit usaha rakyat (KUR), dan alokasi tanggap bencana darurat terbatas.', '#10B981')
            ])

        # Seed Data Indikator
        cursor.execute("SELECT COUNT(*) FROM data_indikator_bps;")
        count = cursor.fetchone()[0]
        if count == 0:
            csv_2025 = os.path.join(os.path.dirname(__file__), 'data', 'palembang_bps_data_2025_2026.csv')
            if os.path.exists(csv_2025):
                df_25 = pd.read_csv(csv_2025)
                for _, r in df_25.iterrows():
                    cursor.execute("""
                    INSERT IGNORE INTO data_indikator_bps 
                    (kecamatan, tahun_data, jumlah_penduduk_miskin, tingkat_pengangguran, pendapatan_rata_rata, kepadatan_penduduk, akses_fasilitas_publik, jumlah_kk_penerima_bansos, ipm)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        r['Kecamatan'], 2025, int(r['Jumlah_Penduduk_Miskin']), float(r['Tingkat_Pengangguran']),
                        int(r['Pendapatan_Rata_Rata']), float(r['Kepadatan_Penduduk']), float(r['Akses_Fasilitas_Publik']),
                        int(r['Jumlah_KK_Penerima_Bansos']), float(r['IPM'])
                    ))

    else:
        # SQLite Table Definitions
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id_user INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            nama_lengkap TEXT NOT NULL,
            role TEXT NOT NULL,
            jabatan TEXT,
            instansi TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS kecamatan (
            kecamatan TEXT PRIMARY KEY,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            luas_wilayah_km2 REAL,
            keterangan TEXT
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS data_indikator_bps (
            id_data INTEGER PRIMARY KEY AUTOINCREMENT,
            kecamatan TEXT NOT NULL,
            tahun_data INTEGER NOT NULL,
            jumlah_penduduk_miskin INTEGER NOT NULL,
            tingkat_pengangguran REAL NOT NULL,
            pendapatan_rata_rata INTEGER NOT NULL,
            kepadatan_penduduk REAL NOT NULL,
            akses_fasilitas_publik REAL NOT NULL,
            jumlah_kk_penerima_bansos INTEGER NOT NULL,
            ipm REAL NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (kecamatan) REFERENCES kecamatan(kecamatan),
            UNIQUE(kecamatan, tahun_data)
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS klaster_prioritas (
            id_cluster INTEGER PRIMARY KEY,
            nama_cluster TEXT NOT NULL,
            status_prioritas TEXT NOT NULL,
            bobot_alokasi_persen REAL NOT NULL,
            rekomendasi_intervensi TEXT NOT NULL,
            warna_map TEXT NOT NULL
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS hasil_clustering (
            id_hasil INTEGER PRIMARY KEY AUTOINCREMENT,
            kecamatan TEXT NOT NULL,
            tahun_data TEXT NOT NULL,
            id_cluster INTEGER NOT NULL,
            kategori_prioritas TEXT NOT NULL,
            skor_kerentanan REAL NOT NULL,
            jarak_ke_centroid_0 REAL,
            jarak_ke_centroid_1 REAL,
            jarak_ke_centroid_2 REAL,
            jarak_terdekat_dmin REAL,
            eksekusi_by TEXT,
            waktu_proses DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (kecamatan) REFERENCES kecamatan(kecamatan)
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS simulasi_alokasi_bansos (
            id_simulasi INTEGER PRIMARY KEY AUTOINCREMENT,
            kecamatan TEXT NOT NULL,
            tahun_data TEXT NOT NULL,
            total_pagu_anggaran_rp REAL NOT NULL,
            total_kuota_kk INTEGER NOT NULL,
            final_weight REAL NOT NULL,
            alokasi_anggaran_rp REAL NOT NULL,
            alokasi_kuota_kk INTEGER NOT NULL,
            nilai_bantuan_per_kk REAL NOT NULL,
            simulasi_by TEXT,
            waktu_simulasi DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS laporan_export (
            id_export INTEGER PRIMARY KEY AUTOINCREMENT,
            format_file TEXT NOT NULL,
            nama_file TEXT NOT NULL,
            tahun_data TEXT NOT NULL,
            dibuat_oleh TEXT NOT NULL,
            waktu_generate DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """)

        conn.commit()

        cursor.execute("SELECT COUNT(*) FROM users;")
        if cursor.fetchone()[0] == 0:
            cursor.executemany("""
            INSERT INTO users (username, password, nama_lengkap, role, jabatan, instansi) VALUES (?, ?, ?, ?, ?, ?)
            """, [
                ('admin', 'admin123', 'M. Syahril', 'Admin / Petugas Kesra', 'Staf Analis Data Kesra', 'Bagian Kesejahteraan Rakyat (Kesra) Setda Kota Palembang'),
                ('pimpinan', 'pimpinan123', 'H. Sodikin, S.Ag., M.Si. / Drs. H. Ratu Dewa, M.Si.', 'Pimpinan / Pengambil Keputusan', 'Kepala Bagian Kesra / Wali Kota Palembang', 'Pemerintah Kota Palembang')
            ])

        cursor.execute("SELECT COUNT(*) FROM kecamatan;")
        if cursor.fetchone()[0] == 0:
            from visualization_helper import KECAMATAN_COORDS
            kec_data = [(k, v[0], v[1], '18 Kecamatan Resmi Kota Palembang') for k, v in KECAMATAN_COORDS.items()]
            cursor.executemany("""
            INSERT INTO kecamatan (kecamatan, latitude, longitude, keterangan) VALUES (?, ?, ?, ?)
            """, kec_data)

        cursor.execute("SELECT COUNT(*) FROM klaster_prioritas;")
        if cursor.fetchone()[0] == 0:
            cursor.executemany("""
            INSERT INTO klaster_prioritas (id_cluster, nama_cluster, status_prioritas, bobot_alokasi_persen, rekomendasi_intervensi, warna_map) VALUES (?, ?, ?, ?, ?, ?)
            """, [
                (0, 'Cluster 0', 'Prioritas Tinggi (Darurat)', 60.0, 'Penyaluran Bansos Tunai Langsung Utama (PKH/BPNT), padat karya tunai, dan intervensi darurat kemiskinan ekstrem.', '#EF4444'),
                (1, 'Cluster 1', 'Prioritas Sedang (Waspada)', 30.0, 'Bantuan kuota bersyarat, pelatihan ketenagakerjaan, pembinaan UMKM, dan monitoring kerentanan berkala.', '#F59E0B'),
                (2, 'Cluster 2', 'Prioritas Rendah (Mandiri)', 10.0, 'Program pemberdayaan kemandirian ekonomi, fasilitasi kredit usaha rakyat (KUR), dan alokasi tanggap bencana darurat terbatas.', '#10B981')
            ])

        cursor.execute("SELECT COUNT(*) FROM data_indikator_bps;")
        if cursor.fetchone()[0] == 0:
            csv_2025 = os.path.join(os.path.dirname(__file__), 'data', 'palembang_bps_data_2025_2026.csv')
            if os.path.exists(csv_2025):
                df_25 = pd.read_csv(csv_2025)
                for _, r in df_25.iterrows():
                    cursor.execute("""
                    INSERT OR IGNORE INTO data_indikator_bps 
                    (kecamatan, tahun_data, jumlah_penduduk_miskin, tingkat_pengangguran, pendapatan_rata_rata, kepadatan_penduduk, akses_fasilitas_publik, jumlah_kk_penerima_bansos, ipm)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        r['Kecamatan'], 2025, int(r['Jumlah_Penduduk_Miskin']), float(r['Tingkat_Pengangguran']),
                        int(r['Pendapatan_Rata_Rata']), float(r['Kepadatan_Penduduk']), float(r['Akses_Fasilitas_Publik']),
                        int(r['Jumlah_KK_Penerima_Bansos']), float(r['IPM'])
                    ))
        conn.commit()

    conn.close()

def get_current_db_status():
    """Returns formatted database status string."""
    conn, mode = get_db_connection()
    conn.close()
    if mode == "MYSQL":
        return "MySQL (localhost:3306 / dss_bansos_palembang)"
    return "SQLite Database (bansos_palembang.db)"

def authenticate_user(username, password):
    """Verifies user login against database."""
    init_database()
    conn, mode = get_db_connection()
    cursor = conn.cursor()
    
    if mode == "MYSQL":
        cursor.execute("""
        SELECT id_user, username, nama_lengkap, role, jabatan, instansi FROM users 
        WHERE username = %s AND password = %s
        """, (username.strip(), password.strip()))
        row = cursor.fetchone()
        user = None
        if row:
            user = {
                'id_user': row[0],
                'username': row[1],
                'nama_lengkap': row[2],
                'role': row[3],
                'jabatan': row[4],
                'instansi': row[5]
            }
    else:
        cursor.execute("""
        SELECT id_user, username, nama_lengkap, role, jabatan, instansi FROM users 
        WHERE username = ? AND password = ?
        """, (username.strip(), password.strip()))
        row = cursor.fetchone()
        user = dict(row) if row else None

    conn.close()
    return user

def get_user_by_username(username):
    """Retrieves user info by username to restore persistent session across refreshes."""
    init_database()
    conn, mode = get_db_connection()
    cursor = conn.cursor()
    if mode == "MYSQL":
        cursor.execute("""
        SELECT id_user, username, nama_lengkap, role, jabatan, instansi FROM users 
        WHERE username = %s
        """, (username.strip(),))
        row = cursor.fetchone()
        user = None
        if row:
            user = {
                'id_user': row[0],
                'username': row[1],
                'nama_lengkap': row[2],
                'role': row[3],
                'jabatan': row[4],
                'instansi': row[5]
            }
    else:
        cursor.execute("""
        SELECT id_user, username, nama_lengkap, role, jabatan, instansi FROM users 
        WHERE username = ?
        """, (username.strip(),))
        row = cursor.fetchone()
        user = dict(row) if row else None
    conn.close()
    return user

def fetch_indicator_data_from_db(tahun: int = 2025):
    """Retrieves indicator dataframe from database with guaranteed numeric types."""
    init_database()
    conn, mode = get_db_connection()
    cursor = conn.cursor()
    
    cols = ['Kecamatan', 'Jumlah_Penduduk_Miskin', 'Tingkat_Pengangguran', 'Pendapatan_Rata_Rata',
            'Kepadatan_Penduduk', 'Akses_Fasilitas_Publik', 'Jumlah_KK_Penerima_Bansos', 'IPM']
    
    if mode == "MYSQL":
        cursor.execute("""
        SELECT kecamatan, jumlah_penduduk_miskin, tingkat_pengangguran, pendapatan_rata_rata,
               kepadatan_penduduk, akses_fasilitas_publik, jumlah_kk_penerima_bansos, ipm
        FROM data_indikator_bps
        ORDER BY kecamatan ASC
        """)
        rows = cursor.fetchall()
        df = pd.DataFrame(rows, columns=cols)
    else:
        df = pd.read_sql_query("""
        SELECT kecamatan as Kecamatan, jumlah_penduduk_miskin as Jumlah_Penduduk_Miskin, 
               tingkat_pengangguran as Tingkat_Pengangguran, pendapatan_rata_rata as Pendapatan_Rata_Rata,
               kepadatan_penduduk as Kepadatan_Penduduk, akses_fasilitas_publik as Akses_Fasilitas_Publik, 
               jumlah_kk_penerima_bansos as Jumlah_KK_Penerima_Bansos, ipm as IPM
        FROM data_indikator_bps
        ORDER BY kecamatan ASC
        """, conn)
    conn.close()

    # Guarantee clean numeric datatypes
    numeric_cols = [c for c in cols if c != 'Kecamatan']
    for c in numeric_cols:
        df[c] = pd.to_numeric(df[c], errors='coerce')

    return df

def save_clustering_results_to_db(df_result: pd.DataFrame, year_label: str, user_name: str):
    """Saves clustering results into database."""
    init_database()
    conn, mode = get_db_connection()
    cursor = conn.cursor()
    
    if mode == "MYSQL":
        cursor.execute("DELETE FROM hasil_clustering WHERE tahun_data = %s", (year_label,))
        for _, row in df_result.iterrows():
            cursor.execute("""
            INSERT INTO hasil_clustering (
                kecamatan, tahun_data, id_cluster, kategori_prioritas, skor_kerentanan,
                jarak_ke_centroid_0, jarak_ke_centroid_1, jarak_ke_centroid_2, jarak_terdekat_dmin, eksekusi_by
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                row['Kecamatan'], str(year_label), int(row['Cluster']), str(row['Kategori_Prioritas']),
                float(row['Skor_Kerentanan']),
                float(row.get('Jarak_Ke_Centroid_0', 0)),
                float(row.get('Jarak_Ke_Centroid_1', 0)),
                float(row.get('Jarak_Ke_Centroid_2', 0)),
                float(row.get('Jarak_Terdekat_d_min', 0)),
                user_name
            ))
    else:
        cursor.execute("DELETE FROM hasil_clustering WHERE tahun_data = ?", (year_label,))
        for _, row in df_result.iterrows():
            cursor.execute("""
            INSERT INTO hasil_clustering (
                kecamatan, tahun_data, id_cluster, kategori_prioritas, skor_kerentanan,
                jarak_ke_centroid_0, jarak_ke_centroid_1, jarak_ke_centroid_2, jarak_terdekat_dmin, eksekusi_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row['Kecamatan'], str(year_label), int(row['Cluster']), str(row['Kategori_Prioritas']),
                float(row['Skor_Kerentanan']),
                float(row.get('Jarak_Ke_Centroid_0', 0)),
                float(row.get('Jarak_Ke_Centroid_1', 0)),
                float(row.get('Jarak_Ke_Centroid_2', 0)),
                float(row.get('Jarak_Terdekat_d_min', 0)),
                user_name
            ))
        conn.commit()
    conn.close()

def save_simulation_results_to_db(df_sim: pd.DataFrame, year_label: str, total_budget: float, total_quota: int, user_name: str):
    """Saves simulation records into database."""
    init_database()
    conn, mode = get_db_connection()
    cursor = conn.cursor()
    if mode == "MYSQL":
        for _, row in df_sim.iterrows():
            cursor.execute("""
            INSERT INTO simulasi_alokasi_bansos (
                kecamatan, tahun_data, total_pagu_anggaran_rp, total_kuota_kk, final_weight,
                alokasi_anggaran_rp, alokasi_kuota_kk, nilai_bantuan_per_kk, simulasi_by
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                row['Kecamatan'], str(year_label), float(total_budget), int(total_quota),
                float(row.get('Final_Weight', 0)), float(row.get('Alokasi_Anggaran_Rp', 0)),
                int(row.get('Alokasi_Kuota_KK', 0)), float(row.get('Nilai_Bantuan_Per_KK', 0)),
                user_name
            ))
    else:
        for _, row in df_sim.iterrows():
            cursor.execute("""
            INSERT INTO simulasi_alokasi_bansos (
                kecamatan, tahun_data, total_pagu_anggaran_rp, total_kuota_kk, final_weight,
                alokasi_anggaran_rp, alokasi_kuota_kk, nilai_bantuan_per_kk, simulasi_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row['Kecamatan'], str(year_label), float(total_budget), int(total_quota),
                float(row.get('Final_Weight', 0)), float(row.get('Alokasi_Anggaran_Rp', 0)),
                int(row.get('Alokasi_Kuota_KK', 0)), float(row.get('Nilai_Bantuan_Per_KK', 0)),
                user_name
            ))
        conn.commit()
    conn.close()

def log_export_to_db(format_file: str, file_name: str, year_label: str, user_name: str):
    """Logs report exports into database."""
    init_database()
    conn, mode = get_db_connection()
    cursor = conn.cursor()
    if mode == "MYSQL":
        cursor.execute("""
        INSERT INTO laporan_export (format_file, nama_file, tahun_data, dibuat_oleh)
        VALUES (%s, %s, %s, %s)
        """, (format_file, file_name, year_label, user_name))
    else:
        cursor.execute("""
        INSERT INTO laporan_export (format_file, nama_file, tahun_data, dibuat_oleh)
        VALUES (?, ?, ?, ?)
        """, (format_file, file_name, year_label, user_name))
        conn.commit()
    conn.close()
