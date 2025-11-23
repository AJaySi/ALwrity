# Content Asset Library Integration Guide

## Overview

The unified Content Asset Library tracks all AI-generated content (text, images, videos, audio) across all ALwrity modules. Similar to the subscription tracking system, it provides a centralized way to manage and organize all generated content.

## Architecture

### Database Models
- `ContentAsset`: Main model for tracking all assets
- `AssetCollection`: Collections/albums for organizing assets

### Service Layer
- `ContentAssetService`: CRUD operations for assets
- `asset_tracker.py`: Helper utility for easy integration

### API Endpoints
- `GET /api/content-assets/`: List assets with filtering
- `POST /api/content-assets/{id}/favorite`: Toggle favorite
- `DELETE /api/content-assets/{id}`: Delete asset
- `POST /api/content-assets/{id}/usage`: Track usage

## Integration Steps

### 1. Story Writer Integration

When story writer generates images, videos, or audio, save them to the asset library:

```python
from utils.asset_tracker import save_asset_to_library

# After generating a story image
asset_id = save_asset_to_library(
    db=db,
    user_id=user_id,
    asset_type="image",
    source_module="story_writer",
    filename=image_filename,
    file_url=image_url,
    file_path=str(image_path),
    file_size=image_path.stat().st_size,
    mime_type="image/png",
    title=f"Scene {scene_number}: {scene_title}",
    description=scene_description,
    prompt=image_prompt,
    tags=["story", "scene", scene_number],
    metadata={
        "scene_number": scene_number,
        "story_id": story_id,
        "provider": image_provider,
    },
    provider=image_provider,
    model=image_model,
    cost=image_cost,
    generation_time=generation_time,
)
```

### 2. Image Studio Integration

When Image Studio generates or edits images:

```python
from utils.asset_tracker import save_asset_to_library

# After generating an image
asset_id = save_asset_to_library(
    db=db,
    user_id=user_id,
    asset_type="image",
    source_module="image_studio",
    filename=result_filename,
    file_url=result_url,
    title=prompt[:100],  # Use prompt as title
    prompt=prompt,
    tags=["image-generation", provider],
    provider=provider,
    model=model,
    cost=cost,
)
```

### 3. Main Text Generation Integration

For text generation modules:

```python
from utils.asset_tracker import save_asset_to_library

# After generating text content
asset_id = save_asset_to_library(
    db=db,
    user_id=user_id,
    asset_type="text",
    source_module="main_text_generation",
    filename=f"generated_{timestamp}.txt",
    file_url=f"/api/text-assets/{filename}",
    title=content_title,
    description=content_summary,
    prompt=generation_prompt,
    tags=["text", "generation"],
    provider=llm_provider,
    model=llm_model,
    cost=api_cost,
)
```

## Frontend Usage

The Asset Library component automatically fetches and displays all assets:

```tsx
import { useContentAssets } from '../../hooks/useContentAssets';

const { assets, loading, error, toggleFavorite, deleteAsset } = useContentAssets({
  asset_type: 'image',
  source_module: 'story_writer',
  search: 'cloud kitchen',
  favorites_only: false,
});
```

## Next Steps

1. **Story Writer**: Add asset tracking to image/video/audio generation endpoints
2. **Image Studio**: Add asset tracking to create/edit/upscale operations
3. **Text Generation**: Add asset tracking to main text generation endpoints
4. **Video Generation**: Add asset tracking when videos are generated
5. **Audio Generation**: Add asset tracking for TTS/audio generation

## Database Migration

Run migration to create the tables:

```bash
# The models are defined in backend/models/content_asset_models.py
# Use Alembic or your migration tool to create the tables
```

## Benefits

- **Unified View**: All generated content in one place
- **Search & Filter**: Find assets by type, source, tags, prompt
- **Cost Tracking**: See generation costs per asset
- **Usage Analytics**: Track downloads, shares, favorites
- **Organization**: Collections and favorites for better organization

