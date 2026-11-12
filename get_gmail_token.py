"""Helper script to authorize Gmail send-only access and obtain your GMAIL_REFRESH_TOKEN."""

import os
import sys
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
BASE_DIR = Path(__file__).resolve().parent
CREDENTIALS_FILE = BASE_DIR / "credentials.json"


def main():
    print("=" * 60)
    print("  GMAIL SEND-ONLY REFRESH TOKEN GENERATOR")
    print("=" * 60)

    if not CREDENTIALS_FILE.exists():
        print(f"\n[!] 'credentials.json' not found in {BASE_DIR}")
        print("Please download your OAuth 2.0 Client credentials JSON from Google Cloud Console,")
        print("rename it to 'credentials.json', and place it in this directory.\n")
        sys.exit(1)

    print("\nOpening your browser to authorize send-only Gmail access...")
    flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
    creds = flow.run_local_server(port=0)

    print("\n" + "=" * 60)
    print("  AUTHORIZATION SUCCESSFUL!")
    print("=" * 60)
    print(f"GMAIL_CLIENT_ID={creds.client_id}")
    print(f"GMAIL_CLIENT_SECRET={creds.client_secret}")
    print(f"GMAIL_REFRESH_TOKEN={creds.refresh_token}")
    print("=" * 60)
    print("\nAdd these three values to morning-digest/.env and to your GitHub Secrets!")


if __name__ == "__main__":
    main()

