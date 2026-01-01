# Video Studio Feature Analysis & Implementation Plan

## 1. Transform Studio - AI Model Documentation Review

### ✅ Phase 1 Complete (FFmpeg Features)
- Format Conversion (MP4, MOV, WebM, GIF)
- Aspect Ratio Conversion (16:9, 9:16, 1:1, 4:5, 21:9)
- Speed Adjustment (0.25x - 4x)
- Resolution Scaling (480p - 4K)
- Compression (File size optimization)

### ⚠️ Phase 2 Pending (Style Transfer - Needs Documentation)

**Required AI Models for Style Transfer:**

1. **WAN 2.1 Ditto** - Video-to-Video Restyle
   - Model: `wavespeed-ai/wan-2.1/ditto`
   - Purpose: Apply artistic styles to videos
   - Status: ⚠️ **Documentation needed**
   - Documentation Requirements:
     - API endpoint URL
     - Input parameters (video, style prompt, style reference image)
     - Output format and metadata
     - Pricing structure
     - Supported resolutions (480p, 720p, 1080p?)
     - Duration limits
     - Use cases and best practices
   - WaveSpeed Link: Need to verify/find

2. **WAN 2.1 Synthetic-to-Real Ditto**
   - Model: `wavespeed-ai/wan-2.1/synthetic-to-real-ditto`
   - Purpose: Convert AI-generated videos to realistic style
   - Status: ⚠️ **Documentation needed**
   - Documentation Requirements: Same as above

**Optional Models (Future):**
- `mirelo-ai/sfx-v1.5/video-to-video` - Alternative style transfer
- `decart/lucy-edit-pro` - Advanced editing and style transfer

---

## 2. Face Swap Feature Analysis

### Current Status: ⚠️ **Partially Implemented (Stub)**

**Backend Code Found:**
- `backend/routers/video_studio/endpoints/avatar.py` - Endpoint accepts `video_file` parameter for face swap
- `backend/services/video_studio/video_studio_service.py` - `generate_avatar_video()` method references face swap
- Model mapping: `"wavespeed/mocha": "wavespeed/mocha/face-swap"`

**Issues Found:**
- ❌ `WaveSpeedClient.generate_video()` method **DOES NOT EXIST**
- ❌ Face swap functionality is **NOT IMPLEMENTED**
- ⚠️ Code structure exists but calls non-existent method

**Documentation References:**
- Comprehensive Plan mentions: `wavespeed-ai/wan-2.1/mocha` (face swap)
- Model catalog lists: `wavespeed-ai/wan-2.1/mocha`, `wavespeed-ai/video-face-swap`

**Required Documentation:**
1. **WAN 2.1 MoCha Face Swap**
   - Model: `wavespeed-ai/wan-2.1/mocha` or `wavespeed-ai/wan-2.1/mocha/face-swap`
   - Purpose: Swap faces in videos
   - Documentation needed:
     - API endpoint
     - Input parameters (source video, face image, optional mask)
     - Output format
     - Pricing
     - Supported resolutions/durations
     - Face detection requirements
     - Best practices

2. **Video Face Swap (Alternative)**
   - Model: `wavespeed-ai/video-face-swap` (if different from MoCha)
   - Documentation: Same as above

**Recommendation:**
- Face swap should be part of **Edit Studio** (not Avatar Studio)
- Avatar Studio is for talking avatars (photo + audio → talking video)
- Face swap is for replacing faces in existing videos (video + face image → swapped video)

---

## 3. Video Translation Feature Analysis

### Current Status: ⚠️ **Partially Implemented (Stub)**

**Backend Code Found:**
- `backend/services/video_studio/video_studio_service.py` - References `heygen/video-translate`
- Model mapping: `"heygen/video-translate": "heygen/video-translate"`
- Listed in available models but **NOT IMPLEMENTED**

**Documentation References:**
- Comprehensive Plan mentions: `heygen/video-translate` (dubbing/translation)
- Model catalog lists: Audio/foley/dubbing models

**Required Documentation:**
1. **HeyGen Video Translate**
   - Model: `heygen/video-translate`
   - Purpose: Translate video language with lip-sync
   - Documentation needed:
     - API endpoint
     - Input parameters (video, source language, target language)
     - Output format
     - Pricing
     - Supported languages
     - Duration limits
     - Lip-sync quality
     - Best practices

**Alternative Models (If HeyGen not available):**
- `wavespeed-ai/hunyuan-video-foley` - Audio generation
- `wavespeed-ai/think-sound` - Audio generation
- May need separate translation service + audio generation

**Recommendation:**
- Video translation should be part of **Edit Studio** or a separate **Localization Studio**
- Could be integrated with Avatar Studio for multilingual avatar videos
- Consider workflow: Video → Translate Audio → Generate Lip-Sync → Output

