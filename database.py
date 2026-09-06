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

# Built-in Default Users (Guarantees login works on ANY computer even without MySQL/SQLite setup)
DEFAULT_USERS = {
    'admin': {
        'id_user': 1,
        'username': 'admin',
        'password': 'admin123',
        'nama_lengkap': 'M. Syahril',
        'role': 'Admin / Petugas Kesra',
        'jabatan': 'Staf Analis Data Kesra',
        'instansi': 'Bagian Kesejahteraan Rakyat (Kesra) Setda Kota Palembang'
    },
    'pimpinan': {
        'id_user': 2,
        'username': 'pimpinan',
        'password': 'pimpinan123',
        'nama_lengkap': 'H. Sodikin, S.Ag., M.Si. / Drs. H. Ratu Dewa, M.Si.',
        'role': 'Pimpinan / Pengambil Keputusan',
        'jabatan': 'Kepala Bagian Kesra / Wali Kota Palembang',
        'instansi': 'Pemerintah Kota Palembang'
    }
}

DB_MODE = "SQLITE"

def test_mysql_connection():
    """Checks if local MySQL server is accessible with short timeout."""
    if not HAS_PYMYSQL:
        return False
    try:
        conn = pymysql.connect(
            host=MYSQL_CONFIG['host'],
            port=MYSQL_CONFIG['port'],
            user=MYSQL_CONFIG['user'],
            password=MYSQL_CONFIG['password'],
            connect_timeout=1
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_CONFIG['database']} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False

def get_db_connection():
    """Returns MySQL or SQLite connection dynamically."""
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
    """Initializes tables and seeds initial data in both MySQL and SQLite."""
    try:
        conn, mode = get_db_connection()
        cursor = conn.cursor()

        if mode == "MYSQL":
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

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS kecamatan (
                kecamatan VARCHAR(50) PRIMARY KEY,
                latitude DOUBLE NOT NULL,
                longitude DOUBLE NOT NULL,
                luas_wilayah_km2 DOUBLE,
                keterangan TEXT
            ) ENGINE=InnoDB;
            """)

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

            cursor.execute("SELECT COUNT(*) FROM users;")
            if cursor.fetchone()[0] == 0:
                cursor.executemany("""
                INSERT INTO users (username, password, nama_lengkap, role, jabatan, instansi) VALUES (%s, %s, %s, %s, %s, %s)
                """, [
                    ('admin', 'admin123', 'M. Syahril', 'Admin / Petugas Kesra', 'Staf Analis Data Kesra', 'Bagian Kesejahteraan Rakyat (Kesra) Setda Kota Palembang'),
                    ('pimpinan', 'pimpinan123', 'H. Sodikin, S.Ag., M.Si. / Drs. H. Ratu Dewa, M.Si.', 'Pimpinan / Pengambil Keputusan', 'Kepala Bagian Kesra / Wali Kota Palembang', 'Pemerintah Kota Palembang')
                ])

            cursor.execute("SELECT COUNT(*) FROM kecamatan;")
            if cursor.fetchone()[0] == 0:
                from visualization_helper import KECAMATAN_COORDS
                kec_data = [(k, v[0], v[1], '18 Kecamatan Resmi Kota Palembang') for k, v in KECAMATAN_COORDS.items()]
                cursor.executemany("INSERT INTO kecamatan (kecamatan, latitude, longitude, keterangan) VALUES (%s, %s, %s, %s)", kec_data)

            cursor.execute("SELECT COUNT(*) FROM data_indikator_bps;")
            if cursor.fetchone()[0] == 0:
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
            # SQLite Self-Healing Setup
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

            # Ensure jabatan column exists in SQLite users table
            try:
                cursor.execute("SELECT jabatan FROM users LIMIT 1;")
            except Exception:
                try:
                    cursor.execute("ALTER TABLE users ADD COLUMN jabatan TEXT;")
                    conn.commit()
                except Exception:
                    pass

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
                INSERT OR REPLACE INTO users (username, password, nama_lengkap, role, jabatan, instansi) VALUES (?, ?, ?, ?, ?, ?)
                """, [
                    ('admin', 'admin123', 'M. Syahril', 'Admin / Petugas Kesra', 'Staf Analis Data Kesra', 'Bagian Kesejahteraan Rakyat (Kesra) Setda Kota Palembang'),
                    ('pimpinan', 'pimpinan123', 'H. Sodikin, S.Ag., M.Si. / Drs. H. Ratu Dewa, M.Si.', 'Pimpinan / Pengambil Keputusan', 'Kepala Bagian Kesra / Wali Kota Palembang', 'Pemerintah Kota Palembang')
                ])

            cursor.execute("SELECT COUNT(*) FROM kecamatan;")
            if cursor.fetchone()[0] == 0:
                from visualization_helper import KECAMATAN_COORDS
                kec_data = [(k, v[0], v[1], '18 Kecamatan Resmi Kota Palembang') for k, v in KECAMATAN_COORDS.items()]
                cursor.executemany("INSERT OR IGNORE INTO kecamatan (kecamatan, latitude, longitude, keterangan) VALUES (?, ?, ?, ?)", kec_data)

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
    except Exception:
        pass

