# Authentication Pattern Alignment

## Review Summary

After reviewing BlogWriter, StoryWriter, and PodcastDashboard components, we've aligned content-planning authentication with the established pattern.

## Established Pattern (BlogWriter/StoryWriter/PodcastDashboard)

1. **ProtectedRoute** handles authentication at route level
   - Waits for Clerk to load (`isLoaded`)
   - Checks if user is signed in (`isSignedIn`)
   - Only renders children when authenticated

2. **Components** don't check authentication
   - Assume they're authenticated (ProtectedRoute ensures this)
   - Make API calls directly without auth checks
   - Rely on API client interceptors for token injection

3. **API Client Interceptors** handle token injection
   - Automatically add `Authorization: Bearer <token>` header
   - Use `authTokenGetter` function set by TokenInstaller

## Changes Applied to Content Planning

### 1. Removed Component-Level Auth Checks ✅

**Files Updated:**
- `ContentStrategyTab.tsx`
- `ContentPlanningDashboard.tsx`

**Before:**
```typescript
const { isLoaded, isSignedIn } = useAuth();

useEffect(() => {
  if (!isLoaded) return;
  if (!isSignedIn) return;
  loadInitialData();
}, [isLoaded, isSignedIn]);
```

**After:**
```typescript
// ProtectedRoute ensures user is authenticated before component renders
useEffect(() => {
  loadInitialData();
}, []);
```

### 2. Enhanced API Client Interceptor ✅

**File Updated:**
- `client.ts`

**Changes:**
- Reject requests if `authTokenGetter` is not set (instead of just warning)
- This prevents 401 errors from requests made before authentication is ready
- Matches the pattern where ProtectedRoute ensures auth is ready before components render

**Before:**
```typescript
if (!authTokenGetter) {
  console.warn('⚠️ authTokenGetter not set - request may fail');
  // Request proceeds anyway → 401 error
}
```

**After:**
```typescript
if (!authTokenGetter) {
  console.error('❌ authTokenGetter not set - rejecting request');
  return Promise.reject(new Error('Authentication not ready...'));
}
```

### 3. Removed Redundant API Service Checks ✅

**File Updated:**
- `contentPlanningApi.ts`

**Changes:**
- Removed manual auth checks from `getStrategies()` method
- Rely on API client interceptor to handle authentication
- Matches pattern used by `blogWriterApi` and `storyWriterApi`

### 4. EventSource Authentication Support ✅

**Files Updated:**
- `contentPlanningApi.ts` (frontend)
- `streaming_endpoints.py` (backend)

**Changes:**
- EventSource doesn't support custom headers, so tokens are passed as query parameters
- Backend uses `get_current_user_with_query_token` to accept tokens from query params
- This is the standard pattern for SSE endpoints that require authentication

## Authentication Flow (Aligned Pattern)

1. **User navigates to `/content-planning`**
2. **ProtectedRoute checks:**
   - Waits for Clerk to load (`isLoaded`)
   - Checks if user is signed in (`isSignedIn`)
   - Only renders `ContentPlanningDashboard` when authenticated
3. **Component renders and makes API calls**
4. **API Client Interceptor:**
   - Checks if `authTokenGetter` is set (should be, since ProtectedRoute passed)
   - Gets token from Clerk
   - Adds `Authorization: Bearer <token>` header
5. **Backend validates token and processes request**

## Benefits

✅ **Consistent Pattern** - Matches BlogWriter/StoryWriter/PodcastDashboard
✅ **Simpler Components** - No redundant auth checks
✅ **Better Error Handling** - Interceptor rejects requests if auth isn't ready
✅ **ProtectedRoute Guarantee** - Components can assume authentication is ready
✅ **EventSource Support** - Streaming endpoints work with query parameter tokens

## Status: ✅ ALIGNED

Content planning now follows the same authentication pattern as other components in the codebase.
