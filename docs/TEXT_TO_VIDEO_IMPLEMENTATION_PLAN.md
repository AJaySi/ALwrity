# Text-to-Video Implementation Plan - Phase 1

## Goal
Implement WaveSpeed text-to-video support in the unified `ai_video_generate()` entry point with modular, maintainable code structure.

## Proposed Architecture

### Modular Structure (Following Image Generation Pattern)

```
backend/services/llm_providers/
├── main_video_generation.py          # Unified entry point (already exists)
└── video_generation/                 # NEW: Modular video generation services
    ├── __init__.py
    ├── base.py                       # Base classes/interfaces
    └── wavespeed_provider.py         # WaveSpeed text-to-video models
        ├── HunyuanVideoService       # HunyuanVideo-1.5
        ├── LTX2ProService            # LTX-2 Pro
        ├── LTX2FastService           # LTX-2 Fast
        └── LTX2RetakeService         # LTX-2 Retake
```

### Implementation Strategy

**Step 1: Create Base Structure**
- Create `video_generation/` directory
- Create `base.py` with base classes/interfaces
- Create `wavespeed_provider.py` with service classes

**Step 2: Implement First Model (HunyuanVideo-1.5)**
- Create `HunyuanVideoService` class
- Implement model-specific logic
- Add progress callback support
- Return metadata dict

**Step 3: Integrate into Unified Entry Point**
- Add `_generate_text_to_video_wavespeed()` function
- Route to appropriate service based on model
- Handle async/sync properly

**Step 4: Test and Validate**
- Test with one model
- Verify all features work
- Ensure backward compatibility

**Step 5: Add Remaining Models**
- Follow same pattern for LTX-2 Pro, Fast, Retake
- Reuse common logic
- Model-specific differences only

## Model Selection

**Recommended Starting Model:** **HunyuanVideo-1.5**
- Most commonly used
- Good documentation availability
- Standard parameters

**Alternative:** Any model you prefer - we'll follow the same pattern.

## Service Class Structure

```python
class HunyuanVideoService:
    """Service for HunyuanVideo-1.5 text-to-video generation."""
    
    MODEL_PATH = "wavespeed-ai/hunyuan-video-1.5/text-to-video"
    MODEL_NAME = "hunyuan-video-1.5"
    
    def __init__(self, client: Optional[WaveSpeedClient] = None):
        self.client = client or WaveSpeedClient()
    
    async def generate_video(
        self,
        prompt: str,
        duration: int = 5,
        resolution: str = "720p",
        negative_prompt: Optional[str] = None,
        seed: Optional[int] = None,
        audio_base64: Optional[str] = None,
        enable_prompt_expansion: bool = True,
        progress_callback: Optional[Callable[[float, str], None]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate video using HunyuanVideo-1.5.
        
        Returns:
            Dict with video_bytes, prompt, duration, model_name, cost, etc.
        """
        # 1. Validate inputs
        # 2. Build payload
        # 3. Submit to WaveSpeed
        # 4. Poll with progress callbacks
        # 5. Download video
        # 6. Return metadata dict
```

## Integration Points

### Unified Entry Point
```python
# In main_video_generation.py
async def _generate_text_to_video_wavespeed(
    prompt: str,
    model: str = "hunyuan-video-1.5",
    progress_callback: Optional[Callable[[float, str], None]] = None,
    **kwargs
) -> Dict[str, Any]:
    """Route to appropriate WaveSpeed text-to-video service."""
    from .video_generation.wavespeed_provider import get_wavespeed_text_to_video_service
    
    service = get_wavespeed_text_to_video_service(model)
    return await service.generate_video(
        prompt=prompt,
        progress_callback=progress_callback,
        **kwargs
    )
```

## Next Steps

1. **Wait for Model Documentation** - You'll provide documentation for the first model
2. **Create Base Structure** - Set up directory and base classes
3. **Implement First Model** - HunyuanVideo-1.5 (or your chosen model)
4. **Test** - Verify functionality
5. **Add Remaining Models** - Follow same pattern

## Questions

1. **Which model should we start with?** (Recommended: HunyuanVideo-1.5)
2. **Do you have the model documentation ready?** (API endpoints, parameters, response format)
3. **Any specific requirements for the first model?** (Parameters, features, etc.)
