# Content Strategy Authentication & Subscription Review

## 🎯 **Executive Summary**

This document reviews the content strategy feature's AI prompt calls to ensure they pass through `main_text_generation` with proper subscription and pre-flight checks. The review identified critical gaps where AI calls bypass subscription validation.

**Review Date**: January 2025  
**Status**: ⚠️ **CRITICAL ISSUES FOUND**

---

## 🔍 **Critical Findings**

### **Issue 1: AI Calls Bypass Subscription Checks** ❌ **CRITICAL**

**Problem**: Content strategy AI calls do NOT pass through `main_text_generation` with subscription checks.

**Current Flow**:
```
StrategyAnalyzer.call_ai_service()
  → AIServiceManager.execute_structured_json_call()
    → AIServiceManager._execute_ai_call()
      → AIServiceManager._call_gemini_structured()
        → gemini_structured_json_response() [DIRECT CALL - NO SUBSCRIPTION CHECK]
```

**Expected Flow**:
```
StrategyAnalyzer.call_ai_service(user_id)
  → AIServiceManager.execute_structured_json_call(user_id)
    → llm_text_gen(prompt, schema, user_id=user_id) [WITH SUBSCRIPTION CHECK]
```

**Impact**: 
- ❌ No subscription limit enforcement
- ❌ No usage tracking
- ❌ No pre-flight validation
- ❌ Potential cost abuse

---

### **Issue 2: Missing User ID in AI Service Calls** ❌ **CRITICAL**

**Problem**: `AIServiceManager.execute_structured_json_call()` does NOT accept or pass `user_id`.

**Current Code**:
```python
# backend/services/ai_service_manager.py:553
async def execute_structured_json_call(self, service_type: AIServiceType, prompt: str, schema: Dict[str, Any]) -> Dict[str, Any]:
    """Public wrapper to execute a structured JSON AI call with a provided schema."""
    return await self._execute_ai_call(service_type, prompt, schema)
```

**Missing**: `user_id` parameter

**Impact**: Cannot pass user_id to subscription checks even if we wanted to.

---

### **Issue 3: StrategyAnalyzer Doesn't Accept User ID** ❌ **CRITICAL**

**Problem**: `StrategyAnalyzer.call_ai_service()` does NOT accept `user_id` parameter.

**Current Code**:
```python
# backend/api/content_planning/services/content_strategy/ai_analysis/strategy_analyzer.py:327
async def call_ai_service(self, prompt: str, analysis_type: str) -> Dict[str, Any]:
    # ... calls AIServiceManager without user_id
```

**Missing**: `user_id` parameter

**Impact**: Cannot pass user_id from strategy creation to AI calls.

---

### **Issue 4: Endpoints Don't Use Clerk Authentication** ⚠️ **HIGH PRIORITY**

**Problem**: Content strategy endpoints accept `user_id` from request body instead of using Clerk authentication.

**Current Code**:
```python
# backend/api/content_planning/api/content_strategy/endpoints/strategy_crud.py:38
@router.post("/create")
async def create_enhanced_strategy(
    strategy_data: Dict[str, Any],  # user_id comes from request body
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
```

**Expected**:
```python
@router.post("/create")
async def create_enhanced_strategy(
    strategy_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user),  # From Clerk
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    user_id = str(current_user.get('id', ''))
```

**Impact**: 
- ⚠️ User can spoof user_id in request
- ⚠️ No authentication validation
- ⚠️ Security vulnerability

---

## 📊 **Detailed Analysis**

### **AI Call Flow Analysis**

#### **Current Implementation (BYPASSES SUBSCRIPTION)**

