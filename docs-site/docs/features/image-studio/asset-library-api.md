# Content Asset Library API

Advanced API documentation for the Content Asset Library, including powerful search capabilities, bulk operations, and comprehensive asset management.

## Overview

The Content Asset Library API provides comprehensive access to all AI-generated content across ALwrity modules. It offers advanced search syntax, bulk operations, metadata management, and analytics capabilities.

## Authentication

### API Key Authentication

```http
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json
```

### Rate Limiting

- **Free Tier**: 1,000 requests per hour
- **Pro Tier**: 10,000 requests per hour
- **Enterprise Tier**: 100,000 requests per hour

## Base URL

```
https://api.alwrity.com/v1/asset-library
```

## Core Resources

### Asset

Represents any AI-generated content item in the library.

**Properties:**
```json
{
  "id": "asset_123456",
  "type": "image",
  "module": "image_studio",
  "submodule": "create_studio",
  "filename": "ai_generated_image_123456.jpg",
  "title": "Stunning mountain landscape",
  "description": "A beautiful mountain landscape generated with Stable Diffusion",
  "tags": ["mountain", "landscape", "nature", "outdoor"],
  "metadata": {
    "width": 1024,
    "height": 1024,
    "format": "jpg",
    "file_size": 245760,
    "model": "stable-diffusion-xl",
    "prompt": "majestic mountain landscape with lake and forest",
    "negative_prompt": "blurry, low quality",
    "seed": 123456789,
    "steps": 20,
    "guidance_scale": 7.5
  },
  "urls": {
    "original": "https://cdn.alwrity.com/assets/asset_123456.jpg",
    "thumbnail": "https://cdn.alwrity.com/assets/thumbs/asset_123456.jpg",
    "preview": "https://cdn.alwrity.com/assets/preview/asset_123456.jpg"
  },
  "status": "completed",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "user_id": "user_789",
  "cost": {
    "credits_used": 5,
    "currency": "USD",
    "amount": 0.05
  },
  "usage_stats": {
    "downloads": 12,
    "views": 45,
    "shares": 3,
    "favorites": 8
  },
  "collections": ["favorites", "landscapes"],
  "is_favorite": true,
  "is_deleted": false
}
```

## Advanced Search API

### Basic Search

Search assets using simple text queries.

```http
GET /assets/search
```

**Query Parameters:**
- `q`: Search query (supports full-text search)
- `type`: Asset type filter (`image`, `video`, `audio`, `text`)
- `module`: Module filter (`image_studio`, `video_studio`, `story_writer`, etc.)
- `limit`: Number of results (default: 20, max: 100)
- `offset`: Pagination offset
- `sort_by`: Sort field (`created_at`, `updated_at`, `downloads`, `relevance`)
- `sort_order`: Sort order (`asc`, `desc`)

**Example:**
```bash
GET /assets/search?q=mountain+landscape&type=image&limit=10&sort_by=relevance
```

### Advanced Search Syntax

Use powerful search operators for precise queries.

```http
GET /assets/search/advanced
```

**Query Parameters:**
- `query`: Advanced search query string
- `filters`: JSON object with additional filters
- `facets`: Fields to include in facet results

#### Search Operators

**Basic Text Search:**
```
mountain landscape
"exact phrase search"
```

**Field-Specific Search:**
```
title:mountain
description:landscape
tags:nature
module:image_studio
```

**Boolean Operators:**
```
mountain AND landscape
mountain OR forest
(mountain OR hill) AND (lake OR river)
NOT blurry
```

**Wildcard Search:**
```
mount*
land*ape
```

**Range Queries:**
```
created_at:[2024-01-01 TO 2024-01-31]
file_size:[100000 TO 500000]
width:[800 TO 2048]
```

**Boosting:**
```
mountain^2 landscape
```

**Fuzzy Search:**
```
mount~0.8
```

#### Advanced Query Examples

**Complex Image Search:**
```
type:image AND (tags:mountain OR tags:landscape) AND width:[1024 TO 2048] AND created_at:[2024-01-01 TO 2024-01-31] AND model:stable-diffusion*
```

