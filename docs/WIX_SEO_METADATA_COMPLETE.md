# Complete Wix SEO Metadata Implementation

## 📊 SEO Metadata Generated vs Posted

### ✅ FULLY POSTED TO WIX

#### 1. **SEO Keywords** (in `seoData.settings.keywords`)
- ✅ `focus_keyword` → Main keyword (`isMain: true`)
- ✅ `blog_tags` → Additional keywords (`isMain: false`)
- ✅ `social_hashtags` → Additional keywords (`isMain: false`)

#### 2. **Meta Tags** (in `seoData.tags`)
- ✅ `meta_description` → `<meta name="description">`
- ✅ `seo_title` → `<meta name="title">`

#### 3. **Open Graph Tags** (in `seoData.tags`)
- ✅ `open_graph.title` → `og:title`
- ✅ `open_graph.description` → `og:description`
- ✅ `open_graph.image` → `og:image` (HTTP/HTTPS URLs only)
- ✅ `og:type` → Always set to `article`
- ✅ `open_graph.url` or `canonical_url` → `og:url`

#### 4. **Twitter Card Tags** (in `seoData.tags`)
- ✅ `twitter_card.title` → `twitter:title`
- ✅ `twitter_card.description` → `twitter:description`
- ✅ `twitter_card.image` → `twitter:image` (HTTP/HTTPS URLs only)
- ✅ `twitter_card.card` → `twitter:card` (default: `summary_large_image`)

#### 5. **Canonical URL** (in `seoData.tags`)
- ✅ `canonical_url` → `<link rel="canonical">`

#### 6. **Blog Categories** (in `draftPost.categoryIds`)
- ✅ `blog_categories` → Lookup/create categories → `categoryIds` (UUIDs)
- **Implementation**: `lookup_or_create_categories()` method
- **Behavior**: Case-insensitive lookup, auto-create if missing

#### 7. **Blog Tags** (in `draftPost.tagIds`)
- ✅ `blog_tags` → Lookup/create tags → `tagIds` (UUIDs)
- **Implementation**: `lookup_or_create_tags()` method
- **Behavior**: Case-insensitive lookup, auto-create if missing
- **Note**: `blog_tags` are also used in SEO keywords, but separately as post tags

### ❌ NOT POSTED (Optional/Future)

1. **JSON-LD Structured Data** (`json_ld_schema`)
   - **Reason**: Wix doesn't support JSON-LD in backend API
   - **Solution**: Would require frontend implementation using `@wix/site-seo` package
   - **Status**: Not implemented (would need to be added to Wix site code)

2. **URL Slug** (`url_slug`)
   - **Reason**: Wix auto-generates URLs from title
   - **Status**: Could be implemented if Wix API supports custom slugs

3. **Reading Time** (`reading_time`)
   - **Reason**: Metadata only, not part of Wix blog post structure
   - **Status**: Not applicable

4. **Optimization Score** (`optimization_score`)
   - **Reason**: Internal metadata for ALwrity, not Wix field
   - **Status**: Not applicable

## 🔄 Conversion Methods

### Markdown to Ricos Conversion

**Primary Method**: Wix Official Ricos Documents API
- **Endpoint**: Tries multiple paths to find correct endpoint
- **Benefits**: Official conversion, handles all edge cases
- **Fallback**: Custom parser if API unavailable

**Fallback Method**: Custom Markdown Parser
- **Location**: `backend/services/integrations/wix/content.py`
- **Supports**: Headings, paragraphs, lists, bold, italic, links, images, blockquotes

## 📋 Complete Post Structure

When publishing to Wix, the blog post includes:

```json
{
  "draftPost": {
    "title": "SEO optimized title",
    "memberId": "author-member-id",
    "richContent": { /* Ricos JSON document */ },
    "excerpt": "First 200 chars of content",
    "categoryIds": ["uuid1", "uuid2"],  // From blog_categories
    "tagIds": ["uuid1", "uuid2"],        // From blog_tags
    "media": { /* Cover image if provided */ },
    "seoData": {
      "settings": {
        "keywords": [
          { "term": "main keyword", "isMain": true },
          { "term": "tag1", "isMain": false },
          { "term": "tag2", "isMain": false }
        ]
      },
      "tags": [
        { "type": "meta", "props": { "name": "description", "content": "..." } },
        { "type": "meta", "props": { "name": "title", "content": "..." } },
        { "type": "meta", "props": { "property": "og:title", "content": "..." } },
        { "type": "meta", "props": { "property": "og:description", "content": "..." } },
        { "type": "meta", "props": { "property": "og:image", "content": "..." } },
        { "type": "meta", "props": { "property": "og:type", "content": "article" } },
        { "type": "meta", "props": { "property": "og:url", "content": "..." } },
        { "type": "meta", "props": { "name": "twitter:title", "content": "..." } },
        { "type": "meta", "props": { "name": "twitter:description", "content": "..." } },
        { "type": "meta", "props": { "name": "twitter:image", "content": "..." } },
        { "type": "meta", "props": { "name": "twitter:card", "content": "summary_large_image" } },
        { "type": "link", "props": { "rel": "canonical", "href": "..." } }
      ]
    }
  },
  "publish": true
}
```

## ✅ Implementation Status

### Fully Implemented ✅
- SEO keywords (main + additional)
- Meta description and title
- Open Graph tags (all standard fields)
- Twitter Card tags (all standard fields)
- Canonical URL
- **Blog categories** (lookup/create)
- **Blog tags** (lookup/create)
- Wix Ricos API integration (with fallback)

### Partially Implemented ⚠️
- Image handling (only HTTP/HTTPS URLs, base64 skipped)

### Not Implemented ❌
- JSON-LD structured data (requires frontend)
- URL slug customization
- Reading time (not applicable)
- Optimization score (not applicable)

## 🎯 Summary

**All major SEO metadata fields are now being posted to Wix:**
- ✅ Keywords
- ✅ Meta tags
- ✅ Open Graph
- ✅ Twitter Cards
- ✅ Canonical URL
- ✅ Categories (auto-lookup/create)
- ✅ Tags (auto-lookup/create)

The only missing piece is JSON-LD structured data, which requires frontend implementation in the Wix site code using the `@wix/site-seo` package.

