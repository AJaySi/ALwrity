# Image Studio Providers Guide

Image Studio supports multiple AI providers, each with unique strengths. This guide helps you choose the right provider for your needs.

## Provider Overview

Image Studio integrates with four major AI providers:
- **Stability AI**: Professional-grade generation and editing
- **WaveSpeed**: Photorealistic and fast generation
- **HuggingFace**: Diverse styles and free tier
- **Gemini**: Google's Imagen models

## Stability AI

### Overview
Stability AI provides professional-grade image generation and editing with multiple model options.

### Available Models

#### Stability Ultra
- **Quality**: Highest quality generation
- **Cost**: 8 credits
- **Speed**: 15-30 seconds
- **Best For**: Premium campaigns, print materials, featured content

#### Stability Core
- **Quality**: Fast and affordable
- **Cost**: 3 credits
- **Speed**: 5-15 seconds
- **Best For**: Standard content, social media, general use

#### SD3.5 Large
- **Quality**: Advanced Stable Diffusion 3.5
- **Cost**: Varies
- **Speed**: 10-20 seconds
- **Best For**: Artistic content, creative projects

### Strengths
- **Professional Quality**: Enterprise-grade results
- **Editing Capabilities**: Full editing suite (25+ operations)
- **Reliability**: Consistent, high-quality output
- **Control**: Advanced parameters (guidance, steps, seed)

### Use Cases
- Professional marketing materials
- High-quality social media content
- Print-ready images
- Detailed product photography
- Brand assets

### When to Choose
- You need highest quality
- Professional/business use
- Detailed, realistic images
- Editing operations needed

---

## WaveSpeed

### Overview
WaveSpeed provides two models: Ideogram V3 for photorealistic images and Qwen for fast generation.

### Ideogram V3 Turbo

#### Characteristics
- **Quality**: Photorealistic with superior text rendering
- **Cost**: 5-6 credits
- **Speed**: 10-20 seconds
- **Best For**: Social media, blog images, marketing content

#### Strengths
- **Text in Images**: Best text rendering among all providers
- **Photorealistic**: Highly realistic images
- **Style**: Modern, professional aesthetic
- **Consistency**: Reliable results

#### Use Cases
- Social media posts with text
- Blog featured images
- Marketing materials
- Product showcases
- Brand content

#### When to Choose
- You need text in images
- Photorealistic quality required
- Social media content
- Modern, professional style

### Qwen Image

#### Characteristics
- **Quality**: Good quality, fast generation
- **Cost**: 1-2 credits
- **Speed**: 2-3 seconds (ultra-fast)
- **Best For**: Quick iterations, high-volume content, drafts

#### Strengths
- **Speed**: Fastest generation
- **Cost-Effective**: Lowest cost option
- **Good Quality**: Decent results for speed
- **Iterations**: Perfect for testing concepts

#### Use Cases
- Quick previews
- High-volume content
- Draft generation
- Concept testing
- Rapid iterations

#### When to Choose
- Speed is priority
- Testing concepts
- High-volume needs
- Cost optimization

---

## HuggingFace

### Overview
HuggingFace provides FLUX models with diverse artistic styles and free tier access.

### Available Models

#### FLUX.1-Krea-dev
- **Quality**: Diverse artistic styles
- **Cost**: Free tier available
- **Speed**: 10-20 seconds
- **Best For**: Creative projects, artistic content, experimentation

### Strengths
- **Free Tier**: No cost for basic usage
- **Diverse Styles**: Wide range of artistic styles
- **Creative**: Good for experimental content
- **Accessibility**: Easy to use

### Use Cases
- Creative projects
- Artistic content
- Experimental generation
- Free tier usage
- Diverse style needs

### When to Choose
- You want free tier access
- Creative/artistic content
- Experimentation
- Diverse style requirements

---

## Gemini

### Overview
Google's Gemini provides Imagen models with good general-purpose generation.

### Available Models

#### Imagen 3.0
- **Quality**: Good general quality
- **Cost**: Free tier available
- **Speed**: 10-20 seconds
- **Best For**: General purpose, Google ecosystem integration

### Strengths
- **Free Tier**: No cost for basic usage
- **Google Integration**: Works with Google services
- **General Purpose**: Good for various use cases
- **Reliability**: Consistent results

### Use Cases
- General purpose generation
- Google ecosystem integration
- Free tier usage
- Standard content needs

### When to Choose
- You need free tier access
- Google ecosystem integration
- General purpose content
- Standard quality sufficient

---

## Provider Comparison

### Quality Comparison

| Provider | Quality Level | Best For |
|----------|--------------|----------|
| **Stability Ultra** | Highest | Premium campaigns, print |
| **Ideogram V3** | Very High | Photorealistic, text in images |
| **Stability Core** | High | Standard content |
| **SD3.5** | High | Artistic content |
| **FLUX** | Medium-High | Creative/artistic |
| **Imagen** | Medium-High | General purpose |
| **Qwen** | Medium | Fast iterations |

