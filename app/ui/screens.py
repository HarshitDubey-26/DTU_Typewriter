"""Four-screen UI for the DTU Typewriter typing test.

Screen 1 — Student Login
Screen 2 — Typing Test Instructions
Screen 3 — Typing Test (reference paragraph + typing area)
Screen 4 — Results Dashboard

Every screen is a tk.Frame that fills the root window.  The controller
calls ``show_<screen>()`` to destroy the current screen and build the next
one.
"""
import tkinter as tk
from tkinter import ttk
import time


# ────────────────────────────────────────────────────────────────
#  Colour palette  (dark-charcoal theme)
# ────────────────────────────────────────────────────────────────
COLORS = {
    "bg":              "#12151c",
    "card_bg":         "#1c212d",
    "card_border":     "#2e394b",
    "fg":              "#f8fafc",
    "fg_muted":        "#94a3b8",
    "accent":          "#3b82f6",
    "accent_hover":    "#60a5fa",
    "correct":         "#22c55e",
    "correct_bg":      "#14532d",
    "error":           "#ef4444",
    "error_bg":        "#450a0a",
    "neutral_fg":      "#94a3b8",      # Crisp, clear, highly readable
    "input_bg":        "#1e2430",
    "input_border":    "#3b4961",
    "timer_fg":        "#f59e0b",
    "gold":            "#eab308",
    "green_badge":     "#16a34a",
    "divider":         "#262f3f",
    "typing_bg":       "#0b0e14",
    "typing_border":   "#334155",
    "ref_bg":          "#171b24",
    "white":           "#ffffff",
    "start_green":     "#16a34a",
    "start_green_h":   "#22c55e",
}


# ────────────────────────────────────────────────────────────────
#  Utility: clear a container
# ────────────────────────────────────────────────────────────────
def _clear(parent: tk.Misc):
    """Destroy every child widget of *parent*."""
    for w in parent.winfo_children():
        w.destroy()


# ================================================================
#  SCREEN 1 — STUDENT LOGIN
# ================================================================
class LoginScreen:
    """Centred login card with Student ID input and LOGIN button."""

    def __init__(self, parent: tk.Tk, on_login):
        """
        Parameters
        ----------
        parent : tk.Tk
            Root window.
        on_login : callable(roll_no: str)
            Callback invoked with the entered Student ID string.
        """
        self.parent = parent
        self.on_login = on_login
        self.frame = tk.Frame(parent, bg=COLORS["bg"])
        self.frame.pack(fill=tk.BOTH, expand=True)
        self._build()

    # ── layout ──────────────────────────────────────────────────
    def _build(self):
        # Centre wrapper
        centre = tk.Frame(self.frame, bg=COLORS["bg"])
        centre.place(relx=0.5, rely=0.5, anchor="center")

        # Card
        card = tk.Frame(
            centre, bg=COLORS["card_bg"],
            highlightbackground=COLORS["card_border"],
            highlightthickness=1, padx=50, pady=44,
        )
        card.pack()

        # ── App icon / logo area ────────────────────────────────
        icon_label = tk.Label(
            card, text="⌨", font=("Segoe UI Emoji", 36),
            bg=COLORS["card_bg"], fg=COLORS["accent"],
        )
        icon_label.pack(pady=(0, 6))

        # Title
        tk.Label(
            card, text="DTU Typewriter",
            font=("Segoe UI", 26, "bold"),
            bg=COLORS["card_bg"], fg=COLORS["white"],
        ).pack(pady=(0, 20))

        # Divider
        tk.Frame(card, bg=COLORS["divider"], height=1).pack(fill=tk.X, pady=(0, 20))

        # Label
        tk.Label(
            card, text="Student ID", font=("Segoe UI", 11),
            bg=COLORS["card_bg"], fg=COLORS["fg_muted"], anchor="w",
        ).pack(fill=tk.X, padx=4, pady=(0, 6))

        # Input
        self.roll_var = tk.StringVar()
        entry_frame = tk.Frame(
            card, bg=COLORS["input_border"],
            highlightbackground=COLORS["input_border"],
            highlightthickness=1,
        )
        entry_frame.pack(fill=tk.X, pady=(0, 8))
        self.entry = tk.Entry(
            entry_frame, textvariable=self.roll_var,
            font=("Segoe UI", 14), bg=COLORS["input_bg"],
            fg=COLORS["fg"], insertbackground=COLORS["accent"],
            relief=tk.FLAT, bd=0, highlightthickness=0,
        )
        self.entry.pack(fill=tk.X, ipady=10, padx=8)
        self.entry.focus_set()

        # Error label (hidden initially)
        self.error_var = tk.StringVar()
        self.error_label = tk.Label(
            card, textvariable=self.error_var,
            font=("Segoe UI", 10), bg=COLORS["card_bg"],
            fg=COLORS["error"], anchor="w",
        )
        self.error_label.pack(fill=tk.X, padx=4, pady=(0, 4))

        # Login button
        self.login_btn = tk.Button(
            card, text="LOGIN", font=("Segoe UI", 13, "bold"),
            bg=COLORS["accent"], fg=COLORS["white"],
            activebackground=COLORS["accent_hover"],
            activeforeground=COLORS["white"],
            relief=tk.FLAT, bd=0, cursor="hand2",
            command=self._handle_login,
        )
        self.login_btn.pack(fill=tk.X, ipady=11, pady=(12, 8))

        # Bind Enter key
        self.entry.bind("<Return>", lambda e: self._handle_login())

    # ── actions ─────────────────────────────────────────────────
    def _handle_login(self):
        roll = self.roll_var.get().strip()
        if not roll:
            self.show_error("Please enter your Student ID.")
            return
        self.error_var.set("")
        self.on_login(roll)

    def show_error(self, msg: str):
        self.error_var.set(msg)

    def destroy(self):
        self.frame.destroy()


