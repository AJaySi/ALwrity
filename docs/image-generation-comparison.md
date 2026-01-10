# Image Generation Implementation Comparison

## Overview
This document compares how **Podcast Maker**, **Story Writer**, and **Blog Writer** implement AI image generation, focusing on model selection, provider routing, and best practices.

---

## 1. **Podcast Maker** (`backend/api/podcast/handlers/images.py`)

### Key Features:
- **Dual Mode**: Character-consistent generation (Ideogram Character) vs. standard generation
- **Auto Provider Selection**: Uses `provider: None` to auto-select based on environment
- **Specialized Prompt Building**: Podcast-optimized prompts with scene context
- **Pre-flight Validation**: Subscription checks before API calls

### Model Usage:
```python
# Character-consistent generation (when base_avatar_url provided)
generate_character_image(
    prompt=image_prompt,
    reference_image_bytes=base_avatar_bytes,
    user_id=user_id,
    style=style,  # "Realistic", "Fiction", "Auto"
    aspect_ratio=aspect_ratio,  # "1:1", "16:9", "9:16", "4:3", "3:4"
    rendering_speed=rendering_speed,  # "Default", "Turbo", "Quality"
)
# Model: ideogram-ai/ideogram-character (WaveSpeed)
# Cost: ~$0.10/image

# Standard generation (no base avatar)
generate_image(
    prompt=image_prompt,
    options={
        "provider": None,  # Auto-select
        "width": request.width,
        "height": request.height,
    },
    user_id=user_id
)
# Provider: Auto-selected (WaveSpeed, HuggingFace, or Stability)
# Cost: ~$0.04/image (varies by provider)
```

### Prompt Building Strategy:
- **Scene Context**: Scene title, content preview, visual keywords
- **Podcast Theme**: Idea/topic context
- **Technical Requirements**: 16:9 aspect ratio, video-optimized composition
- **Style Constraints**: Realistic photography, professional broadcast quality

### Error Handling:
- **Character Generation Failure**: Raises HTTPException (no fallback to standard)
- **Timeout/Connection Issues**: Returns 504 with retry recommendation
- **Other Errors**: Returns 502 with error details

---

## 2. **Story Writer** (`backend/services/story_writer/image_generation_service.py`)

### Key Features:
- **Simple Wrapper**: Thin service layer around `generate_image()`
- **Batch Processing**: Generates images for multiple scenes sequentially
- **Progress Callbacks**: Supports progress tracking for batch operations
- **Error Resilience**: Continues with next scene if one fails

### Model Usage:
```python
# Single scene generation
generate_image(
    prompt=image_prompt,  # From scene.image_prompt
    options={
        "provider": provider,  # Optional, can be None for auto-select
        "width": width,  # Default: 1024
        "height": height,  # Default: 1024
        "model": model,  # Optional
    },
    user_id=user_id
)

# Batch generation
generate_scene_images(
    scenes=scenes_data,
    user_id=user_id,
    provider=request.provider,  # Optional
    width=request.width or 1024,
    height=request.height or 1024,
    model=request.model,  # Optional
    progress_callback=progress_callback  # Optional
)
```

### Prompt Strategy:
- **Direct Use**: Uses `scene.image_prompt` directly (no prompt building)
- **Pre-generated**: Prompts are created during story outline phase
- **No Modification**: Service doesn't modify prompts

### Error Handling:
- **HTTPException**: Re-raised (e.g., 429 subscription limits)
- **Other Exceptions**: Wrapped in RuntimeError, continues with next scene
- **Partial Success**: Returns results with error field for failed scenes

---

## 3. **Blog Writer** (`frontend/src/components/ImageGen/ImageGenerator.tsx`)

### Key Features:
- **Provider Selection**: User can choose WaveSpeed, HuggingFace, or Stability
- **Model Selection**: Dropdown based on selected provider
- **Dimension Validation**: Frontend validation with model-specific limits
- **Prompt Optimization**: "Optimize Prompt" button for blog-optimized prompts
- **Cost Display**: Shows cost information for WaveSpeed models

### Model Usage:
```typescript
// Frontend component
const req: ImageGenerationRequest = {
  prompt,
  negative_prompt: negative,
  provider,  // 'wavespeed' | 'huggingface' | 'stability'
  model,  // e.g., 'qwen-image', 'ideogram-v3-turbo'
  width,
  height
};

// Backend routing (main_image_generation.py)
// Auto-detects Wavespeed models and remaps provider
wavespeed_models = ["qwen-image", "ideogram-v3-turbo"]
if model_lower in wavespeed_models and provider_name != "wavespeed":
    provider_name = "wavespeed"
```

### Available Models:
- **WaveSpeed**: `qwen-image` ($0.05), `ideogram-v3-turbo` ($0.10)
- **HuggingFace**: `black-forest-labs/FLUX.1-Krea-dev`, `black-forest-labs/FLUX.1-dev`, `runwayml/flux-dev`
- **Stability AI**: `stable-diffusion-xl-1024-v1-0`, `stable-diffusion-xl-base-1.0`

### Dimension Limits:
- **WaveSpeed Models**: Max 1024x1024
- **Other Models**: Max 2048x2048
- **Frontend Validation**: Clamps dimensions and shows errors

