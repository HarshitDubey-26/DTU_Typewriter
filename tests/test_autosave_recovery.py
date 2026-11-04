"""Tests for continuous autosave and draft recovery under simulated interruptions."""
import os
import sqlite3
import pytest
from pathlib import Path
from app.services.autosave import AutosaveService
from app.database.db_operations import DBOperations

SCHEMA = (Path(__file__).resolve().parents[1] / "schema.sql").read_text("utf-8")


def _make_db(tmp_path):
    db_file = os.path.join(str(tmp_path), "test.db")
    conn = sqlite3.connect(db_file)
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()
    return db_file


class DummyController:
    def __init__(self):
        self.saved = 0

    def autosave_now(self):
        self.saved += 1


def test_autosave_service_keystroke_threshold(root):
    controller = DummyController()
    svc = AutosaveService(root, controller, interval_ms=1000, periodic_ms=1000)

    # 9 keystrokes should not trigger immediate save
    for _ in range(9):
        svc.mark_dirty(keystroke=True)
    assert controller.saved == 0

    # 10th keystroke triggers immediate save
    svc.mark_dirty(keystroke=True)
    assert controller.saved == 1

    svc.stop()


def test_autosave_service_debounce(root):
    import time
    controller = DummyController()
    svc = AutosaveService(root, controller, interval_ms=50, periodic_ms=50)

    svc.mark_dirty(keystroke=False)
    assert controller.saved == 0

    # Wait for debounce timer
    time.sleep(0.08)
    root.update()

    assert controller.saved >= 1
    svc.stop()


def test_draft_persistence_and_resume_simulation(tmp_path):
    db_file = _make_db(tmp_path)
    ops = DBOperations(db_path=db_file)

    # 1. Create student and paragraph
    sid = ops.create_student("RECOVER/001", "Recovery Student", "rec@dtu.ac.in", "pass")
    pid = ops.add_paragraph("Interrupted Test", "This is an important exam paragraph.")

    # 2. Simulate typing 15 characters, 1 error, 45 seconds left when sudden power cut happens
    ops.upsert_draft(
        student_id=sid,
        paragraph_id=pid,
        typed_text="This is an impo",
        remaining_seconds=45,
        errors=1,
    )

    # 3. Simulate app restart after power returns
    # A fresh DBOperations connection opens (just like app launch)
    ops2 = DBOperations(db_path=db_file)
    recovered_draft = ops2.get_draft(sid)

    assert recovered_draft is not None
    assert recovered_draft["typed_text"] == "This is an impo"
    assert recovered_draft["remaining_seconds"] == 45
    assert recovered_draft["errors"] == 1
    assert recovered_draft["paragraph_id"] == pid

    # 4. Fetch paragraph to resume
    recovered_para = ops2.get_paragraph(recovered_draft["paragraph_id"])
    assert recovered_para["title"] == "Interrupted Test"

    # 5. After test finishes, draft is deleted
    ops2.delete_draft(sid)
    assert ops2.get_draft(sid) is None

    ops.close()
    ops2.close()
