import os
import sqlite3
from contextlib import closing
from datetime import datetime
from typing import Dict, List, Optional

DB_PATH = os.getenv("DATABASE_URL", "sqlite:///./data/db.sqlite3")

# Normalize to file path for sqlite3.
if DB_PATH.startswith("sqlite:///"):
    DB_FILE = DB_PATH.replace("sqlite://", "")
else:
    DB_FILE = DB_PATH


def _ensure_dir():
    directory = os.path.dirname(DB_FILE)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)


def _get_conn():
    _ensure_dir()
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with closing(_get_conn()) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


def save_message(role: str, content: str) -> int:
    now = datetime.utcnow().isoformat() + "Z"
    with closing(_get_conn()) as conn:
        cur = conn.execute(
            "INSERT INTO messages (role, content, created_at) VALUES (?, ?, ?)",
            (role, content, now),
        )
        conn.commit()
        return cur.lastrowid


def get_last_messages(limit: int = 50) -> List[Dict[str, str]]:
    with closing(_get_conn()) as conn:
        cur = conn.execute(
            "SELECT role, content, created_at FROM messages ORDER BY id DESC LIMIT ?", (limit,)
        )
        rows = cur.fetchall()
    return [dict(r) for r in reversed(rows)]


def clear_messages() -> None:
    with closing(_get_conn()) as conn:
        conn.execute("DELETE FROM messages")
        conn.commit()


def get_message_count() -> int:
    with closing(_get_conn()) as conn:
        cur = conn.execute("SELECT COUNT(*) as c FROM messages")
        return cur.fetchone()["c"]


def get_last_n_messages(n: int) -> List[Dict[str, str]]:
    return get_last_messages(limit=n)


# NOTE: Context summarization is handled by the model client.
# This storage layer only manages persistence.
