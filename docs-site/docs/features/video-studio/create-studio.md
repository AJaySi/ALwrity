# Create Studio Guide

Create Studio is your AI-powered video creation hub, enabling you to generate professional videos from text prompts, images, or existing videos. Powered by WaveSpeed AI models including Hunyuan Video, LTX-2 Pro, and Kandinsky5 Pro.

## Overview

Create Studio supports three primary creation methods:

### 1. Text-to-Video (T2V)
Generate videos from text descriptions using advanced AI models.

### 2. Image-to-Video (I2V)
Animate static images into dynamic videos with motion.

### 3. Video Extension
Extend short video clips with temporal consistency.

## Text-to-Video Creation

```mermaid
flowchart LR
    A[📝 Enter Prompt] --> B[⚙️ Configure Settings]
    B --> C[💰 Cost Estimation]
    C --> D{User Approval}
    D -->|Approve| E[🎬 AI Generation]
    D -->|Modify| B

    E --> F[⏳ Processing Queue]
    F --> G[📊 Progress Tracking]
    G --> H{Complete?}
    H -->|No| G
    H -->|Yes| I[✅ Quality Check]
    I --> J[📁 Asset Library]
    J --> K[📤 Download/Export]
    K --> L[📱 Social Sharing]

    style A fill:#e3f2fd
    style E fill:#e8f5e8
    style K fill:#f3e5f5
```

### Quick Start
1. **Select Method**: Choose "Text-to-Video" from the Create Studio menu
2. **Enter Prompt**: Write a detailed description of your desired video
3. **Configure Settings**: Set duration, resolution, and style options
4. **Generate**: Click "Create Video" and wait for processing

### Advanced Prompting

#### Effective Text Prompts
```typescript
// Good prompt - specific and descriptive
"A professional business woman presenting quarterly results in a modern office.
She gestures confidently while charts and graphs appear on a digital screen behind her.
Clean, corporate aesthetic with warm lighting and subtle background music."

// Better prompt - includes motion and style
"A cinematic scene of a chef preparing gourmet pasta in a bustling Italian kitchen.
Slow-motion shots of sauce simmering, steam rising from pots, ingredients being chopped.
Warm golden lighting, rustic wooden surfaces, traditional Italian music in background.
Professional 4K quality, smooth camera movements, 30-second duration."
```

#### Prompt Best Practices
- **Be Specific**: Include details about subjects, actions, setting, and mood
- **Describe Motion**: Specify camera movements, actions, and transitions
- **Include Audio**: Mention background music, sound effects, or ambience
- **Specify Style**: Professional, cinematic, documentary, commercial, etc.
- **Set Duration**: Indicate desired length for optimal results

### Configuration Options

#### Quality Tiers
- **Draft**: Fast generation, lower quality (480p, ~30 seconds processing)
- **Standard**: Balanced quality and speed (720p-1080p, ~2-5 minutes processing)
- **Premium**: High quality, slower processing (1080p-4K, ~5-15 minutes processing)

#### Duration Settings
- **Short**: 5-10 seconds (ideal for social media clips)
- **Medium**: 15-30 seconds (presentations, demos)
- **Long**: 45-60 seconds (detailed explanations, stories)

#### Aspect Ratios
- **16:9**: Horizontal (YouTube, presentations, widescreen)
- **9:16**: Vertical (TikTok, Instagram Stories, mobile)
- **1:1**: Square (Instagram posts, Facebook, LinkedIn)

### AI Models

#### Hunyuan Video (Recommended for General Use)
- **Best For**: General video creation, presentations, educational content
- **Strengths**: Consistent quality, good motion, reliable results
- **Pricing**: $0.02-0.04 per second
- **Limits**: Up to 10 seconds, 480p/720p resolutions

#### LTX-2 Pro (High Quality)
- **Best For**: Professional content, marketing videos, commercials
- **Strengths**: Higher quality output, better motion consistency
- **Pricing**: $0.05-0.10 per second
- **Limits**: Up to 10 seconds, higher resolutions available

#### LTX-2 Fast (Speed Optimized)
- **Best For**: Quick drafts, iterative creation, testing concepts
- **Strengths**: Fast generation, cost-effective for experimentation
- **Pricing**: $0.01-0.02 per second
- **Limits**: Shorter duration, standard quality

## Image-to-Video Creation

### Supported Formats
- **Static Images**: JPG, PNG, WebP
- **Requirements**: Minimum 512x512 pixels, maximum 2048x2048 pixels
- **Best Results**: High-resolution images with clear subjects

### Motion Types
- **Subtle Motion**: Gentle camera movements, slight subject animation
- **Dynamic Motion**: More pronounced movements, action-oriented
- **Custom Motion**: Describe specific camera movements in your prompt

### Example Workflows

#### Product Demo from Image
```typescript
Input: Product photo
Prompt: "Smooth pan around the product showing all features, with gentle rotation and zoom on key details. Clean white background, professional lighting."
Output: Dynamic product showcase video
```

