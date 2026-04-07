# Instagram Graph API — Reference

## Official Documentation
https://developers.facebook.com/docs/instagram-api

---

## Authentication
Instagram uses the **Meta Graph API** with an **OAuth 2.0 Page Access Token**.

### Required Credentials
```
INSTAGRAM_ACCESS_TOKEN          # Long-lived Page/User access token
INSTAGRAM_BUSINESS_ACCOUNT_ID  # Instagram Business or Creator account ID
```

### Getting Credentials
1. Go to https://developers.facebook.com/ and create an app (Business type).
2. Add **Instagram Graph API** product.
3. Connect your Facebook Page to your Instagram Business/Creator account.
4. Generate a **User Access Token** with the required permissions.
5. Exchange for a **Long-Lived Token** (valid 60 days):
   ```
   GET https://graph.facebook.com/oauth/access_token
     ?grant_type=fb_exchange_token
     &client_id={app-id}
     &client_secret={app-secret}
     &fb_exchange_token={short-lived-token}
   ```

---

## Required Permissions (OAuth Scopes)
```
instagram_basic
instagram_content_publish
instagram_manage_insights
pages_show_list
pages_read_engagement
```

---

## Key Endpoints Used

### Create Media Container (Image)
```
POST https://graph.facebook.com/v19.0/{ig-user-id}/media
```
**Body:**
```json
{
  "image_url": "https://example.com/image.jpg",
  "caption": "My post caption #hashtag"
}
```
**Response:** `{ "id": "17889615814797799" }`

### Publish Container
```
POST https://graph.facebook.com/v19.0/{ig-user-id}/media_publish
```
**Body:**
```json
{ "creation_id": "17889615814797799" }
```
**Response:** `{ "id": "17854360229135492" }`

### Get Post Insights
```
GET https://graph.facebook.com/v19.0/{media-id}/insights
  ?metric=impressions,reach,likes,comments,shares,saved,profile_visits
  &period=lifetime
```
**Response:**
```json
{
  "data": [
    { "name": "impressions", "values": [{ "value": 4200 }] },
    { "name": "reach",       "values": [{ "value": 3100 }] },
    { "name": "likes",       "values": [{ "value": 120  }] }
  ]
}
```

### Get Account Insights
```
GET https://graph.facebook.com/v19.0/{ig-user-id}/insights
  ?metric=impressions,reach,follower_count,profile_views
  &period=day
  &since=2026-03-01
  &until=2026-03-11
```

---

## Data Fields Available

| Metric | Description |
|--------|-------------|
| `impressions` | Total times content was seen |
| `reach` | Unique accounts that saw content |
| `likes` | Number of likes |
| `comments` | Number of comments |
| `shares` | Number of shares |
| `saved` | Number of saves |
| `profile_visits` | Profile visits from the post |
| `follower_count` | Daily follower count change |
| `profile_views` | Daily profile view count |

---

## Notes
- **Personal accounts** are NOT supported — requires Business or Creator account.
- Instagram does **not** support text-only posts; at least one media file is required.
- Carousel posts require creating individual child containers first.
- Video/Reel uploads use `media_type=REELS` and `video_url`.
