import sqlite3
from pathlib import Path
import os

DB_PATH = Path(__file__).resolve().parent / "crypto_manager.db"
SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory=sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    # 1. Resetăm baza de date pentru a aplica schema nouă (Clean Slate)
    if DB_PATH.exists():
        try:
            os.remove(DB_PATH)
            print("Baza de date veche a fost ștearsă pentru reinițializare.")
        except PermissionError:
            print("Închide DB Browser sau aplicația înainte de a rula init_db!")
            return

    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(f"Schema file not found at {SCHEMA_PATH}")

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # 2. Executăm scriptul SQL pentru crearea tabelelor
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            sql_script = f.read()
        conn.executescript(sql_script)
        conn.commit()
        print("Tabelele au fost create conform schemei.")

        # 3. POPULARE ALGORITMI (Respectând coloanele tale: id, name, type, key_size, mode)
        # Am pus ID-urile manual ca să fim siguri că se pupă cu ce trimiți din GUI
        cursor.execute("""
            INSERT INTO Algorithms (id, name, type, key_size, mode) 
            VALUES (1, 'AES-256', 'Symmetric', 256, 'CBC')
        """)
        cursor.execute("""
            INSERT INTO Algorithms (id, name, type, key_size, mode) 
            VALUES (2, 'RSA-2048', 'Asymmetric', 2048, 'OAEP')
        """)

        # 4. POPULARE FRAMEWORKS (Cerința cu varianta 2 și 3)
        cursor.execute("INSERT INTO Frameworks (id, name, version) VALUES (1, 'OpenSSL (Subprocess)', '3.x')")
        cursor.execute("INSERT INTO Frameworks (id, name, version) VALUES (2, 'Cryptography (Wrapper)', '42.0')")

        conn.commit()
        print("Algoritmii și Framework-urile au fost inserate cu succes.")

        # Vizualizare tabele pentru confirmare
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("\nTabele identificate în DB:")
        for table in tables:
            print(f" - {table['name']}")

    except Exception as e:
        print(f"Eroare critică la inițializare: {e}")
        conn.rollback()
    finally:
        conn.close()

def execute_query(query, params=()):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
    finally:
        conn.close()

def fetch_query(query, params=()):

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()
    finally:
        conn.close()

if __name__=="__main__":
    init_db()