# Installation Guide

## Prerequisites
- Python 3.11 or higher
- pip (comes with Python)
- Git

---

## Step 1: Clone or Open the Project

If you received the project as a folder, open a terminal inside `automation-platform/`.

```bash
cd automation-platform
```

---

## Step 2: Create a Virtual Environment

```bash
# Create the environment
python -m venv .venv

# Activate it
# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Windows (CMD)
.venv\Scripts\activate.bat

# macOS / Linux
source .venv/bin/activate
```

---

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `mcp` — Model Context Protocol server SDK
- `tweepy` — Twitter API client
- `httpx` — Async HTTP client (Instagram, Facebook, LinkedIn)
- `google-api-python-client` — YouTube API
- `google-ads` — Google Ads API
- `python-dotenv` — `.env` file loader

---

## Step 4: Configure API Keys

```bash
cp config/api_keys.example.env .env
```

Open `.env` in a text editor and fill in your credentials.
See [docs/setup/api_keys.md](api_keys.md) for detailed instructions per platform.

---

## Step 5: Verify the Installation

```bash
python scripts/test_connections.py
```

This tests connectivity to each platform using your configured keys.
A ✓ means connected, ✗ means something needs fixing.

---

## Step 6: Run the MCP Server

```bash
python mcp-server/server.py
```

See [docs/setup/running_mcp_server.md](running_mcp_server.md) for full details.
