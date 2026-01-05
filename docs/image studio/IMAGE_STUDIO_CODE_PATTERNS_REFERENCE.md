# Image Studio: Code Patterns Reference

**Purpose**: Quick reference for reusable code patterns when integrating new AI models  
**Status**: Implementation Guide - Focus on Reusability  
**Key Principle**: Extend existing `main_image_generation.py`, don't duplicate

---

## 📊 Pattern Comparison: Video Studio vs. Image Studio (Existing)

### **Pattern 1: Unified Entry Point**

#### **Video Studio (Reference)**
```python
# backend/services/llm_providers/main_video_generation.py

async def ai_video_generate(
    prompt: Optional[str] = None,
    image_data: Optional[bytes] = None,
    operation_type: str = "text-to-video",
    provider: str = "huggingface",
    user_id: Optional[str] = None,
    progress_callback: Optional[Callable[[float, str], None]] = None,
    **kwargs,
) -> Dict[str, Any]:
    # 1. Validation
    if not user_id:
        raise RuntimeError("user_id is required")
    
    # 2. Pre-flight validation
    validate_video_generation_operations(...)
    
    # 3. Route to provider
    if operation_type == "text-to-video":
        if provider == "wavespeed":
            result = await _generate_text_to_video_wavespeed(...)
        elif provider == "huggingface":
            result = _generate_with_huggingface(...)
    elif operation_type == "image-to-video":
        if provider == "wavespeed":
            result = await _generate_image_to_video_wavespeed(...)
    
    # 4. Track usage
    track_video_usage(...)
    
    # 5. Return standardized result
    return {
        "video_bytes": result["video_bytes"],
        "prompt": result.get("prompt", prompt),
        "duration": result.get("duration", 5.0),
        "model_name": result.get("model_name", model),
        "cost": result.get("cost", 0.0),
        "provider": provider,
        "metadata": result.get("metadata", {}),
    }
```

#### **Image Studio (Proposed)**
```python
# backend/services/llm_providers/main_image_operations.py

# CURRENT: main_image_generation.py (EXISTS)
def generate_image(
    prompt: str,
    options: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None
) -> ImageGenerationResult:
    """Generate image - REUSABLE pattern for all operations."""
    # 1. Pre-flight validation (EXTRACT to helper)
    if user_id:
        _validate_image_operation(user_id, "text-to-image")
    
    # 2. Select provider (REUSABLE)
    provider_name = _select_provider(options.get("provider"))
    provider = _get_provider(provider_name)
    
    # 3. Generate
    result = provider.generate(image_options)
    
    # 4. Track usage (EXTRACT to helper)
    if user_id and result:
        _track_image_operation_usage(
            user_id=user_id,
            provider=provider_name,
            model=result.model,
            operation_type="text-to-image",
            result_bytes=result.image_bytes,
            cost=result.metadata.get("estimated_cost", 0.0),
            metadata=result.metadata
        )
    
    return result

# EXTEND: Add new operations following same pattern
def generate_image_edit(
    image_base64: str,
    prompt: str,
    model: Optional[str] = None,
    options: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None
) -> ImageGenerationResult:
    """Edit image - REUSES same helpers."""
    # 1. REUSE: Validation helper
    if user_id:
        _validate_image_operation(user_id, "image-edit")
    
    # 2. Get provider (REUSES provider pattern)
    provider = _get_edit_provider(model or "wavespeed")
    
    # 3. Edit
    result = provider.edit(image_base64, prompt, options)
    
    # 4. REUSE: Tracking helper
    if user_id and result:
        _track_image_operation_usage(...)
    
    return result
```

---

### **Pattern 2: Pre-flight Validation**

#### **Video Studio (Reference)**
```python
# In main_video_generation.py

from services.subscription.preflight_validator import validate_video_generation_operations

# PRE-FLIGHT VALIDATION: Validate BEFORE API call
db = next(get_db())
try:
    pricing_service = PricingService(db)
    validate_video_generation_operations(
        pricing_service=pricing_service,
        user_id=user_id
    )
except HTTPException:
    # Re-raise immediately - don't proceed with API call
    raise
finally:
    db.close()
```

