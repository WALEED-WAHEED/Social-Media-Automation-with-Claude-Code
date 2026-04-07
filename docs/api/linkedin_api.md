# LinkedIn Marketing API — Reference

## Official Documentation
https://learn.microsoft.com/en-us/linkedin/marketing/

---

## Authentication
LinkedIn uses **OAuth 2.0 Authorization Code Flow**.

### Required Credentials
```
LINKEDIN_ACCESS_TOKEN     # OAuth 2.0 access token
LINKEDIN_ORGANIZATION_ID  # URN: urn:li:organization:12345678
LINKEDIN_PERSON_ID        # URN: urn:li:person:abcDEF123
```

### Getting Credentials
1. Create an app at https://www.linkedin.com/developers/apps
2. Add the required products: **Marketing Developer Platform** and **Sign In with LinkedIn**.
3. Request the OAuth scopes listed below.
4. Implement the Authorization Code Flow:
   ```
   GET https://www.linkedin.com/oauth/v2/authorization
     ?response_type=code
     &client_id={client-id}
     &redirect_uri={redirect-uri}
     &scope=w_member_social%20r_organization_social%20...
   ```
5. Exchange code for access token:
   ```
   POST https://www.linkedin.com/oauth/v2/accessToken
   ```

---

## Required OAuth Scopes
```
w_member_social          # Post as member
r_liteprofile            # Read member profile
r_emailaddress           # Read email
w_organization_social    # Post as organization
r_organization_social    # Read organization posts
rw_ads                   # Manage ad campaigns (if using Ads API)
```

---

## Key Endpoints Used

### Create UGC Post (Company Page)
```
POST https://api.linkedin.com/v2/ugcPosts
```
**Headers:**
```
Authorization: Bearer {access_token}
X-Restli-Protocol-Version: 2.0.0
LinkedIn-Version: 202401
```
**Body:**
```json
{
  "author": "urn:li:organization:12345678",
  "lifecycleState": "PUBLISHED",
  "specificContent": {
    "com.linkedin.ugc.ShareContent": {
      "shareCommentary": { "text": "Check out our latest post!" },
      "shareMediaCategory": "NONE"
    }
  },
  "visibility": {
    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
  }
}
```
**Response:** `{ "id": "urn:li:ugcPost:7012345678901234567" }`

### Get Post Social Actions
```
GET https://api.linkedin.com/v2/socialActions/{ugcPostUrn}
```

### Get Organization Page Statistics
```
GET https://api.linkedin.com/v2/organizationalEntityShareStatistics
  ?q=organizationalEntity
  &organizationalEntity=urn:li:organization:12345678
  &timeIntervals.timeGranularityType=DAY
  &timeIntervals.timeRange.start=1709251200000
```

---

## Data Fields Available

| Field | Description |
|-------|-------------|
| `totalLikes` | Total likes on a post |
| `totalFirstLevelComments` | Direct comments on a post |
| `clickCount` | Clicks on post content |
| `impressionCount` | Times post was shown |
| `uniqueImpressionsCount` | Unique accounts that saw post |
| `shareCount` | Number of shares |
| `engagement` | Engagement rate (interactions / impressions) |