```python
# 1. StrategyAnalyzer calls AI service
async def call_ai_service(self, prompt: str, analysis_type: str):
    ai_service = AIServiceManager()
    response = await ai_service.execute_structured_json_call(
        service_type, prompt, schema
        # ❌ NO user_id passed
    )

# 2. AIServiceManager executes call
async def execute_structured_json_call(self, service_type, prompt, schema):
    return await self._execute_ai_call(service_type, prompt, schema)
    # ❌ NO user_id parameter

# 3. Internal call uses direct Gemini provider
def _call_gemini_structured(self, prompt: str, schema: Dict[str, Any]):
    return _gemini_fn(prompt, schema, ...)
    # ❌ Calls gemini_structured_json_response DIRECTLY
    # ❌ Bypasses llm_text_gen
    # ❌ NO subscription checks
```

#### **Expected Implementation (WITH SUBSCRIPTION)**

```python
# 1. StrategyAnalyzer calls AI service WITH user_id
async def call_ai_service(self, prompt: str, analysis_type: str, user_id: str):
    ai_service = AIServiceManager()
    response = await ai_service.execute_structured_json_call(
        service_type, prompt, schema, user_id=user_id
        # ✅ user_id passed
    )

# 2. AIServiceManager executes call WITH user_id
async def execute_structured_json_call(self, service_type, prompt, schema, user_id: str):
    return await self._execute_ai_call(service_type, prompt, schema, user_id=user_id)
    # ✅ user_id parameter

# 3. Internal call uses llm_text_gen
def _call_llm_with_checks(self, prompt: str, schema: Dict[str, Any], user_id: str):
    return llm_text_gen(
        prompt=prompt,
        json_struct=schema,
        user_id=user_id  # ✅ Passes user_id
    )
    # ✅ Uses llm_text_gen
    # ✅ Has subscription checks
```

---

### **Subscription Check Flow**

#### **How `llm_text_gen` Works (CORRECT)**

```python
# backend/services/llm_providers/main_text_generation.py:19
def llm_text_gen(prompt: str, system_prompt: Optional[str] = None, 
                 json_struct: Optional[Dict[str, Any]] = None, 
                 user_id: str = None) -> str:
    # ✅ SUBSCRIPTION CHECK - Required and strict enforcement
    if not user_id:
        raise RuntimeError("user_id is required for subscription checking.")
    
    # ✅ Pre-flight validation
    can_proceed, message, usage_info = pricing_service.check_usage_limits(
        user_id=user_id,
        provider=provider_enum,
        tokens_requested=estimated_total_tokens
    )
    
    if not can_proceed:
        raise RuntimeError(f"Subscription limit exceeded: {message}")
    
    # ✅ Generate AI response
    # ✅ Track usage after successful call
```

#### **How Content Strategy Currently Works (INCORRECT)**

```python
# ❌ NO subscription check
# ❌ NO user_id validation
# ❌ NO usage tracking
# ❌ Direct Gemini API call
```

---

## 🔧 **Required Fixes**

### **Fix 1: Update AIServiceManager to Accept and Pass user_id**

**File**: `backend/services/ai_service_manager.py`

**Changes Required**:
1. Add `user_id` parameter to `execute_structured_json_call()`
2. Add `user_id` parameter to `_execute_ai_call()`
3. Update `_call_gemini_structured()` to use `llm_text_gen()` instead of direct Gemini call
4. Pass `user_id` through the entire chain

**Code Changes**:
```python
async def execute_structured_json_call(
    self, 
    service_type: AIServiceType, 
    prompt: str, 
    schema: Dict[str, Any],
    user_id: Optional[str] = None  # ✅ ADD THIS
) -> Dict[str, Any]:
    return await self._execute_ai_call(service_type, prompt, schema, user_id=user_id)

async def _execute_ai_call(
    self, 
    service_type: AIServiceType, 
    prompt: str, 
    schema: Dict[str, Any],
    user_id: Optional[str] = None  # ✅ ADD THIS
) -> Dict[str, Any]:
    # ✅ Use llm_text_gen instead of direct gemini call
    response = await asyncio.wait_for(
        asyncio.to_thread(
            self._call_llm_with_checks,  # ✅ CHANGE METHOD NAME
            prompt,
            schema,
            user_id,  # ✅ PASS user_id
        ),
        timeout=self.config['timeout_seconds']
    )

def _call_llm_with_checks(self, prompt: str, schema: Dict[str, Any], user_id: Optional[str] = None):
    """Call LLM through main_text_generation with subscription checks."""
    from services.llm_providers.main_text_generation import llm_text_gen
    
    if not user_id:
        raise RuntimeError("user_id is required for subscription checking")
    
    # ✅ Use llm_text_gen which has subscription checks
    return llm_text_gen(
        prompt=prompt,
        json_struct=schema,
        user_id=user_id  # ✅ Pass user_id for subscription checks
    )
```

