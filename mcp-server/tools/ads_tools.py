"""
Advertising MCP Tools
=====================
Defines MCP tool schemas and dispatches calls to Facebook Ads
(Meta Marketing API) and Google Ads integration clients.

Tools exposed:
  Google Ads:
    - list_google_campaigns
    - get_google_campaign_metrics
    - create_google_campaign
    - pause_google_campaign

  Facebook Ads:
    - list_facebook_campaigns
    - get_facebook_campaign_metrics
    - create_facebook_campaign
    - pause_facebook_campaign
    - get_facebook_ads_account_metrics
"""

import logging

import mcp.types as types

from integrations.google_ads.client import GoogleAdsClient
from integrations.facebook_ads.client import FacebookAdsClient

logger = logging.getLogger(__name__)

_google_ads = GoogleAdsClient()
_facebook_ads = FacebookAdsClient()

# ---------------------------------------------------------------------------
# Tool schemas — Google Ads
# ---------------------------------------------------------------------------

_GOOGLE_ADS_TOOLS: list[types.Tool] = [
    types.Tool(
        name="list_google_campaigns",
        description=(
            "List all Google Ads campaigns for a customer account. "
            "Returns campaign ID, name, status, type, and daily budget. "
            "Also covers YouTube Ads (Video campaigns) since they use the same API."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "customer_id": {
                    "type": "string",
                    "description": "Google Ads customer account ID (10-digit, without dashes).",
                },
                "status_filter": {
                    "type": "string",
                    "enum": ["ALL", "ENABLED", "PAUSED", "REMOVED"],
                    "description": "Filter by campaign status. Defaults to ALL.",
                },
            },
            "required": ["customer_id"],
        },
    ),
    types.Tool(
        name="get_google_campaign_metrics",
        description=(
            "Fetch performance metrics for a Google Ads or YouTube Ads campaign: "
            "impressions, clicks, CTR, CPC, conversions, spend."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "customer_id": {"type": "string", "description": "Google Ads customer ID."},
                "campaign_id": {"type": "string", "description": "Campaign ID to query."},
                "start_date": {"type": "string", "description": "Start date YYYY-MM-DD."},
                "end_date":   {"type": "string", "description": "End date YYYY-MM-DD."},
            },
            "required": ["customer_id", "campaign_id"],
        },
    ),
    types.Tool(
        name="create_google_campaign",
        description=(
            "Create a new Google Ads campaign. Campaign is created PAUSED for safety. "
            "Supports SEARCH, DISPLAY, VIDEO (YouTube Ads), and PERFORMANCE_MAX types."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "customer_id":   {"type": "string"},
                "name":          {"type": "string", "description": "Campaign name."},
                "budget_micros": {
                    "type": "integer",
                    "description": "Daily budget in micros (1 USD = 1,000,000 micros).",
                },
                "campaign_type": {
                    "type": "string",
                    "enum": ["SEARCH", "DISPLAY", "VIDEO", "PERFORMANCE_MAX"],
                },
                "start_date":    {"type": "string", "description": "YYYY-MM-DD."},
                "end_date":      {"type": "string", "description": "YYYY-MM-DD (optional)."},
            },
            "required": ["customer_id", "name", "budget_micros", "campaign_type"],
        },
    ),
    types.Tool(
        name="pause_google_campaign",
        description="Pause a running Google Ads or YouTube Ads campaign.",
        inputSchema={
            "type": "object",
            "properties": {
                "customer_id": {"type": "string"},
                "campaign_id": {"type": "string"},
            },
            "required": ["customer_id", "campaign_id"],
        },
    ),
]

# ---------------------------------------------------------------------------
# Tool schemas — Facebook Ads
# ---------------------------------------------------------------------------

