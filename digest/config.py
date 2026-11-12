"""Configuration management for Morning News Digest."""

import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "digests"
LOGS_DIR = BASE_DIR / "logs"

DATA_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Load .env file
load_dotenv(BASE_DIR / ".env")

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Email Settings
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL", "")
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "")

# Gmail OAuth 2.0 Credentials (Send-Only)
GMAIL_CLIENT_ID = os.getenv("GMAIL_CLIENT_ID", "")
GMAIL_CLIENT_SECRET = os.getenv("GMAIL_CLIENT_SECRET", "")
GMAIL_REFRESH_TOKEN = os.getenv("GMAIL_REFRESH_TOKEN", "")

# Model Tiers
RESEARCHER_MODEL = os.getenv("RESEARCHER_MODEL", "gemini-2.5-flash")
EDITOR_MODEL = os.getenv("EDITOR_MODEL", "gemini-2.5-flash")

