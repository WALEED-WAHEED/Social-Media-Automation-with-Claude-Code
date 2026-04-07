"""
Scheduler Background Process
==============================
Runs the post scheduler loop continuously.
Posts queued via the MCP `schedule_post` tool will be published
when their scheduled_time is reached.

Usage:
    python scripts/run_scheduler.py

Run this in a terminal or as a background service. The scheduler
polls for due posts every 60 seconds.
"""

import asyncio
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

from automation.scheduler.scheduler import Scheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

if __name__ == "__main__":
    scheduler = Scheduler()
    print("Scheduler started. Press Ctrl+C to stop.")
    try:
        asyncio.run(scheduler.run_loop(poll_interval=60))
    except KeyboardInterrupt:
        print("\nScheduler stopped.")
