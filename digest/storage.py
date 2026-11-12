"""Storage management for saving and reading daily news digests."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional
from digest.config import DATA_DIR
from digest.logger import logger


def save_digest(digest_data: Dict[str, Any]) -> Path:
    """Save the day's completed digest to JSON and Markdown files."""
    date_str = digest_data.get("date") or datetime.now().strftime("%Y-%m-%d")
    json_path = DATA_DIR / f"digest_{date_str}.json"
    latest_json_path = DATA_DIR / "latest.json"

    # Save JSON for programmatic access
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(digest_data, f, indent=2, ensure_ascii=False)

    with open(latest_json_path, "w", encoding="utf-8") as f:
        json.dump(digest_data, f, indent=2, ensure_ascii=False)

    logger.info(f"[STORAGE] Digest saved to {json_path} and latest.json")
    return json_path


def get_latest_digest() -> Optional[Dict[str, Any]]:
    """Retrieve the most recent saved digest."""
    latest_path = DATA_DIR / "latest.json"
    if latest_path.exists():
        try:
            with open(latest_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"[STORAGE] Error reading latest.json: {e}")

    # Fallback to scanning dated files
    dated_files = sorted(DATA_DIR.glob("digest_*.json"), reverse=True)
    if dated_files:
        try:
            with open(dated_files[0], "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"[STORAGE] Error reading {dated_files[0]}: {e}")

    return None


def is_digest_stale(digest_data: Dict[str, Any], max_hours: int = 24) -> bool:
    """Check if the digest was created more than max_hours ago."""
    timestamp_str = digest_data.get("created_at")
    if not timestamp_str:
        return True

    try:
        created_time = datetime.fromisoformat(timestamp_str)
        if created_time.tzinfo is None:
            created_time = created_time.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        elapsed_hours = (now - created_time).total_seconds() / 3600
        return elapsed_hours > max_hours
    except Exception:
        return True

