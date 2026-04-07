"""
Base Client
===========
Abstract base class that every platform integration client must implement.
This guarantees a consistent interface for the MCP tool layer.
"""

from abc import ABC, abstractmethod
from typing import Any


class BaseSocialClient(ABC):
    """All social platform clients inherit from this."""

    # ------------------------------------------------------------------
    # Publishing
    # ------------------------------------------------------------------

    @abstractmethod
    async def create_post(
        self,
        content: str,
        media_urls: list[str] | None = None,
        options: dict | None = None,
    ) -> dict[str, Any]:
        """
        Publish a post immediately.

        Returns a dict with at minimum:
          - post_id   (str)
          - url       (str)
          - platform  (str)
          - status    ("published" | "error")
        """

    # ------------------------------------------------------------------
    # Analytics
    # ------------------------------------------------------------------

    @abstractmethod
    async def get_post_analytics(self, post_id: str) -> dict[str, Any]:
        """
        Return metrics for a single post.

        Returns a dict with at minimum:
          - post_id
          - impressions, reach, likes, comments, shares, clicks
        """

    @abstractmethod
    async def get_account_analytics(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> dict[str, Any]:
        """
        Return account-level metrics for the date range.

        Returns a dict with at minimum:
          - platform, followers, impressions, reach, engagement_rate
        """
