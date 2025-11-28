# Create Studio User Guide

Create Studio enables you to generate high-quality images from text prompts using multiple AI providers. This guide covers everything you need to know to create stunning visuals for your marketing campaigns.

## Overview

Create Studio is your primary tool for AI-powered image generation. It supports multiple providers, platform templates, style presets, and batch generation to help you create professional visuals quickly and efficiently.

### Key Features
- **Multi-Provider AI**: Access to Stability AI, WaveSpeed, HuggingFace, and Gemini
- **Platform Templates**: Pre-configured templates for Instagram, LinkedIn, Facebook, and more
- **Style Presets**: 40+ built-in styles for different visual aesthetics
- **Batch Generation**: Create 1-10 variations in a single request
- **Cost Estimation**: See costs before generating
- **Prompt Enhancement**: AI-powered prompt improvement

## Getting Started

### Accessing Create Studio

1. Navigate to **Image Studio** from the main dashboard
2. Click on **Create Studio** or go directly to `/image-generator`
3. You'll see the Create Studio interface with prompt input and controls

### Basic Workflow

1. **Enter Your Prompt**: Describe the image you want to create
2. **Select Template** (optional): Choose a platform template for automatic sizing
3. **Choose Quality Level**: Select Draft, Standard, or Premium
4. **Generate**: Click the generate button and wait for results
5. **Review & Download**: View results and download your favorites

## Provider Selection

Create Studio supports multiple AI providers, each with different strengths:

### Stability AI

**Models Available**:
- **Ultra**: Highest quality (8 credits) - Best for premium content
- **Core**: Fast and affordable (3 credits) - Best for standard content
- **SD3.5**: Advanced Stable Diffusion 3.5 (varies) - Best for artistic content

**Best For**:
- Professional photography style
- Detailed artistic images
- High-quality marketing materials
- When you need maximum control

### WaveSpeed Ideogram V3

**Model**: `ideogram-v3-turbo`

**Best For**:
- Photorealistic images
- Images with text (superior text rendering)
- Social media content
- Premium quality visuals

**Advantages**:
- Excellent text rendering in images
- Photorealistic quality
- Fast generation

### WaveSpeed Qwen

**Model**: `qwen-image`

**Best For**:
- Quick iterations
- High-volume content
- Draft generation
- Cost-effective production

**Advantages**:
- Ultra-fast generation (2-3 seconds)
- Low cost
- Good quality for quick previews

### HuggingFace FLUX

**Model**: `black-forest-labs/FLUX.1-Krea-dev`

**Best For**:
- Diverse artistic styles
- Experimental content
- Free tier usage
- Creative variations

### Gemini Imagen

**Model**: `imagen-3.0-generate-001`

**Best For**:
- Google ecosystem integration
- General purpose generation
- Free tier usage

### Auto Selection

When set to "Auto", Create Studio automatically selects the best provider based on:
- **Quality Level**: Draft → Qwen/HuggingFace, Standard → Core/Ideogram, Premium → Ideogram/Ultra
- **Template Recommendations**: Templates can suggest specific providers
- **User Preferences**: Your previous selections

## Platform Templates

Templates automatically configure dimensions, aspect ratios, and provider settings for specific platforms.

### Available Templates

#### Instagram (4 templates)
- **Feed Post (Square)**: 1080x1080 (1:1) - Standard Instagram posts
- **Feed Post (Portrait)**: 1080x1350 (4:5) - Vertical posts
- **Story**: 1080x1920 (9:16) - Instagram Stories
- **Reel Cover**: 1080x1920 (9:16) - Reel thumbnails

#### LinkedIn (4 templates)
- **Post**: 1200x628 (1.91:1) - Standard LinkedIn posts
- **Post (Square)**: 1080x1080 (1:1) - Square posts
- **Article**: 1200x627 (2:1) - Article cover images
- **Company Cover**: 1128x191 (4:1) - Company page banners

