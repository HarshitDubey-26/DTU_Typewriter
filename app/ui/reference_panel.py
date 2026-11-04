"""Read-only panel that shows the paragraph the student must type."""
import tkinter as tk


class ReferencePanel:
    def __init__(self, parent):
        self.frame = tk.Frame(parent, bd=0, highlightthickness=0)
        # Initially hidden; shown when a test starts
        self.label = tk.Label(
            self.frame,
            text="Reference Paragraph",
            font=("Segoe UI", 10, "bold"),
            anchor="w",
            padx=12,
            pady=4,
        )
        self.label.pack(fill=tk.X)
        self.text = tk.Text(
            self.frame,
            wrap=tk.WORD,
            font=("Consolas", 13),
            height=6,
            padx=20,
            pady=12,
            relief=tk.FLAT,
            borderwidth=0,
            highlightthickness=0,
            state=tk.DISABLED,
            cursor="arrow",
        )
        self.text.pack(fill=tk.X, padx=0, pady=(0, 2))

    def show(self, title: str, content: str):
        self.frame.pack(fill=tk.X, before=self.frame.master.winfo_children()[-1])
        self.label.config(text="Reference:  " + title)
        self.text.config(state=tk.NORMAL)
        self.text.delete("1.0", tk.END)
        self.text.insert("1.0", content)
        self.text.config(state=tk.DISABLED)

    def hide(self):
        self.frame.pack_forget()

    def apply_theme(self, theme: dict):
        self.frame.config(bg=theme["bg"])
        self.label.config(bg=theme["bg"], fg=theme["accent"])
        self.text.config(bg=theme["ref_bg"], fg=theme["ref_fg"])
