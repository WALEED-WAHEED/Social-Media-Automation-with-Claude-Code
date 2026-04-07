# Social Media Automation Platform

A unified automation platform for social media posting, analytics collection,
and advertising management — exposed to Claude Code via a custom MCP server.

---

## Push this project to GitHub

1. Create a new empty repository on [GitHub](https://github.com/new) (no README or `.gitignore` there, since this repo already has them).
2. In the project folder:

```powershell
git init
git add .
git commit -m "Initial commit: social automation platform and MCP server"
git branch -M main
git remote add origin https://github.com/<YOUR_USER>/<YOUR_REPO>.git
git push -u origin main
```

Replace `<YOUR_USER>` and `<YOUR_REPO>` with your GitHub username and repository name. Use SSH instead if you prefer: `git@github.com:<YOUR_USER>/<YOUR_REPO>.git`.

**Security:** Never commit real API keys. This repo uses `config/api_keys.example.env` as a template; keep secrets in a local `.env` file (ignored by git).

---

## What This Does

| Capability | Platforms |
|------------|-----------|
| **Post content** | Twitter/X, Instagram, Facebook, LinkedIn, YouTube |
| **Schedule posts** | All 5 social platforms |
| **Fetch post analytics** | All 5 social platforms |
| **Fetch account analytics** | All 5 social platforms |
| **List ad campaigns** | Google Ads (incl. YouTube Ads) |
| **Get campaign metrics** | Google Ads |
| **Create campaigns** | Google Ads |
| **Pause campaigns** | Google Ads |

---

## Quick Start

### 1. Install dependencies
```bash
python -m venv .venv
.venv\Scripts\activate    # Windows
# source .venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
```

### 2. Configure API keys
```bash
cp config/api_keys.example.env .env
# Edit .env with your credentials
```
See [docs/setup/api_keys.md](docs/setup/api_keys.md) for per-platform setup instructions.

### 3. Test your connections
```bash
python scripts/test_connections.py
```

### 4. Register the MCP server with Claude Code
Add to `~/.claude/claude.json`:
```json
{
  "mcpServers": {
    "social-automation": {
      "command": "python",
      "args": ["<ABSOLUTE_PATH>/mcp-server/server.py"],
      "env": {
        "PYTHONPATH": "<ABSOLUTE_PATH>"
      }
    }
  }
}
```

### 5. Start automation (optional background processes)
```bash
# Post scheduler
python scripts/run_scheduler.py

# Analytics collector (runs every 24h)
python scripts/run_analytics_collector.py

# Campaign monitor (runs every 60min)
python scripts/run_campaign_monitor.py
```

---

## MCP Tools Available

Once registered with Claude Code, you can use these tools:

### Social Media
| Tool | Description |
|------|-------------|
| `post_to_platform` | Publish a post immediately |
| `schedule_post` | Schedule a post for a future time |
| `get_post_analytics` | Get metrics for a specific post |
| `get_account_analytics` | Get account-level metrics |

### Google Ads
| Tool | Description |
|------|-------------|
| `list_campaigns` | List all campaigns for an account |
| `get_campaign_metrics` | CTR, CPC, spend, conversions |
| `create_campaign` | Create a new campaign |
| `pause_campaign` | Pause a running campaign |

### Example Claude Code Prompts
```
Post "Big news dropping tomorrow! 🚀" to Twitter and LinkedIn
```
```
Schedule an Instagram post for 2026-03-15T14:00:00Z with the caption "New blog post is live!"
```
```
Get last 7 days analytics for Facebook
```
```
List all enabled Google Ads campaigns for customer 1234567890
```
```
Get campaign metrics for campaign 9876543 last month
```

---

## Project Structure

```
.
├── mcp-server/              # MCP server entry point + tools
├── integrations/            # Platform API clients
├── automation/              # Background automation engines
├── config/                  # Config templates and settings
├── docs/                    # Full documentation
│   ├── api/                 # Per-platform API reference
│   ├── setup/               # Installation & config guides
│   └── architecture/        # System overview + data flow
├── scripts/                 # Utility and background scripts
└── requirements.txt
```

---

## Documentation

| Document | Description |
|----------|-------------|
| [docs/setup/installation.md](docs/setup/installation.md) | Step-by-step installation |
| [docs/setup/api_keys.md](docs/setup/api_keys.md) | Per-platform API key setup |
| [docs/setup/running_mcp_server.md](docs/setup/running_mcp_server.md) | MCP server registration |
| [docs/architecture/system_overview.md](docs/architecture/system_overview.md) | Architecture + data flow |
| [docs/api/twitter_api.md](docs/api/twitter_api.md) | Twitter API reference |
| [docs/api/instagram_api.md](docs/api/instagram_api.md) | Instagram API reference |
| [docs/api/facebook_api.md](docs/api/facebook_api.md) | Facebook API reference |
| [docs/api/linkedin_api.md](docs/api/linkedin_api.md) | LinkedIn API reference |
| [docs/api/youtube_api.md](docs/api/youtube_api.md) | YouTube API reference |
| [docs/api/google_ads_api.md](docs/api/google_ads_api.md) | Google Ads API reference |

---

## Adding a New Platform

1. Create `integrations/<platform>/client.py`
2. Inherit from `integrations.base_client.BaseSocialClient`
3. Implement `create_post()`, `get_post_analytics()`, `get_account_analytics()`
4. Add the client to `_PLATFORM_CLIENTS` in `mcp-server/tools/social_tools.py`
5. Add credentials to `config/api_keys.example.env`
6. Create `docs/api/<platform>_api.md`

---

## Requirements
- Python 3.11+
- API accounts for the platforms you want to use
- Claude Code with MCP support
