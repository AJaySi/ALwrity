# ALwrity Researcher Export APIs

Comprehensive API documentation for exporting research data, managing research projects, and integrating ALwrity Researcher with external systems.

## Authentication

### API Key Authentication

All API requests require authentication using your ALwrity API key.

```http
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json
```

### OAuth 2.0 Integration

For third-party integrations requiring user-specific access:

```http
POST /oauth/token
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code&code=AUTH_CODE&redirect_uri=YOUR_REDIRECT_URI&client_id=YOUR_CLIENT_ID&client_secret=YOUR_CLIENT_SECRET
```

### Rate Limiting

- **Free Tier**: 500 requests per hour
- **Pro Tier**: 5,000 requests per hour
- **Enterprise Tier**: 50,000 requests per hour

Rate limit headers included in all responses:
```http
X-RateLimit-Limit: 5000
X-RateLimit-Remaining: 4999
X-RateLimit-Reset: 1640995200
X-RateLimit-Retry-After: 60
```

## Base URL

```
https://api.alwrity.com/v1/researcher
```

## Core Resources

### Research Project

Represents a research project with all associated data and metadata.

**Properties:**
```json
{
  "id": "proj_123456",
  "name": "AI in Healthcare Market Research",
  "description": "Comprehensive analysis of AI applications in healthcare",
  "status": "completed",
  "template_id": "market_research_enterprise",
  "created_by": "user_789",
  "created_at": "2024-01-15T10:00:00Z",
  "completed_at": "2024-01-15T12:30:00Z",
  "metadata": {
    "topic": "AI healthcare applications",
    "industry": "healthcare",
    "sources_used": 23,
    "research_depth": "comprehensive",
    "quality_score": 9.2
  }
}
```

### Research Result

Individual research findings and data points.

**Properties:**
```json
{
  "id": "result_123456",
  "project_id": "proj_123456",
  "type": "statistic",
  "title": "AI Market Size in Healthcare",
  "content": "The global AI in healthcare market is projected to reach $45.2 billion by 2026",
  "sources": [
    {
      "url": "https://www.statista.com/statistics/ai-healthcare-market",
      "title": "AI in Healthcare Market Size",
      "publisher": "Statista",
      "publish_date": "2024-01-10",
      "credibility_score": 9.1
    }
  ],
  "metadata": {
    "category": "market_data",
    "confidence_level": 0.95,
    "last_updated": "2024-01-15T12:30:00Z",
    "tags": ["market_size", "growth_forecast", "healthcare_ai"]
  }
}
```

## Export Endpoints

### Export Research Project

Export complete research project data in various formats.

```http
GET /projects/{project_id}/export
```

**Query Parameters:**
- `format`: Export format (`json`, `pdf`, `docx`, `xlsx`, `csv`, `xml`)
- `include_sources`: Include source URLs and metadata (default: `true`)
- `include_metadata`: Include research metadata (default: `true`)
- `sections`: Comma-separated list of sections to include
- `template`: Export template to use for formatting

**Response:** File download or JSON data depending on format

#### JSON Export Format
```json
{
  "project": {
    "id": "proj_123456",
    "name": "AI in Healthcare Market Research",
    "export_date": "2024-01-15T14:00:00Z",
    "version": "1.0"
  },
  "executive_summary": {
    "key_findings": ["Market growing at 35% CAGR", "AI diagnosis accuracy >95%", "Investment increasing"],
    "recommendations": ["Focus on diagnostic applications", "Partner with healthcare providers"],
    "confidence_level": 0.92
  },
  "detailed_findings": [
    {
      "section": "Market Overview",
      "findings": [
        {
          "type": "statistic",
          "title": "Market Size",
          "content": "$45.2 billion by 2026",
          "sources": ["statista_2024", "gartner_2023"],
          "confidence": 0.95
        }
      ]
    }
  ],
  "sources": [...],
  "metadata": {...}
}
```

#### PDF Export Options
```json
{
  "format_options": {
    "layout": "professional",
    "include_toc": true,
    "include_executive_summary": true,
    "page_numbers": true,
    "watermark": "Confidential",
    "font_size": "11pt",
    "margins": "1inch"
  }
}
```

