"""Single-command entrypoint to run the Morning News Digest manually."""

import sys
from pathlib import Path

# Ensure root in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from digest.main import run_morning_digest

if __name__ == "__main__":
    result = run_morning_digest()
    print("\n" + "=" * 50)
    print("  MORNING NEWS DIGEST FINISHED")
    print("=" * 50)
    print(f"Date:             {result['date']}")
    print(f"Searches Used:    {result['metrics']['searches_used']}")
    print(f"Time Taken:       {result['metrics']['elapsed_seconds']}s")
    print(f"Saved Digest:     {result['saved_path']}")
    print(f"Email Status:     {result['email_result'].get('success')}")
    print("=" * 50)

