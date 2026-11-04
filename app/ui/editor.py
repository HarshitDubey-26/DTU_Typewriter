"""Typing editor — wraps a tk.Text widget with theme & event support."""
import tkinter as tk


class Editor:
    def __init__(self, parent, on_change=None):
        self.on_change = on_change
        self.parent = parent

        # Container frame
        self.frame = tk.Frame(parent, bd=0, highlightthickness=0)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        # Scrollbar
        self.scrollbar = tk.Scrollbar(self.frame, width=12)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Text widget
        self.text = tk.Text(
            self.frame,
            wrap=tk.WORD,
            undo=True,
            maxundo=-1,
            font=("Consolas", 14),
            insertwidth=3,
            padx=24,
            pady=18,
            spacing1=4,
            spacing3=4,
            relief=tk.FLAT,
            borderwidth=0,
            highlightthickness=0,
        )
        self.text.pack(fill=tk.BOTH, expand=True)
        self.text.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.text.yview)

        self.text.bind("<<Modified>>", self._on_modified)
        self.text.bind("<Control-a>", self._select_all)

    def _on_modified(self, event=None):
        if self.text.edit_modified():
            if self.on_change:
                self.on_change()
            self.text.edit_modified(False)

    def _select_all(self, event=None):
        self.text.tag_add(tk.SEL, "1.0", tk.END)
        return "break"

    def get_text(self) -> str:
        return self.text.get("1.0", "end-1c")

    def set_text(self, content: str):
        state = str(self.text.cget("state"))
        self.text.config(state=tk.NORMAL)
        self.text.delete("1.0", tk.END)
        if content:
            self.text.insert("1.0", content)
        self.text.edit_modified(False)
        self.text.edit_reset()
        if state == "disabled":
            self.text.config(state=tk.DISABLED)

    def set_font(self, family: str, size: int):
        self.text.configure(font=(family, size))

    def set_readonly(self, readonly: bool):
        self.text.config(
            state=tk.DISABLED if readonly else tk.NORMAL
        )

    def apply_theme(self, theme: dict):
        self.text.config(
            bg=theme["bg"],
            fg=theme["fg"],
            insertbackground=theme["cursor"],
            selectbackground=theme["select_bg"],
        )
        self.frame.config(bg=theme["bg"])
        self.scrollbar.config(
            bg=theme.get("toolbar_bg", "#222"),
            troughcolor=theme["bg"],
        )

    def focus(self):
        self.text.focus_set()
