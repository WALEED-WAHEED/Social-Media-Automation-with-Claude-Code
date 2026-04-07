"""
Campaign Monitor Background Process
=====================================
Monitors Google Ads campaigns every 60 minutes and writes alerts
to data/alerts/campaign_alerts.json when thresholds are exceeded.

Usage:
    python scripts/run_campaign_monitor.py

Set GOOGLE_ADS_CUSTOMER_IDS in your .env file (comma-separated).
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

from automation.campaign_monitor.monitor import CampaignMonitor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

if __name__ == "__main__":
    customer_ids = [
        cid.strip()
        for cid in os.getenv("GOOGLE_ADS_CUSTOMER_IDS", "").split(",")
        if cid.strip()
    ]
    if not customer_ids:
        print("ERROR: Set GOOGLE_ADS_CUSTOMER_IDS in your .env file.")
        sys.exit(1)

    monitor = CampaignMonitor()
    print(f"Campaign monitor started for {len(customer_ids)} account(s). Press Ctrl+C to stop.")
    try:
        asyncio.run(monitor.run_loop(customer_ids=customer_ids, interval_minutes=60))
    except KeyboardInterrupt:
        print("\nMonitor stopped.")
