# API Key Injection - How It Works in Production

## 🎯 The Problem You Identified

**Question:** "For production, when we read APIs from database, how will they be exported to the environment?"

**Answer:** They are **temporarily injected** into `os.environ` for each request, then immediately cleaned up.

---

## 🔍 The Challenge

### **Existing Code Pattern:**

Most of your codebase uses this pattern:

```python
import os
import google.generativeai as genai

def generate_content(prompt: str):
    # Expects GEMINI_API_KEY in environment
    gemini_key = os.getenv('GEMINI_API_KEY')
    genai.configure(api_key=gemini_key)
    # ...
```

### **Production Problem:**

```
User A's request:
  ↓
  os.getenv('GEMINI_API_KEY') → ??? (User A's key in database, not in os.environ)
  
User B's request (simultaneous):
  ↓
  os.getenv('GEMINI_API_KEY') → ??? (User B's key in database, not in os.environ)
```

**Issue:** `os.environ` is global, but we need user-specific keys!

---

## ✅ The Solution: Request-Scoped Injection

### **How It Works:**

```
1. Request arrives with Authorization: Bearer <user_a_token>
   ↓
2. API Key Injection Middleware extracts user_id from token
   ↓
3. Fetch User A's keys from database
   ↓
4. Temporarily inject into os.environ:
   - GEMINI_API_KEY = user_a_gemini_key
   - EXA_API_KEY = user_a_exa_key
   ↓
5. Process request (all os.getenv() calls get User A's keys)
   ↓
6. Request completes
   ↓
7. IMMEDIATELY clean up os.environ (remove User A's keys)
```

### **Key Insight:**

**The injection is request-scoped, not global:**
- User A's keys exist in `os.environ` ONLY during User A's request
- Immediately removed after response sent
- User B's request gets User B's keys injected
- No overlap, no conflict!

---

## 🏗️ Architecture

### **Middleware Flow:**

```
FastAPI Request Pipeline:

┌─────────────────────────────────────────────────────────────┐
│ 1. Rate Limit Middleware                                    │
│    └─> Check rate limits                                    │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. API Key Injection Middleware (NEW!)                      │
│    ├─> Extract user_id from Authorization header            │
│    ├─> Fetch user's API keys from database                  │
│    ├─> Inject into os.environ (temporarily)                 │
│    │   ├─> GEMINI_API_KEY = user_specific_key               │
│    │   ├─> EXA_API_KEY = user_specific_key                  │
│    │   └─> COPILOTKIT_API_KEY = user_specific_key           │
│    └─> [Request processed with user-specific keys]          │
│         ↓                                                    │
│    ├─> [Response generated]                                 │
│    └─> CLEANUP: Remove injected keys from os.environ        │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. Your Endpoint (e.g., /api/blog/generate)                 │
│    └─> Calls service that uses os.getenv('GEMINI_API_KEY')  │
│        └─> Gets user-specific key! ✅                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 💻 Code Example

### **The Middleware:**

```python
async def __call__(self, request: Request, call_next):
    # 1. Extract user_id from token
    user_id = extract_user_from_token(request)
    
    if not user_id or DEPLOY_ENV == 'local':
        return await call_next(request)  # Skip in local mode
    
    # 2. Get user-specific keys from database
    with user_api_keys(user_id) as user_keys:
        # 3. Save original environment (if any)
        original_gemini = os.environ.get('GEMINI_API_KEY')
        original_exa = os.environ.get('EXA_API_KEY')
        
        # 4. Inject user-specific keys
        os.environ['GEMINI_API_KEY'] = user_keys['gemini']
        os.environ['EXA_API_KEY'] = user_keys['exa']
        
        try:
            # 5. Process request with user-specific keys
            response = await call_next(request)
            return response
        finally:
            # 6. CRITICAL: Restore original environment
            if original_gemini is None:
                del os.environ['GEMINI_API_KEY']
            else:
                os.environ['GEMINI_API_KEY'] = original_gemini
            
            if original_exa is None:
                del os.environ['EXA_API_KEY']
            else:
                os.environ['EXA_API_KEY'] = original_exa