# ================================================================
#  SCREEN 2 — INSTRUCTIONS
# ================================================================
class InstructionsScreen:
    """Displays 5 instructions, a demo snippet, and a PROCEED button."""

    def __init__(self, parent: tk.Tk, student_name: str, duration_sec: int,
                 on_proceed):
        self.parent = parent
        self.on_proceed = on_proceed
        self._proceed_clicked = False
        self.frame = tk.Frame(parent, bg=COLORS["bg"])
        self.frame.pack(fill=tk.BOTH, expand=True)
        self._build(student_name, duration_sec)

    def _build(self, student_name, duration_sec):
        # Scrollable wrapper
        canvas = tk.Canvas(self.frame, bg=COLORS["bg"], highlightthickness=0)
        scrollbar = tk.Scrollbar(self.frame, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=COLORS["bg"])

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Content container (centred, max-width)
        content = tk.Frame(scroll_frame, bg=COLORS["bg"])
        content.pack(fill=tk.X, expand=True, padx=60, pady=40)

        # Welcome
        tk.Label(
            content,
            text=f"Welcome, {student_name}!",
            font=("Segoe UI", 22, "bold"),
            bg=COLORS["bg"], fg=COLORS["white"], anchor="w",
        ).pack(fill=tk.X, pady=(0, 4))

        tk.Label(
            content, text="Please read the instructions carefully before proceeding.",
            font=("Segoe UI", 12), bg=COLORS["bg"], fg=COLORS["fg_muted"], anchor="w",
        ).pack(fill=tk.X, pady=(0, 28))

        # Title
        tk.Label(
            content, text="Typing Test Instructions",
            font=("Segoe UI", 18, "bold"),
            bg=COLORS["bg"], fg=COLORS["accent"], anchor="w",
        ).pack(fill=tk.X, pady=(0, 16))

        # Instructions card
        card = tk.Frame(content, bg=COLORS["card_bg"],
                        highlightbackground=COLORS["card_border"],
                        highlightthickness=1)
        card.pack(fill=tk.X, pady=(0, 24))

        instructions = [
            "A paragraph will be displayed on the screen. Type the paragraph exactly as shown.",
            f"The test has a fixed duration of {duration_sec} seconds configured in the settings.",
            "Correctly typed words and characters will be highlighted in green.",
            "Incorrectly typed characters will be highlighted in red. You must correct the mistake before continuing.",
            "Your typing speed, accuracy and total errors will be calculated after the test.",
        ]
        for i, text in enumerate(instructions, 1):
            row = tk.Frame(card, bg=COLORS["card_bg"])
            row.pack(fill=tk.X, padx=28, pady=(18 if i == 1 else 10, 10 if i < 5 else 18))

            # Number badge
            badge = tk.Label(
                row, text=str(i), font=("Segoe UI", 11, "bold"),
                bg=COLORS["accent"], fg=COLORS["white"],
                width=3, height=1,
            )
            badge.pack(side=tk.LEFT, padx=(0, 16))

            tk.Label(
                row, text=text, font=("Segoe UI", 12),
                bg=COLORS["card_bg"], fg=COLORS["fg"],
                anchor="w", wraplength=650, justify=tk.LEFT,
            ).pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Demo section
        tk.Label(
            content, text="Example Preview",
            font=("Segoe UI", 14, "bold"),
            bg=COLORS["bg"], fg=COLORS["fg"], anchor="w",
        ).pack(fill=tk.X, pady=(8, 10))

        demo_card = tk.Frame(content, bg=COLORS["card_bg"],
                             highlightbackground=COLORS["card_border"],
                             highlightthickness=1)
        demo_card.pack(fill=tk.X, pady=(0, 10))
        demo_inner = tk.Frame(demo_card, bg=COLORS["card_bg"])
        demo_inner.pack(fill=tk.X, padx=28, pady=20)

        # Demo text widget showing correct/incorrect coloring
        demo_text = tk.Text(
            demo_inner, font=("Consolas", 15), bg=COLORS["card_bg"],
            fg=COLORS["fg"], height=2, relief=tk.FLAT, bd=0,
            highlightthickness=0, wrap=tk.WORD, cursor="arrow",
            padx=4, pady=4,
        )
        demo_text.pack(fill=tk.X)

        demo_text.tag_configure("correct", foreground=COLORS["correct"])
        demo_text.tag_configure("incorrect", foreground=COLORS["error"], underline=True)
        demo_text.tag_configure("untyped", foreground=COLORS["neutral_fg"])

        demo_text.insert("end", "The quick ", "correct")
        demo_text.insert("end", "brwon", "incorrect")
        demo_text.insert("end", " fox jumps over the lazy dog.", "untyped")
        demo_text.config(state=tk.DISABLED)

        # Legend
        legend = tk.Frame(demo_inner, bg=COLORS["card_bg"])
        legend.pack(fill=tk.X, pady=(12, 0))
        for colour, label in [
            (COLORS["correct"], "Correct"),
            (COLORS["error"], "Incorrect"),
            (COLORS["neutral_fg"], "Not yet typed"),
        ]:
            dot = tk.Label(legend, text="●", font=("Segoe UI", 11),
                           bg=COLORS["card_bg"], fg=colour)
            dot.pack(side=tk.LEFT, padx=(0, 4))
            tk.Label(legend, text=label, font=("Segoe UI", 10),
                     bg=COLORS["card_bg"], fg=COLORS["fg_muted"]).pack(
                side=tk.LEFT, padx=(0, 20))

        # Proceed button
        self.proceed_btn = tk.Button(
            content, text="PROCEED  →", font=("Segoe UI", 14, "bold"),
            bg=COLORS["accent"], fg=COLORS["white"],
            activebackground=COLORS["accent_hover"],
            activeforeground=COLORS["white"],
            relief=tk.FLAT, bd=0, cursor="hand2",
            command=self._handle_proceed,
        )
        self.proceed_btn.pack(fill=tk.X, ipady=13, pady=(20, 8))

        # Bind mousewheel for scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        self._canvas = canvas
        self._mousewheel_handler = _on_mousewheel

    def _handle_proceed(self):
        if self._proceed_clicked:
            return
        self._proceed_clicked = True
        self.proceed_btn.config(state=tk.DISABLED, text="Loading…")
        self.on_proceed()

    def destroy(self):
        try:
            self._canvas.unbind_all("<MouseWheel>")
        except Exception:
            pass
        self.frame.destroy()


