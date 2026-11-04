import logging
import os
from pathlib import Path
from tkinter import Tk

from app.utils.logger import get_logger
from app.core.controller import AppController

def main() -> None:
    """Application entry point.

    Sets up logging, creates the Tk root window, starts the controller, and
    runs the Tkinter main loop.
    """
    logger = get_logger()
    logger.info("DTU Typewriter starting")

    root = Tk()
    root.title("DTU Typewriter")
    # Icon will be set later when assets are added

    # Initialise the application controller (creates DB worker, UI, etc.)
    controller = AppController(root)
    controller.start()

    try:
        root.mainloop()
    finally:
        logger.info("DTU Typewriter shutting down")
        controller.shutdown()

if __name__ == "__main__":
    main()
