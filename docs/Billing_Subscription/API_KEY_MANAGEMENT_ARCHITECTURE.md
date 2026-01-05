# API Key Management Architecture

## Overview

ALwrity supports two deployment modes with different API key management strategies:

1. **Local Development**: API keys stored in `.env` files for convenience
2. **Production (Vercel + Render)**: User-specific API keys stored in database with full user isolation

## Architecture

### 🏠 **Local Development Mode**

**Detection:**
- `DEBUG=true` in environment variables, OR
- `DEPLOY_ENV` is not set

**API Key Storage:**
- **Backend**: `backend/.env` file
- **Frontend**: `frontend/.env` file
- **Database**: Also saved for consistency

**Flow:**
```
User completes onboarding
    ↓
API keys saved to database (user-isolated)
    ↓
API keys ALSO saved to .env files (for convenience)
    ↓
Backend services read from .env file
    ↓
Single developer, single set of keys
```

**Advantages:**
- ✅ Quick setup for developers
- ✅ No need to configure environment for every user
- ✅ Keys persist across server restarts

---

### 🌐 **Production Mode (Vercel + Render)**

**Detection:**
- `DEBUG=false` or not set, AND
- `DEPLOY_ENV` is set (e.g., `DEPLOY_ENV=render`)

**API Key Storage:**
- **Backend**: PostgreSQL database (user-isolated)
- **Frontend**: `localStorage` (runtime only)
- **NOT in .env files**

**Flow:**
```
Alpha Tester A completes onboarding
    ↓
API keys saved to database with user_id_A
    ↓
Backend services fetch keys from database when user_id_A makes requests
    ↓
Multiple users, each with their own keys
    ↓
Alpha Tester B completes onboarding
    ↓
API keys saved to database with user_id_B
    ↓
Backend services fetch keys from database when user_id_B makes requests
```

**Advantages:**
- ✅ **Complete user isolation** - User A's keys never conflict with User B's keys
- ✅ **Zero cost for you** - Each alpha tester uses their own API keys
- ✅ **Secure** - Keys stored encrypted in database
- ✅ **Scalable** - Unlimited alpha testers, each with their own keys

---

## Implementation

### **1. Backend: User API Key Context**

The `UserAPIKeyContext` class provides user-specific API keys to backend services:

```python
from services.user_api_key_context import user_api_keys

# In your backend service
async def generate_content(user_id: str, prompt: str):
    # Get user-specific API keys
    with user_api_keys(user_id) as keys:
        gemini_key = keys.get('gemini')
        exa_key = keys.get('exa')
        
        # Use keys for this specific user
        response = await call_gemini_api(gemini_key, prompt)
        return response
```

**How it works:**
- **Development**: Reads from `backend/.env`
- **Production**: Fetches from database for the specific `user_id`

### **2. Frontend: CopilotKit Key Management**

```typescript
// Frontend automatically handles this:
// 1. Saves to localStorage (for runtime use)
// 2. In dev: Also saves to frontend/.env
// 3. In prod: Only uses localStorage

const copilotApiKey = localStorage.getItem('copilotkit_api_key');
```

### **3. Environment Variable Detection**

**Backend (`backend/.env`):**
```bash
# Development
DEBUG=true

# Production
DEBUG=false
DEPLOY_ENV=render  # or 'railway', 'heroku', etc.
```

**Render Dashboard:**
```
DEBUG=false
DEPLOY_ENV=render
```

**Vercel Dashboard:**
```
REACT_APP_API_URL=https://alwrity.onrender.com
REACT_APP_BACKEND_URL=https://alwrity.onrender.com
```

---

## Use Cases

### **Use Case 1: You (Developer) - Local Development**

**Setup:**
```bash
# backend/.env
DEBUG=true
GEMINI_API_KEY=your_personal_key
EXA_API_KEY=your_personal_key
COPILOTKIT_API_KEY=your_personal_key
```

**Behavior:**
- You complete onboarding once
- Keys saved to both database AND `.env` files
- All your local testing uses these keys
- No need to re-enter keys

---

### **Use Case 2: Alpha Tester A - Production**

**Setup:**
- Alpha Tester A visits `https://alwrity-ai.vercel.app`
- Goes through onboarding
- Enters their own API keys:
  - `GEMINI_API_KEY=tester_a_gemini_key`
  - `EXA_API_KEY=tester_a_exa_key`
  - `COPILOTKIT_API_KEY=tester_a_copilot_key`

**Behavior:**
- Keys saved to database with `user_id=tester_a_clerk_id`
- When Tester A generates content:
  - Backend fetches `tester_a_gemini_key` from database
  - Uses Tester A's Gemini quota
  - All costs charged to Tester A's Gemini account

---

### **Use Case 3: Alpha Tester B - Production (Same Time)**

**Setup:**
- Alpha Tester B visits `https://alwrity-ai.vercel.app`
- Goes through onboarding
- Enters their own API keys:
  - `GEMINI_API_KEY=tester_b_gemini_key`
  - `EXA_API_KEY=tester_b_exa_key`
  - `COPILOTKIT_API_KEY=tester_b_copilot_key`

