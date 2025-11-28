# Image Studio Modules

Image Studio consists of 7 core modules that provide a complete image workflow from creation to optimization. This guide provides detailed information about each module, their features, and current implementation status.

## Module Overview

| Module | Status | Route | Description |
|--------|-------|-------|-------------|
| **Create Studio** | ✅ Live | `/image-generator` | Generate images from text prompts |
| **Edit Studio** | ✅ Live | `/image-editor` | AI-powered image editing |
| **Upscale Studio** | ✅ Live | `/image-upscale` | Enhance image resolution |
| **Social Optimizer** | ✅ Live | `/image-studio/social-optimizer` | Optimize for social platforms |
| **Asset Library** | ✅ Live | `/image-studio/asset-library` | Unified content archive |
| **Transform Studio** | 🚧 Planned | - | Convert images to videos/avatars |
| **Control Studio** | 🚧 Planned | - | Advanced generation controls |

---

## 1. Create Studio ✅

**Status**: Fully implemented and live  
**Route**: `/image-generator`

### Overview
Create Studio enables you to generate high-quality images from text prompts using multiple AI providers. It includes platform templates, style presets, and batch generation capabilities.

### Key Features

#### Multi-Provider Support
- **Stability AI**: Ultra (highest quality), Core (fast & affordable), SD3.5 (advanced)
- **WaveSpeed Ideogram V3**: Photorealistic images with superior text rendering
- **WaveSpeed Qwen**: Ultra-fast generation (2-3 seconds)
- **HuggingFace**: FLUX models for diverse styles
- **Gemini**: Google's Imagen models

#### Platform Templates
- **Instagram**: Feed posts (square, portrait), Stories, Reels
- **LinkedIn**: Post images, article covers, company banners
- **Facebook**: Feed posts, Stories, cover photos
- **Twitter/X**: Post images, header images
- **YouTube**: Thumbnails, channel art
- **Pinterest**: Pins, board covers
- **TikTok**: Video thumbnails
- **Blog**: Featured images, article headers
- **Email**: Newsletter headers, promotional images
- **Website**: Hero images, section backgrounds

#### Style Presets
40+ built-in styles including:
- Photographic
- Digital Art
- 3D Model
- Anime
- Cinematic
- Oil Painting
- Watercolor
- And many more...

#### Advanced Features
- **Batch Generation**: Create 1-10 variations in one request
- **Prompt Enhancement**: AI-powered prompt improvement
- **Cost Estimation**: See costs before generating
- **Quality Levels**: Draft, Standard, Premium
- **Advanced Controls**: Guidance scale, steps, seed for fine-tuning
- **Persona Support**: Generate content aligned with brand personas

### Use Cases
- Social media campaign visuals
- Blog post featured images
- Product photography
- Marketing materials
- Brand assets
- Content library building

### Backend Components
- `CreateStudioService`: Generation logic
- `ImageStudioManager`: Orchestration
- Template system with platform specifications

### Frontend Components
- `CreateStudio.tsx`: Main interface
- `TemplateSelector.tsx`: Template selection
- `ImageResultsGallery.tsx`: Results display
- `CostEstimator.tsx`: Cost calculation

---

## 2. Edit Studio ✅

**Status**: Fully implemented and live  
**Route**: `/image-editor`

### Overview
Edit Studio provides AI-powered image editing capabilities including background operations, object manipulation, and conversational editing.

### Available Operations

#### Background Operations
- **Remove Background**: Extract subjects with transparent backgrounds
- **Replace Background**: Change backgrounds with proper lighting
- **Relight**: Adjust lighting to match new backgrounds

#### Object Manipulation
- **Erase**: Remove unwanted objects from images
- **Inpaint**: Fill or replace specific areas with AI
- **Outpaint**: Expand images beyond original boundaries
- **Search & Replace**: Replace objects using text prompts
- **Search & Recolor**: Change colors using text prompts

#### General Editing
- **General Edit**: Prompt-based editing with optional mask support
- **Mask Editor**: Visual mask creation for precise control

### Key Features
- **Reusable Mask Editor**: Create and reuse masks across operations
- **Optional Masking**: Use masks for `general_edit`, `search_replace`, `search_recolor`
- **Multiple Input Support**: Base image, mask, background, and lighting references
- **Real-time Preview**: See results before applying
- **Operation-Specific Fields**: Dynamic UI based on selected operation

