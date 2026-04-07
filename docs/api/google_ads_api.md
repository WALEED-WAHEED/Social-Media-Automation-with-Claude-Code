# Google Ads API — Reference

## Official Documentation
https://developers.google.com/google-ads/api/docs/start

---

## Authentication
Google Ads API uses **OAuth 2.0** with a **developer token**.

### Required Credentials
```
GOOGLE_ADS_DEVELOPER_TOKEN   # From Google Ads Manager account
GOOGLE_ADS_CLIENT_ID         # OAuth 2.0 Client ID
GOOGLE_ADS_CLIENT_SECRET     # OAuth 2.0 Client Secret
GOOGLE_ADS_REFRESH_TOKEN     # Long-lived refresh token
GOOGLE_ADS_LOGIN_CUSTOMER_ID # Manager (MCC) account ID (optional)
```

### Getting Credentials

**1. Get a Developer Token:**
- Sign in to Google Ads at https://ads.google.com
- Go to **Tools → API Center**
- Apply for a developer token (test tokens available immediately)

**2. Create OAuth Credentials:**
- Go to https://console.cloud.google.com/
- Enable **Google Ads API**
- Create **OAuth 2.0 Client ID** (Desktop app type)

**3. Generate Refresh Token:**
```bash
pip install google-auth-oauthlib
python scripts/generate_google_ads_token.py
```

---

## Google Ads Query Language (GAQL)
The API uses GAQL — a SQL-like query language.

### Example: List Campaigns
```sql
SELECT
  campaign.id,
  campaign.name,
  campaign.status,
  campaign.advertising_channel_type,
  campaign_budget.amount_micros
FROM campaign
WHERE campaign.status = 'ENABLED'
ORDER BY campaign.id
```

### Example: Get Campaign Metrics
```sql
SELECT
  campaign.id,
  campaign.name,
  metrics.impressions,
  metrics.clicks,
  metrics.ctr,
  metrics.average_cpc,
  metrics.conversions,
  metrics.cost_micros
FROM campaign
WHERE campaign.id = 12345678
  AND segments.date BETWEEN '2026-02-11' AND '2026-03-11'
```

---

## Key API Services Used

| Service | Purpose |
|---------|---------|
| `GoogleAdsService.search_stream` | Execute GAQL queries |
| `CampaignService.mutate_campaigns` | Create/update/pause campaigns |
| `CampaignBudgetService.mutate_campaign_budgets` | Manage budgets |

---

## Campaign Creation Flow

1. **Create a Campaign Budget**
2. **Create a Campaign** (linked to the budget)
3. **Create Ad Groups** under the campaign
4. **Create Ads** inside ad groups
5. **Add Keywords** (for Search campaigns)

---

## Data Fields Available

| Metric | Description |
|--------|-------------|
| `metrics.impressions` | Times ad was shown |
| `metrics.clicks` | Times ad was clicked |
| `metrics.ctr` | Click-through rate (clicks/impressions) |
| `metrics.average_cpc` | Average cost-per-click (micros) |
| `metrics.conversions` | Number of conversions |
| `metrics.cost_micros` | Total spend in micros (÷ 1M = USD) |
| `metrics.conversion_value` | Total conversion value |
| `metrics.roas` | Return on ad spend |

---

## Budget Micros
All monetary values use **micros** (1/1,000,000 of the account currency).

```python
# $5.00 daily budget
budget_micros = 5 * 1_000_000  # = 5_000_000

# Convert spend to USD
spend_usd = cost_micros / 1_000_000
```

---

## YouTube Ads
YouTube Ads are managed through Google Ads API using:
- **Campaign type:** `VIDEO`
- **Ad format:** `VIDEO_RESPONSIVE_AD` or `IN_STREAM_AD`
- Analytics available through the same GAQL metrics
