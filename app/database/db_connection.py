"""Thread-local SQLite connection manager.

Creates the database file under %LOCALAPPDATA%\\DTUTypewriter on first
connection and applies schema.sql exactly once.  Supports WAL mode and
enforces foreign keys.
"""
import sqlite3
from pathlib import Path
from app.utils.paths import get_database_path, get_schema_path


class DBConnection:
    def __init__(self, db_path: str = None):
        if db_path is None:
            self.db_path = get_database_path()
        else:
            self.db_path = Path(db_path)
        self._ensure_db_exists()
        self.conn = sqlite3.connect(
            str(self.db_path), timeout=30.0, check_same_thread=False,
        )
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.execute("PRAGMA journal_mode = WAL")
        self.conn.execute("PRAGMA busy_timeout = 5000")
        self.conn.row_factory = sqlite3.Row

    # ── initialisation ──────────────────────────────────────────
    def _ensure_db_exists(self):
        if str(self.db_path) == ":memory:" or self.db_path.exists():
            return
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        schema_path = get_schema_path()
        if not schema_path.exists():
            raise FileNotFoundError(
                "Schema file not found: " + str(schema_path)
            )
        sql = schema_path.read_text(encoding="utf-8")
        tmp = sqlite3.connect(str(self.db_path))
        tmp.executescript(sql)
        tmp.commit()
        tmp.close()

    def init_memory(self, schema_sql: str):
        self.conn.executescript(schema_sql)
        self.conn.commit()

    # ── query helpers ───────────────────────────────────────────
    def execute(self, sql: str, params: tuple = ()):
        cur = self.conn.cursor()
        cur.execute(sql, params)
        self.conn.commit()
        return cur

    def executemany(self, sql: str, seq):
        cur = self.conn.cursor()
        cur.executemany(sql, seq)
        self.conn.commit()
        return cur

    def query(self, sql: str, params: tuple = ()):
        cur = self.conn.cursor()
        cur.execute(sql, params)
        return cur.fetchall()

    def close(self):
        try:
            self.conn.close()
        except Exception:
            pass
