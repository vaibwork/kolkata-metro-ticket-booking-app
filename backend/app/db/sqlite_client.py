import sqlite3
from pathlib import Path
from contextlib import contextmanager
from app.core.config import settings

DB_PATH = Path(settings.SQLITE_DB_PATH)
if not DB_PATH.is_absolute():
    DB_PATH = Path(__file__).resolve().parents[3] / DB_PATH

@contextmanager
def get_sqlite_conn():
    if not DB_PATH.exists():
        raise FileNotFoundError(f"SQLite database not found: {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    try:
        yield conn
    finally:
        conn.close()
