# Instagram Editor API Reference

Complete API documentation for ALwrity Instagram Editor, including authentication, endpoints, request/response formats, and integration examples.

## Authentication

### API Key Authentication

All API requests require an API key for authentication. Include your API key in the request header:

```http
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json
```

### Getting Your API Key

1. Log in to your ALwrity account
2. Navigate to Settings → API Keys
3. Generate a new API key for Instagram Editor
4. Copy and securely store your API key

### Rate Limiting

- **Free Tier**: 100 requests per hour
- **Pro Tier**: 1,000 requests per hour
- **Enterprise Tier**: 10,000 requests per hour

Rate limit headers are included in all responses:
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

## Base URL

```
https://api.alwrity.com/v1/instagram
```

## Endpoints

### Content Creation

#### Generate Instagram Post

Generate a complete Instagram post with caption, hashtags, and image suggestions.

```http
POST /posts/generate
```

**Request Body:**
```json
{
  "topic": "Coffee shop morning routine",
  "content_type": "feed_post",
  "tone": "casual",
  "audience": "young_adults",
  "brand_voice": "warm_and_inviting",
  "include_hashtags": true,
  "include_emoji": true,
  "generate_image": true,
  "image_style": "cozy_cafe",
  "platform_optimization": true
}
```

**Response:**
```json
{
  "id": "post_123456",
  "status": "completed",
  "content": {
    "caption": "☕ Starting the day with the perfect brew at our cozy corner café! Nothing beats that first sip of freshly roasted coffee while watching the world wake up. 🌅✨\n\n#MorningCoffee #CoffeeLovers #CozyCafé #LocalCoffee #CoffeeCulture",
    "hashtags": ["#MorningCoffee", "#CoffeeLovers", "#CozyCafé", "#LocalCoffee", "#CoffeeCulture"],
    "emoji_used": ["☕", "🌅", "✨"],
    "suggested_images": [
      {
        "url": "https://cdn.alwrity.com/images/img_789.jpg",
        "description": "Close-up of coffee cup with steam",
        "aspect_ratio": "1:1",
        "style": "cozy_cafe"
      }
    ],
    "seo_score": 85,
    "engagement_prediction": "high"
  },
  "metadata": {
    "processing_time": 2.3,
    "ai_model": "gemini-pro",
    "tokens_used": 450
  }
}
```

#### Generate Instagram Story

Create an interactive Instagram Story with multiple slides and stickers.

```http
POST /stories/generate
```

**Request Body:**
```json
{
  "topic": "Behind the scenes at our bakery",
  "slides_count": 5,
  "interactive_elements": ["poll", "question", "countdown"],
  "music_mood": "upbeat",
  "brand_colors": ["#8B4513", "#D2691E", "#F4A460"],
  "call_to_action": "Visit our bakery today!"
}
```

#### Generate Instagram Reel

Create a short-form video Reel with optimized script and style.

```http
POST /reels/generate
```

**Request Body:**
```json
{
  "topic": "Quick healthy smoothie recipe",
  "duration": "30_seconds",
  "style": "educational",
  "music_genre": "upbeat_pop",
  "include_subtitles": true,
  "end_screen_cta": "Try this recipe at home!",
  "hashtags": ["#HealthyEating", "#SmoothieRecipe", "#QuickRecipes"]
}
```

### Copilot Integration

#### Start Copilot Conversation

Initialize a new Copilot conversation for Instagram content creation.

```http
POST /copilot/conversations
```

**Request Body:**
```json
{
  "context": "instagram_content_creation",
  "initial_message": "Help me create an Instagram post about my new product launch",
  "preferences": {
    "tone": "professional",
    "audience": "business_professionals",
    "content_types": ["feed_posts", "stories"]
  }
}
```

#### Send Copilot Message

Continue a Copilot conversation with follow-up messages.

```http
POST /copilot/conversations/{conversation_id}/messages
```

**Request Body:**
```json
{
  "message": "Make it more engaging for millennials",
  "context_data": {
    "current_post": "post_123456",
    "previous_suggestions": ["suggestion_1", "suggestion_2"]
  }
}
```

### Batch Operations

#### Generate Multiple Posts

Create multiple Instagram posts for a content series or campaign.

```http
POST /posts/batch
```

**Request Body:**
```json
{
  "posts": [
    {
      "topic": "Product launch teaser",
      "content_type": "feed_post",
      "scheduled_date": "2024-01-15T10:00:00Z"
    },
    {
      "topic": "Product features highlight",
      "content_type": "carousel",
      "scheduled_date": "2024-01-16T14:00:00Z"
    },
    {
      "topic": "Customer testimonials",
      "content_type": "stories",
      "scheduled_date": "2024-01-17T16:00:00Z"
    }
  ],
  "campaign_settings": {
    "theme": "product_launch",
    "consistent_hashtags": true,
    "brand_voice": "excited_and_professional"
  }
}
```