#### **Image Studio (EXISTS - Extract Helper)**
```python
# CURRENT: In main_image_generation.py (lines 58-83)
if user_id:
    db = next(get_db())
    try:
        pricing_service = PricingService(db)
        validate_image_generation_operations(...)
    finally:
        db.close()

# EXTRACT: Reusable helper (REUSE across all operations)
def _validate_image_operation(
    user_id: Optional[str],
    operation_type: str,
    num_operations: int = 1
) -> None:
    """REUSABLE validation helper - extracted from generate_image()."""
    if not user_id:
        logger.warning("No user_id - skipping validation")
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

# USE: In all operation functions
def generate_image_edit(...):
    _validate_image_operation(user_id, "image-edit")  # ✅ REUSE
    # ... rest of function
```

---

### **Pattern 3: Provider Handler**

#### **Video Studio (Reference)**
```python
async def _generate_image_to_video_wavespeed(
    image_data: Optional[bytes] = None,
    image_base64: Optional[str] = None,
    prompt: str = "",
    duration: int = 5,
    resolution: str = "720p",
    model: str = "alibaba/wan-2.5/image-to-video",
    **kwargs
) -> Dict[str, Any]:
    """Generate video from image using WaveSpeed."""
    from services.image_studio.wan25_service import WAN25Service
    
    wan25_service = WAN25Service()
    result = await wan25_service.generate_video(
        image_base64=image_base64,
        prompt=prompt,
        resolution=resolution,
        duration=duration,
        **kwargs
    )
    
    return {
        "video_bytes": result["video_bytes"],
        "prompt": result.get("prompt", prompt),
        "duration": result.get("duration", float(duration)),
        "model_name": result.get("model_name", model),
        "cost": result.get("cost", 0.0),
        "provider": "wavespeed",
        "resolution": result.get("resolution", resolution),
        "width": result.get("width", 1280),
        "height": result.get("height", 720),
        "metadata": result.get("metadata", {}),
    }
```

#### **Image Studio (EXISTS - Extend Pattern)**
```python
# CURRENT: WaveSpeedImageProvider (EXISTS)
# backend/services/llm_providers/image_generation/wavespeed_provider.py

class WaveSpeedImageProvider(ImageGenerationProvider):
    """REUSABLE provider pattern."""
    
    SUPPORTED_MODELS = {
        "ideogram-v3-turbo": {
            "model_path": "ideogram-ai/ideogram-v3-turbo",
            "cost": 0.10,
        },
        "qwen-image": {...}
    }
    
    def __init__(self, api_key: Optional[str] = None):
        self.client = WaveSpeedClient(api_key=api_key)  # REUSE client
    
    def generate(self, options: ImageGenerationOptions) -> ImageGenerationResult:
        # REUSABLE pattern
        model_info = self.SUPPORTED_MODELS.get(options.model)
        image_bytes = self.client.generate_image(
            model=model_info["model_path"],
            prompt=options.prompt,
            **options.to_dict()
        )
        return ImageGenerationResult(...)

# EXTEND: New provider following same pattern
class WaveSpeedEditProvider(ImageEditProvider):
    """REUSES same pattern as WaveSpeedImageProvider."""
    
    SUPPORTED_MODELS = {
        "qwen-edit": {
            "model_path": "wavespeed-ai/qwen-image/edit",
            "cost": 0.02,
        },
        # ... 12 editing models
    }
    
    def __init__(self, api_key: Optional[str] = None):
        self.client = WaveSpeedClient(api_key=api_key)  # ✅ REUSE client
    
    def edit(self, image_base64: str, prompt: str, ...) -> ImageGenerationResult:
        # ✅ REUSES same client call pattern
        model_info = self.SUPPORTED_MODELS.get(model)
        image_bytes = self.client.edit_image(
            model=model_info["model_path"],
            image_base64=image_base64,
            prompt=prompt,
            **options
        )
        return ImageGenerationResult(...)  # ✅ REUSES same result format
```

---

### **Pattern 4: Usage Tracking**

