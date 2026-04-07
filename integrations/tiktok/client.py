"""
TikTok Integration Client
===========================
Handles both organic content posting (TikTok Content Posting API)
and paid advertising (TikTok Marketing API).

⚠️  IMPORTANT: TikTok API requires MANUAL APPROVAL from TikTok.
    Access is NOT automatic. You must apply at:
    https://developers.tiktok.com/
    Review takes 2–7 days and can be denied.

Required environment variables:
  TIKTOK_APP_ID              — From TikTok Developer Portal
  TIKTOK_APP_SECRET          — From TikTok Developer Portal
  TIKTOK_ACCESS_TOKEN        — OAuth 2.0 access token (refreshed every 24h)
  TIKTOK_REFRESH_TOKEN       — Used to obtain new access tokens
  TIKTOK_ADVERTISER_ID       — Ad account ID (for Marketing API)
  TIKTOK_OPEN_ID             — User open_id (for Content Posting API)

Scopes required:
  video.upload, video.publish  — Content posting
  advertiser.read, report.read — Ads analytics
  campaign.management          — Campaign creation and management

Docs:
  Content API: https://developers.tiktok.com/doc/content-posting-api-get-started
  Marketing API: https://business-api.tiktok.com/portal/docs
"""

import logging
import os
from typing import Any

import httpx

from integrations.base_client import BaseSocialClient

logger = logging.getLogger(__name__)

BUSINESS_API_BASE = "https://business-api.tiktok.com/open_api/v1.3"
OPEN_API_BASE = "https://open.tiktokapis.com/v2"


