"""Top toolbar with quick-access buttons."""
import tkinter as tk
from tkinter import ttk


class Toolbar:
    def __init__(self, parent, controller):
        self.controller = controller
        self.frame = tk.Frame(parent, bd=0, highlightthickness=0)
        self.frame.pack(fill=tk.X)
        self.buttons = []

        defs = [
            ("\U0001F464  Login",       controller.show_login),
            ("\u25B6  Start Test",  controller.start_test),
            ("\u2713  Submit",      controller.submit_test),
            ("\U0001F4CA  Results",     controller.show_results),
            ("\u2699  Settings",    controller.show_settings),
            ("\U0001F4BE  Backup DB",   controller.backup_db),
            ("\U0001F3A8  Theme",       controller.toggle_theme),
        ]
        for text, cmd in defs:
            b = tk.Button(
                self.frame,
                text=text,
                command=cmd,
                relief=tk.FLAT,
                bd=0,
                padx=10,
                pady=5,
                font=("Segoe UI", 9),
                cursor="hand2",
            )
            b.pack(side=tk.LEFT, padx=2, pady=3)
            self.buttons.append(b)

    def apply_theme(self, theme: dict):
        self.frame.config(bg=theme["toolbar_bg"])
        for b in self.buttons:
            b.config(
                bg=theme["toolbar_bg"],
                fg=theme["fg"],
                activebackground=theme["select_bg"],
                activeforeground=theme["fg"],
            )

    def show(self):
        self.frame.pack(fill=tk.X)

    def hide(self):
        self.frame.pack_forget()
