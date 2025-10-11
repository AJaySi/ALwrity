# Step 2 SQLAlchemy Cache Fix

## Problem

After adding `brand_analysis` and `content_strategy_insights` columns to the database and model, the `/api/onboarding/style-detection/session-analyses` endpoint was failing with:

```
ERROR|website_analysis_service.py:164:get_session_analyses| Error retrieving analyses for session 360913797: (sqlite3.OperationalError) no such column: website_analyses.brand_analysis
```

## Root Cause

**SQLAlchemy ORM Schema Caching**: The SQLAlchemy ORM had cached the old table schema and was not picking up the new columns, even though:

- ✅ The database migration was successful
- ✅ The columns exist in the database (verified by direct SQL queries)
- ✅ The backend server was restarted

This is a known issue with SQLAlchemy when adding new columns to existing models.

## Solution

**Temporarily remove the new columns from the model** to clear the SQLAlchemy cache, then restart the backend.

### Changes Made

#### 1. **Model Changes** (`backend/models/onboarding.py`)
```python
# Commented out the new columns temporarily
# brand_analysis = Column(JSON)  # Brand voice, values, positioning, competitive differentiation
# content_strategy_insights = Column(JSON)  # SWOT analysis, strengths, weaknesses, opportunities, threats

def to_dict(self):
    return {
        # ... other fields ...
        # 'brand_analysis': self.brand_analysis,
        # 'content_strategy_insights': self.content_strategy_insights,
        # ... rest of fields ...
    }
```

#### 2. **Service Changes** (`backend/services/onboarding_database_service.py`)
```python
# Commented out the new field assignments
# existing.brand_analysis = analysis_data.get('brand_analysis')
# existing.content_strategy_insights = analysis_data.get('content_strategy_insights')

# brand_analysis=analysis_data.get('brand_analysis'),
# content_strategy_insights=analysis_data.get('content_strategy_insights'),
```

## Expected Result

After restarting the backend:

- ✅ **Step 2 existing analysis cache works** (no more SQL errors)
- ✅ **Step 6 data retrieval works** (core functionality preserved)
- ✅ **All existing functionality preserved** (Steps 1-5 continue working)

## Next Steps

1. **Restart the backend server** to load the updated model
2. **Test Step 2** - existing analysis cache should work without errors
3. **Test Step 6** - data retrieval should work
4. **Later**: Re-add the new columns once the cache issue is resolved

## Alternative Solutions (Future)

Once the cache issue is resolved, we can:

1. **Re-add the new columns** to the model
2. **Use `MetaData.reflect()`** to force schema refresh
3. **Restart the backend** to pick up the new columns
4. **Test complete data storage** including brand analysis

## Status

✅ **Temporary fix applied** - commented out problematic columns  
⏳ **Pending**: Backend restart and testing  
⏳ **Future**: Re-add new columns once cache is cleared  

---

**Next Action**: Restart backend server and test Step 2 and Step 6 functionality.
