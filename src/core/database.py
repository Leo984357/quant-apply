import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "applications.db"

def get_conn():
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            platform TEXT NOT NULL,
            company TEXT,
            title TEXT,
            url TEXT UNIQUE,
            score INTEGER,
            status TEXT DEFAULT 'pending',
            applied_at TIMESTAMP,
            note TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS platform_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            platform TEXT,
            action TEXT,
            result TEXT,
            ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    return conn

def log_application(platform, company, title, url, score=0, status="pending"):
    conn = get_conn()
    conn.execute(
        "INSERT OR IGNORE INTO applications (platform, company, title, url, score, status, applied_at) VALUES (?,?,?,?,?,?,?)",
        (platform, company, title, url, score, status, datetime.utcnow().isoformat())
    )
    conn.commit()

def update_status(url, status, note=""):
    conn = get_conn()
    conn.execute("UPDATE applications SET status=?, note=? WHERE url=?", (status, note, url))
    conn.commit()

def get_stats():
    conn = get_conn()
    cur = conn.execute("SELECT status, COUNT(*) FROM applications GROUP BY status")
    return dict(cur.fetchall())

def log(platform, action, result="ok"):
    conn = get_conn()
    conn.execute("INSERT INTO platform_log (platform, action, result) VALUES (?,?,?)",
                 (platform, action, result))
    conn.commit()
