# Edit Studio User Guide

Edit Studio provides AI-powered image editing capabilities to enhance, modify, and transform your images. This guide covers all available operations and how to use them effectively.

## Overview

Edit Studio enables you to perform professional-grade image editing using AI. From simple background removal to complex object replacement, Edit Studio makes advanced editing accessible without design software expertise.

### Key Features
- **7 Editing Operations**: Remove background, inpaint, outpaint, search & replace, search & recolor, relight, and general edit
- **Mask Editor**: Visual mask creation for precise control
- **Multiple Inputs**: Support for base images, masks, backgrounds, and lighting references
- **Real-time Preview**: See results before finalizing
- **Provider Flexibility**: Uses Stability AI and HuggingFace for different operations

## Getting Started

### Accessing Edit Studio

1. Navigate to **Image Studio** from the main dashboard
2. Click on **Edit Studio** or go directly to `/image-editor`
3. Upload your base image to begin editing

### Basic Workflow

1. **Upload Base Image**: Select the image you want to edit
2. **Choose Operation**: Select from available editing operations
3. **Configure Settings**: Add prompts, masks, or reference images as needed
4. **Apply Edit**: Click "Apply Edit" to process
5. **Review Results**: Compare original and edited versions
6. **Download**: Save your edited image

## Available Operations

### 1. Remove Background

**Purpose**: Isolate the main subject by removing the background.

**When to Use**:
- Product photography
- Creating transparent PNGs
- Isolating subjects for compositing
- Social media graphics

**How to Use**:
1. Upload your base image
2. Select "Remove Background" operation
3. Click "Apply Edit"
4. The background is automatically removed

**Tips**:
- Works best with clear subject-background separation
- High contrast images produce better results
- Complex backgrounds may require manual cleanup

### 2. Inpaint & Fix

**Purpose**: Edit specific regions by filling or replacing areas using prompts and optional masks.

**When to Use**:
- Remove unwanted objects
- Fix imperfections
- Fill in missing areas
- Replace specific elements

**How to Use**:
1. Upload your base image
2. Select "Inpaint & Fix" operation
3. **Create Mask** (optional but recommended):
   - Click "Open Mask Editor"
   - Draw over areas you want to edit
   - Save the mask
4. **Enter Prompt**: Describe what you want in the edited area
   - Example: "clean white wall" or "blue sky with clouds"
5. **Negative Prompt** (optional): Describe what to avoid
6. Click "Apply Edit"

**Mask Tips**:
- Precise masks produce better results
- Include some surrounding area for natural blending
- Use the brush tool for detailed masking

**Prompt Examples**:
- "Remove person, replace with empty space"
- "Fix scratch on car door"
- "Add window to wall"
- "Remove text watermark"

### 3. Outpaint

**Purpose**: Extend the canvas in any direction with AI-generated content.

**When to Use**:
- Extend images beyond original boundaries
- Create wider compositions
- Fix cropped images
- Add context around subjects

**How to Use**:
1. Upload your base image
2. Select "Outpaint" operation
3. **Set Expansion**:
   - Use sliders for Left, Right, Up, Down (0-512 pixels)
   - Set expansion for each direction
4. **Negative Prompt** (optional): Exclude unwanted elements
5. Click "Apply Edit"

**Expansion Tips**:
- Start with small expansions (50-100px) for best results
- Large expansions may require multiple passes
- Consider the image content when expanding
- Use negative prompts to guide the expansion

**Use Cases**:
- Extend landscape photos
- Add more space around products
- Create wider social media images
- Fix accidentally cropped images

### 4. Search & Replace

**Purpose**: Locate objects via search prompt and replace them with new content. Optional mask for precise control.

**When to Use**:
- Replace objects in images
- Swap products in photos
- Change elements while maintaining context
- Update outdated content

**How to Use**:
1. Upload your base image
2. Select "Search & Replace" operation
3. **Search Prompt**: Describe what to find and replace
   - Example: "red car" to find a red car