# ================================================================
#  SCREEN 3 — TYPING TEST
# ================================================================
class TypingTestScreen:
    """Reference paragraph at top, typing area below, START button, live stats."""

    def __init__(self, parent: tk.Tk, paragraph_title: str,
                 paragraph_content: str, duration_sec: int,
                 allow_backspace: bool,
                 on_test_complete):
        """
        Parameters
        ----------
        on_test_complete : callable(typed_text, elapsed_sec, error_count,
                                    correct_keystrokes, total_keystrokes)
        """
        self.parent = parent
        self.reference = paragraph_content
        self.duration_sec = duration_sec
        self.allow_backspace = allow_backspace
        self.on_test_complete = on_test_complete

        # Typing state
        self._cursor_pos = 0          # authoritative position in reference
        self._error_count = 0         # total incorrect keystrokes ever
        self._correct_keystrokes = 0  # correct keystrokes ever
        self._total_keystrokes = 0    # every character entry attempt
        self._is_error_locked = False
        self._remaining = duration_sec
        self._timer_id = None
        self._test_active = False
        self._test_started = False    # START button not yet clicked
        self._submitted = False
        self._start_time = None

        self.frame = tk.Frame(parent, bg=COLORS["bg"])
        self.frame.pack(fill=tk.BOTH, expand=True)
        self._build(paragraph_title)

    # ── build ───────────────────────────────────────────────────
    def _build(self, title):
        # ── Top bar (timer + stats) ─────────────────────────────
        top_bar = tk.Frame(self.frame, bg=COLORS["card_bg"], height=60)
        top_bar.pack(fill=tk.X)
        top_bar.pack_propagate(False)

        # Title
        tk.Label(
            top_bar, text=f"  ⌨  {title}",
            font=("Segoe UI", 14, "bold"),
            bg=COLORS["card_bg"], fg=COLORS["white"],
        ).pack(side=tk.LEFT, padx=(20, 0))

        # Timer (right side — WPM, accuracy, errors removed per request)
        timer_frame = tk.Frame(top_bar, bg=COLORS["card_bg"])
        timer_frame.pack(side=tk.RIGHT, padx=24)

        self.timer_var = tk.StringVar(value=self._format_time(self.duration_sec))
        tk.Label(
            timer_frame, text="⏱", font=("Segoe UI", 16),
            bg=COLORS["card_bg"], fg=COLORS["timer_fg"],
        ).pack(side=tk.LEFT, padx=(0, 8))
        self.timer_label = tk.Label(
            timer_frame, textvariable=self.timer_var,
            font=("Consolas", 20, "bold"),
            bg=COLORS["card_bg"], fg=COLORS["timer_fg"],
        )
        self.timer_label.pack(side=tk.LEFT)

        # ── Divider ─────────────────────────────────────────────
        tk.Frame(self.frame, bg=COLORS["divider"], height=1).pack(fill=tk.X)

        # ── Progress bar ────────────────────────────────────────
        self.progress_var = tk.DoubleVar(value=0.0)
        progress_bg = tk.Frame(self.frame, bg=COLORS["input_bg"], height=5)
        progress_bg.pack(fill=tk.X)
        progress_bg.pack_propagate(False)
        self.progress_fill = tk.Frame(progress_bg, bg=COLORS["accent"], height=5)
        self.progress_fill.place(relx=0, rely=0, relheight=1.0, relwidth=0.0)

        # ── Main content area ───────────────────────────────────
        main_area = tk.Frame(self.frame, bg=COLORS["bg"])
        main_area.pack(fill=tk.BOTH, expand=True, padx=24, pady=10)

        # ── BOTTOM BAR (Packed FIRST with side=BOTTOM so it is ALWAYS visible) ──
        self.bottom_bar = tk.Frame(main_area, bg=COLORS["bg"])
        self.bottom_bar.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 4))

        self.start_btn = tk.Button(
            self.bottom_bar,
            text="▶   START TYPING TEST",
            font=("Segoe UI", 15, "bold"),
            bg=COLORS["start_green"], fg=COLORS["white"],
            activebackground=COLORS["start_green_h"],
            activeforeground=COLORS["white"],
            relief=tk.FLAT, bd=0, cursor="hand2",
            command=self._on_start_clicked,
        )
        self.start_btn.pack(fill=tk.X, ipady=12)

        # ── Section A: Reference paragraph (Card directly) ──────
        ref_card = tk.Frame(
            main_area, bg=COLORS["ref_bg"],
            highlightbackground=COLORS["card_border"],
            highlightthickness=1,
        )
        ref_card.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=(4, 10))

        ref_scroll = tk.Scrollbar(ref_card, orient="vertical")
        ref_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.ref_text = tk.Text(
            ref_card, wrap=tk.WORD, height=6,
            font=("Consolas", 17), bg=COLORS["ref_bg"],
            fg=COLORS["neutral_fg"], relief=tk.FLAT, bd=0,
            highlightthickness=0, padx=20, pady=14,
            spacing1=5, spacing2=4, spacing3=5, cursor="arrow",
            yscrollcommand=ref_scroll.set,
        )
        self.ref_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ref_scroll.config(command=self.ref_text.yview)

        # Configure tags for reference text colouring
        self.ref_text.tag_configure("correct", foreground=COLORS["correct"])
        self.ref_text.tag_configure("incorrect", foreground=COLORS["error"],
                                    underline=True)
        self.ref_text.tag_configure("untyped", foreground=COLORS["neutral_fg"])
        self.ref_text.tag_configure("current", foreground=COLORS["white"],
                                    background="#1e3a8a", underline=True)

        # Insert reference text initially as "untyped"
        self.ref_text.insert("1.0", self.reference, "untyped")
        self.ref_text.config(state=tk.DISABLED)

        # ── Section B: Student typing area (Card directly) ──────
        self.type_card = tk.Frame(
            main_area, bg=COLORS["typing_bg"],
            highlightbackground=COLORS["card_border"],
            highlightthickness=2,
        )
        self.type_card.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=(0, 6))

        type_scroll = tk.Scrollbar(self.type_card, orient="vertical")
        type_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.type_text = tk.Text(
            self.type_card, wrap=tk.WORD, height=6,
            font=("Consolas", 17), bg=COLORS["typing_bg"],
            fg=COLORS["fg"], relief=tk.FLAT, bd=0,
            highlightthickness=0, padx=20, pady=14,
            spacing1=5, spacing2=4, spacing3=5,
            insertbackground=COLORS["accent"], insertwidth=3,
            yscrollcommand=type_scroll.set,
        )
        self.type_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        type_scroll.config(command=self.type_text.yview)

        # Configure tags for typed text colouring
        self.type_text.tag_configure("correct", foreground=COLORS["correct"])
        self.type_text.tag_configure("incorrect", foreground=COLORS["error"],
                                     background=COLORS["error_bg"], underline=True)

        # Initially disabled
        self.type_text.config(state=tk.DISABLED)

        # Bind key events on the type_text widget
        self.type_text.bind("<Key>", self._on_key)
        self.type_text.bind("<Button-1>", self._block_mouse)
        self.type_text.bind("<Button-2>", self._block_mouse)
        self.type_text.bind("<Button-3>", self._block_mouse)
        self.type_text.bind("<B1-Motion>", self._block_mouse)
        self.type_text.bind("<<Paste>>", lambda e: "break")
        self.type_text.bind("<<Cut>>", lambda e: "break")
        self.type_text.bind("<Control-v>", lambda e: "break")
        self.type_text.bind("<Control-V>", lambda e: "break")
        self.type_text.bind("<Control-a>", lambda e: "break")
        self.type_text.bind("<Control-x>", lambda e: "break")
        self.type_text.bind("<Control-z>", lambda e: "break")
        self.type_text.bind("<Control-y>", lambda e: "break")
        self.type_text.bind("<Shift-Insert>", lambda e: "break")

    # ── START button handler ────────────────────────────────────
    def _on_start_clicked(self):
        if self._test_started:
            return
        self._test_started = True

        # Hide start button
        self.start_btn.pack_forget()

        # Highlight typing box border
        self.type_card.config(highlightbackground=COLORS["accent"], highlightthickness=2)

        # Enable typing area, clear text, and focus cursor
        self.type_text.config(state=tk.NORMAL)
        self.type_text.delete("1.0", "end")
        self.type_text.focus_set()
        self.type_text.focus_force()
        self.type_text.mark_set("insert", "1.0")

        # Highlight the first character in reference
        self._update_ref_highlight()

        # Begin the test & timer
        self._start_test()

    # ── Block mouse repositioning ───────────────────────────────
    def _block_mouse(self, event):
        if not self._test_started:
            # If user clicks into writing space before clicking start, trigger start!
            self._on_start_clicked()
            return "break"
        if self._test_active:
            self.type_text.focus_set()
            self.type_text.mark_set("insert", "end-1c")
            self.type_text.see("end-1c")
        return "break"

    # ── Timer ───────────────────────────────────────────────────
    @staticmethod
    def _format_time(seconds):
        m, s = divmod(max(seconds, 0), 60)
        return f"{m:02d}:{s:02d}"

    def _start_test(self):
        self._test_active = True
        self._start_time = time.time()
        self._tick()

    def _tick(self):
        if not self._test_active:
            return
        elapsed = time.time() - self._start_time
        self._remaining = max(0, self.duration_sec - int(elapsed))
        self.timer_var.set(self._format_time(self._remaining))

        # Update live WPM & accuracy
        self._update_live_stats(elapsed)

        if self._remaining <= 0:
            self._finish_test()
            return
        self._timer_id = self.parent.after(200, self._tick)

    def _update_live_stats(self, elapsed):
        # Progress bar
        if len(self.reference) > 0 and hasattr(self, "progress_fill"):
            pct = min(1.0, self._cursor_pos / len(self.reference))
            self.progress_fill.place(relx=0, rely=0, relheight=1.0, relwidth=pct)

    # ── Key handling ────────────────────────────────────────────
    def _on_key(self, event):
        if not self._test_started:
            self._on_start_clicked()

        if not self._test_active:
            return "break"

        # Allow only regular characters and Backspace
        char = event.char
        keysym = event.keysym

        # Block navigation keys
        if keysym in ("Left", "Right", "Up", "Down", "Home", "End",
                      "Prior", "Next", "Delete", "Insert"):
            return "break"

        # Block Ctrl/Alt combinations (except backspace)
        if event.state & 0x4 or event.state & 0x20000:  # Ctrl or Alt
            return "break"

        # Handle Backspace
        if keysym == "BackSpace":
            return self._handle_backspace()

        # Handle Tab key
        if keysym == "Tab":
            return "break"

        # Handle Return/Enter — if reference has newline at position, allow
        if keysym == "Return" or keysym == "KP_Enter":
            if self._cursor_pos < len(self.reference):
                if self.reference[self._cursor_pos] == '\n':
                    char = '\n'
                else:
                    return "break"
            else:
                return "break"

        # Ignore non-printable
        if not char or len(char) != 1:
            if keysym not in ("BackSpace",):
                return "break"

        # If error-locked, only backspace allowed
        if self._is_error_locked:
            return "break"

        # Check if we've reached end of reference
        if self._cursor_pos >= len(self.reference):
            return "break"

        # ── Character validation ────────────────────────────────
        expected = self.reference[self._cursor_pos]
        self._total_keystrokes += 1

        if char == expected:
            # CORRECT
            self._correct_keystrokes += 1
            self.type_text.insert("end", char, "correct")
            self._cursor_pos += 1
            self._is_error_locked = False
        else:
            # INCORRECT
            self._error_count += 1
            # Display the wrong character in red
            self.type_text.insert("end", char, "incorrect")
            self._cursor_pos += 1
            self._is_error_locked = True

        # Update reference highlighting
        self._update_ref_highlight()

        # Force cursor to end
        self.type_text.mark_set("insert", "end-1c")
        self.type_text.see("end")

        # Check paragraph completion
        if self._cursor_pos >= len(self.reference) and not self._is_error_locked:
            self.parent.after(100, self._finish_test)

        return "break"

    def _handle_backspace(self):
        if self._cursor_pos <= 0:
            return "break"

        # If error-locked, always allow backspace to correct
        if self._is_error_locked:
            # Remove last character
            self.type_text.delete("end-2c", "end-1c")
            self._cursor_pos -= 1
            self._is_error_locked = False
            self._update_ref_highlight()
            self.type_text.mark_set("insert", "end-1c")
            return "break"

        # If backspace is allowed in settings, allow deleting correct chars
        if self.allow_backspace:
            self.type_text.delete("end-2c", "end-1c")
            self._cursor_pos -= 1
            self._update_ref_highlight()
            self.type_text.mark_set("insert", "end-1c")
            return "break"

        # Backspace not allowed in settings and not error-locked
        return "break"

    # ── Reference highlighting ──────────────────────────────────
    def _update_ref_highlight(self):
        self.ref_text.config(state=tk.NORMAL)

        # Remove all tags
        for tag in ("correct", "incorrect", "untyped", "current"):
            self.ref_text.tag_remove(tag, "1.0", "end")

        # Get typed text for comparison
        typed = self.type_text.get("1.0", "end-1c")

        # Colour character by character in reference
        for i in range(len(self.reference)):
            start_idx = f"1.0+{i}c"
            end_idx = f"1.0+{i + 1}c"

            if i < len(typed):
                if typed[i] == self.reference[i]:
                    self.ref_text.tag_add("correct", start_idx, end_idx)
                else:
                    self.ref_text.tag_add("incorrect", start_idx, end_idx)
            elif i == self._cursor_pos:
                self.ref_text.tag_add("current", start_idx, end_idx)
            else:
                self.ref_text.tag_add("untyped", start_idx, end_idx)

        # Keep current position in view
        if self._cursor_pos < len(self.reference):
            self.ref_text.see(f"1.0+{self._cursor_pos}c")

        self.ref_text.config(state=tk.DISABLED)

    # ── Test completion ─────────────────────────────────────────
    def _finish_test(self):
        if self._submitted:
            return
        self._submitted = True
        self._test_active = False

        if self._timer_id:
            self.parent.after_cancel(self._timer_id)
            self._timer_id = None

        # Disable typing
        self.type_text.config(state=tk.DISABLED)

        elapsed = time.time() - self._start_time if self._start_time else 0
        elapsed = max(1, int(elapsed))

        typed = self.type_text.get("1.0", "end-1c")

        self.on_test_complete(
            typed, elapsed, self._error_count,
            self._correct_keystrokes, self._total_keystrokes,
        )

    def get_typed_text(self):
        try:
            return self.type_text.get("1.0", "end-1c")
        except tk.TclError:
            return ""

    def destroy(self):
        if self._timer_id:
            self.parent.after_cancel(self._timer_id)
            self._timer_id = None
        self._test_active = False
        self.frame.destroy()


