"""Gmail API send-only email delivery with automatic token refresh."""

import base64
import json
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Dict, Any, Optional
import httpx

from digest.config import (
    GMAIL_CLIENT_ID,
    GMAIL_CLIENT_SECRET,
    GMAIL_REFRESH_TOKEN,
    RECIPIENT_EMAIL,
    SENDER_EMAIL,
    DATA_DIR,
    BASE_DIR
)
from digest.logger import logger


def get_fresh_access_token() -> Optional[str]:
    """Exchange long-lived OAuth refresh token for a short-lived access token."""
    refresh_token = GMAIL_REFRESH_TOKEN
    client_id = GMAIL_CLIENT_ID
    client_secret = GMAIL_CLIENT_SECRET

    # Also check local token.json if env vars are empty
    token_file = BASE_DIR / "token.json"
    if (not refresh_token or not client_id) and token_file.exists():
        try:
            with open(token_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                refresh_token = refresh_token or data.get("refresh_token")
                client_id = client_id or data.get("client_id")
                client_secret = client_secret or data.get("client_secret")
        except Exception as e:
            logger.warning(f"[GMAIL] Failed to read token.json: {e}")

    if not (refresh_token and client_id and client_secret):
        logger.info("[GMAIL] OAuth credentials missing. Running in local preview mode.")
        return None

    token_url = "https://oauth2.googleapis.com/token"
    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token"
    }

    try:
        response = httpx.post(token_url, data=payload, timeout=10.0)
        if response.status_code == 200:
            return response.json().get("access_token")
        else:
            logger.error(f"[GMAIL] Token refresh failed ({response.status_code}): {response.text}")
            return None
    except Exception as e:
        logger.error(f"[GMAIL] Token exchange exception: {e}")
        return None


def send_digest_email(subject: str, html_body: str, text_body: str) -> Dict[str, Any]:
    """Send digest email via Gmail REST API (https://www.googleapis.com/auth/gmail.send)."""
    recipient = RECIPIENT_EMAIL
    sender = SENDER_EMAIL or recipient

    date_str = datetime.now().strftime("%Y-%m-%d")
    preview_file = DATA_DIR / f"email_{date_str}.html"

    # Always save a local HTML preview
    with open(preview_file, "w", encoding="utf-8") as f:
        f.write(html_body)

    if not recipient:
        logger.info(f"[GMAIL] RECIPIENT_EMAIL not set. Saved preview to {preview_file}")
        return {"success": False, "reason": "No recipient configured", "preview": str(preview_file)}

    access_token = get_fresh_access_token()
    if not access_token:
        logger.info(f"[GMAIL] No access token available. Saved preview to {preview_file}")
        return {"success": False, "reason": "Gmail credentials missing", "preview": str(preview_file)}

    # Construct MIME message
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient

    msg.attach(MIMEText(text_body, "plain", "utf-8"))
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    raw_message = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")
    send_url = "https://gmail.googleapis.com/gmail/v1/users/me/messages/send"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    try:
        res = httpx.post(send_url, headers=headers, json={"raw": raw_message}, timeout=15.0)
        if res.status_code in (200, 202):
            msg_id = res.json().get("id", "sent")
            logger.info(f"[GMAIL] Email sent successfully to {recipient}! (Message ID: {msg_id})")
            return {"success": True, "message_id": msg_id}
        else:
            logger.error(f"[GMAIL] Failed to send email ({res.status_code}): {res.text}")
            return {"success": False, "reason": res.text, "preview": str(preview_file)}
    except Exception as e:
        logger.error(f"[GMAIL] Exception sending email: {e}")
        return {"success": False, "reason": str(e), "preview": str(preview_file)}

