# Image Studio Editing Feature Implementation Plan

**Status**: 📋 **PLANNED** - Ready for Phase 2 Implementation  
**Based On**: Architecture Proposal, Enhancement Proposal, Code Patterns Reference  
**Timeline**: Week 2 (Phase 2)

---

## 🎯 Implementation Goals

1. ✅ **Add `generate_image_edit()`** to `main_image_generation.py` (reuses Phase 1 helpers)
2. ✅ **Create `ImageEditProvider` protocol** following existing pattern
3. ✅ **Create `WaveSpeedEditProvider`** with 14 editing models
4. ✅ **Refactor `EditStudioService`** to use unified entry point
5. ✅ **Add model selection UI** to frontend
6. ✅ **Ensure backward compatibility** with existing Stability AI editing

---

## 📋 Step-by-Step Implementation Plan

### **Step 1: Extend Provider Protocol** (Day 1)

**File**: `backend/services/llm_providers/image_generation/base.py`

**Action**: Add `ImageEditProvider` protocol following `ImageGenerationProvider` pattern

```python
class ImageEditProvider(Protocol):
    """Protocol for image editing providers."""
    
    def edit(
        self,
        image_base64: str,
        prompt: str,
        operation: str,
        options: ImageEditOptions
    ) -> ImageGenerationResult:
        ...
```

**Benefits**:
- ✅ Consistent with existing `ImageGenerationProvider` pattern
- ✅ Easy to add new editing providers later
- ✅ Type-safe interface

---

### **Step 2: Create ImageEditOptions Dataclass** (Day 1)

**File**: `backend/services/llm_providers/image_generation/base.py`

**Action**: Add `ImageEditOptions` dataclass for editing operations

```python
@dataclass
class ImageEditOptions:
    image_base64: str
    prompt: str
    operation: str  # "general_edit", "inpaint", "outpaint", etc.
    mask_base64: Optional[str] = None
    negative_prompt: Optional[str] = None
    model: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    guidance_scale: Optional[float] = None
    steps: Optional[int] = None
    seed: Optional[int] = None
    extra: Optional[Dict[str, Any]] = None
```

---

### **Step 3: Create WaveSpeedEditProvider** (Day 2-3)

**File**: `backend/services/llm_providers/image_generation/wavespeed_edit_provider.py`

**Action**: Create provider following `WaveSpeedImageProvider` pattern

**Key Features**:
- ✅ **Reuses `WaveSpeedClient`** - Same client as generation
- ✅ **Model Registry** - `SUPPORTED_MODELS` dict with 14 models
- ✅ **Cost Calculation** - Model-specific costs
- ✅ **Validation** - Model and parameter validation
- ✅ **Error Handling** - Consistent error patterns

**Models to Support** (14 total):

1. **Budget Tier** ($0.02-$0.03):
   - `qwen-image/edit` - $0.02
   - `qwen-image/edit-plus` - $0.02
   - `step1x-edit` - $0.03
   - `hidream-e1-full` - $0.024
   - `bytedance/seededit-v3` - $0.027

2. **Mid Tier** ($0.035-$0.04):
   - `alibaba/wan-2.5/image-edit` - $0.035
   - `flux-kontext-pro` - $0.04
   - `flux-kontext-pro/multi` - $0.04

3. **Premium Tier** ($0.08-$0.15):
   - `flux-kontext-max` - $0.08
   - `ideogram-character` - $0.10-$0.20
   - `google/nano-banana-pro/edit-ultra` - $0.15 (4K) / $0.18 (8K)

4. **Variable Pricing**:
   - `openai/gpt-image-1` - $0.011-$0.250 (quality-based)

5. **Specialized**:
   - `z-image-turbo-inpaint` - $0.02 (inpainting)
   - `image-zoom-out` - $0.02 (outpainting)

**Implementation Pattern**:
```python
class WaveSpeedEditProvider(ImageEditProvider):
    """WaveSpeed AI image editing provider - REUSES client pattern."""
    
    SUPPORTED_MODELS = {
        "qwen-edit": {
            "model_path": "wavespeed-ai/qwen-image/edit",
            "cost": 0.02,
            "max_resolution": (2048, 2048),
            "capabilities": ["general_edit", "style_transfer"],
        },
        # ... 13 more models
    }
    
    def __init__(self, api_key: Optional[str] = None):
        self.client = WaveSpeedClient(api_key=api_key)  # ✅ REUSE client
    
    def edit(self, image_base64: str, prompt: str, operation: str, options: ImageEditOptions) -> ImageGenerationResult:
        # ✅ REUSES same client call pattern
        model_info = self.SUPPORTED_MODELS.get(options.model)
        image_bytes = self.client.edit_image(
            model=model_info["model_path"],
            image_base64=image_base64,
            prompt=prompt,
            **options.to_dict()
        )
        # ✅ REUSES same result format
        return ImageGenerationResult(...)
```

