# API Key Management - Quick Reference

## 🎯 The Big Picture

**Problem:** You want to develop locally with convenience, but alpha testers should use their own API keys (so you don't pay for their usage).

**Solution:** 
- **Local Dev**: API keys saved to `.env` files (convenient)
- **Production**: API keys saved to database per user (isolated, zero cost to you)

---

## 🚀 How It Works

### **1. Local Development (You)**

```bash
# backend/.env
DEBUG=true
GEMINI_API_KEY=your_key_here
EXA_API_KEY=your_exa_key
COPILOTKIT_API_KEY=your_copilot_key
```

**Behavior:**
- ✅ Complete onboarding once
- ✅ Keys saved to `.env` AND database
- ✅ All services use keys from `.env`
- ✅ Convenient, keys persist

**You pay for:** Your own API usage

---

### **2. Production (Alpha Testers)**

```bash
# Render environment variables
DEBUG=false
DEPLOY_ENV=render
DATABASE_URL=postgresql://...
```

**Behavior:**
- ✅ Each tester completes onboarding with their keys
- ✅ Keys saved to database (user-specific rows)
- ✅ Services fetch keys from database per user
- ✅ Complete user isolation

**You pay for:** $0-$7/month (infrastructure only)  
**Testers pay for:** Their own API usage

---

## 📝 Code Examples

### **Using User API Keys in Services**

```python
from services.user_api_key_context import user_api_keys
import google.generativeai as genai

def generate_blog(user_id: str, topic: str):
    # Get user-specific API keys
    with user_api_keys(user_id) as keys:
        gemini_key = keys.get('gemini')
        
        # Configure Gemini with THIS user's key
        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel('gemini-pro')
        
        # Generate content (charges THIS user's Gemini account)
        response = model.generate_content(f"Write a blog about {topic}")
        return response.text
```

**What this does:**
- **Dev mode** (`user_id=None` or `DEBUG=true`): Uses `.env` file
- **Prod mode** (`DEPLOY_ENV=render`): Fetches from database for this `user_id`

---

## 🔄 Migration Checklist

### **Step 1: Update Environment Variables**

**Local (backend/.env):**
```bash
DEBUG=true
# Your development API keys (stay as-is)
GEMINI_API_KEY=...
EXA_API_KEY=...
```

**Render Dashboard:**
```bash
DEBUG=false
DEPLOY_ENV=render
DATABASE_URL=postgresql://...
# Remove GEMINI_API_KEY, EXA_API_KEY from here!
# Users will provide their own via onboarding
```

### **Step 2: Update Services to Use user_api_keys**

**Before:**
```python
import os
gemini_key = os.getenv('GEMINI_API_KEY')  # ❌ Same for all users!
```

**After:**
```python
from services.user_api_key_context import user_api_keys
with user_api_keys(user_id) as keys:
    gemini_key = keys.get('gemini')  # ✅ User-specific!
```

### **Step 3: Update FastAPI Endpoints**

**Add user_id parameter:**
```python
@router.post("/api/generate")
async def generate(
    prompt: str,
    current_user: dict = Depends(get_current_user)  # Get authenticated user
):
    user_id = current_user.get('user_id')  # Extract user_id
    
    # Pass user_id to service
    result = await my_service.generate(user_id, prompt)
    return result
```

### **Step 4: Test**

**Local:**
1. Complete onboarding
2. Check `backend/.env` has your keys ✅
3. Generate content - should work ✅

**Production:**
1. Deploy to Render with `DEPLOY_ENV=render`
2. User A: Complete onboarding with keys A
3. User B: Complete onboarding with keys B
4. User A generates content → Uses keys A ✅
5. User B generates content → Uses keys B ✅

---

## 🔍 Troubleshooting

### **"No API key found" error**

**In development:**
```bash
# Check backend/.env exists and has:
DEBUG=true
GEMINI_API_KEY=your_key_here
```

**In production:**
```sql
-- Check database has keys for this user:
SELECT s.user_id, k.provider, k.key
FROM api_keys k
JOIN onboarding_sessions s ON k.session_id = s.id
WHERE s.user_id = 'user_xxx';
```

### **Wrong user's keys being used**

**Cause:** Service not using `user_api_keys(user_id)`

**Fix:**
```python
# OLD (wrong):
gemini_key = os.getenv('GEMINI_API_KEY')

# NEW (correct):
with user_api_keys(user_id) as keys:
    gemini_key = keys.get('gemini')
```

### **Keys not saving to .env in development**

**Cause:** `DEBUG` not set to `true`

**Fix:**
```bash
# backend/.env
DEBUG=true  # Must be explicitly true
```

---

## 📊 Cost Breakdown

### **Your Monthly Costs**

| Item | Dev | Production |
|------|-----|------------|
| **Infrastructure** | $0 | $0-7/month |
| **Database** | Free | Free (Render) |
| **API Usage (Gemini, Exa, etc.)** | Your usage | $0 (users pay!) |
| **Total** | Your API usage | $0-7/month |

### **Alpha Tester Costs**

| Item | Cost |
|------|------|
| **ALwrity Subscription** | Free (alpha) |
| **Their Gemini API** | Their usage |
| **Their Exa API** | Their usage |
| **Total** | Their API usage |

---

## 🎓 Key Concepts

### **Environment Detection**

```python
is_development = (
    os.getenv('DEBUG', 'false').lower() == 'true' or
    os.getenv('DEPLOY_ENV') is None
)

if is_development:
    # Use .env file (convenience)
    keys = load_from_env()
else:
    # Use database (user isolation)
    keys = load_from_database(user_id)
```

### **User Isolation**

```
Database guarantees:
┌──────────────────┬─────────────┬──────────────────┐
│ user_id          │ provider    │ key              │
├──────────────────┼─────────────┼──────────────────┤
│ user_tester_a    │ gemini      │ tester_a_key     │ ← Isolated
│ user_tester_b    │ gemini      │ tester_b_key     │ ← Isolated
└──────────────────┴─────────────┴──────────────────┘

Query for Tester A: WHERE user_id = 'user_tester_a'
Query for Tester B: WHERE user_id = 'user_tester_b'

No overlap, no conflicts!
```

---

## 🚀 Quick Start

### **For Local Development:**

1. Clone repo
2. Set `DEBUG=true` in `backend/.env`
3. Add your API keys to `backend/.env`
4. Run backend: `python start_alwrity_backend.py --dev`
5. Complete onboarding (keys auto-save to `.env`)
6. Done! ✅

### **For Production Deployment:**

1. Deploy backend to Render
2. Set environment variables:
   - `DEBUG=false`
   - `DEPLOY_ENV=render`
   - `DATABASE_URL=postgresql://...`
3. Deploy frontend to Vercel
4. Alpha testers complete onboarding with their keys
5. Done! Each tester uses their own keys ✅

---

## 📚 Further Reading

- [Complete Architecture Guide](./API_KEY_MANAGEMENT_ARCHITECTURE.md)
- [Usage Examples](./EXAMPLES_USER_API_KEYS.md)
- [Flow Diagrams](./API_KEY_FLOW_DIAGRAM.md)

---

## ✅ Summary

**The magic:**
- Same codebase works in both dev and prod
- Dev: Convenience of `.env` files
- Prod: Isolation via database
- Zero cost: Testers use their own API keys
- Automatic: Just set `DEBUG` and `DEPLOY_ENV`

**Bottom line:**
> Write code once, works everywhere. Development is convenient, production is isolated. You focus on building, testers pay for their usage. Win-win! 🎉

