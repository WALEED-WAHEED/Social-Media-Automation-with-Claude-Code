"""
Test Connections
================
Verifies that each platform client can authenticate and reach its API.
Run this after setting up your .env file.

Usage:
    python scripts/test_connections.py
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables
from config.settings import *  # noqa: F401,F403
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")


PASS = "✓"
FAIL = "✗"
SKIP = "–"


async def test_twitter() -> tuple[bool, str]:
    try:
        import os
        if not os.getenv("TWITTER_BEARER_TOKEN"):
            return False, "TWITTER_BEARER_TOKEN not set"
        from integrations.twitter.client import TwitterClient
        client = TwitterClient()
        result = await client.get_account_analytics()
        if "error" in result:
            return False, result["error"]
        return True, f"followers={result.get('followers', '?')}"
    except Exception as exc:
        return False, str(exc)


async def test_instagram() -> tuple[bool, str]:
    try:
        import os
        if not os.getenv("INSTAGRAM_ACCESS_TOKEN"):
            return False, "INSTAGRAM_ACCESS_TOKEN not set"
        from integrations.instagram.client import InstagramClient
        client = InstagramClient()
        result = await client.get_account_analytics()
        if "error" in result:
            return False, result["error"]
        return True, "Connected"
    except Exception as exc:
        return False, str(exc)


async def test_facebook() -> tuple[bool, str]:
    try:
        import os
        if not os.getenv("FACEBOOK_ACCESS_TOKEN"):
            return False, "FACEBOOK_ACCESS_TOKEN not set"
        from integrations.facebook.client import FacebookClient
        client = FacebookClient()
        result = await client.get_account_analytics()
        if "error" in result:
            return False, result["error"]
        return True, "Connected"
    except Exception as exc:
        return False, str(exc)


async def test_linkedin() -> tuple[bool, str]:
    try:
        import os
        if not os.getenv("LINKEDIN_ACCESS_TOKEN"):
            return False, "LINKEDIN_ACCESS_TOKEN not set"
        from integrations.linkedin.client import LinkedInClient
        client = LinkedInClient()
        result = await client.get_account_analytics()
        if "error" in result:
            return False, result["error"]
        return True, "Connected"
    except Exception as exc:
        return False, str(exc)


async def test_youtube() -> tuple[bool, str]:
    try:
        import os
        if not os.getenv("YOUTUBE_REFRESH_TOKEN"):
            return False, "YOUTUBE_REFRESH_TOKEN not set"
        from integrations.youtube.client import YouTubeClient
        client = YouTubeClient()
        result = await client.get_account_analytics()
        if "error" in result:
            return False, result["error"]
        return True, "Connected"
    except Exception as exc:
        return False, str(exc)


async def test_google_ads() -> tuple[bool, str]:
    try:
        import os
        if not os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN"):
            return False, "GOOGLE_ADS_DEVELOPER_TOKEN not set"
        from integrations.google_ads.client import GoogleAdsClient
        client = GoogleAdsClient()
        customer_ids = os.getenv("GOOGLE_ADS_CUSTOMER_IDS", "").split(",")
        if not customer_ids or not customer_ids[0].strip():
            return False, "GOOGLE_ADS_CUSTOMER_IDS not set"
        result = await client.list_campaigns(customer_ids[0].strip(), "ALL")
        if "error" in result:
            return False, result["error"]
        count = len(result.get("campaigns", []))
        return True, f"{count} campaign(s) found"
    except Exception as exc:
        return False, str(exc)


async def main() -> None:
    print("\n" + "=" * 55)
    print("  Social Media Automation Platform — Connection Test")
    print("=" * 55 + "\n")

    tests = [
        ("Twitter / X", test_twitter),
        ("Instagram", test_instagram),
        ("Facebook", test_facebook),
        ("LinkedIn", test_linkedin),
        ("YouTube", test_youtube),
        ("Google Ads", test_google_ads),
    ]

    all_passed = True
    for name, test_fn in tests:
        try:
            passed, message = await test_fn()
        except Exception as exc:
            passed, message = False, str(exc)

        icon = PASS if passed else FAIL
        if not passed:
            all_passed = False
        print(f"  {icon}  {name:<20}  {message}")

    print("\n" + "=" * 55)
    if all_passed:
        print("  All platforms connected successfully!")
    else:
        print("  Some platforms failed — check your .env configuration.")
        print("  See docs/setup/api_keys.md for setup instructions.")
    print("=" * 55 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
