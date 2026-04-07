# Twitter / X API — Reference

## Official Documentation
https://developer.twitter.com/en/docs/twitter-api

---

## Authentication
Twitter API v2 supports two auth methods:

| Method | Use Case |
|--------|----------|
| **OAuth 1.0a User Context** | Write endpoints (post tweets, upload media) |
| **OAuth 2.0 Bearer Token** | Read-only endpoints (search, analytics) |

### Required Credentials
```
TWITTER_API_KEY              # App API Key (consumer key)
TWITTER_API_SECRET           # App API Secret (consumer secret)
TWITTER_ACCESS_TOKEN         # User access token
TWITTER_ACCESS_TOKEN_SECRET  # User access token secret
TWITTER_BEARER_TOKEN         # App-only Bearer Token
```

### Getting Credentials
1. Go to https://developer.twitter.com/en/portal/dashboard
2. Create a project and app.
3. Enable "Read and Write" permissions under User authentication settings.
4. Generate Access Token & Secret from the Keys and Tokens tab.
5. Enable OAuth 1.0a with callback URL (e.g., `http://localhost:3000`).

---

## Required App Permissions
- `Read` — for analytics
- `Write` — for creating tweets
- `Direct Messages` — only if DM automation is needed

---

## Key Endpoints Used

### Create Tweet
```
POST https://api.twitter.com/2/tweets
```
**Auth:** OAuth 1.0a
**Body:**
```json
{
  "text": "Hello world!",
  "media": { "media_ids": ["123456789"] }
}
```
**Response:**
```json
{
  "data": {
    "id": "1234567890",
    "text": "Hello world!"
  }
}
```

### Get Tweet Metrics
```
GET https://api.twitter.com/2/tweets/:id
```
**Auth:** Bearer Token
**Query params:** `tweet.fields=public_metrics`
**Response:**
```json
{
  "data": {
    "id": "1234567890",
    "public_metrics": {
      "impression_count": 1200,
      "like_count": 45,
      "retweet_count": 12,
      "reply_count": 3,
      "quote_count": 2,
      "bookmark_count": 8,
      "url_link_clicks": 30
    }
  }
}
```

### Get Authenticated User
```
GET https://api.twitter.com/2/users/me
```
**Query params:** `user.fields=public_metrics`

---

## Data Fields Available

| Field | Description |
|-------|-------------|
| `impression_count` | Times tweet was seen |
| `like_count` | Number of likes |
| `retweet_count` | Number of retweets |
| `reply_count` | Number of replies |
| `quote_count` | Number of quote tweets |
| `bookmark_count` | Number of bookmarks |
| `url_link_clicks` | Clicks on URLs in the tweet |
| `followers_count` | Account followers (account metrics) |
| `tweet_count` | Total tweets from account |

---

## API Tiers & Rate Limits

| Tier | Monthly Tweets | Analytics Depth |
|------|---------------|-----------------|
| Free | 1,500 write/month | None |
| Basic ($100/mo) | 3,000 write/month | Basic metrics |
| Pro ($5,000/mo) | Full access | Full metrics + Ads |

> **Note:** Impression counts on individual tweets require at minimum the **Basic** tier.
