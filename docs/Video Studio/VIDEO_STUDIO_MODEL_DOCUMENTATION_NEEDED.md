# Video Studio: Model Documentation Needed

**Last Updated**: Current Session  
**Purpose**: Track which AI model documentation is needed to complete immediate next steps

---

## Immediate Next Steps (1-2 Weeks)

### 1. Complete Enhance Studio Frontend
### 2. Add Remaining Text-to-Video Models
### 3. Add Image-to-Video Alternatives

---

## Required Model Documentation

### Priority 1: Enhance Studio Models ⚠️ **URGENT**

#### 1. **FlashVSR (Video Upscaling)** ✅ **RECEIVED**
- **Model**: `wavespeed-ai/flashvsr`
- **Purpose**: Video super-resolution and upscaling
- **Use Case**: Enhance Studio - upscale videos from 480p/720p to 1080p/4K
- **Status**: ✅ Documentation received, implementation in progress
- **Documentation**: https://wavespeed.ai/docs/docs-api/wavespeed-ai/flashvsr
- **Implementation Notes**:
  - Endpoint: `https://api.wavespeed.ai/api/v3/wavespeed-ai/flashvsr`
  - Input: `video` (base64 or URL), `target_resolution` ("720p", "1080p", "2k", "4k")
  - Pricing: $0.06-$0.16 per 5 seconds (based on resolution)
  - Max clip length: 10 minutes
  - Processing: 3-20 seconds wall time per 1 second of video

#### 2. **Video Extend/Outpaint** ✅ **RECEIVED & IMPLEMENTED**
- **Models**: 
  - `alibaba/wan-2.5/video-extend` (Full Featured)
  - `wavespeed-ai/wan-2.2-spicy/video-extend` (Fast & Affordable)
  - `bytedance/seedance-v1.5-pro/video-extend` (Advanced)
- **Purpose**: Extend video duration with motion/audio continuity
- **Use Case**: Extend Studio - extend short clips into longer videos
- **Status**: ✅ Documentation received, all three models implemented with model selector and comparison UI
- **Documentation**: 
  - WAN 2.5: https://wavespeed.ai/docs/docs-api/alibaba/alibaba-wan-2.5-video-extend
  - WAN 2.2 Spicy: https://wavespeed.ai/docs/docs-api/wavespeed-ai/wan-2.2-spicy/video-extend
  - Seedance 1.5 Pro: https://wavespeed.ai/docs/docs-api/bytedance/seedance-v1.5-pro/video-extend
- **Implementation Notes**:
  - **WAN 2.5**: Full featured model
    - Endpoint: `https://api.wavespeed.ai/api/v3/alibaba/wan-2.5/video-extend`
    - Required: `video`, `prompt`
    - Optional: `audio` (URL, ≤15MB, 3-30s), `negative_prompt`, `resolution` (480p/720p/1080p), `duration` (3-10s), `enable_prompt_expansion`, `seed`
    - Pricing: $0.05/s (480p), $0.10/s (720p), $0.15/s (1080p)
    - Audio handling: If audio > video length, only first segment used; if audio < video length, remaining is silent; if no audio, can auto-generate
    - Multilingual: Supports Chinese and English prompts
  - **WAN 2.2 Spicy**: Fast and affordable model
    - Endpoint: `https://api.wavespeed.ai/api/v3/wavespeed-ai/wan-2.2-spicy/video-extend`
    - Required: `video`, `prompt`
    - Optional: `resolution` (480p/720p only), `duration` (5 or 8s only), `seed`
    - Pricing: $0.03/s (480p), $0.06/s (720p) - **Most affordable option**
    - No audio, negative prompt, or prompt expansion support
    - Simpler API for quick extensions
    - Optimized for expressive visuals, smooth temporal coherence, and cinematic color
  - **Seedance 1.5 Pro**: Advanced model with unique features
    - Endpoint: `https://api.wavespeed.ai/api/v3/bytedance/seedance-v1.5-pro/video-extend`
    - Required: `video`, `prompt`
    - Optional: `resolution` (480p/720p only), `duration` (4-12s), `generate_audio` (boolean, default true), `camera_fixed` (boolean, default false), `seed`
    - Pricing (with audio): $0.024/s (480p), $0.052/s (720p)
    - Pricing (without audio): $0.012/s (480p), $0.026/s (720p)
    - **Audio generation doubles the cost** - disable for budget-friendly extensions
    - Unique features: Auto audio generation, camera position control
    - No audio upload, negative prompt, or prompt expansion support
    - Ideal for ad creatives and short dramas
    - Natural motion continuation, stable aesthetics, upscaled output
    - Best practices: Use clean input videos, keep prompts specific but short, start with 5s to validate