_FACEBOOK_ADS_TOOLS: list[types.Tool] = [
    types.Tool(
        name="list_facebook_campaigns",
        description=(
            "List all Facebook Ads campaigns for the configured ad account. "
            "Returns campaign ID, name, objective, status, and budget."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "status_filter": {
                    "type": "string",
                    "enum": ["ALL", "ACTIVE", "PAUSED", "DELETED", "ARCHIVED"],
                    "description": "Filter by campaign status. Defaults to ALL.",
                },
            },
            "required": [],
        },
    ),
    types.Tool(
        name="get_facebook_campaign_metrics",
        description=(
            "Fetch performance metrics for a Facebook Ads campaign via the Insights API: "
            "impressions, reach, clicks, CTR, CPC, spend, conversions, ROAS."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "campaign_id": {"type": "string", "description": "Facebook campaign ID."},
                "start_date":  {"type": "string", "description": "Start date YYYY-MM-DD."},
                "end_date":    {"type": "string", "description": "End date YYYY-MM-DD."},
            },
            "required": ["campaign_id"],
        },
    ),
    types.Tool(
        name="create_facebook_campaign",
        description=(
            "Create a new Facebook Ads campaign. "
            "Campaign is created PAUSED by default for safety. "
            "Objective options: OUTCOME_AWARENESS, OUTCOME_TRAFFIC, "
            "OUTCOME_ENGAGEMENT, OUTCOME_LEADS, OUTCOME_APP_PROMOTION, OUTCOME_SALES."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "name":      {"type": "string", "description": "Campaign name."},
                "objective": {
                    "type": "string",
                    "enum": [
                        "OUTCOME_AWARENESS", "OUTCOME_TRAFFIC",
                        "OUTCOME_ENGAGEMENT", "OUTCOME_LEADS",
                        "OUTCOME_APP_PROMOTION", "OUTCOME_SALES",
                    ],
                },
                "daily_budget_cents": {
                    "type": "integer",
                    "description": "Daily budget in cents (100 = $1.00).",
                },
                "lifetime_budget_cents": {
                    "type": "integer",
                    "description": "Lifetime budget in cents (alternative to daily).",
                },
                "start_time": {
                    "type": "string",
                    "description": "ISO 8601 start time (optional).",
                },
                "end_time": {
                    "type": "string",
                    "description": "ISO 8601 end time (optional).",
                },
            },
            "required": ["name", "objective"],
        },
    ),
    types.Tool(
        name="pause_facebook_campaign",
        description="Pause an active Facebook Ads campaign.",
        inputSchema={
            "type": "object",
            "properties": {
                "campaign_id": {"type": "string", "description": "Facebook campaign ID to pause."},
            },
            "required": ["campaign_id"],
        },
    ),
    types.Tool(
        name="get_facebook_ads_account_metrics",
        description=(
            "Fetch account-level Facebook Ads summary: total spend, impressions, "
            "clicks, reach, CTR, and CPC across all campaigns for a date range."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "start_date": {"type": "string", "description": "Start date YYYY-MM-DD."},
                "end_date":   {"type": "string", "description": "End date YYYY-MM-DD."},
            },
            "required": [],
        },
    ),
]

# ---------------------------------------------------------------------------
# All tools combined
# ---------------------------------------------------------------------------

ADS_TOOLS: list[types.Tool] = _GOOGLE_ADS_TOOLS + _FACEBOOK_ADS_TOOLS

# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------


async def handle_ads_tool(name: str, args: dict) -> dict:
    """Route an MCP ads tool call to the correct client."""

    # --- Google Ads ---
    if name == "list_google_campaigns":
        return await _google_ads.list_campaigns(
            customer_id=args["customer_id"],
            status_filter=args.get("status_filter", "ALL"),
        )

    if name == "get_google_campaign_metrics":
        return await _google_ads.get_campaign_metrics(
            customer_id=args["customer_id"],
            campaign_id=args["campaign_id"],
            start_date=args.get("start_date"),
            end_date=args.get("end_date"),
        )

    if name == "create_google_campaign":
        return await _google_ads.create_campaign(
            customer_id=args["customer_id"],
            name=args["name"],
            budget_micros=args["budget_micros"],
            campaign_type=args["campaign_type"],
            start_date=args.get("start_date"),
            end_date=args.get("end_date"),
        )

    if name == "pause_google_campaign":
        return await _google_ads.pause_campaign(
            customer_id=args["customer_id"],
            campaign_id=args["campaign_id"],
        )

    # --- Facebook Ads ---
    if name == "list_facebook_campaigns":
        return await _facebook_ads.list_campaigns(
            status_filter=args.get("status_filter", "ALL"),
        )

    if name == "get_facebook_campaign_metrics":
        return await _facebook_ads.get_campaign_metrics(
            campaign_id=args["campaign_id"],
            start_date=args.get("start_date"),
            end_date=args.get("end_date"),
        )

    if name == "create_facebook_campaign":
        return await _facebook_ads.create_campaign(
            name=args["name"],
            objective=args["objective"],
            daily_budget_cents=args.get("daily_budget_cents"),
            lifetime_budget_cents=args.get("lifetime_budget_cents"),
            start_time=args.get("start_time"),
            end_time=args.get("end_time"),
        )

    if name == "pause_facebook_campaign":
        return await _facebook_ads.pause_campaign(
            campaign_id=args["campaign_id"],
        )

    if name == "get_facebook_ads_account_metrics":
        return await _facebook_ads.get_account_metrics(
            start_date=args.get("start_date"),
            end_date=args.get("end_date"),
        )

    return {"error": f"Unhandled ads tool: {name}"}
