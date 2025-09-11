# Stability AI Integration Documentation

This document provides comprehensive documentation for the Stability AI integration in the ALwrity backend.

## Overview

The Stability AI integration provides access to all major Stability AI services including:

- **Image Generation**: Ultra, Core, and SD3.5 models
- **Image Editing**: Erase, Inpaint, Outpaint, Search & Replace, Search & Recolor, Background Removal
- **Image Upscaling**: Fast, Conservative, and Creative upscaling
- **Image Control**: Sketch, Structure, Style, and Style Transfer control
- **3D Generation**: Fast 3D and Point-Aware 3D model generation
- **Audio Generation**: Text-to-Audio, Audio-to-Audio, and Audio Inpainting
- **Legacy V1 APIs**: SDXL 1.0 and other V1 engines

## Architecture

### Modular Structure

```
backend/
├── models/
│   └── stability_models.py          # Pydantic models for all API schemas
├── services/
│   └── stability_service.py         # Core service class with HTTP client
├── routers/
│   ├── stability.py                 # Main API endpoints
│   ├── stability_advanced.py        # Advanced workflows and features
│   └── stability_admin.py           # Admin and monitoring endpoints
├── middleware/
│   └── stability_middleware.py      # Rate limiting, caching, monitoring
├── utils/
│   └── stability_utils.py           # Utility functions and validators
├── config/
│   └── stability_config.py          # Configuration and constants
└── test/
    └── test_stability_endpoints.py  # Comprehensive test suite
```

### Key Components

1. **StabilityAIService**: Core service class handling all API interactions
2. **Pydantic Models**: Comprehensive request/response models with validation
3. **FastAPI Routers**: Organized endpoints for different service categories
4. **Middleware**: Rate limiting, caching, monitoring, and content moderation
5. **Utilities**: File handling, validation, optimization, and workflow management

## API Endpoints

### Generation Endpoints

#### POST `/api/stability/generate/ultra`
Generate high-quality images using Stable Image Ultra.

**Parameters:**
- `prompt` (required): Text description of desired image
- `image` (optional): Input image for image-to-image generation
- `negative_prompt` (optional): What you don't want to see
- `aspect_ratio` (optional): Image aspect ratio (default: "1:1")
- `seed` (optional): Random seed (0-4294967294)
- `output_format` (optional): Output format (jpeg, png, webp)
- `style_preset` (optional): Style preset
- `strength` (optional): Image influence strength (required if image provided)

**Response:** Image bytes or JSON with generation ID

**Cost:** 8 credits per generation

#### POST `/api/stability/generate/core`
Fast and affordable image generation.

**Parameters:**
- `prompt` (required): Text description
- `negative_prompt` (optional): Negative prompt
- `aspect_ratio` (optional): Image aspect ratio
- `seed` (optional): Random seed
- `output_format` (optional): Output format
- `style_preset` (optional): Style preset

**Cost:** 3 credits per generation

#### POST `/api/stability/generate/sd3`
Generate using Stable Diffusion 3.5 models.

**Parameters:**
- `prompt` (required): Text description
- `mode` (optional): "text-to-image" or "image-to-image"
- `image` (optional): Input image (required for image-to-image)
- `strength` (optional): Image influence (required for image-to-image)
- `aspect_ratio` (optional): Image aspect ratio (text-to-image only)
- `model` (optional): SD3 model variant
- `cfg_scale` (optional): CFG scale (1-10)

**Cost:** 2.5-6.5 credits depending on model

### Edit Endpoints

#### POST `/api/stability/edit/erase`
Remove unwanted objects using masks.

**Parameters:**
- `image` (required): Image file to edit
- `mask` (optional): Mask image (or use alpha channel)
- `grow_mask` (optional): Mask edge growth (0-20 pixels)
- `seed` (optional): Random seed
- `output_format` (optional): Output format

**Cost:** 5 credits per generation

#### POST `/api/stability/edit/inpaint`
Fill or replace specified areas with new content.

**Parameters:**
- `image` (required): Image file to edit
- `prompt` (required): Description of desired content
- `mask` (optional): Mask image
- `negative_prompt` (optional): Negative prompt
- `grow_mask` (optional): Mask edge growth (0-100 pixels)
- `style_preset` (optional): Style preset

**Cost:** 5 credits per generation

#### POST `/api/stability/edit/outpaint`
Expand image in specified directions.

**Parameters:**
- `image` (required): Image file to expand
- `left` (optional): Pixels to expand left (0-2000)
- `right` (optional): Pixels to expand right (0-2000)
- `up` (optional): Pixels to expand up (0-2000)
- `down` (optional): Pixels to expand down (0-2000)
- `creativity` (optional): Creativity level (0-1)
- `prompt` (optional): Guidance prompt

