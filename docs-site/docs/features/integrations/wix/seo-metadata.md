# SEO Metadata (Wix)

This page summarizes what ALwrity posts to Wix and what remains out of scope.

## Posted to Wix
- Keywords (seoData.settings.keywords)
  - Main keyword: `focus_keyword` → `isMain: true`
  - Additional: `blog_tags`, `social_hashtags` → `isMain: false`
- Meta Tags (seoData.tags)
  - `<meta name="description">` from `meta_description`
  - `<meta name="title">` from `seo_title`
- Open Graph (seoData.tags)
  - `og:title`, `og:description`, `og:image`, `og:type=article`, `og:url`
- Twitter Card (seoData.tags)
  - `twitter:title`, `twitter:description`, `twitter:image`, `twitter:card`
- Canonical URL (seoData.tags)
  - `<link rel="canonical">`
- Categories & Tags
  - Auto‑lookup/create and post as `categoryIds` and `tagIds`

## Not Posted (Limitations)
- JSON‑LD structured data
  - Reason: Requires Wix site frontend (`@wix/site-seo`)
- URL slug customization
  - Wix auto‑generates from title
- Reading time / optimization score
  - Internal metadata, not part of Wix post

## Conversion
- Markdown → Ricos JSON via official API (with custom parser fallback)
- Supports headings, paragraphs, lists, images, basic formatting

## Example (structure excerpt)
```json
{
  "draftPost": {
    "title": "SEO optimized title",
    "memberId": "author-member-id",
    "richContent": { /* Ricos JSON */ },
    "excerpt": "First 200 chars...",
    "categoryIds": ["uuid1"],
    "tagIds": ["uuid1","uuid2"],
    "seoData": {
      "settings": { "keywords": [ { "term": "main", "isMain": true } ] },
      "tags": [ { "type": "meta", "props": { "name": "description", "content": "..." } } ]
    }
  },
  "publish": true
}
```


