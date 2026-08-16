import sqlite3
import json
import hashlib
import re
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
            kind TEXT NOT NULL,
            category TEXT NOT NULL,
            title TEXT NOT NULL,
            company TEXT,
            location TEXT,
            url TEXT NOT NULL,
            source TEXT NOT NULL,
            posted TEXT,
            score INTEGER DEFAULT 0,
            opportunity_type TEXT DEFAULT 'JOB',
            match_score INTEGER DEFAULT 0,
            matched_skills TEXT DEFAULT '[]',
            status TEXT DEFAULT 'new',
            fingerprint TEXT,
            fetched_at TEXT NOT NULL
        )
    """)
    cols = [row["name"] for row in conn.execute("PRAGMA table_info(listings)")]
    if "fingerprint" not in cols:
        conn.execute("ALTER TABLE listings ADD COLUMN fingerprint TEXT")
    if "opportunity_type" not in cols:
        conn.execute(
            "ALTER TABLE listings ADD COLUMN opportunity_type TEXT DEFAULT 'JOB'"
        )
    if "match_score" not in cols:
        conn.execute(
            "ALTER TABLE listings ADD COLUMN match_score INTEGER DEFAULT 0"
        )
    if "matched_skills" not in cols:
        conn.execute(
            "ALTER TABLE listings ADD COLUMN matched_skills TEXT DEFAULT '[]'"
        )
    if "lead_type" not in cols:
        conn.execute(
            "ALTER TABLE listings ADD COLUMN lead_type TEXT DEFAULT 'JOB'"
        )
    if "intent" not in cols:
        conn.execute(
            "ALTER TABLE listings ADD COLUMN intent TEXT DEFAULT 'EMPLOYMENT'"
        )
    if "commercial_value" not in cols:
        conn.execute(
            "ALTER TABLE listings ADD COLUMN commercial_value TEXT DEFAULT 'LOW'"
        )
    if "recommended_action" not in cols:
        conn.execute(
            "ALTER TABLE listings ADD COLUMN recommended_action TEXT DEFAULT 'REVIEW'"
        )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_fingerprint ON listings (category, kind, fingerprint)"
    )
    conn.commit()
    conn.close()


def make_id(source: str, url: str) -> str:
    return hashlib.sha256(f"{source}:{url}".encode()).hexdigest()[:16]


def make_fingerprint(title: str, company: str) -> str:
    """Normalized signature used to catch the same listing posted on multiple sources."""
    def norm(s):
        s = (s or "").lower()
        s = re.sub(r"[^a-z0-9]+", " ", s)
        return re.sub(r"\s+", " ", s).strip()
    return f"{norm(title)}|{norm(company)}"


def upsert_listing(listing: dict) -> bool:
    """Insert if genuinely new. Returns False for exact id repeats AND for
    cross-source duplicates (same normalized title+company in the same category)."""
    conn = _connect()
    existing = conn.execute("SELECT id FROM listings WHERE id = ?", (listing["id"],)).fetchone()
    if existing:
        conn.close()
        return False

    fingerprint = make_fingerprint(listing["title"], listing.get("company", ""))
    dupe = conn.execute(
        "SELECT id FROM listings WHERE category = ? AND kind = ? AND fingerprint = ?",
        (listing["category"], listing["kind"], fingerprint),
    ).fetchone()
    if dupe:
        conn.close()
        return False

    conn.execute("""
        INSERT INTO listings (
            id, kind, category, title, company, location, url, source,
            posted, score, opportunity_type, match_score, matched_skills,
            status, fingerprint, fetched_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'new', ?, ?)
    """, (
        listing["id"], listing["kind"], listing["category"], listing["title"],
        listing.get("company", ""), listing.get("location", ""), listing["url"],
        listing["source"],
        listing.get("posted", ""),
        listing.get("score", 0),
        listing.get("opportunity_type", "JOB"),
        listing.get("match_score", 0),
        json.dumps(listing.get("matched_skills", [])),
        fingerprint,
        datetime.utcnow().isoformat(),
    ))
    conn.commit()
    conn.close()
    return True


def list_listings(category=None, status=None, kind=None, limit=25, min_score=None):
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
    if min_score is not None:
        query += " AND score >= ?"
        params.append(min_score)
    query += " ORDER BY score DESC, fetched_at DESC LIMIT ?"
    params.append(limit)
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return rows


def export_listings(category=None, status=None, kind=None, min_score=None):
    """Same filters as list_listings but no limit — used for full exports."""
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
    if min_score is not None:
        query += " AND score >= ?"
        params.append(min_score)
    query += " ORDER BY score DESC, fetched_at DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return rows


def get_listing(listing_id: str):
    conn = _connect()
    row = conn.execute(
        "SELECT * FROM listings WHERE id = ? OR id LIKE ?", (listing_id, f"{listing_id}%")
    ).fetchone()
    conn.close()
    return row


def set_status(listing_id: str, status: str) -> bool:
    conn = _connect()
    cur = conn.execute(
        "UPDATE listings SET status = ? WHERE id = ? OR id LIKE ?", (status, listing_id, f"{listing_id}%")
    )
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
