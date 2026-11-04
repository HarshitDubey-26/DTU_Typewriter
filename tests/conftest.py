import os
import sys
import tkinter as tk
import pytest
from pathlib import Path

# Ensure Tcl/Tk paths are configured for Tkinter in tests
tcl_dir = Path(sys.base_prefix) / "tcl"
if tcl_dir.exists():
    for sub in tcl_dir.iterdir():
        if sub.is_dir():
            if sub.name.startswith("tcl8."):
                os.environ.setdefault("TCL_LIBRARY", str(sub))
            elif sub.name.startswith("tk8."):
                os.environ.setdefault("TK_LIBRARY", str(sub))


@pytest.fixture(scope="session")
def root():
    r = tk.Tk()
    r.geometry("1060x720")
    yield r
    try:
        r.destroy()
    except Exception:
        pass