---

### **Step 4: Add generate_image_edit() Function** (Day 4)

**File**: `backend/services/llm_providers/main_image_generation.py`

**Action**: Add unified entry point for editing operations

**Key Features**:
- ✅ **Reuses `_validate_image_operation()`** helper (Phase 1)
- ✅ **Reuses `_track_image_operation_usage()`** helper (Phase 1)
- ✅ **Provider routing** - Routes to appropriate provider
- ✅ **Standardized returns** - `ImageGenerationResult`
- ✅ **Error handling** - Consistent error patterns

**Implementation**:
```python
def generate_image_edit(
    image_base64: str,
    prompt: str,
    operation: str = "general_edit",
    model: Optional[str] = None,
    options: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None
) -> ImageGenerationResult:
    """
    Generate edited image - REUSES validation and tracking helpers.
    
    Args:
        image_base64: Base64-encoded input image
        prompt: Edit instruction prompt
        operation: Type of edit operation
        model: Model ID to use (default: auto-select)
        options: Additional options (mask, negative_prompt, etc.)
        user_id: User ID for validation and tracking
        
    Returns:
        ImageGenerationResult with edited image
    """
    # 1. REUSE: Validation helper
    _validate_image_operation(
        user_id=user_id,
        operation_type="image-edit",
        num_operations=1,
        log_prefix="[Image Edit]"
    )
    
    # 2. Get provider (REUSES provider pattern)
    provider = _get_edit_provider(model or "wavespeed")
    
    # 3. Prepare options
    edit_options = ImageEditOptions(
        image_base64=image_base64,
        prompt=prompt,
        operation=operation,
        **options or {}
    )
    
    # 4. Edit
    result = provider.edit(edit_options)
    
    # 5. REUSE: Tracking helper
    if user_id and result and result.image_bytes:
        _track_image_operation_usage(
            user_id=user_id,
            provider=result.provider,
            model=result.model,
            operation_type="image-edit",
            result_bytes=result.image_bytes,
            cost=result.metadata.get("estimated_cost", 0.0),
            prompt=prompt,
            endpoint="/image-generation/edit",
            metadata=result.metadata,
            log_prefix="[Image Edit]"
        )
    
    return result
```

---

### **Step 5: Add Provider Selection Helper** (Day 4)

**File**: `backend/services/llm_providers/main_image_generation.py`

**Action**: Add `_get_edit_provider()` helper following `_get_provider()` pattern

```python
def _get_edit_provider(provider_name: str):
    """Get editing provider instance.
    
    Args:
        provider_name: Provider name ("wavespeed", "stability", etc.)
        
    Returns:
        ImageEditProvider instance
    """
    if provider_name == "wavespeed":
        return WaveSpeedEditProvider()
    elif provider_name == "stability":
        # Keep existing Stability editing support
        return StabilityEditProvider()  # If exists, or wrap existing
    else:
        raise ValueError(f"Unknown edit provider: {provider_name}")
```

---

### **Step 6: Refactor EditStudioService** (Day 5)

**File**: `backend/services/image_studio/edit_service.py`

**Action**: Update to use unified `generate_image_edit()` entry point

**Changes**:
- ✅ **Remove direct provider calls** - Use unified entry point
- ✅ **Keep existing operations** - Stability AI operations still work
- ✅ **Add WaveSpeed model selection** - New models available
- ✅ **Maintain backward compatibility** - Existing API unchanged

**Implementation**:
```python
# In EditStudioService.process_edit()

# For WaveSpeed models
if request.provider == "wavespeed" or (request.provider is None and request.model and request.model.startswith("wavespeed")):
    from services.llm_providers.main_image_generation import generate_image_edit
    
    result = generate_image_edit(
        image_base64=request.image_base64,
        prompt=request.prompt or "",
        operation=request.operation,
        model=request.model,
        options={
            "mask_base64": request.mask_base64,
            "negative_prompt": request.negative_prompt,
            # ... other options
        },
        user_id=user_id
    )
    
    image_bytes = result.image_bytes
else:
    # Keep existing Stability AI editing logic
    image_bytes = await self._handle_stability_edit(...)
```

---

### **Step 7: Update API Endpoint** (Day 5)

**File**: `backend/routers/image_studio.py`

**Action**: Add `model` parameter to edit endpoint

**Changes**:
- ✅ Add `model` parameter to request schema
- ✅ Pass model to `EditStudioService`
- ✅ Maintain backward compatibility (model optional)

---

### **Step 8: Frontend Model Selector** (Day 6-7)

**File**: `frontend/src/components/ImageStudio/EditStudio.tsx`

**Action**: Add model selection UI

**Features**:
- ✅ **Model Dropdown** - List all 14 editing models
- ✅ **Cost Display** - Show cost per model
- ✅ **Quality Tiers** - Group by Budget/Mid/Premium
- ✅ **Smart Recommendations** - Auto-suggest based on operation type
- ✅ **Side-by-Side Comparison** - Compare different models (optional)

