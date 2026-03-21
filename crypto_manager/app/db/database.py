import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "crypto_manager.db"
SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory=sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(f"Schema file not found at {SCHEMA_PATH}")
    conn=get_connection()

    with open(SCHEMA_PATH,"r", encoding="utf-8") as f:
        sql_script=f.read()
    conn.executescript(sql_script)
    conn.commit()

    print("Database initialized successfully.")

    cursor=conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables=cursor.fetchall()
    print("Tables in the database:")
    for table in tables:
        print(table["name"])
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