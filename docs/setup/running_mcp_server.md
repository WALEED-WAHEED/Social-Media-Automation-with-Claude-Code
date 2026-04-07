# Running the MCP Server

## What is the MCP Server?

The MCP (Model Context Protocol) server is a local process that exposes
social media and ads automation **tools** to Claude Code. When Claude Code
needs to post a tweet, fetch analytics, or check a campaign, it calls a
tool on this server instead of accessing the APIs directly.

---

## Prerequisites

1. Dependencies installed (`pip install -r requirements.txt`)
2. `.env` file configured with API keys
3. Python 3.11+

---

## Starting the Server

```bash
# From the automation-platform/ directory
python mcp-server/server.py
```

The server communicates over **stdio** (standard input/output), so it
doesn't open a network port — it's designed to be launched by Claude Code.

---

## Registering with Claude Code

Add the server to your Claude Code config file.

**Location of config file:**
- macOS/Linux: `~/.claude/claude.json`
- Windows: `C:\Users\<you>\.claude\claude.json`

**Add the following entry** (adjust the path):

```json
{
  "mcpServers": {
    "social-automation": {
      "command": "python",
      "args": [
        "C:/Users/Programmer/Desktop/Developments/Social Media Automation with Claude Code/automation-platform/mcp-server/server.py"
      ],
      "env": {
        "PYTHONPATH": "C:/Users/Programmer/Desktop/Developments/Social Media Automation with Claude Code/automation-platform"
      }
    }
  }
}
```

**Windows users:** Use forward slashes in JSON paths.

---

## Verifying the Server is Registered

In a new Claude Code session, run:
```
/mcp
```
You should see `social-automation` listed with all 8 tools:

| Tool | Description |
|------|-------------|
| `post_to_platform` | Publish a post immediately |
| `schedule_post` | Schedule a post for later |
| `get_post_analytics` | Get metrics for a specific post |
| `get_account_analytics` | Get account-level metrics |
| `list_campaigns` | List Google Ads campaigns |
| `get_campaign_metrics` | Get campaign performance |
| `create_campaign` | Create a new campaign |
| `pause_campaign` | Pause a running campaign |

---

## Using Tools in Claude Code

Once registered, you can ask Claude to use the tools naturally:

```
Post this to Twitter: "Just shipped our new feature! 🚀"
```

```
Get last week's analytics for Instagram
```

```
List all active Google Ads campaigns for customer 1234567890
```

Claude Code will automatically call the appropriate MCP tool.

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Server not found | Check the path in `claude.json` is absolute and correct |
| Import errors | Make sure `PYTHONPATH` points to `automation-platform/` |
| Auth errors | Verify your `.env` credentials are set correctly |
| Tools not showing | Restart Claude Code after updating `claude.json` |
