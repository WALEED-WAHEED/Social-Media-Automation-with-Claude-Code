"""
Facebook Ads Integration Client (Meta Marketing API)
=====================================================
Separate from the organic Facebook client — this module handles
paid advertising via the Meta Marketing API v25.0.

Required environment variables:
  FACEBOOK_ADS_ACCESS_TOKEN   — System User access token (never expires)
                                OR long-lived user token (60 days)
  FACEBOOK_ADS_ACCOUNT_ID     — Ad account ID, format: act_XXXXXXXXXXXXXXXX

Authentication notes:
  • Use a Business Manager System User token for production automation.
    System User tokens do not expire and do not require user interaction.
  • Standard (development) access is automatic.
  • Advanced (production) access requires App Review + Business Verification.

Docs: https://developers.facebook.com/docs/marketing-apis
      https://developers.facebook.com/docs/marketing-api/reference/ad-campaign-group
"""

import logging
import os
from typing import Any

import httpx

logger = logging.getLogger(__name__)

GRAPH_BASE = "https://graph.facebook.com/v25.0"


class FacebookAdsClient:
    """Meta Marketing API client for Facebook/Instagram Ads."""

    def __init__(self) -> None:
        self._token = os.getenv("FACEBOOK_ADS_ACCESS_TOKEN", "")
        self._account_id = os.getenv("FACEBOOK_ADS_ACCOUNT_ID", "")
        # Ensure act_ prefix
        if self._account_id and not self._account_id.startswith("act_"):
            self._account_id = f"act_{self._account_id}"

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _params(self, extra: dict | None = None) -> dict:
        p = {"access_token": self._token}
        if extra:
            p.update(extra)
        return p

    async def _get(self, path: str, params: dict | None = None) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{GRAPH_BASE}/{path}",
                params=self._params(params),
                timeout=30,
            )
            resp.raise_for_status()
            return resp.json()

    async def _post(self, path: str, data: dict) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{GRAPH_BASE}/{path}",
                params={"access_token": self._token},
                json=data,
                timeout=30,
            )
            resp.raise_for_status()
            return resp.json()

    async def _post_form(self, path: str, data: dict) -> dict:
        """Some Marketing API endpoints require form-encoded data."""
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{GRAPH_BASE}/{path}",
                data={**data, "access_token": self._token},
                timeout=30,
            )
            resp.raise_for_status()
            return resp.json()

    # ------------------------------------------------------------------
    # Campaigns
    # ------------------------------------------------------------------

    async def list_campaigns(
        self, status_filter: str = "ALL"
    ) -> dict[str, Any]:
        """
        List all campaigns for the configured ad account.
        status_filter: ACTIVE | PAUSED | DELETED | ARCHIVED | ALL
        """
        try:
            params: dict[str, Any] = {
                "fields": "id,name,status,objective,daily_budget,lifetime_budget,start_time,stop_time",
                "limit": 100,
            }
            if status_filter != "ALL":
                params["effective_status"] = f'["{status_filter}"]'

            data = await self._get(f"{self._account_id}/campaigns", params)
            campaigns = data.get("data", [])
            logger.info("Listed %d Facebook Ads campaigns", len(campaigns))
            return {
                "account_id": self._account_id,
                "campaigns": campaigns,
                "total": len(campaigns),
            }
        except httpx.HTTPError as exc:
            logger.error("list_campaigns failed: %s", exc)
            return {"error": str(exc)}

    async def get_campaign_metrics(
        self,
        campaign_id: str,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> dict[str, Any]:
        """
        Fetch performance metrics for a single campaign via the Insights API.
        Returns: impressions, clicks, CTR, CPC, spend, conversions, ROAS, reach.
        """
        try:
            import datetime

            start = start_date or (
                datetime.date.today() - datetime.timedelta(days=30)
            ).isoformat()
            end = end_date or datetime.date.today().isoformat()

            params: dict[str, Any] = {
                "fields": (
                    "campaign_name,impressions,clicks,ctr,cpc,"
                    "spend,actions,action_values,reach,frequency"
                ),
                "time_range": f'{{"since":"{start}","until":"{end}"}}',
                "level": "campaign",
            }
            data = await self._get(f"{campaign_id}/insights", params)
            items = data.get("data", [])
            if not items:
                return {
                    "campaign_id": campaign_id,
                    "message": "No data for this period",
                    "start_date": start,
                    "end_date": end,
                }

            row = items[0]
            # Extract conversions from actions array
            actions = {a["action_type"]: float(a["value"]) for a in row.get("actions", [])}
            action_values = {
                a["action_type"]: float(a["value"])
                for a in row.get("action_values", [])
            }
            conversions = actions.get("offsite_conversion.fb_pixel_purchase", 0)
            conversion_value = action_values.get("offsite_conversion.fb_pixel_purchase", 0)
            spend = float(row.get("spend", 0))
            roas = round(conversion_value / spend, 2) if spend else 0

            return {
                "campaign_id": campaign_id,
                "campaign_name": row.get("campaign_name", ""),
                "start_date": start,
                "end_date": end,
                "impressions": int(row.get("impressions", 0)),
                "reach": int(row.get("reach", 0)),
                "clicks": int(row.get("clicks", 0)),
                "ctr_pct": round(float(row.get("ctr", 0)), 4),
                "cpc_usd": round(float(row.get("cpc", 0)), 4),
                "spend_usd": spend,
                "conversions": conversions,
                "conversion_value_usd": conversion_value,
                "roas": roas,
            }
        except httpx.HTTPError as exc:
            logger.error("get_campaign_metrics failed: %s", exc)
            return {"error": str(exc)}

    async def create_campaign(
        self,
        name: str,
        objective: str,
        daily_budget_cents: int | None = None,
        lifetime_budget_cents: int | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
        status: str = "PAUSED",
    ) -> dict[str, Any]:
        """
        Create a new Facebook Ads campaign.

        objective options (current Meta API):
        OUTCOME_AWARENESS, OUTCOME_TRAFFIC, OUTCOME_ENGAGEMENT,
        OUTCOME_LEADS, OUTCOME_APP_PROMOTION, OUTCOME_SALES

        Budgets are in cents (100 = $1.00).
        Campaign is created PAUSED by default for safety.
        """
        try:
            payload: dict[str, Any] = {
                "name": name,
                "objective": objective,
                "status": status,
                "special_ad_categories": [],  # Required field; add categories if needed
            }
            if daily_budget_cents:
                payload["daily_budget"] = str(daily_budget_cents)
            if lifetime_budget_cents:
                payload["lifetime_budget"] = str(lifetime_budget_cents)
            if start_time:
                payload["start_time"] = start_time
            if end_time:
                payload["stop_time"] = end_time

            result = await self._post_form(
                f"{self._account_id}/campaigns", payload
            )
            campaign_id = result.get("id", "")
            logger.info("Facebook Ads campaign created: %s", campaign_id)
            return {
                "status": "created",
                "campaign_id": campaign_id,
                "campaign_name": name,
                "objective": objective,
                "note": "Campaign created as PAUSED. Enable it when ad sets and ads are ready.",
            }
        except httpx.HTTPError as exc:
            logger.error("create_campaign failed: %s", exc)
            return {"error": str(exc)}

    async def pause_campaign(self, campaign_id: str) -> dict[str, Any]:
        """Pause an active Facebook Ads campaign."""
        try:
            result = await self._post_form(
                campaign_id, {"status": "PAUSED"}
            )
            logger.info("Facebook Ads campaign paused: %s", campaign_id)
            return {
                "status": "paused",
                "campaign_id": campaign_id,
                "success": result.get("success", False),
            }
        except httpx.HTTPError as exc:
            logger.error("pause_campaign failed: %s", exc)
            return {"error": str(exc)}

    async def enable_campaign(self, campaign_id: str) -> dict[str, Any]:
        """Enable (unpause) a paused campaign."""
        try:
            result = await self._post_form(
                campaign_id, {"status": "ACTIVE"}
            )
            logger.info("Facebook Ads campaign enabled: %s", campaign_id)
            return {
                "status": "active",
                "campaign_id": campaign_id,
                "success": result.get("success", False),
            }
        except httpx.HTTPError as exc:
            logger.error("enable_campaign failed: %s", exc)
            return {"error": str(exc)}

    # ------------------------------------------------------------------
    # Account-level analytics
    # ------------------------------------------------------------------

    async def get_account_metrics(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> dict[str, Any]:
        """
        Account-level ad spend overview — total spend, impressions,
        clicks, reach across all campaigns.
        """
        try:
            import datetime

            start = start_date or (
                datetime.date.today() - datetime.timedelta(days=30)
            ).isoformat()
            end = end_date or datetime.date.today().isoformat()

            params: dict[str, Any] = {
                "fields": "impressions,clicks,spend,reach,ctr,cpc",
                "time_range": f'{{"since":"{start}","until":"{end}"}}',
                "level": "account",
            }
            data = await self._get(f"{self._account_id}/insights", params)
            items = data.get("data", [])
            if not items:
                return {"account_id": self._account_id, "message": "No data", "start": start, "end": end}
            row = items[0]
            return {
                "account_id": self._account_id,
                "start_date": start,
                "end_date": end,
                "impressions": int(row.get("impressions", 0)),
                "reach": int(row.get("reach", 0)),
                "clicks": int(row.get("clicks", 0)),
                "ctr_pct": round(float(row.get("ctr", 0)), 4),
                "cpc_usd": round(float(row.get("cpc", 0)), 4),
                "spend_usd": float(row.get("spend", 0)),
            }
        except httpx.HTTPError as exc:
            logger.error("get_account_metrics failed: %s", exc)
            return {"error": str(exc)}
