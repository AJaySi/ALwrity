# Wix SEO Metadata Review

## SEO Metadata We Generate (`BlogSEOMetadataResponse`)

### Available Fields:
1. ✅ **seo_title** - SEO optimized title
2. ✅ **meta_description** - Meta description
3. ✅ **url_slug** - URL slug for the blog post
4. ✅ **blog_tags** - Array of tag strings (NOW being used for Wix post tags via lookup/create)
5. ✅ **blog_categories** - Array of category strings (NOW being used for Wix post categories via lookup/create)
6. ✅ **social_hashtags** - Hashtags for social media
7. ✅ **open_graph** - Open Graph metadata object:
   - title
   - description
   - image
   - url
   - type
8. ✅ **twitter_card** - Twitter Card metadata object:
   - title
   - description
   - image
   - card (type)
9. ✅ **canonical_url** - Canonical URL
10. ✅ **focus_keyword** - Main SEO keyword
11. ❌ **json_ld_schema** - JSON-LD structured data (NOT being posted - would need frontend implementation)
12. ❌ **schema** - Legacy schema field (NOT being used)
13. ❌ **reading_time** - Estimated reading time (NOT being posted)
14. ❌ **optimization_score** - SEO optimization score (NOT being posted)
15. ❌ **generated_at** - Generation timestamp (NOT being posted)

## What We're Currently Posting to Wix

### ✅ Posted via `seoData`:
- **Keywords** (from `focus_keyword`, `blog_tags`, `social_hashtags`)
  - Main keyword: `focus_keyword` → `isMain: true`
  - Additional keywords: `blog_tags` and `social_hashtags` → `isMain: false`
- **Meta Tags**:
  - `meta description` → `<meta name="description">`
  - `seo_title` → `<meta name="title">`
- **Open Graph Tags**:
  - `og:title`, `og:description`, `og:image`, `og:type`, `og:url`
- **Twitter Card Tags**:
  - `twitter:title`, `twitter:description`, `twitter:image`, `twitter:card`
- **Canonical URL**:
  - `<link rel="canonical">`

### ✅ NOW Being Posted (Recently Implemented):

1. **Blog Categories** (`blog_categories`)
   - ✅ **Implemented**: `lookup_or_create_categories()` method
   - ✅ **Behavior**: Case-insensitive lookup, auto-create if missing
   - ✅ **Result**: Categories from SEO metadata are posted as `categoryIds` (UUIDs)

2. **Blog Tags** (`blog_tags` for post organization)
   - ✅ **Implemented**: `lookup_or_create_tags()` method
   - ✅ **Behavior**: Case-insensitive lookup, auto-create if missing
   - ✅ **Result**: Tags from SEO metadata are posted as `tagIds` (UUIDs)
   - **Note**: `blog_tags` are used BOTH for SEO keywords AND for Wix post tags

3. **JSON-LD Structured Data** (`json_ld_schema`)
   - **Issue**: Wix doesn't support JSON-LD in backend API
   - **Solution**: Would need frontend implementation using `@wix/site-seo` package
   - **Status**: Not implemented

4. **URL Slug** (`url_slug`)
   - **Issue**: Not being passed to Wix
   - **Status**: Wix generates URL automatically, but we could potentially set it

## Implementation Status

### ✅ Fully Implemented:
- SEO keywords in `seoData.settings.keywords`
- Meta description tag
- SEO title tag
- Open Graph tags (title, description, image, type, url)
- Twitter Card tags (title, description, image, card type)
- Canonical URL link tag

### ✅ Fully Implemented:
- **Blog Categories**: Auto-lookup/create from `blog_categories`
- **Blog Tags**: Auto-lookup/create from `blog_tags`
- **Wix Ricos API Integration**: Uses official Wix API with fallback to custom parser

### ❌ Not Implemented (Optional):
- JSON-LD structured data (frontend only - requires `@wix/site-seo` package)
- URL slug setting (Wix auto-generates URLs)
- Reading time (metadata only, not applicable)
- Optimization score (metadata only, not applicable)

## Summary

✅ **All major SEO metadata is now being posted to Wix:**
- SEO keywords (main + additional)
- Meta tags (description, title)
- Open Graph tags (title, description, image, type, url)
- Twitter Card tags (title, description, image, card type)
- Canonical URL
- **Blog Categories** (auto-lookup/create)
- **Blog Tags** (auto-lookup/create)

The only missing piece is JSON-LD structured data, which requires frontend implementation in the Wix site code using `@wix/site-seo` package (not a backend concern).