---

### Priority 2: Additional Text-to-Video Models

#### 3. **LTX-2 Fast**
- **Model**: `lightricks/ltx-2-fast/text-to-video`
- **Purpose**: Fast draft generation for quick iterations
- **Use Case**: Create Studio - quick previews, draft mode
- **Documentation Needed**:
  - API endpoint
  - Input parameters (prompt, duration, resolution, aspect ratio)
  - Speed/latency characteristics
  - Quality trade-offs vs LTX-2 Pro
  - Pricing (likely lower than Pro)
  - Supported resolutions and durations
- **WaveSpeed Link**: https://wavespeed.ai/models/lightricks/ltx-2-fast/text-to-video
- **Status**: Mentioned in plan, TODO in code (`# "lightricks/ltx-2-fast": LTX2FastService`)

#### 4. **LTX-2 Retake**
- **Model**: `lightricks/ltx-2-retake`
- **Purpose**: Regenerate/retake videos with variations
- **Use Case**: Create Studio - regeneration workflows, variations
- **Documentation Needed**:
  - API endpoint
  - How it differs from initial generation
  - Seed/prompt variation parameters
  - Pricing (likely similar to LTX-2 Pro)
  - Use cases and best practices
- **WaveSpeed Link**: Check for `lightricks/ltx-2-retake` documentation
- **Status**: Mentioned in plan, TODO in code (`# "lightricks/ltx-2-retake": LTX2RetakeService`)

---

### Priority 3: Image-to-Video Alternatives

#### 5. **Kandinsky 5 Pro Image-to-Video**
- **Model**: `wavespeed-ai/kandinsky5-pro/image-to-video`
- **Purpose**: Alternative image-to-video model
- **Use Case**: Create Studio - image-to-video with different quality/style
- **Documentation Needed**:
  - API endpoint
  - Input parameters (image, prompt, duration, resolution)
  - Quality characteristics vs WAN 2.5
  - Pricing structure
  - Supported resolutions (512p/1024p mentioned in plan)
  - Duration limits
  - Best use cases
- **WaveSpeed Link**: https://wavespeed.ai/models/wavespeed-ai/kandinsky5-pro/image-to-video
- **Note**: Plan mentions 5s MP4, 512p/1024p, ~$0.20/0.60 per run

---

## Currently Implemented Models ✅

These models are already implemented and working:
- ✅ **HunyuanVideo-1.5** (`wavespeed-ai/hunyuan-video-1.5/text-to-video`)
- ✅ **LTX-2 Pro** (`lightricks/ltx-2-pro/text-to-video`)
- ✅ **Google Veo 3.1** (`google/veo3.1/text-to-video`)
- ✅ **Hunyuan Avatar** (`wavespeed-ai/hunyuan-avatar`)
- ✅ **InfiniteTalk** (`wavespeed-ai/infinitetalk`)
- ✅ **WAN 2.5** (text-to-video and image-to-video via unified generation)

---

## Documentation Request Format

For each model, please provide:

1. **API Documentation Link** (WaveSpeed model page)
2. **Input Schema**:
   - Required parameters
   - Optional parameters
   - Parameter types and constraints
   - Default values
3. **Output Schema**:
   - Response format
   - File URLs or data format
   - Metadata returned
4. **Pricing Information**:
   - Cost per second/run
   - Resolution-based pricing
   - Duration limits and pricing
5. **Capabilities**:
   - Supported resolutions
   - Duration limits
   - Aspect ratios
   - Special features (audio, style, etc.)
6. **Example Requests/Responses**:
   - cURL examples
   - Python examples
   - Response samples

---

## Implementation Priority

### Week 1 Focus:
1. **FlashVSR** - Critical for Enhance Studio frontend
2. **LTX-2 Fast** - Quick to implement (similar to LTX-2 Pro)

### Week 2 Focus:
3. **LTX-2 Retake** - Complete LTX-2 suite
4. **Kandinsky 5 Pro** - Image-to-video alternative

### Future (Phase 3):
5. **Video-extend** - For Enhance Studio temporal features
6. Other enhancement models as needed

---

## Notes

- All models should follow the same pattern as existing implementations
- Use `BaseWaveSpeedTextToVideoService` or similar base classes
- Integrate into `main_video_generation.py` unified entry point
- Add to model selector in frontend with education system
- Ensure cost estimation and preflight validation work correctly
