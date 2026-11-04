-- ==========================================
-- DTU TYPEWRITER - SQLITE3 DATABASE SCHEMA
-- ==========================================

PRAGMA foreign_keys = ON;

-- 1. STUDENTS TABLE
CREATE TABLE IF NOT EXISTS students (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    roll_no         TEXT NOT NULL UNIQUE,
    name            TEXT NOT NULL,
    email           TEXT NOT NULL,
    password        TEXT NOT NULL,
    has_attempted   INTEGER NOT NULL DEFAULT 0
                    CHECK (has_attempted IN (0, 1))
);

-- 2. PARAGRAPHS TABLE
CREATE TABLE IF NOT EXISTS paragraphs (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    title           TEXT NOT NULL,
    content         TEXT NOT NULL,
    is_active       INTEGER NOT NULL DEFAULT 1
                    CHECK (is_active IN (0, 1))
);

-- 3. SETTINGS TABLE
CREATE TABLE IF NOT EXISTS settings (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    duration_sec    INTEGER NOT NULL DEFAULT 60
                    CHECK (duration_sec > 0),
    allow_backspace INTEGER NOT NULL DEFAULT 1
                    CHECK (allow_backspace IN (0, 1))
);

-- 4. TYPING DRAFTS TABLE
CREATE TABLE IF NOT EXISTS typing_drafts (
    student_id        INTEGER PRIMARY KEY,
    paragraph_id      INTEGER NOT NULL,
    typed_text        TEXT NOT NULL DEFAULT '',
    remaining_seconds INTEGER NOT NULL DEFAULT 0
                      CHECK (remaining_seconds >= 0),
    errors            INTEGER NOT NULL DEFAULT 0
                      CHECK (errors >= 0),
    updated_at        TEXT NOT NULL DEFAULT
                      (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    FOREIGN KEY (student_id)
        REFERENCES students(id)
        ON DELETE CASCADE,
    FOREIGN KEY (paragraph_id)
        REFERENCES paragraphs(id)
);

-- 5. RESULTS TABLE
CREATE TABLE IF NOT EXISTS results (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id      INTEGER NOT NULL,
    paragraph_id    INTEGER NOT NULL,
    wpm             REAL NOT NULL DEFAULT 0
                    CHECK (wpm >= 0),
    accuracy        REAL NOT NULL DEFAULT 0
                    CHECK (accuracy >= 0 AND accuracy <= 100),
    errors          INTEGER NOT NULL DEFAULT 0
                    CHECK (errors >= 0),
    time_taken      INTEGER NOT NULL DEFAULT 0
                    CHECK (time_taken >= 0),
    submitted_at    TEXT NOT NULL DEFAULT
                    (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    FOREIGN KEY (student_id)
        REFERENCES students(id)
        ON DELETE CASCADE,
    FOREIGN KEY (paragraph_id)
        REFERENCES paragraphs(id)
);

-- ==========================================
-- INDEXES
-- ==========================================
CREATE INDEX IF NOT EXISTS idx_results_student ON results(student_id);
CREATE INDEX IF NOT EXISTS idx_results_submitted ON results(submitted_at);
CREATE INDEX IF NOT EXISTS idx_results_paragraph ON results(paragraph_id);
CREATE INDEX IF NOT EXISTS idx_paragraphs_active ON paragraphs(is_active);

-- ==========================================
-- DEFAULT SETTINGS
-- ==========================================
INSERT OR IGNORE INTO settings (id, duration_sec, allow_backspace) VALUES (1, 60, 1);

-- ==========================================
-- DEFAULT STUDENTS
-- ==========================================
INSERT OR IGNORE INTO students (id, roll_no, name, email, password) VALUES
(1, 'DTU2024001', 'Aarti Sharma', 'aarti@dtu.ac.in', 'pass'),
(2, '2K21/CO/001', 'Test Student', 'student@dtu.ac.in', 'pass'),
(3, '2K21/CO/002', 'Aman Verma', 'aman@dtu.ac.in', 'pass'),
(4, 'STUDENT01', 'Demo Candidate', 'demo@dtu.ac.in', 'pass');

-- ==========================================
-- DEFAULT PARAGRAPHS
-- ==========================================
INSERT OR IGNORE INTO paragraphs (id, title, content, is_active) VALUES
(1, 'The Quick Brown Fox', 'The quick brown fox jumps over the lazy dog. Pack my box with five dozen liquor jugs. How vexingly quick daft zebras jump.', 1),
(2, 'Technology and Progress', 'Technology is best when it brings people together. The advance of technology is based on making it fit in so that you do not really even notice it, so it is part of everyday life. Any sufficiently advanced technology is indistinguishable from magic.', 1),
(3, 'Delhi Technological University', 'Delhi Technological University, formerly Delhi College of Engineering, is one of the premier technical universities in India. Established in 1941, it has a rich history of academic excellence and innovation. The university offers undergraduate, postgraduate, and doctoral programmes across multiple disciplines.', 1),
(4, 'Importance of Typing', 'Learning to type quickly and accurately is an essential skill in the modern digital world. Proficient typing allows you to focus on your thoughts rather than the mechanics of entering text. Regular practice is the key to improving both speed and accuracy over time.', 1),
(5, 'Computer Science', 'Computer science is the study of computation, automation, and information. It spans theoretical disciplines such as algorithms, theory of computation, and information theory to applied disciplines including the design and implementation of hardware and software.', 1);

-- ==========================================
-- AUTOMATIC ATTEMPT TRACKING
-- ==========================================
CREATE TRIGGER IF NOT EXISTS trg_student_attempted
AFTER INSERT ON results
BEGIN
    UPDATE students
    SET has_attempted = 1
    WHERE id = NEW.student_id;
END;
