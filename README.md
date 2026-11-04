# DTU Typewriter

A lightweight, offline typing-test desktop application developed for the
**Computer Centre, Delhi Technological University (DTU)**.

---

## Features

| Feature | Description |
|---------|-------------|
| **Student Login / Register** | Roll-number-based authentication stored locally in SQLite |
| **Timed Typing Test** | Configurable duration, random paragraph selection |
| **Live Stats** | Real-time word count, character count, countdown timer |
| **Auto-Save Drafts** | Debounced draft saving every 3 seconds of inactivity |
| **Draft Recovery** | Recover unsaved work after a crash or unexpected shutdown |
| **Results** | WPM, accuracy, error count stored per student |
| **Dark / Light Theme** | Toggle with a single click; preference persisted |
| **Database Backup** | One-click backup using SQLite's `backup` API |
| **Fully Offline** | No internet, no cloud, no external APIs |
| **Standalone EXE** | PyInstaller one-dir bundle; no Python required on target |
| **Windows Installer** | Inno Setup installer with shortcuts and uninstaller |

---

## Quick Start (from source)

```bash
# 1. Navigate to the project
cd  DTU-Typewriter

# 2. (Optional) create a virtual environment
python -m venv venv
venv\Scripts\activate

# 3. Install dev dependencies
pip install -r requirements.txt

# 4. Seed sample paragraphs into the database
python seed_paragraphs.py

# 5. Run the application
python main.py

# 6. Run tests
python -m pytest tests/ -v
```

### First-time usage

1. Launch with `python main.py`.
2. Click **Login** and **Register** a new account (roll no, password, name, email).
3. Log in with your credentials.
4. Click **Start Test** — a reference paragraph appears at the top.
5. Type the paragraph in the editor below before the timer runs out.
6. Click **Submit** (or wait for auto-submit when time expires).
7. Click **Results** to see your WPM, accuracy, and error count.

---

## Architecture

```
main.py                    Entry point
create_database.py         Standalone DB creation helper
seed_paragraphs.py         Seed sample paragraphs
schema.sql                 SQLite schema (source of truth)

app/
  core/
    controller.py          Coordinates UI <-> services <-> DB worker
  database/
    db_connection.py       Thread-local SQLite connection manager
    db_operations.py       Repository layer (one method per operation)
  workers/
    db_worker.py           Background thread processing DB tasks
    task_queue.py          DBTask / Result dataclasses
  services/
    autosave.py            Debounced draft auto-save
    recovery.py            Draft recovery on startup
    settings.py            UI preferences (JSON)
  ui/
    main_window.py         Tkinter root window, menus, status bar
    editor.py              Text widget wrapper
    reference_panel.py     Read-only paragraph display
    toolbar.py             Quick-access button bar
    dialogs.py             Find/Replace, About, Settings, Results
    themes.py              Dark / light colour palettes
  utils/
    paths.py               %LOCALAPPDATA% helpers
    logger.py              Rotating file logger
    helpers.py              Word count, WPM, accuracy calculations

tests/
  test_db.py               14 pytest tests covering every DB operation

installers/
  dtu_typewriter.iss       Inno Setup installer script

DTUTypewriter.spec         PyInstaller spec file
```

---

## Database

The SQLite database is stored at:

```
%LOCALAPPDATA%\DTUTypewriter\dtu_typewriter.db
```

It is created automatically on first launch using `schema.sql`.
User data is **never** stored inside the installation directory.

### Tables

| Table | Purpose |
|-------|---------|
| `students` | Roll no, name, email, password, has_attempted flag |
| `paragraphs` | Typing-test paragraphs (title, content, is_active) |
| `settings` | Test duration, allow-backspace toggle |
| `typing_drafts` | Auto-saved in-progress work |
| `results` | WPM, accuracy, errors, time_taken per attempt |

---

## Building the Executable

```bash
pip install pyinstaller
pyinstaller DTUTypewriter.spec
```

Output: `dist/DTUTypewriter/DTUTypewriter.exe`

Test by running the EXE on a machine **without Python installed**.

---

## Building the Installer

1. Install [Inno Setup](https://jrsoftware.org/isdl.php).
2. Build the PyInstaller bundle first (see above).
3. Compile the installer:

```bash
iscc installers\dtu_typewriter.iss
```

Output: `dist/DTUTypewriterSetup.exe`

---

## Testing

```bash
python -m pytest tests/ -v
```

All tests use temporary databases and never touch user data.

---

## Data Safety

- User data survives application **upgrades** and **reinstalls**.
- The **uninstaller** does NOT delete `%LOCALAPPDATA%\DTUTypewriter`.
- Use the **Backup DB** button to create timestamped backups under
  `%LOCALAPPDATA%\DTUTypewriter\backups\`.

---

## Technology Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.10+ |
| GUI | Tkinter + ttk |
| Database | SQLite 3 (stdlib `sqlite3`) |
| Threading | `threading` + `queue.Queue` |
| Logging | `logging` (RotatingFileHandler) |
| Testing | pytest |
| Packaging | PyInstaller (one-dir) |
| Installer | Inno Setup |

---

## License

Internal project — Delhi Technological University Computer Centre.
