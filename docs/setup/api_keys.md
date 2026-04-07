# API Keys Setup Guide

All credentials are stored in a `.env` file at the project root (`automation-platform/.env`).
**Never commit this file to version control.**

The template is at `config/api_keys.example.env`.

---

## Twitter / X

1. Go to https://developer.twitter.com/en/portal/dashboard
2. Click **Create Project** → **Create App**
3. Under **User authentication settings**, enable:
   - OAuth 1.0a
   - App permissions: **Read and Write**
   - Callback URL: `http://localhost:3000` (or any valid URL)
4. Go to **Keys and Tokens** tab:
   - Copy **API Key** → `TWITTER_API_KEY`
   - Copy **API Key Secret** → `TWITTER_API_SECRET`
   - Generate **Access Token and Secret** → `TWITTER_ACCESS_TOKEN` + `TWITTER_ACCESS_TOKEN_SECRET`
   - Copy **Bearer Token** → `TWITTER_BEARER_TOKEN`

---

## Instagram

1. Go to https://developers.facebook.com/ → **My Apps → Create App**
2. Choose **Business** app type
3. Add **Instagram Graph API** product
4. Connect your Facebook Page to Instagram Business/Creator account
5. Use the **Graph API Explorer** to generate a token with these permissions:
   - `instagram_basic`
   - `instagram_content_publish`
   - `instagram_manage_insights`
   - `pages_show_list`
6. Exchange for a long-lived token (valid 60 days; use System User for permanent tokens)
7. Set `INSTAGRAM_ACCESS_TOKEN` and `INSTAGRAM_BUSINESS_ACCOUNT_ID`

---

## Facebook

1. Same Facebook App as Instagram (or a new one)
2. Add **Pages API** product
3. Request permissions: `pages_manage_posts`, `pages_read_engagement`, `read_insights`
4. In Graph API Explorer, select your Page from the dropdown to get a **Page Access Token**
5. Exchange for long-lived token
6. Set `FACEBOOK_ACCESS_TOKEN` and `FACEBOOK_PAGE_ID`

---

## LinkedIn

1. Go to https://www.linkedin.com/developers/apps → **Create App**
2. Under **Products**, request **Marketing Developer Platform**
3. Under **Auth**, note your **Client ID** and **Client Secret**
4. Add OAuth redirect URL (e.g., `http://localhost:8000/callback`)
5. Run the OAuth flow to obtain an access token:
   ```bash
   python scripts/generate_linkedin_token.py
   ```
6. Set `LINKEDIN_ACCESS_TOKEN`, `LINKEDIN_ORGANIZATION_ID`, `LINKEDIN_PERSON_ID`

---

## YouTube

1. Go to https://console.cloud.google.com/
2. Create a new project (or use existing)
3. Enable **YouTube Data API v3** and **YouTube Analytics API**
4. Go to **APIs & Services → Credentials → Create OAuth 2.0 Client ID**
   - Application type: **Desktop app**
5. Download the JSON credentials file
6. Run the token generation script:
   ```bash
   python scripts/generate_youtube_token.py
   ```
7. Set `YOUTUBE_CLIENT_ID`, `YOUTUBE_CLIENT_SECRET`, `YOUTUBE_REFRESH_TOKEN`, `YOUTUBE_CHANNEL_ID`

---

## Google Ads

1. Go to https://ads.google.com → **Tools → API Center**
2. Apply for a **developer token** (test token is available immediately)
3. In Google Cloud Console, enable **Google Ads API** on the same project as YouTube
4. Create an OAuth 2.0 Client ID (Desktop app)
5. Run the token generation script:
   ```bash
   python scripts/generate_google_ads_token.py
   ```
6. Set all `GOOGLE_ADS_*` environment variables

---

## Testing Your Keys

After setting up all keys, run:
```bash
python scripts/test_connections.py
```

Each platform will be tested individually and you'll see which ones are configured correctly.