**Behavior:**
- Keys saved to database with `user_id=tester_b_clerk_id`
- When Tester B generates content:
  - Backend fetches `tester_b_gemini_key` from database
  - Uses Tester B's Gemini quota
  - All costs charged to Tester B's Gemini account
- **Tester A and Tester B completely isolated** ✅

---

## Database Schema

```sql
-- OnboardingSession: One per user
CREATE TABLE onboarding_sessions (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) UNIQUE NOT NULL,  -- Clerk user ID
    current_step INTEGER DEFAULT 1,
    progress FLOAT DEFAULT 0.0,
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

-- APIKey: Multiple per user (one per provider)
CREATE TABLE api_keys (
    id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES onboarding_sessions(id),
    provider VARCHAR(50) NOT NULL,  -- 'gemini', 'exa', 'copilotkit'
    key TEXT NOT NULL,              -- Encrypted in production
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(session_id, provider)    -- One key per provider per user
);
```

**Isolation:**
- Each user has their own `onboarding_session`
- Each session has its own set of `api_keys`
- Query: `SELECT key FROM api_keys WHERE session_id = (SELECT id FROM onboarding_sessions WHERE user_id = ?)`

---

## Migration Path

### **Current State:**
- ❌ All users' keys overwrite the same `.env` file
- ❌ Last user's keys are used for all users

### **New State:**
- ✅ Development: `.env` file for convenience
- ✅ Production: Database per user
- ✅ Complete user isolation

### **Code Changes Required:**

**Before (BAD - uses global .env):**
```python
import os

def generate_content(prompt: str):
    gemini_key = os.getenv('GEMINI_API_KEY')  # Same for all users!
    response = call_gemini_api(gemini_key, prompt)
    return response
```

**After (GOOD - uses user-specific keys):**
```python
from services.user_api_key_context import user_api_keys

def generate_content(user_id: str, prompt: str):
    with user_api_keys(user_id) as keys:
        gemini_key = keys.get('gemini')  # User-specific key!
        response = call_gemini_api(gemini_key, prompt)
        return response
```

---

## Testing

### **Test Local Development:**
1. Set `DEBUG=true` in `backend/.env`
2. Complete onboarding with test keys
3. Check `backend/.env` - should contain keys ✅
4. Generate content - should use keys from `.env` ✅

### **Test Production:**
1. Set `DEBUG=false` and `DEPLOY_ENV=render` on Render
2. User A completes onboarding with keys A
3. User B completes onboarding with keys B
4. User A generates content - uses keys A ✅
5. User B generates content - uses keys B ✅
6. Check database:
   ```sql
   SELECT user_id, provider, key FROM api_keys 
   JOIN onboarding_sessions ON api_keys.session_id = onboarding_sessions.id;
   ```
   Should show separate keys for User A and User B ✅

---

## Security Considerations

### **Production Enhancements (Future):**
1. **Encrypt API keys** in database using application secret
2. **Rate limiting** per user to prevent abuse
3. **Key validation** before saving
4. **Audit logging** of API key usage
5. **Key rotation** support

### **Current Implementation:**
- ✅ Keys stored in database (not in code)
- ✅ User isolation via `user_id`
- ✅ HTTPS encryption in transit
- ⚠️ Keys not encrypted at rest (TODO)

---

## Troubleshooting

### **Issue: "No API key found"**
- **Development**: Check `backend/.env` file exists and has keys
- **Production**: Check database has keys for this user:
  ```sql
  SELECT * FROM api_keys 
  WHERE session_id = (SELECT id FROM onboarding_sessions WHERE user_id = 'user_xxx');
  ```

### **Issue: "Wrong user's keys being used"**
- **Cause**: Service not using `UserAPIKeyContext`
- **Fix**: Update service to use `user_api_keys(user_id)` context manager

### **Issue: "Keys not saving to .env in development"**
- **Cause**: `DEBUG` not set to `true`
- **Fix**: Set `DEBUG=true` in `backend/.env`

---

## Summary

| Feature | Local Development | Production |
|---------|------------------|------------|
| **Key Storage** | `.env` files + Database | Database only |
| **User Isolation** | Not needed (single user) | Full isolation |
| **Cost** | Your API keys | Each user's API keys |
| **Convenience** | High (keys persist) | Medium (enter once) |
| **Scalability** | 1 developer | Unlimited users |
| **Detection** | `DEBUG=true` | `DEPLOY_ENV` set |

**Bottom Line:**
- 🏠 **Local**: Quick setup, your keys, `.env` convenience
- 🌐 **Production**: User isolation, their keys, zero cost for you

This architecture ensures:
1. ✅ You can develop locally with convenience
2. ✅ Alpha testers use their own keys (no cost to you)
3. ✅ Complete user isolation in production
4. ✅ Seamless transition between environments