#### Excel Export Format
```json
{
  "worksheets": {
    "Executive_Summary": [
      ["Key Finding", "Value", "Confidence", "Sources"],
      ["Market Size", "$45.2B", "95%", "Statista, Gartner"]
    ],
    "Detailed_Findings": [...],
    "Sources": [...],
    "Metadata": [...]
  }
}
```

### Export Research Results

Export individual research results or filtered subsets.

```http
GET /projects/{project_id}/results/export
```

**Query Parameters:**
- `format`: Export format (`json`, `csv`, `xlsx`, `xml`)
- `type`: Filter by result type (`statistic`, `quote`, `case_study`, `trend`)
- `category`: Filter by category (`market_data`, `competitor_info`, `customer_insights`)
- `date_from`: Filter results from date
- `date_to`: Filter results to date
- `min_confidence`: Minimum confidence level (0.0-1.0)
- `tags`: Comma-separated tags to include

#### CSV Export Example
```csv
id,type,title,content,confidence,sources,tags
result_123,statistic,"AI Healthcare Market Size","$45.2 billion by 2026",0.95,"statista_2024,gartner_2023","market_size,growth,healthcare"
result_124,quote,"Dr. Sarah Johnson Quote","AI will transform diagnostic accuracy from 70% to over 95%",0.88,"forrester_report","ai_accuracy,diagnosis"
result_125,trend,"Telemedicine Growth","Telemedicine market grew 300% during COVID-19",0.92,"who_report,statista","telemedicine,growth,pandemic"
```

### Bulk Export Multiple Projects

Export data from multiple research projects simultaneously.

```http
POST /projects/bulk-export
```

**Request Body:**
```json
{
  "project_ids": ["proj_123", "proj_456", "proj_789"],
  "export_format": "json",
  "combine_results": true,
  "options": {
    "include_sources": true,
    "include_metadata": true,
    "deduplicate_sources": true,
    "sort_by": "relevance",
    "limit_per_project": 50
  }
}
```

**Response:**
```json
{
  "export_id": "export_123456",
  "status": "processing",
  "estimated_completion": "2024-01-15T14:05:00Z",
  "download_url": "https://api.alwrity.com/v1/researcher/exports/export_123456/download"
}
```

### Export Templates

Export research using predefined templates.

```http
GET /projects/{project_id}/export/template/{template_id}
```

**Available Templates:**
- `executive_summary`: Concise executive summary format
- `detailed_report`: Comprehensive research report
- `presentation`: PowerPoint-ready format
- `newsletter`: Newsletter-ready content
- `blog_post`: Blog post format
- `social_media`: Social media content format

#### Template Customization
```json
{
  "template_id": "executive_summary",
  "customizations": {
    "sections": ["key_findings", "recommendations", "next_steps"],
    "branding": {
      "company_name": "ALwrity Research",
      "logo_url": "https://alwrity.com/logo.png",
      "color_scheme": "#4A90E2"
    },
    "formatting": {
      "font_family": "Arial",
      "font_size": "12pt",
      "line_spacing": "1.5"
    }
  }
}
```

## Research Management APIs

### Create Research Project

Start a new research project programmatically.

```http
POST /projects
```

**Request Body:**
```json
{
  "name": "Sustainable Fashion Market Analysis",
  "description": "Research sustainable fashion trends and market opportunities",
  "template_id": "market_research_enterprise",
  "parameters": {
    "topic": "sustainable fashion",
    "industry": "fashion",
    "geography": "global",
    "timeframe": "2024-2026",
    "depth": "comprehensive",
    "sources_minimum": 20
  },
  "options": {
    "auto_start": true,
    "priority": "high",
    "notifications": {
      "email": "researcher@company.com",
      "webhook": "https://company.com/webhooks/research"
    }
  }
}
```

**Response:**
```json
{
  "project_id": "proj_123456",
  "status": "initializing",
  "estimated_completion": "2024-01-15T11:30:00Z",
  "progress_url": "/projects/proj_123456/progress"
}
```

