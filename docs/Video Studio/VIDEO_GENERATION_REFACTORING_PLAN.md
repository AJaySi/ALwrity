# Video Generation Refactoring Plan

## Goal
Remove redundant/duplicate code across video studio, image studio, story writer, etc., and ensure all video generation goes through the unified `ai_video_generate()` entry point.

## Current State Analysis

### ✅ Already Using Unified Entry Point
1. **Image Studio Transform Service** (`backend/services/image_studio/transform_service.py`)
   - ✅ Uses `ai_video_generate()` for image-to-video
   - ✅ Properly handles file saving and asset library

2. **Video Studio Service - Image-to-Video** (`backend/services/video_studio/video_studio_service.py`)
   - ✅ `generate_image_to_video()` uses `ai_video_generate()`
   - ✅ Properly handles file saving and asset library

3. **Story Writer** (`backend/api/story_writer/utils/hd_video.py`)
   - ✅ Uses `ai_video_generate()` for text-to-video
   - ✅ Properly handles file saving

### ❌ Issues Found - Redundant Code

1. **Video Studio Service - Text-to-Video** (`backend/services/video_studio/video_studio_service.py:99`)
   - ❌ Calls `self.wavespeed_client.generate_video()` which **DOES NOT EXIST**
   - ❌ Bypasses unified entry point
   - ❌ Missing pre-flight validation
   - ❌ Missing usage tracking
   - **Action**: Refactor to use `ai_video_generate()`

2. **Video Studio Service - Avatar Generation** (`backend/services/video_studio/video_studio_service.py:320`)
   - ❌ Calls `self.wavespeed_client.generate_video()` which **DOES NOT EXIST**
   - ⚠️ This is a different operation (talking avatar) - may need separate handling
   - **Action**: Investigate if this should use unified entry point or stay separate

3. **Video Studio Service - Video Enhancement** (`backend/services/video_studio/video_studio_service.py:405`)
   - ❌ Calls `self.wavespeed_client.generate_video()` which **DOES NOT EXIST**
   - ⚠️ This is a different operation (video-to-video) - may need separate handling
   - **Action**: Investigate if this should use unified entry point or stay separate

4. **Unified Entry Point - WaveSpeed Text-to-Video** (`backend/services/llm_providers/main_video_generation.py:454`)
   - ❌ Currently raises `VideoProviderNotImplemented` for WaveSpeed text-to-video
   - **Action**: Implement WaveSpeed text-to-video support

### ⚠️ Special Cases (Keep Separate for Now)

1. **Podcast InfiniteTalk** (`backend/services/wavespeed/infinitetalk.py`)
   - ✅ Specialized operation: talking avatar with audio sync
   - ✅ Has its own polling and error handling
   - **Decision**: Keep separate - this is a specialized use case

## Refactoring Steps

### Phase 1: Implement WaveSpeed Text-to-Video in Unified Entry Point

**File**: `backend/services/llm_providers/main_video_generation.py`

**Changes**:
1. Add `_generate_text_to_video_wavespeed()` function
2. Use `WaveSpeedClient.generate_text_video()` or `submit_text_to_video()` + polling
3. Support models: hunyuan-video-1.5, ltx-2-pro, ltx-2-fast, ltx-2-retake
4. Return metadata dict with video_bytes, cost, duration, etc.

