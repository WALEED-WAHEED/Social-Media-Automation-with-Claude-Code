"""
Instagram Integration Client
==============================
Uses the Instagram Graph API (part of Meta's Graph API).

Required environment variables:
  INSTAGRAM_ACCESS_TOKEN      — Long-lived User or Page access token
  INSTAGRAM_BUSINESS_ACCOUNT_ID — Instagram Business/Creator account ID

Note: Posting requires a Facebook Page connected to the Instagram
Business/Creator account. Personal accounts are NOT supported.

Docs: https://developers.facebook.com/docs/instagram-api
"""

import logging
import os
from typing import Any

import httpx

from integrations.base_client import BaseSocialClient

logger = logging.getLogger(__name__)

GRAPH_API_BASE = "https://graph.facebook.com/v19.0"


class InstagramClient(BaseSocialClient):
    """Instagram Graph API client."""

    def __init__(self) -> None:
        self._access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
        self._account_id = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID", "")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _params(self, extra: dict | None = None) -> dict:
        params = {"access_token": self._access_token}
        if extra:
            params.update(extra)
        return params

    async def _get(self, path: str, params: dict | None = None) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{GRAPH_API_BASE}/{path}",
                params=self._params(params),
                timeout=30,
            )
            resp.raise_for_status()
            return resp.json()

    async def _post(self, path: str, data: dict) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{GRAPH_API_BASE}/{path}",
                params={"access_token": self._access_token},
                json=data,
                timeout=60,
            )
            resp.raise_for_status()
            return resp.json()

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
        Publish an Instagram post.
        - Image post: provide exactly one image URL in media_urls.
        - Carousel:  provide multiple image URLs.
        - Reel/video: provide a single video URL with options={"media_type":"REELS"}.
        """
        try:
            account_id = self._account_id
            if not media_urls:
                # Text-only posts are not supported on Instagram; use a static image.
                return {
                    "status": "error",
                    "platform": "instagram",
                    "error": "Instagram requires at least one media_url for posts.",
                }

            if len(media_urls) == 1:
                creation_id = await self._create_single_media_container(
                    content, media_urls[0], options or {}
                )
            else:
                creation_id = await self._create_carousel_container(
                    content, media_urls
                )

            # Publish
            result = await self._post(
                f"{account_id}/media_publish",
                {"creation_id": creation_id},
            )
            post_id = result.get("id", "")
            logger.info("Instagram post published: %s", post_id)
            return {
                "status": "published",
                "platform": "instagram",
                "post_id": post_id,
                "url": f"https://www.instagram.com/p/{post_id}/",
            }
        except httpx.HTTPError as exc:
            logger.error("Instagram create_post failed: %s", exc)
            return {"status": "error", "platform": "instagram", "error": str(exc)}

    async def _create_single_media_container(
        self, caption: str, media_url: str, options: dict
    ) -> str:
        media_type = options.get("media_type", "IMAGE").upper()
        payload: dict[str, Any] = {"caption": caption}
        if media_type == "VIDEO" or media_type == "REELS":
            payload["media_type"] = "REELS"
            payload["video_url"] = media_url
        else:
            payload["image_url"] = media_url
        result = await self._post(f"{self._account_id}/media", payload)
        return result["id"]

    async def _create_carousel_container(
        self, caption: str, media_urls: list[str]
    ) -> str:
        child_ids = []
        for url in media_urls:
            child = await self._post(
                f"{self._account_id}/media",
                {"image_url": url, "is_carousel_item": True},
            )
            child_ids.append(child["id"])
        result = await self._post(
            f"{self._account_id}/media",
            {"media_type": "CAROUSEL", "children": ",".join(child_ids), "caption": caption},
        )
        return result["id"]

    # ------------------------------------------------------------------
    # Analytics
    # ------------------------------------------------------------------

    async def get_post_analytics(self, post_id: str) -> dict[str, Any]:
        try:
            data = await self._get(
                f"{post_id}/insights",
                {
                    "metric": "impressions,reach,likes,comments,shares,saved,profile_visits",
                    "period": "lifetime",
                },
            )
            metrics: dict[str, Any] = {"platform": "instagram", "post_id": post_id}
            for item in data.get("data", []):
                metrics[item["name"]] = item["values"][0]["value"]
            return metrics
        except httpx.HTTPError as exc:
            logger.error("Instagram get_post_analytics failed: %s", exc)
            return {"error": str(exc)}

    async def get_account_analytics(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> dict[str, Any]:
        try:
            params: dict[str, Any] = {
                "metric": "impressions,reach,follower_count,profile_views",
                "period": "day",
            }
            if start_date:
                import datetime
                params["since"] = int(
                    datetime.datetime.strptime(start_date, "%Y-%m-%d").timestamp()
                )
            if end_date:
                import datetime
                params["until"] = int(
                    datetime.datetime.strptime(end_date, "%Y-%m-%d").timestamp()
                )
            data = await self._get(f"{self._account_id}/insights", params)
            return {"platform": "instagram", "data": data.get("data", [])}
        except httpx.HTTPError as exc:
            logger.error("Instagram get_account_analytics failed: %s", exc)
            return {"error": str(exc)}
