# Facebook Graph API — Reference

## Official Documentation
https://developers.facebook.com/docs/graph-api

---

## Authentication
Facebook uses **OAuth 2.0 Page Access Tokens** for page management.

### Required Credentials
```
FACEBOOK_ACCESS_TOKEN  # Long-lived Page access token
FACEBOOK_PAGE_ID       # Facebook Page ID
```

### Getting Credentials
1. Create a Facebook App at https://developers.facebook.com/
2. Add **Pages API** product.
3. Generate a **User Access Token** via Graph API Explorer.
4. Exchange for a **Page Access Token**:
   ```
   GET https://graph.facebook.com/{page-id}
     ?fields=access_token
     &access_token={user-access-token}
   ```
5. Convert to **Long-Lived Token** (never expires if using System User):
   ```
   GET https://graph.facebook.com/oauth/access_token
     ?grant_type=fb_exchange_token
     &client_id={app-id}
     &client_secret={app-secret}
     &fb_exchange_token={short-lived-token}
   ```

---

## Required Permissions
```
pages_manage_posts
pages_read_engagement
pages_show_list
read_insights
public_profile
```

---

## Key Endpoints Used

### Create Text Post
```
POST https://graph.facebook.com/v19.0/{page-id}/feed
```
**Body:**
```json
{
  "message": "Hello from the API!",
  "link": "https://example.com"
}
```
**Response:** `{ "id": "123456789_987654321" }`

### Create Photo Post
```
POST https://graph.facebook.com/v19.0/{page-id}/photos
```
**Body:**
```json
{
  "url": "https://example.com/image.jpg",
  "message": "Check out this image!"
}
```

### Get Post Insights
```
GET https://graph.facebook.com/v19.0/{post-id}/insights
  ?metric=post_impressions,post_reach,post_engaged_users,post_clicks
```
**Response:**
```json
{
  "data": [
    {
      "name": "post_impressions",
      "values": [{ "value": 5420, "end_time": "2026-03-11T07:00:00+0000" }]
    },
    {
      "name": "post_reach",
      "values": [{ "value": 3800 }]
    }
  ]
}
```

### Get Page Insights
```
GET https://graph.facebook.com/v19.0/{page-id}/insights
  ?metric=page_fans,page_impressions,page_reach,page_engaged_users
  &period=day
  &since=2026-03-01
  &until=2026-03-11
```

---

## Data Fields Available

| Metric | Description |
|--------|-------------|
| `post_impressions` | Total times post was shown |
| `post_reach` | Unique users who saw the post |
| `post_engaged_users` | Users who engaged with post |
| `post_clicks` | Total clicks on post |
| `post_reactions_by_type_total` | Reactions broken down by type |
| `page_fans` | Total page likes (followers) |
| `page_impressions` | Page content impressions |
| `page_reach` | Unique users who saw page content |
| `page_engaged_users` | Users who interacted with page |