### Analytics & Optimization

#### Get Post Performance

Retrieve performance metrics for generated Instagram content.

```http
GET /posts/{post_id}/analytics
```

**Response:**
```json
{
  "post_id": "post_123456",
  "platform_metrics": {
    "instagram": {
      "likes": 245,
      "comments": 18,
      "shares": 12,
      "saves": 67,
      "reach": 3250,
      "impressions": 4100,
      "engagement_rate": 4.2
    }
  },
  "ai_insights": {
    "performance_score": 8.5,
    "optimization_suggestions": [
      "Consider posting similar content at 7 PM on weekdays",
      "This type of content performs 40% better with carousel format",
      "Hashtags #CoffeeLovers and #MorningCoffee drove significant engagement"
    ],
    "trend_analysis": "Coffee content engagement up 15% this week"
  }
}
```

#### Get Content Recommendations

Receive AI-powered recommendations for optimal Instagram content strategy.

```http
GET /recommendations/content
```

**Query Parameters:**
- `timeframe`: `week` | `month` | `quarter`
- `audience`: Target audience segment
- `content_type`: Type of content to optimize for

**Response:**
```json
{
  "recommendations": [
    {
      "type": "content_optimization",
      "title": "Increase Carousel Usage",
      "description": "Your carousel posts perform 35% better than single images",
      "action": "Create more multi-image posts",
      "expected_impact": "25-40% engagement increase"
    },
    {
      "type": "timing_optimization",
      "title": "Optimal Posting Times",
      "description": "Post between 11 AM - 1 PM and 7 PM - 9 PM for maximum reach",
      "current_performance": "Average reach: 2,500 per post",
      "potential_improvement": "40% reach increase"
    },
    {
      "type": "hashtag_strategy",
      "title": "Hashtag Performance",
      "description": "Focus on niche hashtags with 10K-100K posts for better engagement",
      "recommended_hashtags": ["#LocalCoffee", "#CoffeeCulture", "#MorningVibes"],
      "expected_improvement": "20% engagement boost"
    }
  ],
  "overall_score": 7.8,
  "improvement_potential": "+35% engagement"
}
```

### Image Generation

#### Generate Instagram Images

Create custom images optimized for Instagram formats and algorithms.

```http
POST /images/generate
```

**Request Body:**
```json
{
  "prompt": "A cozy coffee shop interior with warm lighting and vintage decor",
  "style": "instagram_aesthetic",
  "aspect_ratio": "1:1",
  "mood": "warm_and_inviting",
  "colors": ["#8B4513", "#D2691E", "#F4A460"],
  "instagram_optimized": true,
  "include_text_overlay": false
}
```

#### Edit Generated Images

Apply Instagram-specific edits and optimizations to images.

```http
POST /images/{image_id}/edit
```

**Request Body:**
```json
{
  "edits": [
    {
      "type": "crop",
      "aspect_ratio": "4:5",
      "position": "smart_crop"
    },
    {
      "type": "filter",
      "filter_name": "instagram_warm",
      "intensity": 0.7
    },
    {
      "type": "text_overlay",
      "text": "NOW OPEN!",
      "position": "bottom_center",
      "font": "instagram_sans",
      "color": "#FFFFFF"
    }
  ],
  "instagram_optimization": true
}
```

### Account Management

#### Connect Instagram Account

Link an Instagram business account for enhanced features.

```http
POST /accounts/connect
```

**Request Body:**
```json
{
  "platform": "instagram",
  "account_type": "business",
  "permissions": ["read_insights", "publish_content", "manage_comments"],
  "callback_url": "https://your-app.com/oauth/callback"
}
```

#### Get Account Information

Retrieve connected Instagram account details and capabilities.

```http
GET /accounts/{account_id}
```

**Response:**
```json
{
  "account_id": "acc_123456",
  "platform": "instagram",
  "username": "@cozycoffee_shop",
  "account_type": "business",
  "capabilities": {
    "can_publish": true,
    "can_read_insights": true,
    "can_manage_comments": true,
    "connected_date": "2024-01-10T08:00:00Z"
  },
  "insights_access": {
    "available": true,
    "metrics": ["reach", "impressions", "engagement", "follower_demographics"]
  }
}
```

## Error Handling

### Error Response Format

All API errors follow a consistent format:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The provided topic is too short. Please provide at least 10 characters.",
    "details": {
      "field": "topic",
      "provided_length": 5,
      "minimum_length": 10
    },
    "request_id": "req_1234567890",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

### Common Error Codes

