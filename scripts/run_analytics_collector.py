"""
Analytics Collector Background Process
=======================================
Fetches analytics from all platforms every 24 hours and saves
snapshots to data/analytics/<platform>/<date>.json.

Usage:
    python scripts/run_analytics_collector.py
"""

import asyncio
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

from automation.analytics_collector.collector import AnalyticsCollector

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

if __name__ == "__main__":
    collector = AnalyticsCollector()
    print("Analytics collector started. Press Ctrl+C to stop.")
    try:
        asyncio.run(collector.run_loop(interval_hours=24))
    except KeyboardInterrupt:
        print("\nCollector stopped.")
