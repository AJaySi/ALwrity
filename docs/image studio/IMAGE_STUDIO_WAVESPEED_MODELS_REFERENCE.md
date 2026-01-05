# Image Studio: WaveSpeed AI Models Reference

**Purpose**: Complete reference guide for all WaveSpeed AI models integrated into Image Studio  
**Last Updated**: Current Session

---

## 📊 Model Overview

Image Studio integrates **30+ WaveSpeed AI models** across multiple categories, giving users multiple options for each task based on cost, quality, and use case requirements.

---

## 🎨 Image Editing Models (12 Models)

### **Budget Tier** ($0.02-$0.03)

#### 1. **Qwen Image Edit** - `wavespeed-ai/qwen-image/edit`
- **Cost**: $0.02
- **Features**: Bilingual (CN/EN), appearance + semantic editing, style preservation
- **Best For**: Budget-conscious editing, bilingual content, style transfers
- **Use Cases**: Quick edits, content localization, style experiments

#### 2. **Qwen Image Edit Plus** - `wavespeed-ai/qwen-image/edit-plus`
- **Cost**: $0.02
- **Features**: Multi-image editing, ControlNet support, character consistency
- **Best For**: Batch editing, consistent character work, multi-image workflows
- **Use Cases**: Character consistency across images, batch style application

#### 3. **Step1X Edit** - `wavespeed-ai/step1x-edit`
- **Cost**: $0.03
- **Features**: Simple prompt editing, precise modifications
- **Best For**: Quick edits, straightforward changes
- **Use Cases**: Hair color changes, accessory additions, simple modifications

#### 4. **HiDream E1 Full** - `wavespeed-ai/hidream-e1-full`
- **Cost**: $0.024
- **Features**: Identity-preserving edits, wardrobe/accessory changes
- **Best For**: Fashion edits, character consistency, portrait work
- **Use Cases**: Outfit changes, accessory modifications, portrait retouching

#### 5. **SeedEdit V3** - `bytedance/seededit-v3`
- **Cost**: $0.027
- **Features**: Prompt-guided editing, identity preservation
- **Best For**: Portrait edits, e-commerce variants, localized edits
- **Use Cases**: Hair/style changes, product color variants, marketing iterations

---

### **Mid Tier** ($0.035-$0.04)

#### 6. **Alibaba WAN 2.5 Image Edit** - `alibaba/wan-2.5/image-edit`
- **Cost**: $0.035
- **Features**: Structure-preserving edits, prompt expansion
- **Best For**: Quick adjustments, cost-effective editing
- **Use Cases**: Lighting changes, color adjustments, object modifications

#### 7. **FLUX Kontext Pro** - `wavespeed-ai/flux-kontext-pro`
- **Cost**: $0.04
- **Features**: Improved prompt adherence, typography generation, consistency
- **Best For**: Typography-heavy edits, consistent results, professional work
- **Use Cases**: Text in images, poster editing, marketing materials

#### 8. **FLUX Kontext Pro Multi** - `wavespeed-ai/flux-kontext-pro/multi`
- **Cost**: $0.04
- **Features**: Multi-image handling (up to 5 references), context combination
- **Best For**: Character consistency, style alignment, multi-image workflows
- **Use Cases**: Consistent character generation, product variations, style matching

---

### **Premium Tier** ($0.08-$0.15)

#### 9. **FLUX Kontext Max** - `wavespeed-ai/flux-kontext-max`
- **Cost**: $0.08
- **Features**: Premium quality, high-fidelity transformations
- **Best For**: Professional retouching, style transformations, high-end work
- **Use Cases**: Premium retouching, cinematic edits, artistic transformations

#### 10. **Ideogram Character** - `ideogram-ai/ideogram-character`
- **Cost**: $0.10-$0.20 (Turbo/Default/Quality)
- **Features**: Character-focused editing, outfit/appearance changes, style modes
- **Best For**: Fashion visualization, character design, portrait work
- **Use Cases**: Outfit changes, character variations, fashion campaigns

