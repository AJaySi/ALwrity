# Step 2 Dual Persistence Issue and Fix

## Problem Discovery

User reported that after our database migration changes, they cannot see previous analysis in Step 2's cache/existing analysis feature.

## Root Cause Analysis

### Two Competing Systems Writing to Same Table

Both systems write to `website_analyses` table but with **different `session_id` strategies**:

#### 1. Style Detection System (Original)
**Endpoints**: `/api/onboarding/style-detection/*`  
**Service**: `WebsiteAnalysisService`  
**Session ID Type**: `INTEGER` (SHA256 hash of Clerk user_id)

```python
# component_logic.py line 523
user_id_int = clerk_user_id_to_int(user_id)  # SHA256 hash → 724716666

# Saves to website_analyses table
analysis_service.save_analysis(user_id_int, request.url, response_data)
# Result: session_id = 724716666
```

#### 2. Onboarding System (New)
**Service**: `OnboardingDatabaseService`  
**Session ID Type**: Auto-increment integer from `OnboardingSession.id`

```python
# OnboardingDatabaseService
session = self.get_or_create_session(user_id, session_db)  # user_id is Clerk string
# session.id = 1, 2, 3, etc. (auto-increment)

# Saves to website_analyses table
analysis = WebsiteAnalysis(session_id=session.id, ...)  # session_id = 1, 2, 3...
```

### The Conflict

When a user analyzes their website:

1. **Analysis happens** → `/style-detection/complete` saves with `session_id = 724716666`
2. **Check existing** → Queries for `session_id = 724716666` ✅ **FINDS IT**
3. **User clicks Continue** → `OnboardingProgress.save_progress()` saves with `session_id = 3` (from `OnboardingSession.id`)
4. **Result**: **TWO records** in `website_analyses` for same URL but different `session_id` values!

```sql
-- Table: website_analyses
id  | session_id  | website_url           | writing_style | ...
----|-------------|-----------------------|---------------|----
42  | 724716666   | https://example.com   | {...}         | ... (from /style-detection/complete)
43  | 3           | https://example.com   | {...}         | ... (from OnboardingProgress.save_progress)
```

### Why User Can't See Previous Analysis

After our migration:
- `OnboardingSession.user_id` changed to **STRING** (Clerk ID)
- `OnboardingSession.id` is auto-increment (1, 2, 3...)
- Step 2 queries using SHA256 hash approach (724716666)
- Onboarding system saves using auto-increment ID (3)
- They never match!

## Solutions

### Option 1: Unified Session ID Strategy (RECOMMENDED)

Make **both systems** use the same `session_id` approach: the `OnboardingSession.id`.

**Changes Required**:

1. Update `/style-detection/complete` endpoint to use `OnboardingSession`:

```python
# backend/api/component_logic.py
@router.post("/style-detection/complete")
async def complete_style_detection(request, current_user):
    user_id = str(current_user.get('id'))
    
    # Get or create OnboardingSession (not SHA256 hash)
    from services.onboarding_database_service import OnboardingDatabaseService
    onboarding_service = OnboardingDatabaseService()
    db = next(get_db())
    session = onboarding_service.get_or_create_session(user_id, db)
    session_id = session.id  # Use OnboardingSession.id instead of hash
    
    # Save using this session_id
    analysis_service.save_analysis(session_id, request.url, response_data)
```

2. Update `check-existing` endpoint similarly:

```python
@router.get("/style-detection/check-existing/{website_url:path}")
async def check_existing_analysis(website_url, current_user):
    user_id = str(current_user.get('id'))
    
    # Get OnboardingSession (not SHA256 hash)
    onboarding_service = OnboardingDatabaseService()
    db = next(get_db())
    session = onboarding_service.get_session_by_user(user_id, db)
    
    if not session:
        return {"exists": False}
    
    # Query using OnboardingSession.id
    existing = analysis_service.check_existing_analysis(session.id, website_url)
    return existing
```

3. Update `get-analysis/:id` endpoint similarly.

### Option 2: Keep Dual System, Sync Both Records

Keep both approaches but ensure both records are created/updated together.

❌ **Not recommended** - More complexity, potential for sync issues.

### Option 3: Query Both Ways

Query by both session_id types and merge results.

❌ **Not recommended** - Hacky, doesn't solve root cause.

## Implementation Plan

### Phase 1: Update Style Detection Endpoints ✅

1. Update `/style-detection/complete` to use `OnboardingSession.id`
2. Update `/style-detection/check-existing/{url}` to use `OnboardingSession.id`
3. Update `/style-detection/analysis/{id}` to use `OnboardingSession.id`
4. Update `/style-detection/session-analyses` to use `OnboardingSession.id`

### Phase 2: Data Migration

Clean up duplicate records:

```sql
-- Keep only OnboardingSession-based records
DELETE FROM website_analyses 
WHERE session_id NOT IN (
    SELECT id FROM onboarding_sessions
);
```

### Phase 3: Remove SHA256 Hash Approach

Remove `clerk_user_id_to_int()` function as it's no longer needed.

## Benefits of Unified Approach

1. ✅ **Single source of truth** for session_id
2. ✅ **No duplicate records**
3. ✅ **Consistent user isolation**
4. ✅ **Simpler codebase**
5. ✅ **Cache/existing analysis works correctly**
6. ✅ **Step 6 can retrieve data**

## Status

- ⏳ **Pending**: Update style detection endpoints
- ⏳ **Pending**: Test existing analysis feature
- ⏳ **Pending**: Data migration script

---

**Next Action**: Update `/style-detection/*` endpoints to use `OnboardingSession.id` instead of SHA256 hash.