**Video Content Search:**
```
type:video AND module:video_studio AND duration:[30 TO 120] AND tags:(educational OR tutorial)
```

**Multi-Module Search:**
```
(module:image_studio OR module:video_studio) AND (tags:marketing OR tags:brand) AND created_at:[2024-01-15 TO 2024-01-31]
```

**Cost-Based Search:**
```
cost.amount:[0.01 TO 0.10] AND usage_stats.downloads:>5
```

### Faceted Search

Get aggregated results with facet counts for filtering.

```http
GET /assets/search/facets
```

**Query Parameters:**
- `query`: Search query
- `facets`: Comma-separated list of fields to facet on

**Response:**
```json
{
  "results": [...],
  "facets": {
    "type": {
      "image": 145,
      "video": 67,
      "audio": 23,
      "text": 12
    },
    "module": {
      "image_studio": 89,
      "video_studio": 67,
      "story_writer": 45,
      "blog_writer": 23,
      "linkedin_writer": 23
    },
    "tags": {
      "nature": 45,
      "landscape": 32,
      "portrait": 28,
      "marketing": 25,
      "brand": 20
    },
    "model": {
      "stable-diffusion-xl": 67,
      "dalle-3": 45,
      "midjourney": 34,
      "stable-diffusion-1.5": 23
    }
  },
  "total_count": 247
}
```

### Saved Searches

Save and reuse complex search queries.

```http
POST /searches
```

**Request Body:**
```json
{
  "name": "Marketing Images Q1 2024",
  "query": "type:image AND module:image_studio AND tags:marketing AND created_at:[2024-01-01 TO 2024-03-31]",
  "filters": {
    "sort_by": "downloads",
    "sort_order": "desc"
  },
  "description": "High-performing marketing images from Q1"
}
```

```http
GET /searches/{search_id}/execute
```

## Bulk Operations API

### Bulk Asset Retrieval

Retrieve multiple assets by IDs or criteria.

```http
POST /assets/bulk/retrieve
```

**Request Body:**
```json
{
  "asset_ids": ["asset_123", "asset_456", "asset_789"],
  "include_metadata": true,
  "include_urls": true,
  "include_stats": true
}
```

**Response:**
```json
{
  "assets": [
    {
      "id": "asset_123",
      "title": "Mountain Landscape",
      "urls": {...},
      "metadata": {...},
      "usage_stats": {...}
    }
  ],
  "total_found": 3,
  "total_requested": 3
}
```

### Bulk Metadata Update

Update metadata for multiple assets simultaneously.

```http
PATCH /assets/bulk/metadata
```

**Request Body:**
```json
{
  "asset_ids": ["asset_123", "asset_456", "asset_789"],
  "updates": {
    "tags": {
      "add": ["marketing", "q1_2024"],
      "remove": ["draft"]
    },
    "title_prefix": "Marketing - ",
    "description_suffix": " - Generated with ALwrity",
    "collections": {
      "add": ["marketing_campaign_q1"],
      "remove": ["drafts"]
    }
  },
  "options": {
    "create_backup": true,
    "validate_changes": true,
    "notify_on_completion": true
  }
}
```

**Response:**
```json
{
  "operation_id": "bulk_update_123456",
  "status": "processing",
  "assets_updated": 3,
  "assets_total": 3,
  "estimated_completion": "2024-01-15T10:35:00Z"
}
```

### Bulk Download

Download multiple assets as a ZIP archive.

```http
POST /assets/bulk/download
```

**Request Body:**
```json
{
  "asset_ids": ["asset_123", "asset_456", "asset_789"],
  "format": "zip",
  "options": {
    "include_originals": true,
    "include_thumbnails": false,
    "include_metadata": true,
    "metadata_format": "json",
    "organize_by_type": true,
    "compression_level": "normal"
  }
}
```

**Response:**
```json
{
  "download_id": "download_123456",
  "status": "preparing",
  "file_count": 3,
  "total_size_mb": 15.7,
  "estimated_ready_time": "2024-01-15T10:32:00Z",
  "download_url": "https://api.alwrity.com/v1/asset-library/downloads/download_123456"
}
```

