import logging
import sys
from datetime import datetime
from pathlib import Path

_handler: logging.Handler | None = None


def _get_handler() -> logging.Handler:
    global _handler
    if _handler is None:
        _handler = logging.StreamHandler(sys.stderr)
        _handler.setLevel(logging.INFO)
        fmt = "%(asctime)s %(levelname)s %(name)s — %(message)s"
        _handler.setFormatter(logging.Formatter(fmt, datefmt="%H:%M:%S"))
    return _handler


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.propagate = False  # Don't let root logger (WARNING) filter our messages
    if not logger.handlers:
        logger.addHandler(_get_handler())
    return logger


def setup_logger(
    name: str, log_dir: Path | None = None, level: int = logging.INFO
) -> logging.Logger:
    """Logger with optional file output (used by ExperimentRunner)."""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    if log_dir:
        log_dir = Path(log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"{name}_{timestamp}.log"

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