---

### **Fix 2: Update StrategyAnalyzer to Accept and Pass user_id**

**File**: `backend/api/content_planning/services/content_strategy/ai_analysis/strategy_analyzer.py`

**Changes Required**:
1. Add `user_id` parameter to `call_ai_service()`
2. Add `user_id` parameter to `generate_comprehensive_ai_recommendations()`
3. Pass `user_id` to `AIServiceManager.execute_structured_json_call()`

**Code Changes**:
```python
async def generate_comprehensive_ai_recommendations(
    self, 
    strategy: EnhancedContentStrategy, 
    db: Session,
    user_id: Optional[str] = None  # ✅ ADD THIS
) -> None:
    # Extract user_id from strategy if not provided
    if not user_id:
        user_id = str(strategy.user_id)
    
    # ... existing code ...
    
    recommendations = await self.generate_specialized_recommendations(
        strategy, analysis_type, db, user_id=user_id  # ✅ PASS user_id
    )

async def generate_specialized_recommendations(
    self, 
    strategy: EnhancedContentStrategy, 
    analysis_type: str, 
    db: Session,
    user_id: Optional[str] = None  # ✅ ADD THIS
) -> Dict[str, Any]:
    # Extract user_id from strategy if not provided
    if not user_id:
        user_id = str(strategy.user_id)
    
    prompt = self.create_specialized_prompt(strategy, analysis_type)
    
    # ✅ Pass user_id to AI service call
    ai_response = await self.call_ai_service(prompt, analysis_type, user_id=user_id)

async def call_ai_service(
    self, 
    prompt: str, 
    analysis_type: str,
    user_id: Optional[str] = None  # ✅ ADD THIS
) -> Dict[str, Any]:
    ai_service = AIServiceManager()
    
    # ✅ Pass user_id to execute_structured_json_call
    response = await ai_service.execute_structured_json_call(
        service_type,
        prompt,
        schema,
        user_id=user_id  # ✅ PASS user_id
    )
```

---

### **Fix 3: Update Content Strategy Endpoints to Use Clerk Authentication**

**File**: `backend/api/content_planning/api/content_strategy/endpoints/strategy_crud.py`

**Changes Required**:
1. Import `get_current_user` from middleware
2. Add `current_user` dependency to endpoints
3. Extract `user_id` from Clerk user object
4. Validate `user_id` matches request body (if provided)

**Code Changes**:
```python
# ✅ ADD IMPORT
from middleware.auth_middleware import get_current_user

@router.post("/create")
async def create_enhanced_strategy(
    strategy_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user),  # ✅ ADD THIS
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Create a new enhanced content strategy."""
    try:
        # ✅ Extract user_id from Clerk authentication
        clerk_user_id = str(current_user.get('id', ''))
        if not clerk_user_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid user ID in authentication token"
            )
        
        # ✅ Override user_id from request body with authenticated user_id
        strategy_data['user_id'] = clerk_user_id
        
        # ✅ Validate required fields
        required_fields = ['name']
        for field in required_fields:
            if field not in strategy_data or not strategy_data[field]:
                raise HTTPException(
                    status_code=400,
                    detail=f"Missing required field: {field}"
                )
        
        # ... rest of existing code ...
```

**Apply Same Pattern To**:
- `get_enhanced_strategies()` - Filter by authenticated user_id
- `get_enhanced_strategy_by_id()` - Verify ownership
- `update_enhanced_strategy()` - Verify ownership
- `delete_enhanced_strategy()` - Verify ownership

---