#### Facebook (4 templates)
- **Feed Post**: 1200x630 (1.91:1) - Standard feed posts
- **Feed Post (Square)**: 1080x1080 (1:1) - Square posts
- **Story**: 1080x1920 (9:16) - Facebook Stories
- **Cover Photo**: 820x312 (16:9) - Page cover photos

#### Twitter/X (3 templates)
- **Post**: 1200x675 (16:9) - Standard tweets
- **Card**: 1200x600 (2:1) - Twitter cards
- **Header**: 1500x500 (3:1) - Profile headers

#### Other Platforms
- **YouTube**: Thumbnails, Channel Art
- **Pinterest**: Pins, Story Pins
- **TikTok**: Video thumbnails
- **Blog**: Featured images, Headers
- **Email**: Banners, Product images
- **Website**: Hero images, Banners

### Using Templates

1. **Click Template Selector**: Open the template selection panel
2. **Filter by Platform**: Select a platform to see relevant templates
3. **Search Templates**: Use the search bar to find specific templates
4. **Select Template**: Click on a template to apply it
5. **Auto-Configuration**: Dimensions, aspect ratio, and provider are automatically set

### Template Benefits

- **Automatic Sizing**: No need to calculate dimensions manually
- **Platform Optimization**: Optimized for each platform's requirements
- **Provider Recommendations**: Templates suggest the best provider
- **Style Guidance**: Templates include style recommendations

## Quality Levels

Create Studio offers three quality levels that balance speed, cost, and quality:

### Draft
- **Speed**: Fastest (2-5 seconds)
- **Cost**: Lowest (1-2 credits)
- **Providers**: Qwen, HuggingFace
- **Use Case**: Quick previews, iterations, high-volume content

### Standard
- **Speed**: Medium (5-15 seconds)
- **Cost**: Moderate (3-5 credits)
- **Providers**: Stability Core, Ideogram V3
- **Use Case**: Most marketing content, social media posts

### Premium
- **Speed**: Slower (15-30 seconds)
- **Cost**: Highest (6-8 credits)
- **Providers**: Ideogram V3, Stability Ultra
- **Use Case**: Premium campaigns, print materials, featured content

## Writing Effective Prompts

### Prompt Structure

A good prompt includes:
1. **Subject**: What you want to see
2. **Style**: Visual style or aesthetic
3. **Details**: Specific elements, colors, mood
4. **Quality Descriptors**: Professional, high quality, detailed

### Example Prompts

**Basic**:
```
Modern minimalist workspace with laptop
```

**Enhanced**:
```
Modern minimalist workspace with laptop, natural lighting, professional photography, high quality, detailed, clean background
```

**Style-Specific**:
```
Futuristic cityscape at sunset, cinematic lighting, dramatic clouds, 4K quality, professional photography
```

### Prompt Enhancement

Create Studio can automatically enhance your prompts:
- **Enable Prompt Enhancement**: Toggle on in advanced options
- **Style Integration**: Automatically adds style-specific descriptors
- **Quality Boosters**: Adds quality and detail descriptors

### Negative Prompts

Use negative prompts to exclude unwanted elements:
- **Common Exclusions**: "blurry, low quality, distorted, watermark"
- **Style Exclusions**: "cartoon, illustration" (if you want photography)
- **Content Exclusions**: "text, logo, watermark"

## Advanced Options

### Provider Settings

**Manual Provider Selection**:
- Override auto-selection
- Choose specific provider and model
- Useful for testing or specific requirements

**Model Selection**:
- Select specific model within a provider
- Useful for fine-tuning results

### Generation Parameters

**Guidance Scale** (Provider-specific):
- Controls how closely the image follows the prompt
- Higher = more adherence to prompt
- Typical range: 4-10

**Steps** (Provider-specific):
- Number of inference steps
- Higher = better quality but slower
- Typical range: 20-50

**Seed**:
- Random seed for reproducibility
- Same seed + same prompt = same result
- Useful for variations and consistency

### Style Presets

Available style presets:
- **Photographic**: Professional photography style
- **Digital Art**: Digital art, vibrant colors
- **Cinematic**: Film-like, dramatic lighting
- **3D Model**: 3D render style
- **Anime**: Anime/manga style
- **Line Art**: Clean line art

