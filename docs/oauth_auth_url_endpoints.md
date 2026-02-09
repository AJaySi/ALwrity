# Canonical OAuth Auth URL Endpoints

## Purpose
These endpoints provide a single backend source of truth for OAuth URLs and
metadata needed by the frontend, so the UI no longer needs to hardcode origins,
redirect URIs, or client IDs. They also enforce environment-driven redirect URI
validation to prevent prod/stage/dev mismatches.

## Endpoints
Base path: `/api/oauth`

### `GET /api/oauth/{provider}/auth-url`
Returns provider-specific OAuth URL data for the frontend. Supported providers:
- `wix`
- `wordpress`
- `bing`
- `gsc`

**Response shape (generic):**
```json
{
  "provider": "wix",
  "auth_url": "https://provider.example/...",
  "redirect_uri": "https://app.example/wix/callback",
  "client_id": "...",
  "state": "...",
  "oauth_data": {
    "state": "...",
    "codeVerifier": "...",
    "codeChallenge": "...",
    "redirectUri": "..."
  },
  "trusted_origins": ["https://app.example"]
}
```
Fields vary by provider:
- **Wix**: returns PKCE metadata (`oauth_data`) plus `trusted_origins` so the UI
  can validate postMessage origins.
- **WordPress/Bing**: return `state` and `redirect_uri` for popup flows.
- **GSC**: returns `redirect_uri` used when building the Google OAuth flow.

## Redirect URI Validation
Redirect URIs are validated server-side to ensure:
1. **`FRONTEND_URL` origin matches** the configured redirect origin (when
   `FRONTEND_URL` is set).
2. **`DEPLOY_ENV` matches** the inferred environment from the redirect origin:
   - `dev`: localhost, ngrok, `.local`
   - `stage`: host contains `staging` or `stage`
   - `prod`: everything else

If validation fails, the service logs the error and returns a configuration
error instead of generating the OAuth URL.

## Required Environment Variables
- `FRONTEND_URL`
- `DEPLOY_ENV` (`local`, `development`, `dev`, `staging`, `stage`, `production`, `prod`)
- `BING_REDIRECT_URI`
- `WORDPRESS_REDIRECT_URI`
- `WIX_REDIRECT_URI`
- `GSC_REDIRECT_URI`

Provider client credentials are still required per service:
- `BING_CLIENT_ID`, `BING_CLIENT_SECRET`
- `WORDPRESS_CLIENT_ID`, `WORDPRESS_CLIENT_SECRET`
- `WIX_CLIENT_ID`
- `GSC_CREDENTIALS_FILE`

## Frontend Integration Notes (Wix)
The onboarding flow calls `/api/oauth/wix/auth-url`, stores the returned
`oauth_data` and `client_id` in session storage, and navigates to the returned
`auth_url`. The callback page restores the stored data to complete the Wix SDK
PKCE flow.
