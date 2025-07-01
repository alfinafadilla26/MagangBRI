# File: database.py (VERSI FINAL dengan Implementasi Lengkap)
import mysql.connector
from mysql.connector import Error
import configparser
import os
import bcrypt
from datetime import datetime
import sys
import logging

# --- Fungsi Konfigurasi dan Koneksi ---

def get_base_path():
    """Mendapatkan path dasar aplikasi, baik saat dijalankan sebagai script atau .exe."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        # Diasumsikan database.py ada di root folder proyek
        return os.path.dirname(os.path.abspath(__file__))

# Setup logging
log_file_path = os.path.join(get_base_path(), 'debug_log.txt')
logging.basicConfig(filename=log_file_path, level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filemode='w')

def get_config_value(section, key, fallback=None):
    """Membaca nilai dari file config.ini dengan nilai fallback."""
    config = configparser.ConfigParser()
    config_file_path = os.path.join(get_base_path(), 'config.ini')
    
    if not os.path.exists(config_file_path):
        error_msg = f"File 'config.ini' tidak ditemukan di path: {config_file_path}"
        logging.error(error_msg)
        raise FileNotFoundError(error_msg)
        
    config.read(config_file_path)
    return config.get(section, key, fallback=fallback)

def create_connection():
    """Membuat koneksi ke database MySQL."""
    conn = None
    try:
        db_config = {
            'host': get_config_value('Database', 'Host'),
            'user': get_config_value('Database', 'User'),
            'password': get_config_value('Database', 'Password'),
            'database': get_config_value('Database', 'DatabaseName'),
            'port': int(get_config_value('Database', 'Port'))
        }

        # Membuat SSL menjadi opsional. Hanya digunakan jika ada di config.ini.
        ssl_ca_value = get_config_value('Database', 'SSL_CA', fallback=None)
        if ssl_ca_value:
            ssl_ca_path = os.path.join(get_base_path(), ssl_ca_value)
            if not os.path.exists(ssl_ca_path):
                error_msg = f"File sertifikat '{ssl_ca_value}' tidak ditemukan di: {ssl_ca_path}."
                logging.error(error_msg)
                raise FileNotFoundError(error_msg)
            db_config['ssl_ca'] = ssl_ca_path
            db_config['ssl_verify_cert'] = True

        conn = mysql.connector.connect(**db_config)
    except Error as e:
        logging.error(f"Error connecting to MySQL database: {e}")
    except (FileNotFoundError, KeyError, configparser.NoSectionError, configparser.NoOptionError) as e:
        logging.error(f"Error pada konfigurasi database: {e}")
    return conn

# --- Fungsi-fungsi Inisialisasi dan CRUD ---

def create_tables():
    """Membuat semua tabel jika belum ada."""
    conn = None
    try:
        conn = create_connection()
        if not (conn and conn.is_connected()): return
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INT AUTO_INCREMENT PRIMARY KEY, nama VARCHAR(255) NOT NULL, personal_number VARCHAR(255) UNIQUE NOT NULL, password TEXT NOT NULL, role VARCHAR(50) NOT NULL DEFAULT 'superadmin') ENGINE=InnoDB;")
        cursor.execute("CREATE TABLE IF NOT EXISTS categories (category_id INT AUTO_INCREMENT PRIMARY KEY, category_name VARCHAR(255) UNIQUE NOT NULL) ENGINE=InnoDB;")
        cursor.execute("CREATE TABLE IF NOT EXISTS items (item_id INT AUTO_INCREMENT PRIMARY KEY, item_name VARCHAR(255) NOT NULL, description TEXT, stock INT NOT NULL DEFAULT 0, date_added DATETIME NOT NULL, category_id INT, image_url VARCHAR(255), FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE SET NULL) ENGINE=InnoDB;")
        # Menambahkan kolom item_name_snapshot untuk menyimpan nama barang saat transaksi
        cursor.execute("CREATE TABLE IF NOT EXISTS history_log (log_id INT AUTO_INCREMENT PRIMARY KEY, item_id INT, item_name_snapshot VARCHAR(255), taker_name VARCHAR(255) NOT NULL, quantity_taken INT NOT NULL, date_taken DATETIME NOT NULL, transaction_type VARCHAR(50) NOT NULL DEFAULT 'keluar', FOREIGN KEY (item_id) REFERENCES items(item_id) ON DELETE SET NULL) ENGINE=InnoDB;")
        logging.info("Pengecekan dan pembuatan tabel selesai.")
        conn.commit()
    except Error as e:
        logging.error(f"Error saat membuat tabel: {e}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def setup_default_admin():
    """Membuat user admin default jika belum ada user sama sekali."""
    conn = None
    try:
        conn = create_connection()
        if conn and conn.is_connected():
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users")
            if cursor.fetchone()[0] == 0:
                pn = get_config_value('Admin', 'DefaultPersonalNumber')
                pw = get_config_value('Admin', 'DefaultPassword')
                hashed_pw = bcrypt.hashpw(pw.encode('utf-8'), bcrypt.gensalt())
                query = "INSERT INTO users (nama, personal_number, password, role) VALUES (%s, %s, %s, %s)"
                cursor.execute(query, ('Default Admin', pn, hashed_pw, 'superadmin'))
                conn.commit()
                logging.info("Default admin created successfully.")
    except (Error, KeyError) as e:
        logging.error(f"Error setting up default admin: {e}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def verify_admin(personal_number, password):
    """Memvalidasi kredensial admin dengan password yang di-hash."""
    conn = None
    try:
        conn = create_connection()
        if not (conn and conn.is_connected()): 
            logging.error("validate_admin: Gagal terhubung ke DB.")
            return False
        
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT password FROM users WHERE personal_number = %s", (personal_number,))
        result = cursor.fetchone()
        
        if result and 'password' in result and result['password']:
            stored_password_hash = result['password'].encode('utf-8')
            if bcrypt.checkpw(password.encode('utf-8'), stored_password_hash):
                logging.info(f"Login berhasil untuk user: {personal_number}")
                return True
            else:
                logging.warning(f"Password salah untuk user: {personal_number}")
        else:
            logging.warning(f"User tidak ditemukan: {personal_number}")
    except Error as e:
        logging.error(f"Error dalam validate_admin: {e}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
    return False

# --- Fungsi untuk Kategori ---
def add_category(name):
    conn = None
    try:
        conn = create_connection()
        if not (conn and conn.is_connected()): return
        cursor = conn.cursor()
        cursor.execute("INSERT INTO categories (category_name) VALUES (%s)", (name,))
        conn.commit()
    except Error as e:
        logging.error(f"Error adding category: {e}")
        raise e
    finally:
        if conn and conn.is_connected(): cursor.close(); conn.close()

def get_all_categories():
    conn = None
    try:
        conn = create_connection()
        if not (conn and conn.is_connected()): return []
        cursor = conn.cursor()
        cursor.execute("SELECT category_id, category_name FROM categories ORDER BY category_name")
        return cursor.fetchall()
    except Error as e:
        logging.error(f"Error getting categories: {e}")
        return []
    finally:
        if conn and conn.is_connected(): cursor.close(); conn.close()

def update_category(cat_id, new_name):
    conn = None
    try:
        conn = create_connection()
        if not (conn and conn.is_connected()): return
        cursor = conn.cursor()
        cursor.execute("UPDATE categories SET category_name = %s WHERE category_id = %s", (new_name, cat_id))
        conn.commit()
    except Error as e:
        logging.error(f"Error updating category: {e}")
        raise e
    finally:
        if conn and conn.is_connected(): cursor.close(); conn.close()

def delete_category(cat_id):
    conn = None
    try:
        conn = create_connection()
        if not (conn and conn.is_connected()): return
        cursor = conn.cursor()
        cursor.execute("UPDATE items SET category_id = NULL WHERE category_id = %s", (cat_id,))
        cursor.execute("DELETE FROM categories WHERE category_id = %s", (cat_id,))
        conn.commit()
    except Error as e:
        logging.error(f"Error deleting category: {e}")
        raise e
    finally:
        if conn and conn.is_connected(): cursor.close(); conn.close()

# --- Fungsi untuk Barang (Items) ---

def add_item(name, desc, stock, cat_id, image_url=None):
    """Menambah item baru dan mencatatnya sebagai 'masuk' di riwayat."""
    conn = None
    try:
        conn = create_connection()
        if not (conn and conn.is_connected()): return
        cursor = conn.cursor()
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        query = "INSERT INTO items (item_name, description, stock, date_added, category_id, image_url) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (name, desc, stock, date, cat_id, image_url))
        new_item_id = cursor.lastrowid
        record_transaction(new_item_id, name, stock, "Admin", "masuk", conn)
        conn.commit()
    except Error as e:
        if conn: conn.rollback()
        logging.error(f"Error adding item: {e}")
        raise e
    finally:
        if conn and conn.is_connected(): cursor.close(); conn.close()

def update_item(item_id, name, desc, stock, cat_id, image_url=None):
    conn = None
    try:
        conn = create_connection()
        if not (conn and conn.is_connected()): return
        cursor = conn.cursor()
        query = "UPDATE items SET item_name = %s, description = %s, stock = %s, category_id = %s, image_url = %s WHERE item_id = %s"
        cursor.execute(query, (name, desc, stock, cat_id, image_url, item_id))
        conn.commit()
    except Error as e:
        logging.error(f"Error updating item: {e}")
        raise e
    finally:
        if conn and conn.is_connected(): cursor.close(); conn.close()

def delete_item(item_id):
    """Menghapus item dan mencatatnya sebagai 'dihapus' di riwayat."""
    conn = None
    try:
        conn = create_connection()
        if not (conn and conn.is_connected()): return
        cursor = conn.cursor()
        cursor.execute("SELECT item_name, stock FROM items WHERE item_id = %s", (item_id,))
        item_details = cursor.fetchone()
        if item_details:
            item_name, stock = item_details
            record_transaction(item_id, item_name, stock, "Admin", "dihapus", conn)
        cursor.execute("DELETE FROM items WHERE item_id = %s", (item_id,))
        conn.commit()
    except Error as e:
        if conn: conn.rollback()
        logging.error(f"Error deleting item: {e}")
        raise e
    finally:
        if conn and conn.is_connected(): cursor.close(); conn.close()

def take_item(item_id, quantity, taker_name):
    """Mengambil item, mengurangi stok, dan mencatatnya sebagai 'keluar'."""
    success = False
    conn = None
    try:
        conn = create_connection()
        if not (conn and conn.is_connected()): return False
        cursor = conn.cursor()
        cursor.execute("SELECT item_name, stock FROM items WHERE item_id = %s FOR UPDATE", (item_id,))
        result = cursor.fetchone()
        if result:
            item_name, current_stock = result
            if current_stock >= quantity:
                new_stock = current_stock - quantity
                cursor.execute("UPDATE items SET stock = %s WHERE item_id = %s", (new_stock, item_id))
                record_transaction(item_id, item_name, quantity, taker_name, "keluar", conn)
                conn.commit()
                success = True
            else:
                conn.rollback()
    except Error as e:
        if conn: conn.rollback()
        logging.error(f"Error in take_item: {e}")
    finally:
        if conn and conn.is_connected(): cursor.close(); conn.close()
    return success
    
def adjust_stock(item_id, quantity, transaction_type):
    """
    Menambah atau mengurangi stok item dan mencatat transaksi.
    transaction_type bisa 'masuk' atau 'keluar'.
    """
    conn = None
    try:
        conn = create_connection()
        if not (conn and conn.is_connected()):
            raise Exception("Koneksi ke database gagal.")
        
        cursor = conn.cursor()
        cursor.execute("SELECT item_name, stock FROM items WHERE item_id = %s FOR UPDATE", (item_id,))
        result = cursor.fetchone()
        
        if not result:
            raise ValueError("Item tidak ditemukan.")
            
        item_name, current_stock = result
        
        if transaction_type == 'masuk':
            new_stock = current_stock + quantity
        elif transaction_type == 'keluar':
            if current_stock < quantity:
                raise ValueError(f"Stok tidak cukup. Stok saat ini: {current_stock}")
            new_stock = current_stock - quantity
        else:
            raise ValueError("Tipe transaksi tidak valid.")
            
        cursor.execute("UPDATE items SET stock = %s WHERE item_id = %s", (new_stock, item_id))
        record_transaction(item_id, item_name, quantity, "Admin", transaction_type, conn)
        conn.commit()
        
    except Exception as e:
        if conn:
            conn.rollback()
        logging.error(f"Error in adjust_stock: {e}")
        raise e
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# --- Fungsi untuk Riwayat (History) ---

def record_transaction(item_id, item_name, quantity, user_name, transaction_type, existing_conn=None):
    """Mencatat setiap transaksi barang. Bisa menggunakan koneksi yang sudah ada."""
    conn = None
    try:
        conn = existing_conn or create_connection()
        if not (conn and conn.is_connected()): raise Exception("Koneksi DB Gagal")
        cursor = conn.cursor()
        date_taken = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        query = "INSERT INTO history_log (item_id, item_name_snapshot, quantity_taken, taker_name, date_taken, transaction_type) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (item_id, item_name, quantity, user_name, date_taken, transaction_type))
        if not existing_conn: conn.commit()
    except Error as e:
        if conn and not existing_conn: conn.rollback()
        logging.error(f"Error recording transaction: {e}")
        raise e
    finally:
        if conn and not existing_conn and conn.is_connected():
            cursor.close()
            conn.close()

def get_history():
    """Mengambil seluruh data riwayat dari database, termasuk nama snapshot."""
    conn = None
    try:
        conn = create_connection()
        if not (conn and conn.is_connected()): return []
        cursor = conn.cursor()
        query = "SELECT date_taken, item_name_snapshot, quantity_taken, taker_name, transaction_type FROM history_log ORDER BY log_id DESC"
        cursor.execute(query)
        return cursor.fetchall()
    except Error as e:
        logging.error(f"Error getting history: {e}")
        return []
    finally:
        if conn and conn.is_connected(): cursor.close(); conn.close()

def get_history_by_date_range(start_date, end_date):
    """Mengambil data riwayat berdasarkan rentang tanggal."""
    conn = None
    try:
        end_date_inclusive = f"{end_date} 23:59:59"
        conn = create_connection()
        if not (conn and conn.is_connected()): return []
        cursor = conn.cursor()
        query = "SELECT date_taken, item_name_snapshot, quantity_taken, taker_name, transaction_type FROM history_log WHERE date_taken BETWEEN %s AND %s ORDER BY log_id DESC"
        cursor.execute(query, (start_date, end_date_inclusive))
        return cursor.fetchall()
    except Error as e:
        logging.error(f"Error getting history by date range: {e}")
        return []
    finally:
        if conn and conn.is_connected(): cursor.close(); conn.close()

# --- Fungsi Getter Lainnya ---

def get_item_by_id(item_id):
    conn = None
    try:
        conn = create_connection()
        if not (conn and conn.is_connected()): return None
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM items WHERE item_id = %s", (item_id,))
        return cursor.fetchone()
    except Error as e:
        logging.error(f"Error getting item by ID: {e}")
        return None
    finally:
        if conn and conn.is_connected(): cursor.close(); conn.close()

def find_item_by_name(item_name):
    """Mencari item berdasarkan nama yang sama persis (case-insensitive)."""
    conn = None
    try:
        conn = create_connection()
        if not (conn and conn.is_connected()): return None
        cursor = conn.cursor(dictionary=True)
        query = "SELECT item_id, stock FROM items WHERE LOWER(item_name) = LOWER(%s)"
        cursor.execute(query, (item_name,))
        return cursor.fetchone()
    except Error as e:
        logging.error(f"Error finding item by name: {e}")
        return None
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def search_items(category_id=None, keyword=""):
    conn = None
    try:
        conn = create_connection()
        if not (conn and conn.is_connected()): return []
        cursor = conn.cursor()
        query = "SELECT item_id, item_name, category_id, stock, description, date_added, image_url FROM items WHERE 1=1"
        params = []
        if category_id is not None:
            query += " AND category_id = %s"
            params.append(category_id)
        if keyword and keyword.strip():
            query += " AND item_name LIKE %s"
            params.append(f"%{keyword.strip()}%")
        query += " ORDER BY item_name ASC"
        cursor.execute(query, tuple(params))
        return cursor.fetchall()
    except Error as err:
        logging.error(f"Error saat mencari item: {err}")
        return []
    finally:
        if conn and conn.is_connected(): cursor.close(); conn.close()

def get_items_by_category(category_id):
    conn = None
    try:
        conn = create_connection()
        if not (conn and conn.is_connected()): return []
        cursor = conn.cursor()
        # Mengembalikan 8 kolom agar cocok dengan `management_frame.py`
        query = "SELECT i.item_id, i.item_name, c.category_name, i.stock, i.description, i.date_added, i.image_url, i.category_id FROM items i LEFT JOIN categories c ON i.category_id = c.category_id WHERE i.category_id = %s ORDER BY i.item_name"
        cursor.execute(query, (category_id,))
        return cursor.fetchall()
    except Error as e:
        logging.error(f"Error in get_items_by_category: {e}")
        return []
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def get_category_name_by_item_id(item_id):
    conn = None
    try:
        conn = create_connection()
        if not (conn and conn.is_connected()): return "N/A"
        cursor = conn.cursor()
        query = "SELECT c.category_name FROM categories c JOIN items i ON c.category_id = i.category_id WHERE i.item_id = %s"
        cursor.execute(query, (item_id,))
        result = cursor.fetchone()
        return result[0] if result else "Tanpa Kategori"
    except Error as e:
        logging.error(f"Error getting category name by item ID: {e}")
        return "Error"
    finally:
        if conn and conn.is_connected(): cursor.close(); conn.close()

# --- FUNGSI BARU UNTUK NOTIFIKASI ---
def get_low_stock_items(threshold=5):
    """Mengambil semua item yang stoknya di bawah atau sama dengan threshold."""
    conn = None
    try:
        conn = create_connection()
        if not (conn and conn.is_connected()): return []
        cursor = conn.cursor(dictionary=True)
        query = "SELECT item_id, item_name, stock FROM items WHERE stock <= %s ORDER BY stock ASC"
        cursor.execute(query, (threshold,))
        return cursor.fetchall()
    except Error as e:
        logging.error(f"Error getting low stock items: {e}")
        return []
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# --- Main Execution Block ---
if __name__ == '__main__':
    logging.info("Menjalankan database.py secara manual untuk inisialisasi.")
    print("Mempersiapkan database...")
    create_tables()
    print("Mempersiapkan admin default...")
    setup_default_admin()
    print("Proses selesai.")