**Implementation**:
```python
async def _generate_text_to_video_wavespeed(
    prompt: str,
    duration: int = 5,
    resolution: str = "720p",
    model: str = "hunyuan-video-1.5/text-to-video",
    negative_prompt: Optional[str] = None,
    seed: Optional[int] = None,
    audio_base64: Optional[str] = None,
    enable_prompt_expansion: bool = True,
    progress_callback: Optional[Callable[[float, str], None]] = None,
    **kwargs
) -> Dict[str, Any]:
    """Generate text-to-video using WaveSpeed models."""
    from services.wavespeed.client import WaveSpeedClient
    
    client = WaveSpeedClient()
    
    # Map model names to full paths
    model_mapping = {
        "hunyuan-video-1.5": "hunyuan-video-1.5/text-to-video",
        "lightricks/ltx-2-pro": "lightricks/ltx-2-pro/text-to-video",
        "lightricks/ltx-2-fast": "lightricks/ltx-2-fast/text-to-video",
        "lightricks/ltx-2-retake": "lightricks/ltx-2-retake/text-to-video",
    }
    full_model = model_mapping.get(model, model)
    
    # Use generate_text_video which handles polling internally
    result = await client.generate_text_video(
        prompt=prompt,
        resolution=resolution,
        duration=duration,
        negative_prompt=negative_prompt,
        seed=seed,
        audio_base64=audio_base64,
        enable_prompt_expansion=enable_prompt_expansion,
        enable_sync_mode=False,  # Use async mode with polling
        timeout=600,  # 10 minutes
    )
    
    return {
        "video_bytes": result["video_bytes"],
        "prompt": prompt,
        "duration": float(duration),
        "model_name": full_model,
        "cost": result.get("cost", 0.0),
        "provider": "wavespeed",
        "resolution": resolution,
        "width": result.get("width", 1280),
        "height": result.get("height", 720),
        "metadata": result.get("metadata", {}),
    }
```

### Phase 2: Refactor VideoStudioService.generate_text_to_video()

**File**: `backend/services/video_studio/video_studio_service.py`

**Changes**:
1. Replace `self.wavespeed_client.generate_video()` call with `ai_video_generate()`
2. Remove model mapping (handled in unified entry point)
3. Remove cost calculation (handled in unified entry point)
4. Add file saving and asset library integration
5. Preserve existing return format for backward compatibility

**Before**:
```python
result = await self.wavespeed_client.generate_video(...)  # DOES NOT EXIST
```

**After**:
```python
result = ai_video_generate(
    prompt=prompt,
    operation_type="text-to-video",
    provider=provider,
    user_id=user_id,
    duration=duration,
    resolution=resolution,
    negative_prompt=negative_prompt,
    model=model,
    **kwargs
)

# Save file and update asset library
save_result = self._save_video_file(...)
```

### Phase 3: Fix Avatar and Enhancement Methods

**Decision Needed**: 
- Are avatar generation and video enhancement different enough to warrant separate handling?
- Or should they be integrated into unified entry point?

**Options**:
1. **Keep Separate**: Create separate unified entry points (`ai_avatar_generate()`, `ai_video_enhance()`)
2. **Integrate**: Add `operation_type="avatar"` and `operation_type="enhance"` to `ai_video_generate()`

**Recommendation**: Keep separate for now, but ensure they use proper WaveSpeed client methods.

## Testing Strategy

### Pre-Refactoring
1. ✅ Document current behavior
2. ✅ Identify all call sites
3. ✅ Create test cases for each scenario

### Post-Refactoring
1. Test text-to-video with WaveSpeed models
2. Test image-to-video (already working)
3. Verify pre-flight validation works
4. Verify usage tracking works
5. Verify file saving works
6. Verify asset library integration works

## Risk Mitigation

1. **Backward Compatibility**: Preserve existing return formats
2. **Gradual Migration**: Refactor one method at a time
3. **Feature Flags**: Consider feature flag for new unified path
4. **Comprehensive Testing**: Test all scenarios before deployment

## Files to Modify

1. `backend/services/llm_providers/main_video_generation.py`
   - Add `_generate_text_to_video_wavespeed()`
   - Update `ai_video_generate()` to support WaveSpeed text-to-video

2. `backend/services/video_studio/video_studio_service.py`
   - Refactor `generate_text_to_video()` to use `ai_video_generate()`
   - Fix `generate_avatar()` and `enhance_video()` method calls

3. `backend/routers/video_studio.py`
   - Update to use refactored service methods

## Success Criteria

- ✅ All video generation goes through unified entry point
- ✅ No redundant code
- ✅ Pre-flight validation works everywhere
- ✅ Usage tracking works everywhere
- ✅ File saving works everywhere
- ✅ Asset library integration works everywhere
- ✅ No breaking changes
- ✅ All existing functionality preserved