# ================================================================
#  SCREEN 4 — RESULTS DASHBOARD
# ================================================================
class ResultsScreen:
    """Typing test result dashboard with prominent metric cards."""

    def __init__(self, parent: tk.Tk, student_name: str, result: dict,
                 on_retake=None, on_instructions=None, on_close=None):
        """
        Parameters
        ----------
        result : dict
            Keys: wpm, accuracy, errors, time_taken, status
        on_retake : callable or None
            Callback to retake the test immediately with a new paragraph.
        on_instructions : callable or None
            Callback to go back to instructions screen.
        on_close : callable or None
            Callback to close the application.
        """
        self.parent = parent
        self.frame = tk.Frame(parent, bg=COLORS["bg"])
        self.frame.pack(fill=tk.BOTH, expand=True)
        self._build(student_name, result, on_retake, on_instructions, on_close)

    def _build(self, student_name, result, on_retake, on_instructions, on_close):
        # Centre container
        container = tk.Frame(self.frame, bg=COLORS["bg"])
        container.place(relx=0.5, rely=0.5, anchor="center")

        # Title
        tk.Label(
            container, text="Typing Test Completed",
            font=("Segoe UI", 28, "bold"),
            bg=COLORS["bg"], fg=COLORS["white"],
        ).pack(pady=(0, 6))

        # Student name
        tk.Label(
            container, text=f"Candidate: {student_name}",
            font=("Segoe UI", 13),
            bg=COLORS["bg"], fg=COLORS["fg_muted"],
        ).pack(pady=(0, 24))

        # ── Metric cards (Only WPM and Accuracy) ────────────────
        cards_frame = tk.Frame(container, bg=COLORS["bg"])
        cards_frame.pack(pady=(0, 28))

        wpm = result.get("wpm", 0)
        accuracy = result.get("accuracy", 0)

        row = tk.Frame(cards_frame, bg=COLORS["bg"])
        row.pack()

        self._metric_card(row, "WORDS PER MINUTE", f"{wpm:.1f}",
                          COLORS["correct"], side=tk.LEFT, width=280, height=150, val_size=38)
        self._metric_card(row, "ACCURACY", f"{accuracy:.1f}%",
                          COLORS["accent"], side=tk.LEFT, width=280, height=150, val_size=38)

        # ── Buttons row ─────────────────────────────────────────
        btn_frame = tk.Frame(container, bg=COLORS["bg"])
        btn_frame.pack(pady=(0, 8))

        # Retake Test button (prominent primary)
        if on_retake:
            tk.Button(
                btn_frame, text="🔄  RETAKE TEST",
                font=("Segoe UI", 13, "bold"),
                bg=COLORS["accent"], fg=COLORS["white"],
                activebackground=COLORS["accent_hover"],
                activeforeground=COLORS["white"],
                relief=tk.FLAT, bd=0, cursor="hand2",
                padx=36, pady=0,
                command=on_retake,
            ).pack(side=tk.LEFT, padx=8, ipady=12)

        # View Instructions button (secondary)
        if on_instructions:
            tk.Button(
                btn_frame, text="📋  INSTRUCTIONS",
                font=("Segoe UI", 11, "bold"),
                bg=COLORS["card_bg"], fg=COLORS["fg"],
                activebackground=COLORS["input_bg"],
                activeforeground=COLORS["white"],
                highlightbackground=COLORS["card_border"],
                highlightthickness=1,
                relief=tk.FLAT, bd=0, cursor="hand2",
                padx=24, pady=0,
                command=on_instructions,
            ).pack(side=tk.LEFT, padx=8, ipady=12)

        # Close/Exit button (muted)
        if on_close:
            tk.Button(
                btn_frame, text="🚪  EXIT",
                font=("Segoe UI", 11),
                bg=COLORS["card_bg"], fg=COLORS["fg_muted"],
                activebackground=COLORS["input_bg"],
                activeforeground=COLORS["fg"],
                relief=tk.FLAT, bd=0, cursor="hand2",
                padx=20, pady=0,
                command=on_close,
            ).pack(side=tk.LEFT, padx=8, ipady=12)

    def _metric_card(self, parent, label, value, color, side, width=180, height=110, val_size=26):
        card = tk.Frame(
            parent, bg=COLORS["card_bg"],
            highlightbackground=COLORS["card_border"],
            highlightthickness=1, width=width,
        )
        card.pack(side=side, padx=6)
        card.pack_propagate(False)
        card.config(height=height, width=width)

        tk.Label(
            card, text=label, font=("Segoe UI", 9, "bold"),
            bg=COLORS["card_bg"], fg=COLORS["fg_muted"],
        ).pack(pady=(16, 4))

        tk.Label(
            card, text=value, font=("Segoe UI", val_size, "bold"),
            bg=COLORS["card_bg"], fg=color,
        ).pack(pady=(0, 8))

    def destroy(self):
        self.frame.destroy()
