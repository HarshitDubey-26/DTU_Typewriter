"""Tests for UI screens: LoginScreen, InstructionsScreen, TypingTestScreen, ResultsScreen."""
import os
import tkinter as tk
import pytest
from app.ui.screens import LoginScreen, InstructionsScreen, TypingTestScreen, ResultsScreen
from app.services.pdf_report import generate_typing_report


def test_typing_test_screen_start_button_and_cursor(root):
    completed = []

    def on_complete(typed, elapsed, errors, correct, total):
        completed.append((typed, elapsed, errors, correct, total))

    screen = TypingTestScreen(
        root,
        paragraph_title="Test Para",
        paragraph_content="Hello world.",
        duration_sec=60,
        allow_backspace=True,
        on_test_complete=on_complete,
    )
    root.update()

    # Verify initial state: test not started, timer not running
    assert screen._test_started is False
    assert screen._test_active is False
    assert screen.start_btn.winfo_ismapped()
    assert str(screen.type_text.cget("state")) == "disabled"
    assert screen.type_text.get("1.0", "end-1c") == ""

    # Simulate user clicking START button
    screen._on_start_clicked()
    root.update()

    # Verify state after start: active, placeholder cleared, text enabled, cursor at 1.0
    assert screen._test_started is True
    assert screen._test_active is True
    assert str(screen.type_text.cget("state")) == "normal"
    assert screen.type_text.get("1.0", "end-1c") == ""
    assert screen.type_text.index("insert") == "1.0"

    # Simulate typing 'H'
    class KeyEvent:
        char = 'H'
        keysym = 'H'
        state = 0

    res = screen._on_key(KeyEvent())
    assert res == "break"
    assert screen.type_text.get("1.0", "end-1c") == "H"
    assert screen._cursor_pos == 1
    assert screen._correct_keystrokes == 1
    assert screen._error_count == 0

    screen.destroy()


def test_results_screen_retake_button(root):
    retake_called = []
    close_called = []

    screen = ResultsScreen(
        root,
        student_name="Alice",
        result={"wpm": 45.0, "accuracy": 98.0, "errors": 1, "time_taken": 60, "status": "Completed"},
        on_retake=lambda: retake_called.append(True),
        on_close=lambda: close_called.append(True),
    )
    root.update()

    # Find the retake button
    found_retake = False
    for widget in screen.frame.winfo_children():
        for child in widget.winfo_children():
            if isinstance(child, tk.Frame):
                for subchild in child.winfo_children():
                    if isinstance(subchild, tk.Button) and "RETAKE" in subchild.cget("text"):
                        found_retake = True
                        subchild.invoke()

    assert found_retake is True
    assert retake_called == [True]
    screen.destroy()


def test_typing_test_screen_resumed_from_draft(root):
    completed = []
    changes = []

    draft = {
        "typed_text": "Hello",
        "remaining_seconds": 45,
        "errors": 1,
    }

    screen = TypingTestScreen(
        root,
        paragraph_title="Resume Para",
        paragraph_content="Hello world.",
        duration_sec=60,
        allow_backspace=True,
        on_test_complete=lambda *args: completed.append(args),
        on_change=lambda: changes.append(True),
        draft=draft,
    )
    root.update()

    # Verify resumed state
    assert screen._test_started is False
    assert "RESUME" in screen.start_btn.cget("text")
    assert screen.timer_var.get() == "00:45"
    assert screen.type_text.get("1.0", "end-1c") == "Hello"
    assert screen._cursor_pos == 5
    assert screen._error_count == 1
    assert screen._initial_elapsed == 15

    # Click resume
    screen._on_start_clicked()
    root.update()

    assert screen._test_started is True
    assert screen._test_active is True
    assert screen.type_text.get("1.0", "end-1c") == "Hello"

    # Type next character ' ' (space)
    class SpaceEvent:
        char = ' '
        keysym = 'space'
        state = 0

    screen._on_key(SpaceEvent())
    assert screen.type_text.get("1.0", "end-1c") == "Hello "
    assert screen._cursor_pos == 6
    assert len(changes) >= 1

    screen.destroy()


def test_results_screen_thank_you_and_download_button(root, tmp_path):
    res_data = {
        "wpm": 52.4,
        "accuracy": 98.5,
        "kdph": 15720.0,
        "errors": 2,
        "time_taken": 60,
        "total_keystrokes": 262,
        "correct_keystrokes": 258,
        "paragraph_title": "DTU Examination",
        "assigned_paragraph": "Delhi Technological University is premier.",
        "typed_text": "Delhi Technological University is premier.",
        "status": "Completed",
    }

    screen = ResultsScreen(
        root,
        student_name="Aarti Sharma",
        student_roll="2K21/CO/999",
        result=res_data,
    )
    root.update()

    # Check that Thank You greeting and Student ID are present
    labels = []
    def collect_labels(w):
        if isinstance(w, tk.Label):
            labels.append(w.cget("text"))
        for child in w.winfo_children():
            collect_labels(child)

    collect_labels(screen.frame)
    assert any("Thank You, Aarti Sharma!" in txt for txt in labels)
    assert any("Student ID: 2K21/CO/999" in txt for txt in labels)

    # Check Download Report button exists
    assert hasattr(screen, "download_btn")
    assert "DOWNLOAD YOUR REPORT" in screen.download_btn.cget("text")

    # Verify PDF generation directly with this result
    pdf_out = str(tmp_path / "test_report.pdf")
    gen_path = generate_typing_report(pdf_out, res_data)
    assert os.path.exists(gen_path)
    assert os.path.getsize(gen_path) > 1000

    screen.destroy()
