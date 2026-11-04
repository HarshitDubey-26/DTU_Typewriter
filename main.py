"""
DTU Typewriter — Entry Point
============================
A lightweight, offline typing-test desktop application
for Delhi Technological University.

Usage:
    python main.py
"""
import sys
import tkinter as tk
from app.utils.logger import get_logger
from app.core.controller import AppController


def main() -> None:
    logger = get_logger()
    logger.info("DTU Typewriter starting  (Python %s)", sys.version)

    root = tk.Tk()
    root.title("DTU Typewriter")

    # Set a default window icon (will use custom .ico when available)
    try:
        root.iconbitmap(default="")
    except tk.TclError:
        pass

    controller = AppController(root)
    controller.start()

    try:
        root.mainloop()
    except KeyboardInterrupt:
        pass
    finally:
        logger.info("DTU Typewriter shut down")


if __name__ == "__main__":
    main()
