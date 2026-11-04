"""Modal dialogs: Find/Replace, About, Test Settings, Results table."""
import tkinter as tk
from tkinter import ttk, messagebox


class FindReplaceDialog:
    def __init__(self, parent, text_widget: tk.Text):
        self.tw = text_widget
        self.win = tk.Toplevel(parent)
        self.win.title("Find & Replace")
        self.win.geometry("420x165")
        self.win.resizable(False, False)
        self.win.transient(parent)
        self.win.grab_set()

        ttk.Label(self.win, text="Find:").grid(
            row=0, column=0, padx=10, pady=6, sticky="e"
        )
        self.find_var = tk.StringVar()
        ttk.Entry(self.win, textvariable=self.find_var, width=32).grid(
            row=0, column=1, padx=4
        )

        ttk.Label(self.win, text="Replace:").grid(
            row=1, column=0, padx=10, pady=6, sticky="e"
        )
        self.repl_var = tk.StringVar()
        ttk.Entry(self.win, textvariable=self.repl_var, width=32).grid(
            row=1, column=1, padx=4
        )

        bf = ttk.Frame(self.win)
        bf.grid(row=2, column=0, columnspan=2, pady=12)
        ttk.Button(bf, text="Find Next", command=self._find).pack(
            side=tk.LEFT, padx=4
        )
        ttk.Button(bf, text="Replace", command=self._replace).pack(
            side=tk.LEFT, padx=4
        )
        ttk.Button(bf, text="Replace All", command=self._replace_all).pack(
            side=tk.LEFT, padx=4
        )

    def _find(self):
        self.tw.tag_remove("found", "1.0", tk.END)
        q = self.find_var.get()
        if not q:
            return
        idx = self.tw.search(q, "insert+1c", nocase=True)
        if idx:
            end = idx + "+%dc" % len(q)
            self.tw.tag_add("found", idx, end)
            self.tw.tag_config("found", background="#4fc3f7", foreground="#000")
            self.tw.mark_set("insert", end)
            self.tw.see(idx)
        else:
            messagebox.showinfo("Find", "No more matches.", parent=self.win)

    def _replace(self):
        try:
            self.tw.selection_get()
        except tk.TclError:
            self._find()
            return
        self.tw.delete(tk.SEL_FIRST, tk.SEL_LAST)
        self.tw.insert(tk.INSERT, self.repl_var.get())
        self._find()

    def _replace_all(self):
        q = self.find_var.get()
        r = self.repl_var.get()
        if not q:
            return
        content = self.tw.get("1.0", tk.END)
        new = content.replace(q, r)
        self.tw.delete("1.0", tk.END)
        self.tw.insert("1.0", new)


class AboutDialog:
    def __init__(self, parent):
        messagebox.showinfo(
            "About DTU Typewriter",
            "DTU Typewriter  v1.0\n\n"
            "Developed for the Computer Centre\n"
            "Delhi Technological University\n\n"
            "A lightweight, offline typing-test\n"
            "desktop application for Windows.",
            parent=parent,
        )


class SettingsDialog:
    def __init__(self, parent, current: dict, on_save=None):
        self.on_save = on_save
        self.win = tk.Toplevel(parent)
        self.win.title("Test Settings")
        self.win.geometry("350x190")
        self.win.resizable(False, False)
        self.win.transient(parent)
        self.win.grab_set()

        ttk.Label(self.win, text="Duration (seconds):").grid(
            row=0, column=0, padx=12, pady=10, sticky="e"
        )
        self.dur = tk.IntVar(value=current.get("duration_sec", 60))
        ttk.Spinbox(
            self.win, from_=10, to=600, textvariable=self.dur, width=8
        ).grid(row=0, column=1, padx=8)

        self.bs = tk.BooleanVar(
            value=current.get("allow_backspace", True)
        )
        ttk.Checkbutton(
            self.win, text="Allow backspace", variable=self.bs
        ).grid(row=1, column=0, columnspan=2, padx=12, pady=8)

        ttk.Button(self.win, text="Save", command=self._save).grid(
            row=2, column=0, columnspan=2, pady=14
        )

    def _save(self):
        if self.on_save:
            self.on_save(self.dur.get(), int(self.bs.get()))
        self.win.destroy()


class ResultsDialog:
    def __init__(self, parent, results: list):
        self.win = tk.Toplevel(parent)
        self.win.title("Your Results")
        self.win.geometry("640x340")
        self.win.transient(parent)
        self.win.grab_set()

        cols = ("WPM", "Accuracy", "Errors", "Time (s)", "Date")
        tree = ttk.Treeview(
            self.win, columns=cols, show="headings", height=12
        )
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=120, anchor="center")
        for r in results:
            tree.insert(
                "",
                tk.END,
                values=(
                    f"{r['wpm']:.1f}",
                    f"{r['accuracy']:.1f}%",
                    r["errors"],
                    r["time_taken"],
                    r.get("submitted_at", ""),
                ),
            )
        tree.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        ttk.Button(self.win, text="Close", command=self.win.destroy).pack(
            pady=6
        )