4. **Prompt**: Describe the replacement
   - Example: "blue car" to replace with a blue car
5. **Mask** (optional): Use mask editor for precise region selection
6. Click "Apply Edit"

**Prompt Examples**:
- Search: "old phone", Replace: "modern smartphone"
- Search: "winter trees", Replace: "spring trees with flowers"
- Search: "wooden table", Replace: "glass table"

**Tips**:
- Be specific in search prompts
- Use masks for better precision
- Consider lighting and perspective in replacements

### 5. Search & Recolor

**Purpose**: Select elements via prompt and recolor them. Optional mask for exact region selection.

**When to Use**:
- Change colors of specific objects
- Create color variations
- Match brand colors
- Experiment with color schemes

**How to Use**:
1. Upload your base image
2. Select "Search & Recolor" operation
3. **Select Prompt**: Describe what to recolor
   - Example: "red dress" or "blue car"
4. **Prompt**: Describe the new color
   - Example: "green dress" or "yellow car"
5. **Mask** (optional): Use mask editor for precise selection
6. Click "Apply Edit"

**Prompt Examples**:
- Select: "red shirt", Recolor: "blue shirt"
- Select: "green grass", Recolor: "autumn brown grass"
- Select: "white wall", Recolor: "beige wall"

**Tips**:
- Be specific about what to recolor
- Consider lighting and shadows
- Use masks for complex selections

### 6. Replace Background & Relight

**Purpose**: Swap backgrounds and adjust lighting using reference images.

**When to Use**:
- Change photo backgrounds
- Match lighting between subjects and backgrounds
- Create composite images
- Professional product photography

**How to Use**:
1. Upload your base image (subject)
2. Select "Replace Background & Relight" operation
3. **Upload Background Image**: Reference image for new background
4. **Upload Lighting Image** (optional): Reference for lighting style
5. Click "Apply Edit"

**Tips**:
- Use high-quality background images
- Match perspective and angle when possible
- Lighting reference helps create realistic composites
- Consider subject-background compatibility

### 7. General Edit / Prompt-based Edit

**Purpose**: Make general edits to images using natural language prompts. Optional mask for targeted editing.

**When to Use**:
- General image modifications
- Style changes
- Atmosphere adjustments
- Creative transformations

**How to Use**:
1. Upload your base image
2. Select "General Edit" operation
3. **Enter Prompt**: Describe the desired changes
   - Example: "make it more vibrant and colorful"
   - Example: "add warm sunset lighting"
   - Example: "convert to black and white with high contrast"
4. **Mask** (optional): Use mask editor to target specific areas
5. **Negative Prompt** (optional): Exclude unwanted changes
6. Click "Apply Edit"

**Prompt Examples**:
- "Add dramatic lighting with shadows"
- "Make colors more saturated and vibrant"
- "Convert to vintage film style"
- "Add fog and atmosphere"
- "Enhance details and sharpness"

**Tips**:
- Be descriptive in your prompts
- Use masks for localized edits
- Combine with negative prompts for better control

## Mask Editor

The Mask Editor is a powerful tool for precise editing control. It allows you to visually define areas to edit.

### Accessing the Mask Editor

1. Select an operation that supports masks (Inpaint, Search & Replace, Search & Recolor, General Edit)
2. Click "Open Mask Editor" button
3. The mask editor opens in a dialog

### Using the Mask Editor

**Drawing Masks**:
- **Brush Tool**: Paint over areas you want to edit
- **Eraser Tool**: Remove mask areas
- **Brush Size**: Adjust brush size for precision
- **Zoom**: Zoom in/out for detailed work

**Mask Tips**:
- **Precise Masks**: Draw exactly over areas to edit
- **Soft Edges**: Include some surrounding area for natural blending
- **Multiple Passes**: You can refine masks after seeing results
- **Save Masks**: Masks can be reused for similar edits

**When to Use Masks**:
- **Inpaint**: Define areas to fill or replace
- **Search & Replace**: Target specific regions
- **Search & Recolor**: Select exact elements to recolor
- **General Edit**: Apply edits to specific areas only

