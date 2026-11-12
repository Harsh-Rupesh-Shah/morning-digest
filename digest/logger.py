"""Logging and execution metrics for Morning News Digest."""

import logging
import time
from digest.config import LOGS_DIR

LOG_FILE = LOGS_DIR / "digest.log"

logger = logging.getLogger("MorningDigest")
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
file_formatter = logging.Formatter(
    "[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
file_handler.setFormatter(file_formatter)

console_handler = logging.StreamHandler()
console_handler.setFormatter(file_formatter)

if not logger.handlers:
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

# Metric counters
_search_counter = 0
_start_time = None


def start_run() -> None:
    """Initialize run timer and search counter."""
    global _search_counter, _start_time
    _search_counter = 0
    _start_time = time.time()
    logger.info("=== Starting Morning News Digest Job ===")


def record_search() -> None:
    """Increment the search operation counter."""
    global _search_counter
    _search_counter += 1


def finish_run() -> dict:
    """Log and return execution metrics."""
    global _search_counter, _start_time
    elapsed = round(time.time() - (_start_time or time.time()), 2)
    metrics = {
        "searches_used": _search_counter,
        "elapsed_seconds": elapsed
    }
    logger.info(
        f"=== Morning Digest Complete | Searches Used: {_search_counter} | "
        f"Elapsed Time: {elapsed}s ==="
    )
    return metrics