#### **Video Studio (Reference)**
```python
def track_video_usage(
    *,
    user_id: str,
    provider: str,
    model_name: str,
    prompt: str,
    video_bytes: bytes,
    cost_override: Optional[float] = None,
) -> Dict[str, Any]:
    """Track subscription usage for video generation."""
    from services.database import get_db
    from models.subscription_models import APIProvider, APIUsageLog, UsageSummary
    
    db = next(get_db())
    try:
        pricing_service = PricingService(db)
        current_period = pricing_service.get_current_billing_period(user_id)
        
        # Get or create usage summary
        usage_summary = get_or_create_usage_summary(user_id, current_period)
        
        # Calculate cost
        cost = cost_override or calculate_video_cost(provider, model_name)
        
        # Update usage summary
        usage_summary.video_calls += 1
        usage_summary.video_cost += cost
        
        # Log API usage
        usage_log = APIUsageLog(
            user_id=user_id,
            provider=APIProvider.VIDEO,
            model_used=model_name,
            cost_total=cost,
            response_size=len(video_bytes),
        )
        db.add(usage_log)
        db.commit()
        
        return {
            "current_calls": usage_summary.video_calls,
            "cost": cost,
        }
    finally:
        db.close()
```

#### **Image Studio (EXISTS - Extract Helper)**
```python
# CURRENT: In main_image_generation.py (lines 117-265)
# EXTRACT: Reusable tracking helper

def _track_image_operation_usage(
    user_id: str,
    provider: str,
    model: str,
    operation_type: str,
    result_bytes: bytes,
    cost: float,
    prompt: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    REUSABLE tracking helper - extracted from generate_image().
    Used by ALL image operation functions.
    """
    from services.database import get_db
    from models.subscription_models import UsageSummary, APIUsageLog, APIProvider
    from services.subscription import PricingService
    
    db = next(get_db())
    try:
        pricing = PricingService(db)
        current_period = pricing.get_current_billing_period(user_id) or datetime.now().strftime("%Y-%m")
        
        # REUSE: Same summary lookup pattern
        summary = db.query(UsageSummary).filter(
            UsageSummary.user_id == user_id,
            UsageSummary.billing_period == current_period
        ).first()
        
        if not summary:
            summary = UsageSummary(user_id=user_id, billing_period=current_period)
            db.add(summary)
            db.flush()
        
        # REUSE: Same update pattern
        current_calls = getattr(summary, "stability_calls", 0) or 0
        current_cost = getattr(summary, "stability_cost", 0.0) or 0.0
        
        from sqlalchemy import text as sql_text
        db.execute(sql_text("""
            UPDATE usage_summaries 
            SET stability_calls = :new_calls, stability_cost = :new_cost
            WHERE user_id = :user_id AND billing_period = :period
        """), {
            'new_calls': current_calls + 1,
            'new_cost': current_cost + cost,
            'user_id': user_id,
            'period': current_period
        })
        
        # REUSE: Same logging pattern
        usage_log = APIUsageLog(
            user_id=user_id,
            provider=APIProvider.STABILITY,
            model_used=model,
            cost_total=cost,
            response_size=len(result_bytes),
            billing_period=current_period,
        )
        db.add(usage_log)
        db.commit()
        
        return {"current_calls": current_calls + 1, "cost": cost}
    finally:
        db.close()

# USE: In all operation functions
def generate_image_edit(...):
    result = provider.edit(...)
    if user_id and result:
        _track_image_operation_usage(...)  # ✅ REUSE
    return result
```

---

### **Pattern 5: Service Integration**

#### **Video Studio (Reference)**
```python
# backend/services/video_studio/video_studio_service.py

class VideoStudioService:
    async def generate_image_to_video(
        self,
        image_data: bytes,
        provider: str = "wavespeed",
        model: str = "alibaba/wan-2.5",
        user_id: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate video from image."""
        from services.llm_providers.main_video_generation import ai_video_generate
        
        # Use unified entry point
        result = ai_video_generate(
            image_data=image_data,
            operation_type="image-to-video",
            provider=provider,
            user_id=user_id,
            model=model,
            **kwargs
        )
        
        # Save video file
        save_result = self._save_video_file(
            video_bytes=result["video_bytes"],
            operation_type="image-to-video",
            user_id=user_id,
        )
        
        return {
            "video_url": save_result["file_url"],
            "cost": result["cost"],
            "metadata": result["metadata"],
        }
```