def get_current_db_status():
    """Returns formatted database status string."""
    try:
        conn, mode = get_db_connection()
        conn.close()
        if mode == "MYSQL":
            return "MySQL (localhost:3306 / dss_bansos_palembang)"
        return "SQLite Database (bansos_palembang.db)"
    except Exception:
        return "Local Storage (Standby Mode)"

def authenticate_user(username, password):
    """Verifies user login against database with foolproof fallback."""
    u_clean = username.strip() if username else ""
    p_clean = password.strip() if password else ""

    # 1. Check in database
    try:
        init_database()
        conn, mode = get_db_connection()
        cursor = conn.cursor()
        
        if mode == "MYSQL":
            cursor.execute("""
            SELECT id_user, username, nama_lengkap, role, jabatan, instansi FROM users 
            WHERE username = %s AND password = %s
            """, (u_clean, p_clean))
            row = cursor.fetchone()
            if row:
                conn.close()
                return {
                    'id_user': row[0],
                    'username': row[1],
                    'nama_lengkap': row[2],
                    'role': row[3],
                    'jabatan': row[4] or '',
                    'instansi': row[5] or ''
                }
        else:
            cursor.execute("""
            SELECT id_user, username, nama_lengkap, role, password FROM users 
            WHERE username = ?
            """, (u_clean,))
            row = cursor.fetchone()
            if row:
                r_dict = dict(row)
                db_pass = r_dict.get('Password') or r_dict.get('password')
                if db_pass == p_clean:
                    conn.close()
                    return {
                        'id_user': r_dict.get('Id_User') or r_dict.get('id_user') or 1,
                        'username': r_dict.get('Username') or r_dict.get('username') or u_clean,
                        'nama_lengkap': r_dict.get('Nama_Lengkap') or r_dict.get('nama_lengkap') or u_clean,
                        'role': r_dict.get('Role') or r_dict.get('role') or 'Admin / Petugas Kesra',
                        'jabatan': r_dict.get('Jabatan') or r_dict.get('jabatan') or '',
                        'instansi': r_dict.get('Instansi') or r_dict.get('instansi') or 'Pemerintah Kota Palembang'
                    }
        conn.close()
    except Exception:
        pass

    # 2. Built-in Fallback for 100% Guaranteed Login on ANY machine
    if u_clean in DEFAULT_USERS:
        def_u = DEFAULT_USERS[u_clean]
        if def_u['password'] == p_clean:
            return def_u.copy()

    return None