### Speed Comparison

| Provider | Speed | Use Case |
|----------|-------|----------|
| **Qwen** | 2-3 seconds | Fastest, quick previews |
| **Stability Core** | 5-15 seconds | Fast standard generation |
| **Ideogram V3** | 10-20 seconds | Balanced quality/speed |
| **Stability Ultra** | 15-30 seconds | Highest quality |
| **FLUX/Imagen** | 10-20 seconds | Standard generation |

### Cost Comparison

| Provider | Cost (Credits) | Value |
|----------|---------------|-------|
| **Qwen** | 1-2 | Best value for speed |
| **HuggingFace** | Free tier | Best for free usage |
| **Gemini** | Free tier | Good free option |
| **Stability Core** | 3 | Good value for quality |
| **Ideogram V3** | 5-6 | Premium quality |
| **Stability Ultra** | 8 | Highest quality |

## Provider Selection Guide

### By Use Case

#### Social Media Content
- **Primary**: Ideogram V3 (text in images, photorealistic)
- **Alternative**: Stability Core (fast, reliable)
- **Budget**: Qwen (fast, cost-effective)

#### Blog Featured Images
- **Primary**: Ideogram V3 or Stability Core
- **Alternative**: Stability Ultra (premium quality)
- **Budget**: HuggingFace or Gemini (free tier)

#### Product Photography
- **Primary**: Stability Ultra (highest quality)
- **Alternative**: Ideogram V3 (photorealistic)
- **Budget**: Stability Core (good quality)

#### Marketing Materials
- **Primary**: Stability Ultra or Ideogram V3
- **Alternative**: Stability Core
- **Budget**: Qwen for iterations, Premium for final

#### Creative/Artistic
- **Primary**: SD3.5 or FLUX
- **Alternative**: Stability Core with style presets
- **Budget**: HuggingFace (free tier)

### By Quality Level

#### Draft Quality
- **Recommended**: Qwen, HuggingFace, Gemini
- **Use**: Quick previews, iterations, testing

#### Standard Quality
- **Recommended**: Stability Core, Ideogram V3
- **Use**: Most content, social media, general use

#### Premium Quality
- **Recommended**: Stability Ultra, Ideogram V3
- **Use**: Important campaigns, print, featured content

### By Budget

#### Free Tier
- **Options**: HuggingFace, Gemini
- **Limitations**: Rate limits, basic features
- **Best For**: Testing, learning, low-volume

#### Cost-Effective
- **Options**: Qwen, Stability Core
- **Balance**: Good quality at lower cost
- **Best For**: High-volume, standard content

#### Premium
- **Options**: Stability Ultra, Ideogram V3
- **Investment**: Higher cost, highest quality
- **Best For**: Important campaigns, professional use

## Auto Selection

When set to "Auto", Create Studio selects providers based on:

### Quality-Based Selection
- **Draft**: Qwen, HuggingFace
- **Standard**: Stability Core, Ideogram V3
- **Premium**: Ideogram V3, Stability Ultra

### Template Recommendations
- Templates can suggest specific providers
- Based on platform and use case
- Optimized for best results

### User Preferences
- Learns from your selections
- Adapts to your workflow
- Optimizes for your needs

## Best Practices

### Provider Selection
1. **Start with Auto**: Let system choose initially
2. **Test Providers**: Try different providers for same prompt
3. **Match to Use Case**: Choose based on specific needs
4. **Consider Cost**: Balance quality and cost
5. **Iterate Efficiently**: Use fast providers for testing

### Quality Management
1. **Draft First**: Test with fast, low-cost providers
2. **Upgrade for Final**: Use premium providers for final versions
3. **Compare Results**: Test multiple providers
4. **Learn Preferences**: Note which providers work best for you

### Cost Optimization
1. **Use Free Tier**: HuggingFace/Gemini for testing
2. **Fast Iterations**: Qwen for quick previews
3. **Standard for Most**: Stability Core for general use
4. **Premium Selectively**: Ultra only for important content

## Troubleshooting

### Provider-Specific Issues

**Stability AI**:
- Slower but highest quality
- Best for professional use
- Good editing capabilities

**WaveSpeed Ideogram V3**:
- Best for text in images
- Photorealistic results
- Good for social media

**WaveSpeed Qwen**:
- Fastest generation
- Good for iterations
- Cost-effective

**HuggingFace**:
- Free tier available
- Diverse styles
- Good for experimentation

**Gemini**:
- Free tier available
- Google integration
- General purpose

## Next Steps

- See [Create Studio Guide](create-studio.md) for provider usage
- Check [Cost Guide](cost-guide.md) for cost details
- Review [Workflow Guide](workflow-guide.md) for provider selection in workflows

---

*For technical details, see the [Implementation Overview](implementation-overview.md). For API usage, see the [API Reference](api-reference.md).*

