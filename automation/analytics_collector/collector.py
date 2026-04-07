"""
Analytics Collector
====================
Periodically fetches account-level analytics from every connected
platform and saves them to data/analytics/<platform>/<date>.json.

This can be run as a cron job or a background process.

Usage:
    python -m automation.analytics_collector.collector
    # or via scripts/run_analytics_collector.py
"""

import asyncio
import json
import logging
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent.parent.parent / "data" / "analytics"


class AnalyticsCollector:
    """Pulls analytics from all platforms and stores snapshots on disk."""

    PLATFORMS = ["twitter", "instagram", "facebook", "linkedin", "youtube"]

    def __init__(self) -> None:
        DATA_DIR.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def collect_all(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> dict[str, Any]:
        """
        Collect analytics from all platforms concurrently.
        Returns a summary dict keyed by platform name.
        """
        today = date.today()
        start = start_date or (today - timedelta(days=7)).isoformat()
        end = end_date or today.isoformat()

        logger.info("Collecting analytics %s → %s for all platforms", start, end)

        tasks = {
            platform: self._collect_platform(platform, start, end)
            for platform in self.PLATFORMS
        }
        results = await asyncio.gather(*tasks.values(), return_exceptions=True)

        summary: dict[str, Any] = {}
        for platform, result in zip(tasks.keys(), results):
            if isinstance(result, Exception):
                logger.error("Analytics collection failed for %s: %s", platform, result)
                summary[platform] = {"error": str(result)}
            else:
                summary[platform] = result
                self._save_snapshot(platform, result)

        return summary

    async def collect_platform(
        self,
        platform: str,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> dict[str, Any]:
        today = date.today()
        start = start_date or (today - timedelta(days=7)).isoformat()
        end = end_date or today.isoformat()
        result = await self._collect_platform(platform, start, end)
        self._save_snapshot(platform, result)
        return result

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    async def _collect_platform(
        self, platform: str, start: str, end: str
    ) -> dict[str, Any]:
        client = self._get_client(platform)
        return await client.get_account_analytics(start_date=start, end_date=end)

    def _get_client(self, platform: str):
        from integrations.twitter.client import TwitterClient
        from integrations.instagram.client import InstagramClient
        from integrations.facebook.client import FacebookClient
        from integrations.linkedin.client import LinkedInClient
        from integrations.youtube.client import YouTubeClient

        mapping = {
            "twitter": TwitterClient,
            "instagram": InstagramClient,
            "facebook": FacebookClient,
            "linkedin": LinkedInClient,
            "youtube": YouTubeClient,
        }
        cls = mapping.get(platform)
        if not cls:
            raise ValueError(f"Unknown platform: {platform}")
        return cls()

    def _save_snapshot(self, platform: str, data: dict) -> None:
        platform_dir = DATA_DIR / platform
        platform_dir.mkdir(parents=True, exist_ok=True)
        filename = platform_dir / f"{date.today().isoformat()}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "collected_at": datetime.now(timezone.utc).isoformat(),
                    "data": data,
                },
                f,
                indent=2,
                ensure_ascii=False,
            )
        logger.info("Saved analytics snapshot: %s", filename)

    # ------------------------------------------------------------------
    # Scheduled loop
    # ------------------------------------------------------------------

    async def run_loop(self, interval_hours: int = 24) -> None:
        """Run analytics collection on a recurring schedule."""
        logger.info(
            "Analytics collector loop started (interval: %dh)", interval_hours
        )
        while True:
            await self.collect_all()
            await asyncio.sleep(interval_hours * 3600)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(AnalyticsCollector().collect_all())
