# API Key Management Flow Diagrams

## 🏠 Local Development Mode

```
┌─────────────────────────────────────────────────────────────────────┐
│                         LOCAL DEVELOPMENT                            │
│                         (DEBUG=true)                                 │
└─────────────────────────────────────────────────────────────────────┘

Developer completes onboarding
            │
            ├─> Frontend: Save API keys
            │   └─> POST /api/onboarding/api-keys (gemini, exa, copilotkit)
            │
            ├─> Backend: Process API keys
            │   │
            │   ├─> Save to PostgreSQL database
            │   │   └─> onboarding_sessions (user_id)
            │   │       └─> api_keys (provider, key)
            │   │
            │   └─> Save to backend/.env file  [DEV MODE ONLY]
            │       ├─> GEMINI_API_KEY=xxx
            │       ├─> EXA_API_KEY=xxx
            │       └─> COPILOTKIT_API_KEY=xxx
            │
            └─> Frontend: Save CopilotKit to frontend/.env
                └─> REACT_APP_COPILOTKIT_API_KEY=xxx


Developer generates content
            │
            ├─> Service calls user_api_keys(user_id=None)
            │   │
            │   └─> Detects DEV mode (DEBUG=true)
            │       └─> Reads from backend/.env file
            │           └─> Returns all keys
            │
            └─> Content generated using developer's keys
                └─> All costs → Developer's API account


✅ Advantages:
   • Quick setup (keys persist in .env)
   • No database required for basic dev
   • Single developer = single set of keys
   • Keys survive server restarts
```

---

## 🌐 Production Mode (Multi-User)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    PRODUCTION (VERCEL + RENDER)                      │
│                    (DEBUG=false, DEPLOY_ENV=render)                  │
└─────────────────────────────────────────────────────────────────────┘

Alpha Tester A visits https://alwrity-ai.vercel.app
            │
            ├─> Completes onboarding
            │   └─> Enters API keys:
            │       ├─> GEMINI_API_KEY=tester_a_key
            │       ├─> EXA_API_KEY=tester_a_exa
            │       └─> COPILOTKIT_API_KEY=tester_a_copilot
            │
            ├─> Frontend: Save API keys
            │   ├─> POST /api/onboarding/api-keys (gemini, exa, copilotkit)
            │   └─> Save to localStorage (CopilotKit)
            │
            └─> Backend: Process API keys
                ├─> Save to PostgreSQL database ONLY [PROD MODE]
                │   └─> onboarding_sessions
                │       ├─> user_id = "user_clerk_tester_a"
                │       └─> api_keys
                │           ├─> (session_id, "gemini", "tester_a_key")
                │           ├─> (session_id, "exa", "tester_a_exa")
                │           └─> (session_id, "copilotkit", "tester_a_copilot")
                │
                └─> [SKIP] ❌ Do NOT save to .env file (multi-user conflict!)


Alpha Tester A generates blog content
            │
            ├─> Request to /api/blog/generate
            │   └─> Headers: Authorization: Bearer <tester_a_clerk_token>
            │
            ├─> Auth Middleware extracts user_id = "user_clerk_tester_a"
            │
            ├─> BlogService calls user_api_keys("user_clerk_tester_a")
            │   │
            │   ├─> Detects PROD mode (DEPLOY_ENV=render)
            │   │
            │   └─> Query database:
            │       SELECT key FROM api_keys
            │       WHERE session_id = (
            │           SELECT id FROM onboarding_sessions
            │           WHERE user_id = 'user_clerk_tester_a'
            │       )
            │       └─> Returns: {"gemini": "tester_a_key", "exa": "tester_a_exa"}
            │
            └─> Content generated using Tester A's Gemini key
                └─> All costs → Tester A's Gemini account


────────────────────────────────────────────────────────────────────────

SIMULTANEOUSLY...

Alpha Tester B visits https://alwrity-ai.vercel.app
            │
            ├─> Completes onboarding
            │   └─> Enters API keys:
            │       ├─> GEMINI_API_KEY=tester_b_key
            │       ├─> EXA_API_KEY=tester_b_exa
            │       └─> COPILOTKIT_API_KEY=tester_b_copilot
            │
            └─> Backend: Save to database
                └─> onboarding_sessions
                    ├─> user_id = "user_clerk_tester_b"
                    └─> api_keys
                        ├─> (session_id, "gemini", "tester_b_key")  [SEPARATE!]
                        ├─> (session_id, "exa", "tester_b_exa")
                        └─> (session_id, "copilotkit", "tester_b_copilot")


