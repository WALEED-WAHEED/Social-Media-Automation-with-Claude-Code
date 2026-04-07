"""
Facebook Integration Client
=============================
Uses the Meta (Facebook) Graph API.

Required environment variables:
  FACEBOOK_ACCESS_TOKEN   — Page access token (long-lived)
  FACEBOOK_PAGE_ID        — Target Facebook Page ID

Permissions required:
  pages_manage_posts, pages_read_engagement, pages_show_list,
  read_insights, public_profile

Docs: https://developers.facebook.com/docs/graph-api
"""

import logging
import os
from typing import Any

import httpx

from integrations.base_client import BaseSocialClient

logger = logging.getLogger(__name__)

GRAPH_API_BASE = "https://graph.facebook.com/v19.0"


class FacebookClient(BaseSocialClient):
    """Meta Graph API client for Facebook Pages."""

    def __init__(self) -> None:
        self._access_token = os.getenv("FACEBOOK_ACCESS_TOKEN", "")
        self._page_id = os.getenv("FACEBOOK_PAGE_ID", "")

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

    async def _post_request(self, path: str, data: dict) -> dict:
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
        """Publish a post to a Facebook Page (text, photo, or video)."""
        options = options or {}
        try:
            page_id = self._page_id
            if media_urls and len(media_urls) == 1:
                # Single photo/video post
                endpoint = f"{page_id}/photos"
                payload = {"url": media_urls[0], "message": content}
            elif media_urls and len(media_urls) > 1:
                # Multi-photo post (unpublished photos first, then a feed post)
                photo_ids = []
                for url in media_urls:
                    r = await self._post_request(
                        f"{page_id}/photos",
                        {"url": url, "published": False},
                    )
                    photo_ids.append({"media_fbid": r["id"]})
                endpoint = f"{page_id}/feed"
                payload = {"message": content, "attached_media": photo_ids}
            else:
                # Text-only post
                endpoint = f"{page_id}/feed"
                payload = {"message": content}

            if link := options.get("link"):
                payload["link"] = link

            result = await self._post_request(endpoint, payload)
            post_id = result.get("id", result.get("post_id", ""))
            logger.info("Facebook post created: %s", post_id)
            return {
                "status": "published",
                "platform": "facebook",
                "post_id": post_id,
                "url": f"https://www.facebook.com/{post_id}",
            }
        except httpx.HTTPError as exc:
            logger.error("Facebook create_post failed: %s", exc)
            return {"status": "error", "platform": "facebook", "error": str(exc)}

    # ------------------------------------------------------------------
    # Analytics
    # ------------------------------------------------------------------

    async def get_post_analytics(self, post_id: str) -> dict[str, Any]:
        try:
            data = await self._get(
                f"{post_id}/insights",
                {
                    "metric": (
                        "post_impressions,post_reach,post_engaged_users,"
                        "post_clicks,post_reactions_by_type_total"
                    )
                },
            )
            metrics: dict[str, Any] = {"platform": "facebook", "post_id": post_id}
            for item in data.get("data", []):
                val = item.get("values", [{}])
                metrics[item["name"]] = val[0].get("value", 0) if val else 0
            return metrics
        except httpx.HTTPError as exc:
            logger.error("Facebook get_post_analytics failed: %s", exc)
            return {"error": str(exc)}

    async def get_account_analytics(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> dict[str, Any]:
        try:
            params: dict[str, Any] = {
                "metric": "page_fans,page_impressions,page_reach,page_engaged_users",
                "period": "day",
            }
            if start_date:
                params["since"] = start_date
            if end_date:
                params["until"] = end_date
            data = await self._get(f"{self._page_id}/insights", params)
            return {"platform": "facebook", "data": data.get("data", [])}
        except httpx.HTTPError as exc:
            logger.error("Facebook get_account_analytics failed: %s", exc)
            return {"error": str(exc)}
