# System Architecture Overview

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Claude Code                         │
│                  (AI Assistant / User)                  │
└────────────────────────┬────────────────────────────────┘
                         │  MCP Protocol (stdio)
                         ▼
┌─────────────────────────────────────────────────────────┐
│                    MCP Server                           │
│                 mcp-server/server.py                    │
│                                                         │
│  ┌──────────────────┐    ┌──────────────────────────┐  │
│  │  social_tools.py │    │     ads_tools.py          │  │
│  │                  │    │                           │  │
│  │ post_to_platform │    │ list_campaigns            │  │
│  │ schedule_post    │    │ get_campaign_metrics      │  │
│  │ get_post_analytics│   │ create_campaign           │  │
│  │ get_acct_analytics│   │ pause_campaign            │  │
│  └─────────┬────────┘    └────────────┬─────────────┘  │
└────────────┼───────────────────────────┼────────────────┘
             │                           │
             ▼                           ▼
┌────────────────────────┐   ┌───────────────────────────┐
│  Social Integrations   │   │    Ads Integration        │
│                        │   │                           │
│  twitter/client.py     │   │  google_ads/client.py     │
│  instagram/client.py   │   │  (Google Ads API v18)     │
│  facebook/client.py    │   └──────────────┬────────────┘
│  linkedin/client.py    │                  │
│  youtube/client.py     │                  │
└────────────┬───────────┘                  │
             │                              │
             ▼                              ▼
   ┌─────────────────────────────────────────────────┐
   │              External Platform APIs              │
   │                                                 │
   │  Twitter API v2  │  Instagram Graph API         │
   │  Facebook Graph  │  LinkedIn Marketing API      │
   │  YouTube Data v3 │  Google Ads API              │
   └─────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│                  Automation Layer                        │
│                                                         │
│  ┌──────────────────┐  ┌──────────────┐  ┌──────────┐  │
│  │    Scheduler     │  │  Analytics   │  │ Campaign │  │
│  │  (scheduler.py)  │  │  Collector   │  │ Monitor  │  │
│  │                  │  │ (collector.py│  │(monitor.py│ │
│  │ Persists jobs to │  │              │  │          │  │
│  │ data/scheduled   │  │ Saves to     │  │ Writes   │  │
│  │ _posts.json      │  │ data/analytics│ │ alerts   │  │
│  └──────────────────┘  └──────────────┘  └──────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## Data Flow

### Posting a Tweet via MCP

```
User → "Post this to Twitter"
  → Claude Code calls MCP tool: post_to_platform(platform="twitter", content="...")
  → MCP server routes to social_tools.handle_social_tool()
  → TwitterClient.create_post() is called
  → tweepy.Client.create_tweet() hits Twitter API v2
  → Returns { post_id, url, status: "published" }
  → Claude Code shows result to user
```

### Scheduling a Post

```
User → "Schedule this for tomorrow 2pm"
  → MCP tool: schedule_post(platform, content, scheduled_time)
  → Scheduler.schedule() writes job to data/scheduled_posts.json
  → Returns job_id to Claude Code
  → Background process (run_scheduler.py) checks every 60s
  → When scheduled_time passes, publishes via platform client
```

### Collecting Analytics

```
Background process (run_analytics_collector.py) runs every 24h
  → AnalyticsCollector.collect_all() runs concurrently
  → Each platform client.get_account_analytics() is called
  → Results saved to data/analytics/{platform}/{date}.json
  → MCP tool get_account_analytics() can also trigger on-demand
```

### Campaign Monitoring

```
Background process (run_campaign_monitor.py) runs every 60min
  → CampaignMonitor.check_all_campaigns() fetches ENABLED campaigns
  → get_campaign_metrics() queries today's spend/CTR/CPC
  → Thresholds evaluated (spend, CTR, CPC)
  → Alerts written to data/alerts/campaign_alerts.json
```

---

## Directory Structure

```
automation-platform/
├── mcp-server/              # MCP server (Claude Code interface)
│   ├── server.py            # Entry point
│   └── tools/
│       ├── social_tools.py  # Social media tool definitions + dispatcher
│       └── ads_tools.py     # Ads tool definitions + dispatcher
│
├── integrations/            # Platform API clients
│   ├── base_client.py       # Abstract base class
│   ├── twitter/client.py
│   ├── instagram/client.py
│   ├── facebook/client.py
│   ├── linkedin/client.py
│   ├── youtube/client.py
│   └── google_ads/client.py
│
├── automation/              # Background automation engines
│   ├── scheduler/           # Scheduled post queue
│   ├── analytics_collector/ # Periodic analytics snapshots
│   └── campaign_monitor/    # Ads campaign health monitoring
│
├── config/
│   ├── api_keys.example.env # Template — copy to .env
│   └── settings.py          # Typed config loader
│
├── data/                    # Auto-created at runtime
│   ├── scheduled_posts.json
│   ├── analytics/
│   └── alerts/
│
├── docs/
│   ├── api/                 # Per-platform API reference
│   ├── setup/               # Installation and configuration
│   └── architecture/        # This file
│
├── scripts/                 # Utility and background process scripts
├── requirements.txt
└── README.md
```

---

## Design Principles

1. **Thin MCP layer** — the MCP tools only handle routing and serialization; all business logic lives in the integration/automation modules.

2. **Flat async** — all platform clients are fully async (`async def`), enabling concurrent API calls.

3. **File-based persistence** — scheduled jobs and analytics snapshots use JSON files for simplicity and zero-dependency storage. Swap for a database by changing only the `_load`/`_save` methods.

4. **Environment-variable config** — no secrets are ever hardcoded. The `config/settings.py` module centralizes all env loading.

5. **Modular integrations** — each platform is a self-contained module. Adding a new platform means creating a new `integrations/<platform>/client.py` that inherits `BaseSocialClient`, then adding it to the social_tools registry.
