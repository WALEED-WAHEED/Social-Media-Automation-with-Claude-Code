"""
Campaign Monitor
================
Periodically fetches Google Ads campaign metrics, detects budget
overruns or CTR drops, and logs alerts.

Alerts are written to data/alerts/campaign_alerts.json.

Usage:
    python -m automation.campaign_monitor.monitor
    # or via scripts/run_campaign_monitor.py
"""

import asyncio
import json
import logging
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent.parent.parent / "data"
ALERTS_FILE = DATA_DIR / "alerts" / "campaign_alerts.json"


class CampaignMonitor:
    """
    Monitors Google Ads campaigns and raises alerts based on
    configurable thresholds.
    """

    DEFAULT_THRESHOLDS = {
        "max_daily_spend_usd": 100.0,   # Alert if spend exceeds this
        "min_ctr_pct": 0.5,             # Alert if CTR drops below this
        "max_cpc_usd": 5.0,             # Alert if CPC rises above this
    }

    def __init__(self, thresholds: dict | None = None) -> None:
        self._thresholds = {**self.DEFAULT_THRESHOLDS, **(thresholds or {})}
        ALERTS_FILE.parent.mkdir(parents=True, exist_ok=True)
        if not ALERTS_FILE.exists():
            ALERTS_FILE.write_text("[]")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def check_all_campaigns(
        self, customer_ids: list[str]
    ) -> dict[str, Any]:
        """
        Run a monitoring check across all specified customer accounts.
        Returns a summary with any triggered alerts.
        """
        from integrations.google_ads.client import GoogleAdsClient

        client = GoogleAdsClient()
        all_alerts = []
        summary: dict[str, Any] = {}

        for customer_id in customer_ids:
            logger.info("Monitoring campaigns for customer: %s", customer_id)
            campaigns_result = await client.list_campaigns(customer_id, "ENABLED")
            campaigns = campaigns_result.get("campaigns", [])
            customer_alerts = []

            for campaign in campaigns:
                metrics = await client.get_campaign_metrics(
                    customer_id=customer_id,
                    campaign_id=campaign["id"],
                    start_date=date.today().isoformat(),
                    end_date=date.today().isoformat(),
                )
                alerts = self._evaluate(campaign, metrics)
                if alerts:
                    customer_alerts.extend(alerts)
                    all_alerts.extend(alerts)

            summary[customer_id] = {
                "campaigns_checked": len(campaigns),
                "alerts": customer_alerts,
            }

        self._save_alerts(all_alerts)
        return {"checked_at": datetime.now(timezone.utc).isoformat(), "summary": summary}

    # ------------------------------------------------------------------
    # Alert evaluation
    # ------------------------------------------------------------------

    def _evaluate(self, campaign: dict, metrics: dict) -> list[dict]:
        """Check thresholds and return any triggered alerts."""
        alerts = []
        cid = campaign.get("id", "?")
        name = campaign.get("name", "?")

        spend = metrics.get("spend_usd", 0)
        ctr = metrics.get("ctr_pct", 0)
        cpc = metrics.get("avg_cpc_usd", 0)

        if spend > self._thresholds["max_daily_spend_usd"]:
            alerts.append(
                self._alert(
                    cid,
                    name,
                    "HIGH_SPEND",
                    f"Daily spend ${spend:.2f} exceeds threshold "
                    f"${self._thresholds['max_daily_spend_usd']:.2f}",
                )
            )

        if ctr and ctr < self._thresholds["min_ctr_pct"]:
            alerts.append(
                self._alert(
                    cid,
                    name,
                    "LOW_CTR",
                    f"CTR {ctr:.2f}% is below threshold "
                    f"{self._thresholds['min_ctr_pct']:.2f}%",
                )
            )

        if cpc and cpc > self._thresholds["max_cpc_usd"]:
            alerts.append(
                self._alert(
                    cid,
                    name,
                    "HIGH_CPC",
                    f"Avg CPC ${cpc:.4f} exceeds threshold "
                    f"${self._thresholds['max_cpc_usd']:.2f}",
                )
            )

        if alerts:
            logger.warning(
                "Campaign %s (%s) triggered %d alert(s)", cid, name, len(alerts)
            )
        return alerts

    def _alert(
        self, campaign_id: str, campaign_name: str, alert_type: str, message: str
    ) -> dict:
        return {
            "campaign_id": campaign_id,
            "campaign_name": campaign_name,
            "alert_type": alert_type,
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _save_alerts(self, new_alerts: list[dict]) -> None:
        if not new_alerts:
            return
        try:
            existing = json.loads(ALERTS_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, FileNotFoundError):
            existing = []
        existing.extend(new_alerts)
        ALERTS_FILE.write_text(
            json.dumps(existing, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    def get_recent_alerts(self, hours: int = 24) -> list[dict]:
        """Return alerts from the last N hours."""
        try:
            all_alerts = json.loads(ALERTS_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, FileNotFoundError):
            return []
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        return [
            a
            for a in all_alerts
            if datetime.fromisoformat(a["timestamp"]) >= cutoff
        ]

    # ------------------------------------------------------------------
    # Scheduled loop
    # ------------------------------------------------------------------

    async def run_loop(
        self, customer_ids: list[str], interval_minutes: int = 60
    ) -> None:
        """Poll campaigns on a regular schedule."""
        logger.info(
            "Campaign monitor loop started (interval: %dm)", interval_minutes
        )
        while True:
            await self.check_all_campaigns(customer_ids)
            await asyncio.sleep(interval_minutes * 60)


if __name__ == "__main__":
    import os
    import sys

    logging.basicConfig(level=logging.INFO)
    ids = os.getenv("GOOGLE_ADS_CUSTOMER_IDS", "").split(",")
    ids = [i.strip() for i in ids if i.strip()]
    if not ids:
        print("Set GOOGLE_ADS_CUSTOMER_IDS env var (comma-separated)")
        sys.exit(1)
    asyncio.run(CampaignMonitor().check_all_campaigns(ids))
