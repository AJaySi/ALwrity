# Transform Studio Implementation Plan

## Overview

Transform Studio allows users to convert videos between formats, change aspect ratios, adjust speed, compress, and apply style transfers to videos.

## Features Breakdown

### ✅ **No AI Documentation Needed** (FFmpeg/MoviePy-based)

These features can be implemented immediately using existing video processing libraries:

1. **Format Conversion** (MP4, MOV, WebM, GIF)
   - Tool: FFmpeg/MoviePy
   - No AI models needed
   - Can implement immediately

2. **Aspect Ratio Conversion** (16:9 ↔ 9:16 ↔ 1:1)
   - Tool: FFmpeg/MoviePy
   - No AI models needed
   - Can implement immediately

3. **Speed Adjustment** (Slow motion, fast forward)
   - Tool: FFmpeg/MoviePy
   - No AI models needed
   - Can implement immediately

4. **Resolution Scaling** (Scale up or down)
   - Tool: FFmpeg/MoviePy
   - Note: We already have FlashVSR for AI upscaling (in Enhance Studio)
   - For downscaling/simple scaling, FFmpeg is sufficient
   - Can implement immediately

5. **Compression** (Optimize file size)
   - Tool: FFmpeg/MoviePy
   - No AI models needed
   - Can implement immediately

### ⚠️ **AI Documentation Needed** (Style Transfer)

For **video-to-video style transfer**, we need WaveSpeed AI model documentation:

#### Required Models:

1. **WAN 2.1 Ditto** - Video-to-Video Restyle
   - Model: `wavespeed-ai/wan-2.1/ditto`
   - Purpose: Apply artistic styles to videos
   - Documentation needed:
     - API endpoint
     - Input parameters (video, style prompt/reference)
     - Output format
     - Pricing
     - Supported resolutions/durations
     - Use cases and best practices
   - WaveSpeed Link: Need to find/verify

2. **WAN 2.1 Synthetic-to-Real Ditto**
   - Model: `wavespeed-ai/wan-2.1/synthetic-to-real-ditto`
   - Purpose: Convert synthetic/AI-generated videos to realistic style
   - Documentation needed:
     - API endpoint
     - Input parameters
     - Output format
     - Pricing
     - Use cases
   - WaveSpeed Link: Need to find/verify

#### Optional Models (Future):

3. **SFX V1.5 Video-to-Video**
   - Model: `mirelo-ai/sfx-v1.5/video-to-video`
   - Purpose: Video style transfer
   - Documentation: Can be added later

4. **Lucy Edit Pro**
   - Model: `decart/lucy-edit-pro`
   - Purpose: Advanced video editing and style transfer
   - Documentation: Can be added later

## Implementation Strategy

### Phase 1: Immediate Implementation (No Docs Needed)

Start with FFmpeg-based features:

1. **Format Conversion**
   - MP4, MOV, WebM, GIF
   - Codec selection (H.264, VP9, etc.)
   - Quality presets

2. **Aspect Ratio Conversion**
   - 16:9, 9:16, 1:1, 4:5, 21:9
   - Smart cropping (center, face detection, etc.)
   - Letterboxing/pillarboxing options

3. **Speed Adjustment**
   - 0.25x, 0.5x, 1.5x, 2x, 4x
   - Smooth frame interpolation

4. **Resolution Scaling**
   - Scale to target resolution
   - Maintain aspect ratio
   - Quality presets

5. **Compression**
   - Target file size
   - Quality-based compression
   - Bitrate control

### Phase 2: Style Transfer (After Documentation)

Once we have model documentation:

1. **Add Style Transfer Tab**
2. **Implement WAN 2.1 Ditto integration**
3. **Implement Synthetic-to-Real Ditto**
4. **Add style presets (Cinematic, Vintage, Artistic, etc.)**

## Technical Implementation

### Backend Structure

```
backend/services/video_studio/
├── transform_service.py          # Main transform service
├── video_processors/
│   ├── format_converter.py       # Format conversion (FFmpeg)
│   ├── aspect_converter.py       # Aspect ratio conversion (FFmpeg)
│   ├── speed_adjuster.py         # Speed adjustment (FFmpeg)
│   ├── resolution_scaler.py      # Resolution scaling (FFmpeg)
│   └── compressor.py             # Compression (FFmpeg)
└── style_transfer/
    └── ditto_service.py          # Style transfer (WaveSpeed AI) - Phase 2
```

### Frontend Structure

```
frontend/src/components/VideoStudio/modules/TransformVideo/
├── TransformVideo.tsx            # Main component
├── components/
│   ├── VideoUpload.tsx           # Shared video upload
│   ├── VideoPreview.tsx          # Shared video preview
│   ├── TransformTabs.tsx         # Tab navigation
│   ├── FormatConverter.tsx       # Format conversion UI
│   ├── AspectConverter.tsx       # Aspect ratio UI
│   ├── SpeedAdjuster.tsx         # Speed adjustment UI
│   ├── ResolutionScaler.tsx      # Resolution scaling UI
│   ├── Compressor.tsx            # Compression UI
│   └── StyleTransfer.tsx         # Style transfer UI (Phase 2)
└── hooks/
    └── useTransformVideo.ts      # Shared state management
```

## API Endpoint

```
POST /api/video-studio/transform
```

### Request Parameters:

```typescript
{
  file: File,                      // Video file
  transform_type: string,          // "format" | "aspect" | "speed" | "resolution" | "compress" | "style"
  
  // Format conversion
  output_format?: "mp4" | "mov" | "webm" | "gif",
  codec?: "h264" | "vp9" | "h265",
  quality?: "high" | "medium" | "low",
  
  // Aspect ratio
  target_aspect?: "16:9" | "9:16" | "1:1" | "4:5" | "21:9",
  crop_mode?: "center" | "smart" | "letterbox",
  
  // Speed
  speed_factor?: number,           // 0.25, 0.5, 1.0, 1.5, 2.0, 4.0
  
  // Resolution
  target_resolution?: string,      // "480p" | "720p" | "1080p"
  maintain_aspect?: boolean,
  
  // Compression
  target_size_mb?: number,         // Target file size in MB
  quality?: "high" | "medium" | "low",
  
  // Style transfer (Phase 2)
  style_prompt?: string,
  style_reference?: File,
  model?: "ditto" | "synthetic-to-real-ditto",
}
```

## Summary

### Can Start Immediately ✅

- Format Conversion
- Aspect Ratio Conversion
- Speed Adjustment
- Resolution Scaling
- Compression

**Tools**: FFmpeg/MoviePy (already available in codebase via MoviePy)

### Need Documentation First ⚠️

- **Style Transfer** - Need WaveSpeed AI model docs for:
  1. `wavespeed-ai/wan-2.1/ditto`
  2. `wavespeed-ai/wan-2.1/synthetic-to-real-ditto`

### Recommendation

1. **Start Phase 1** (FFmpeg features) - Can implement immediately
2. **Request documentation** for style transfer models
3. **Implement Phase 2** (Style transfer) once docs are available

This allows us to deliver 80% of Transform Studio functionality immediately while waiting for AI model documentation.
