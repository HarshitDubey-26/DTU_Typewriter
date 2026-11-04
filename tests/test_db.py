"""pytest suite for the database repository layer.

Every test creates a fresh temporary database from schema.sql so that the
real user database is never touched.
"""
import sqlite3
import os
import pytest
from pathlib import Path

SCHEMA = (Path(__file__).resolve().parents[1] / "schema.sql").read_text("utf-8")


def _make_db(tmp_path):
    db_file = os.path.join(str(tmp_path), "test.db")
    conn = sqlite3.connect(db_file)
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()
    return db_file


def _ops(db_file):
    from app.database.db_operations import DBOperations
    return DBOperations(db_path=db_file)


# ── settings ────────────────────────────────────────────────────
def test_default_settings(tmp_path):
    ops = _ops(_make_db(tmp_path))
    s = ops.get_settings()
    assert s["duration_sec"] == 60
    assert s["allow_backspace"] is True
    ops.close()

def test_update_settings(tmp_path):
    ops = _ops(_make_db(tmp_path))
    ops.update_settings(120, 0)
    s = ops.get_settings()
    assert s["duration_sec"] == 120
    assert s["allow_backspace"] is False
    ops.close()

# ── students ────────────────────────────────────────────────────
def test_create_student(tmp_path):
    ops = _ops(_make_db(tmp_path))
    sid = ops.create_student("TEST/CO/001", "Alice", "alice@dtu.ac.in", "pass")
    assert sid >= 1
    stu = ops.get_student_by_roll("TEST/CO/001")
    assert stu["name"] == "Alice"
    ops.close()

def test_duplicate_roll_raises(tmp_path):
    ops = _ops(_make_db(tmp_path))
    ops.create_student("TEST/CO/002", "Bob", "bob@dtu.ac.in", "pw")
    with pytest.raises(Exception):
        ops.create_student("TEST/CO/002", "Bob2", "b2@dtu.ac.in", "pw2")
    ops.close()

def test_authenticate(tmp_path):
    ops = _ops(_make_db(tmp_path))
    ops.create_student("TEST/CO/003", "Carol", "c@dtu.ac.in", "secret")
    assert ops.authenticate_student("TEST/CO/003", "secret") is not None
    assert ops.authenticate_student("TEST/CO/003", "wrong") is None
    ops.close()

# ── paragraphs ──────────────────────────────────────────────────
def test_paragraphs(tmp_path):
    ops = _ops(_make_db(tmp_path))
    initial_count = len(ops.list_active_paragraphs())
    pid = ops.add_paragraph("Sample", "The quick brown fox.")
    assert pid >= 1
    paras = ops.list_active_paragraphs()
    assert len(paras) == initial_count + 1
    assert any(p["title"] == "Sample" for p in paras)
    ops.close()

# ── drafts ──────────────────────────────────────────────────────
def test_draft_upsert(tmp_path):
    ops = _ops(_make_db(tmp_path))
    sid = ops.create_student("TEST/CO/004", "Dave", "d@dtu.ac.in", "pw")
    pid = ops.add_paragraph("T", "Hello world.")
    ops.upsert_draft(sid, pid, "Hel", 55, 0)
    d = ops.get_draft(sid)
    assert d["typed_text"] == "Hel"
    # Update
    ops.upsert_draft(sid, pid, "Hello", 50, 1)
    d2 = ops.get_draft(sid)
    assert d2["typed_text"] == "Hello"
    assert d2["errors"] == 1
    ops.close()

def test_delete_draft(tmp_path):
    ops = _ops(_make_db(tmp_path))
    sid = ops.create_student("TEST/CO/005", "Eve", "e@dtu.ac.in", "pw")
    pid = ops.add_paragraph("T", "text")
    ops.upsert_draft(sid, pid, "te", 58, 0)
    ops.delete_draft(sid)
    assert ops.get_draft(sid) is None
    ops.close()

# ── results ─────────────────────────────────────────────────────
def test_result_and_trigger(tmp_path):
    ops = _ops(_make_db(tmp_path))
    sid = ops.create_student("TEST/CO/006", "Frank", "f@dtu.ac.in", "pw")
    pid = ops.add_paragraph("T", "text")
    rid = ops.insert_result(sid, pid, 45.5, 92.3, 3, 58)
    assert rid >= 1
    stu = ops.get_student_by_roll("TEST/CO/006")
    assert stu["has_attempted"] == 1
    ops.close()

def test_results_listing(tmp_path):
    ops = _ops(_make_db(tmp_path))
    sid = ops.create_student("TEST/CO/007", "Grace", "g@dtu.ac.in", "pw")
    pid = ops.add_paragraph("T", "text")
    ops.insert_result(sid, pid, 40.0, 90.0, 2, 60)
    ops.insert_result(sid, pid, 50.0, 95.0, 1, 55)
    results = ops.list_results_for_student(sid)
    assert len(results) == 2
    ops.close()

# ── unicode / Hindi ─────────────────────────────────────────────
def test_unicode_hindi(tmp_path):
    ops = _ops(_make_db(tmp_path))
    sid = ops.create_student("TEST/CO/008", "Test", "t@dtu.ac.in", "pw")
    pid = ops.add_paragraph("Hindi", "\u0928\u092e\u0938\u094d\u0924\u0947 \u0926\u0941\u0928\u093f\u092f\u093e")
    ops.upsert_draft(sid, pid, "\u0928\u092e\u0938\u094d\u0924\u0947", 30, 0)
    d = ops.get_draft(sid)
    assert "\u0928\u092e" in d["typed_text"]
    ops.close()

# ── helpers ─────────────────────────────────────────────────────
def test_calculate_accuracy():
    from app.utils.helpers import calculate_accuracy
    acc, errs = calculate_accuracy("hello", "hello")
    assert acc == 100.0
    assert errs == 0

def test_calculate_wpm():
    from app.utils.helpers import calculate_wpm
    wpm = calculate_wpm("one two three four five", 60)
    assert wpm == 5.0