#### 11. **Google Nano Banana Pro Edit Ultra** - `google/nano-banana-pro/edit-ultra`
- **Cost**: $0.15 (4K) / $0.18 (8K)
- **Features**: Native 4K/8K editing, natural language, multilingual text
- **Best For**: Professional marketing, high-res edits, typography work
- **Use Cases**: Campaign visuals, print materials, high-resolution work

---

### **Quality Tiers** (Variable Pricing)

#### 12. **OpenAI GPT Image 1** - `openai/gpt-image-1`
- **Cost**: $0.011-$0.250 (varies by quality and size)
  - Low: $0.011 (square) / $0.016 (rectangular)
  - Medium: $0.042 (square) / $0.063 (rectangular)
  - High: $0.167 (square) / $0.250 (rectangular)
- **Features**: Quality tiers, mask support, style transformation
- **Best For**: Style transfers, creative transformations, quality control
- **Use Cases**: Artistic style changes, creative edits, quality-based workflows

---

## ⬆️ Upscaling Models (3 Models)

### 1. **Image Upscaler** - `wavespeed-ai/image-upscaler`
- **Cost**: $0.01
- **Resolution**: 2K/4K/8K
- **Best For**: Fast, affordable upscaling
- **Speed**: Fast

### 2. **Bria Increase Resolution** - `bria/increase-resolution`
- **Cost**: $0.04
- **Resolution**: 2x/4x multiplier
- **Best For**: Detail-preserving upscale
- **Speed**: Medium

### 3. **Ultimate Image Upscaler** - `wavespeed-ai/ultimate-image-upscaler`
- **Cost**: $0.06
- **Resolution**: 2K/4K/8K
- **Best For**: Premium quality upscaling
- **Speed**: Medium

---

## 👤 Face Swap Models (5 Models)

### 1. **Image Face Swap** - `wavespeed-ai/image-face-swap`
- **Cost**: $0.01
- **Features**: Basic face replacement
- **Best For**: Quick swaps, cost-sensitive use cases

### 2. **Image Face Swap Pro** - `wavespeed-ai/image-face-swap-pro`
- **Cost**: $0.025
- **Features**: Enhanced blending, realistic results
- **Best For**: Professional quality swaps

### 3. **Image Head Swap** - `wavespeed-ai/image-head-swap`
- **Cost**: $0.025
- **Features**: Full head replacement (face + hair + outline)
- **Best For**: Complete head swaps, casting mockups

### 4. **InfiniteYou** - `wavespeed-ai/infinite-you`
- **Cost**: $0.05
- **Features**: High-quality identity preservation (ByteDance)
- **Best For**: High-quality swaps, identity preservation

### 5. **Akool Multi-Face Swap** - `akool/image-face-swap`
- **Cost**: $0.16
- **Features**: Multi-face swapping in group photos
- **Best For**: Group photos, multiple face replacements

---

## 🔧 Specialized Editing Models

### **Erasing**
- **Image Eraser** - `wavespeed-ai/image-eraser` ($0.025)
  - Remove objects, people, text with mask support
  - Multi-region removal, context-aware reconstruction

### **Expansion/Outpainting**
- **Bria Expand** - `bria/expand` ($0.04)
  - Aspect ratio expansion, intelligent outpainting
  - Context-aware, maintains lighting/perspective

### **Background**
- **Bria Background Generation** - `bria/generate-background` ($0.04)
  - Text or reference image-driven background replacement
  - Subject preservation, style options

### **Text Removal**
- **Image Text Remover** - `wavespeed-ai/image-text-remover` ($0.15)
  - Automatic text detection and removal
  - High-fidelity inpainting

---

## 🌐 Translation Models (2 Models)

### 1. **WaveSpeed Image Translator** - `wavespeed-ai/image-translator`
- **Cost**: $0.15
- **Features**: 30+ languages, font preservation, layout-aware
- **Best For**: High-quality translation with visual fidelity