---

## 4. Social Optimizer Implementation Plan

### Overview
Social Optimizer creates platform-optimized versions of videos for Instagram, TikTok, YouTube, LinkedIn, Facebook, and Twitter.

### Features to Implement

#### Core Features (FFmpeg-based - Can Start Immediately):

1. **Platform Presets**
   - Instagram Reels (9:16, max 90s)
   - TikTok (9:16, max 60s)
   - YouTube Shorts (9:16, max 60s)
   - LinkedIn Video (16:9, max 10min)
   - Facebook (16:9 or 1:1, max 240s)
   - Twitter/X (16:9, max 140s)

2. **Aspect Ratio Conversion**
   - Auto-crop to platform ratio (reuse Transform Studio logic)
   - Smart cropping (center, face detection)
   - Letterboxing/pillarboxing

3. **Duration Trimming**
   - Auto-trim to platform max duration
   - Smart trimming (keep beginning, middle, or end)
   - User-selectable trim points

4. **File Size Optimization**
   - Compress to meet platform limits
   - Quality presets per platform
   - Bitrate optimization

5. **Thumbnail Generation**
   - Extract frame from video (FFmpeg)
   - Generate multiple thumbnails (start, middle, end)
   - Custom thumbnail selection

#### Advanced Features (May Need AI):

6. **Caption Overlay**
   - Auto-caption generation (speech-to-text)
   - Platform-specific caption styles
   - Safe zone overlays

7. **Safe Zone Visualization**
   - Show text-safe areas per platform
   - Visual overlay in preview
   - Platform-specific guidelines

### Implementation Strategy

**Phase 1: Core Features (FFmpeg)**
- Platform presets and aspect ratio conversion
- Duration trimming
- File size compression
- Basic thumbnail generation
- Batch export for multiple platforms

**Phase 2: Advanced Features**
- Caption overlay (may need speech-to-text API)
- Safe zone visualization
- Enhanced thumbnail generation

### Technical Approach

**Backend:**
- Reuse `video_processors.py` from Transform Studio
- Create `social_optimizer_service.py`
- Platform specifications (aspect ratios, durations, file size limits)
- Batch processing for multiple platforms

**Frontend:**
- Platform selection checkboxes
- Preview grid showing all platform versions
- Individual download or batch download
- Progress tracking for batch operations

### Platform Specifications

| Platform | Aspect Ratio | Max Duration | Max File Size | Formats |
|----------|--------------|--------------|---------------|---------|
| Instagram Reels | 9:16 | 90s | 4GB | MP4 |
| TikTok | 9:16 | 60s | 287MB | MP4, MOV |
| YouTube Shorts | 9:16 | 60s | 256GB | MP4, MOV, WebM |
| LinkedIn | 16:9, 1:1 | 10min | 5GB | MP4 |
| Facebook | 16:9, 1:1 | 240s | 4GB | MP4, MOV |
| Twitter/X | 16:9 | 140s | 512MB | MP4 |

---

## Summary & Recommendations

### Transform Studio
- ✅ **Phase 1 Complete**: All FFmpeg features implemented
- ⚠️ **Phase 2 Pending**: Need documentation for style transfer models (Ditto)

### Face Swap
- ⚠️ **Not Implemented**: Code structure exists but functionality missing
- 📋 **Action Required**: 
  - Get WaveSpeed documentation for `wavespeed-ai/wan-2.1/mocha` or `wavespeed-ai/video-face-swap`
  - Implement face swap in **Edit Studio** (not Avatar Studio)
  - Add face swap tab to Edit Studio UI

### Video Translation
- ⚠️ **Not Implemented**: Only referenced in code, no actual implementation
- 📋 **Action Required**:
  - Get HeyGen documentation for `heygen/video-translate`
  - Or find alternative translation + lip-sync solution
  - Consider adding to Edit Studio or separate Localization module

### Social Optimizer
- ✅ **Can Start Immediately**: 80% of features use FFmpeg (reuse Transform Studio processors)
- 📋 **Implementation Plan**: 
  - Phase 1: Platform presets, aspect conversion, trimming, compression, thumbnails
  - Phase 2: Caption overlay, safe zones (may need additional APIs)

---

## Next Steps Priority

1. **Social Optimizer** (Immediate - No AI docs needed)
   - Reuse Transform Studio processors
   - Platform specifications
   - Batch processing

2. **Face Swap** (After Social Optimizer)
   - Get WaveSpeed MoCha documentation
   - Implement in Edit Studio
   - Add UI for face selection

3. **Video Translation** (After Face Swap)
   - Get HeyGen documentation
   - Implement translation + lip-sync
   - Add to Edit Studio or separate module

4. **Style Transfer** (Transform Studio Phase 2)
   - Get Ditto model documentation
   - Add style transfer tab to Transform Studio