## Batch Generation

Create multiple variations in one request:

### How to Use

1. **Set Variations**: Use the slider to select 1-10 variations
2. **Generate**: All variations are created in one request
3. **Review**: Compare all variations side-by-side
4. **Select**: Choose your favorites

### Use Cases

- **A/B Testing**: Generate multiple options for testing
- **Content Libraries**: Build collections quickly
- **Iterations**: Explore different interpretations
- **Time Saving**: Generate multiple images at once

### Cost Considerations

- Each variation consumes credits
- Batch generation is more cost-effective than individual requests
- Cost is displayed before generation

## Cost Estimation

### Pre-Flight Validation

Before generating, Create Studio shows:
- **Estimated Cost**: Credits required
- **Subscription Check**: Validates your subscription tier
- **Credit Balance**: Shows available credits

### Cost Factors

- **Provider**: Different providers have different costs
- **Quality Level**: Premium costs more than Draft
- **Dimensions**: Larger images may cost more
- **Variations**: Each variation adds to the cost

### Cost Optimization Tips

1. **Use Draft for Iterations**: Test ideas with low-cost Draft quality
2. **Batch Efficiently**: Generate multiple variations in one request
3. **Choose Appropriate Quality**: Don't use Premium for quick previews
4. **Template Optimization**: Templates optimize for cost-effectiveness

## Best Practices

### For Social Media

1. **Use Templates**: Templates ensure correct dimensions
2. **Standard Quality**: Usually sufficient for social media
3. **Batch Generate**: Create multiple options for A/B testing
4. **Text Considerations**: Use Ideogram V3 if you need text in images

### For Marketing Materials

1. **Premium Quality**: Use for important campaigns
2. **Detailed Prompts**: Include specific details about brand, style, mood
3. **Negative Prompts**: Exclude unwanted elements
4. **Consistent Seeds**: Use seeds for brand consistency

### For Content Libraries

1. **Batch Generation**: Generate multiple variations efficiently
2. **Draft First**: Test concepts with Draft quality
3. **Template Variety**: Use different templates for diversity
4. **Organize Results**: Save favorites to Asset Library

### Prompt Writing Tips

1. **Be Specific**: Include details about style, mood, composition
2. **Use Quality Descriptors**: "high quality", "professional", "detailed"
3. **Include Lighting**: "natural lighting", "dramatic lighting", "soft lighting"
4. **Specify Style**: "photographic", "cinematic", "minimalist"
5. **Avoid Ambiguity**: Clear, specific descriptions work best

## Troubleshooting

### Common Issues

**Low Quality Results**:
- Try Premium quality level
- Use a different provider (try Ideogram V3 or Stability Ultra)
- Enhance your prompt with quality descriptors
- Increase guidance scale or steps

**Images Don't Match Prompt**:
- Be more specific in your prompt
- Use negative prompts to exclude unwanted elements
- Try a different provider
- Adjust guidance scale

**Slow Generation**:
- Use Draft quality for faster results
- Try Qwen or HuggingFace providers
- Reduce image dimensions
- Check your internet connection

**High Costs**:
- Use Draft quality for iterations
- Reduce number of variations
- Choose cost-effective providers (Qwen, HuggingFace)
- Use templates for optimization

### Getting Help

- Check the [Providers Guide](providers.md) for provider-specific tips
- Review the [Cost Guide](cost-guide.md) for cost optimization
- See [Workflow Guide](workflow-guide.md) for end-to-end workflows

## Next Steps

After generating images in Create Studio:

1. **Edit**: Use [Edit Studio](edit-studio.md) to refine images
2. **Upscale**: Use [Upscale Studio](upscale-studio.md) to enhance resolution
3. **Optimize**: Use [Social Optimizer](social-optimizer.md) for platform-specific exports
4. **Organize**: Save to [Asset Library](asset-library.md) for easy access

---

*For technical details, see the [Implementation Overview](implementation-overview.md). For API usage, see the [API Reference](api-reference.md).*