### 2. **Alibaba Qwen Image Translate** - `alibaba/qwen-image/translate`
- **Cost**: $0.01
- **Features**: OCR + translation, terminology control, sensitive word filtering
- **Best For**: Cost-effective translation, document processing

---

## 🎮 3D Generation Models (9 Models)

### **Budget Tier** ($0.02)

#### 1. **SAM 3D Body** - `wavespeed-ai/sam-3d-body`
- **Cost**: $0.02
- **Input**: Single image + optional mask
- **Output**: 3D human body model
- **Best For**: Character modeling, avatar creation

#### 2. **SAM 3D Objects** - `wavespeed-ai/sam-3d-objects`
- **Cost**: $0.02
- **Input**: Single image + optional mask + prompt
- **Output**: 3D object model
- **Best For**: Product visualization, props

#### 3. **Hunyuan3D V2 Multi-View** - `wavespeed-ai/hunyuan3d/v2-multi-view`
- **Cost**: $0.02
- **Input**: Front + back + left images
- **Output**: High-fidelity 3D with 4K textures
- **Best For**: Accurate reconstruction, digital twins

### **Premium Tier** ($0.25-$0.30)

#### 4. **Tripo3D V2.5 Image-to-3D** - `tripo3d/v2.5/image-to-3d`
- **Cost**: $0.30
- **Input**: Single image
- **Output**: High-quality 3D asset
- **Best For**: Game assets, e-commerce, AR/VR

#### 5. **Hunyuan3D V2.1** - `wavespeed-ai/hunyuan3d/v2.1`
- **Cost**: $0.30
- **Input**: Single image
- **Output**: Scalable 3D with PBR textures
- **Best For**: Production workflows, game art

#### 6. **Hunyuan3D V3 Image-to-3D** - `wavespeed-ai/hunyuan3d-v3/image-to-3d`
- **Cost**: $0.25
- **Input**: Single image + optional multi-view
- **Output**: Ultra-high-resolution 3D
- **Best For**: Film-quality geometry

#### 7. **Hyper3D Rodin v2 Image-to-3D** - `hyper3d/rodin-v2/image-to-3d`
- **Cost**: $0.30
- **Input**: Single/multiple images + optional prompt
- **Output**: Production-ready 3D with UVs/textures
- **Best For**: Game art, film/TV, XR

#### 8. **Tripo3D V2.5 Multiview** - `tripo3d/v2.5/multiview-to-3d`
- **Cost**: $0.30
- **Input**: Multiple views
- **Output**: Higher-fidelity 3D
- **Best For**: Digital twins, 3D catalogs

### **Text-to-3D** ($0.30)

#### 9. **Hyper3D Rodin v2 Text-to-3D** - `hyper3d/rodin-v2/text-to-3d`
- **Cost**: $0.30
- **Input**: Text prompt
- **Output**: Production-ready 3D with UVs/textures
- **Best For**: Concept to 3D, rapid prototyping

### **Sketch-to-3D** ($0.375)

#### 10. **Hunyuan3D V3 Sketch-to-3D** - `wavespeed-ai/hunyuan3d-v3/sketch-to-3d`
- **Cost**: $0.375
- **Input**: Sketch image + optional prompt
- **Output**: 3D model with optional PBR
- **Best For**: Concept art to 3D, game development

---

## 📝 Utility Models

### **Image Captioning**
- **Image Captioner** - `wavespeed-ai/image-captioner` ($0.001)
  - Generate detailed image descriptions
  - SEO/accessibility, dataset labeling

### **Additional Inpainting**
- **Z-Image Turbo Inpaint** - `wavespeed-ai/z-image/turbo-inpaint` ($0.02)
  - Ultra-fast inpainting with natural language
  - Best for: Product photo cleanup, object removal

### **Additional Outpainting**
- **Image Zoom-Out** - `wavespeed-ai/image-zoom-out` ($0.02)
  - Professional outpainting/expansion
  - Best for: Expanding images, cinematic compositions

