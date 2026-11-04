"""Main application window — assembles all UI components."""
import tkinter as tk
from tkinter import ttk, messagebox
from app.ui.editor import Editor
from app.ui.toolbar import Toolbar
from app.ui.reference_panel import ReferencePanel
from app.ui.dialogs import FindReplaceDialog, AboutDialog
from app.ui.themes import get_theme


class MainWindow:
    def __init__(self, root: tk.Tk, controller):
        self.root = root
        self.controller = controller
        self.editor = None
        self.toolbar = None
        self.ref_panel = None
        self.status_labels = {}

    # ── build ───────────────────────────────────────────────────
    def setup(self):
        self.root.geometry("1000x680")
        self.root.minsize(760, 500)

        self._create_menu()
        self.toolbar = Toolbar(self.root, self.controller)
        self.ref_panel = ReferencePanel(self.root)
        self.editor = Editor(
            self.root, on_change=self.controller.on_text_changed
        )
        self._create_status_bar()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        # Apply theme after all widgets exist
        self.refresh_theme()
        self.editor.set_readonly(True)
        self.update_status("status", "Ready  |  Please log in to start")

    # ── menu bar ────────────────────────────────────────────────
    def _create_menu(self):
        mb = tk.Menu(self.root)

        # File
        fm = tk.Menu(mb, tearoff=0)
        fm.add_command(label="Login / Register", command=self.controller.show_login)
        fm.add_command(label="Start Test", command=self.controller.start_test)
        fm.add_command(label="Submit Test", command=self.controller.submit_test)
        fm.add_separator()
        fm.add_command(label="Backup Database", command=self.controller.backup_db)
        fm.add_separator()
        fm.add_command(label="Exit", accelerator="Alt+F4", command=self._on_close)
        mb.add_cascade(label="File", menu=fm)

        # Edit
        em = tk.Menu(mb, tearoff=0)
        em.add_command(label="Undo", accelerator="Ctrl+Z",
                       command=lambda: self._safe(self.editor.text.edit_undo))
        em.add_command(label="Redo", accelerator="Ctrl+Y",
                       command=lambda: self._safe(self.editor.text.edit_redo))
        em.add_separator()
        em.add_command(label="Cut", accelerator="Ctrl+X",
                       command=lambda: self.root.focus_get().event_generate("<<Cut>>"))
        em.add_command(label="Copy", accelerator="Ctrl+C",
                       command=lambda: self.root.focus_get().event_generate("<<Copy>>"))
        em.add_command(label="Paste", accelerator="Ctrl+V",
                       command=lambda: self.root.focus_get().event_generate("<<Paste>>"))
        em.add_separator()
        em.add_command(label="Select All", accelerator="Ctrl+A",
                       command=lambda: self.editor._select_all())
        em.add_command(label="Find & Replace", accelerator="Ctrl+H",
                       command=self._show_find_replace)
        mb.add_cascade(label="Edit", menu=em)

        # View
        vm = tk.Menu(mb, tearoff=0)
        vm.add_command(label="Toggle Theme", command=self.controller.toggle_theme)
        vm.add_command(label="Toggle Toolbar", command=self._toggle_toolbar)
        vm.add_command(label="Full Screen", accelerator="F11",
                       command=self._toggle_fullscreen)
        mb.add_cascade(label="View", menu=vm)

        # Format
        fom = tk.Menu(mb, tearoff=0)
        fom.add_command(label="Increase Font  (Ctrl++)",
                        command=lambda: self.controller.change_font_size(2))
        fom.add_command(label="Decrease Font  (Ctrl+-)",
                        command=lambda: self.controller.change_font_size(-2))
        mb.add_cascade(label="Format", menu=fom)

        # Help
        hm = tk.Menu(mb, tearoff=0)
        hm.add_command(label="About", command=lambda: AboutDialog(self.root))
        mb.add_cascade(label="Help", menu=hm)

        self.root.config(menu=mb)

        # Global key bindings
        self.root.bind("<F11>", lambda e: self._toggle_fullscreen())
        self.root.bind("<Control-h>", lambda e: self._show_find_replace())
        self.root.bind("<Control-plus>", lambda e: self.controller.change_font_size(2))
        self.root.bind("<Control-minus>", lambda e: self.controller.change_font_size(-2))
        self.root.bind("<Control-equal>", lambda e: self.controller.change_font_size(2))

    # ── status bar ──────────────────────────────────────────────
    def _create_status_bar(self):
        bar = tk.Frame(self.root, bd=0, highlightthickness=0, height=28)
        bar.pack(side=tk.BOTTOM, fill=tk.X)
        self._status_bar = bar

        for key in ("student", "timer", "words", "chars", "status"):
            lbl = tk.Label(
                bar, text="", font=("Segoe UI", 9), padx=12, pady=3, anchor="w",
            )
            lbl.pack(side=tk.LEFT)
            self.status_labels[key] = lbl

    def update_status(self, key: str, text: str):
        lbl = self.status_labels.get(key)
        if lbl:
            lbl.config(text=text)

    # ── theme ───────────────────────────────────────────────────
    def refresh_theme(self):
        name = self.controller.ui_settings.get("theme", "dark")
        t = get_theme(name)
        self.root.configure(bg=t["bg"])
        if self.toolbar:
            self.toolbar.apply_theme(t)
        if self.ref_panel:
            self.ref_panel.apply_theme(t)
        if self.editor:
            self.editor.apply_theme(t)
        if hasattr(self, "_status_bar"):
            self._status_bar.config(bg=t["status_bg"])
            for lbl in self.status_labels.values():
                lbl.config(bg=t["status_bg"], fg=t["status_fg"])

    # ── helpers ─────────────────────────────────────────────────
    def _safe(self, fn):
        try:
            fn()
        except tk.TclError:
            pass

    def _show_find_replace(self):
        if self.editor:
            FindReplaceDialog(self.root, self.editor.text)

    def _toggle_toolbar(self):
        if self.toolbar.frame.winfo_viewable():
            self.toolbar.hide()
        else:
            self.toolbar.show()

    def _toggle_fullscreen(self):
        fs = self.root.attributes("-fullscreen")
        self.root.attributes("-fullscreen", not fs)

    def _on_close(self):
        if self.controller.test_running:
            if not messagebox.askyesno(
                "Quit?",
                "A test is in progress. Your draft will be saved.\n"
                "Are you sure you want to quit?",
                parent=self.root,
            ):
                return
            self.controller.autosave_now()
        self.controller.shutdown()
        self.root.destroy()

    def show_message(self, title: str, msg: str):
        messagebox.showinfo(title, msg, parent=self.root)

    def show_error(self, title: str, msg: str):
        messagebox.showerror(title, msg, parent=self.root)

    def handle_worker_result(self, result):
        pass
