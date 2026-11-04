"""Standalone script to create / verify the SQLite database.

Usage:
    python create_database.py
"""
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
SCHEMA_FILE = BASE_DIR / "schema.sql"
DATABASE_FILE = BASE_DIR / "dtu_typewriter.db"


def create_database():
    if not SCHEMA_FILE.exists():
        raise FileNotFoundError("Schema file not found: " + str(SCHEMA_FILE))

    if DATABASE_FILE.exists():
        print("Database already exists!")
        print("Location:", DATABASE_FILE)
        return

    connection = None
    try:
        schema = SCHEMA_FILE.read_text(encoding="utf-8")
        connection = sqlite3.connect(DATABASE_FILE)
        connection.execute("PRAGMA foreign_keys = ON")
        connection.executescript(schema)
        connection.commit()

        cursor = connection.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type='table' AND name NOT LIKE 'sqlite_%' "
            "ORDER BY name"
        )
        tables = cursor.fetchall()
        print("\nDTU Typewriter Database Created Successfully!")
        print("\nTables Created:")
        for t in tables:
            print("  -", t[0])

        result = connection.execute("PRAGMA integrity_check").fetchone()
        print("\nDatabase Integrity:", result[0])
        print("\nDatabase Location:", DATABASE_FILE)

    except sqlite3.Error as error:
        print("Database Error:", error)
        if connection:
            connection.rollback()
        if DATABASE_FILE.exists():
            if connection:
                connection.close()
                connection = None
            DATABASE_FILE.unlink()
    finally:
        if connection:
            connection.close()


if __name__ == "__main__":
    create_database()
