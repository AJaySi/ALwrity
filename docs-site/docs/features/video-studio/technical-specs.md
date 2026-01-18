# Video Studio Technical Specifications

Comprehensive technical documentation for ALwrity Video Studio, including API endpoints, model specifications, performance characteristics, and integration details.

## API Architecture

### Core Endpoints

#### Video Generation
```typescript
POST /api/video-studio/generate
Content-Type: multipart/form-data

Parameters:
- method: "text-to-video" | "image-to-video" | "extend-video"
- prompt: string (required for text-to-video)
- duration: number (5-60 seconds)
- resolution: "480p" | "720p" | "1080p" | "4k"
- aspect_ratio: "16:9" | "9:16" | "1:1"
- quality: "draft" | "standard" | "premium"
- model: string (optional, auto-selected by default)
- source_file: File (required for image-to-video/extend-video)
```

#### Video Processing
```typescript
POST /api/video-studio/process
Content-Type: multipart/form-data

Parameters:
- operation: "edit" | "enhance" | "transform" | "optimize"
- source_file: File (required)
- settings: object (operation-specific parameters)
```

#### Task Management
```typescript
GET /api/video-studio/tasks/{task_id}/status
GET /api/video-studio/tasks/{task_id}/result
DELETE /api/video-studio/tasks/{task_id}
```

## AI Model Specifications

### Text-to-Video Models

#### Hunyuan Video (Primary)
- **Provider**: WaveSpeed AI
- **Model ID**: `wavespeed-ai/hunyuan-video-1.5/text-to-video`
- **Capabilities**:
  - Resolutions: 480p, 720p
  - Duration: 5-10 seconds
  - Pricing: $0.02-0.04/second
  - Processing: 30-120 seconds
- **Strengths**: Consistent quality, reliable motion, cost-effective
- **Use Cases**: General content, presentations, educational videos

#### LTX-2 Pro
- **Provider**: Lightricks
- **Model ID**: `lightricks/ltx-2-pro/text-to-video`
- **Capabilities**:
  - Resolutions: 720p, 1080p
  - Duration: 5-10 seconds
  - Pricing: $0.05-0.10/second
  - Processing: 60-180 seconds
- **Strengths**: Higher quality, better motion consistency
- **Use Cases**: Professional content, marketing videos, commercials

#### LTX-2 Fast
- **Provider**: Lightricks
- **Model ID**: `lightricks/ltx-2-fast/text-to-video`
- **Capabilities**:
  - Resolutions: 480p, 720p
  - Duration: 5 seconds
  - Pricing: $0.01-0.02/second
  - Processing: 15-45 seconds
- **Strengths**: Fast generation, cost-effective iteration
- **Use Cases**: Drafts, testing, quick concepts

### Image-to-Video Models

#### Kandinsky5 Pro
- **Provider**: WaveSpeed AI
- **Model ID**: `wavespeed-ai/kandinsky5-pro/image-to-video`
- **Capabilities**:
  - Input: 512x512 to 2048x2048 images
  - Duration: 5 seconds
  - Resolutions: 512p, 1024p
  - Pricing: $0.20-0.60/run
  - Processing: 45-120 seconds
- **Strengths**: Creative animation, artistic motion
- **Limitations**: Fixed 5-second duration

### Video Enhancement Models

#### FlashVSR (Upscaling)
- **Provider**: WaveSpeed AI
- **Model ID**: `wavespeed-ai/flashvsr`
- **Capabilities**:
  - Input: Any resolution video
  - Output: Up to 4K resolution
  - Processing: 5-15 seconds
  - Pricing: $0.05-0.15/minute
- **Strengths**: Fast processing, quality enhancement
- **Use Cases**: Resolution upgrade, quality improvement

#### Video Outpainter (Extension)
- **Provider**: WaveSpeed AI
- **Model ID**: `wavespeed.ai/video-outpainter`
- **Capabilities**:
  - Input: 2-5 second videos
  - Extension: Up to 10 additional seconds
  - Processing: 60-180 seconds
  - Pricing: $0.10-0.30/minute
- **Strengths**: Temporal consistency, seamless extension

## Performance Characteristics

### Processing Times

#### Text-to-Video Generation
| Quality Tier | Resolution | Duration | Processing Time | Cost Range |
|-------------|------------|----------|-----------------|------------|
| Draft | 480p | 5s | 15-45s | $0.01-0.02 |
| Standard | 720p | 10s | 60-120s | $0.02-0.05 |
| Premium | 1080p | 10s | 120-300s | $0.05-0.15 |

#### Image-to-Video Generation
| Model | Duration | Processing Time | Cost Range |
|-------|----------|-----------------|------------|
| Kandinsky5 Pro | 5s | 45-120s | $0.20-0.60 |

#### Video Enhancement
| Operation | Input Length | Processing Time | Cost Range |
|-----------|--------------|-----------------|------------|
| Upscaling | Any | 5-15s | $0.05-0.15/min |
| Extension | 2-5s | 60-180s | $0.10-0.30/min |

### Quality Tiers

#### Draft Quality
- **Purpose**: Testing concepts, quick iterations
- **Trade-offs**: Faster processing, lower quality
- **Best For**: Initial drafts, cost-conscious users

#### Standard Quality
- **Purpose**: Production content, social media
- **Balance**: Quality and speed optimization
- **Best For**: Marketing videos, professional content

#### Premium Quality
- **Purpose**: Broadcast, high-end production
- **Focus**: Maximum quality, slower processing
- **Best For**: Commercial use, premium content

## File Specifications

### Supported Formats

#### Input Formats
- **Video**: MP4, MOV, WebM, AVI
- **Image**: JPG, PNG, WebP
- **Audio**: MP3, WAV, M4A (for audio integration)

