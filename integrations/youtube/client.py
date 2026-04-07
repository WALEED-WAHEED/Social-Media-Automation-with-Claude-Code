"""
YouTube Integration Client
============================
Uses the YouTube Data API v3.

Required environment variables:
  YOUTUBE_CLIENT_ID
  YOUTUBE_CLIENT_SECRET
  YOUTUBE_REFRESH_TOKEN    — Generated via OAuth 2.0 consent flow
  YOUTUBE_CHANNEL_ID       — Your YouTube channel ID

OAuth 2.0 scopes required:
  https://www.googleapis.com/auth/youtube.upload
  https://www.googleapis.com/auth/youtube.readonly
  https://www.googleapis.com/auth/yt-analytics.readonly

Docs: https://developers.google.com/youtube/v3
"""

import logging
import os
from typing import Any

import httpx
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from integrations.base_client import BaseSocialClient

logger = logging.getLogger(__name__)


class YouTubeClient(BaseSocialClient):
    """YouTube Data API v3 client."""

    SCOPES = [
        "https://www.googleapis.com/auth/youtube.upload",
        "https://www.googleapis.com/auth/youtube.readonly",
        "https://www.googleapis.com/auth/yt-analytics.readonly",
    ]

    def __init__(self) -> None:
        self._client_id = os.getenv("YOUTUBE_CLIENT_ID", "")
        self._client_secret = os.getenv("YOUTUBE_CLIENT_SECRET", "")
        self._refresh_token = os.getenv("YOUTUBE_REFRESH_TOKEN", "")
        self._channel_id = os.getenv("YOUTUBE_CHANNEL_ID", "")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_credentials(self) -> Credentials:
        creds = Credentials(
            token=None,
            refresh_token=self._refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=self._client_id,
            client_secret=self._client_secret,
            scopes=self.SCOPES,
        )
        creds.refresh(Request())
        return creds

    def _youtube_service(self):
        return build("youtube", "v3", credentials=self._get_credentials())

    def _analytics_service(self):
        return build("youtubeAnalytics", "v2", credentials=self._get_credentials())

    # ------------------------------------------------------------------
    # Publishing
    # ------------------------------------------------------------------

    async def create_post(
        self,
        content: str,
        media_urls: list[str] | None = None,
        options: dict | None = None,
    ) -> dict[str, Any]:
        """
        Upload a YouTube video.
        - content        → video description
        - media_urls[0]  → local file path OR public URL of the video file
        - options:
            title        → video title (required)
            tags         → list of tag strings
            category_id  → YouTube category ID (default "22" = People & Blogs)
            privacy      → "public" | "unlisted" | "private" (default "public")
        """
        options = options or {}
        if not media_urls:
            return {
                "status": "error",
                "platform": "youtube",
                "error": "YouTube upload requires a video file path in media_urls[0].",
            }
        try:
            import asyncio

            video_source = media_urls[0]
            title = options.get("title", "Untitled Video")
            tags = options.get("tags", [])
            category_id = str(options.get("category_id", "22"))
            privacy = options.get("privacy", "public")

            body = {
                "snippet": {
                    "title": title,
                    "description": content,
                    "tags": tags,
                    "categoryId": category_id,
                },
                "status": {"privacyStatus": privacy},
            }

            # If it's a URL, download first
            if video_source.startswith("http"):
                import tempfile
                import pathlib

                async with httpx.AsyncClient() as http:
                    resp = await http.get(video_source, timeout=300)
                    resp.raise_for_status()
                    suffix = pathlib.Path(video_source).suffix or ".mp4"
                    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                        tmp.write(resp.content)
                        video_source = tmp.name

            youtube = self._youtube_service()
            media = MediaFileUpload(video_source, chunksize=-1, resumable=True)

            # Run blocking call in executor
            loop = asyncio.get_event_loop()
            request = youtube.videos().insert(
                part=",".join(body.keys()),
                body=body,
                media_body=media,
            )
            response = await loop.run_in_executor(None, request.execute)

            video_id = response.get("id", "")
            logger.info("YouTube video uploaded: %s", video_id)
            return {
                "status": "published",
                "platform": "youtube",
                "post_id": video_id,
                "url": f"https://www.youtube.com/watch?v={video_id}",
            }
        except Exception as exc:
            logger.error("YouTube create_post failed: %s", exc)
            return {"status": "error", "platform": "youtube", "error": str(exc)}

    # ------------------------------------------------------------------
    # Analytics
    # ------------------------------------------------------------------

    async def get_post_analytics(self, post_id: str) -> dict[str, Any]:
        """Fetch statistics for a single YouTube video."""
        try:
            import asyncio

            youtube = self._youtube_service()
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: youtube.videos()
                .statistics()
                .list(part="statistics", id=post_id)
                .execute(),
            )
            items = response.get("items", [])
            if not items:
                return {"error": f"Video {post_id} not found"}
            stats = items[0]["statistics"]
            return {
                "platform": "youtube",
                "post_id": post_id,
                "views": int(stats.get("viewCount", 0)),
                "likes": int(stats.get("likeCount", 0)),
                "comments": int(stats.get("commentCount", 0)),
                "favorites": int(stats.get("favoriteCount", 0)),
            }
        except Exception as exc:
            logger.error("YouTube get_post_analytics failed: %s", exc)
            return {"error": str(exc)}

    async def get_account_analytics(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> dict[str, Any]:
        """Fetch channel-level analytics via YouTube Analytics API."""
        try:
            import asyncio
            import datetime

            analytics = self._analytics_service()
            start = start_date or (
                datetime.date.today() - datetime.timedelta(days=28)
            ).isoformat()
            end = end_date or datetime.date.today().isoformat()

            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: analytics.reports()
                .query(
                    ids=f"channel=={self._channel_id}",
                    startDate=start,
                    endDate=end,
                    metrics="views,estimatedMinutesWatched,averageViewDuration,likes,shares,subscribersGained,subscribersLost",
                    dimensions="day",
                )
                .execute(),
            )
            return {"platform": "youtube", "start": start, "end": end, "data": response}
        except Exception as exc:
            logger.error("YouTube get_account_analytics failed: %s", exc)
            return {"error": str(exc)}