#### **Image Studio (Proposed)**
```python
# backend/services/image_studio/create_service.py

class CreateStudioService:
    async def generate(
        self,
        request: CreateStudioRequest,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate image using unified entry point."""
        from services.llm_providers.main_image_operations import ai_image_generate
        
        # Use unified entry point
        result = await ai_image_generate(
            prompt=request.prompt,
            operation_type="text-to-image",
            provider=request.provider or "auto",
            model=request.model,
            user_id=user_id,
            width=request.width,
            height=request.height,
            **request.to_kwargs(),
        )
        
        # Save to asset library
        asset = save_to_asset_library(
            image_bytes=result["image_bytes"],
            user_id=user_id,
            module="create_studio",
            metadata=result["metadata"],
        )
        
        return {
            "images": [result["image_bytes"]],
            "asset_id": asset.id,
            "cost": result["cost"],
            "metadata": result["metadata"],
        }
```

---

## 🔑 Key Differences to Note

### **1. Operation Types**
- **Video**: `text-to-video`, `image-to-video`
- **Image**: `text-to-image`, `image-edit`, `image-upscale`, `image-to-3d`, `face-swap`, etc.

### **2. Return Formats**
- **Video**: Always returns `video_bytes`
- **Image**: Returns `image_bytes` (but may also return 3D models, etc.)

### **3. Cost Calculation**
- **Video**: Based on duration, resolution
- **Image**: Based on model, operation type, resolution

### **4. Usage Tracking**
- **Video**: Tracks `video_calls`, `video_cost`
- **Image**: Tracks `stability_calls`, `image_edit_calls`, etc. based on operation type

---

## 📝 Checklist for Adding New Model (REUSABLE PATTERN)

### **Step 1: Add to Provider** (REUSES existing pattern)
- [ ] Add model to provider's `SUPPORTED_MODELS` dict
  ```python
  # In WaveSpeedEditProvider
  SUPPORTED_MODELS["new-model"] = {
      "model_path": "wavespeed-ai/new-model",
      "cost": 0.05,
  }
  ```

### **Step 2: Register in Model Registry** (REUSES registry)
- [ ] Add to `ImageModelRegistry.MODELS`
  ```python
  ImageModelRegistry.MODELS["new-model"] = ImageModel(
      id="new-model",
      provider="wavespeed",
      model_path="wavespeed-ai/new-model",
      cost=0.05,  # From provider
      category="editing",
  )
  ```

### **Step 3: Use in Service** (REUSES unified entry)
- [ ] Call unified entry point (validation/tracking automatic)
  ```python
  result = generate_image_edit(
      model="new-model",  # ✅ Just specify model ID
      image_base64=image,
      prompt=prompt,
      user_id=user_id,
  )
  ```

### **Key Reusability Points**
- ✅ **No new validation code** - reuses `_validate_image_operation()`
- ✅ **No new tracking code** - reuses `_track_image_operation_usage()`
- ✅ **No new provider base** - follows `ImageEditProvider` protocol
- ✅ **No new client code** - reuses `WaveSpeedClient`
- ✅ **Consistent pattern** - same as existing models

---

## 🔄 Reusability Quick Reference

### **Existing Code to Reuse**
- ✅ `main_image_generation.py` - Extend this file (don't create new)
- ✅ `ImageGenerationProvider` protocol - Extend this pattern
- ✅ `WaveSpeedClient` - Reuse for all WaveSpeed operations
- ✅ Validation logic - Extract to helper
- ✅ Tracking logic - Extract to helper

### **Pattern to Follow**
```python
# 1. Extract helpers from existing code
def _validate_image_operation(...):  # Extract from generate_image()
def _track_image_operation_usage(...):  # Extract from generate_image()

# 2. Extend existing file
def generate_image_edit(...):  # Add to main_image_generation.py
    _validate_image_operation(...)  # REUSE
    result = provider.edit(...)
    _track_image_operation_usage(...)  # REUSE
    return result

# 3. Extend provider protocol
class ImageEditProvider(Protocol):  # Add to base.py
    def edit(...) -> ImageGenerationResult: ...

# 4. Create provider following pattern
class WaveSpeedEditProvider(ImageEditProvider):
    def __init__(self):
        self.client = WaveSpeedClient()  # REUSE client
    
    def edit(...):
        return self.client.edit_image(...)  # REUSE client
```

---

*Document Version: 2.0*  
*Last Updated: Current Session*  
*Status: Implementation Reference - Reusability Focus*