| Error Code | HTTP Status | Description |
|------------|-------------|-------------|
| `VALIDATION_ERROR` | 400 | Invalid request parameters |
| `AUTHENTICATION_ERROR` | 401 | Invalid or missing API key |
| `RATE_LIMIT_EXCEEDED` | 429 | API rate limit exceeded |
| `INSUFFICIENT_CREDITS` | 402 | Account has insufficient credits |
| `CONTENT_POLICY_VIOLATION` | 400 | Content violates platform policies |
| `PLATFORM_ERROR` | 502 | Instagram API temporarily unavailable |
| `PROCESSING_ERROR` | 500 | Internal processing error |

## SDK Examples

### JavaScript/Node.js

```javascript
const AlwrityInstagram = require('alwrity-instagram-sdk');

const client = new AlwrityInstagram({
  apiKey: 'your-api-key'
});

// Generate a post
const post = await client.posts.generate({
  topic: 'New product launch',
  content_type: 'feed_post',
  tone: 'excited'
});

console.log('Generated post:', post.content.caption);
```

### Python

```python
from alwrity_instagram import InstagramClient

client = InstagramClient(api_key='your-api-key')

# Generate content with Copilot
conversation = client.copilot.start_conversation(
    context="instagram_content_creation",
    initial_message="Help me create a carousel post for my bakery"
)

response = client.copilot.send_message(
    conversation_id=conversation.id,
    message="Make it focus on our seasonal pastries"
)

print("Copilot suggestion:", response.suggestion)
```

### cURL Examples

#### Generate Instagram Post
```bash
curl -X POST "https://api.alwrity.com/v1/instagram/posts/generate" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Sustainable fashion tips",
    "content_type": "feed_post",
    "tone": "educational",
    "include_hashtags": true,
    "generate_image": true
  }'
```

#### Get Analytics
```bash
curl -X GET "https://api.alwrity.com/v1/instagram/posts/post_123456/analytics" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

## Webhooks

### Setup Webhooks

Receive real-time notifications for content processing and performance updates.

```http
POST /webhooks
```

**Request Body:**
```json
{
  "url": "https://your-app.com/webhooks/instagram",
  "events": [
    "content.generated",
    "content.published",
    "analytics.updated",
    "copilot.message"
  ],
  "secret": "your-webhook-secret"
}
```

### Webhook Events

#### Content Generated
```json
{
  "event": "content.generated",
  "id": "evt_123456",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "content_id": "post_123456",
    "content_type": "feed_post",
    "status": "completed",
    "content": {
      "caption": "Generated caption...",
      "hashtags": ["#hashtag1", "#hashtag2"],
      "image_url": "https://cdn.alwrity.com/images/img_789.jpg"
    }
  }
}
```

#### Analytics Updated
```json
{
  "event": "analytics.updated",
  "id": "evt_123457",
  "timestamp": "2024-01-15T12:00:00Z",
  "data": {
    "content_id": "post_123456",
    "platform": "instagram",
    "metrics": {
      "likes": 150,
      "comments": 8,
      "shares": 5,
      "reach": 2100,
      "engagement_rate": 3.8
    },
    "insights": {
      "performance_score": 8.2,
      "top_performing_hashtag": "#CoffeeLovers"
    }
  }
}
```

## Best Practices

### API Usage
- **Batch Requests**: Use batch endpoints for multiple content pieces
- **Rate Limiting**: Implement exponential backoff for rate limit errors
- **Error Handling**: Always handle API errors gracefully with retries
- **Caching**: Cache frequently used content and analytics data

### Content Optimization
- **Platform-Specific**: Tailor content for Instagram's algorithm and audience
- **Timing**: Use analytics to determine optimal posting times
- **Hashtags**: Research and use relevant hashtags for better reach
- **Engagement**: Monitor and respond to comments and messages

### Integration Patterns
- **Webhook Handling**: Implement proper webhook signature verification
- **Idempotency**: Use request IDs to prevent duplicate processing
- **Monitoring**: Track API usage and performance metrics
- **Security**: Store API keys securely and rotate regularly

## Support

### Getting Help
- **API Status**: Check current API status at [status.alwrity.com](https://status.alwrity.com)
- **Documentation**: Visit [docs.alwrity.com/instagram-api](https://docs.alwrity.com/features/instagram-editor/api-reference.md)
- **Support**: Contact developer support at [dev-support@alwrity.com](mailto:dev-support@alwrity.com)

### Rate Limit Increases
Contact sales for higher rate limits and enterprise features:
- **Email**: [sales@alwrity.com](mailto:sales@alwrity.com)
- **Phone**: 1-800-ALWRITY (toll-free in US/Canada)

---

*For additional examples and integration guides, visit our [Developer Portal](https://developers.alwrity.com/instagram-editor).*

[:octicons-arrow-right-24: Back to Overview](overview.md)
[:octicons-arrow-right-24: Getting Started Guide](getting-started.md)