class TikTokClient(BaseSocialClient):
    """
    TikTok client for organic posting and paid advertising.
    Requires approved API access from TikTok Developer Portal.
    """

    def __init__(self) -> None:
        self._app_id = os.getenv("TIKTOK_APP_ID", "")
        self._app_secret = os.getenv("TIKTOK_APP_SECRET", "")
        self._access_token = os.getenv("TIKTOK_ACCESS_TOKEN", "")
        self._refresh_token = os.getenv("TIKTOK_REFRESH_TOKEN", "")
        self._advertiser_id = os.getenv("TIKTOK_ADVERTISER_ID", "")
        self._open_id = os.getenv("TIKTOK_OPEN_ID", "")

    # ------------------------------------------------------------------
    # Token management
    # ------------------------------------------------------------------

    async def refresh_access_token(self) -> str:
        """
        Refresh the access token using the refresh token.
        TikTok access tokens expire every 24 hours.
        Call this proactively or handle 401 responses.
        """
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{OPEN_API_BASE}/oauth/token/",
                json={
                    "client_key": self._app_id,
                    "client_secret": self._app_secret,
                    "grant_type": "refresh_token",
                    "refresh_token": self._refresh_token,
                },
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json().get("data", {})
            new_token = data.get("access_token", "")
            if new_token:
                self._access_token = new_token
                logger.info("TikTok access token refreshed successfully")
            return new_token

    # ------------------------------------------------------------------
    # Organic posting
    # ------------------------------------------------------------------

    async def create_post(
        self,
        content: str,
        media_urls: list[str] | None = None,
        options: dict | None = None,
    ) -> dict[str, Any]:
        """
        Upload and publish a video to TikTok.

        media_urls[0] must be a local file path or public video URL.
        Options:
          privacy_level: PUBLIC_TO_EVERYONE | MUTUAL_FOLLOW_FRIENDS |
                         FOLLOWER_OF_CREATOR | SELF_ONLY
          disable_comment: bool
          disable_duet: bool
          disable_stitch: bool

        Rate limits: 2 videos/minute, 20 videos/day (hard limits).
        """
        options = options or {}
        if not media_urls:
            return {
                "status": "error",
                "platform": "tiktok",
                "error": "TikTok requires a video file in media_urls[0].",
            }

        try:
            video_source = media_urls[0]

            # Step 1: Initialize upload
            init_payload = {
                "post_info": {
                    "title": content[:2200],  # TikTok caption max 2200 chars
                    "privacy_level": options.get("privacy_level", "PUBLIC_TO_EVERYONE"),
                    "disable_comment": options.get("disable_comment", False),
                    "disable_duet": options.get("disable_duet", False),
                    "disable_stitch": options.get("disable_stitch", False),
                },
                "source_info": {
                    "source": "FILE_UPLOAD",
                    "video_size": 0,  # Will be set after file read
                    "chunk_size": 0,
                    "total_chunk_count": 1,
                },
            }

            # Download video if URL
            if video_source.startswith("http"):
                async with httpx.AsyncClient() as http:
                    video_resp = await http.get(video_source, timeout=300)
                    video_resp.raise_for_status()
                    video_bytes = video_resp.content
            else:
                with open(video_source, "rb") as f:
                    video_bytes = f.read()

            video_size = len(video_bytes)
            init_payload["source_info"]["video_size"] = video_size
            init_payload["source_info"]["chunk_size"] = video_size

            async with httpx.AsyncClient() as client:
                # Step 1: Init upload
                init_resp = await client.post(
                    f"{OPEN_API_BASE}/post/publish/video/init/",
                    headers={
                        "Authorization": f"Bearer {self._access_token}",
                        "Content-Type": "application/json; charset=UTF-8",
                    },
                    json=init_payload,
                    timeout=30,
                )
                init_resp.raise_for_status()
                init_data = init_resp.json().get("data", {})
                publish_id = init_data.get("publish_id", "")
                upload_url = init_data.get("upload_url", "")

                if not upload_url:
                    return {
                        "status": "error",
                        "platform": "tiktok",
                        "error": "No upload_url returned from TikTok init",
                    }

                # Step 2: Upload video bytes
                upload_resp = await client.put(
                    upload_url,
                    content=video_bytes,
                    headers={
                        "Content-Type": "video/mp4",
                        "Content-Length": str(video_size),
                        "Content-Range": f"bytes 0-{video_size - 1}/{video_size}",
                    },
                    timeout=300,
                )
                upload_resp.raise_for_status()

            logger.info("TikTok video published, publish_id: %s", publish_id)
            return {
                "status": "published",
                "platform": "tiktok",
                "post_id": publish_id,
                "url": "https://www.tiktok.com/@{}/video/{}".format(
                    self._open_id, publish_id
                ),
            }

        except httpx.HTTPError as exc:
            logger.error("TikTok create_post failed: %s", exc)
            return {"status": "error", "platform": "tiktok", "error": str(exc)}

    # ------------------------------------------------------------------
    # Organic analytics
    # ------------------------------------------------------------------

    async def get_post_analytics(self, post_id: str) -> dict[str, Any]:
        """
        Fetch metrics for a specific TikTok video.
        Requires video.query scope.
        """
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"{OPEN_API_BASE}/video/query/",
                    headers={
                        "Authorization": f"Bearer {self._access_token}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "filters": {"video_ids": [post_id]},
                        "fields": [
                            "id", "title", "view_count", "like_count",
                            "comment_count", "share_count", "reach",
                            "video_duration",
                        ],
                    },
                    timeout=30,
                )
                resp.raise_for_status()
                data = resp.json().get("data", {})
                videos = data.get("videos", [])

                if not videos:
                    return {"error": f"Video {post_id} not found"}

                v = videos[0]
                return {
                    "platform": "tiktok",
                    "post_id": post_id,
                    "views": v.get("view_count", 0),
                    "likes": v.get("like_count", 0),
                    "comments": v.get("comment_count", 0),
                    "shares": v.get("share_count", 0),
                    "reach": v.get("reach", 0),
                }
        except httpx.HTTPError as exc:
            logger.error("TikTok get_post_analytics failed: %s", exc)
            return {"error": str(exc)}

    async def get_account_analytics(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> dict[str, Any]:
        """
        Fetch account-level follower and engagement stats.
        Note: TikTok requires data refresh every 15 days.
        """
        try:
            import datetime

            start = start_date or (
                datetime.date.today() - datetime.timedelta(days=7)
            ).isoformat()
            end = end_date or datetime.date.today().isoformat()

            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{OPEN_API_BASE}/research/user/stats/",
                    headers={
                        "Authorization": f"Bearer {self._access_token}",
                        "Content-Type": "application/json",
                    },
                    params={
                        "open_id": self._open_id,
                        "start_date": start.replace("-", ""),
                        "end_date": end.replace("-", ""),
                        "fields": "follower_count,profile_view,video_views,likes,comments,shares",
                    },
                    timeout=30,
                )
                resp.raise_for_status()
                data = resp.json().get("data", {})
                return {"platform": "tiktok", "start": start, "end": end, "data": data}
        except httpx.HTTPError as exc:
            logger.error("TikTok get_account_analytics failed: %s", exc)
            return {"error": str(exc)}

    # ------------------------------------------------------------------
    # Paid advertising
    # ------------------------------------------------------------------

    async def list_ad_campaigns(self, status_filter: str = "ALL") -> dict[str, Any]:
        """List TikTok Ads campaigns for the configured advertiser account."""
        try:
            params: dict[str, Any] = {
                "advertiser_id": self._advertiser_id,
                "fields": '["campaign_id","campaign_name","status","budget","budget_mode","create_time"]',
                "page_size": 100,
            }
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{BUSINESS_API_BASE}/campaign/get/",
                    headers={"Access-Token": self._access_token},
                    params=params,
                    timeout=30,
                )
                resp.raise_for_status()
                data = resp.json().get("data", {})
                campaigns = data.get("list", [])
                return {
                    "advertiser_id": self._advertiser_id,
                    "campaigns": campaigns,
                    "total": len(campaigns),
                }
        except httpx.HTTPError as exc:
            logger.error("TikTok list_ad_campaigns failed: %s", exc)
            return {"error": str(exc)}

    async def get_ad_campaign_metrics(
        self,
        campaign_id: str,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> dict[str, Any]:
        """Fetch ad performance metrics for a TikTok campaign."""
        try:
            import datetime

            start = start_date or (
                datetime.date.today() - datetime.timedelta(days=30)
            ).strftime("%Y-%m-%d")
            end = end_date or datetime.date.today().strftime("%Y-%m-%d")

            payload = {
                "advertiser_id": self._advertiser_id,
                "report_type": "BASIC",
                "dimensions": ["campaign_id"],
                "metrics": [
                    "spend", "impressions", "clicks", "ctr", "cpc",
                    "conversions", "cost_per_conversion", "video_play_actions",
                    "video_watched_2s", "video_watched_6s",
                ],
                "start_date": start,
                "end_date": end,
                "filters": [
                    {"field_name": "campaign_id", "filter_type": "IN", "filter_value": f'["{campaign_id}"]'}
                ],
                "page_size": 1,
            }
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{BUSINESS_API_BASE}/report/integrated/get/",
                    headers={"Access-Token": self._access_token},
                    params={"advertiser_id": self._advertiser_id},
                    timeout=30,
                )
                resp.raise_for_status()
                data = resp.json().get("data", {}).get("list", [])
                if not data:
                    return {"campaign_id": campaign_id, "message": "No data"}
                row = data[0].get("metrics", {})
                return {
                    "campaign_id": campaign_id,
                    "start_date": start,
                    "end_date": end,
                    "spend_usd": float(row.get("spend", 0)),
                    "impressions": int(row.get("impressions", 0)),
                    "clicks": int(row.get("clicks", 0)),
                    "ctr_pct": float(row.get("ctr", 0)),
                    "cpc_usd": float(row.get("cpc", 0)),
                    "conversions": int(row.get("conversions", 0)),
                    "video_plays": int(row.get("video_play_actions", 0)),
                }
        except httpx.HTTPError as exc:
            logger.error("TikTok get_ad_campaign_metrics failed: %s", exc)
            return {"error": str(exc)}
