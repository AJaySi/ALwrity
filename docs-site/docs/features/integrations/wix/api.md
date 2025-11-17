# API (Summary)

Short reference of Wix integration endpoints exposed by ALwrity’s backend.

## Authentication
### Get Authorization URL
```http
GET /api/wix/auth/url?state=optional_state
```

### OAuth Callback
```http
POST /api/wix/auth/callback
Content-Type: application/json
{
  "code": "authorization_code",
  "state": "optional_state"
}
```

## Connection
### Status
```http
GET /api/wix/connection/status
```

### Disconnect
```http
POST /api/wix/disconnect
```

## Publishing
### Publish blog post
```http
POST /api/wix/publish
Content-Type: application/json
{
  "title": "Blog Post Title",
  "content": "Markdown",
  "cover_image_url": "https://example.com/image.jpg",
  "category_ids": ["category_id"],
  "tag_ids": ["tag_id_1", "tag_id_2"],
  "publish": true
}
```

## Content Management
### Categories
```http
GET /api/wix/categories
```

### Tags
```http
GET /api/wix/tags
```


