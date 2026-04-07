"""
Post Scheduler
==============
Persists scheduled posts to a JSON file on disk and executes them
at the correct time when the scheduler loop is running.

Storage format: data/scheduled_posts.json
Each job entry:
  {
    "id": "uuid",
    "platform": "twitter",
    "content": "...",
    "media_urls": [],
    "options": {},
    "scheduled_time": "2026-03-15T14:30:00Z",
    "status": "pending" | "published" | "failed",
    "created_at": "...",
    "published_at": null,
    "error": null
  }

Usage (background daemon):
    python scripts/run_scheduler.py

Usage (from MCP tool):
    scheduler = Scheduler()
    job_id = await scheduler.schedule(platform, content, scheduled_time)
"""

import asyncio
import json
import logging
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent.parent.parent / "data"
JOBS_FILE = DATA_DIR / "scheduled_posts.json"


class Scheduler:
    """Manages a persistent queue of scheduled social media posts."""

    def __init__(self) -> None:
        DATA_DIR.mkdir(exist_ok=True)
        if not JOBS_FILE.exists():
            JOBS_FILE.write_text("[]")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def schedule(
        self,
        platform: str,
        content: str,
        scheduled_time: str,
        media_urls: list[str] | None = None,
        options: dict | None = None,
    ) -> str:
        """Add a post to the schedule. Returns the job ID."""
        job: dict[str, Any] = {
            "id": str(uuid.uuid4()),
            "platform": platform,
            "content": content,
            "media_urls": media_urls or [],
            "options": options or {},
            "scheduled_time": scheduled_time,
            "status": "pending",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "published_at": None,
            "error": None,
        }
        jobs = self._load()
        jobs.append(job)
        self._save(jobs)
        logger.info("Scheduled post %s for %s on %s", job["id"], scheduled_time, platform)
        return job["id"]

    def list_jobs(self, status: str | None = None) -> list[dict]:
        """Return all jobs, optionally filtered by status."""
        jobs = self._load()
        if status:
            jobs = [j for j in jobs if j["status"] == status]
        return jobs

    def cancel_job(self, job_id: str) -> bool:
        """Cancel a pending job. Returns True if found and cancelled."""
        jobs = self._load()
        for job in jobs:
            if job["id"] == job_id and job["status"] == "pending":
                job["status"] = "cancelled"
                self._save(jobs)
                logger.info("Cancelled job %s", job_id)
                return True
        return False

    # ------------------------------------------------------------------
    # Scheduler loop (run in background process)
    # ------------------------------------------------------------------

    async def run_loop(self, poll_interval: int = 60) -> None:
        """
        Continuously checks for due posts and publishes them.
        Run this in a dedicated process: python scripts/run_scheduler.py
        """
        logger.info("Scheduler loop started (poll interval: %ds)", poll_interval)
        while True:
            await self._process_due_jobs()
            await asyncio.sleep(poll_interval)

    async def _process_due_jobs(self) -> None:
        """Publish any pending jobs whose scheduled_time has passed."""
        now = datetime.now(timezone.utc)
        jobs = self._load()
        updated = False

        for job in jobs:
            if job["status"] != "pending":
                continue
            try:
                due_time = datetime.fromisoformat(
                    job["scheduled_time"].replace("Z", "+00:00")
                )
            except ValueError:
                logger.warning("Invalid scheduled_time for job %s", job["id"])
                continue

            if due_time <= now:
                logger.info(
                    "Publishing scheduled post %s to %s", job["id"], job["platform"]
                )
                result = await self._publish(job)
                if result.get("status") == "published":
                    job["status"] = "published"
                    job["published_at"] = datetime.now(timezone.utc).isoformat()
                else:
                    job["status"] = "failed"
                    job["error"] = result.get("error", "Unknown error")
                updated = True

        if updated:
            self._save(jobs)

    async def _publish(self, job: dict) -> dict:
        """Delegate to the correct platform client."""
        from integrations.twitter.client import TwitterClient
        from integrations.instagram.client import InstagramClient
        from integrations.facebook.client import FacebookClient
        from integrations.linkedin.client import LinkedInClient
        from integrations.youtube.client import YouTubeClient

        clients = {
            "twitter": TwitterClient(),
            "instagram": InstagramClient(),
            "facebook": FacebookClient(),
            "linkedin": LinkedInClient(),
            "youtube": YouTubeClient(),
        }
        client = clients.get(job["platform"])
        if not client:
            return {"error": f"Unknown platform: {job['platform']}"}
        return await client.create_post(
            content=job["content"],
            media_urls=job.get("media_urls", []),
            options=job.get("options", {}),
        )

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _load(self) -> list[dict]:
        try:
            return json.loads(JOBS_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _save(self, jobs: list[dict]) -> None:
        JOBS_FILE.write_text(
            json.dumps(jobs, indent=2, ensure_ascii=False), encoding="utf-8"
        )
