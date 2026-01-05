# Social Optimizer Implementation Plan

## Overview

Social Optimizer creates platform-optimized versions of videos for Instagram, TikTok, YouTube, LinkedIn, Facebook, and Twitter with one click. Reuses Transform Studio processors for aspect ratio conversion, trimming, and compression.

## Features

### Core Features (FFmpeg-based - Can Start Immediately)

1. **Platform Presets**
   - Instagram Reels (9:16, max 90s, 4GB)
   - TikTok (9:16, max 60s, 287MB)
   - YouTube Shorts (9:16, max 60s, 256GB)
   - LinkedIn Video (16:9, max 10min, 5GB)
   - Facebook (16:9 or 1:1, max 240s, 4GB)
   - Twitter/X (16:9, max 140s, 512MB)

2. **Aspect Ratio Conversion**
   - Auto-crop to platform ratio (reuse Transform Studio `convert_aspect_ratio`)
   - Smart cropping (center, face detection)
   - Letterboxing/pillarboxing

3. **Duration Trimming**
   - Auto-trim to platform max duration
   - Smart trimming options (keep beginning, middle, end)
   - User-selectable trim points

4. **File Size Optimization**
   - Compress to meet platform limits (reuse Transform Studio `compress_video`)
   - Quality presets per platform
   - Bitrate optimization

5. **Thumbnail Generation**
   - Extract frames from video (FFmpeg)
   - Generate multiple thumbnails (start, middle, end)
   - Custom thumbnail selection

6. **Batch Export**
   - Generate optimized versions for multiple platforms simultaneously
   - Progress tracking per platform
   - Individual or bulk download

### Advanced Features (Phase 2)

7. **Caption Overlay**
   - Auto-caption generation (speech-to-text API needed)
   - Platform-specific caption styles
   - Safe zone overlays

8. **Safe Zone Visualization**
   - Show text-safe areas per platform
   - Visual overlay in preview
   - Platform-specific guidelines

## Platform Specifications

| Platform | Aspect Ratio | Max Duration | Max File Size | Formats | Resolution |
|----------|--------------|--------------|---------------|---------|------------|
| Instagram Reels | 9:16 | 90s | 4GB | MP4 | 1080x1920 |
| TikTok | 9:16 | 60s | 287MB | MP4, MOV | 1080x1920 |
| YouTube Shorts | 9:16 | 60s | 256GB | MP4, MOV, WebM | 1080x1920 |
| LinkedIn | 16:9, 1:1 | 10min | 5GB | MP4 | 1920x1080 or 1080x1080 |
| Facebook | 16:9, 1:1 | 240s | 4GB | MP4, MOV | 1920x1080 or 1080x1080 |
| Twitter/X | 16:9 | 140s | 512MB | MP4 | 1920x1080 |

## Technical Implementation

### Backend Structure

```
backend/services/video_studio/
├── social_optimizer_service.py    # Main service
└── platform_specs.py                # Platform specifications
```

**Reuse from Transform Studio:**
- `convert_aspect_ratio()` - For aspect ratio conversion
- `compress_video()` - For file size optimization
- `scale_resolution()` - For resolution scaling (if needed)

**New Functions Needed:**
- `trim_video()` - Trim video to platform duration
- `extract_thumbnail()` - Generate thumbnails from video
- `batch_process()` - Process multiple platforms in parallel

### Frontend Structure

```
frontend/src/components/VideoStudio/modules/SocialVideo/
├── SocialVideo.tsx                  # Main component
├── components/
│   ├── VideoUpload.tsx             # Shared upload
│   ├── PlatformSelector.tsx        # Platform checkboxes
│   ├── OptimizationOptions.tsx     # Options panel
│   ├── PreviewGrid.tsx             # Platform previews
│   └── BatchProgress.tsx           # Progress tracking
└── hooks/
    └── useSocialVideo.ts           # State management
```

## API Endpoint

```
POST /api/video-studio/social/optimize
```

### Request Parameters:

```typescript
{
  file: File,                        // Source video
  platforms: string[],              // ["instagram", "tiktok", "youtube", ...]
  options: {
    auto_crop: boolean,              // Auto-crop to platform ratio
    generate_thumbnails: boolean,    // Generate thumbnails
    add_captions: boolean,           // Add caption overlay (Phase 2)
    compress: boolean,               // Compress for file size limits
    trim_mode: "beginning" | "middle" | "end",  // Where to trim if needed
  }
}
```

