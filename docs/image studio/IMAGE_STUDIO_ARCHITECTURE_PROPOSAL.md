# Image Studio: Unified Architecture & Integration Patterns

**Purpose**: Define **reusable** code patterns and architecture for integrating 40+ WaveSpeed AI models into Image Studio  
**Status**: Architecture Proposal - Pre-Implementation Review  
**Based On**: Existing `main_image_generation.py` + Video Studio patterns  
**Key Principle**: **REUSABILITY** - Extend existing code, don't duplicate

---

## 📊 Executive Summary

This document proposes a **reusable architecture** for Image Studio that:
1. **✅ Extends Existing Code**: Builds on `main_image_generation.py` (already exists)
2. **✅ Extracts Reusable Helpers**: Validation and tracking from existing functions
3. **✅ Reuses Provider Pattern**: Extends `ImageGenerationProvider` protocol
4. **✅ Reuses Infrastructure**: WaveSpeedClient, validation, tracking logic
5. **✅ Scales to 40+ Models**: Easy addition by following existing patterns

---

## 🔍 Current State Analysis

### **Video Studio Pattern** (`main_video_generation.py`) - Reference

#### **Architecture**
```
┌─────────────────────────────────────────┐
│  ai_video_generate()                    │  ← Unified Entry Point
│  - Pre-flight validation                │
│  - Provider routing                     │
│  - Usage tracking                       │
│  - Progress callbacks                   │
└──────────────┬──────────────────────────┘
               │
       ┌───────┴────────┐
       │                │
┌──────▼──────┐  ┌─────▼──────────┐
│ HuggingFace │  │ WaveSpeed      │
│ Provider    │  │ Provider        │
└─────────────┘  └────────────────┘
```

#### **Key Patterns**
1. **Unified Entry Point**: `ai_video_generate()` handles all video operations
2. **Pre-flight Validation**: Subscription checks BEFORE API calls
3. **Provider Abstraction**: Routes to provider-specific handlers
4. **Standardized Returns**: Always returns `Dict[str, Any]` with consistent keys
5. **Usage Tracking**: Centralized `track_video_usage()` function
6. **Progress Callbacks**: Optional progress updates for async operations
7. **Error Handling**: Consistent HTTPException patterns

---

### **Image Studio Current Pattern** ✅ **ALREADY EXISTS**

#### **Architecture**
```
┌─────────────────────────────────────────┐
│  main_image_generation.py               │  ← Unified Entry Point (EXISTS)
│  - generate_image()                     │
│  - generate_character_image()           │
│  - Pre-flight validation                │
│  - Usage tracking                       │
└──────────────┬──────────────────────────┘
               │
    ┌──────────┼──────────┐
    │          │          │
┌───▼───┐ ┌───▼───┐ ┌───▼───┐
│Create │ │ Edit  │ │Upscale│
│Service│ │Service│ │Service│
└───┬───┘ └───┬───┘ └───┬───┘
    │          │          │
┌───▼──────────▼──────────▼───┐
│  image_generation/          │
│  - ImageGenerationProvider  │  ← Protocol (EXISTS)
│  - WaveSpeedImageProvider    │
│  - StabilityImageProvider    │
│  - HuggingFaceImageProvider  │
│  - GeminiImageProvider      │
└──────────────────────────────┘
```

#### **Current Implementation** ✅
1. **✅ Unified Entry Point EXISTS**: `main_image_generation.py` with `generate_image()`
2. **✅ Pre-flight Validation**: Implemented in `generate_image()`
3. **✅ Provider Abstraction**: `ImageGenerationProvider` protocol with implementations
4. **✅ Usage Tracking**: Implemented in `generate_image()`
5. **✅ Standardized Returns**: `ImageGenerationResult` dataclass

#### **Current Usage**
- ✅ **Used by**: YouTube, Podcast, Story Writer, Facebook Writer, LinkedIn
- ⚠️ **NOT used by**: `CreateStudioService` (uses providers directly)
- ⚠️ **Missing**: Editing, Upscaling, 3D operations don't use unified entry

#### **Reusability Opportunities**
1. **Extend `main_image_generation.py`** for editing operations
2. **Reuse provider pattern** for new WaveSpeed models
3. **Standardize all services** to use unified entry point
4. **Extract common validation/tracking** into reusable functions

