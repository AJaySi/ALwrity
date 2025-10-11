# 🚨 CRITICAL: Onboarding Data Must Use Database

## Issue Summary

**Severity:** 🔴 CRITICAL  
**Impact:** User isolation, data persistence, security  
**Status:** ⚠️ NEEDS IMMEDIATE FIX AFTER DEPLOYMENT STABILIZES

## Problem Description

The onboarding system currently saves all user data to a JSON file (`.onboarding_progress.json`) instead of using the database. This causes multiple critical issues:

### 1. **No User Isolation** 🔴
- All users share the same JSON file
- User data can be overwritten by other users
- Privacy violation - users can see each other's data
- **Line:** `backend/services/api_key_manager.py:45`
- **Code:** `self.progress_file = progress_file or ".onboarding_progress.json"`

### 2. **Data Loss on Deployment** 🔴
- Render uses ephemeral filesystem
- File is deleted on every deployment/restart
- Users lose all onboarding progress
- Have to restart onboarding after each deployment

### 3. **No Scalability** 🔴
- Won't work with multiple backend instances
- File locking issues
- Race conditions
- Performance bottleneck

### 4. **Security Risk** 🔴
- API keys stored in plain text JSON file
- No encryption
- File accessible with filesystem access
- Should be in database with proper security

## Current Architecture

```
User completes step → OnboardingProgress.mark_step_completed()
                   → save_progress() (line 214)
                   → json.dump(progress_data, ".onboarding_progress.json")
```

**File Location:** `backend/.onboarding_progress.json`  
**Affected Code:**
- `backend/services/api_key_manager.py` (OnboardingProgress class)
- `backend/api/onboarding_utils/endpoints_core.py`
- `backend/api/onboarding_utils/step_management_service.py`

## Database Models Available

✅ **Good News:** Proper database models already exist!

**File:** `backend/models/onboarding.py`

```python
- OnboardingSession (user_id, current_step, progress, started_at, updated_at)
- APIKey (session_id, provider, key, created_at, updated_at)
- WebsiteAnalysis (session_id, website_url, analysis_date, writing_style, etc.)
- ResearchPreferences (session_id, research_depth, content_types, etc.)
```

**Database Schema:**
- ✅ User isolation via `user_id` and `session_id`
- ✅ Proper relationships and foreign keys
- ✅ Timestamps for audit trail
- ✅ JSON fields for complex data
- ✅ Cascade deletes for cleanup

## Required Changes

### Phase 1: Database Layer (Priority 1)

**File:** `backend/services/onboarding_database_service.py` (NEW)

```python
class OnboardingDatabaseService:
    """Database-backed onboarding service replacing JSON file storage."""
    
    def get_or_create_session(self, user_id: str) -> OnboardingSession:
        """Get existing session or create new one."""
        
    def get_progress(self, user_id: str) -> OnboardingProgress:
        """Load progress from database."""
        
    def save_step_data(self, user_id: str, step_number: int, data: Dict):
        """Save step data to database."""
        
    def mark_step_completed(self, user_id: str, step_number: int):
        """Mark step as completed in database."""
        
    def get_step_data(self, user_id: str, step_number: int) -> Dict:
        """Retrieve step data from database."""
```

### Phase 2: Refactor API Key Manager (Priority 1)

**File:** `backend/services/api_key_manager.py`

**Changes:**
1. Remove JSON file operations (lines 214-242)
2. Add database dependency injection
3. Replace `save_progress()` with database calls
4. Replace `load_progress()` with database queries
5. Add user_id parameter to all methods

**Before:**
```python
def mark_step_completed(self, step_number: int, data: Optional[Dict] = None):
    # ... update in-memory state ...
    self.save_progress()  # Saves to JSON file
```

**After:**
```python
def mark_step_completed(self, user_id: str, step_number: int, data: Optional[Dict] = None):
    # ... update database ...
    db_service.save_step_data(user_id, step_number, data)
    db_service.mark_step_completed(user_id, step_number)
```

