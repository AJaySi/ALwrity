# Testing (Bypass Guide)

Local testing options to exercise Wix integration without onboarding blockers.

## Routes
| Option | URL | Purpose |
| --- | --- | --- |
| Primary | `http://localhost:3000/wix-test` | Main Wix test page |
| Backup | `http://localhost:3000/wix-test-direct` | Direct route (no protections) |
| Backend | `http://localhost:8000/api/wix/auth/url` | Direct API testing |

## How to Test
1. Start backend: `python start_alwrity_backend.py`  
2. Start frontend: `npm start`  
3. Navigate to `/wix-test`, connect account, publish a test post

## Env (backend)
```bash
WIX_CLIENT_ID=your_wix_client_id_here
WIX_REDIRECT_URI=http://localhost:3000/wix/callback
```

## Restore After Testing
- Re‑enable monitoring middleware in `backend/app.py` if disabled  
- Remove any temporary onboarding mocks  
- Restore `ProtectedRoute` for `/wix-test` if removed

## Expected Results
- No onboarding redirect
- Wix OAuth works
- Blog posting works
- No rate‑limit errors


