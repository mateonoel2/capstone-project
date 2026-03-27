import logging
import sys
from datetime import datetime
from pathlib import Path


class _FlushHandler(logging.StreamHandler):
    """StreamHandler that flushes after every emit (needed for Docker)."""

    def emit(self, record: logging.LogRecord) -> None:
        super().emit(record)
        self.flush()


def _make_handler() -> logging.Handler:
    handler = _FlushHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    fmt = "%(levelname)s  [%(name)s] %(message)s"
    handler.setFormatter(logging.Formatter(fmt))
    return handler


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    # Always ensure a fresh handler pointing to current sys.stdout
    logger.handlers.clear()
    logger.addHandler(_make_handler())
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