#### Scene Animation
```typescript
Input: Landscape photo
Prompt: "Cinematic camera movement through the scene, starting with wide establishing shot, moving through the landscape with gentle parallax effects."
Output: Immersive scene exploration video
```

## Video Extension

### How It Works
1. **Upload Base Video**: Provide 2-5 second source video
2. **Extension Prompt**: Describe how the video should continue
3. **AI Processing**: Model analyzes motion patterns and extends seamlessly
4. **Output**: Longer video with consistent motion and style

### Best Practices
- **Start Short**: Use 2-5 second clips for best results
- **Consistent Motion**: Choose videos with steady, predictable motion
- **Clear Intent**: Be specific about how the extension should flow
- **Style Matching**: Ensure extension prompt matches original video style

## Cost Estimation

### Pricing Calculator
View estimated costs before generation:
- **Real-time Updates**: Costs update as you change settings
- **Credit Balance**: Shows available credits and post-generation balance
- **Duration Impact**: See how length affects total cost
- **Quality Multipliers**: Understand quality tier pricing differences

### Cost Optimization
- **Start with Draft**: Use draft quality for testing concepts
- **Shorter Videos**: Break long content into multiple shorter videos
- **Batch Processing**: Generate multiple variations efficiently
- **Reuse Assets**: Extend existing videos instead of creating new ones

## Processing & Delivery

### Queue System
- **Background Processing**: Long-running tasks processed asynchronously
- **Progress Tracking**: Real-time status updates and ETA
- **Email Notifications**: Get notified when videos are ready
- **Queue Management**: View and manage pending tasks

### File Delivery
- **Secure URLs**: Temporary signed URLs for download
- **Multiple Formats**: MP4, WebM, MOV options
- **CDN Delivery**: Fast download from global CDN
- **Version Control**: Track different generations and edits

### Asset Library Integration
- **Auto-Save**: Generated videos automatically saved to your library
- **Tagging**: AI-powered automatic tagging and categorization
- **Search**: Find videos by content, creation date, or tags
- **Sharing**: Secure sharing links with access controls

## Troubleshooting

### Common Issues

**Video Generation Failed:**
- Check prompt specificity (add more details)
- Try different quality tier
- Verify supported file formats and sizes

**Poor Quality Output:**
- Use more descriptive prompts
- Try premium quality tier
- Experiment with different AI models

**Motion Issues:**
- For image-to-video: Ensure high-quality source images
- For extension: Use videos with consistent motion
- Add specific motion descriptions to prompts

**Processing Time:**
- Draft quality: 30 seconds - 2 minutes
- Standard quality: 2 - 5 minutes
- Premium quality: 5 - 15 minutes

### Optimization Tips
- **Prompt Refinement**: Iterate on prompts for better results
- **Quality Testing**: Start with draft, then upgrade successful concepts
- **Batch Creation**: Generate multiple variations in one session
- **Asset Reuse**: Use existing videos as starting points

## Advanced Features

### Batch Generation
Create multiple video variations simultaneously:
- **Prompt Variations**: Generate different versions of the same concept
- **Style Exploration**: Test different artistic styles
- **Format Testing**: Create versions for different platforms
- **A/B Testing**: Compare different approaches

### Custom Templates
Save and reuse successful configurations:
- **Prompt Templates**: Pre-built prompts for common use cases
- **Style Presets**: Saved combinations of settings
- **Brand Templates**: Consistent branding across videos
- **Platform Presets**: Optimized settings for specific platforms

### API Integration
For developers and agencies:
- **REST API**: Programmatic video generation
- **Webhook Notifications**: Real-time status updates
- **Bulk Operations**: Process multiple videos simultaneously
- **Custom Workflows**: Integrate with existing CMS and tools

## Success Metrics

Track your Create Studio performance:

- **Generation Success Rate**: Percentage of successful video creations
- **Average Processing Time**: Time from request to completion
- **Cost per Video**: Average spend per generated video
- **Quality Satisfaction**: User ratings and feedback scores
- **Usage Frequency**: How often different features are used

## Use Cases

### Marketing & Advertising
- **Product Demos**: Dynamic product showcases
- **Brand Stories**: Cinematic brand narratives
- **Social Proof**: Customer testimonial videos
- **Event Highlights**: Key moment compilations

### Education & Training
- **Explainer Videos**: Complex concept visualization
- **Tutorial Content**: Step-by-step instructional videos
- **Course Previews**: Engaging course introduction videos
- **Training Materials**: Interactive learning content

### Social Media Content
- **Platform Shorts**: Vertical video content for TikTok/Instagram
- **Story Sequences**: Multi-part story content
- **Behind-the-Scenes**: Authentic brand content
- **User-Generated Style**: Content that feels organic and real

---

*Ready to create your first AI-generated video? Start with a simple text prompt and watch your ideas come to life!*

[:octicons-arrow-right-24: Back to Overview](overview.md)
[:octicons-arrow-right-24: Avatar Studio Guide](avatar-studio.md)