**Note:** At least one direction must be specified.

**Cost:** 4 credits per generation

#### POST `/api/stability/edit/search-and-replace`
Replace objects using text prompts instead of masks.

**Parameters:**
- `image` (required): Image file to edit
- `prompt` (required): Description of replacement
- `search_prompt` (required): What to search for
- `grow_mask` (optional): Mask edge growth (0-20 pixels)

**Cost:** 5 credits per generation

#### POST `/api/stability/edit/search-and-recolor`
Change colors of specific objects using prompts.

**Parameters:**
- `image` (required): Image file to edit
- `prompt` (required): Description of new colors
- `select_prompt` (required): What to select for recoloring

**Cost:** 5 credits per generation

#### POST `/api/stability/edit/remove-background`
Remove background from images.

**Parameters:**
- `image` (required): Image file
- `output_format` (optional): Output format (png, webp)

**Cost:** 5 credits per generation

### Upscale Endpoints

#### POST `/api/stability/upscale/fast`
Fast 4x upscaling (~1 second processing).

**Parameters:**
- `image` (required): Image file to upscale
- `output_format` (optional): Output format

**Cost:** 2 credits per generation

#### POST `/api/stability/upscale/conservative`
Conservative upscaling to 4K with minimal changes.

**Parameters:**
- `image` (required): Image file to upscale
- `prompt` (required): Description for guidance
- `creativity` (optional): Creativity level (0.2-0.5)

**Cost:** 40 credits per generation

#### POST `/api/stability/upscale/creative`
Creative upscaling for highly degraded images (async).

**Parameters:**
- `image` (required): Image file to upscale
- `prompt` (required): Description for guidance
- `creativity` (optional): Creativity level (0.1-0.5)
- `style_preset` (optional): Style preset

**Cost:** 60 credits per generation

### Control Endpoints

#### POST `/api/stability/control/sketch`
Generate refined images from sketches.

**Parameters:**
- `image` (required): Sketch or line art
- `prompt` (required): Description of desired result
- `control_strength` (optional): Control strength (0-1)

**Cost:** 5 credits per generation

#### POST `/api/stability/control/structure`
Maintain structure while changing content.

**Parameters:**
- `image` (required): Structure reference image
- `prompt` (required): Description of desired result
- `control_strength` (optional): Control strength (0-1)

**Cost:** 5 credits per generation

#### POST `/api/stability/control/style`
Extract and apply style from reference image.

**Parameters:**
- `image` (required): Style reference image
- `prompt` (required): Description of desired result
- `aspect_ratio` (optional): Output aspect ratio
- `fidelity` (optional): Style fidelity (0-1)

**Cost:** 5 credits per generation

#### POST `/api/stability/control/style-transfer`
Transfer style between two images.

**Parameters:**
- `init_image` (required): Image to restyle
- `style_image` (required): Style reference
- `style_strength` (optional): Style strength (0-1)
- `composition_fidelity` (optional): Composition preservation (0-1)

**Cost:** 8 credits per generation

### 3D Endpoints

#### POST `/api/stability/3d/stable-fast-3d`
Generate 3D models from 2D images (fast).

**Parameters:**
- `image` (required): 2D image to convert
- `texture_resolution` (optional): Texture resolution (512, 1024, 2048)
- `foreground_ratio` (optional): Object size ratio (0.1-1)
- `remesh` (optional): Remesh algorithm (none, triangle, quad)

**Output:** GLB 3D model file

**Cost:** 10 credits per generation

#### POST `/api/stability/3d/stable-point-aware-3d`
Advanced 3D generation with editing capabilities.

**Parameters:**
- `image` (required): 2D image to convert
- `texture_resolution` (optional): Texture resolution
- `foreground_ratio` (optional): Object size ratio (1-2)
- `target_type` (optional): Simplification target (none, vertex, face)
- `guidance_scale` (optional): Guidance scale (1-10)

**Cost:** 4 credits per generation

### Audio Endpoints

#### POST `/api/stability/audio/text-to-audio`
Generate audio from text descriptions.

**Parameters:**
- `prompt` (required): Audio description
- `duration` (optional): Duration in seconds (1-190)
- `model` (optional): Audio model (stable-audio-2, stable-audio-2.5)
- `steps` (optional): Sampling steps (model-dependent)
- `cfg_scale` (optional): CFG scale (1-25)

**Cost:** 20 credits per generation

#### POST `/api/stability/audio/audio-to-audio`
Transform audio using text instructions.