#### Output Formats
- **Primary**: MP4 (H.264/AAC)
- **Additional**: WebM, MOV (on request)
- **Streaming**: HLS, DASH (enterprise)

### File Size Limits

#### Free Tier
- **Upload**: 100MB per file
- **Generation**: 500MB total storage
- **Download**: Unlimited (rate limited)

#### Pro Tier
- **Upload**: 500MB per file
- **Generation**: 5GB total storage
- **Download**: Unlimited (higher rate limits)

#### Enterprise Tier
- **Upload**: 2GB per file
- **Generation**: Unlimited storage
- **Download**: Unlimited (maximum rate limits)

### Resolution Specifications

#### Input Resolutions
- **Minimum**: 480x270 (270p)
- **Recommended**: 1920x1080 (1080p)
- **Maximum**: 4096x2160 (4K)

#### Output Resolutions
- **Available**: 480p, 720p, 1080p, 1440p, 2160p (4K)
- **Aspect Ratios**: 16:9, 9:16, 1:1, 4:5, 21:9

## Cost Structure

### Pricing Model

#### Per-Second Pricing
- **Base Rate**: $0.01-0.30 per second of output video
- **Factors**: Model complexity, resolution, quality tier
- **Discounts**: Bulk processing, subscription tiers

#### Per-Operation Pricing
- **Fixed Cost**: $0.05-2.00 per operation
- **Examples**: Face swap, style transfer, format conversion
- **Volume Discounts**: Reduced rates for high-volume users

### Cost Estimation API

```typescript
POST /api/video-studio/estimate-cost
Content-Type: application/json

Body: {
  "method": "text-to-video",
  "duration": 30,
  "resolution": "1080p",
  "quality": "standard",
  "model": "hunyuan-video"
}

Response: {
  "estimated_cost": 0.75,
  "currency": "USD",
  "processing_time_estimate": 180,
  "confidence": "high"
}
```

## Error Handling

### Common Error Codes

#### Validation Errors (400)
- `INVALID_PROMPT`: Prompt too short or contains prohibited content
- `UNSUPPORTED_FORMAT`: File format not supported
- `FILE_TOO_LARGE`: File exceeds size limits
- `INVALID_RESOLUTION`: Resolution not supported by selected model

#### Processing Errors (500)
- `MODEL_UNAVAILABLE`: AI model temporarily unavailable
- `PROCESSING_TIMEOUT`: Generation exceeded time limits
- `INSUFFICIENT_CREDITS`: Account balance insufficient
- `RATE_LIMIT_EXCEEDED`: Too many requests in time window

#### Delivery Errors (502)
- `STORAGE_FULL`: User storage quota exceeded
- `DELIVERY_FAILED`: File delivery failed
- `CORRUPTION_DETECTED`: Generated file corrupted

### Retry Logic

#### Automatic Retries
- **Network Issues**: Up to 3 retries with exponential backoff
- **Temporary Failures**: Retry after 30-300 seconds
- **Model Busy**: Queue and retry when available

#### Manual Intervention
- **Content Policy**: Manual review required
- **Technical Issues**: Contact support for resolution
- **Credit Issues**: Resolve billing before retry

## Security & Compliance

### Data Protection
- **Encryption**: All files encrypted at rest and in transit
- **Access Control**: User-scoped file access
- **Audit Logging**: Complete activity tracking
- **Data Retention**: Configurable retention policies

### Content Safety
- **Automated Filtering**: AI-powered content moderation
- **Prohibited Content**: Block harmful, illegal, or inappropriate content
- **User Reporting**: Report inappropriate generated content
- **Moderation Queue**: Human review for edge cases

### Compliance Standards
- **GDPR**: EU data protection compliance
- **SOC 2**: Security and privacy controls
- **COPPA**: Children's privacy protection
- **DMCA**: Copyright protection measures

## Integration Options

### REST API
```typescript
// Generate video
const response = await fetch('/api/video-studio/generate', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${token}` },
  body: formData
});

// Check status
const status = await fetch(`/api/video-studio/tasks/${taskId}/status`);

// Download result
const result = await fetch(`/api/video-studio/tasks/${taskId}/result`);
```

### Webhooks
```typescript
// Register webhook
POST /api/video-studio/webhooks
{
  "url": "https://your-app.com/webhook",
  "events": ["task.completed", "task.failed"],
  "secret": "your-webhook-secret"
}

// Webhook payload
{
  "event": "task.completed",
  "task_id": "task_123",
  "user_id": "user_456",
  "result_url": "https://cdn.alwrity.com/videos/task_123.mp4",
  "metadata": { ... }
}
```

### SDK Options
- **JavaScript SDK**: npm install @alwrity/video-studio
- **Python SDK**: pip install alwrity-video-studio
- **PHP SDK**: composer require alwrity/video-studio

## Monitoring & Analytics

### Usage Metrics
- **Generation Volume**: Videos created per time period
- **Processing Time**: Average completion times
- **Success Rate**: Percentage of successful generations
- **Cost Tracking**: Spending by model and operation

### Performance Monitoring
- **API Latency**: Response times for all endpoints
- **Error Rates**: Failure rates by operation type
- **Queue Depth**: Current processing backlog
- **Resource Usage**: Server utilization and scaling metrics

### Business Intelligence
- **User Behavior**: Feature usage patterns
- **Content Trends**: Popular models and use cases
- **Quality Metrics**: User satisfaction and ratings
- **ROI Tracking**: Cost vs. business value generated

---

*For API documentation and integration guides, visit our [Developer Portal](https://developers.alwrity.com/video-studio).*

[:octicons-arrow-right-24: Back to Overview](overview.md)
[:octicons-arrow-right-24: Create Studio Guide](create-studio.md)