### Use Cases
- Remove unwanted objects
- Change backgrounds
- Fix imperfections
- Add or modify elements
- Adjust colors
- Extend image canvas

### Backend Components
- `EditStudioService`: Editing logic
- Stability AI integration
- HuggingFace integration

### Frontend Components
- `EditStudio.tsx`: Main interface
- `ImageMaskEditor.tsx`: Mask creation tool
- `EditImageUploader.tsx`: Image upload interface
- `EditOperationsToolbar.tsx`: Operation selection

---

## 3. Upscale Studio ✅

**Status**: Fully implemented and live  
**Route**: `/image-upscale`

### Overview
Upscale Studio enhances image resolution using AI-powered upscaling with multiple modes and quality presets.

### Upscaling Modes

#### Fast Upscale
- **Speed**: ~1 second
- **Quality**: 4x upscaling
- **Use Case**: Quick previews, web display
- **Cost**: 2 credits

#### Conservative Upscale
- **Quality**: 4K resolution
- **Style**: Preserves original style
- **Use Case**: Professional printing, high-quality display
- **Cost**: 6 credits
- **Optional Prompt**: Guide the upscaling process

#### Creative Upscale
- **Quality**: 4K resolution
- **Style**: Enhances and improves style
- **Use Case**: Artistic enhancement, style improvement
- **Cost**: 6 credits
- **Optional Prompt**: Guide creative enhancements

### Key Features
- **Quality Presets**: Web, print, social media optimizations
- **Side-by-Side Comparison**: Before/after preview with synchronized zoom
- **Prompt Support**: Optional prompts for conservative/creative modes
- **Real-time Preview**: See results immediately
- **Metadata Display**: View upscaling details

### Use Cases
- Enhance low-resolution images
- Prepare images for printing
- Improve image quality for display
- Upscale product photos
- Enhance social media images

### Backend Components
- `UpscaleStudioService`: Upscaling logic
- Stability AI upscaling endpoints

### Frontend Components
- `UpscaleStudio.tsx`: Main interface
- Comparison viewer with zoom

---

## 4. Social Optimizer ✅

**Status**: Fully implemented and live  
**Route**: `/image-studio/social-optimizer`

### Overview
Social Optimizer automatically resizes and optimizes images for all major social media platforms with smart cropping and safe zone visualization.

### Supported Platforms
- **Instagram**: Feed posts (square, portrait), Stories, Reels
- **Facebook**: Feed posts, Stories, cover photos
- **Twitter/X**: Post images, header images
- **LinkedIn**: Post images, article covers, company banners
- **YouTube**: Thumbnails, channel art
- **Pinterest**: Pins, board covers
- **TikTok**: Video thumbnails

### Key Features

#### Platform Formats
- **Multiple Formats per Platform**: Choose from various format options
- **Automatic Sizing**: Platform-specific dimensions
- **Format Selection**: Pick the best format for your content

#### Crop Modes
- **Smart Crop**: Preserve important content with intelligent cropping
- **Center Crop**: Crop from center
- **Fit**: Fit with padding

#### Safe Zones
- **Visual Overlays**: Display text-safe areas
- **Platform-Specific**: Safe zones tailored to each platform
- **Toggle Display**: Show/hide safe zones

#### Batch Export
- **Multi-Platform**: Generate optimized versions for multiple platforms
- **Single Source**: One image → all platforms
- **Individual Downloads**: Download specific formats
- **Bulk Download**: Download all optimized images at once

### Use Cases
- Social media campaigns
- Multi-platform content distribution
- Brand consistency across platforms
- Time-saving batch optimization

### Backend Components
- `SocialOptimizerService`: Optimization logic
- Platform format specifications
- Image processing and resizing

### Frontend Components
- `SocialOptimizer.tsx`: Main interface
- Platform selector
- Format selection
- Results grid

---

## 5. Asset Library ✅

**Status**: Fully implemented and live  
**Route**: `/image-studio/asset-library`

### Overview
Asset Library is a unified content archive that tracks all AI-generated content (images, videos, audio, text) across all ALwrity modules.

### Key Features

#### Search & Filtering
- **Advanced Search**: Search by ID, model, keywords
- **Type Filtering**: Filter by image, video, audio, text
- **Module Filtering**: Filter by source module (Image Studio, Story Writer, Blog Writer, etc.)
- **Status Filtering**: Filter by completion status
- **Date Filtering**: Filter by creation date
- **Favorites Filter**: Show only favorited assets

