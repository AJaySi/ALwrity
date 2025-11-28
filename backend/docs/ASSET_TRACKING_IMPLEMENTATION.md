# Asset Tracking Implementation Guide

## Overview

This document describes the production-ready implementation of asset tracking across all ALwrity modules. The unified Content Asset Library automatically tracks all AI-generated content (images, videos, audio, text) for easy management and organization.

## Architecture

### Core Components

1. **Database Models** (`backend/models/content_asset_models.py`)
   - `ContentAsset`: Main model for tracking assets
   - `AssetCollection`: Collections/albums for organizing assets
   - `AssetType`: Enum (text, image, video, audio)
   - `AssetSource`: Enum (all ALwrity modules)

2. **Service Layer** (`backend/services/content_asset_service.py`)
   - CRUD operations for assets
   - Search, filter, pagination
   - Usage tracking

3. **Utility Functions**
   - `backend/utils/asset_tracker.py`: `save_asset_to_library()` helper
   - `backend/utils/file_storage.py`: Robust file saving utilities

## Implementation Status

### ✅ Completed Integrations

#### 1. Story Writer (`backend/api/story_writer/router.py`)
- **Images**: Tracks all scene images with metadata
- **Audio**: Tracks all scene audio files with narration details
- **Videos**: Tracks individual scene videos and complete story videos
- **Location**: After generation in `/generate-images`, `/generate-audio`, `/generate-video`, `/generate-complete-video`
- **Metadata**: Includes prompts, scene numbers, providers, models, costs, status

#### 2. Image Studio (`backend/api/images.py`)
- **Image Generation**: Tracks all generated images
- **Image Editing**: Tracks all edited images
- **Location**: After generation in `/api/images/generate` and `/api/images/edit`
- **Features**:
  - Robust file saving with validation
  - Atomic file writes
  - Proper error handling (non-blocking)
  - File serving endpoint at `/api/images/image-studio/images/{filename}`

### 📝 Notes on Other Modules

#### Main Generation Services
- **Text Generation** (`main_text_generation.py`): Returns strings, not files. If text content needs tracking, save to `.txt` or `.md` files first.
- **Video Generation** (`main_video_generation.py`): Already integrated via Story Writer
- **Audio Generation** (`main_audio_generation.py`): Already integrated via Story Writer

#### Social Writers
- **LinkedIn Writer**: Generates text content (posts, articles). No file generation currently.
- **Facebook Writer**: Generates text content (posts, stories, reels). No file generation currently.
- **Blog Writer**: Generates blog content. May generate images in future.

**Note**: If these modules generate files in the future, follow the integration pattern below.

## Integration Pattern

### For Image Generation

```python
from utils.asset_tracker import save_asset_to_library
from utils.file_storage import save_file_safely, generate_unique_filename
from sqlalchemy.orm import Session
from pathlib import Path

# After successful image generation
try:
    base_dir = Path(__file__).parent.parent
    output_dir = base_dir / "module_images"
    
    image_filename = generate_unique_filename(
        prefix="img_prompt",
        extension=".png",
        include_uuid=True
    )
    
    # Save file safely
    image_path, save_error = save_file_safely(
        content=result.image_bytes,
        directory=output_dir,
        filename=image_filename,
        max_file_size=50 * 1024 * 1024  # 50MB
    )
    
    if image_path and not save_error:
        image_url = f"/api/module/images/{image_path.name}"
        
        # Track in asset library (non-blocking)
        try:
            asset_id = save_asset_to_library(
                db=db,
                user_id=user_id,
                asset_type="image",
                source_module="module_name",
                filename=image_path.name,
                file_url=image_url,
                file_path=str(image_path),
                file_size=len(result.image_bytes),
                mime_type="image/png",
                title="Image Title",
                description="Image description",
                prompt=prompt,
                tags=["tag1", "tag2"],
                provider=result.provider,
                model=result.model,
                metadata={"status": "completed"}
            )
            logger.info(f"✅ Asset saved: ID={asset_id}")
        except Exception as e:
            logger.error(f"Asset tracking failed: {e}", exc_info=True)
            # Don't fail the request
except Exception as e:
    logger.error(f"File save failed: {e}", exc_info=True)
    # Continue - base64 is still available
```

### For Video Generation

