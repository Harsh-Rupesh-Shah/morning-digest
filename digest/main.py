"""Main execution pipeline for Morning News Digest."""

from datetime import datetime, timezone
from typing import Dict, Any

from digest.logger import start_run, finish_run, logger
from digest.agents.graph import digest_graph
from digest.storage import save_digest
from digest.gmail_sender import send_digest_email


def run_morning_digest() -> Dict[str, Any]:
    """Execute the end-to-end morning news digest pipeline."""
    start_run()
    today_str = datetime.now().strftime("%Y-%m-%d")
    readable_date = datetime.now().strftime("%B %d, %Y")

    logger.info(f"[DIGEST] Generating digest for {readable_date}")

    # Initial state
    initial_state = {
        "date": readable_date,
    }

    # Run LangGraph pipeline
    final_state = digest_graph.invoke(initial_state)

    # Calculate metrics
    metrics = finish_run()

    # Prepare structured storage payload
    digest_payload = {
        "date": today_str,
        "formatted_date": readable_date,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "metrics": metrics,
        "sections": {
            "ai": final_state.get("ai_headlines", []),
            "tech": final_state.get("tech_headlines", []),
            "finance": final_state.get("finance_headlines", [])
        },
        "email_text": final_state.get("email_text", ""),
        "email_html": final_state.get("email_html", "")
    }

    # 1. Save locally to dated file & latest.json
    saved_path = save_digest(digest_payload)
    logger.info(f"[DIGEST] Persisted to disk at: {saved_path}")

    # 2. Deliver via Gmail API
    subject = f"Morning brief — {readable_date}"
    email_result = send_digest_email(
        subject=subject,
        html_body=final_state.get("email_html", ""),
        text_body=final_state.get("email_text", "")
    )

    return {
        "success": True,
        "date": today_str,
        "saved_path": str(saved_path),
        "email_result": email_result,
        "metrics": metrics,
        "sections": digest_payload["sections"]
    }


if __name__ == "__main__":
    run_morning_digest()

