"""
Twitter / X Integration Client
================================
Uses the Twitter API v2 via the `tweepy` library.

Required environment variables:
  TWITTER_API_KEY
  TWITTER_API_SECRET
  TWITTER_ACCESS_TOKEN
  TWITTER_ACCESS_TOKEN_SECRET
  TWITTER_BEARER_TOKEN

OAuth 1.0a User Context is required for write endpoints (posting tweets).
OAuth 2.0 Bearer Token is used for read-only endpoints (analytics via
the Basic/Pro/Enterprise tiers).

Docs: https://developer.twitter.com/en/docs/twitter-api
"""

import logging
import os
from typing import Any

import tweepy
import tweepy.asynchronous

from integrations.base_client import BaseSocialClient

logger = logging.getLogger(__name__)


class TwitterClient(BaseSocialClient):
    """Twitter/X API v2 client."""

    def __init__(self) -> None:
        self._api_key = os.getenv("TWITTER_API_KEY", "")
        self._api_secret = os.getenv("TWITTER_API_SECRET", "")
        self._access_token = os.getenv("TWITTER_ACCESS_TOKEN", "")
        self._access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET", "")
        self._bearer_token = os.getenv("TWITTER_BEARER_TOKEN", "")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_client(self) -> tweepy.Client:
        """Return an authenticated Tweepy v2 Client."""
        return tweepy.Client(
            bearer_token=self._bearer_token,
            consumer_key=self._api_key,
            consumer_secret=self._api_secret,
            access_token=self._access_token,
            access_token_secret=self._access_token_secret,
            wait_on_rate_limit=True,
        )

    # ------------------------------------------------------------------
    # Publishing
    # ------------------------------------------------------------------

    async def create_post(
        self,
        content: str,
        media_urls: list[str] | None = None,
        options: dict | None = None,
    ) -> dict[str, Any]:
        """Post a tweet (with optional media)."""
        options = options or {}
        try:
            client = self._get_client()
            media_ids = None

            if media_urls:
                media_ids = await self._upload_media(media_urls)

            kwargs: dict[str, Any] = {"text": content}
            if media_ids:
                kwargs["media_ids"] = media_ids
            if reply_to := options.get("reply_to_id"):
                kwargs["in_reply_to_tweet_id"] = reply_to

            response = client.create_tweet(**kwargs)
            tweet_id = response.data["id"]
            logger.info("Twitter post created: %s", tweet_id)
            return {
                "status": "published",
                "platform": "twitter",
                "post_id": tweet_id,
                "url": f"https://x.com/i/web/status/{tweet_id}",
            }
        except tweepy.TweepyException as exc:
            logger.error("Twitter create_post failed: %s", exc)
            return {"status": "error", "platform": "twitter", "error": str(exc)}

    async def _upload_media(self, media_urls: list[str]) -> list[str]:
        """
        Upload media to Twitter and return media IDs.
        NOTE: Twitter v1.1 media upload is used (v2 doesn't support direct upload yet).
        """
        import httpx

        auth = tweepy.OAuth1UserHandler(
            self._api_key,
            self._api_secret,
            self._access_token,
            self._access_token_secret,
        )
        api_v1 = tweepy.API(auth)
        media_ids = []
        async with httpx.AsyncClient() as http:
            for url in media_urls:
                resp = await http.get(url)
                resp.raise_for_status()
                media = api_v1.simple_upload(filename="media", file=resp.content)
                media_ids.append(str(media.media_id))
        return media_ids

    # ------------------------------------------------------------------
    # Analytics
    # ------------------------------------------------------------------

    async def get_post_analytics(self, post_id: str) -> dict[str, Any]:
        """
        Fetch public metrics for a tweet.
        Requires Basic tier or higher for non-public metrics.
        """
        try:
            client = self._get_client()
            response = client.get_tweet(
                id=post_id,
                tweet_fields=["public_metrics", "created_at", "text"],
            )
            if not response.data:
                return {"error": f"Tweet {post_id} not found"}
            metrics = response.data.public_metrics
            return {
                "platform": "twitter",
                "post_id": post_id,
                "impressions": metrics.get("impression_count", 0),
                "likes": metrics.get("like_count", 0),
                "retweets": metrics.get("retweet_count", 0),
                "replies": metrics.get("reply_count", 0),
                "quotes": metrics.get("quote_count", 0),
                "bookmarks": metrics.get("bookmark_count", 0),
                "url_clicks": metrics.get("url_link_clicks", 0),
            }
        except tweepy.TweepyException as exc:
            logger.error("Twitter get_post_analytics failed: %s", exc)
            return {"error": str(exc)}

    async def get_account_analytics(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> dict[str, Any]:
        """
        Fetch account-level public metrics.
        Detailed analytics require Twitter API Elevated/Pro/Enterprise access.
        """
        try:
            client = self._get_client()
            # Get authenticated user
            me = client.get_me(user_fields=["public_metrics"])
            if not me.data:
                return {"error": "Could not fetch account info"}
            metrics = me.data.public_metrics
            return {
                "platform": "twitter",
                "followers": metrics.get("followers_count", 0),
                "following": metrics.get("following_count", 0),
                "tweet_count": metrics.get("tweet_count", 0),
                "listed_count": metrics.get("listed_count", 0),
                "note": "Detailed impressions/reach require Twitter API Pro tier.",
            }
        except tweepy.TweepyException as exc:
            logger.error("Twitter get_account_analytics failed: %s", exc)
            return {"error": str(exc)}