---

## 🎯 Proposed Architecture Enhancement

### **Core Principle: Extend Existing Pattern for Maximum Reusability**

**Build on existing `main_image_generation.py`** instead of creating new modules. Extend it to support all image operations while maintaining the proven pattern.

### **Enhanced Architecture Diagram**

```
┌─────────────────────────────────────────────────────────────┐
│  main_image_generation.py (EXISTS - EXTEND)                 │
│  ✅ generate_image()              (text-to-image)           │
│  ✅ generate_character_image()    (character consistency)   │
│  🆕 generate_image_edit()          (editing operations)       │
│  🆕 generate_image_upscale()      (upscaling)               │
│  🆕 generate_image_to_3d()          (3D generation)           │
│  🆕 generate_face_swap()            (face swapping)            │
│  🆕 generate_image_translate()     (translation)              │
└──────────────┬──────────────────────────────────────────────┘
               │
    ┌──────────┼──────────┬──────────┐
    │          │          │          │
┌───▼───┐ ┌───▼───┐ ┌───▼───┐ ┌───▼───┐
│Generate│ │ Edit  │ │Upscale│ │Transform│
│Provider│ │Provider│ │Provider│ │Provider│
└───┬───┘ └───┬───┘ └───┬───┘ └───┬───┘
    │          │          │          │
┌───▼──────────▼──────────▼──────────▼───┐
│  image_generation/ (EXISTS - EXTEND)   │
│  ✅ ImageGenerationProvider Protocol   │
│  ✅ WaveSpeedImageProvider              │
│  🆕 WaveSpeedEditProvider               │
│  🆕 WaveSpeedUpscaleProvider             │
│  🆕 WaveSpeed3DProvider                  │
│  🆕 WaveSpeedFaceSwapProvider            │
└─────────────────────────────────────────┘
```

### **Key Reusability Principles**