### **Enhanced Generation**
- **WAN 2.2 Text-to-Image Realism** - `wavespeed-ai/wan-2.2/text-to-image-realism` ($0.025)
  - Ultra-realistic photorealistic generation
  - Best for: Lifestyle photography, stock imagery

---

## 🎯 Model Selection Strategy

### **By Cost**
- **Budget** ($0.01-$0.03): Qwen Edit, Step1X, Face Swap, Image Upscaler
- **Mid-Range** ($0.04-$0.05): FLUX Kontext Pro, Bria models, InfiniteYou
- **Premium** ($0.08-$0.20): FLUX Kontext Max, Ideogram Character, Nano Banana Pro

### **By Quality**
- **Good**: Qwen, Step1X, HiDream, SeedEdit
- **Excellent**: FLUX Kontext Pro/Max, GPT Image 1, Ideogram Character
- **Premium**: Nano Banana Pro Edit Ultra (4K/8K)

### **By Use Case**
- **Quick Edits**: Qwen Edit ($0.02), Step1X ($0.03)
- **Professional Work**: Nano Banana Pro ($0.15), FLUX Kontext Max ($0.08)
- **Character Work**: Ideogram Character ($0.10-$0.20), HiDream ($0.024)
- **Typography**: FLUX Kontext Pro ($0.04), Ideogram V3 Turbo ($0.03)
- **Multi-Image**: FLUX Kontext Pro Multi ($0.04), Qwen Edit Plus ($0.02)

---

## 💡 Smart Model Selection

### **Auto-Select Based On**:
1. **Budget Mode**: Select cheapest model
2. **Quality Mode**: Select best quality model
3. **Balanced Mode**: Select best value model
4. **Use Case**: Select model optimized for specific task

### **User Choice**:
- Show all available models with cost/quality comparison
- Allow manual selection
- Display recommendations based on edit type

---

## 📊 Cost Comparison Examples

### **Editing a Portrait**:
- **Budget**: Qwen Edit ($0.02) or Step1X ($0.03)
- **Balanced**: FLUX Kontext Pro ($0.04) or SeedEdit ($0.027)
- **Premium**: Nano Banana Pro ($0.15) or FLUX Kontext Max ($0.08)

### **Upscaling an Image**:
- **Budget**: Image Upscaler ($0.01)
- **Balanced**: Bria Increase Resolution ($0.04)
- **Premium**: Ultimate Upscaler ($0.06)

### **Face Swapping**:
- **Budget**: Face Swap ($0.01)
- **Balanced**: Face Swap Pro ($0.025) or InfiniteYou ($0.05)
- **Premium**: Multi-Face Swap ($0.16)

---

## 🔗 Integration Points

### **Edit Studio**
- Add model selector dropdown
- Show cost comparison
- Display quality recommendations
- Allow side-by-side comparison

### **Upscale Studio**
- Add WaveSpeed models as alternatives to Stability
- Cost comparison UI
- Quality preview

### **Face Swap Studio** (New)
- Model selection with use case recommendations
- Cost/quality comparison
- Batch processing support

### **Translation Studio** (New)
- Model selector (high-quality vs. budget)
- Language support comparison
- Batch translation

---

## 📚 Related Documentation

- [Image Studio Enhancement Proposal](docs/IMAGE_STUDIO_ENHANCEMENT_PROPOSAL.md)
- [Image Studio Implementation Review](docs/IMAGE_STUDIO_IMPLEMENTATION_REVIEW.md)
- [WaveSpeed Implementation Roadmap](docs/WAVESPEED_IMPLEMENTATION_ROADMAP.md)

---

*Document Version: 2.0*  
*Last Updated: Current Session*  
*Total Models: 40+ WaveSpeed AI models*

---

## 📊 Complete Model Count

- **Image Editing**: 14 models
- **Upscaling**: 3 models
- **Face Swapping**: 5 models
- **3D Generation**: 9 models
- **Translation**: 2 models
- **Specialized**: 7 models (erasing, expansion, background, text removal, captioning, inpainting, generation)
- **Total**: 40+ WaveSpeed AI models
