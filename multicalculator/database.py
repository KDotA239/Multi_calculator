"""Historial de operaciones en SQLite (consultas siempre parametrizadas)."""
import sqlite3
from contextlib import closing

MAX_ROWS = 500

SCHEMA = """
CREATE TABLE IF NOT EXISTS history (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    kind       TEXT NOT NULL CHECK (kind IN ('calculo', 'matriz')),
    input      TEXT NOT NULL,
    result     TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
)
"""


def _connect(path):
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(path):
    with closing(_connect(path)) as conn, conn:
        conn.execute(SCHEMA)


def add_entry(path, kind, input_text, result_text):
    with closing(_connect(path)) as conn, conn:
        conn.execute(
            "INSERT INTO history (kind, input, result) VALUES (?, ?, ?)",
            (kind, input_text, result_text),
        )
        # Conserva solo las últimas MAX_ROWS operaciones.
        conn.execute(
            "DELETE FROM history WHERE id NOT IN (SELECT id FROM history ORDER BY id DESC LIMIT ?)",
            (MAX_ROWS,),
        )


def list_entries(path, limit=50):
    with closing(_connect(path)) as conn:
        rows = conn.execute(
            "SELECT kind, input, result, created_at FROM history ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [dict(r) for r in rows]


def clear(path):
    with closing(_connect(path)) as conn, conn:
        conn.execute("DELETE FROM history")