**Parameters:**
- `prompt` (required): Transformation description
- `audio` (required): Input audio file
- `duration` (optional): Output duration (1-190)
- `strength` (optional): Input influence (0-1)

**Cost:** 20 credits per generation

### Results Endpoint

#### GET `/api/stability/results/{generation_id}`
Get results from async generations.

**Parameters:**
- `generation_id` (required): ID from async operation
- `accept_type` (optional): Response format preference

**Response:** Generated content or status update

## Advanced Features

### Workflow Processing

The integration supports complex multi-step workflows:

```python
# Example workflow
workflow = [
    {"operation": "generate_core", "parameters": {"prompt": "a landscape"}},
    {"operation": "upscale_fast", "parameters": {}},
    {"operation": "inpaint", "parameters": {"prompt": "add a house"}}
]
```

### Batch Processing

Process multiple images with the same operation:

```python
POST /api/stability/advanced/batch/process-folder
```

### Model Comparison

Compare results across different models:

```python
POST /api/stability/advanced/compare/models
```

### AI Director Mode

Automated creative decision making:

```python
POST /api/stability/advanced/experimental/ai-director
```

## Configuration

### Environment Variables

```bash
STABILITY_API_KEY=your_api_key_here
STABILITY_BASE_URL=https://api.stability.ai  # Optional
STABILITY_TIMEOUT=300                         # Optional
STABILITY_MAX_RETRIES=3                      # Optional
STABILITY_MAX_FILE_SIZE=10485760             # Optional (10MB)
```

### Rate Limiting

- **Default Limit**: 150 requests per 10 seconds
- **Timeout**: 60 seconds when limit exceeded
- **Configurable**: Can be adjusted in middleware

### File Size Limits

- **Images**: 10MB maximum
- **Audio**: 50MB maximum
- **3D Models**: 10MB maximum

### Image Requirements

#### Generate Operations
- **Minimum**: 4,096 pixels total
- **Maximum**: 16,777,216 pixels total (16MP)
- **Dimensions**: At least 64x64 pixels

#### Edit Operations
- **Minimum**: 4,096 pixels total
- **Maximum**: 9,437,184 pixels total (~9.4MP)
- **Aspect Ratio**: Between 1:2.5 and 2.5:1

#### Upscale Operations
- **Fast**: 1,024 to 1,048,576 pixels, 32-1536px dimensions
- **Conservative**: 4,096 to 9,437,184 pixels
- **Creative**: 4,096 to 1,048,576 pixels

## Usage Examples

### Basic Text-to-Image Generation

```python
import requests

response = requests.post(
    "http://localhost:8000/api/stability/generate/ultra",
    data={
        "prompt": "A majestic mountain landscape at sunset",
        "aspect_ratio": "16:9",
        "style_preset": "photographic"
    }
)

if response.status_code == 200:
    with open("generated_image.png", "wb") as f:
        f.write(response.content)
```

### Image Editing with Inpainting

```python
files = {
    "image": open("input.png", "rb"),
    "mask": open("mask.png", "rb")
}

data = {
    "prompt": "a beautiful garden",
    "grow_mask": 10
}

response = requests.post(
    "http://localhost:8000/api/stability/edit/inpaint",
    files=files,
    data=data
)
```

### Audio Generation

```python
response = requests.post(
    "http://localhost:8000/api/stability/audio/text-to-audio",
    data={
        "prompt": "Peaceful piano music with nature sounds",
        "duration": 60,
        "model": "stable-audio-2.5"
    }
)

if response.status_code == 200:
    with open("generated_audio.mp3", "wb") as f:
        f.write(response.content)
```

### 3D Model Generation

```python
files = {"image": open("object.png", "rb")}

response = requests.post(
    "http://localhost:8000/api/stability/3d/stable-fast-3d",
    files=files,
    data={
        "texture_resolution": "1024",
        "foreground_ratio": 0.85
    }
)

if response.status_code == 200:
    with open("model.glb", "wb") as f:
        f.write(response.content)
```

## Error Handling

The API provides comprehensive error handling:

### Common Error Codes

- **400**: Invalid parameters or file format
- **403**: Content moderation flag or insufficient permissions
- **413**: File too large
- **422**: Request well-formed but rejected
- **429**: Rate limit exceeded
- **500**: Internal server error

### Error Response Format

```json
{
    "id": "error_id",
    "name": "error_name",
    "errors": ["Detailed error messages"]
}
```

## Monitoring and Analytics

### Health Check Endpoints

- `GET /api/stability/health` - Basic health check
- `GET /api/stability/admin/health/detailed` - Comprehensive health check

### Statistics Endpoints