### Bulk Delete

Delete multiple assets with confirmation.

```http
DELETE /assets/bulk
```

**Request Body:**
```json
{
  "asset_ids": ["asset_123", "asset_456", "asset_789"],
  "confirmation_required": true,
  "reason": "Cleanup old draft assets",
  "options": {
    "permanent_delete": false,
    "create_backup": true,
    "notify_team": true
  }
}
```

### Bulk Move to Collection

Add multiple assets to collections.

```http
POST /assets/bulk/collections
```

**Request Body:**
```json
{
  "asset_ids": ["asset_123", "asset_456"],
  "collections": {
    "add": ["marketing_q1", "approved_assets"],
    "remove": ["drafts", "review_pending"]
  }
}
```

### Bulk Favorite/Bookmark

Mark multiple assets as favorites.

```http
POST /assets/bulk/favorites
```

**Request Body:**
```json
{
  "asset_ids": ["asset_123", "asset_456"],
  "action": "add", // or "remove"
  "collection": "favorites"
}
```

## Asset Management API

### Get Asset Details

Retrieve comprehensive asset information.

```http
GET /assets/{asset_id}
```

**Query Parameters:**
- `include_metadata`: Include full metadata (default: true)
- `include_stats`: Include usage statistics (default: true)
- `include_urls`: Include all URL variants (default: true)

### Update Asset Metadata

Update individual asset information.

```http
PATCH /assets/{asset_id}
```

**Request Body:**
```json
{
  "title": "Updated Mountain Landscape",
  "description": "A stunning mountain landscape perfect for marketing campaigns",
  "tags": ["mountain", "landscape", "marketing", "brand"],
  "collections": ["marketing_assets", "landscapes"],
  "is_favorite": true
}
```

### Delete Asset

Delete an individual asset.

```http
DELETE /assets/{asset_id}
```

**Query Parameters:**
- `permanent`: Permanently delete (bypass trash) - default: false
- `backup`: Create backup before deletion - default: true

## Collections API

### Create Collection

Create a new asset collection.

```http
POST /collections
```

**Request Body:**
```json
{
  "name": "Marketing Campaign Q1 2024",
  "description": "Assets for Q1 marketing campaigns",
  "type": "campaign", // or "theme", "project", "favorites"
  "is_public": false,
  "tags": ["marketing", "q1", "campaign"],
  "color": "#4A90E2",
  "icon": "campaign"
}
```

### List Collections

Get user's collections with asset counts.

```http
GET /collections
```

**Response:**
```json
{
  "collections": [
    {
      "id": "coll_123",
      "name": "Marketing Q1",
      "description": "Q1 marketing assets",
      "asset_count": 45,
      "type": "campaign",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-15T10:00:00Z"
    }
  ]
}
```

### Add Assets to Collection

```http
POST /collections/{collection_id}/assets
```

**Request Body:**
```json
{
  "asset_ids": ["asset_123", "asset_456"],
  "position": "end" // or "beginning", or specific index
}
```

### Remove Assets from Collection

```http
DELETE /collections/{collection_id}/assets
```

**Request Body:**
```json
{
  "asset_ids": ["asset_123", "asset_456"]
}
```

## Analytics API

### Asset Usage Statistics

Get comprehensive usage analytics for assets.

```http
GET /analytics/assets
```

**Query Parameters:**
- `asset_ids`: Comma-separated asset IDs
- `date_from`: Start date for analytics
- `date_to`: End date for analytics
- `metrics`: Comma-separated metrics (downloads, views, shares, favorites)
- `group_by`: Group results by (day, week, month, asset_type, module)

