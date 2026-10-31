"""
Admin sign-in sessions, stored in SQLite so they survive a server restart.

Only a SHA-256 hash of each token is stored. A copy of the database cannot
be used to sign in, because the token itself is never written to disk.
"""

import hashlib
import secrets
import sqlite3
import time
from contextlib import closing
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "data" / "risklens.db"

# How long a sign-in lasts.
SESSION_SECONDS = 12 * 60 * 60


def _connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS admin_sessions ("
        " token_hash TEXT PRIMARY KEY,"
        " expires_at REAL NOT NULL)"
    )
    return conn


def _hash(token):
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_session():
    """Start a sign-in and return its token. The caller sends the token to the browser."""
    token = secrets.token_urlsafe(32)
    now = time.time()
    with closing(_connect()) as conn, conn:
        conn.execute("DELETE FROM admin_sessions WHERE expires_at <= ?", (now,))
        conn.execute(
            "INSERT INTO admin_sessions (token_hash, expires_at) VALUES (?, ?)",
            (_hash(token), now + SESSION_SECONDS),
        )
    return token


def is_valid_session(token):
    """True when the token belongs to a sign-in that has not expired."""
    if not token:
        return False
    with closing(_connect()) as conn:
        row = conn.execute(
            "SELECT expires_at FROM admin_sessions WHERE token_hash = ?",
            (_hash(token),),
        ).fetchone()
    return row is not None and row[0] > time.time()


def delete_session(token):
    """End a sign-in. Unknown or empty tokens are ignored."""
    if not token:
        return
    with closing(_connect()) as conn, conn:
        conn.execute("DELETE FROM admin_sessions WHERE token_hash = ?", (_hash(token),))