### **Fix 4: Update All Content Strategy Endpoints**

**Files to Update**:
1. `backend/api/content_planning/api/content_strategy/endpoints/strategy_crud.py`
2. `backend/api/content_planning/api/content_strategy/endpoints/ai_generation_endpoints.py`
3. `backend/api/content_planning/api/content_strategy/endpoints/autofill_endpoints.py`
4. `backend/api/content_planning/api/content_strategy/endpoints/streaming_endpoints.py`
5. `backend/api/content_planning/api/content_strategy/endpoints/analytics_endpoints.py`

**Pattern to Apply**:
```python
from middleware.auth_middleware import get_current_user

@router.post("/endpoint")
async def endpoint_function(
    request_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user),  # ✅ ADD
    db: Session = Depends(get_db)
):
    # ✅ Extract authenticated user_id
    user_id = str(current_user.get('id', ''))
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # ✅ Use authenticated user_id (override any from request)
    # ✅ Pass user_id to all service calls
```

---

## 📋 **Implementation Checklist**

### **Phase 1: Core AI Service Fixes** 🔴 **CRITICAL**

- [ ] **Fix 1.1**: Update `AIServiceManager.execute_structured_json_call()` to accept `user_id`
- [ ] **Fix 1.2**: Update `AIServiceManager._execute_ai_call()` to accept `user_id`
- [ ] **Fix 1.3**: Replace `_call_gemini_structured()` with `_call_llm_with_checks()` using `llm_text_gen`
- [ ] **Fix 1.4**: Update all `AIServiceManager` methods to pass `user_id`

### **Phase 2: Strategy Analyzer Fixes** 🔴 **CRITICAL**

- [ ] **Fix 2.1**: Update `StrategyAnalyzer.call_ai_service()` to accept `user_id`
- [ ] **Fix 2.2**: Update `StrategyAnalyzer.generate_comprehensive_ai_recommendations()` to accept `user_id`
- [ ] **Fix 2.3**: Update `StrategyAnalyzer.generate_specialized_recommendations()` to accept `user_id`
- [ ] **Fix 2.4**: Pass `user_id` from strategy object when available

### **Phase 3: Endpoint Authentication** 🟡 **HIGH PRIORITY**

- [ ] **Fix 3.1**: Add `get_current_user` to `strategy_crud.py` endpoints
- [ ] **Fix 3.2**: Add `get_current_user` to `ai_generation_endpoints.py` endpoints
- [ ] **Fix 3.3**: Add `get_current_user` to `autofill_endpoints.py` endpoints
- [ ] **Fix 3.4**: Add `get_current_user` to `streaming_endpoints.py` endpoints
- [ ] **Fix 3.5**: Add `get_current_user` to `analytics_endpoints.py` endpoints
- [ ] **Fix 3.6**: Update all endpoints to extract `user_id` from Clerk authentication

### **Phase 4: Service Layer Updates** 🟡 **HIGH PRIORITY**

- [ ] **Fix 4.1**: Update `EnhancedStrategyService.create_enhanced_strategy()` to accept `user_id`
- [ ] **Fix 4.2**: Update `EnhancedStrategyService.get_enhanced_strategies()` to filter by authenticated `user_id`
- [ ] **Fix 4.3**: Update all service methods to use authenticated `user_id`
- [ ] **Fix 4.4**: Add ownership validation for update/delete operations

### **Phase 5: Testing & Validation** 🟢 **MEDIUM PRIORITY**

- [ ] **Fix 5.1**: Test subscription limit enforcement
- [ ] **Fix 5.2**: Test usage tracking
- [ ] **Fix 5.3**: Test authentication enforcement
- [ ] **Fix 5.4**: Test user_id validation
- [ ] **Fix 5.5**: Verify all AI calls go through `llm_text_gen`

---

## 🔄 **Migration Strategy**

### **Step 1: Update AIServiceManager (Backward Compatible)**

