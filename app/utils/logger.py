"""Rotating-file logger writing to %LOCALAPPDATA%\\DTUTypewriter\\logs."""
import logging
import logging.handlers
from app.utils.paths import get_local_appdata_dir


def get_logger(name: str = "dtu_typewriter") -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    log_dir = get_local_appdata_dir() / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "app.log"

    fh = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=5_242_880, backupCount=3, encoding="utf-8",
    )
    fmt = logging.Formatter(
        "%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    return logger
