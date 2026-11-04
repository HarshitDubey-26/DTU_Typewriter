"""Application controller — the single point of coordination.

Implements the four-screen workflow:
    Screen 1: Student Login
    Screen 2: Instructions
    Screen 3: Typing Test
    Screen 4: Results

* Owns the task and result queues.
* Starts the background DatabaseWorker.
* Maps UI events to DB tasks.
* Dispatches worker results back to the UI.
"""
import queue
import logging
import random
import tkinter as tk
from tkinter import messagebox
from app.workers.db_worker import DatabaseWorker
from app.workers.task_queue import DBTask, Result
from app.services.typing_stats import TypingStatsService
from app.services.autosave import AutosaveService

logger = logging.getLogger("dtu_typewriter.controller")


class AppController:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.task_queue: queue.Queue = queue.Queue()
        self.result_queue: queue.Queue = queue.Queue()
        self.db_worker = DatabaseWorker(self.task_queue, self.result_queue)
        self.stats_service = TypingStatsService()
        self.autosave = AutosaveService(root, self, interval_ms=3000)

        # Session state
        self.current_student = None   # dict with id, name, roll_no, …
        self.current_paragraph = None  # dict with id, title, content
        self.test_running = False
        self._test_settings = {"duration_sec": 60, "allow_backspace": True}
        self._result_submitted = False

        # Current screen reference (for cleanup)
        self._current_screen = None

    # ────────────────────────────────────────────────────────────
    #  Lifecycle
    # ────────────────────────────────────────────────────────────
    def start(self):
        self.db_worker.start()

        # Configure root window
        self.root.geometry("1060x720")
        self.root.minsize(860, 600)
        self.root.configure(bg="#1a1d23")
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        # Load settings from DB, then show login
        self._enqueue("get_settings", {}, "settings_loaded")
        self._poll_worker()

        # Show the login screen immediately
        self._show_login_screen()

    def shutdown(self):
        self.autosave.stop()
        self.task_queue.put(DBTask(action="shutdown"))
        self.db_worker.join(timeout=3)
        logger.info("Controller shut down")

    # ────────────────────────────────────────────────────────────
    #  Worker polling (runs on main thread via root.after)
    # ────────────────────────────────────────────────────────────
    def _poll_worker(self):
        try:
            while True:
                r: Result = self.result_queue.get_nowait()
                self._dispatch(r)
        except queue.Empty:
            pass
        self.root.after(100, self._poll_worker)

    def _enqueue(self, action: str, payload: dict, callback: str = ""):
        tid = self.db_worker.next_task_id()
        self.task_queue.put(
            DBTask(action=action, payload=payload, task_id=tid, callback=callback)
        )

    # ────────────────────────────────────────────────────────────
    #  Result dispatcher
    # ────────────────────────────────────────────────────────────
    def _dispatch(self, r: Result):
        if r.error:
            logger.error("Worker error [%s]: %s", r.callback, r.error)
            self._show_error("Database Error", r.error)
            return
        cb = r.callback
        if cb == "settings_loaded":
            if r.data:
                self._test_settings = r.data
        elif cb == "student_looked_up":
            self._on_student_lookup(r.data)
        elif cb == "paragraphs_loaded":
            self._on_paragraphs(r.data)
        elif cb == "draft_saved":
            pass  # silent
        elif cb == "result_saved":
            self._on_result_saved(r.data)
        # (future callbacks can be added here)

    # ────────────────────────────────────────────────────────────
    #  Screen management
    # ────────────────────────────────────────────────────────────
    def _destroy_current_screen(self):
        if self._current_screen is not None:
            try:
                self._current_screen.destroy()
            except Exception:
                pass
            self._current_screen = None

    # ────────────────────────────────────────────────────────────
    #  SCREEN 1 — Login
    # ────────────────────────────────────────────────────────────
    def _show_login_screen(self):
        from app.ui.screens import LoginScreen
        self._destroy_current_screen()
        self._current_screen = LoginScreen(self.root, on_login=self._do_login)

    def _do_login(self, roll_no: str):
        """Called when user clicks LOGIN.  Queries DB for the student."""
        self._enqueue(
            "get_student_by_roll",
            {"roll_no": roll_no},
            "student_looked_up",
        )

    def _on_student_lookup(self, data):
        if data is None:
            # Student not found
            if self._current_screen and hasattr(self._current_screen, "show_error"):
                self._current_screen.show_error(
                    "Student ID not found. Please check and try again."
                )
            return
        # Success — store student, navigate to instructions
        self.current_student = data
        logger.info("Student logged in: %s (%s)",
                    data["name"], data["roll_no"])
        self._show_instructions_screen()

    # ────────────────────────────────────────────────────────────
    #  SCREEN 2 — Instructions
    # ────────────────────────────────────────────────────────────
    def _show_instructions_screen(self):
        from app.ui.screens import InstructionsScreen
        self._destroy_current_screen()
        duration = self._test_settings.get("duration_sec", 60)
        self._current_screen = InstructionsScreen(
            self.root,
            student_name=self.current_student["name"],
            duration_sec=duration,
            on_proceed=self._on_proceed,
        )

    def _on_proceed(self):
        """Load paragraphs from DB, then show typing test."""
        self._enqueue("list_active_paragraphs", {}, "paragraphs_loaded")

    def _on_paragraphs(self, paras):
        if not paras:
            self._show_error(
                "No Paragraphs",
                "No active paragraphs available. Please ask the admin to add some.",
            )
            # Re-enable proceed
            if self._current_screen and hasattr(self._current_screen, "proceed_btn"):
                self._current_screen.proceed_btn.config(state=tk.NORMAL,
                                                        text="PROCEED  →")
                self._current_screen._proceed_clicked = False
            return
        self.current_paragraph = random.choice(paras)
        self._show_typing_test_screen()

    # ────────────────────────────────────────────────────────────
    #  SCREEN 3 — Typing Test
    # ────────────────────────────────────────────────────────────
    def _show_typing_test_screen(self):
        from app.ui.screens import TypingTestScreen
        self._destroy_current_screen()
        self.test_running = True
        self._result_submitted = False

        duration = self._test_settings.get("duration_sec", 60)
        allow_bs = self._test_settings.get("allow_backspace", True)

        self._current_screen = TypingTestScreen(
            self.root,
            paragraph_title=self.current_paragraph["title"],
            paragraph_content=self.current_paragraph["content"],
            duration_sec=duration,
            allow_backspace=allow_bs,
            on_test_complete=self._on_test_complete,
        )

    def _on_test_complete(self, typed_text, elapsed_sec, error_count,
                          correct_keystrokes, total_keystrokes):
        """Called when the test ends (timer or paragraph completion)."""
        if self._result_submitted:
            return
        self._result_submitted = True
        self.test_running = False

        # Calculate stats
        wpm = self.stats_service.calculate_net_wpm(
            correct_keystrokes, elapsed_sec
        )
        accuracy = self.stats_service.calculate_accuracy(
            correct_keystrokes, total_keystrokes
        )

        # Save to DB
        self._enqueue("insert_result", {
            "student_id": self.current_student["id"],
            "paragraph_id": self.current_paragraph["id"],
            "wpm": wpm,
            "accuracy": accuracy,
            "errors": error_count,
            "time_taken": elapsed_sec,
        }, "result_saved")

        # Delete draft after successful submission
        self._enqueue("delete_draft", {
            "student_id": self.current_student["id"],
        })

        # Store result for the results screen
        self._pending_result = {
            "wpm": wpm,
            "accuracy": accuracy,
            "errors": error_count,
            "time_taken": elapsed_sec,
            "status": "Completed",
        }

    def _on_result_saved(self, data):
        """Navigate to results screen after DB confirms save."""
        if self.current_student:
            self.current_student["has_attempted"] = 1
        self._show_results_screen()

    # ────────────────────────────────────────────────────────────
    #  SCREEN 4 — Results
    # ────────────────────────────────────────────────────────────
    def _show_results_screen(self):
        from app.ui.screens import ResultsScreen
        self._destroy_current_screen()

        result = getattr(self, "_pending_result", {
            "wpm": 0, "accuracy": 0, "errors": 0,
            "time_taken": 0, "status": "Unknown",
        })

        self._current_screen = ResultsScreen(
            self.root,
            student_name=self.current_student["name"],
            result=result,
            on_retake=self._on_retake,
            on_instructions=self._show_instructions_screen,
            on_close=self._on_close,
        )

    def _on_retake(self):
        """Retake test: reset test state and immediately prepare a new test session."""
        self.test_running = False
        self._result_submitted = False
        self._pending_result = None
        self._on_proceed()

    # ────────────────────────────────────────────────────────────
    #  Draft management / Autosave
    # ────────────────────────────────────────────────────────────
    def autosave_now(self):
        if not self.current_student or not self.current_paragraph:
            return
        if not self._current_screen or not hasattr(self._current_screen, "get_typed_text"):
            return
        typed = self._current_screen.get_typed_text()
        remaining = getattr(self._current_screen, "_remaining", 0)
        errors = getattr(self._current_screen, "_error_count", 0)
        self._enqueue("upsert_draft", {
            "student_id": self.current_student["id"],
            "paragraph_id": self.current_paragraph["id"],
            "typed_text": typed,
            "remaining_seconds": max(remaining, 0),
            "errors": errors,
        }, "draft_saved")

    # ────────────────────────────────────────────────────────────
    #  Close / shutdown
    # ────────────────────────────────────────────────────────────
    def _on_close(self):
        if self.test_running:
            if not messagebox.askyesno(
                "Quit?",
                "A test is in progress. Your draft will be saved.\n"
                "Are you sure you want to quit?",
                parent=self.root,
            ):
                return
            self.autosave_now()
        self.shutdown()
        self.root.destroy()

    # ────────────────────────────────────────────────────────────
    #  Helpers
    # ────────────────────────────────────────────────────────────
    def _show_error(self, title, msg):
        messagebox.showerror(title, msg, parent=self.root)