- `GET /api/stability/admin/stats` - Service statistics
- `GET /api/stability/admin/usage/summary` - Usage summary
- `GET /api/stability/admin/request-logs` - Request logs

### Cost Estimation

- `GET /api/stability/admin/costs/estimate` - Estimate operation costs

## Best Practices

### Prompt Optimization

1. **Be Specific**: Use detailed, descriptive language
2. **Include Style**: Specify artistic style or photographic type
3. **Add Quality Terms**: Include "high quality", "detailed", "sharp"
4. **Use Negative Prompts**: Specify what you don't want

### Image Preparation

1. **Check Dimensions**: Ensure images meet size requirements
2. **Optimize File Size**: Compress large images before upload
3. **Use Appropriate Formats**: PNG for transparency, JPEG for photos
4. **Validate Aspect Ratios**: Check ratio requirements for operations

### Performance Optimization

1. **Use Appropriate Models**: Choose model based on speed vs quality needs
2. **Batch Operations**: Use batch endpoints for multiple similar operations
3. **Cache Results**: Enable caching for repeated operations
4. **Monitor Usage**: Track credit usage and optimize accordingly

## Security Considerations

### API Key Management

- Store API keys securely in environment variables
- Never commit API keys to version control
- Rotate keys regularly
- Monitor key usage for unauthorized access

### Content Moderation

- Built-in content moderation middleware
- Configurable blocked terms
- Automatic flagging of inappropriate content
- Audit logging for compliance

### Rate Limiting

- Automatic rate limiting per client
- Configurable limits and timeouts
- IP-based and API key-based limiting
- Graceful handling of limit exceeded scenarios

## Troubleshooting

### Common Issues

#### "API key missing or invalid"
- Check STABILITY_API_KEY environment variable
- Verify key is correct and active
- Check account balance

#### "Rate limit exceeded"
- Wait for timeout period (60 seconds)
- Implement request queuing
- Consider upgrading API plan

#### "File too large"
- Compress images before upload
- Check file size limits for operation
- Use appropriate image formats

#### "Invalid image dimensions"
- Check minimum/maximum pixel requirements
- Validate aspect ratio constraints
- Resize image if necessary

### Debug Endpoints

- `POST /api/stability/admin/debug/test-connection` - Test API connectivity
- `GET /api/stability/admin/debug/request-logs` - View recent requests
- `POST /api/stability/utils/image-info` - Analyze image properties

## Integration Examples

### React Frontend Integration

```javascript
// Upload and generate
const formData = new FormData();
formData.append('prompt', 'A beautiful landscape');
formData.append('aspect_ratio', '16:9');

const response = await fetch('/api/stability/generate/ultra', {
    method: 'POST',
    body: formData
});

if (response.ok) {
    const blob = await response.blob();
    const imageUrl = URL.createObjectURL(blob);
    // Display image
}
```

### Python Service Integration

```python
from services.stability_service import StabilityAIService

async def generate_content_images(prompts: List[str]):
    service = StabilityAIService()
    
    async with service:
        results = []
        for prompt in prompts:
            result = await service.generate_core(
                prompt=prompt,
                aspect_ratio="16:9"
            )
            results.append(result)
    
    return results
```

## Performance Metrics

### Typical Response Times

- **Fast Operations** (Fast Upscale): ~1-2 seconds
- **Standard Operations** (Core Generation): ~5-10 seconds
- **Complex Operations** (Ultra Generation): ~10-20 seconds
- **Heavy Operations** (Creative Upscale): ~30-60 seconds

### Throughput

- **Rate Limit**: 150 requests per 10 seconds
- **Concurrent Requests**: Limited by API key
- **Batch Processing**: Recommended for multiple operations

## Future Enhancements

### Planned Features

1. **Advanced Caching**: Redis-based caching for better performance
2. **Queue Management**: Async job queue for heavy operations
3. **Result Storage**: Persistent storage for generated content
4. **Analytics Dashboard**: Real-time usage analytics
5. **Custom Workflows**: Visual workflow builder
6. **A/B Testing**: Compare different approaches automatically

### API Extensions

1. **Webhook Support**: Real-time notifications for async operations
2. **Streaming Responses**: Progressive image generation updates
3. **Template System**: Predefined generation templates
4. **Collaboration Features**: Shared workspaces and results

## Support

For issues and questions:

1. Check the troubleshooting section above
2. Review the test suite for usage examples
3. Check Stability AI documentation: https://platform.stability.ai/docs
4. Contact support through the admin panel

## Version History

- **v1.0.0**: Initial implementation with all major Stability AI features
  - Complete API coverage for v2beta endpoints
  - Legacy v1 API support
  - Comprehensive middleware and utilities
  - Full test suite and documentation