```python
# After successful video generation
try:
    asset_id = save_asset_to_library(
        db=db,
        user_id=user_id,
        asset_type="video",
        source_module="module_name",
        filename=video_filename,
        file_url=video_url,
        file_path=str(video_path),
        file_size=file_size,
        mime_type="video/mp4",
        title="Video Title",
        description="Video description",
        prompt=prompt,
        tags=["video", "tag"],
        provider=provider,
        model=model,
        cost=cost,
        metadata={"duration": duration, "status": "completed"}
    )
except Exception as e:
    logger.error(f"Asset tracking failed: {e}", exc_info=True)
```

### For Audio Generation

```python
# After successful audio generation
try:
    asset_id = save_asset_to_library(
        db=db,
        user_id=user_id,
        asset_type="audio",
        source_module="module_name",
        filename=audio_filename,
        file_url=audio_url,
        file_path=str(audio_path),
        file_size=file_size,
        mime_type="audio/mpeg",
        title="Audio Title",
        description="Audio description",
        prompt=text,
        tags=["audio", "tag"],
        provider=provider,
        model=model,
        cost=cost,
        metadata={"status": "completed"}
    )
except Exception as e:
    logger.error(f"Asset tracking failed: {e}", exc_info=True)
```

## Best Practices

### 1. Error Handling
- **Always non-blocking**: Asset tracking failures should never break the main request
- **Log errors**: Use `logger.error()` with `exc_info=True` for debugging
- **Graceful degradation**: Continue with base64/file response even if tracking fails

### 2. File Management
- **Use `save_file_safely()`**: Handles validation, atomic writes, directory creation
- **Sanitize filenames**: Use `sanitize_filename()` to prevent path traversal
- **Unique filenames**: Use `generate_unique_filename()` with UUIDs
- **File size limits**: Enforce reasonable limits (50MB for images, 100MB for videos)

### 3. Database Sessions
- **Pass session explicitly**: Use `db: Session = Depends(get_db)` in endpoints
- **Handle session lifecycle**: Let FastAPI manage session cleanup
- **Background tasks**: Get new session in background tasks

### 4. Metadata
- **Rich metadata**: Include provider, model, dimensions, cost, status
- **Searchable tags**: Use consistent tag naming (e.g., "image_studio", "generated")
- **Status tracking**: Always include `"status": "completed"` in metadata

### 5. File URLs
- **Consistent patterns**: Use `/api/{module}/images/{filename}` format
- **Serving endpoints**: Create corresponding GET endpoints to serve files
- **Authentication**: Protect file serving endpoints with `get_current_user`

## File Storage Utilities

### `save_file_safely()`
- Validates file size
- Creates directories automatically
- Atomic writes (temp file + rename)
- Returns `(file_path, error_message)` tuple

### `sanitize_filename()`
- Removes dangerous characters
- Prevents path traversal
- Limits filename length
- Handles empty filenames

### `generate_unique_filename()`
- Creates unique filenames with UUIDs
- Sanitizes prefix
- Handles extensions properly

## Testing Checklist

- [ ] Images are saved to disk correctly
- [ ] Files are accessible via serving endpoints
- [ ] Asset tracking works (check database)
- [ ] Errors don't break main requests
- [ ] File size limits are enforced
- [ ] Filenames are sanitized properly
- [ ] Metadata is complete and accurate
- [ ] Asset Library UI displays assets correctly

## Future Enhancements

1. **Text Content Tracking**: Save text content as files when needed
2. **Batch Operations**: Track multiple assets in single transaction
3. **File Cleanup**: Automatic cleanup of orphaned files
4. **Storage Backends**: Support S3, GCS for production
5. **Thumbnail Generation**: Auto-generate thumbnails for videos/images
6. **Compression**: Compress large files before storage

## Troubleshooting

### Assets not appearing in library
1. Check database: `SELECT * FROM content_assets WHERE user_id = '...'`
2. Check logs for asset tracking errors
3. Verify `save_asset_to_library()` returns asset ID
4. Check file URLs are correct

### File serving fails
1. Verify file exists on disk
2. Check serving endpoint is registered
3. Verify authentication is working
4. Check file permissions

### Performance issues
1. Use background tasks for heavy operations
2. Batch database operations
3. Consider async file I/O for large files
4. Monitor database query performance

