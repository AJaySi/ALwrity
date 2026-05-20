# ALwrity SEO Tools - API Reference Guide

**Last Updated**: May 18, 2026  
**API Version**: 1.0  
**Base URL**: `https://api.alwrity.com`

---

## Table of Contents
1. [Individual Tool Endpoints](#individual-tool-endpoints)
2. [Dashboard Endpoints](#dashboard-endpoints)
3. [Workflow Endpoints](#workflow-endpoints)
4. [Request/Response Examples](#requestresponse-examples)
5. [Authentication](#authentication)
6. [Error Handling](#error-handling)

---

## Individual Tool Endpoints

### 1. Meta Description Generator

**Endpoint**: `POST /api/seo/meta-description`

**Description**: Generate AI-powered SEO meta descriptions based on keywords and context.

**Request Model**:
```typescript
{
  keywords: string[],           // Required. At least one keyword
  tone: string,                 // Default: "General"
  search_intent: string,        // Default: "Informational Intent"
  language: string,             // Default: "English"
  custom_prompt?: string        // Optional custom instruction
}
```

**Response Model**:
```typescript
{
  success: boolean,
  message: string,
  execution_time: number,
  data: {
    meta_descriptions: string[],
    analysis: {
      keyword_density: number,
      length_optimal: boolean,
      seo_score: number
    }
  }
}
```

**Example Request**:
```bash
curl -X POST https://api.alwrity.com/api/seo/meta-description \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "keywords": ["SEO", "content marketing"],
    "tone": "Professional",
    "search_intent": "Informational Intent"
  }'
```

**Example Response**:
```json
{
  "success": true,
  "message": "Meta description generated successfully",
  "execution_time": 2.3,
  "data": {
    "meta_descriptions": [
      "Master SEO and content marketing strategies to boost your online visibility and drive organic traffic.",
      "Learn proven SEO techniques and content marketing best practices for 2024..."
    ],
    "analysis": {
      "keyword_density": 0.08,
      "length_optimal": true,
      "seo_score": 92
    }
  }
}
```

---

### 2. PageSpeed Analyzer

**Endpoint**: `POST /api/seo/pagespeed-analysis`

**Description**: Analyze website performance using Google PageSpeed Insights with AI insights.

**Request Model**:
```typescript
{
  url: string,                   // Required. Valid HTTP(S) URL
  strategy: string,              // Default: "DESKTOP" | Options: "DESKTOP", "MOBILE"
  locale: string,                // Default: "en"
  categories: string[]           // Default: ["performance", "accessibility", "best-practices", "seo"]
}
```

**Response Model**:
```typescript
{
  success: boolean,
  message: string,
  execution_time: number,
  data: {
    url: string,
    scores: {
      performance: number,
      accessibility: number,
      best_practices: number,
      seo: number
    },
    core_web_vitals: {
      lcp: number,               // Largest Contentful Paint (ms)
      fid: number,               // First Input Delay (ms)
      cls: number                // Cumulative Layout Shift (score)
    },
    opportunities: Array,        // Optimization opportunities
    diagnostics: Array,          // Technical issues
    ai_insights: string          // AI-powered recommendations
  }
}
```

**Example Request**:
```bash
curl -X POST https://api.alwrity.com/api/seo/pagespeed-analysis \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "strategy": "MOBILE",
    "categories": ["performance", "seo"]
  }'
```

---

### 3. Sitemap Analyzer

**Endpoint**: `POST /api/seo/sitemap-analysis`

**Description**: Analyze website structure, content distribution, and publishing patterns.

**Request Model**:
```typescript
{
  sitemap_url: string,           // Required. Valid sitemap.xml URL
  analyze_content_trends: boolean, // Default: true
  analyze_publishing_patterns: boolean  // Default: true
}
```

**Response Model**:
```typescript
{
  success: boolean,
  message: string,
  execution_time: number,
  data: {
    basic_metrics: {
      total_urls: number,
      url_patterns: Record<string, number>,
      file_types: Record<string, number>,
      average_path_depth: number,
      max_path_depth: number,
      structure_quality: string
    },
    content_trends: {
      date_range: { span_days: number, earliest: string, latest: string },
      monthly_distribution: Record<string, number>,
      yearly_distribution: Record<string, number>,
      publishing_velocity: number,  // Posts per week
      total_dated_urls: number,
      trends: string[]
    },
    publishing_patterns: {
      priority_distribution: Record<string, number>,
      changefreq_distribution: Record<string, number>,
      optimization_opportunities: string[]
    },
    ai_insights: {
      summary: string,
      content_strategy: string[],
      seo_opportunities: string[],
      technical_recommendations: string[],
      growth_recommendations: string[]
    },
    seo_recommendations: Array
  }
}
```

---

### 4. Image Alt Text Generator

**Endpoint**: `POST /api/seo/image-alt-text`

**Description**: Generate SEO-optimized alt text for images using AI vision analysis.

**Request Model** (multipart/form-data):
```typescript
// Option 1: Upload file
{
  image_file: File,              // Image file (JPG, PNG, WebP, GIF)
  context?: string,              // Optional context about the image
  keywords?: string[]            // Optional keywords to include
}

// Option 2: URL reference
{
  image_url: string,             // URL of image to analyze
  context?: string,
  keywords?: string[]
}
```

**Response Model**:
```typescript
{
  success: boolean,
  message: string,
  execution_time: number,
  data: {
    alt_text: string,            // Generated alt text
    analysis: {
      keywords_used: string[],
      length: number,
      seo_score: number,
      accessibility_score: number
    },
    alternatives: string[],      // Alternative suggestions
    keywords_identified: string[]
  }
}
```

---

### 5. OpenGraph Generator

**Endpoint**: `POST /api/seo/opengraph-tags`

**Description**: Generate platform-specific OpenGraph tags for social media optimization.

**Request Model**:
```typescript
{
  url: string,                   // Required. Page URL
  title_hint?: string,           // Suggested page title
  description_hint?: string,     // Suggested description
  platform: string               // Default: "General" | Options: "Facebook", "Twitter", "LinkedIn", "Pinterest"
}
```

**Response Model**:
```typescript
{
  success: boolean,
  message: string,
  execution_time: number,
  data: {
    og_tags: {
      "og:title": string,
      "og:description": string,
      "og:image": string,
      "og:type": string,
      "og:url": string,
      "og:locale": string,
      [key: string]: string       // Platform-specific tags
    },
    twitter_card: {              // If Twitter platform
      "twitter:card": string,
      "twitter:title": string,
      "twitter:description": string,
      "twitter:image": string
    },
    html_code: string            // HTML ready to use
  }
}
```

---

### 6. On-Page SEO Analyzer

**Endpoint**: `POST /api/seo/on-page-analysis`

**Description**: Comprehensive on-page SEO analysis including meta tags, content quality, and recommendations.

**Request Model**:
```typescript
{
  url: string,                   // Required. Page URL to analyze
  target_keywords?: string[],    // Optional keywords to check
  analyze_images: boolean,       // Default: true
  analyze_content_quality: boolean  // Default: true
}
```

**Response Model**:
```typescript
{
  success: boolean,
  message: string,
  execution_time: number,
  data: {
    overall_score: number,       // 0-100
    url: string,
    meta_analysis: {
      title: { text: string, score: number, issues: string[] },
      description: { text: string, score: number, issues: string[] },
      keywords: { score: number, density: number, issues: string[] },
      headings: Array
    },
    content_analysis: {
      word_count: number,
      readability_score: number,
      keyword_density: number,
      issues: string[]
    },
    technical_analysis: {
      links_internal: number,
      links_external: number,
      images: number,
      images_with_alt: number,
      structured_data: boolean
    },
    critical_issues: Array,
    warnings: Array,
    recommendations: Array
  }
}
```

---

### 7. Technical SEO Analyzer

**Endpoint**: `POST /api/seo/technical-seo`

**Description**: Comprehensive technical SEO audit with crawling and analysis.

**Request Model**:
```typescript
{
  url: string,                   // Required. Website URL to crawl
  crawl_depth: number,           // Default: 3 | Range: 1-5
  include_external_links: boolean, // Default: true
  analyze_performance: boolean   // Default: true
}
```

**Response Model**:
```typescript
{
  success: boolean,
  message: string,
  execution_time: number,
  data: {
    overall_score: number,
    pages_crawled: number,
    issues: Array<{
      severity: "critical" | "high" | "medium" | "low",
      url: string,
      issue: string,
      recommendation: string
    }>,
    robots_txt: { valid: boolean, content: string },
    sitemap: { valid: boolean, urls_found: number },
    canonicalization: { issues: string[] },
    redirects: Array,
    broken_links: Array,
    performance_metrics: {
      avg_load_time: number,
      mobile_friendly: boolean,
      https_enabled: boolean
    },
    recommendations: Array
  }
}
```

---

## Dashboard Endpoints

### 1. SEO Dashboard Overview

**Endpoint**: `GET /api/seo-dashboard/overview`

**Query Parameters**:
- `site_url` (optional): Specific site to analyze

**Response**:
```typescript
{
  success: boolean,
  data: {
    health_score: {
      score: number,
      change: number,
      trend: "up" | "down" | "flat",
      label: string,
      color: string
    },
    key_insight: string,
    priority_alert: string,
    metrics: Record<string, SEOMetric>,
    platforms: Record<string, PlatformStatus>,
    ai_insights: Array<AIInsight>,
    last_updated: string,
    website_url?: string
  }
}
```

---

### 2. Platform Status

**Endpoint**: `GET /api/seo-dashboard/platforms`

**Response**:
```typescript
{
  success: boolean,
  data: {
    gsc: {
      connected: boolean,
      sites: string[],
      last_sync: string | null,
      status: "connected" | "disconnected" | "error"
    },
    bing: {
      connected: boolean,
      sites: string[],
      last_sync: string | null,
      status: "connected" | "disconnected" | "error",
      has_expired_tokens: boolean
    },
    ga4: {
      connected: boolean,
      properties: Array,
      last_sync: string | null,
      status: "connected" | "disconnected" | "error"
    }
  }
}
```

---

### 3. Health Score

**Endpoint**: `GET /api/seo-dashboard/health-score`

**Response**:
```typescript
{
  success: boolean,
  data: {
    overall_score: number,         // 0-100
    previous_score: number,
    change: number,                // +/- points
    trend: "up" | "down" | "flat",
    status: "excellent" | "good" | "needs_attention" | "critical",
    breakdown: {
      technical: number,
      content: number,
      performance: number,
      mobile: number
    }
  }
}
```

---

### 4. Competitive Insights

**Endpoint**: `GET /api/seo-dashboard/competitive-insights`

**Response**:
```typescript
{
  success: boolean,
  data: {
    competitors: Array<{
      url: string,
      trust_score: number,
      content_volume: number,
      publishing_frequency: string,
      strengths: string[],
      weaknesses: string[]
    }>,
    market_position: string,
    opportunities: string[],
    threats: string[]
  }
}
```

---

### 5. Strategic Insights History

**Endpoint**: `GET /api/seo-dashboard/strategic-insights/history`

**Response**:
```typescript
{
  success: boolean,
  data: {
    history: Array<{
      date: string,
      insights: string[],
      recommendations: string[],
      priority_level: "high" | "medium" | "low"
    }>
  }
}
```

---

## Workflow Endpoints

### 1. Complete Website Audit

**Endpoint**: `POST /api/seo/workflow/website-audit`

**Request Model**:
```typescript
{
  website_url: string,           // Required
  workflow_type: string,         // "comprehensive" | "quick" | "competitive"
  competitors?: string[],        // Max 5 competitor URLs
  target_keywords?: string[],
  custom_parameters?: Record<string, any>
}
```

**Response**:
```typescript
{
  success: boolean,
  message: string,
  execution_time: number,
  data: {
    overall_score: number,
    audit_date: string,
    technical_seo_score: number,
    on_page_score: number,
    competitive_score: number,
    critical_issues: Array,
    warnings: Array,
    recommendations: Array,
    pdf_report_url?: string
  }
}
```

---

### 2. Content Analysis Workflow

**Endpoint**: `POST /api/seo/workflow/content-analysis`

**Request Model**:
```typescript
{
  website_url: string,           // Required
  workflow_type: string,
  competitors?: string[],
  target_keywords?: string[],
  custom_parameters?: Record<string, any>
}
```

**Response**:
```typescript
{
  success: boolean,
  data: {
    content_gaps: Array<{
      topic: string,
      opportunity_score: number,
      difficulty: "Easy" | "Medium" | "Hard",
      search_volume: string,
      competition: string,
      recommended_content_types: string[]
    }>,
    opportunities: Array,
    competitive_positioning: {
      content_volume: number,
      average_length: number,
      content_types_used: string[]
    },
    recommendations: string[]
  }
}
```

---

### 3. Competitive Sitemap Benchmarking

**Endpoint**: `POST /api/seo/competitive-sitemap-benchmarking/run`

**Request Model**:
```typescript
{
  max_competitors: number,       // Default: 5, Range: 1-10
  competitors?: string[]         // Optional specific competitors
}
```

**Response** (Queued for background processing):
```typescript
{
  success: boolean,
  message: "Competitive sitemap benchmarking started in background",
  data: {
    status: "queued",
    competitors_count: number
  }
}
```

**Get Results**:
```
GET /api/seo/competitive-sitemap-benchmarking
```

---

## Request/Response Examples

### Example 1: Complete Workflow

```bash
# Step 1: Analyze PageSpeed
curl -X POST https://api.alwrity.com/api/seo/pagespeed-analysis \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "strategy": "MOBILE"
  }'

# Step 2: Analyze Sitemap
curl -X POST https://api.alwrity.com/api/seo/sitemap-analysis \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "sitemap_url": "https://example.com/sitemap.xml"
  }'

# Step 3: Technical SEO
curl -X POST https://api.alwrity.com/api/seo/technical-seo \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "crawl_depth": 3
  }'

# Step 4: Get Dashboard
curl -X GET "https://api.alwrity.com/api/seo-dashboard/overview?site_url=https://example.com" \
  -H "Authorization: Bearer TOKEN"
```

---

## Authentication

### Required Headers
```
Authorization: Bearer {JWT_TOKEN}
Content-Type: application/json
```

### Token Acquisition
- Via Clerk authentication
- Obtained after user login
- Expires: As per JWT configuration

### OAuth for Platform Access
- **Google**: OAuth 2.0 for GSC/GA4
- **Microsoft**: OAuth 2.0 for Bing
- Requested during dashboard setup

---

## Error Handling

### Error Response Format
```typescript
{
  success: false,
  message: string,
  error_type: string,
  error_details: string,
  timestamp: ISO8601_DATE,
  execution_time: number,
  traceback?: string  // Only in DEBUG mode
}
```

### Common Error Codes

| Code | Error | Solution |
|------|-------|----------|
| 401 | Unauthorized | Provide valid JWT token |
| 400 | Invalid URL | Check URL format (must be HTTP/HTTPS) |
| 404 | Resource not found | Verify endpoint exists |
| 429 | Rate limited | Wait before retrying |
| 500 | Server error | Contact support |

### Example Error Response
```json
{
  "success": false,
  "message": "Error in generate_meta_description: Invalid keywords list",
  "error_type": "ValueError",
  "error_details": "At least one keyword is required",
  "timestamp": "2024-01-15T10:30:00Z",
  "execution_time": 0.1
}
```

---

## Rate Limiting

- **Individual Tools**: 100 requests/hour per user
- **Workflows**: 10 requests/hour per user
- **Dashboard**: 1000 requests/hour per user

Headers returned:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1234567890
```

---

## Caching

### Cache Headers
```
Cache-Control: max-age=3600  // 1 hour for dashboard data
ETag: "abc123..."
Last-Modified: 2024-01-15T10:00:00Z
```

### Cache Keys
- Dashboard data: `seo_dashboard:{user_id}:{site_url}`
- Analysis results: `seo_analysis:{tool_name}:{url_hash}`

---

## WebSocket Support (Planned)

For real-time dashboard updates:
```
wss://api.alwrity.com/ws/seo-dashboard/{user_id}
```

---

## Pagination

Applicable to list endpoints:

```
GET /api/seo-dashboard/competitive-insights?page=1&limit=10
```

Response:
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 45,
    "pages": 5
  }
}
```

---

## Version Management

Current API Version: **1.0**

Future versions will support:
- `/api/v2/seo/...` for breaking changes
- Backward compatibility for v1 endpoints
- Deprecation notice 6 months before sunset

---

## Support & Documentation

- **API Status**: https://status.alwrity.com
- **Documentation**: https://docs.alwrity.com/seo
- **Support Email**: support@alwrity.com
- **Issue Tracker**: https://github.com/alwrity/issues

---

**Last Updated**: May 18, 2026  
**API Version**: 1.0  
**Status**: Production Ready ✅