Alpha Tester B generates blog content
            │
            ├─> Request to /api/blog/generate
            │   └─> Headers: Authorization: Bearer <tester_b_clerk_token>
            │
            ├─> Auth Middleware extracts user_id = "user_clerk_tester_b"
            │
            ├─> BlogService calls user_api_keys("user_clerk_tester_b")
            │   │
            │   └─> Query database:
            │       WHERE user_id = 'user_clerk_tester_b'  [DIFFERENT!]
            │       └─> Returns: {"gemini": "tester_b_key", "exa": "tester_b_exa"}
            │
            └─> Content generated using Tester B's Gemini key
                └─> All costs → Tester B's Gemini account


✅ User Isolation:
   • Tester A's keys ≠ Tester B's keys
   • Tester A's costs ≠ Tester B's costs
   • Completely isolated in database
   • You (owner) pay nothing! 🎉
```

---

## 🔄 Environment Detection Logic

```
┌─────────────────────────────────────────────────────────────────────┐
│                    ENVIRONMENT DETECTION                             │
└─────────────────────────────────────────────────────────────────────┘

When user_api_keys(user_id) is called:

    ┌──────────────────────────────────┐
    │ Check environment variables      │
    └──────────────────────────────────┘
                   │
                   ├─> DEBUG=true OR DEPLOY_ENV=None
                   │   │
                   │   ├─> DEVELOPMENT MODE
                   │   │   └─> Read from backend/.env file
                   │   │       └─> os.getenv('GEMINI_API_KEY')
                   │   │
                   │   └─> Log: "[DEV MODE] Using .env file"
                   │
                   └─> DEBUG=false AND DEPLOY_ENV=render
                       │
                       ├─> PRODUCTION MODE
                       │   └─> Read from database
                       │       └─> SELECT key FROM api_keys WHERE user_id=?
                       │
                       └─> Log: "[PROD MODE] Using database for user {user_id}"


Example configurations:

    Local Development:
    ┌─────────────────────────────┐
    │ backend/.env                │
    ├─────────────────────────────┤
    │ DEBUG=true                  │
    │ GEMINI_API_KEY=dev_key      │
    │ EXA_API_KEY=dev_exa         │
    └─────────────────────────────┘
    
    Render Production:
    ┌─────────────────────────────┐
    │ Environment Variables       │
    ├─────────────────────────────┤
    │ DEBUG=false                 │
    │ DEPLOY_ENV=render           │
    │ DATABASE_URL=postgresql://  │
    └─────────────────────────────┘
```

---

## 📊 Database Schema Visualization

```
┌─────────────────────────────────────────────────────────────────────┐
│                    DATABASE SCHEMA                                   │
└─────────────────────────────────────────────────────────────────────┘

onboarding_sessions
┌────────────┬──────────────────────────┬─────────────┬──────────┐
│ id (PK)    │ user_id (UNIQUE)         │ current_step│ progress │
├────────────┼──────────────────────────┼─────────────┼──────────┤
│ 1          │ user_clerk_tester_a      │ 6           │ 100.0    │
│ 2          │ user_clerk_tester_b      │ 6           │ 100.0    │
│ 3          │ user_clerk_tester_c      │ 3           │ 50.0     │
└────────────┴──────────────────────────┴─────────────┴──────────┘

api_keys
┌────────────┬────────────┬──────────────┬────────────────────────┐
│ id (PK)    │ session_id │ provider     │ key                    │
│            │ (FK)       │              │                        │
├────────────┼────────────┼──────────────┼────────────────────────┤
│ 1          │ 1          │ gemini       │ tester_a_gemini_key    │ ← Tester A
│ 2          │ 1          │ exa          │ tester_a_exa_key       │ ← Tester A
│ 3          │ 1          │ copilotkit   │ tester_a_copilot_key   │ ← Tester A
├────────────┼────────────┼──────────────┼────────────────────────┤
│ 4          │ 2          │ gemini       │ tester_b_gemini_key    │ ← Tester B
│ 5          │ 2          │ exa          │ tester_b_exa_key       │ ← Tester B
│ 6          │ 2          │ copilotkit   │ tester_b_copilot_key   │ ← Tester B
├────────────┼────────────┼──────────────┼────────────────────────┤
│ 7          │ 3          │ gemini       │ tester_c_gemini_key    │ ← Tester C
│ 8          │ 3          │ exa          │ tester_c_exa_key       │ ← Tester C
└────────────┴────────────┴──────────────┴────────────────────────┘