**Response:**
```json
{
  "summary": {
    "total_assets": 156,
    "total_downloads": 1247,
    "total_views": 5678,
    "total_shares": 234,
    "most_downloaded_asset": "asset_123",
    "most_viewed_asset": "asset_456"
  },
  "trends": [
    {
      "date": "2024-01-15",
      "downloads": 45,
      "views": 123,
      "shares": 8
    }
  ],
  "top_performers": [
    {
      "asset_id": "asset_123",
      "downloads": 89,
      "views": 234,
      "engagement_rate": 0.38
    }
  ]
}
```

### Cost Analytics

Track generation and usage costs.

```http
GET /analytics/costs
```

**Query Parameters:**
- `date_from`: Start date
- `date_to`: End date
- `group_by`: Group by (day, week, month, module, type)
- `currency`: Currency for cost display

**Response:**
```json
{
  "cost_summary": {
    "total_credits_used": 1250,
    "total_cost_usd": 12.50,
    "average_cost_per_asset": 0.08,
    "cost_by_module": {
      "image_studio": 8.75,
      "video_studio": 3.25,
      "story_writer": 0.50
    }
  },
  "cost_trends": [
    {
      "period": "2024-01",
      "credits_used": 450,
      "cost_usd": 4.50,
      "assets_generated": 56
    }
  ]
}
```

## Export API

### Export Search Results

Export search results in various formats.

```http
POST /exports/search
```

**Request Body:**
```json
{
  "query": "type:image AND tags:marketing",
  "format": "csv", // csv, json, xlsx, zip
  "include_metadata": true,
  "include_urls": true,
  "include_stats": false,
  "max_results": 1000
}
```

### Export Collection

Export all assets in a collection.

```http
POST /exports/collections/{collection_id}
```

**Request Body:**
```json
{
  "format": "zip",
  "include_originals": true,
  "include_thumbnails": true,
  "include_metadata": true,
  "organize_by_type": true
}
```

## Webhooks

### Setup Webhooks

Receive real-time notifications for asset operations.

```http
POST /webhooks
```

**Request Body:**
```json
{
  "url": "https://your-app.com/webhooks/assets",
  "events": [
    "asset.created",
    "asset.updated",
    "asset.deleted",
    "bulk_operation.completed",
    "collection.updated"
  ],
  "secret": "your-webhook-secret"
}
```

#### Webhook Events

**Bulk Operation Completed:**
```json
{
  "event": "bulk_operation.completed",
  "operation_id": "bulk_update_123456",
  "operation_type": "metadata_update",
  "status": "success",
  "assets_affected": 25,
  "timestamp": "2024-01-15T10:35:00Z",
  "details": {
    "updates_applied": {
      "tags_added": ["marketing"],
      "collections_added": ["q1_campaign"]
    }
  }
}
```

**Asset Created:**
```json
{
  "event": "asset.created",
  "asset_id": "asset_123456",
  "asset_type": "image",
  "module": "image_studio",
  "user_id": "user_789",
  "timestamp": "2024-01-15T10:30:00Z",
  "metadata": {
    "title": "New Marketing Image",
    "tags": ["marketing", "brand"],
    "cost": {"credits_used": 5}
  }
}
```

## Advanced Features

### Smart Recommendations

Get AI-powered asset recommendations.

```http
GET /assets/recommendations
```

**Query Parameters:**
- `based_on`: Asset ID to base recommendations on
- `type`: Type of recommendation (similar, complementary, trending)
- `limit`: Number of recommendations

**Response:**
```json
{
  "recommendations": [
    {
      "asset_id": "asset_456",
      "similarity_score": 0.87,
      "reason": "Similar style and composition",
      "type": "similar"
    },
    {
      "asset_id": "asset_789",
      "complementary_score": 0.92,
      "reason": "Complements your color scheme",
      "type": "complementary"
    }
  ]
}
```

### Duplicate Detection

Find duplicate or similar assets.

```http
POST /assets/duplicates/find
```

**Request Body:**
```json
{
  "asset_ids": ["asset_123", "asset_456"],
  "similarity_threshold": 0.85,
  "check_all": false
}
```

**Response:**
```json
{
  "duplicates": [
    {
      "asset_id": "asset_123",
      "duplicate_of": "asset_456",
      "similarity_score": 0.91,
      "reason": "Identical prompt and parameters"
    }
  ]
}
```

