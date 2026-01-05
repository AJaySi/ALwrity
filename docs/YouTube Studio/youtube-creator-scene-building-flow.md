# YouTube Creator: Build Scenes from Plan - User Flow & Safeguards

## User Flow

### Step-by-Step Process

1. **User clicks "Build Scenes from Plan" button**
   - **Location**: `ScenesStep` component (Step 2)
   - **Condition**: Button only shows when `scenes.length === 0`
   - **Handler**: `handleBuildScenes()` in `YouTubeCreator.tsx`

2. **Frontend Validation**
   - ✅ Checks if `videoPlan` exists (shows error if missing)
   - ✅ **NEW**: Checks if scenes already exist (prevents duplicate calls)
   - ✅ Sets loading state to prevent double-clicks
   - ✅ Shows preflight check via `OperationButton` (subscription validation)

3. **API Call**
   - **Endpoint**: `POST /api/youtube/scenes`
   - **Payload**: `{ video_plan: VideoPlan, custom_script?: string }`
   - **Client**: `youtubeApi.buildScenes(videoPlan)`

4. **Backend Processing** (`YouTubeSceneBuilderService.build_scenes_from_plan`)
   
   **Optimization Strategy (minimizes AI calls):**
   
   a. **Check for existing scenes** (0 AI calls)
      - If `video_plan.scenes` exists and `_scenes_included=True` → Reuse scenes
      - Logs: `♻️ Reusing X scenes from plan - skipping generation`
   
   b. **Custom script parsing** (0 AI calls)
      - If `custom_script` provided → Parse into scenes without AI
   
   c. **Shorts optimization** (0 AI calls if already in plan)
      - If `duration_type="shorts"` and `_scenes_included=True` → Use normalized scenes
      - Otherwise → Generate scenes normally (1 AI call)
   
   d. **Medium/Long videos** (1-3 AI calls)
      - Generate scenes: 1 AI call
      - Batch enhance prompts:
        - Shorts: Skip enhancement (0 calls)
        - Medium: 1 batch call for all scenes (1 call)
        - Long: 2 batch calls, split scenes (2 calls)
   
   **Total AI calls per video type:**
   - **Shorts** (with optimization): 0-1 calls (0 if included in plan, 1 if not)
   - **Medium**: 2 calls (1 generation + 1 batch enhancement)
   - **Long**: 3 calls (1 generation + 2 batch enhancements)
   - **Custom script**: 0-2 calls (0 parsing + 0-2 enhancements)

5. **Response Processing**
   - Normalizes scene data (adds `enabled: true` by default)
   - Updates state via `updateState({ scenes: updatedScenes })`
   - Shows success message
   - Navigates to Step 2 (Scenes review)

## Safeguards to Prevent Wasting AI Calls

### Frontend Safeguards

1. **Button Visibility**
   - Button only appears when `scenes.length === 0`
   - Prevents accidental clicks when scenes exist

2. **Duplicate Call Prevention** ✅ **NEW**
   ```typescript
   if (scenes.length > 0) {
     console.warn('[YouTubeCreator] Scenes already exist, skipping build');
     setError('Scenes have already been generated...');
     return;
   }
   ```

3. **Loading State**
   - Button disabled during `loading` state
   - Prevents multiple simultaneous calls

4. **Preflight Check**
   - `OperationButton` performs subscription validation before API call
   - Shows cost estimate and subscription limits
   - Prevents calls if limits exceeded (but allows click to show modal)

### Backend Safeguards

1. **Scene Reuse Detection** ✅ **ENHANCED**
   - Checks `video_plan.scenes` and `_scenes_included` flag
   - Reuses existing scenes (0 AI calls)
   - Logs reuse to track optimization success

2. **Shorts Optimization**
   - When plan is generated with `include_scenes=True` for shorts
   - Scenes are included in plan generation (1 combined call)
   - Scene builder reuses them instead of regenerating

3. **Batch Processing**
   - Visual prompt enhancement batched (1-2 calls instead of N calls)
   - Shorts skip enhancement entirely (saves 1 call)

4. **Error Handling**
   - Graceful fallbacks if batch enhancement fails
   - Uses original prompts instead of failing completely

## Testing Recommendations

### To Test Without Wasting AI Calls

1. **Use Shorts Duration**
   - Scenes included in plan generation (optimized)
   - Scene building reuses existing scenes (0 calls)

2. **Use Custom Script**
   - Parse custom script (0 AI calls)
   - Still needs enhancement for medium/long (1-2 calls)

3. **Test with Existing Scenes**
   - Frontend guard prevents duplicate calls
   - Backend detects and reuses existing scenes

4. **Monitor Logs**
   - Look for `♻️ Reusing X scenes` messages
   - Verify `0 AI calls` for optimized paths
   - Check scene count matches expectations

### Log Messages to Watch

- `♻️ Reusing X scenes from plan - skipping generation` ✅ **NEW**
- `Using scenes from optimized plan+scenes call` (shorts optimization)
- `Skipping prompt enhancement for shorts` (saves 1 call)
- `Batch enhancing X scenes in 1 AI call` (medium optimization)
- `Batch enhancing X scenes in 2 AI calls` (long optimization)

## API Call Summary

| Video Type | Scenario | AI Calls | Details |
|------------|----------|----------|---------|
| Shorts | Plan with scenes | 0 | Reuses scenes from plan |
| Shorts | Plan without scenes | 1 | Generates scenes only (no enhancement) |
| Medium | Normal flow | 2 | 1 generation + 1 batch enhancement |
| Long | Normal flow | 3 | 1 generation + 2 batch enhancements |
| Any | Custom script | 0-2 | 0 parsing + 0-2 enhancements |

## Code References

- **Frontend Handler**: `frontend/src/components/YouTubeCreator/YouTubeCreator.tsx:214`
- **API Endpoint**: `backend/api/youtube/router.py:295`
- **Scene Builder**: `backend/services/youtube/scene_builder.py:26`
- **Operation Helper**: `frontend/src/components/YouTubeCreator/utils/operationHelpers.ts:136`

