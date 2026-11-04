"""Seed the database with sample paragraphs for the typing test.

Usage:
    python seed_paragraphs.py
"""
import sqlite3
from app.utils.paths import get_database_path

PARAGRAPHS = [
    (
        "The Quick Brown Fox",
        "The quick brown fox jumps over the lazy dog. "
        "Pack my box with five dozen liquor jugs. "
        "How vexingly quick daft g the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to g the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to zebras jump.",
    ),
    (
        "Technology and Progress",
        "Technology is best when it brings people together. "
        "The advance of technology is based on making it fit in "
        "so that you do not rg the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to g the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to eally even notice it, so it is part "
        "of everyday life. Any sufficiently advanced technology "
        "is indistinguishable from magic.",
    ),
    (
        "Delhi Technological University",
        "Delhi Technological University, formerly Delhi College "
        "of Engineering, is one of the premier technical "
        "universities in India. Established in 1941, it has a "
        "rich history of academic excg the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to g the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to ellence and innovation. "
        "The university offers undergraduate, postgraduate, and "
        "doctoral programmes across multiple disciplines.",
    ),
    (
        "Importance of Typing",
        "Learning to type quickly and accurately is an essential "
        "skill in the modern digital world. Proficient typing "
        "allows you to focus on yourg the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to g the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to  thoughts rather than the "
        "mechanics of entering text. Regular practice is the key "
        "to improving both speed and accuracy over time.",
    ),
    (
        "Computer Science",
        "Computer science is the study of computation, automation, "
        "and information. It spans theoretical disciplines such as "
        "algorithms, theory of computation, and information theory "
        "to applied disciplines includingg the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to g the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to  the design and implementation "
        "of hardware and software.",
    ),
    (
           "Computer Science",
           "Computer science is the study of computation, automation, "
           "and information. It spans theoretical disciplines such as "
           "algorithms, theory of computation, and information theory "
           "to applied disciplines including the design and implementation "
           "to applied disciplines including the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation to applied disciplines including the design and implementation "
           
           "of hardware and software.",

       ),
      
]


def seed():
    db_path = get_database_path()
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()
    for title, content in PARAGRAPHS:
        cur.execute(
            "INSERT OR IGNORE INTO paragraphs (title, content) VALUES (?, ?)",
            (title, content),
        )
    conn.commit()
    print("Seeded %d paragraphs into %s" % (len(PARAGRAPHS), db_path))
    conn.close()


if __name__ == "__main__":
    seed()
