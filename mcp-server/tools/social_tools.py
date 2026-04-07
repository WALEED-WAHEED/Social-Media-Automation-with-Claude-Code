"""
Social Media MCP Tools
======================
Defines MCP tool schemas and dispatches calls to the appropriate
platform integration client.

Tools exposed:
  - post_to_platform
  - post_to_all_platforms
  - schedule_post
  - get_post_analytics
  - get_account_analytics
  - get_all_analytics
"""

import asyncio
import logging
from typing import Any

import mcp.types as types

from integrations.twitter.client import TwitterClient
from integrations.instagram.client import InstagramClient
from integrations.facebook.client import FacebookClient
from integrations.linkedin.client import LinkedInClient
from integrations.youtube.client import YouTubeClient
from integrations.tiktok.client import TikTokClient

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Platform registry — add new platforms here
# ---------------------------------------------------------------------------

_PLATFORM_CLIENTS: dict[str, Any] = {
    "twitter":   TwitterClient(),
    "instagram": InstagramClient(),
    "facebook":  FacebookClient(),
    "linkedin":  LinkedInClient(),
    "youtube":   YouTubeClient(),
    "tiktok":    TikTokClient(),   # Requires manual TikTok API approval
}

SUPPORTED_PLATFORMS = list(_PLATFORM_CLIENTS.keys())

# ---------------------------------------------------------------------------
# Tool schemas (MCP)
# ---------------------------------------------------------------------------

SOCIAL_TOOLS: list[types.Tool] = [
    types.Tool(
        name="post_to_platform",
        description=(
            "Publish a post immediately to a single social media platform. "
            "Supported: twitter, instagram, facebook, linkedin, youtube, tiktok. "
            "For simultaneous multi-platform posting, use post_to_all_platforms."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "platform": {
                    "type": "string",
                    "enum": SUPPORTED_PLATFORMS,
                    "description": "Target social media platform.",
                },
                "content": {
                    "type": "string",
                    "description": "The text body of the post.",
                },
                "media_urls": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional list of publicly accessible media URLs to attach.",
                },
                "options": {
                    "type": "object",
                    "description": (
                        "Platform-specific options. Examples: "
                        "twitter: {reply_to_id}, "
                        "instagram: {media_type: 'REELS'}, "
                        "linkedin: {target: 'person', visibility: 'PUBLIC'}, "
                        "youtube: {title, tags, privacy}, "
                        "tiktok: {privacy_level, disable_comment}"
                    ),
                },
            },
            "required": ["platform", "content"],
        },
    ),
    types.Tool(
        name="post_to_all_platforms",
        description=(
            "Publish content to multiple social media platforms simultaneously. "
            "Accepts platform-specific content variations so each post can be "
            "tailored for its audience. All posts are sent concurrently."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "posts": {
                    "type": "array",
                    "description": "List of platform posts to publish.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "platform": {
                                "type": "string",
                                "enum": SUPPORTED_PLATFORMS,
                            },
                            "content": {"type": "string"},
                            "media_urls": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                            "options": {"type": "object"},
                        },
                        "required": ["platform", "content"],
                    },
                }
            },
            "required": ["posts"],
        },
    ),
    types.Tool(
        name="schedule_post",
        description=(
            "Schedule a post to be published at a future date and time. "
            "The scheduler persists the job to disk and runs as a background process. "
            "Use ISO 8601 format for scheduled_time, e.g. 2026-03-15T14:30:00Z."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "platform": {
                    "type": "string",
                    "enum": SUPPORTED_PLATFORMS,
                    "description": "Target social media platform.",
                },
                "content": {
                    "type": "string",
                    "description": "The text body of the post.",
                },
                "scheduled_time": {
                    "type": "string",
                    "description": "ISO 8601 datetime string (e.g. 2026-03-15T14:30:00Z).",
                },
                "media_urls": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional media URLs.",
                },
                "options": {
                    "type": "object",
                    "description": "Platform-specific options.",
                },
            },
            "required": ["platform", "content", "scheduled_time"],
        },
    ),
    types.Tool(
        name="get_post_analytics",
        description=(
            "Retrieve performance metrics for a specific post: "
            "impressions, reach, likes, comments, shares, clicks."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "platform": {
                    "type": "string",
                    "enum": SUPPORTED_PLATFORMS,
                    "description": "Platform where the post lives.",
                },
                "post_id": {
                    "type": "string",
                    "description": "The platform-specific post/tweet/video ID.",
                },
            },
            "required": ["platform", "post_id"],
        },
    ),
    types.Tool(
        name="get_account_analytics",
        description=(
            "Retrieve account-level analytics for a single platform: "
            "followers, impressions, reach, engagement, audience demographics."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "platform": {
                    "type": "string",
                    "enum": SUPPORTED_PLATFORMS,
                    "description": "Platform to query.",
                },
                "start_date": {
                    "type": "string",
                    "description": "Start date YYYY-MM-DD.",
                },
                "end_date": {
                    "type": "string",
                    "description": "End date YYYY-MM-DD.",
                },
            },
            "required": ["platform"],
        },
    ),
    types.Tool(
        name="get_all_analytics",
        description=(
            "Retrieve account-level analytics from ALL connected platforms "
            "simultaneously and return a unified summary. "
            "Ideal for generating weekly or monthly performance reports."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "start_date": {
                    "type": "string",
                    "description": "Start date YYYY-MM-DD. Defaults to 7 days ago.",
                },
                "end_date": {
                    "type": "string",
                    "description": "End date YYYY-MM-DD. Defaults to today.",
                },
                "platforms": {
                    "type": "array",
                    "items": {"type": "string", "enum": SUPPORTED_PLATFORMS},
                    "description": (
                        "Specific platforms to query. "
                        "If omitted, all platforms are queried."
                    ),
                },
            },
            "required": [],
        },
    ),
]

# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------


async def handle_social_tool(name: str, args: dict) -> dict:
    """Route an MCP tool call to the correct platform client method."""

    if name == "post_to_platform":
        return await _post_to_platform(args)

    if name == "post_to_all_platforms":
        return await _post_to_all_platforms(args)

    if name == "schedule_post":
        return await _schedule_post(args)

    if name == "get_post_analytics":
        return await _get_post_analytics(args)

    if name == "get_account_analytics":
        return await _get_account_analytics(args)

    if name == "get_all_analytics":
        return await _get_all_analytics(args)

    return {"error": f"Unhandled social tool: {name}"}


# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------


async def _post_to_platform(args: dict) -> dict:
    platform = args.get("platform", "")
    client = _PLATFORM_CLIENTS.get(platform)
    if client is None:
        return {"error": f"Unknown platform: {platform}"}
    logger.info("Posting to %s", platform)
    return await client.create_post(
        content=args["content"],
        media_urls=args.get("media_urls", []),
        options=args.get("options", {}),
    )


async def _post_to_all_platforms(args: dict) -> dict:
    """Publish to multiple platforms concurrently."""
    posts = args.get("posts", [])
    if not posts:
        return {"error": "No posts provided"}

    tasks = []
    for post in posts:
        platform = post.get("platform", "")
        client = _PLATFORM_CLIENTS.get(platform)
        if client:
            tasks.append(
                client.create_post(
                    content=post["content"],
                    media_urls=post.get("media_urls", []),
                    options=post.get("options", {}),
                )
            )
        else:
            tasks.append(
                asyncio.coroutine(lambda p=platform: {"error": f"Unknown platform: {p}"})()
            )

    results = await asyncio.gather(*tasks, return_exceptions=True)
    summary = {}
    for post, result in zip(posts, results):
        platform = post.get("platform", "unknown")
        if isinstance(result, Exception):
            summary[platform] = {"error": str(result)}
        else:
            summary[platform] = result

    published = sum(1 for r in summary.values() if r.get("status") == "published")
    return {
        "summary": f"Published to {published}/{len(posts)} platforms",
        "results": summary,
    }


async def _schedule_post(args: dict) -> dict:
    from automation.scheduler.scheduler import Scheduler
    scheduler = Scheduler()
    job_id = await scheduler.schedule(
        platform=args["platform"],
        content=args["content"],
        scheduled_time=args["scheduled_time"],
        media_urls=args.get("media_urls", []),
        options=args.get("options", {}),
    )
    return {
        "status": "scheduled",
        "job_id": job_id,
        "platform": args["platform"],
        "scheduled_time": args["scheduled_time"],
    }


async def _get_post_analytics(args: dict) -> dict:
    platform = args.get("platform", "")
    client = _PLATFORM_CLIENTS.get(platform)
    if client is None:
        return {"error": f"Unknown platform: {platform}"}
    return await client.get_post_analytics(post_id=args["post_id"])


async def _get_account_analytics(args: dict) -> dict:
    platform = args.get("platform", "")
    client = _PLATFORM_CLIENTS.get(platform)
    if client is None:
        return {"error": f"Unknown platform: {platform}"}
    return await client.get_account_analytics(
        start_date=args.get("start_date"),
        end_date=args.get("end_date"),
    )


async def _get_all_analytics(args: dict) -> dict:
    """Fetch analytics from all (or selected) platforms concurrently."""
    import datetime

    start = args.get("start_date") or (
        datetime.date.today() - datetime.timedelta(days=7)
    ).isoformat()
    end = args.get("end_date") or datetime.date.today().isoformat()
    platforms = args.get("platforms") or SUPPORTED_PLATFORMS

    tasks = {
        p: _PLATFORM_CLIENTS[p].get_account_analytics(start_date=start, end_date=end)
        for p in platforms
        if p in _PLATFORM_CLIENTS
    }

    results = await asyncio.gather(*tasks.values(), return_exceptions=True)
    summary: dict[str, Any] = {}
    for platform, result in zip(tasks.keys(), results):
        if isinstance(result, Exception):
            summary[platform] = {"error": str(result)}
        else:
            summary[platform] = result

    return {
        "period": {"start_date": start, "end_date": end},
        "platforms": summary,
    }