### Get Research Progress

Monitor the progress of ongoing research projects.

```http
GET /projects/{project_id}/progress
```

**Response:**
```json
{
  "project_id": "proj_123456",
  "status": "researching",
  "progress_percentage": 65,
  "current_stage": "data_analysis",
  "stage_progress": {
    "intent_analysis": {"status": "completed", "duration": 45},
    "query_generation": {"status": "completed", "duration": 120},
    "source_collection": {"status": "completed", "duration": 300},
    "data_extraction": {"status": "in_progress", "progress": 80},
    "analysis_synthesis": {"status": "pending", "estimated_duration": 180}
  },
  "sources_found": 18,
  "results_generated": 23,
  "quality_metrics": {
    "source_credibility": 8.7,
    "data_completeness": 0.85,
    "analysis_depth": 0.92
  },
  "estimated_completion": "2024-01-15T11:45:00Z"
}
```

### Update Research Project

Modify research parameters or add additional requirements.

```http
PATCH /projects/{project_id}
```

**Request Body:**
```json
{
  "parameters": {
    "additional_topics": ["consumer_behavior", "regulatory_changes"],
    "geography": ["north_america", "europe"],
    "extend_deadline": true
  },
  "options": {
    "priority": "urgent",
    "additional_sources": ["bloomberg", "mckinsey_reports"]
  }
}
```

### List Research Projects

Retrieve list of research projects with filtering options.

```http
GET /projects
```

**Query Parameters:**
- `status`: Filter by status (`active`, `completed`, `failed`)
- `template_id`: Filter by template used
- `created_by`: Filter by creator
- `date_from`: Filter projects created after date
- `date_to`: Filter projects created before date
- `tags`: Filter by project tags
- `limit`: Number of results (default: 20, max: 100)
- `offset`: Pagination offset

**Response:**
```json
{
  "projects": [
    {
      "id": "proj_123456",
      "name": "AI Healthcare Research",
      "status": "completed",
      "template_id": "market_research_enterprise",
      "created_at": "2024-01-15T10:00:00Z",
      "quality_score": 9.2
    }
  ],
  "total_count": 47,
  "pagination": {
    "limit": 20,
    "offset": 0,
    "has_more": true
  }
}
```

## Advanced Export Features

### Filtered Exports

Export specific subsets of research data with complex filtering.

```http
POST /projects/{project_id}/export/filtered
```

**Request Body:**
```json
{
  "filters": {
    "result_types": ["statistic", "trend"],
    "categories": ["market_data", "competitor_info"],
    "confidence_range": {"min": 0.8, "max": 1.0},
    "date_range": {"from": "2024-01-01", "to": "2024-01-31"},
    "tags": ["growth", "innovation"],
    "sources": ["statista", "gartner", "forrester"]
  },
  "grouping": {
    "group_by": "category",
    "sort_within_groups": "confidence_desc",
    "include_group_summaries": true
  },
  "format": "xlsx",
  "options": {
    "include_charts": true,
    "include_summaries": true,
    "anonymize_sources": false
  }
}
```

### Custom Export Formats

Create custom export formats using templates.

```http
POST /exports/custom
```

**Request Body:**
```json
{
  "name": "Custom Market Research Report",
  "template": {
    "structure": {
      "cover_page": {
        "title": "{{project.name}}",
        "subtitle": "Market Research Report",
        "date": "{{export_date}}",
        "branding": "{{company_branding}}"
      },
      "table_of_contents": true,
      "sections": [
        {
          "title": "Executive Summary",
          "content": "{{executive_summary}}",
          "charts": ["market_size_chart", "growth_trend_chart"]
        },
        {
          "title": "Market Analysis",
          "content": "{{market_analysis}}",
          "subsections": ["size", "growth", "segmentation"]
        }
      ],
      "appendices": ["sources", "methodology", "glossary"]
    },
    "styling": {
      "font_family": "Calibri",
      "heading_styles": {
        "h1": {"size": "16pt", "color": "#2E4057", "bold": true},
        "h2": {"size": "14pt", "color": "#5D6D7E", "bold": true}
      },
      "table_styles": {
        "header_bg": "#F8F9FA",
        "border_color": "#DEE2E6"
      }
    }
  },
  "output_format": "pdf"
}
```

