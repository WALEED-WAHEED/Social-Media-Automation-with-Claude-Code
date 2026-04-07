# YouTube Data API v3 — Reference

## Official Documentation
https://developers.google.com/youtube/v3

---

## Authentication
YouTube uses **OAuth 2.0** via Google Cloud Console.

### Required Credentials
```
YOUTUBE_CLIENT_ID      # OAuth 2.0 Client ID
YOUTUBE_CLIENT_SECRET  # OAuth 2.0 Client Secret
YOUTUBE_REFRESH_TOKEN  # Long-lived refresh token
YOUTUBE_CHANNEL_ID     # Your YouTube channel ID (UC...)
```

### Getting Credentials
1. Go to https://console.cloud.google.com/
2. Create or select a project.
3. Enable **YouTube Data API v3** and **YouTube Analytics API**.
4. Go to **APIs & Services → Credentials → Create OAuth 2.0 Client ID**.
5. Run the OAuth consent flow to get a refresh token:
   ```bash
   python scripts/generate_youtube_token.py
   ```
   This will open a browser for consent and save the refresh token.

---

## Required OAuth Scopes
```
https://www.googleapis.com/auth/youtube.upload
https://www.googleapis.com/auth/youtube.readonly
https://www.googleapis.com/auth/yt-analytics.readonly
```

---

## Key Endpoints Used

### Upload Video
```
POST https://www.googleapis.com/upload/youtube/v3/videos
  ?part=snippet,status
  &uploadType=resumable
```
**Body:**
```json
{
  "snippet": {
    "title": "My Video Title",
    "description": "Video description here",
    "tags": ["tag1", "tag2"],
    "categoryId": "22"
  },
  "status": {
    "privacyStatus": "public"
  }
}
```
**Response:**
```json
{
  "kind": "youtube#video",
  "id": "dQw4w9WgXcQ",
  "snippet": { "title": "My Video Title" }
}
```

### Get Video Statistics
```
GET https://www.googleapis.com/youtube/v3/videos
  ?part=statistics
  &id={video-id}
```
**Response:**
```json
{
  "items": [{
    "statistics": {
      "viewCount": "125430",
      "likeCount": "4210",
      "commentCount": "342",
      "favoriteCount": "0"
    }
  }]
}
```

### Get Channel Analytics (YouTube Analytics API)
```
GET https://youtubeanalytics.googleapis.com/v2/reports
  ?ids=channel=={channel-id}
  &startDate=2026-02-11
  &endDate=2026-03-11
  &metrics=views,estimatedMinutesWatched,averageViewDuration,likes,shares,subscribersGained
  &dimensions=day
```

---

## Data Fields Available

| Field | Description |
|-------|-------------|
| `viewCount` | Total views on a video |
| `likeCount` | Likes on a video |
| `commentCount` | Comments on a video |
| `views` | Channel views (Analytics API) |
| `estimatedMinutesWatched` | Total watch time in minutes |
| `averageViewDuration` | Avg seconds watched per view |
| `subscribersGained` | New subscribers in period |
| `subscribersLost` | Unsubscribes in period |
| `shares` | Video shares |

---

## Video Category IDs (Common)
| ID | Category |
|----|----------|
| 1 | Film & Animation |
| 10 | Music |
| 22 | People & Blogs |
| 24 | Entertainment |
| 27 | Education |
| 28 | Science & Technology |
