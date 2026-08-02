import sqlite3
import hashlib
from datetime import datetime

from config import DB_PATH


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = _connect()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS listings (
            id TEXT PRIMARY KEY,
            kind TEXT NOT NULL,           -- 'job' or 'client'
            category TEXT NOT NULL,
            title TEXT NOT NULL,
            company TEXT,
            location TEXT,
            url TEXT NOT NULL,
            source TEXT NOT NULL,
            posted TEXT,
            score INTEGER DEFAULT 0,
            status TEXT DEFAULT 'new',    -- new, saved, applied, rejected
            fetched_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def make_id(source: str, url: str) -> str:
    return hashlib.sha256(f"{source}:{url}".encode()).hexdigest()[:16]


def upsert_listing(listing: dict) -> bool:
    """Insert if new. Returns True if it was a new row, False if it already existed."""
    conn = _connect()
    existing = conn.execute("SELECT id FROM listings WHERE id = ?", (listing["id"],)).fetchone()
    if existing:
        conn.close()
        return False
    conn.execute("""
        INSERT INTO listings (id, kind, category, title, company, location, url, source, posted, score, status, fetched_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'new', ?)
    """, (
        listing["id"], listing["kind"], listing["category"], listing["title"],
        listing.get("company", ""), listing.get("location", ""), listing["url"],
        listing["source"], listing.get("posted", ""), listing.get("score", 0),
        datetime.utcnow().isoformat(),
    ))
    conn.commit()
    conn.close()
    return True


def list_listings(category=None, status=None, kind=None, limit=25):
    conn = _connect()
    query = "SELECT * FROM listings WHERE 1=1"
    params = []
    if category:
        query += " AND category = ?"
        params.append(category)
    if status:
        query += " AND status = ?"
        params.append(status)
    if kind:
        query += " AND kind = ?"
        params.append(kind)
    query += " ORDER BY score DESC, fetched_at DESC LIMIT ?"
    params.append(limit)
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return rows


def get_listing(listing_id: str):
    conn = _connect()
    row = conn.execute("SELECT * FROM listings WHERE id = ? OR id LIKE ?", (listing_id, f"{listing_id}%")).fetchone()
    conn.close()
    return row


def set_status(listing_id: str, status: str) -> bool:
    conn = _connect()
    cur = conn.execute("UPDATE listings SET status = ? WHERE id = ? OR id LIKE ?", (status, listing_id, f"{listing_id}%"))
    conn.commit()
    changed = cur.rowcount > 0
    conn.close()
    return changed


def stats():
    conn = _connect()
    rows = conn.execute("""
        SELECT category, status, COUNT(*) as n FROM listings GROUP BY category, status
    """).fetchall()
    conn.close()
    return rows