## Integration APIs

### Webhook Integration

Set up webhooks for real-time research updates.

```http
POST /webhooks
```

**Request Body:**
```json
{
  "url": "https://your-app.com/webhooks/researcher",
  "events": [
    "project.created",
    "project.completed",
    "project.failed",
    "export.ready",
    "quality_alert"
  ],
  "secret": "your-webhook-secret",
  "filters": {
    "project_templates": ["market_research_enterprise"],
    "minimum_quality_score": 8.0
  }
}
```

#### Webhook Payload Examples

**Project Completed:**
```json
{
  "event": "project.completed",
  "project_id": "proj_123456",
  "timestamp": "2024-01-15T12:30:00Z",
  "data": {
    "name": "AI Healthcare Research",
    "quality_score": 9.2,
    "results_count": 47,
    "export_formats": ["json", "pdf", "xlsx"],
    "download_urls": {
      "json": "https://api.alwrity.com/v1/researcher/exports/proj_123456_json",
      "pdf": "https://api.alwrity.com/v1/researcher/exports/proj_123456_pdf"
    }
  }
}
```

### Third-Party Integrations

#### Zapier Integration
```json
{
  "integration_type": "zapier",
  "triggers": [
    {
      "event": "research_completed",
      "action": "create_google_doc",
      "mapping": {
        "document_title": "{{project.name}}",
        "content": "{{executive_summary}}",
        "folder": "Research Reports"
      }
    }
  ]
}
```

#### Slack Integration
```json
{
  "integration_type": "slack",
  "webhook_url": "https://hooks.slack.com/services/...",
  "notifications": {
    "project_completed": {
      "channel": "#research",
      "message": "🎉 Research completed: {{project.name}}\nQuality Score: {{quality_score}}/10\nDownload: {{download_url}}"
    },
    "quality_alert": {
      "channel": "#research-alerts",
      "message": "⚠️ Low quality research detected: {{project.name}} (Score: {{quality_score}}/10)"
    }
  }
}
```

## Error Handling

### Error Response Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid export format specified",
    "details": {
      "field": "format",
      "provided": "invalid_format",
      "allowed_values": ["json", "pdf", "docx", "xlsx", "csv", "xml"]
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
| `AUTHENTICATION_ERROR` | 401 | Invalid or missing API key |
| `AUTHORIZATION_ERROR` | 403 | Insufficient permissions |
| `NOT_FOUND_ERROR` | 404 | Project or resource not found |
| `RATE_LIMIT_EXCEEDED` | 429 | API rate limit exceeded |
| `PROCESSING_ERROR` | 500 | Research processing failed |
| `EXPORT_ERROR` | 500 | Export generation failed |

## Best Practices

### Export Optimization

1. **Format Selection**: Choose appropriate format for your use case
2. **Filtering**: Use filters to reduce export size and improve relevance
3. **Incremental Exports**: Export only new/changed data for large projects
4. **Compression**: Use compressed formats for large datasets

### API Usage

1. **Rate Limiting**: Implement proper rate limiting and retry logic
2. **Error Handling**: Handle all error codes appropriately
3. **Caching**: Cache frequently accessed research data
4. **Monitoring**: Monitor API usage and performance metrics

### Integration Patterns

1. **Webhook Verification**: Always verify webhook signatures
2. **Idempotency**: Use request IDs to prevent duplicate operations
3. **Pagination**: Handle large result sets with proper pagination
4. **Versioning**: Specify API versions in requests

### Security Considerations

1. **API Key Management**: Rotate API keys regularly
2. **Data Encryption**: Use HTTPS for all API communications
3. **Access Control**: Implement proper user/role-based access
4. **Audit Logging**: Log all API access for security monitoring

---

[:octicons-arrow-right-24: Back to Overview](overview.md)
[:octicons-arrow-right-24: Research Templates Library](templates-library.md)