### Prompt Optimization:
- **Backend Endpoint**: `/api/images/suggest-prompts`
- **Blog-Optimized**: Focuses on data visualization, infographics, text overlay areas
- **Context-Aware**: Uses title, section, research, persona for better prompts

---

## 4. **Common Patterns & Best Practices**

### Provider Selection:
```python
# Pattern 1: Auto-select (Podcast Maker)
options = {"provider": None}  # Let _select_provider() decide

# Pattern 2: Explicit (Story Writer, Blog Writer)
options = {"provider": "wavespeed"}  # User or service specifies

# Pattern 3: Model-based remapping (Blog Writer backend)
# Automatically remaps provider based on model name
```

### Model Routing:
```python
# Backend auto-detection (main_image_generation.py)
# Detects Wavespeed models and remaps provider
wavespeed_models = ["qwen-image", "ideogram-v3-turbo"]
if model_lower in wavespeed_models and provider_name != "wavespeed":
    provider_name = "wavespeed"
```

### Error Handling:
```python
# Pattern 1: Re-raise HTTPExceptions (subscription limits)
except HTTPException:
    raise

# Pattern 2: Wrap in RuntimeError (Story Writer)
except Exception as e:
    raise RuntimeError(f"Failed to generate image: {str(e)}") from e

# Pattern 3: Return error in result (Story Writer batch)
image_results.append({
    "error": str(e),
    "image_url": None,
})
```

### Subscription Validation:
```python
# Pre-flight validation (Podcast Maker)
validate_image_generation_operations(
    pricing_service=pricing_service,
    user_id=user_id,
    num_images=1
)

# Built-in validation (main_image_generation.py)
_validate_image_operation(
    user_id=user_id,
    operation_type="image-generation",
    num_operations=1,
)
```

---

## 5. **Key Differences**

| Feature | Podcast Maker | Story Writer | Blog Writer |
|---------|---------------|--------------|-------------|
| **Provider Selection** | Auto-select | Optional explicit | User selects |
| **Model Selection** | Auto (Character) or Auto-select | Optional explicit | User selects |
| **Prompt Building** | Custom podcast prompts | Pre-generated | User + optimization |
| **Dimension Limits** | No validation | No validation | Frontend validation |
| **Error Handling** | Strict (no fallback) | Resilient (continues) | User-friendly alerts |
| **Cost Display** | Estimated in response | Not shown | Shown in UI |
| **Special Features** | Character consistency | Batch processing | Prompt optimization |

---

## 6. **Recommendations for Blog Writer**

### ✅ Already Implemented:
1. ✅ Provider/model selection UI
2. ✅ Dimension validation
3. ✅ Model-based provider remapping
4. ✅ Cost information display
5. ✅ Prompt optimization

### 🔄 Could Improve:
1. **Pre-flight Validation**: Add subscription checks before API calls (like Podcast Maker)
2. **Error Messages**: More specific error messages based on error type
3. **Batch Generation**: Support generating multiple images for blog sections
4. **Progress Tracking**: Show progress for multiple image generations
5. **Retry Logic**: Automatic retry for transient failures

### 📝 Implementation Notes:
- **Provider Routing**: Backend correctly auto-detects Wavespeed models
- **Dimension Limits**: Frontend validation prevents invalid dimensions
- **Cost Tracking**: Handled by centralized `generate_image()` function
- **Asset Library**: Images are saved to asset library automatically

---

## 7. **Model-Specific Details**

### WaveSpeed Models:
- **qwen-image**: $0.05/image, max 1024x1024, fast generation
- **ideogram-v3-turbo**: $0.10/image, max 1024x1024, superior text rendering
- **ideogram-character**: $0.10/image, character consistency (Podcast only)

### HuggingFace Models:
- **FLUX.1-Krea-dev**: Photorealistic, optimized for blog images
- **FLUX.1-dev**: General purpose
- **flux-dev**: RunwayML variant

### Stability AI Models:
- **SDXL 1024**: Professional quality, $0.04/image
- **SDXL Base**: Standard quality

---

## 8. **Code References**

### Backend:
- `backend/services/llm_providers/main_image_generation.py` - Core generation logic
- `backend/services/llm_providers/image_generation/wavespeed_provider.py` - WaveSpeed implementation
- `backend/api/podcast/handlers/images.py` - Podcast image generation
- `backend/services/story_writer/image_generation_service.py` - Story Writer service
- `backend/api/images.py` - Blog Writer image API

### Frontend:
- `frontend/src/components/ImageGen/ImageGenerator.tsx` - Blog Writer component
- `frontend/src/components/shared/ImageGenerationModal.tsx` - Shared modal (Podcast/YouTube)
- `frontend/src/components/StoryWriter/Phases/StoryOutlineParts/ImageEditModal.tsx` - Story Writer UI

---

## Summary

All three tools use the centralized `generate_image()` function but with different approaches:

1. **Podcast Maker**: Specialized for character consistency, auto-selects providers
2. **Story Writer**: Simple wrapper, batch processing, error resilient
3. **Blog Writer**: User-controlled provider/model selection, frontend validation, prompt optimization

The Blog Writer implementation is the most user-friendly with explicit controls, while Podcast Maker focuses on specialized use cases and Story Writer prioritizes simplicity and batch operations.