Query to get Tester A's Gemini key:

    SELECT k.key
    FROM api_keys k
    JOIN onboarding_sessions s ON k.session_id = s.id
    WHERE s.user_id = 'user_clerk_tester_a'
      AND k.provider = 'gemini'
    
    Result: 'tester_a_gemini_key'


Query to get Tester B's Gemini key:

    SELECT k.key
    FROM api_keys k
    JOIN onboarding_sessions s ON k.session_id = s.id
    WHERE s.user_id = 'user_clerk_tester_b'
      AND k.provider = 'gemini'
    
    Result: 'tester_b_gemini_key'  [DIFFERENT!]
```

---

## 🔐 Security & Isolation

```
┌─────────────────────────────────────────────────────────────────────┐
│                    USER ISOLATION GUARANTEE                          │
└─────────────────────────────────────────────────────────────────────┘

Scenario: Both Tester A and Tester B generate content simultaneously

    Tester A's Request Thread:
    ┌────────────────────────────────────────────┐
    │ 1. Auth: user_id = "user_clerk_tester_a"   │
    │ 2. Fetch keys: WHERE user_id = tester_a    │
    │ 3. Get: gemini_key = "tester_a_key"        │
    │ 4. Generate with tester_a_key              │
    │ 5. Response to Tester A                    │
    └────────────────────────────────────────────┘
              ↓
         [Database]
              ↑
    ┌────────────────────────────────────────────┐
    │ 1. Auth: user_id = "user_clerk_tester_b"   │
    │ 2. Fetch keys: WHERE user_id = tester_b    │
    │ 3. Get: gemini_key = "tester_b_key"        │
    │ 4. Generate with tester_b_key              │
    │ 5. Response to Tester B                    │
    └────────────────────────────────────────────┘
    Tester B's Request Thread:


✅ Guarantees:
   • Tester A NEVER sees Tester B's keys
   • Tester B NEVER sees Tester A's keys
   • Tester A's costs charged to Tester A
   • Tester B's costs charged to Tester B
   • Database enforces isolation via user_id
   • Clerk auth ensures correct user_id
```

---

## 💰 Cost Distribution

```
┌─────────────────────────────────────────────────────────────────────┐
│                    WHO PAYS FOR WHAT?                                │
└─────────────────────────────────────────────────────────────────────┘

Local Development (You):
    Your API Keys → Your Costs
    ┌─────────────────────────────────────────────┐
    │ Developer generates 100 blog posts          │
    │ Uses: GEMINI_API_KEY from .env             │
    │ Cost: $5.00 → Charged to developer's       │
    │              Google Cloud account           │
    └─────────────────────────────────────────────┘


Production (Alpha Testers):
    Their API Keys → Their Costs
    ┌─────────────────────────────────────────────┐
    │ Tester A generates 50 blog posts            │
    │ Uses: tester_a_gemini_key from database     │
    │ Cost: $2.50 → Charged to Tester A's        │
    │              Google Cloud account           │
    └─────────────────────────────────────────────┘
    
    ┌─────────────────────────────────────────────┐
    │ Tester B generates 200 blog posts           │
    │ Uses: tester_b_gemini_key from database     │
    │ Cost: $10.00 → Charged to Tester B's       │
    │               Google Cloud account          │
    └─────────────────────────────────────────────┘
    
    ┌─────────────────────────────────────────────┐
    │ You (owner) host infrastructure             │
    │ Render: Free tier / $7/month                │
    │ Vercel: Free tier                           │
    │ Database: Render free tier                  │
    │ Cost: $0 - $7/month (infrastructure only)   │
    └─────────────────────────────────────────────┘


Total monthly cost for you with 100 alpha testers:
    Infrastructure: $0 - $7
    API usage: $0 (testers pay their own!)
    ────────────────────────────
    Total: $0 - $7/month 🎉
```

---

## 🎯 Summary

| Aspect | Local Dev | Production |
|--------|-----------|------------|
| **Environment** | `DEBUG=true` | `DEPLOY_ENV=render` |
| **Key Storage** | `.env` file + DB | Database only |
| **Key Retrieval** | `os.getenv()` | Database query |
| **User Isolation** | Not needed | Full isolation |
| **Cost Bearer** | You (developer) | Each tester |
| **Scalability** | 1 developer | Unlimited users |
| **Setup Effort** | Low (persist .env) | Low (onboard once) |

**Architecture Principle:**
> Development convenience with `.env` files, production isolation with database. Best of both worlds! 🚀

