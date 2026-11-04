"""Centralised path helpers.

All user data lives under  %LOCALAPPDATA%\\DTUTypewriter  so that the
application can be installed in Program Files without write-permission
issues and user data survives upgrades / reinstalls.
"""
import os
import sys
from pathlib import Path


def get_local_appdata_dir() -> Path:
    local = os.getenv("LOCALAPPDATA")
    if not local:
        local = str(Path.home() / "AppData" / "Local")
    base = Path(local) / "DTUTypewriter"
    base.mkdir(parents=True, exist_ok=True)
    return base


def get_database_path() -> Path:
    return get_local_appdata_dir() / "dtu_typewriter.db"


def get_backup_dir() -> Path:
    d = get_local_appdata_dir() / "backups"
    d.mkdir(parents=True, exist_ok=True)
    return d


def get_schema_path() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / "schema.sql"
    return Path(__file__).resolve().parents[2] / "schema.sql"
