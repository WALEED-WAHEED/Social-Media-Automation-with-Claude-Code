"""
Social Media Automation Platform - MCP Server
==============================================
Exposes social media and ads tools to Claude Code via the
Model Context Protocol (MCP).

Usage:
    python mcp-server/server.py

Claude Code config (~/.claude/claude.json):
    {
      "mcpServers": {
        "social-automation": {
          "command": "python",
          "args": ["<absolute-path>/mcp-server/server.py"]
        }
      }
    }
"""

import asyncio
import json
import logging
import sys
from pathlib import Path

# Add project root to path so integrations & automation modules are importable
sys.path.insert(0, str(Path(__file__).parent.parent))

import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions

from tools.social_tools import SOCIAL_TOOLS, handle_social_tool
from tools.ads_tools import ADS_TOOLS, handle_ads_tool

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)
logger = logging.getLogger("mcp-social-automation")

# ---------------------------------------------------------------------------
# Server instantiation
# ---------------------------------------------------------------------------

server = Server("social-automation")

ALL_TOOLS: list[types.Tool] = SOCIAL_TOOLS + ADS_TOOLS


# ---------------------------------------------------------------------------
# MCP handlers
# ---------------------------------------------------------------------------


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    """Return every tool this server exposes."""
    logger.info("list_tools called — returning %d tools", len(ALL_TOOLS))
    return ALL_TOOLS


@server.call_tool()
async def call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Route tool calls to the appropriate handler."""
    logger.info("call_tool: %s  args=%s", name, arguments)
    args = arguments or {}

    # Social media tools
    social_names = {t.name for t in SOCIAL_TOOLS}
    if name in social_names:
        result = await handle_social_tool(name, args)
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

    # Ads tools
    ads_names = {t.name for t in ADS_TOOLS}
    if name in ads_names:
        result = await handle_ads_tool(name, args)
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

    raise ValueError(f"Unknown tool: {name}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


async def main() -> None:
    logger.info("Starting Social Automation MCP server...")
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="social-automation",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
