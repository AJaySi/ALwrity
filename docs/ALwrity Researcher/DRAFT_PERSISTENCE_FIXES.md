# Draft Persistence Fixes

## Issues Fixed

### 1. Draft Not Restoring on Page Refresh
**Problem**: When the page refreshed after clicking "Intent & Options", the intent analysis and queries were lost.

**Root Causes**:
- Draft restoration in `useResearchExecution` wasn't properly validating the restored data
- Timing issues between wizard state restoration and execution hook restoration
- Missing error handling for invalid draft data

**Fixes Applied**:
- Enhanced draft restoration with proper type validation
- Added comprehensive logging to track restoration process
- Improved error handling for invalid draft formats
- Ensured `intentAnalysis` is properly restored with all queries

### 2. Drafts Not Saving Immediately
**Problem**: Drafts were debounced (5-second delay), causing loss if page refreshed quickly.

**Root Causes**:
- Database saves were debounced to reduce API calls
- Critical saves (intent analysis completion) weren't prioritized

**Fixes Applied**:
- Removed debounce for critical saves (intent analysis completion)
- Immediate save when user clicks "Intent & Options"
- Immediate save when user confirms intent
- Debounce still applies for non-critical updates

### 3. Drafts Not Visible in Projects
**Problem**: User couldn't see drafts in "My Projects".

**Status Logic**:
- `"draft"` - Only keywords entered, no intent analysis
- `"in_progress"` - Intent analysis completed (after "Intent & Options")
- `"completed"` - Research results available

**Note**: After clicking "Intent & Options", projects are saved with status `"in_progress"`, not `"draft"`. This is correct behavior - they should appear in the projects list.

**To View Projects**:
- Projects are saved to database with status based on completion
- Use `/api/research/projects` endpoint to list projects
- Filter by `status=draft` for drafts, `status=in_progress` for active projects
- Currently, there's no UI component to display research projects (similar to PodcastMaker's ProjectList)

## Changes Made

### Frontend Changes

1. **`frontend/src/utils/researchDraftManager.ts`**:
   - Removed debounce for critical saves (intent analysis completion)
   - Added logging for save operations
   - Immediate database save when intent analysis completes

2. **`frontend/src/components/Research/hooks/useResearchExecution.ts`**:
   - Enhanced draft restoration with type validation
   - Added comprehensive logging
   - Improved error handling for invalid draft data
   - Immediate save on intent confirmation

3. **`frontend/src/components/Research/hooks/useResearchWizard.ts`**:
   - Enhanced logging for draft restoration
   - Better validation of restored draft data

4. **`frontend/src/components/Research/ResearchWizard.tsx`**:
   - Added draft restoration check
   - Enhanced logging for debugging

5. **`frontend/src/components/Research/steps/components/IntentConfirmationPanel/IntentConfirmationPanel.tsx`**:
   - Added validation to prevent execution with zero queries
   - Better error handling

### Backend Changes

No backend changes needed - the save endpoint already handles drafts correctly.

## How Draft Persistence Works

### Save Flow

1. **User enters keywords** → Saved to localStorage only
2. **User clicks "Intent & Options"** → Intent analysis completes
   - Saved to localStorage immediately
   - Saved to database immediately (critical save, no debounce)
   - Status: `"in_progress"`
3. **User confirms intent** → Confirmed intent saved
   - Saved to localStorage immediately
   - Saved to database immediately (critical save)
   - Status: `"in_progress"`
4. **Research completes** → Results saved
   - Saved to localStorage immediately
   - Saved to database immediately
   - Status: `"completed"`

### Restore Flow

1. **Page loads** → `useResearchWizard` restores wizard state from draft
2. **Execution hook initializes** → `useResearchExecution` restores intent analysis, confirmed intent, and results
3. **UI renders** → IntentConfirmationPanel shows restored intent analysis with queries

### Storage Keys

- `alwrity_research_draft` - Complete draft data (localStorage)
- `alwrity_research_draft_id` - Project UUID for updates (localStorage)
- `alwrity_last_draft_db_save` - Timestamp for debouncing (localStorage)

## Testing

To verify drafts are working:

1. **Enter keywords and click "Intent & Options"**
   - Check browser console for: `[ResearchDraftManager] ✅ Draft saved to database`
   - Check localStorage for `alwrity_research_draft`

2. **Refresh the page**
   - Check console for: `[useResearchExecution] ✅ Restored intent analysis from draft`
   - IntentConfirmationPanel should show with queries

3. **Check projects list**
   - Projects with `intent_analysis` have status `"in_progress"`
   - Use API endpoint: `GET /api/research/projects?status=in_progress`

## Future Improvements

1. **Add Research Projects List UI**:
   - Create `ResearchProjectList` component (similar to `PodcastMaker/ProjectList`)
   - Display drafts, in-progress, and completed projects
   - Allow users to resume drafts

2. **Auto-save on Field Changes**:
   - Save draft when user modifies intent fields
   - Debounced saves for non-critical changes

3. **Draft Expiration**:
   - Auto-archive old drafts (e.g., 30 days)
   - Clear localStorage drafts after successful completion

4. **Better Error Recovery**:
   - Retry failed database saves
   - Show user notification if draft save fails