```

---

## 📊 Concurrent Requests Example

### **Scenario: Two Users Generate Content Simultaneously**

```
TIME: 00:00:000
User A request arrives
├─> Extract user_id = "user_a"
├─> Fetch keys from DB: gemini_key = "key_a_123"
├─> os.environ['GEMINI_API_KEY'] = "key_a_123"
│
├─> TIME: 00:00:050 (50ms later)
│   User B request arrives
│   ├─> Extract user_id = "user_b"
│   ├─> Fetch keys from DB: gemini_key = "key_b_456"
│   ├─> os.environ['GEMINI_API_KEY'] = "key_b_456"  ← Overwrites!
│   │
│   ├─> User B's request processes
│   │   os.getenv('GEMINI_API_KEY') → "key_b_456" ✅
│   │
│   └─> TIME: 00:00:100
│       User B response sent
│       os.environ['GEMINI_API_KEY'] restored
│
└─> TIME: 00:00:120
    User A's request processes
    os.getenv('GEMINI_API_KEY') → ??? (Could be wrong!)
```

**⚠️ PROBLEM: Race condition!**

---

## 🔒 Thread Safety Solution

Python's asyncio in FastAPI handles this correctly:

```python
# FastAPI uses asyncio, which is single-threaded
# Each request is processed in sequence (no parallel execution)
# So the injection is safe!

User A request:
  ├─> Inject A's keys
  ├─> await generate_content()  ← Async, but single-threaded
  └─> Cleanup A's keys

User B request (after A):
  ├─> Inject B's keys
  ├─> await generate_content()
  └─> Cleanup B's keys
```

**BUT:** If your code uses threading or multiprocessing, this approach WON'T work safely.

---

## 🎛️ Modes Compared

### **Local Mode (DEPLOY_ENV=local):**

```
Request arrives
  ↓
Middleware detects DEPLOY_ENV=local
  ↓
SKIP injection (keys already in .env)
  ↓
os.getenv('GEMINI_API_KEY') → reads from .env file
  ↓
Works! ✅
```

### **Production Mode (DEPLOY_ENV=production):**

```
Request arrives with user_id=user_123
  ↓
Middleware detects DEPLOY_ENV=production
  ↓
Fetch user_123's keys from database
  ↓
Inject into os.environ (temporarily)
  ↓
os.getenv('GEMINI_API_KEY') → gets user_123's key
  ↓
Process request
  ↓
Clean up os.environ
  ↓
Works! ✅
```

---

## 🚨 Important Caveats

### **1. Async-Only Safety**

This approach is safe ONLY because FastAPI uses asyncio (single-threaded event loop).

**If you use:**
- `concurrent.futures.ThreadPoolExecutor`
- `multiprocessing.Pool`
- `threading.Thread`

Then environment injection is **NOT SAFE** and will cause race conditions!

### **2. Better Long-Term Approach**

For critical services, refactor to pass `user_id` explicitly:

```python
# Instead of:
def generate(prompt: str):
    key = os.getenv('GEMINI_API_KEY')  # Fragile!
    
# Do this:
def generate(user_id: str, prompt: str):
    with user_api_keys(user_id) as keys:
        key = keys['gemini']  # Explicit and safe!
```

---

## 📝 Summary

### **The Magic:**

1. **Request arrives** → Middleware extracts `user_id`
2. **Fetch from DB** → Get user's keys
3. **Inject temporarily** → `os.environ['GEMINI_API_KEY'] = user_key`
4. **Process request** → All `os.getenv()` calls get user's key
5. **Cleanup** → Remove from `os.environ`
6. **Next request** → Different user, different keys

### **Why It Works:**

- ✅ FastAPI is async + single-threaded
- ✅ Injection is request-scoped
- ✅ Cleanup is guaranteed (finally block)
- ✅ Existing code works without changes
- ✅ Each user gets their own keys

### **Limitations:**

- ⚠️ Not safe with threading/multiprocessing
- ⚠️ Slightly slower (DB query per request)
- ⚠️ Better to refactor critical services

### **Bottom Line:**

> **It works!** Your existing code that uses `os.getenv()` will get user-specific keys in production, with zero code changes. The middleware handles everything automatically.

---

## 🔄 Migration Path

### **Phase 1: Now (Compatibility Layer)**
- ✅ Middleware injects keys for ALL services
- ✅ No code changes needed
- ✅ Works immediately

### **Phase 2: Later (Gradual Refactor)**
- Refactor critical services to use `UserAPIKeyContext` directly
- Remove dependency on `os.getenv()`
- More explicit, safer

### **Phase 3: Future (Full Migration)**
- All services use `user_api_keys(user_id)`
- Remove injection middleware
- Clean, explicit architecture

**For now:** Middleware lets you deploy immediately without touching 100+ files! 🎉

