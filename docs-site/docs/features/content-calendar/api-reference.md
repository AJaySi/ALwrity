# Content Calendar API Reference

Complete API documentation for ALwrity Content Calendar, including calendar management, content scheduling, analytics integration, and automation features.

## Authentication

### API Key Authentication

All API requests require authentication using your ALwrity API key.

```http
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json
```

### OAuth 2.0 Integration

For third-party integrations, use OAuth 2.0 flow:

```http
POST /oauth/token
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code&code=AUTH_CODE&redirect_uri=YOUR_REDIRECT_URI&client_id=YOUR_CLIENT_ID&client_secret=YOUR_CLIENT_SECRET
```

### Rate Limiting

- **Free Tier**: 1,000 requests per hour
- **Pro Tier**: 10,000 requests per hour
- **Enterprise Tier**: 100,000 requests per hour

Rate limit headers included in all responses:
```http
X-RateLimit-Limit: 10000
X-RateLimit-Remaining: 9999
X-RateLimit-Reset: 1640995200
X-RateLimit-Retry-After: 60
```

## Base URL

```
https://api.alwrity.com/v1/calendar
```

## Core Resources

### Calendar

Represents a content calendar with events, settings, and metadata.

**Properties:**
```json
{
  "id": "cal_123456",
  "name": "Brand Content Calendar 2024",
  "description": "Main content calendar for brand marketing",
  "timezone": "America/New_York",
  "owner_id": "user_789",
  "team_id": "team_456",
  "settings": {
    "default_platform": "instagram",
    "working_hours": {"start": "09:00", "end": "17:00"},
    "auto_publish": false,
    "approval_workflow": true
  },
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### Event

Represents a content event in the calendar.

**Properties:**
```json
{
  "id": "evt_123456",
  "calendar_id": "cal_123456",
  "title": "Product Launch Announcement",
  "description": "Announcing our new eco-friendly water bottle",
  "content_type": "social_post",
  "platform": "instagram",
  "status": "scheduled",
  "scheduled_at": "2024-01-20T14:00:00Z",
  "duration": 300,
  "content": {
    "caption": "🌿 Introducing our revolutionary eco-water bottle...",
    "media_urls": ["https://cdn.alwrity.com/images/img_123.jpg"],
    "hashtags": ["#EcoFriendly", "#SustainableLiving"],
    "tags": ["product_launch", "sustainability"]
  },
  "metadata": {
    "priority": "high",
    "campaign_id": "cmp_789",
    "assigned_to": "user_456",
    "approval_required": true,
    "ai_generated": true
  },
  "performance": {
    "impressions": 15420,
    "engagements": 1247,
    "clicks": 89
  }
}
```

## Endpoints

### Calendar Management

#### Create Calendar

```http
POST /calendars
```

**Request Body:**
```json
{
  "name": "Q1 Marketing Calendar",
  "description": "Content strategy for Q1 2024",
  "timezone": "America/New_York",
  "settings": {
    "default_platform": "multi",
    "working_hours": {"start": "09:00", "end": "17:00"},
    "auto_publish": false,
    "approval_workflow": true
  }
}
```

**Response:**
```json
{
  "id": "cal_123456",
  "name": "Q1 Marketing Calendar",
  "status": "active",
  "created_at": "2024-01-15T10:00:00Z"
}
```

#### Get Calendar

```http
GET /calendars/{calendar_id}
```

**Response:**
```json
{
  "calendar": {
    "id": "cal_123456",
    "name": "Q1 Marketing Calendar",
    "events_count": 47,
    "upcoming_events": 12,
    "settings": {...}
  },
  "events": [
    {
      "id": "evt_123456",
      "title": "Product Launch Post",
      "scheduled_at": "2024-01-20T14:00:00Z",
      "status": "scheduled"
    }
  ]
}
```

#### List Calendars

```http
GET /calendars
```

**Query Parameters:**
- `team_id`: Filter by team
- `status`: active, archived
- `limit`: Number of results (default: 20, max: 100)
- `offset`: Pagination offset

#### Update Calendar

```http
PATCH /calendars/{calendar_id}
```

**Request Body:**
```json
{
  "name": "Q1 2024 Marketing Calendar",
  "settings": {
    "auto_publish": true
  }
}
```

#### Delete Calendar

```http
DELETE /calendars/{calendar_id}
```

### Event Management

#### Create Event

```http
POST /calendars/{calendar_id}/events
```

**Request Body:**
```json
{
  "title": "Instagram Product Showcase",
  "description": "Showcase new product features",
  "content_type": "carousel_post",
  "platform": "instagram",
  "scheduled_at": "2024-01-20T15:00:00Z",
  "content": {
    "caption": "Discover the features that make our product revolutionary ✨",
    "media_urls": [
      "https://cdn.alwrity.com/images/carousel_1.jpg",
      "https://cdn.alwrity.com/images/carousel_2.jpg",
      "https://cdn.alwrity.com/images/carousel_3.jpg"
    ],
    "hashtags": ["#ProductShowcase", "#Innovation"],
    "location": "New York, NY"
  },
  "metadata": {
    "priority": "high",
    "campaign_id": "cmp_launch_2024",
    "assigned_to": "user_marketing",
    "approval_required": true
  }
}
```

#### Get Event

```http
GET /calendars/{calendar_id}/events/{event_id}
```

#### List Events

```http
GET /calendars/{calendar_id}/events
```

**Query Parameters:**
- `start_date`: Filter events from this date (ISO 8601)
- `end_date`: Filter events until this date (ISO 8601)
- `platform`: Filter by platform (instagram, facebook, etc.)
- `status`: scheduled, published, draft, cancelled
- `assigned_to`: Filter by assigned user
- `campaign_id`: Filter by campaign
- `limit`: Number of results (default: 50, max: 200)
- `offset`: Pagination offset

#### Update Event

```http
PATCH /calendars/{calendar_id}/events/{event_id}
```

**Request Body:**
```json
{
  "scheduled_at": "2024-01-20T16:00:00Z",
  "content": {
    "caption": "Updated caption with new call-to-action 📣"
  },
  "status": "approved"
}
```

#### Bulk Update Events

```http
PATCH /calendars/{calendar_id}/events/bulk
```

**Request Body:**
```json
{
  "event_ids": ["evt_123", "evt_456", "evt_789"],
  "updates": {
    "status": "published",
    "metadata": {
      "campaign_id": "cmp_q1_2024"
    }
  }
}
```

#### Delete Event

```http
DELETE /calendars/{calendar_id}/events/{event_id}
```

### Content Generation

#### Generate Content Event

```http
POST /calendars/{calendar_id}/events/generate
```

**Request Body:**
```json
{
  "topic": "Sustainable living tips for busy professionals",
  "content_type": "thread",
  "platform": "twitter",
  "tone": "professional_helpful",
  "audience": "business_professionals",
  "word_count": 800,
  "include_hashtags": true,
  "include_cta": true,
  "scheduled_at": "2024-01-18T11:00:00Z"
}
```

**Response:**
```json
{
  "event_id": "evt_generated_123",
  "status": "generated",
  "content": {
    "title": "5 Sustainable Living Hacks for Busy Professionals",
    "thread_content": [
      "🌱 As busy professionals, sustainability often takes a backseat. But small changes can make a big impact. Here are 5 practical tips:\n\n#SustainableLiving #EcoFriendly",
      "1️⃣ Digital over Paper: Switch to digital receipts, invoices, and notes. Save trees and reduce clutter!\n\n#GoDigital #Paperless",
      "2️⃣ Reusable Everything: Invest in quality reusable water bottles, coffee cups, and shopping bags. Your future self will thank you.\n\n#ReduceWaste #Reusable",
      "3️⃣ Smart Commute: Combine errands, use public transport, or carpool when possible. Every mile saved counts.\n\n#SustainableCommute #EcoTravel"
    ],
    "hashtags": ["#SustainableLiving", "#EcoTips", "#GreenOffice"],
    "estimated_performance": {
      "engagement_rate": 4.2,
      "reach_potential": "medium"
    }
  }
}
```

#### Generate Content Series

```http
POST /calendars/{calendar_id}/series/generate
```

**Request Body:**
```json
{
  "series_title": "Ultimate Guide to Remote Work Productivity",
  "description": "7-part series on remote work best practices",
  "content_types": ["blog_post", "social_thread", "video_script"],
  "platforms": ["linkedin", "twitter", "youtube"],
  "schedule": {
    "frequency": "weekly",
    "start_date": "2024-02-01",
    "posts_per_week": 3
  },
  "audience": "remote_workers",
  "tone": "professional_expert"
}
```

### Advanced Scheduling

#### Optimal Timing Analysis

```http
GET /calendars/{calendar_id}/timing/analyze
```

**Query Parameters:**
- `platform`: Platform to analyze (instagram, facebook, etc.)
- `content_type`: Type of content
- `audience_segment`: Target audience group
- `date_range`: Analysis period (default: last 30 days)

**Response:**
```json
{
  "platform": "instagram",
  "analysis_period": "2024-01-01 to 2024-01-31",
  "optimal_times": [
    {
      "day_of_week": "wednesday",
      "hour": 14,
      "timezone": "America/New_York",
      "performance_score": 9.2,
      "expected_reach": 15400,
      "confidence": 0.87
    },
    {
      "day_of_week": "friday",
      "hour": 11,
      "timezone": "America/New_York",
      "performance_score": 8.9,
      "expected_reach": 12800,
      "confidence": 0.82
    }
  ],
  "audience_insights": {
    "peak_activity": "14:00-16:00",
    "timezone_distribution": {
      "EST": 45,
      "PST": 30,
      "GMT": 15,
      "other": 10
    }
  }
}
```

#### Smart Scheduling

```http
POST /calendars/{calendar_id}/events/smart-schedule
```

**Request Body:**
```json
{
  "events": [
    {
      "title": "Product Announcement",
      "content_type": "feed_post",
      "platform": "instagram",
      "priority": "high",
      "flexibility": "medium"
    },
    {
      "title": "Behind the Scenes",
      "content_type": "story",
      "platform": "instagram",
      "priority": "medium",
      "flexibility": "high"
    }
  ],
  "constraints": {
    "min_spacing_hours": 4,
    "max_per_day": 3,
    "business_hours_only": true,
    "avoid_dates": ["2024-01-01", "2024-12-25"]
  },
  "optimization_goals": {
    "maximize_reach": true,
    "balance_content_types": true,
    "respect_capacity": true
  }
}
```

**Response:**
```json
{
  "scheduled_events": [
    {
      "original_id": "evt_123",
      "scheduled_at": "2024-01-20T14:30:00Z",
      "confidence_score": 0.91,
      "expected_performance": {
        "reach": 15200,
        "engagement_rate": 4.1
      }
    },
    {
      "original_id": "evt_456",
      "scheduled_at": "2024-01-20T16:45:00Z",
      "confidence_score": 0.88,
      "expected_performance": {
        "reach": 8900,
        "engagement_rate": 3.8
      }
    }
  ],
  "optimization_summary": {
    "total_reach_optimized": 24100,
    "content_balance_score": 9.2,
    "capacity_utilization": 78
  }
}
```

### Analytics & Reporting

#### Get Event Performance

```http
GET /calendars/{calendar_id}/events/{event_id}/performance
```

**Response:**
```json
{
  "event_id": "evt_123456",
  "platform": "instagram",
  "metrics": {
    "impressions": 15420,
    "reach": 12890,
    "engagements": 1247,
    "likes": 892,
    "comments": 156,
    "shares": 67,
    "saves": 132,
    "clicks": 89,
    "engagement_rate": 9.7,
    "click_through_rate": 0.69
  },
  "audience_insights": {
    "demographics": {
      "age_18_24": 25,
      "age_25_34": 45,
      "age_35_44": 20,
      "female": 68,
      "male": 32
    },
    "top_cities": ["New York", "Los Angeles", "Chicago"]
  },
  "ai_insights": {
    "performance_score": 8.5,
    "optimization_suggestions": [
      "This posting time performs 25% better than average",
      "Carousel format increased engagement by 40%",
      "Consider more educational content like this"
    ]
  }
}
```

#### Get Calendar Analytics

```http
GET /calendars/{calendar_id}/analytics
```

**Query Parameters:**
- `start_date`: Analysis start date
- `end_date`: Analysis end date
- `platform`: Filter by platform
- `content_type`: Filter by content type
- `group_by`: day, week, month

**Response:**
```json
{
  "summary": {
    "total_events": 156,
    "published_events": 142,
    "total_impressions": 2345678,
    "total_engagements": 187654,
    "average_engagement_rate": 8.0
  },
  "performance_trends": [
    {
      "date": "2024-01-15",
      "impressions": 45678,
      "engagements": 3456,
      "engagement_rate": 7.6
    }
  ],
  "platform_breakdown": {
    "instagram": {"events": 89, "engagements": 123456},
    "linkedin": {"events": 34, "engagements": 34567},
    "twitter": {"events": 19, "engagements": 29876}
  },
  "content_performance": {
    "best_performing_type": "educational_posts",
    "worst_performing_type": "promotional_posts",
    "optimal_posting_times": ["14:00", "16:00", "19:00"]
  }
}
```

### Campaign Management

#### Create Campaign

```http
POST /calendars/{calendar_id}/campaigns
```

**Request Body:**
```json
{
  "name": "Q1 Product Launch Campaign",
  "description": "Launch campaign for new eco-friendly product line",
  "objectives": [
    "Generate 500 qualified leads",
    "Achieve 50K impressions",
    "Drive 1000 website visits"
  ],
  "target_audience": "eco_conscious_millennials",
  "budget": {
    "amount": 5000,
    "currency": "USD",
    "platforms": ["instagram", "facebook", "google_ads"]
  },
  "timeline": {
    "start_date": "2024-01-15",
    "end_date": "2024-03-15",
    "milestones": [
      {"date": "2024-01-20", "name": "Teaser Launch"},
      {"date": "2024-02-01", "name": "Full Launch"},
      {"date": "2024-02-15", "name": "Mid-campaign Review"}
    ]
  },
  "content_strategy": {
    "pillars": ["sustainability", "innovation", "community"],
    "content_mix": {
      "educational": 40,
      "promotional": 30,
      "engagement": 20,
      "user_generated": 10
    }
  }
}
```

#### Get Campaign Performance

```http
GET /calendars/{calendar_id}/campaigns/{campaign_id}/performance
```

### Team Collaboration

#### Share Calendar

```http
POST /calendars/{calendar_id}/share
```

**Request Body:**
```json
{
  "user_id": "user_456",
  "role": "editor",
  "permissions": {
    "create_events": true,
    "edit_events": true,
    "delete_events": false,
    "publish_content": false,
    "view_analytics": true
  }
}
```

#### Approval Workflows

```http
POST /calendars/{calendar_id}/events/{event_id}/approve
```

**Request Body:**
```json
{
  "approved": true,
  "comments": "Looks great! Approved for publishing.",
  "approved_by": "user_manager"
}
```

### Webhooks

#### Setup Webhooks

```http
POST /webhooks
```

**Request Body:**
```json
{
  "url": "https://your-app.com/webhooks/calendar",
  "events": [
    "event.created",
    "event.updated",
    "event.published",
    "event.performance_updated",
    "calendar.analytics_ready"
  ],
  "secret": "your-webhook-secret"
}
```

#### Webhook Events

```json
{
  "event": "event.published",
  "id": "wh_123456",
  "timestamp": "2024-01-20T14:00:00Z",
  "data": {
    "calendar_id": "cal_123456",
    "event_id": "evt_789",
    "platform": "instagram",
    "published_at": "2024-01-20T14:00:00Z",
    "performance_initial": {
      "impressions": 0,
      "engagements": 0
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
    "message": "Invalid scheduled date: cannot schedule events in the past",
    "details": {
      "field": "scheduled_at",
      "provided_value": "2023-12-01T10:00:00Z",
      "current_time": "2024-01-15T10:00:00Z"
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
| `NOT_FOUND_ERROR` | 404 | Resource not found |
| `RATE_LIMIT_EXCEEDED` | 429 | API rate limit exceeded |
| `CALENDAR_FULL` | 402 | Calendar has reached event limit |
| `PLATFORM_ERROR` | 502 | External platform API error |

## SDK Examples

### JavaScript/Node.js

```javascript
const AlwrityCalendar = require('alwrity-calendar-sdk');

const client = new AlwrityCalendar({
  apiKey: 'your-api-key'
});

// Create a calendar
const calendar = await client.calendars.create({
  name: 'Marketing Calendar 2024',
  timezone: 'America/New_York'
});

// Schedule content
const event = await client.events.create(calendar.id, {
  title: 'Product Launch Post',
  platform: 'instagram',
  scheduled_at: '2024-01-20T14:00:00Z',
  content: {
    caption: 'Exciting news coming soon! 🚀',
    hashtags: ['#ComingSoon', '#Innovation']
  }
});
```

### Python

```python
from alwrity_calendar import CalendarClient

client = CalendarClient(api_key='your-api-key')

# Generate and schedule content series
series = client.series.generate(
    calendar_id='cal_123456',
    series_title='Social Media Marketing Guide',
    content_types=['thread', 'carousel', 'video'],
    platforms=['twitter', 'instagram', 'youtube'],
    schedule={'frequency': 'weekly', 'posts_per_week': 3}
)

print(f"Generated {len(series.events)} events")
```

## Best Practices

### API Usage
- **Batch Operations**: Use bulk endpoints for multiple events
- **Rate Limiting**: Implement exponential backoff
- **Caching**: Cache calendar data for better performance
- **Webhooks**: Use webhooks for real-time updates

### Scheduling Optimization
- **Audience Analysis**: Use timing analytics for optimal scheduling
- **Content Balance**: Mix content types for better engagement
- **Platform Strategy**: Tailor content for each platform's algorithm
- **Performance Monitoring**: Track and optimize based on analytics

### Integration Patterns
- **Webhook Security**: Verify webhook signatures
- **Error Handling**: Implement comprehensive error handling
- **Retry Logic**: Handle temporary failures gracefully
- **Monitoring**: Track API usage and performance

---

[:octicons-arrow-right-24: Back to Overview](overview.md)