def get_user_by_username(username):
    """Retrieves user info by username to restore persistent session across refreshes."""
    u_clean = username.strip() if username else ""
    try:
        init_database()
        conn, mode = get_db_connection()
        cursor = conn.cursor()
        if mode == "MYSQL":
            cursor.execute("""
            SELECT id_user, username, nama_lengkap, role, jabatan, instansi FROM users 
            WHERE username = %s
            """, (u_clean,))
            row = cursor.fetchone()
            if row:
                conn.close()
                return {
                    'id_user': row[0],
                    'username': row[1],
                    'nama_lengkap': row[2],
                    'role': row[3],
                    'jabatan': row[4] or '',
                    'instansi': row[5] or ''
                }
        else:
            cursor.execute("SELECT * FROM users WHERE username = ? OR Username = ?", (u_clean, u_clean))
            row = cursor.fetchone()
            if row:
                r_dict = dict(row)
                conn.close()
                return {
                    'id_user': r_dict.get('Id_User') or r_dict.get('id_user') or 1,
                    'username': r_dict.get('Username') or r_dict.get('username') or u_clean,
                    'nama_lengkap': r_dict.get('Nama_Lengkap') or r_dict.get('nama_lengkap') or u_clean,
                    'role': r_dict.get('Role') or r_dict.get('role') or 'Admin / Petugas Kesra',
                    'jabatan': r_dict.get('Jabatan') or r_dict.get('jabatan') or '',
                    'instansi': r_dict.get('Instansi') or r_dict.get('instansi') or 'Pemerintah Kota Palembang'
                }
        conn.close()
    except Exception:
        pass

    if u_clean in DEFAULT_USERS:
        return DEFAULT_USERS[u_clean].copy()

    return None

def fetch_indicator_data_from_db(tahun: int = 2025):
    """Retrieves indicator dataframe from database or fallback CSV with guaranteed numeric types."""
    cols = ['Kecamatan', 'Jumlah_Penduduk_Miskin', 'Tingkat_Pengangguran', 'Pendapatan_Rata_Rata',
            'Kepadatan_Penduduk', 'Akses_Fasilitas_Publik', 'Jumlah_KK_Penerima_Bansos', 'IPM']
    
    df = None
    try:
        init_database()
        conn, mode = get_db_connection()
        cursor = conn.cursor()
        
        if mode == "MYSQL":
            cursor.execute("""
            SELECT kecamatan, jumlah_penduduk_miskin, tingkat_pengangguran, pendapatan_rata_rata,
                   kepadatan_penduduk, akses_fasilitas_publik, jumlah_kk_penerima_bansos, ipm
            FROM data_indikator_bps
            WHERE tahun_data = %s
            ORDER BY kecamatan ASC
            """, (tahun,))
            rows = cursor.fetchall()
            if rows and len(rows) > 0:
                df = pd.DataFrame(rows, columns=cols)
        else:
            cursor.execute("""
            SELECT kecamatan, jumlah_penduduk_miskin, tingkat_pengangguran, pendapatan_rata_rata,
                   kepadatan_penduduk, akses_fasilitas_publik, jumlah_kk_penerima_bansos, ipm
            FROM data_indikator_bps
            WHERE tahun_data = ? OR tahun_data = ?
            ORDER BY kecamatan ASC
            """, (tahun, str(tahun)))
            rows = cursor.fetchall()
            if rows and len(rows) > 0:
                clean_rows = []
                for r in rows:
                    clean_rows.append([r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7]])
                df = pd.DataFrame(clean_rows, columns=cols)
        conn.close()
    except Exception:
        df = None

    # Guaranteed Fallback to CSV file if DB returned empty or failed
    if df is None or len(df) == 0:
        csv_file = os.path.join(os.path.dirname(__file__), 'data', 'palembang_bps_data_2025_2026.csv')
        if not os.path.exists(csv_file):
            csv_file = os.path.join(os.path.dirname(__file__), 'data', 'palembang_bps_data.csv')
        if os.path.exists(csv_file):
            df = pd.read_csv(csv_file)

    # Convert all indicator columns to numeric floats
    if df is not None:
        numeric_cols = [c for c in cols if c != 'Kecamatan']
        for c in numeric_cols:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0.0)

    return df

def save_clustering_results_to_db(df_result: pd.DataFrame, year_label: str, user_name: str):
    """Saves clustering results into database safely."""
    try:
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
    except Exception:
        pass

def save_simulation_results_to_db(df_sim: pd.DataFrame, year_label: str, total_budget: float, total_quota: int, user_name: str):
    """Saves simulation records into database safely."""
    try:
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
    except Exception:
        pass

def log_export_to_db(format_file: str, file_name: str, year_label: str, user_name: str):
    """Logs report exports into database safely."""
    try:
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
    except Exception:
        pass
