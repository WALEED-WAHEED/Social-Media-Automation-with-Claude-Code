# Facebook Ads — Meta Marketing API Reference

## Official Documentation
https://developers.facebook.com/docs/marketing-apis

---

## Overview
The Meta Marketing API (v25.0) is the official API for automating Facebook and Instagram advertising. It is separate from the organic Facebook Graph API used for page posting.

---

## Authentication

### Recommended: System User Token (Production Automation)
For fully automated, non-expiring token access:
1. Go to **Meta Business Manager** → Settings → Users → **System Users**
2. Create a System User with Admin role
3. Generate an access token for the System User
4. Assign the System User to your Ad Account with appropriate permissions

System User tokens **never expire** — ideal for automation.

### Alternative: Long-Lived User Token (60 days)
```
GET https://graph.facebook.com/oauth/access_token
  ?grant_type=fb_exchange_token
  &client_id={app-id}
  &client_secret={app-secret}
  &fb_exchange_token={short-lived-token}
```

### Required Credentials
```
FACEBOOK_ADS_ACCESS_TOKEN  # System User token (preferred) or long-lived user token
FACEBOOK_ADS_ACCOUNT_ID    # Format: act_XXXXXXXXXXXXXXXX
```

---

## Required App Permissions
```
ads_management          # Create and manage campaigns, ad sets, ads
ads_read                # Read ad account data
business_management     # Manage business assets
read_insights           # Access performance analytics
```

Standard (development) access is **automatic**. Advanced access (production/multi-client) requires App Review + Business Verification.

---

## API Version
Current: **v25.0** (January 2026)

---

## Key Endpoints

### List Campaigns
```
GET https://graph.facebook.com/v25.0/{act_account_id}/campaigns
  ?fields=id,name,status,objective,daily_budget,lifetime_budget
  &access_token={token}
```
**Response:**
```json
{
  "data": [
    {
      "id": "6042147342661",
      "name": "Spring Sale Campaign",
      "status": "ACTIVE",
      "objective": "OUTCOME_SALES",
      "daily_budget": "5000"
    }
  ]
}
```

### Create Campaign
```
POST https://graph.facebook.com/v25.0/{act_account_id}/campaigns
```
**Body (form-encoded):**
```
name=Spring Sale Campaign
objective=OUTCOME_SALES
status=PAUSED
daily_budget=5000
special_ad_categories=[]
access_token={token}
```
**Response:** `{ "id": "6042147342661" }`

### Get Campaign Insights (Analytics)
```
GET https://graph.facebook.com/v25.0/{campaign_id}/insights
  ?fields=campaign_name,impressions,clicks,ctr,cpc,spend,actions,reach
  &time_range={"since":"2026-03-01","until":"2026-03-11"}
  &level=campaign
  &access_token={token}
```
**Response:**
```json
{
  "data": [{
    "campaign_name": "Spring Sale Campaign",
    "impressions": "45200",
    "reach": "32100",
    "clicks": "1840",
    "ctr": "4.0708",
    "cpc": "0.54",
    "spend": "993.60",
    "actions": [
      { "action_type": "offsite_conversion.fb_pixel_purchase", "value": "124" }
    ]
  }]
}
```

### Pause Campaign
```
POST https://graph.facebook.com/v25.0/{campaign_id}
```
**Body:** `status=PAUSED&access_token={token}`

---

## Campaign Objectives (Current — 2026)

| Objective | Use Case |
|-----------|----------|
| `OUTCOME_AWARENESS` | Brand visibility, reach |
| `OUTCOME_TRAFFIC` | Website clicks, link clicks |
| `OUTCOME_ENGAGEMENT` | Likes, comments, shares, video views |
| `OUTCOME_LEADS` | Lead generation forms |
| `OUTCOME_APP_PROMOTION` | App installs and in-app events |
| `OUTCOME_SALES` | Conversions, catalog sales, ROAS |

> Note: Legacy objectives (CONVERSIONS, TRAFFIC, etc.) were deprecated in 2023. Use Outcome-based objectives above.

---

## Data Fields Available (Insights API)

| Metric | Description |
|--------|-------------|
| `impressions` | Total times ad was shown |
| `reach` | Unique accounts that saw the ad |
| `clicks` | Total clicks (all) |
| `ctr` | Click-through rate (%) |
| `cpc` | Cost per click (USD) |
| `spend` | Total amount spent (USD) |
| `actions` | Conversions, purchases, leads (by type) |
| `action_values` | Revenue value from actions |
| `frequency` | Average times each person saw the ad |
| `video_p25_watched_actions` | Videos watched 25% through |
| `video_p50_watched_actions` | Videos watched 50% through |
| `video_p100_watched_actions` | Videos watched to completion |

---

## Rate Limits
- **Standard tier:** 60 score max, decay 300s
- **Advanced tier:** 9,000 score max, decay 300s
- **Mutations:** Max 100 requests/second per app per ad account
- **Insights API:** 600 pts/hr (standard), 190,000+ pts/hr (advanced)

---

## Important Notes (2026)
- Attribution window changes (Jan 2026): 7-day and 28-day view-through windows removed from Insights API
- Advantage Shopping and App Campaign legacy APIs deprecated Q1 2026 — use Advantage+ structures
- All ads go through standard ad review regardless of API origin
- `special_ad_categories` field is **required** on campaign creation (use `[]` if none apply)