#### Organization
- **Favorites**: Mark and organize favorite assets
- **Collections**: Organize assets into collections (coming soon)
- **Tags**: AI-powered tagging (coming soon)
- **Version History**: Track asset versions (coming soon)

#### Views
- **Grid View**: Visual card-based layout
- **List View**: Detailed table layout with all metadata
- **Toggle Views**: Switch between grid and list views

#### Bulk Operations
- **Bulk Download**: Download multiple assets at once
- **Bulk Delete**: Delete multiple assets
- **Bulk Share**: Share multiple assets (coming soon)

#### Usage Tracking
- **Download Count**: Track asset downloads
- **Share Count**: Track asset shares
- **Usage Analytics**: Monitor asset performance

#### Asset Information
- **Metadata Display**: View provider, model, cost, generation time
- **Status Indicators**: Visual status chips (completed, processing, failed)
- **Source Module**: Identify which ALwrity tool created the asset
- **Creation Date**: Timestamp of asset creation

### Integration
Assets are automatically tracked from:
- **Image Studio**: All generated and edited images
- **Story Writer**: Scene images, audio, videos
- **Blog Writer**: Generated images
- **LinkedIn Writer**: Generated content
- **Other Modules**: All ALwrity tools

### Use Cases
- Organize campaign assets
- Find previously generated content
- Track content usage
- Manage brand assets
- Archive content library

### Backend Components
- `ContentAssetService`: Asset management
- Database models for asset storage
- Search and filtering logic

### Frontend Components
- `AssetLibrary.tsx`: Main interface
- Search and filter controls
- Grid and list views
- Bulk operation tools

---

## 6. Transform Studio 🚧

**Status**: Planned for future release

### Overview
Transform Studio will enable conversion of images into videos, creation of talking avatars, and generation of 3D models.

### Planned Features

#### Image-to-Video
- **WaveSpeed WAN 2.5**: Convert static images to dynamic videos
- **Resolutions**: 480p, 720p, 1080p
- **Duration**: Up to 10 seconds
- **Audio Support**: Add audio/voiceover
- **Social Optimization**: Optimize for social platforms

#### Make Avatar
- **Hunyuan Avatar**: Create talking avatars from photos
- **Audio-Driven**: Lip-sync with audio input
- **Duration**: Up to 2 minutes
- **Emotion Control**: Adjust avatar expressions
- **Resolutions**: 480p, 720p

#### Image-to-3D
- **Stable Fast 3D**: Generate 3D models from images
- **Export Formats**: Standard 3D formats
- **Quality Options**: Multiple quality levels

### Use Cases
- Product showcases
- Social media videos
- Explainer videos
- Personal branding
- Marketing campaigns

---

## 7. Control Studio 🚧

**Status**: Planned for future release

### Overview
Control Studio will provide advanced generation controls for fine-grained image creation.

### Planned Features

#### Sketch-to-Image
- **Control Strength**: Adjust how closely the image follows the sketch
- **Style Transfer**: Apply styles to sketches
- **Multiple Sketches**: Combine multiple control inputs

#### Style Transfer
- **Style Library**: Pre-built style library
- **Custom Styles**: Upload custom style images
- **Strength Control**: Adjust style application intensity

#### Structure Control
- **Pose Control**: Control human poses
- **Depth Control**: Control depth information
- **Edge Control**: Control edge detection

### Use Cases
- Precise image generation
- Style consistency
- Brand-aligned visuals
- Advanced creative control

---

## Module Dependencies

### Infrastructure
- **ImageStudioManager**: Orchestrates all modules
- **Shared UI Components**: Consistent interface across modules
- **Cost Estimation**: Unified cost calculation
- **Authentication**: User validation for all operations

### Data Flow
1. User selects module
2. Module-specific UI loads
3. User provides input (prompt, image, settings)
4. Pre-flight validation (cost, subscription)
5. Operation executes
6. Results displayed
7. Asset saved to Asset Library (if applicable)

---

## Module Status Summary

### ✅ Implemented (5/7)
- Create Studio
- Edit Studio
- Upscale Studio
- Social Optimizer
- Asset Library

### 🚧 Planned (2/7)
- Transform Studio
- Control Studio

---

*For detailed guides on each module, see the module-specific documentation: [Create Studio](create-studio.md), [Edit Studio](edit-studio.md), [Upscale Studio](upscale-studio.md), [Social Optimizer](social-optimizer.md), [Asset Library](asset-library.md).*