## Image Uploads

Edit Studio supports multiple image inputs:

### Base Image
- **Required**: Always needed
- **Purpose**: The main image to edit
- **Formats**: JPG, PNG
- **Size**: Recommended under 10MB for best performance

### Mask Image
- **Optional**: For operations that support masks
- **Purpose**: Define areas to edit
- **Creation**: Use Mask Editor or upload existing mask
- **Format**: PNG with transparency

### Background Image
- **Optional**: For Replace Background & Relight
- **Purpose**: Reference for new background
- **Tips**: Match perspective and lighting when possible

### Lighting Image
- **Optional**: For Replace Background & Relight
- **Purpose**: Reference for lighting style
- **Tips**: Use images with desired lighting characteristics

## Advanced Options

### Negative Prompts

Use negative prompts to exclude unwanted elements or effects:

**Common Negative Prompts**:
- "blurry, low quality, distorted"
- "watermark, text, logo"
- "oversaturated, unrealistic colors"
- "artifacts, noise, compression"

**Operation-Specific**:
- **Outpaint**: "people, buildings, text" (to avoid adding unwanted elements)
- **Inpaint**: "blurry edges, artifacts" (to ensure clean fills)
- **General Edit**: "oversaturated, unrealistic" (to maintain natural look)

### Provider Settings

**Stability AI** (default for most operations):
- High quality results
- Reliable performance
- Good for professional editing

**HuggingFace** (for general edits):
- Alternative provider
- Good for creative edits
- Free tier available

## Best Practices

### For Product Photography

1. **Remove Background**: Use for clean product isolation
2. **Replace Background**: Use for different scene contexts
3. **Inpaint**: Remove unwanted elements or reflections
4. **Search & Replace**: Swap product variations

### For Social Media

1. **Remove Background**: Create transparent PNGs for graphics
2. **Outpaint**: Extend images for different aspect ratios
3. **Search & Recolor**: Match brand colors
4. **General Edit**: Apply consistent style across images

### For Photo Editing

1. **Inpaint**: Remove unwanted objects or people
2. **Outpaint**: Fix cropped images
3. **Search & Replace**: Update outdated elements
4. **General Edit**: Enhance overall image quality

### Prompt Writing Tips

1. **Be Specific**: Clear, detailed prompts work best
2. **Use Context**: Reference surrounding elements
3. **Consider Style**: Match the existing image style
4. **Test Iteratively**: Refine prompts based on results

### Mask Creation Tips

1. **Precision**: Draw exactly over target areas
2. **Soft Edges**: Include some surrounding area
3. **Multiple Objects**: Create separate masks for different objects
4. **Refinement**: Adjust masks after seeing initial results

## Troubleshooting

### Common Issues

**Poor Quality Results**:
- Try a different operation
- Use more specific prompts
- Create precise masks
- Adjust negative prompts

**Unwanted Changes**:
- Use negative prompts to exclude elements
- Create more precise masks
- Be more specific in prompts
- Try a different operation

**Mask Not Working**:
- Ensure mask covers the correct area
- Check mask format (should be PNG with transparency)
- Verify operation supports masks
- Try recreating the mask

**Slow Processing**:
- Large images take longer
- Complex operations require more time
- Check your internet connection
- Try reducing image size

### Getting Help

- Check operation-specific tips above
- Review the [Workflow Guide](workflow-guide.md) for common workflows
- See [Implementation Overview](implementation-overview.md) for technical details

## Next Steps

After editing images in Edit Studio:

1. **Upscale**: Use [Upscale Studio](upscale-studio.md) to enhance resolution
2. **Optimize**: Use [Social Optimizer](social-optimizer.md) for platform-specific exports
3. **Organize**: Save to [Asset Library](asset-library.md) for easy access
4. **Create More**: Use [Create Studio](create-studio.md) to generate new images

---

*For technical details, see the [Implementation Overview](implementation-overview.md). For API usage, see the [API Reference](api-reference.md).*

