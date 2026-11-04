"""Repository layer — one method per database operation.

Every public method maps directly to a table in the existing schema.
The controller never writes raw SQL; it calls these methods instead.
"""
import sqlite3
import shutil
import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
from app.database.db_connection import DBConnection
from app.utils.paths import get_backup_dir


class DBOperations:
    def __init__(self, db_path: str = None):
        self.conn = DBConnection(db_path)

    # ── settings ────────────────────────────────────────────────
    def get_settings(self) -> Dict[str, Any]:
        rows = self.conn.query(
            "SELECT duration_sec, allow_backspace FROM settings WHERE id = 1"
        )
        if rows:
            r = rows[0]
            return {
                "duration_sec": r["duration_sec"],
                "allow_backspace": bool(r["allow_backspace"]),
            }
        return {"duration_sec": 60, "allow_backspace": True}

    def update_settings(self, duration_sec: int, allow_backspace: int) -> None:
        self.conn.execute(
            "UPDATE settings SET duration_sec=?, allow_backspace=? WHERE id=1",
            (duration_sec, allow_backspace),
        )

    # ── students ────────────────────────────────────────────────
    def create_student(
        self, roll_no: str, name: str, email: str, password: str
    ) -> int:
        cur = self.conn.execute(
            "INSERT INTO students (roll_no, name, email, password) "
            "VALUES (?, ?, ?, ?)",
            (roll_no, name, email, password),
        )
        return cur.lastrowid

    def get_student_by_roll(self, roll_no: str) -> Optional[Dict[str, Any]]:
        rows = self.conn.query(
            "SELECT * FROM students WHERE roll_no = ?", (roll_no,)
        )
        return dict(rows[0]) if rows else None

    def get_student_by_id(self, student_id: int) -> Optional[Dict[str, Any]]:
        rows = self.conn.query(
            "SELECT * FROM students WHERE id = ?", (student_id,)
        )
        return dict(rows[0]) if rows else None

    def authenticate_student(
        self, roll_no: str, password: str
    ) -> Optional[Dict[str, Any]]:
        rows = self.conn.query(
            "SELECT * FROM students WHERE roll_no = ? AND password = ?",
            (roll_no, password),
        )
        return dict(rows[0]) if rows else None

    # ── paragraphs ──────────────────────────────────────────────
    def list_active_paragraphs(self) -> List[Dict[str, Any]]:
        rows = self.conn.query(
            "SELECT id, title, content FROM paragraphs WHERE is_active = 1"
        )
        return [dict(r) for r in rows]

    def get_paragraph(self, paragraph_id: int) -> Optional[Dict[str, Any]]:
        rows = self.conn.query(
            "SELECT * FROM paragraphs WHERE id = ?", (paragraph_id,)
        )
        return dict(rows[0]) if rows else None

    def add_paragraph(self, title: str, content: str) -> int:
        cur = self.conn.execute(
            "INSERT INTO paragraphs (title, content) VALUES (?, ?)",
            (title, content),
        )
        return cur.lastrowid

    # ── typing_drafts ───────────────────────────────────────────
    def upsert_draft(
        self,
        student_id: int,
        paragraph_id: int,
        typed_text: str,
        remaining_seconds: int,
        errors: int,
    ) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO typing_drafts "
            "(student_id, paragraph_id, typed_text, remaining_seconds, "
            "errors, updated_at) "
            "VALUES (?, ?, ?, ?, ?, strftime('%Y-%m-%dT%H:%M:%fZ','now'))",
            (student_id, paragraph_id, typed_text, remaining_seconds, errors),
        )

    def get_draft(self, student_id: int) -> Optional[Dict[str, Any]]:
        rows = self.conn.query(
            "SELECT * FROM typing_drafts WHERE student_id = ?",
            (student_id,),
        )
        return dict(rows[0]) if rows else None

    def delete_draft(self, student_id: int) -> None:
        self.conn.execute(
            "DELETE FROM typing_drafts WHERE student_id = ?",
            (student_id,),
        )

    # ── results ─────────────────────────────────────────────────
    def insert_result(
        self,
        student_id: int,
        paragraph_id: int,
        wpm: float,
        accuracy: float,
        errors: int,
        time_taken: int,
    ) -> int:
        cur = self.conn.execute(
            "INSERT INTO results "
            "(student_id, paragraph_id, wpm, accuracy, errors, "
            "time_taken, submitted_at) "
            "VALUES (?, ?, ?, ?, ?, ?, "
            "strftime('%Y-%m-%dT%H:%M:%fZ','now'))",
            (student_id, paragraph_id, wpm, accuracy, errors, time_taken),
        )
        return cur.lastrowid

    def list_results_for_student(
        self, student_id: int
    ) -> List[Dict[str, Any]]:
        rows = self.conn.query(
            "SELECT * FROM results WHERE student_id = ? "
            "ORDER BY submitted_at DESC",
            (student_id,),
        )
        return [dict(r) for r in rows]

    # ── backup ──────────────────────────────────────────────────
    def backup_database(self) -> str:
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        dest = get_backup_dir() / ("dtu_typewriter_backup_" + ts + ".db")
        src = sqlite3.connect(str(self.conn.db_path))
        dst = sqlite3.connect(str(dest))
        src.backup(dst)
        dst.close()
        src.close()
        return str(dest)

    def close(self):
        self.conn.close()
