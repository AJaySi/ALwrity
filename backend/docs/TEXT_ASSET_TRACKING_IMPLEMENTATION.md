# Text Asset Tracking Implementation

## Overview

Text content tracking has been successfully implemented across LinkedIn Writer and Facebook Writer endpoints. All generated text content is automatically saved as files and tracked in the unified Content Asset Library.

## Implementation Status

### ✅ Completed Integrations

#### 1. LinkedIn Writer (`backend/routers/linkedin.py`)
- **Post Generation**: Tracks LinkedIn posts with content, hashtags, and CTAs
- **Article Generation**: Tracks LinkedIn articles with full content, sections, and SEO metadata
- **Carousel Generation**: Tracks LinkedIn carousels with all slides
- **Video Script Generation**: Tracks LinkedIn video scripts with hooks, scenes, captions
- **Comment Response Generation**: Tracks LinkedIn comment responses

**File Format**: Markdown (`.md`) for articles, carousels, video scripts, comment responses; Text (`.txt`) for posts

**Storage Location**: `backend/linkedinwriter_text/{subdirectory}/`
- `posts/` - LinkedIn posts
- `articles/` - LinkedIn articles  
- `carousels/` - LinkedIn carousels
- `video_scripts/` - LinkedIn video scripts
- `comment_responses/` - LinkedIn comment responses

#### 2. Facebook Writer (`backend/api/facebook_writer/routers/facebook_router.py`)
- **Post Generation**: Tracks Facebook posts with content and analytics
- **Story Generation**: Tracks Facebook stories

**File Format**: Text (`.txt`)

**Storage Location**: `backend/facebookwriter_text/{subdirectory}/`
- `posts/` - Facebook posts
- `stories/` - Facebook stories

### 📝 Pending Integrations

#### Facebook Writer (Additional Endpoints)
- Reel Generation
- Carousel Generation
- Event Generation
- Group Post Generation
- Page About Generation
- Ad Copy Generation
- Hashtag Generation

#### Blog Writer (`backend/api/blog_writer/router.py`)
- Blog content generation endpoints
- Medium blog generation
- Blog section generation

## Architecture

### Core Components

1. **Text Asset Tracker** (`backend/utils/text_asset_tracker.py`)
   - `save_and_track_text_content()`: Main function for saving and tracking text
   - Handles file saving, URL generation, and asset library tracking
   - Non-blocking error handling

2. **File Storage Utilities** (`backend/utils/file_storage.py`)
   - `save_text_file_safely()`: Safely saves text files with validation
   - `sanitize_filename()`: Prevents path traversal
   - `generate_unique_filename()`: Creates unique filenames

3. **Asset Tracker** (`backend/utils/asset_tracker.py`)
   - `save_asset_to_library()`: Saves asset metadata to database

## Integration Pattern

### Basic Integration

```python
from utils.text_asset_tracker import save_and_track_text_content
from sqlalchemy.orm import Session
from middleware.auth_middleware import get_current_user

@router.post("/generate-content")
async def generate_content(
    request: ContentRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Generate content
    response = await service.generate(request)
    
    # Save and track text content (non-blocking)
    if response.content:
        try:
            user_id = str(current_user.get('id', '') or current_user.get('sub', ''))
            
            if user_id:
                save_and_track_text_content(
                    db=db,
                    user_id=user_id,
                    content=response.content,
                    source_module="module_name",
                    title=f"Content Title: {request.topic[:60]}",
                    description=f"Content description",
                    prompt=f"Topic: {request.topic}",
                    tags=["tag1", "tag2"],
                    metadata={"key": "value"},
                    subdirectory="content_type"
                )
        except Exception as track_error:
            logger.warning(f"Failed to track text asset: {track_error}")
    
    return response
```

## File Serving

Text files are saved with URLs like `/api/text-assets/{module}/{subdirectory}/{filename}`. A serving endpoint should be created in `backend/app.py`:

```python
@router.get("/api/text-assets/{file_path:path}")
async def serve_text_asset(
    file_path: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Serve text assets with authentication."""
    # Implementation needed
    pass
```

## Best Practices

1. **Non-blocking**: Text tracking failures should never break the main request
2. **Error Handling**: Use try/except around tracking calls
3. **User ID Extraction**: Support both `current_user` dependency and header-based extraction
4. **Content Formatting**: Combine related content (e.g., post + hashtags + CTA)
5. **Metadata**: Include rich metadata for search and filtering
6. **File Organization**: Use subdirectories to organize by content type

## Next Steps

1. Add text tracking to remaining Facebook Writer endpoints
2. Add text tracking to Blog Writer endpoints
3. Create text asset serving endpoint
4. Add text preview in Asset Library UI
5. Support text file downloads

