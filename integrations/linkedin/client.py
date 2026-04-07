"""
LinkedIn Integration Client
=============================
Uses the LinkedIn Marketing API v2 / REST API.

Required environment variables:
  LINKEDIN_ACCESS_TOKEN    — OAuth 2.0 access token
  LINKEDIN_ORGANIZATION_ID — URN of your LinkedIn Company Page
                              e.g. "urn:li:organization:12345678"
  LINKEDIN_PERSON_ID       — URN for personal profile posts
                              e.g. "urn:li:person:abc123"

Permissions (OAuth scopes) required:
  w_member_social, r_liteprofile, r_emailaddress,
  w_organization_social, r_organization_social,
  rw_ads (for Ads API)

Docs: https://learn.microsoft.com/en-us/linkedin/marketing/
"""

import logging
import os
from typing import Any

import httpx

from integrations.base_client import BaseSocialClient

logger = logging.getLogger(__name__)

API_BASE = "https://api.linkedin.com/v2"
REST_BASE = "https://api.linkedin.com/rest"


class LinkedInClient(BaseSocialClient):
    """LinkedIn Marketing API client."""

    def __init__(self) -> None:
        self._access_token = os.getenv("LINKEDIN_ACCESS_TOKEN", "")
        self._org_id = os.getenv("LINKEDIN_ORGANIZATION_ID", "")
        self._person_id = os.getenv("LINKEDIN_PERSON_ID", "")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @property
    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
            "LinkedIn-Version": "202401",
        }

    async def _post_request(self, url: str, payload: dict) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, headers=self._headers, json=payload, timeout=30)
            resp.raise_for_status()
            # LinkedIn returns 201 with empty body or a JSON body
            return resp.json() if resp.content else {"id": resp.headers.get("x-restli-id", "")}

    async def _get(self, url: str, params: dict | None = None) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=self._headers, params=params, timeout=30)
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
        Publish a post to a LinkedIn Company Page or personal profile.
        Pass options={"target": "person"} to post as personal profile.
        """
        options = options or {}
        author = (
            self._person_id
            if options.get("target") == "person"
            else self._org_id
        )
        try:
            payload: dict[str, Any] = {
                "author": author,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {"text": content},
                        "shareMediaCategory": "NONE",
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": options.get(
                        "visibility", "PUBLIC"
                    )
                },
            }

            if media_urls:
                # For simplicity, attach as article link (full media upload uses separate flow)
                media_category = "ARTICLE"
                payload["specificContent"]["com.linkedin.ugc.ShareContent"]["shareMediaCategory"] = media_category
                payload["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [
                    {
                        "status": "READY",
                        "originalUrl": url,
                    }
                    for url in media_urls
                ]

            result = await self._post_request(f"{API_BASE}/ugcPosts", payload)
            post_id = result.get("id", "")
            logger.info("LinkedIn post created: %s", post_id)
            return {
                "status": "published",
                "platform": "linkedin",
                "post_id": post_id,
                "url": f"https://www.linkedin.com/feed/update/{post_id}/",
            }
        except httpx.HTTPError as exc:
            logger.error("LinkedIn create_post failed: %s", exc)
            return {"status": "error", "platform": "linkedin", "error": str(exc)}

    # ------------------------------------------------------------------
    # Analytics
    # ------------------------------------------------------------------

    async def get_post_analytics(self, post_id: str) -> dict[str, Any]:
        try:
            data = await self._get(
                f"{API_BASE}/socialActions/{post_id}",
            )
            return {
                "platform": "linkedin",
                "post_id": post_id,
                "likes": data.get("likesSummary", {}).get("totalLikes", 0),
                "comments": data.get("commentsSummary", {}).get("totalFirstLevelComments", 0),
            }
        except httpx.HTTPError as exc:
            logger.error("LinkedIn get_post_analytics failed: %s", exc)
            return {"error": str(exc)}

    async def get_account_analytics(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> dict[str, Any]:
        """
        Fetch organization page statistics.
        Requires r_organization_social scope and a Company Page.
        """
        try:
            org_id_num = self._org_id.split(":")[-1]
            params: dict[str, Any] = {
                "q": "organizationalEntity",
                "organizationalEntity": self._org_id,
                "timeIntervals.timeGranularityType": "DAY",
                "timeIntervals.timeRange.start": 0,
            }
            if start_date:
                import datetime
                dt = datetime.datetime.strptime(start_date, "%Y-%m-%d")
                params["timeIntervals.timeRange.start"] = int(dt.timestamp() * 1000)
            data = await self._get(
                f"{API_BASE}/organizationalEntityShareStatistics",
                params,
            )
            return {"platform": "linkedin", "org_id": org_id_num, "data": data}
        except httpx.HTTPError as exc:
            logger.error("LinkedIn get_account_analytics failed: %s", exc)
            return {"error": str(exc)}
