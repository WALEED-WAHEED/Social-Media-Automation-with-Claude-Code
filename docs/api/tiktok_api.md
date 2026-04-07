# TikTok API — Reference

## Official Documentation
- Content Posting API: https://developers.tiktok.com/doc/content-posting-api-get-started
- Marketing API: https://business-api.tiktok.com/portal/docs

---

## ⚠️ Access Warning
TikTok API access requires **manual review and approval**. It is NOT automatic.
- Apply at: https://developers.tiktok.com/
- Review typically takes **2–7 days** (no guaranteed timeline)
- Access can be **denied** based on country, business type, or documentation
- TikTok tightened requirements in 2025 — provide thorough documentation

**Leave all `TIKTOK_*` env vars blank until you have approved access.**

---

## Authentication
OAuth 2.0 (RFC 6749 standard).

### Required Credentials
```
TIKTOK_APP_ID         # From TikTok Developer Portal
TIKTOK_APP_SECRET     # From TikTok Developer Portal
TIKTOK_ACCESS_TOKEN   # OAuth 2.0 access token (expires every 24 hours)
TIKTOK_REFRESH_TOKEN  # Used to obtain new access tokens without user re-consent
TIKTOK_ADVERTISER_ID  # Ad account ID (Marketing API only)
TIKTOK_OPEN_ID        # User open_id (Content Posting API)
```

### Token Refresh (Every 24 Hours)
```
POST https://open.tiktokapis.com/v2/oauth/token/
```
**Body:**
```json
{
  "client_key": "{app_id}",
  "client_secret": "{app_secret}",
  "grant_type": "refresh_token",
  "refresh_token": "{refresh_token}"
}
```

### Required OAuth Scopes
```
video.upload            # Upload video content
video.publish           # Publish to TikTok profile
video.query             # Read video metrics
user.info.basic         # Basic profile info
advertiser.read         # Read ad account data
report.read             # Access ad performance reports
campaign.management     # Create and manage campaigns
```

---

## Content Posting API

### Initialize Video Upload
```
POST https://open.tiktokapis.com/v2/post/publish/video/init/
Authorization: Bearer {access_token}
```
**Body:**
```json
{
  "post_info": {
    "title": "Your caption here",
    "privacy_level": "PUBLIC_TO_EVERYONE",
    "disable_comment": false,
    "disable_duet": false,
    "disable_stitch": false
  },
  "source_info": {
    "source": "FILE_UPLOAD",
    "video_size": 15728640,
    "chunk_size": 15728640,
    "total_chunk_count": 1
  }
}
```
**Response:** `{ "data": { "publish_id": "...", "upload_url": "..." } }`

### Upload Video (PUT to upload_url)
```
PUT {upload_url}
Content-Type: video/mp4
Content-Length: {size}
Content-Range: bytes 0-{size-1}/{size}

[binary video data]
```

### Get Video Analytics
```
POST https://open.tiktokapis.com/v2/video/query/
Authorization: Bearer {access_token}
```
**Body:**
```json
{
  "filters": { "video_ids": ["7123456789012345678"] },
  "fields": ["id", "title", "view_count", "like_count", "comment_count", "share_count", "reach"]
}
```

---

## Marketing API (Paid Ads)

### List Campaigns
```
GET https://business-api.tiktok.com/open_api/v1.3/campaign/get/
Access-Token: {access_token}
```
**Params:** `advertiser_id={id}&fields=["campaign_id","campaign_name","status","budget"]`

### Get Campaign Performance Report
```
GET https://business-api.tiktok.com/open_api/v1.3/report/integrated/get/
Access-Token: {access_token}
```
**Body:**
```json
{
  "advertiser_id": "7000000000000",
  "report_type": "BASIC",
  "dimensions": ["campaign_id"],
  "metrics": ["spend", "impressions", "clicks", "ctr", "cpc", "conversions"],
  "start_date": "2026-03-01",
  "end_date": "2026-03-11"
}
```

---

## Data Fields Available

### Organic (Content Posting API)
| Field | Description |
|-------|-------------|
| `view_count` | Total video views |
| `like_count` | Number of likes |
| `comment_count` | Number of comments |
| `share_count` | Number of shares |
| `reach` | Unique viewers |

### Paid (Marketing API)
| Metric | Description |
|--------|-------------|
| `spend` | Total ad spend |
| `impressions` | Times ad was shown |
| `clicks` | Ad clicks |
| `ctr` | Click-through rate |
| `cpc` | Cost per click |
| `conversions` | Conversion events |
| `video_play_actions` | Video play starts |
| `video_watched_2s` | 2-second video views |
| `video_watched_6s` | 6-second video views |

---

## Rate Limits
| Endpoint | Limit |
|----------|-------|
| Content publishing | 2 videos/minute, **20 videos/day** (hard limit) |
| General API endpoints | 600 requests/minute |
| Data refresh requirement | Every **15 days** |

---

## Known Limitations
- Cannot edit published posts via API
- No custom thumbnails (frame selection only)
- No line breaks in captions
- No direct messaging via API
- No livestream comment fetching
- All posts are public by default (unaudited clients may be restricted to private)
- No sentiment analysis or AI enrichment permitted on fetched data
- Unofficial scraping/workarounds risk permanent account bans
- Not available in all countries
