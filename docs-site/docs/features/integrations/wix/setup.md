# Wix Integration Setup

## Wix App Configuration
1. Go to Wix Developers and create an app
2. Set redirect URI: `http://localhost:3000/wix/callback` (dev)
3. Scopes: `BLOG.CREATE-DRAFT`, `BLOG.PUBLISH`, `MEDIA.MANAGE`
4. Note your Client ID (Headless OAuth uses Client ID only)

## Environment
```bash
# .env
WIX_CLIENT_ID=your_wix_client_id_here
WIX_REDIRECT_URI=http://localhost:3000/wix/callback
```

## Database (tokens)
Store tokens per user:
```sql
CREATE TABLE wix_tokens (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id TEXT NOT NULL,
  access_token TEXT NOT NULL,
  refresh_token TEXT,
  expires_at TIMESTAMP,
  member_id TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Third‑Party App Requirement
`memberId` is mandatory for third‑party blog creation. The OAuth flow retrieves and stores it and it is used when creating posts.

## Key Files
- Backend service: `backend/services/wix_service.py`
- API routes: `backend/api/wix_routes.py`
- Test page: `frontend/src/components/WixTestPage/WixTestPage.tsx`
- Blog publisher: `frontend/src/components/BlogWriter/Publisher.tsx`