**UI Components**:
```tsx
<ModelSelector
  models={editingModels}
  selectedModel={selectedModel}
  onModelChange={setSelectedModel}
  showCost={true}
  showQuality={true}
  recommendations={getRecommendations(operation)}
/>
```

---

### **Step 9: Testing & Verification** (Day 8-10)

**Test Cases**:
1. ✅ **All 14 models work** - Test each model with sample edits
2. ✅ **Validation works** - Pre-flight validation for editing
3. ✅ **Tracking works** - Usage tracking for editing operations
4. ✅ **Error handling** - Invalid models, API failures, etc.
5. ✅ **Backward compatibility** - Existing Stability editing still works
6. ✅ **Frontend integration** - Model selector works correctly
7. ✅ **Cost calculation** - Correct costs tracked per model

---

## 📊 Implementation Checklist

### **Backend**
- [ ] Add `ImageEditProvider` protocol to `base.py`
- [ ] Add `ImageEditOptions` dataclass to `base.py`
- [ ] Create `WaveSpeedEditProvider` class
- [ ] Add 14 editing models to `SUPPORTED_MODELS`
- [ ] Implement `edit()` method for each model
- [ ] Add `generate_image_edit()` to `main_image_generation.py`
- [ ] Add `_get_edit_provider()` helper
- [ ] Refactor `EditStudioService` to use unified entry
- [ ] Update API endpoint to accept `model` parameter
- [ ] Test all 14 models

### **Frontend**
- [ ] Add model selector component
- [ ] Update `EditStudio.tsx` with model dropdown
- [ ] Add cost display per model
- [ ] Add quality tier grouping
- [ ] Add smart recommendations
- [ ] Test model selection flow

### **Documentation**
- [ ] Update API documentation
- [ ] Add model comparison guide
- [ ] Update user documentation

---

## 🎯 Success Criteria

1. ✅ **All 14 WaveSpeed editing models integrated**
2. ✅ **Unified entry point** - `generate_image_edit()` works
3. ✅ **Reuses Phase 1 helpers** - Validation and tracking
4. ✅ **Backward compatible** - Existing Stability editing works
5. ✅ **Frontend model selection** - Users can choose models
6. ✅ **Cost tracking** - Correct costs tracked per model
7. ✅ **No regressions** - All existing functionality works

---

## 📝 Files to Create/Modify

### **New Files**
1. `backend/services/llm_providers/image_generation/wavespeed_edit_provider.py`

### **Modified Files**
1. `backend/services/llm_providers/image_generation/base.py` - Add protocol and options
2. `backend/services/llm_providers/main_image_generation.py` - Add `generate_image_edit()`
3. `backend/services/image_studio/edit_service.py` - Use unified entry
4. `backend/routers/image_studio.py` - Add model parameter
5. `frontend/src/components/ImageStudio/EditStudio.tsx` - Add model selector

---

## 🔄 Integration with Existing Code

### **Reuses Phase 1 Helpers**
- ✅ `_validate_image_operation()` - Pre-flight validation
- ✅ `_track_image_operation_usage()` - Usage tracking

### **Follows Existing Patterns**
- ✅ Provider protocol pattern (like `ImageGenerationProvider`)
- ✅ Model registry pattern (like `WaveSpeedImageProvider.SUPPORTED_MODELS`)
- ✅ Client reuse pattern (uses `WaveSpeedClient`)
- ✅ Result format pattern (returns `ImageGenerationResult`)

### **Maintains Compatibility**
- ✅ Existing Stability AI editing still works
- ✅ API endpoints backward compatible
- ✅ Frontend components work with or without model selection

---

## 🚀 Timeline

- **Day 1**: Protocol and options dataclass
- **Day 2-3**: WaveSpeedEditProvider with all 14 models
- **Day 4**: `generate_image_edit()` function
- **Day 5**: Refactor EditStudioService
- **Day 6-7**: Frontend model selector
- **Day 8-10**: Testing and bug fixes

**Total**: ~10 days (2 weeks with buffer)

---

## 📚 Related Documentation

- [Image Studio Architecture Proposal](docs/IMAGE_STUDIO_ARCHITECTURE_PROPOSAL.md)
- [Image Studio Enhancement Proposal](docs/IMAGE_STUDIO_ENHANCEMENT_PROPOSAL.md)
- [WaveSpeed Models Reference](docs/IMAGE_STUDIO_WAVESPEED_MODELS_REFERENCE.md)
- [Code Patterns Reference](docs/IMAGE_STUDIO_CODE_PATTERNS_REFERENCE.md)
- [Phase 1 Implementation Summary](docs/IMAGE_STUDIO_PHASE1_IMPLEMENTATION_SUMMARY.md)

---

*Ready for Phase 2 Implementation - Editing Feature*
