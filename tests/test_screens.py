"""Tests for UI screens: LoginScreen, InstructionsScreen, TypingTestScreen, ResultsScreen."""
import tkinter as tk
import pytest
from app.ui.screens import LoginScreen, InstructionsScreen, TypingTestScreen, ResultsScreen


@pytest.fixture
def root():
    r = tk.Tk()
    r.geometry("1060x720")
    yield r
    try:
        r.destroy()
    except Exception:
        pass


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
    buttons = [w for w in screen.frame.winfo_children() if isinstance(w, tk.Frame)]
    # Look through container children for buttons
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