1. **Reuse Existing Infrastructure**
   - Extend `main_image_generation.py` (don't duplicate)
   - Reuse `ImageGenerationProvider` protocol pattern
   - Reuse validation and tracking logic

2. **Consistent Function Signatures**
   - All functions follow same pattern: `generate_<operation>()`
   - All use same validation/tracking helpers
   - All return standardized results

3. **Provider Pattern Extension**
   - Create new provider classes following `ImageGenerationProvider` protocol
   - Reuse `WaveSpeedClient` for all WaveSpeed operations
   - Consistent error handling across providers

---

## 📐 Reusable Code Patterns

### **Pattern 1: Extend Existing Unified Entry Point** ✅

#### **Current Structure** (EXISTS)
```python
# backend/services/llm_providers/main_image_generation.py

def generate_image(
    prompt: str,
    options: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None
) -> ImageGenerationResult:
    """Generate image with pre-flight validation."""
    # 1. Pre-flight validation
    if user_id:
        validate_image_generation_operations(...)
    
    # 2. Select provider
    provider_name = _select_provider(options.get("provider"))
    provider = _get_provider(provider_name)
    
    # 3. Generate
    result = provider.generate(image_options)
    
    # 4. Track usage
    if user_id and result:
        track_image_usage(...)
    
    return result
```

#### **Proposed Extensions** (REUSABLE PATTERN)
```python
# backend/services/llm_providers/main_image_generation.py

# REUSE: Common validation helper
def _validate_image_operation(
    user_id: Optional[str],
    operation_type: str,
    num_operations: int = 1
) -> None:
    """Reusable pre-flight validation for all image operations."""
    if not user_id:
        logger.warning("No user_id provided - skipping validation")
        return
    
    from services.database import get_db
    from services.subscription import PricingService
    from services.subscription.preflight_validator import validate_image_generation_operations
    
    db = next(get_db())
    try:
        pricing_service = PricingService(db)
        validate_image_generation_operations(
            pricing_service=pricing_service,
            user_id=user_id,
            num_images=num_operations
        )
    finally:
        db.close()

# REUSE: Common usage tracking helper
def _track_image_usage(
    user_id: str,
    provider: str,
    model: str,
    operation_type: str,
    result_bytes: bytes,
    cost: float,
    metadata: Optional[Dict[str, Any]] = None
) -> None:
    """Reusable usage tracking for all image operations."""
    # ... (extract from existing generate_image function)

# NEW: Extend for editing operations
def generate_image_edit(
    image_base64: str,
    prompt: str,
    operation: str = "general_edit",
    model: Optional[str] = None,
    options: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None
) -> ImageGenerationResult:
    """Generate edited image - REUSES validation and tracking."""
    # 1. Reuse validation
    _validate_image_operation(user_id, "image-edit")
    
    # 2. Get provider (extend to support editing providers)
    provider = _get_edit_provider(model or "wavespeed")
    
    # 3. Generate edit
    result = provider.edit(image_base64, prompt, operation, options)
    
    # 4. Reuse tracking
    if user_id and result:
        _track_image_usage(
            user_id=user_id,
            provider=result.provider,
            model=result.model,
            operation_type="image-edit",
            result_bytes=result.image_bytes,
            cost=result.metadata.get("estimated_cost", 0.0),
            metadata=result.metadata
        )
    
    return result
```

#### **Benefits**
- ✅ **Reuses existing infrastructure** - no duplication
- ✅ **Consistent patterns** - all operations follow same flow
- ✅ **Easy to extend** - add new operations by following pattern
- ✅ **Single source of truth** - validation/tracking in one place

---

### **Pattern 2: Reusable Validation & Tracking Helpers** ✅

#### **Current Implementation** (EXISTS in `main_image_generation.py`)
```python
# Pre-flight validation (lines 58-83)
if user_id:
    db = next(get_db())
    try:
        pricing_service = PricingService(db)
        validate_image_generation_operations(...)
    finally:
        db.close()

# Usage tracking (lines 117-265)
if user_id and result and result.image_bytes:
    # ... tracking logic
```

#### **Proposed Refactoring** (EXTRACT FOR REUSABILITY)
```python
# backend/services/llm_providers/main_image_generation.py

# EXTRACT: Reusable validation function
def _validate_and_track_image_operation(
    user_id: Optional[str],
    operation_type: str,
    provider: str,
    model: str,
    result: Optional[ImageGenerationResult],
    num_operations: int = 1
) -> None:
    """
    REUSABLE helper for validation and tracking.
    Used by all image operation functions.
    """
    # Pre-flight validation
    if user_id:
        _validate_image_operation(user_id, operation_type, num_operations)
    
    # Post-generation tracking
    if user_id and result and result.image_bytes:
        _track_image_usage(
            user_id=user_id,
            provider=provider,
            model=model,
            operation_type=operation_type,
            result_bytes=result.image_bytes,
            cost=result.metadata.get("estimated_cost", 0.0) if result.metadata else 0.0,
            metadata=result.metadata
        )

# REFACTOR: Existing generate_image to use helper
def generate_image(...) -> ImageGenerationResult:
    """Generate image - now uses reusable helpers."""
    # ... provider selection and generation ...
    
    # REUSE: Validation and tracking
    _validate_and_track_image_operation(
        user_id=user_id,
        operation_type="text-to-image",
        provider=provider_name,
        model=result.model,
        result=result
    )
    
    return result
```

#### **Benefits**
- ✅ **DRY Principle** - validation/tracking logic in one place
- ✅ **Consistent behavior** - all operations use same validation
- ✅ **Easy maintenance** - change validation logic once, affects all
- ✅ **Testable** - helpers can be tested independently

---

### **Pattern 3: Extend Provider Pattern for Reusability** ✅

#### **Current Structure** (EXISTS)
```python
# backend/services/llm_providers/image_generation/base.py

class ImageGenerationProvider(Protocol):
    """Protocol for image generation providers."""
    def generate(self, options: ImageGenerationOptions) -> ImageGenerationResult:
        ...

# backend/services/llm_providers/image_generation/wavespeed_provider.py

class WaveSpeedImageProvider(ImageGenerationProvider):
    """WaveSpeed AI image generation provider."""
    SUPPORTED_MODELS = {
        "ideogram-v3-turbo": {...},
        "qwen-image": {...}
    }
    
    def generate(self, options: ImageGenerationOptions) -> ImageGenerationResult:
        # ... implementation
```

#### **Proposed Extension** (REUSE PATTERN)
```python
# backend/services/llm_providers/image_generation/base.py

# EXTEND: Add editing protocol
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

# NEW: Reuse WaveSpeed client pattern
# backend/services/llm_providers/image_generation/wavespeed_edit_provider.py

class WaveSpeedEditProvider(ImageEditProvider):
    """WaveSpeed AI image editing provider - REUSES client."""
    
    # REUSE: Same client initialization
    def __init__(self, api_key: Optional[str] = None):
        self.client = WaveSpeedClient(api_key=api_key)  # REUSE
    
    # REUSE: Model registry pattern
    SUPPORTED_MODELS = {
        "qwen-edit": {
            "model_path": "wavespeed-ai/qwen-image/edit",
            "cost": 0.02,
        },
        "step1x-edit": {
            "model_path": "wavespeed-ai/step1x-edit",
            "cost": 0.03,
        },
        # ... 12 editing models
    }
    
    def edit(
        self,
        image_base64: str,
        prompt: str,
        operation: str,
        options: ImageEditOptions
    ) -> ImageGenerationResult:
        """Edit image - REUSES client pattern."""
        model_info = self.SUPPORTED_MODELS.get(options.model)
        if not model_info:
            raise ValueError(f"Unsupported model: {options.model}")
        
        # REUSE: Same client call pattern
        image_bytes = self.client.edit_image(
            model=model_info["model_path"],
            image_base64=image_base64,
            prompt=prompt,
            **options.to_dict()
        )
        
        # REUSE: Same result format
        return ImageGenerationResult(
            image_bytes=image_bytes,
            width=options.width,
            height=options.height,
            provider="wavespeed",
            model=options.model,
            metadata={"cost": model_info["cost"]}
        )
```

#### **Benefits**
- ✅ **Reuses existing protocol pattern** - consistent interface
- ✅ **Reuses WaveSpeedClient** - no duplicate client code
- ✅ **Reuses model registry pattern** - easy to add models
- ✅ **Reuses result format** - consistent return types

---

### **Pattern 4: Reusable Model Registry** (ENHANCE EXISTING)

#### **Current Pattern** (EXISTS in providers)
```python
# WaveSpeedImageProvider.SUPPORTED_MODELS
SUPPORTED_MODELS = {
    "ideogram-v3-turbo": {
        "name": "Ideogram V3 Turbo",
        "cost_per_image": 0.10,
        "max_resolution": (1024, 1024),
    },
    "qwen-image": {...}
}
```

#### **Proposed Enhancement** (CENTRALIZE FOR REUSABILITY)
```python
# backend/services/image_studio/model_registry.py

@dataclass
class ImageModel:
    """Model metadata - REUSES existing provider pattern."""
    id: str
    name: str
    provider: str
    model_path: str
    cost: float
    category: str  # "generation", "editing", "upscaling", "3d", "face-swap"
    capabilities: List[str]
    max_resolution: Optional[tuple[int, int]] = None

class ImageModelRegistry:
    """Centralized registry - AGGREGATES from providers."""
    
    # REUSE: Extract from existing providers
    MODELS: Dict[str, ImageModel] = {
        # Generation (from WaveSpeedImageProvider)
        "ideogram-v3-turbo": ImageModel(
            id="ideogram-v3-turbo",
            name="Ideogram V3 Turbo",
            provider="wavespeed",
            model_path="ideogram-ai/ideogram-v3-turbo",
            cost=0.10,  # From SUPPORTED_MODELS
            category="generation",
            capabilities=["text-to-image"],
        ),
        # Editing (NEW - follows same pattern)
        "qwen-edit": ImageModel(
            id="qwen-edit",
            name="Qwen Image Edit",
            provider="wavespeed",
            model_path="wavespeed-ai/qwen-image/edit",
            cost=0.02,
            category="editing",
            capabilities=["image-edit", "style-transfer"],
        ),
        # ... 40+ models
    }
    
    @classmethod
    def get_model(cls, model_id: str) -> Optional[ImageModel]:
        """Get model by ID - REUSABLE across all services."""
        return cls.MODELS.get(model_id)
    
    @classmethod
    def list_by_category(cls, category: str) -> List[ImageModel]:
        """List models by category - REUSABLE query."""
        return [m for m in cls.MODELS.values() if m.category == category]
    
    @classmethod
    def get_cost(cls, model_id: str) -> float:
        """Get cost for model - REUSABLE cost lookup."""
        model = cls.get_model(model_id)
        return model.cost if model else 0.0
```

#### **Benefits**
- ✅ **Reuses provider model definitions** - single source of truth
- ✅ **Reusable queries** - all services can use same registry
- ✅ **Cost calculation** - centralized cost lookup
- ✅ **Frontend integration** - single endpoint for model list

---

### **Pattern 5: Usage Tracking**

#### **Structure**
```python
# backend/services/llm_providers/main_image_operations.py

def track_image_usage(
    *,
    user_id: str,
    provider: str,
    model_name: str,
    operation_type: str,
    image_bytes: bytes,
    cost_override: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Track subscription usage for image operations.
    Mirrors track_video_usage() pattern.
    """
    from services.database import get_db
    from models.subscription_models import APIProvider, APIUsageLog, UsageSummary
    
    db = next(get_db())
    try:
        pricing_service = PricingService(db)
        current_period = pricing_service.get_current_billing_period(user_id)
        
        # Get or create usage summary
        usage_summary = get_or_create_usage_summary(user_id, current_period)
        
        # Calculate cost
        cost = cost_override or calculate_cost(provider, model_name, operation_type)
        
        # Update usage summary
        update_usage_summary(usage_summary, operation_type, cost)
        
        # Log API usage
        log_api_usage(user_id, provider, model_name, operation_type, cost, image_bytes)
        
        db.commit()
        
        return {
            "previous_calls": previous_count,
            "current_calls": usage_summary.image_calls,
            "cost": cost,
            "total_cost": usage_summary.image_cost,
        }
    finally:
        db.close()
```

#### **Benefits**
- Consistent with video tracking
- Centralized cost calculation
- Automatic usage logging
- Real-time limit checking

---

### **Pattern 6: Service Layer - Reuse Existing Entry Point** ✅

#### **Current Implementation** (MIXED USAGE)
```python
# CreateStudioService - Uses providers directly (NOT using main_image_generation.py)
# Other services (YouTube, Podcast) - Use main_image_generation.py ✅
```

#### **Proposed Refactoring** (REUSE UNIFIED ENTRY)
```python
# backend/services/image_studio/create_service.py

class CreateStudioService:
    """Service for Create Studio - REUSES unified entry point."""
    
    async def generate(
        self,
        request: CreateStudioRequest,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate image - REUSES main_image_generation.py."""
        # REUSE: Existing unified entry point
        from services.llm_providers.main_image_generation import generate_image
        
        # Map request to unified format
        options = {
            "provider": request.provider or "auto",
            "model": request.model,
            "width": request.width,
            "height": request.height,
            "negative_prompt": request.negative_prompt,
            "guidance_scale": request.guidance_scale,
            "steps": request.steps,
            "seed": request.seed,
        }
        
        # REUSE: Call unified entry point
        results = []
        for i in range(request.num_variations):
            result = generate_image(
                prompt=request.prompt,
                options=options,
                user_id=user_id
            )
            results.append({
                "image_bytes": result.image_bytes,
                "width": result.width,
                "height": result.height,
                "model": result.model,
                "metadata": result.metadata,
            })
        
        return {
            "success": True,
            "results": results,
            "cost": sum(r["metadata"].get("estimated_cost", 0) for r in results),
        }
```

#### **Benefits**
- ✅ **Reuses existing unified entry** - no duplicate validation/tracking
- ✅ **Consistent behavior** - all services use same entry point
- ✅ **Thin service layer** - services focus on business logic
- ✅ **Easy to maintain** - changes in entry point affect all services

---

## 🏗️ Implementation Structure (REUSE EXISTING)

### **File Organization** (EXTEND, DON'T DUPLICATE)

```
backend/services/
├── llm_providers/
│   ├── main_image_generation.py      ← EXISTS - EXTEND for new operations
│   │   ✅ generate_image()            (text-to-image)
│   │   ✅ generate_character_image()  (character consistency)
│   │   🆕 generate_image_edit()        (editing operations)
│   │   🆕 generate_image_upscale()     (upscaling)
│   │   🆕 generate_image_to_3d()       (3D generation)
│   │   🆕 generate_face_swap()          (face swapping)
│   │   🆕 generate_image_translate()    (translation)
│   │
│   │   # REUSABLE HELPERS (extract from existing)
│   │   🆕 _validate_image_operation()   (extract validation)
│   │   🆕 _track_image_operation_usage() (extract tracking)
│   │
│   ├── main_video_generation.py      ← Reference pattern
│   │
│   └── image_generation/              ← EXISTS - EXTEND
│       ├── __init__.py                ✅ Exports providers
│       ├── base.py                    ✅ Protocol (EXISTS)
│       │   - ImageGenerationOptions
│       │   - ImageGenerationResult
│       │   - ImageGenerationProvider (Protocol)
│       │   🆕 ImageEditProvider (Protocol)
│       │   🆕 ImageUpscaleProvider (Protocol)
│       │   🆕 Image3DProvider (Protocol)
│       │
│       ├── wavespeed_provider.py      ✅ EXISTS - EXTEND
│       │   - WaveSpeedImageProvider
│       │   🆕 WaveSpeedEditProvider
│       │   🆕 WaveSpeedUpscaleProvider
│       │   🆕 WaveSpeed3DProvider
│       │   🆕 WaveSpeedFaceSwapProvider
│       │
│       ├── stability_provider.py      ✅ EXISTS
│       ├── hf_provider.py             ✅ EXISTS
│       └── gemini_provider.py         ✅ EXISTS
│
├── image_studio/
│   ├── studio_manager.py             ✅ EXISTS (orchestrator)
│   ├── create_service.py              ⚠️ REFACTOR: Use main_image_generation
│   ├── edit_service.py                ⚠️ REFACTOR: Use main_image_generation
│   ├── upscale_service.py             ⚠️ REFACTOR: Use main_image_generation
│   ├── transform_service.py           ✅ Uses main_video_generation
│   ├── three_d_service.py             🆕 NEW: Uses main_image_generation
│   ├── face_swap_service.py           🆕 NEW: Uses main_image_generation
│   └── model_registry.py               🆕 NEW: Centralized registry
│
└── subscription/
    └── preflight_validator.py         ✅ EXISTS - REUSE
        - validate_image_generation_operations()
```

### **Key Reusability Principles**

1. **Extend, Don't Duplicate**
   - ✅ Extend `main_image_generation.py` (don't create new file)
   - ✅ Extend `ImageGenerationProvider` protocol (don't create new base)
   - ✅ Reuse `WaveSpeedClient` (don't duplicate client code)

2. **Extract Common Logic**
   - ✅ Extract validation into reusable helper
   - ✅ Extract tracking into reusable helper
   - ✅ Extract cost calculation into reusable helper

3. **Consistent Patterns**
   - ✅ All operations follow same function signature pattern
   - ✅ All operations use same validation/tracking helpers
   - ✅ All providers follow same protocol pattern

---

## 🔄 Implementation Strategy (REUSE EXISTING)

### **Phase 1: Extract Reusable Helpers** (Week 1)
1. ✅ **Extract validation helper** from `generate_image()` → `_validate_image_operation()`
2. ✅ **Extract tracking helper** from `generate_image()` → `_track_image_operation_usage()`
3. ✅ **Refactor existing functions** to use extracted helpers
4. ✅ **Test** - ensure existing functionality unchanged

### **Phase 2: Extend for Editing** (Week 2)
1. ✅ **Add `ImageEditProvider` protocol** to `base.py`
2. ✅ **Create `WaveSpeedEditProvider`** following existing provider pattern
3. ✅ **Add `generate_image_edit()`** to `main_image_generation.py` (reuses helpers)
4. ✅ **Refactor `EditStudioService`** to use unified entry point

### **Phase 3: Extend for Upscaling** (Week 3)
1. ✅ **Add `ImageUpscaleProvider` protocol** to `base.py`
2. ✅ **Create `WaveSpeedUpscaleProvider`** (reuses WaveSpeedClient)
3. ✅ **Add `generate_image_upscale()`** (reuses validation/tracking)
4. ✅ **Refactor `UpscaleStudioService`** to use unified entry

### **Phase 4: Extend for 3D & Specialized** (Week 4-5)
1. ✅ **Add `Image3DProvider` protocol**
2. ✅ **Create `WaveSpeed3DProvider`** (reuses client pattern)
3. ✅ **Add `generate_image_to_3d()`** (reuses helpers)
4. ✅ **Add face swap, translation** following same pattern
5. ✅ **Create new services** (3D, Face Swap) using unified entry

### **Phase 5: Model Registry** (Week 6)
1. ✅ **Create `model_registry.py`** aggregating from providers
2. ✅ **Update providers** to register models in central registry
3. ✅ **Add API endpoint** for model list (frontend integration)
4. ✅ **Update cost estimation** to use registry

### **Key Principles**
- ✅ **Reuse existing code** - don't duplicate
- ✅ **Extract common logic** - DRY principle
- ✅ **Follow existing patterns** - consistency
- ✅ **Test incrementally** - ensure no regressions

---

## 📋 Reusable Code Examples

### **Example 1: Adding a New Editing Model** (REUSES PATTERNS)

```python
# 1. Add to WaveSpeedEditProvider (REUSES existing pattern)
# backend/services/llm_providers/image_generation/wavespeed_edit_provider.py

class WaveSpeedEditProvider(ImageEditProvider):
    SUPPORTED_MODELS = {
        # ... existing models ...
        "new-edit-model": {  # 🆕 NEW MODEL
            "model_path": "wavespeed-ai/new-edit-model",
            "cost": 0.05,
            "max_resolution": (2048, 2048),
        }
    }
    
    def edit(self, image_base64: str, prompt: str, ...):
        # REUSES: Same client call pattern
        model_info = self.SUPPORTED_MODELS.get(options.model)
        image_bytes = self.client.edit_image(
            model=model_info["model_path"],
            image_base64=image_base64,
            prompt=prompt,
            **options.to_dict()
        )
        # REUSES: Same result format
        return ImageGenerationResult(...)

# 2. Register in model registry (REUSES registry pattern)
# backend/services/image_studio/model_registry.py
ImageModelRegistry.MODELS["new-edit-model"] = ImageModel(
    id="new-edit-model",
    name="New Edit Model",
    provider="wavespeed",
    model_path="wavespeed-ai/new-edit-model",
    cost=0.05,  # From provider SUPPORTED_MODELS
    category="editing",
    capabilities=["image-edit"],
)

# 3. Use in service (REUSES unified entry)
# backend/services/image_studio/edit_service.py
from services.llm_providers.main_image_generation import generate_image_edit

result = generate_image_edit(
    image_base64=image,
    prompt=prompt,
    model="new-edit-model",  # 🆕 Just specify model ID
    user_id=user_id,
)
# ✅ Validation, tracking, error handling all handled automatically
```

### **Example 2: Adding a New Operation Type** (REUSES HELPERS)

```python
# In main_image_generation.py (EXTEND existing file)

def generate_face_swap(
    source_image_base64: str,
    target_image_base64: str,
    model: str = "wavespeed-ai/image-face-swap",
    options: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None
) -> ImageGenerationResult:
    """
    Face swap operation - REUSES validation and tracking helpers.
    """
    # 1. REUSE: Validation helper
    _validate_image_operation(user_id, "face-swap")
    
    # 2. Get provider (REUSES provider pattern)
    provider = _get_face_swap_provider(model)
    
    # 3. Perform operation
    result = provider.face_swap(
        source_image_base64=source_image_base64,
        target_image_base64=target_image_base64,
        model=model,
        options=options or {}
    )
    
    # 4. REUSE: Tracking helper
    if user_id and result:
        _track_image_operation_usage(
            user_id=user_id,
            provider=result.provider,
            model=result.model,
            operation_type="face-swap",
            result_bytes=result.image_bytes,
            cost=result.metadata.get("estimated_cost", 0.0),
            metadata=result.metadata
        )
    
    return result
```

### **Example 3: Refactoring Existing Service** (REUSE UNIFIED ENTRY)

```python
# BEFORE: CreateStudioService uses providers directly
class CreateStudioService:
    async def generate(self, request, user_id):
        # ... validation logic ...
        provider = self._get_provider_instance(provider_name)
        result = provider.generate(options)
        # ... tracking logic ...
        return result

# AFTER: CreateStudioService REUSES unified entry
class CreateStudioService:
    async def generate(self, request, user_id):
        # REUSE: Unified entry point (validation + tracking included)
        from services.llm_providers.main_image_generation import generate_image
        
        results = []
        for i in range(request.num_variations):
            result = generate_image(  # ✅ All validation/tracking handled
                prompt=request.prompt,
                options={...},
                user_id=user_id
            )
            results.append(result)
        
        return {"results": results}
```

---

## ✅ Benefits of Reusable Architecture

1. **✅ Reuses Existing Code**: Builds on `main_image_generation.py` (no duplication)
2. **✅ DRY Principle**: Validation and tracking extracted into reusable helpers
3. **✅ Consistent Patterns**: All operations follow same proven pattern
4. **✅ Easy to Extend**: Add new operations by following existing pattern
5. **✅ Single Source of Truth**: Model registry aggregates from providers
6. **✅ Maintainable**: Changes in helpers affect all operations
7. **✅ Testable**: Helpers can be tested independently
8. **✅ Backward Compatible**: Existing code continues to work

---

## 🎯 Next Steps

1. **✅ Review existing `main_image_generation.py`** - understand current implementation
2. **✅ Extract reusable helpers** - validation and tracking functions
3. **✅ Extend for editing operations** - add `generate_image_edit()` following pattern
4. **✅ Create model registry** - aggregate models from all providers
5. **✅ Refactor services** - make them use unified entry point
6. **✅ Add new operations** - 3D, face swap, translation following same pattern

## 📝 Implementation Checklist

### **Reusability Focus**
- [ ] Extract `_validate_image_operation()` helper from existing code
- [ ] Extract `_track_image_operation_usage()` helper from existing code
- [ ] Refactor `generate_image()` to use extracted helpers
- [ ] Refactor `generate_character_image()` to use extracted helpers
- [ ] Add `generate_image_edit()` using same helpers
- [ ] Add `generate_image_upscale()` using same helpers
- [ ] Add `generate_image_to_3d()` using same helpers
- [ ] Create `ImageModelRegistry` aggregating from providers
- [ ] Refactor `CreateStudioService` to use unified entry
- [ ] Refactor `EditStudioService` to use unified entry
- [ ] All new operations follow same pattern

---

## 🎯 Reusability Implementation Roadmap

### **Phase 1: Extract Reusable Helpers** (Week 1)
**Goal**: Extract common logic from existing code

1. ✅ **Extract `_validate_image_operation()`** from `generate_image()` (lines 58-83)
2. ✅ **Extract `_track_image_operation_usage()`** from `generate_image()` (lines 117-265)
3. ✅ **Refactor existing functions** to use extracted helpers
4. ✅ **Test** - ensure no regressions

### **Phase 2: Extend for Editing** (Week 2)
**Goal**: Add editing operations reusing patterns

1. ✅ **Add `ImageEditProvider` protocol** to `base.py` (reuses protocol pattern)
2. ✅ **Create `WaveSpeedEditProvider`** (reuses WaveSpeedClient, model registry pattern)
3. ✅ **Add `generate_image_edit()`** to `main_image_generation.py` (reuses helpers)
4. ✅ **Refactor `EditStudioService`** to use unified entry

### **Phase 3: Extend for Other Operations** (Week 3-4)
**Goal**: Add upscaling, 3D, face swap following same pattern

- Same approach as Phase 2 for each operation type

### **Phase 4: Model Registry** (Week 5)
**Goal**: Centralize model information

- Aggregate models from all providers
- Single source of truth for cost, capabilities, etc.

---

## 📚 Related Documentation

- [Image Studio Enhancement Proposal](docs/IMAGE_STUDIO_ENHANCEMENT_PROPOSAL.md) - **Updated with reusability focus**
- [Code Patterns Reference](docs/IMAGE_STUDIO_CODE_PATTERNS_REFERENCE.md) - **Reusability patterns**
- [WaveSpeed Models Reference](docs/IMAGE_STUDIO_WAVESPEED_MODELS_REFERENCE.md)
- [Image Studio Implementation Review](docs/IMAGE_STUDIO_IMPLEMENTATION_REVIEW.md)
- [Video Studio Implementation](backend/services/llm_providers/main_video_generation.py) - Reference pattern

---

*Document Version: 2.0*  
*Last Updated: Current Session*  
*Status: Architecture Proposal - Reusability Focus*  
*Key Principle: Extend existing `main_image_generation.py`, don't duplicate*