1. Add `user_id` as optional parameter (defaults to None)
2. If `user_id` is None, log warning but don't fail (for backward compatibility)
3. If `user_id` is provided, use `llm_text_gen` with subscription checks
4. Gradually migrate all callers to provide `user_id`

### **Step 2: Update StrategyAnalyzer**

1. Extract `user_id` from strategy object
2. Pass `user_id` to all AI service calls
3. Add fallback to strategy.user_id if not provided

### **Step 3: Update Endpoints**

1. Add `get_current_user` dependency
2. Extract `user_id` from Clerk authentication
3. Override any `user_id` from request body
4. Pass authenticated `user_id` to services

### **Step 4: Remove Backward Compatibility**

1. Make `user_id` required in `AIServiceManager`
2. Make `user_id` required in `StrategyAnalyzer`
3. Remove fallback logic
4. Enforce authentication on all endpoints

---

## 📊 **Impact Assessment**

### **Security Impact** 🔴 **CRITICAL**

- **Current**: Users can spoof `user_id` in requests
- **Current**: No subscription limit enforcement
- **Current**: No usage tracking
- **After Fix**: Proper authentication and authorization
- **After Fix**: Subscription limits enforced
- **After Fix**: Usage properly tracked

### **Cost Impact** 🔴 **CRITICAL**

- **Current**: Unlimited AI calls without subscription checks
- **Current**: No cost tracking
- **After Fix**: Subscription limits prevent abuse
- **After Fix**: Proper cost tracking and billing

### **Functionality Impact** 🟢 **LOW**

- **Current**: AI calls work but bypass checks
- **After Fix**: AI calls work WITH proper checks
- **No Breaking Changes**: Backward compatible migration path

---

## 🎯 **Priority Actions**

### **Immediate (This Week)**

1. ✅ **Fix AIServiceManager** - Add user_id support and use llm_text_gen
2. ✅ **Fix StrategyAnalyzer** - Accept and pass user_id
3. ✅ **Fix strategy_crud.py** - Add Clerk authentication

### **Short Term (Next Week)**

4. ✅ **Fix all content strategy endpoints** - Add authentication
5. ✅ **Update service layer** - Use authenticated user_id
6. ✅ **Add ownership validation** - Prevent unauthorized access

### **Medium Term (Next Sprint)**

7. ✅ **Remove backward compatibility** - Enforce user_id requirement
8. ✅ **Add comprehensive tests** - Verify subscription checks
9. ✅ **Update documentation** - Document authentication flow

---

## 📝 **Code Examples**

### **Before (INCORRECT)**

```python
# ❌ No authentication
@router.post("/create")
async def create_enhanced_strategy(
    strategy_data: Dict[str, Any],  # user_id from request body
    db: Session = Depends(get_db)
):
    user_id = strategy_data.get('user_id')  # ❌ Can be spoofed
    
    # ❌ AI call without subscription check
    await strategy_analyzer.generate_comprehensive_ai_recommendations(strategy, db)
    # ❌ No user_id passed
```

### **After (CORRECT)**

```python
# ✅ Clerk authentication
@router.post("/create")
async def create_enhanced_strategy(
    strategy_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user),  # ✅ From Clerk
    db: Session = Depends(get_db)
):
    user_id = str(current_user.get('id', ''))  # ✅ Authenticated
    strategy_data['user_id'] = user_id  # ✅ Override request body
    
    # ✅ AI call WITH subscription check
    await strategy_analyzer.generate_comprehensive_ai_recommendations(
        strategy, db, user_id=user_id  # ✅ Pass user_id
    )
```

---

## 🔍 **Verification Steps**

After implementing fixes, verify:

1. ✅ All content strategy endpoints require authentication
2. ✅ All AI calls pass through `llm_text_gen` with `user_id`
3. ✅ Subscription limits are enforced
4. ✅ Usage is tracked correctly
5. ✅ Users cannot access other users' strategies
6. ✅ Pre-flight validation works correctly

---

**Last Updated**: January 2025  
**Status**: ⚠️ **CRITICAL FIXES REQUIRED**  
**Priority**: 🔴 **HIGHEST**
