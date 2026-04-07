"""
Settings
========
Loads environment variables from a .env file (if present) and
exposes typed configuration values to the rest of the application.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from the project root (one level above config/)
_ROOT = Path(__file__).parent.parent
load_dotenv(_ROOT / ".env", override=False)


# ---------------------------------------------------------------------------
# Twitter
# ---------------------------------------------------------------------------
TWITTER_API_KEY: str = os.environ.get("TWITTER_API_KEY", "")
TWITTER_API_SECRET: str = os.environ.get("TWITTER_API_SECRET", "")
TWITTER_ACCESS_TOKEN: str = os.environ.get("TWITTER_ACCESS_TOKEN", "")
TWITTER_ACCESS_TOKEN_SECRET: str = os.environ.get("TWITTER_ACCESS_TOKEN_SECRET", "")
TWITTER_BEARER_TOKEN: str = os.environ.get("TWITTER_BEARER_TOKEN", "")

# ---------------------------------------------------------------------------
# Instagram
# ---------------------------------------------------------------------------
INSTAGRAM_ACCESS_TOKEN: str = os.environ.get("INSTAGRAM_ACCESS_TOKEN", "")
INSTAGRAM_BUSINESS_ACCOUNT_ID: str = os.environ.get("INSTAGRAM_BUSINESS_ACCOUNT_ID", "")

# ---------------------------------------------------------------------------
# Facebook
# ---------------------------------------------------------------------------
FACEBOOK_ACCESS_TOKEN: str = os.environ.get("FACEBOOK_ACCESS_TOKEN", "")
FACEBOOK_PAGE_ID: str = os.environ.get("FACEBOOK_PAGE_ID", "")

# ---------------------------------------------------------------------------
# LinkedIn
# ---------------------------------------------------------------------------
LINKEDIN_ACCESS_TOKEN: str = os.environ.get("LINKEDIN_ACCESS_TOKEN", "")
LINKEDIN_ORGANIZATION_ID: str = os.environ.get("LINKEDIN_ORGANIZATION_ID", "")
LINKEDIN_PERSON_ID: str = os.environ.get("LINKEDIN_PERSON_ID", "")

# ---------------------------------------------------------------------------
# YouTube
# ---------------------------------------------------------------------------
YOUTUBE_CLIENT_ID: str = os.environ.get("YOUTUBE_CLIENT_ID", "")
YOUTUBE_CLIENT_SECRET: str = os.environ.get("YOUTUBE_CLIENT_SECRET", "")
YOUTUBE_REFRESH_TOKEN: str = os.environ.get("YOUTUBE_REFRESH_TOKEN", "")
YOUTUBE_CHANNEL_ID: str = os.environ.get("YOUTUBE_CHANNEL_ID", "")

# ---------------------------------------------------------------------------
# Google Ads
# ---------------------------------------------------------------------------
GOOGLE_ADS_DEVELOPER_TOKEN: str = os.environ.get("GOOGLE_ADS_DEVELOPER_TOKEN", "")
GOOGLE_ADS_CLIENT_ID: str = os.environ.get("GOOGLE_ADS_CLIENT_ID", "")
GOOGLE_ADS_CLIENT_SECRET: str = os.environ.get("GOOGLE_ADS_CLIENT_SECRET", "")
GOOGLE_ADS_REFRESH_TOKEN: str = os.environ.get("GOOGLE_ADS_REFRESH_TOKEN", "")
GOOGLE_ADS_LOGIN_CUSTOMER_ID: str = os.environ.get("GOOGLE_ADS_LOGIN_CUSTOMER_ID", "")
GOOGLE_ADS_CUSTOMER_IDS: list[str] = [
    cid.strip()
    for cid in os.environ.get("GOOGLE_ADS_CUSTOMER_IDS", "").split(",")
    if cid.strip()
]