### Phase 3: Update Endpoints (Priority 2)

**Files to Update:**
- `backend/api/onboarding_utils/endpoints_core.py`
- `backend/api/onboarding_utils/step_management_service.py`
- `backend/api/onboarding_utils/step3_routes.py`
- `backend/api/onboarding_utils/step4_persona_routes.py`

**Changes:**
1. Pass `user_id` from `get_current_user` to all service calls
2. Remove file-based caching
3. Use database queries for progress retrieval

### Phase 4: Migration Script (Priority 3)

**File:** `backend/scripts/migrate_onboarding_to_database.py` (NEW)

```python
def migrate_json_to_database():
    """
    Migrate existing .onboarding_progress.json to database.
    Only needed if production has existing data in JSON files.
    """
    # Read JSON file
    # Create database records
    # Backup JSON file
    # Delete JSON file
```

## Implementation Plan

### Step 1: Create Database Service (1-2 hours)
- [ ] Create `onboarding_database_service.py`
- [ ] Implement CRUD operations
- [ ] Add user isolation checks
- [ ] Write unit tests

### Step 2: Refactor API Key Manager (2-3 hours)
- [ ] Remove JSON file operations
- [ ] Add database calls
- [ ] Update method signatures with user_id
- [ ] Test with database

### Step 3: Update Endpoints (1-2 hours)
- [ ] Pass user_id to service calls
- [ ] Remove file-based logic
- [ ] Test each endpoint

### Step 4: Testing (2-3 hours)
- [ ] Test user isolation
- [ ] Test data persistence across deployments
- [ ] Test concurrent users
- [ ] Test error handling

### Step 5: Deployment (1 hour)
- [ ] Deploy to staging
- [ ] Run migration script if needed
- [ ] Deploy to production
- [ ] Monitor for issues

**Total Estimated Time:** 8-12 hours

## Temporary Mitigation

Until this is fixed, we must:

1. ✅ Add `.onboarding_progress.json` to `.gitignore`
2. ✅ Document that onboarding data will be lost on deployment
3. ⚠️ Warn users that onboarding must be completed in one session
4. ⚠️ Consider using Render's persistent disk (expensive workaround)

## Testing Checklist

After migration:

- [ ] User A completes onboarding
- [ ] User B completes onboarding
- [ ] Verify User A and User B data are separate
- [ ] Redeploy backend
- [ ] Verify both users' data persists
- [ ] User C starts onboarding
- [ ] Verify User C doesn't see User A or B data
- [ ] Test concurrent onboarding (multiple users at once)
- [ ] Verify API keys are stored securely
- [ ] Test onboarding restart (partial completion)

## Security Considerations

### Current (Insecure):
```json
{
  "steps": [
    {
      "step_number": 1,
      "data": {
        "api_keys": {
          "gemini": "ACTUAL_API_KEY_HERE",
          "exa": "ACTUAL_API_KEY_HERE"
        }
      }
    }
  ]
}
```

### After Migration (Secure):
- API keys in database with user isolation
- Encrypted at rest (if database supports it)
- Access controlled by user_id
- Audit trail via timestamps

## References

- Database Models: `backend/models/onboarding.py`
- Current Implementation: `backend/services/api_key_manager.py`
- Endpoints: `backend/api/onboarding_utils/`
- Issue tracking: GitHub Issue #XXX (to be created)

## Priority

**This must be fixed before:**
- ❌ Going to production with real users
- ❌ Accepting paying customers
- ❌ Handling sensitive data
- ❌ Scaling to multiple instances

**Acceptable to delay if:**
- ✅ Still in alpha/beta with limited users
- ✅ Users aware of data loss on deployment
- ✅ Not handling production workloads yet

## Conclusion

This is a critical architectural flaw that violates basic principles:
- User data isolation
- Data persistence
- Security best practices
- Scalability

**Must be fixed immediately after current deployment stabilizes.**