### Batch Processing Status

Monitor long-running bulk operations.

```http
GET /operations/{operation_id}
```

**Response:**
```json
{
  "operation_id": "bulk_download_123456",
  "type": "bulk_download",
  "status": "completed",
  "progress": {
    "completed": 25,
    "total": 25,
    "percentage": 100
  },
  "result": {
    "download_url": "https://cdn.alwrity.com/downloads/bulk_123456.zip",
    "file_count": 25,
    "total_size_mb": 45.2,
    "expires_at": "2024-01-16T10:00:00Z"
  },
  "created_at": "2024-01-15T10:30:00Z",
  "completed_at": "2024-01-15T10:32:00Z"
}
```

## Error Handling

### Error Response Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid asset ID format",
    "details": {
      "field": "asset_ids",
      "provided": "invalid_id",
      "expected_format": "asset_[0-9]+"
    },
    "request_id": "req_1234567890",
    "timestamp": "2024-01-15T10:00:00Z"
  }
}
```

### Common Error Codes

| Error Code | HTTP Status | Description |
|------------|-------------|-------------|
| `VALIDATION_ERROR` | 400 | Invalid request parameters |
| `ASSET_NOT_FOUND` | 404 | Asset not found |
| `BULK_OPERATION_FAILED` | 500 | Bulk operation failed |
| `STORAGE_LIMIT_EXCEEDED` | 402 | Storage limit exceeded |
| `RATE_LIMIT_EXCEEDED` | 429 | API rate limit exceeded |

## SDK Examples

### JavaScript/Node.js

```javascript
const AlwrityAssetLibrary = require('alwrity-asset-library-sdk');

const client = new AlwrityAssetLibrary({
  apiKey: 'your-api-key'
});

// Advanced search with filters
const results = await client.search.advanced({
  query: 'type:image AND tags:marketing AND created_at:[2024-01-01 TO 2024-01-31]',
  filters: {
    sort_by: 'downloads',
    sort_order: 'desc'
  },
  limit: 50
});

// Bulk metadata update
const updateResult = await client.assets.bulkUpdateMetadata({
  asset_ids: ['asset_123', 'asset_456'],
  updates: {
    tags: { add: ['q1_campaign'] },
    collections: { add: ['marketing'] }
  }
});
```

### Python

```python
from alwrity_asset_library import AssetLibraryClient

client = AssetLibraryClient(api_key='your-api-key')

# Search with facets
search_results = client.search.with_facets(
    query="type:image AND module:image_studio",
    facets=["tags", "model", "created_at"]
)

# Bulk download
download = client.assets.bulk_download(
    asset_ids=['asset_123', 'asset_456', 'asset_789'],
    format='zip',
    include_metadata=True
)

print(f"Download ready: {download.download_url}")
```

## Best Practices

### Search Optimization

1. **Use Specific Queries**: Combine multiple filters for precise results
2. **Leverage Facets**: Use faceted search for better filtering
3. **Save Searches**: Save frequently used complex queries
4. **Use Wildcards**: For partial matches and variations

### Bulk Operations

1. **Batch Size**: Limit bulk operations to 100 items for optimal performance
2. **Monitor Progress**: Use operation IDs to track long-running tasks
3. **Error Handling**: Implement proper error handling for failed operations
4. **Validation**: Validate asset IDs before bulk operations

### Performance

1. **Pagination**: Use pagination for large result sets
2. **Caching**: Cache frequently accessed assets and metadata
3. **Async Operations**: Use webhooks for real-time updates
4. **Rate Limiting**: Respect API rate limits and implement backoff

### Organization

1. **Consistent Tagging**: Use consistent tag naming conventions
2. **Regular Cleanup**: Regularly review and clean up unused assets
3. **Collections**: Organize assets into logical collections
4. **Metadata**: Keep metadata updated and accurate

---

[:octicons-arrow-right-24: Back to Asset Library](asset-library.md)
[:octicons-arrow-right-24: Image Studio Overview](../overview.md)