### Response:

```typescript
{
  success: boolean,
  results: [
    {
      platform: "instagram",
      video_url: string,
      thumbnail_url: string,
      aspect_ratio: "9:16",
      duration: number,
      file_size: number,
    },
    // ... one per selected platform
  ],
  cost: 0,  // Free (FFmpeg processing)
}
```

## Implementation Phases

### Phase 1: Core Features (Week 1-2)

1. **Platform Specifications**
   - Define platform specs (aspect, duration, file size)
   - Create `platform_specs.py` with all platform data

2. **Backend Service**
   - Create `social_optimizer_service.py`
   - Implement batch processing
   - Reuse Transform Studio processors
   - Add thumbnail extraction

3. **Backend Endpoint**
   - Create `/api/video-studio/social/optimize` endpoint
   - Handle batch processing
   - Return results for all platforms

4. **Frontend UI**
   - Platform selector (checkboxes)
   - Options panel
   - Preview grid
   - Batch progress tracking
   - Download buttons (individual + bulk)

### Phase 2: Advanced Features (Week 3-4)

5. **Caption Overlay**
   - Speech-to-text integration (may need external API)
   - Caption styling per platform
   - Safe zone visualization

6. **Enhanced Thumbnails**
   - Multiple thumbnail options
   - Custom thumbnail selection
   - Thumbnail preview

## Cost

- **Free**: All operations use FFmpeg (no AI cost)
- Processing time depends on video length and number of platforms
- Batch processing is efficient (parallel processing)

## User Experience Flow

1. **Upload Video**: User uploads source video
2. **Select Platforms**: Check platforms to optimize for
3. **Configure Options**: Set cropping, compression, thumbnail options
4. **Preview**: See preview of all platform versions
5. **Optimize**: Click "Optimize for All Platforms"
6. **Progress**: Track progress for each platform
7. **Download**: Download individual or all optimized versions

## Example UI

```
┌─────────────────────────────────────────────────────────┐
│  SOCIAL OPTIMIZER                                       │
├─────────────────────────────────────────────────────────┤
│  Source Video: [video_1080x1920.mp4] (15s)             │
│                                                         │
│  Select Platforms:                                      │
│  ☑ Instagram Reels (9:16, max 90s)                    │
│  ☑ TikTok (9:16, max 60s)                             │
│  ☑ YouTube Shorts (9:16, max 60s)                      │
│  ☑ LinkedIn Video (16:9, max 10min)                   │
│  ☐ Facebook (16:9 or 1:1)                              │
│  ☐ Twitter (16:9, max 2:20)                            │
│                                                         │
│  Optimization Options:                                  │
│  ☑ Auto-crop to platform ratio                        │
│  ☑ Generate thumbnails                                 │
│  ☑ Compress for file size limits                      │
│  ☐ Add captions overlay (Phase 2)                      │
│                                                         │
│  [Optimize for All Platforms]                          │
│                                                         │
│  PREVIEW GRID:                                          │
│  ┌─────────┬─────────┬─────────┬─────────┐           │
│  │ Instagram│ TikTok  │ YouTube │ LinkedIn│           │
│  │  9:16    │  9:16   │  9:16   │  16:9   │           │
│  │ [Video]  │ [Video] │ [Video] │ [Video] │           │
│  │ [Download]│[Download]│[Download]│[Download]│      │
│  └─────────┴─────────┴─────────┴─────────┘           │
│                                                         │
│  [Download All]                                        │
└─────────────────────────────────────────────────────────┘
```

## Benefits

1. **Time Savings**: One video → multiple platform versions in one click
2. **Consistency**: Same content optimized for each platform
3. **Compliance**: Automatic adherence to platform requirements
4. **Efficiency**: Batch processing saves time
5. **Free**: No AI costs, uses FFmpeg

## Next Steps

1. Create platform specifications module
2. Implement social optimizer service (reuse Transform Studio processors)
3. Create backend endpoint
4. Build frontend UI with platform selector and preview grid
5. Add batch processing and progress tracking
