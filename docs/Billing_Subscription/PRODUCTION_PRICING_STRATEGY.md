# Production Pricing Strategy - Basic Tier Launch (OSS-Focused)

## Executive Summary

This document provides a comprehensive pricing strategy for ALwrity's production launch with **Basic Tier only**. All features and tools will be accessible to Basic tier users, requiring careful cost calculation and limit setting to ensure sustainability while providing value.

**Critical Goals**:
1. **OSS-First Strategy**: Prioritize Open-Source AI models (WaveSpeed OSS models) for cost efficiency
2. **Hard Cost Cap**: $40-50 per user per month maximum (protects against losses)
3. **Maximum User Value**: Provide generous limits while staying within cost constraints
4. **Fair Pricing**: Balance between sustainability and user value (not excessive profit margins)

**Strategy**: Use WaveSpeed's OSS models (Qwen, FLUX, Ideogram, WAN 2.5) which offer better pricing than proprietary alternatives, allowing us to provide more value to users while maintaining profitability.

---

## Current State Analysis

### Current Basic Tier (Code Implementation)

**Price**: $29/month ($290/year)

**Limits**:
- **AI Text Generation**: 10 unified calls/month (across all LLM providers)
- **Tokens**: 20,000 per provider (Gemini, OpenAI, Anthropic, Mistral)
- **Search APIs**: 200 Tavily, 200 Serper, 100 Metaphor, 100 Firecrawl, 500 Exa
- **Image Generation**: 5 Stability AI images/month
- **Image Editing**: 30 AI image edits/month
- **Video Generation**: 20 videos/month
- **Audio Generation**: 50 TTS generations/month
- **Monthly Cost Cap**: $50.00

**Problem**: 10 unified AI text generation calls is **too restrictive** for production launch where users need to experience all features.

---

## ALwrity Tools & Content Generation Analysis

### Content Generation Tools

#### 1. **Text Generation Tools** (Primary LLM Usage)

| Tool | API Calls per Generation | Typical Usage | Cost per Generation |
|------|--------------------------|---------------|---------------------|
| **Blog Writer** | 3-5 calls | 1 blog = research (1) + outline (1) + content (1-3) | $0.01 - $0.05 |
| **Story Writer** | 2-3 calls | 1 story = outline (1) + script (1-2) | $0.01 - $0.03 |
| **Podcast Maker** | 3-4 calls | 1 podcast = research (1) + script (1) + outline (1-2) | $0.01 - $0.04 |
| **Facebook Writer** | 1-2 calls | 1 post = generation (1) + optional optimization (1) | $0.005 - $0.01 |
| **LinkedIn Writer** | 1-2 calls | 1 post = generation (1) + optional optimization (1) | $0.005 - $0.01 |
| **SEO Tools** | 1-3 calls | Varies by tool complexity | $0.005 - $0.02 |
| **Content Planning** | 2-4 calls | Strategy generation + analysis | $0.01 - $0.03 |

**Average**: ~2-3 LLM calls per content generation workflow

#### 2. **Image Generation Tools**

| Tool | API Calls | Cost per Generation |
|------|-----------|---------------------|
| **Image Generator** | 1 Stability call | $0.04 per image |
| **Image Editor** | 1 Image Edit call | $0.04 per edit operation |

**Current Limit**: 5 images/month (too low for production)

#### 3. **Video Generation Tools**

| Tool | API Calls | Cost per Video | Notes |
|------|-----------|-----------------|-------|
| **Video Studio** | 1 video call | $0.10 - $0.42 | Depends on model/duration |
| **YouTube Creator** | 1 video call per scene | $0.10 - $0.42 per scene | 5 scenes = $0.50 - $2.10 |
| **Story Writer Video** | 1 video call per scene | $0.10 - $0.42 per scene | Variable scenes |
| **Podcast Maker Video** | 1 video call per scene | $0.10 - $0.42 per scene | Optional video generation |

**Current Limit**: 20 videos/month (reasonable)

#### 4. **Audio Generation Tools**

| Tool | API Calls | Cost per Generation | Notes |
|------|-----------|---------------------|-------|
| **Audio Generator** | 1 audio call | $0.05 per 1,000 chars | ~$0.10 - $0.50 per audio |
| **Podcast Maker TTS** | 1 audio call per scene | $0.05 per 1,000 chars | Multiple scenes |
| **Story Writer Narration** | 1 audio call per scene | $0.05 per 1,000 chars | Multiple scenes |

**Current Limit**: 50 audio generations/month (reasonable)

---

## API Cost Breakdown

### LLM Provider Costs (Per 1M Tokens)

| Provider | Model | Input Cost | Output Cost | Typical Use |
|----------|-------|------------|-------------|-------------|
| **Gemini** | 2.5 Flash | $0.30 | $2.50 | Default (cost-effective) |
| **Gemini** | 2.5 Pro | $1.25 | $10.00 | Premium quality |
| **OpenAI** | GPT-4o Mini | $0.15 | $0.60 | Cost-effective |
| **OpenAI** | GPT-4o | $2.50 | $10.00 | Premium quality |
| **Anthropic** | Claude 3.5 Sonnet | $3.00 | $15.00 | Premium quality |
| **HuggingFace** | GPT-OSS-120B | $1.00 | $3.00 | Alternative option |

**Average Cost per LLM Call** (assuming 1K input + 2K output tokens):
- Gemini Flash: ~$0.0056 per call
- GPT-4o Mini: ~$0.0015 per call
- Claude 3.5: ~$0.033 per call

**Recommendation**: Use Gemini Flash as default for cost efficiency.

### Search API Costs

| Provider | Cost per Search | Typical Usage |
|----------|----------------|---------------|
| **Tavily** | $0.001 | Research operations |
| **Serper** | $0.001 | Research operations |
| **Metaphor** | $0.003 | Research operations |
| **Exa** | $0.005 | Neural search (premium) |
| **Firecrawl** | $0.002 | Web page extraction |

**Average**: ~$0.002 per search operation

### Media Generation Costs (OSS-Focused via WaveSpeed)

#### **Image Generation** (OSS Models via WaveSpeed)
| Model | Cost | Type | Notes |
|------|------|------|-------|
| **Qwen Image** | $0.03 per image | OSS | Fast generation, cost-effective |
| **Ideogram V3 Turbo** | $0.05 per image | OSS | Photorealistic, text rendering |
| **Default (Qwen)** | $0.03 per image | OSS | **Recommended for Basic tier** |

#### **Image Editing** (OSS Models via WaveSpeed)
| Model | Cost | Type | Use Case |
|------|------|------|----------|
| **Qwen Image Edit** | $0.02 per edit | OSS | Budget editing, bilingual |
| **Qwen Image Edit Plus** | $0.02 per edit | OSS | Multi-image editing |
| **FLUX Kontext Pro** | $0.04 per edit | OSS | Typography, professional |
| **Default (Qwen Edit)** | $0.02 per edit | OSS | **Recommended for Basic tier** |

#### **Video Generation** (OSS Models via WaveSpeed)
| Model | Cost | Type | Duration | Notes |
|------|------|------|----------|-------|
| **WAN 2.5** | $0.05/sec | OSS | 5-15 sec | Text-to-Video, Image-to-Video |
| **Seedance 1.5 Pro** | $0.08/sec | OSS | 10-30 sec | Longer duration |
| **Kling v2.5 Turbo (5s)** | $0.21 per video | OSS | 5 sec | Image-to-Video |
| **Kling v2.5 Turbo (10s)** | $0.42 per video | OSS | 10 sec | Extended duration |
| **Default (WAN 2.5)** | $0.25 per video | OSS | ~5 sec | **Recommended for Basic tier** |

#### **Audio Generation** (OSS Models via WaveSpeed)
| Model | Cost | Type | Notes |
|------|------|------|-------|
| **Minimax Speech 02 HD** | $0.05 per 1K chars | OSS | High-quality TTS |
| **Default** | $0.05 per 1K chars | OSS | ~$0.10-0.50 per audio |

#### **Face Swap & Specialized** (OSS Models via WaveSpeed)
| Operation | Cost | Type | Notes |
|-----------|------|------|-------|
| **Face Swap** | $0.01-$0.03 | OSS | Basic to premium quality |
| **Image Upscaling** | $0.01-$0.06 | OSS | 2K/4K/8K options |
| **3D Generation** | $0.02-$0.30 | OSS | Budget to premium |

**OSS Advantage**: WaveSpeed provides access to OSS models (Qwen, FLUX, Ideogram, WAN 2.5) at significantly lower costs than proprietary alternatives, enabling better value for users.

---

## Production-Ready Basic Tier Proposal

### Revised Limits for Production Launch

**Price**: $29/month ($290/year) - **KEEP CURRENT PRICING**

**Rationale**: Competitive pricing point, allows for sustainable margins with proper limits.

### Proposed Limits

#### 1. **AI Text Generation** (Unified Limit)
- **Current**: 10 calls/month ❌ **TOO LOW**
- **Proposed**: **50 calls/month** ✅
- **Rationale**: 
  - Allows ~16-25 content generations/month (assuming 2-3 calls each)
  - Enables users to experience Blog Writer, Story Writer, Podcast Maker, Social Writers
  - Sustainable cost: ~$0.28/month (50 calls × $0.0056 average)

#### 2. **Token Limits** (Per Provider)
- **Current**: 20,000 tokens/provider
- **Proposed**: **100,000 tokens/provider** ✅
- **Rationale**:
  - Allows ~33-50 LLM calls per provider (assuming 2K tokens/call)
  - Provides buffer for longer content generation
  - Aligns with unified call limit (50 calls × 2K tokens = 100K tokens)

#### 3. **Search APIs**
- **Tavily**: 200 calls/month ✅ (Keep)
- **Serper**: 200 calls/month ✅ (Keep)
- **Metaphor**: 100 calls/month ✅ (Keep)
- **Firecrawl**: 100 calls/month ✅ (Keep)
- **Exa**: 500 calls/month ✅ (Keep)
- **Rationale**: Sufficient for research-heavy tools (Blog Writer, Podcast Maker, SEO tools)

#### 4. **Image Generation** (OSS Models via WaveSpeed)
- **Current**: 5 images/month ❌ **TOO LOW**
- **Proposed**: **50 images/month** ✅ (INCREASED - OSS models are cheaper)
- **Rationale**: 
  - OSS models (Qwen Image $0.03) are cheaper than Stability ($0.04)
  - Allows users to generate images for Story Writer, Blog Writer, Social Media
  - Cost: ~$1.50/month (50 × $0.03 using Qwen Image OSS model)
  - Enables visual content creation workflows
  - **Default to Qwen Image OSS model** for cost efficiency

#### 5. **Image Editing** (OSS Models via WaveSpeed)
- **Current**: 30 edits/month
- **Proposed**: **50 edits/month** ✅ (INCREASED - OSS models are cheaper)
- **Rationale**: 
  - OSS models (Qwen Edit $0.02) are cheaper than Stability ($0.04)
  - Cost: ~$1.00/month (50 × $0.02 using Qwen Edit OSS model)
  - Sufficient for image optimization workflows
  - **Default to Qwen Edit OSS model** for cost efficiency

#### 6. **Video Generation** (OSS Models via WaveSpeed)
- **Current**: 20 videos/month
- **Proposed**: **30 videos/month** ✅ (INCREASED - OSS models available)
- **Rationale**: 
  - OSS models (WAN 2.5 $0.25 per 5s video) provide good value
  - Allows ~6-10 full video projects/month (assuming 3-5 scenes each)
  - Cost: ~$7.50/month (30 × $0.25 using WAN 2.5 OSS model)
  - Enables Video Studio, YouTube Creator, Story Writer video features
  - **Default to WAN 2.5 OSS model** for cost efficiency

#### 7. **Audio Generation** (OSS Models via WaveSpeed)
- **Current**: 50 generations/month
- **Proposed**: **100 generations/month** ✅ (INCREASED - OSS models are affordable)
- **Rationale**:
  - OSS models (Minimax Speech 02 HD) provide high quality at $0.05/1K chars
  - Sufficient for Podcast Maker, Story Writer narration
  - Cost: ~$10.00-$25.00/month (depending on length, assuming 2K-5K chars per audio)
  - Enables audio content workflows
  - **Default to Minimax Speech 02 HD OSS model**

#### 8. **Monthly Cost Cap**
- **Current**: $50.00
- **Proposed**: **$45.00** ✅ (ADJUSTED - aligns with $40-50 target)
- **Rationale**: 
  - Protects against unexpected high usage
  - Allows flexibility within limits
  - Provides safety margin
  - Aligns with $40-50 hard limit requirement

---

## Cost Analysis: Proposed Basic Tier (OSS-Focused)

### Monthly Cost Breakdown (Per User) - Using OSS Models

| Category | Usage | Cost per Unit (OSS) | Monthly Cost |
|----------|-------|---------------------|--------------|
| **LLM Calls** | 50 calls | $0.0056 avg (Gemini Flash) | **$0.28** |
| **Search APIs** | 200 searches | $0.002 avg | **$0.40** |
| **Image Generation** | 50 images | $0.03 (Qwen Image OSS) | **$1.50** |
| **Image Editing** | 50 edits | $0.02 (Qwen Edit OSS) | **$1.00** |
| **Video Generation** | 30 videos | $0.25 (WAN 2.5 OSS, ~5s) | **$7.50** |
| **Audio Generation** | 100 audios | $0.10-$0.50 avg | **$10.00-$25.00** |
| **Total Variable Cost** | | | **$20.68-$35.68** |

### Margin Analysis (OSS-Focused)

**Subscription Revenue**: $29.00/month
**Variable Costs (OSS Models)**: $20.68-$35.68/month (depending on usage)
**Gross Margin**: **-$6.68 to +$8.32/month**

**✅ IMPROVEMENT**: OSS models reduce costs significantly:
- Image generation: $0.03 vs $0.04 (25% savings)
- Image editing: $0.02 vs $0.04 (50% savings)
- Video generation: $0.25 vs $0.42 (40% savings)

**Mitigation Strategy**: 
1. **Cost cap enforcement**: Monthly cost cap of $45 prevents extreme losses
2. **OSS model defaults**: Default to cheaper OSS models (Qwen, WAN 2.5)
3. **Realistic usage**: Most users won't hit all limits simultaneously
4. **Average usage assumption**: ~60-70% of limits = $12-25 cost = $4-17 margin
5. **Hard limit protection**: $45 cap ensures we never exceed $50/user/month

---

## Revised Basic Tier Limits (Production-Ready, OSS-Focused)

```python
{
    "name": "Basic",
    "tier": SubscriptionTier.BASIC,
    "price_monthly": 29.0,
    "price_yearly": 290.0,
    
    # AI Text Generation (Unified Limit)
    "ai_text_generation_calls_limit": 50,  # INCREASED from 10
    
    # Token Limits (Per Provider)
    "gemini_tokens_limit": 100000,  # INCREASED from 20,000
    "openai_tokens_limit": 100000,  # INCREASED from 20,000
    "anthropic_tokens_limit": 100000,  # INCREASED from 20,000
    "mistral_tokens_limit": 100000,  # INCREASED from 20,000
    
    # Search APIs
    "tavily_calls_limit": 200,  # Keep
    "serper_calls_limit": 200,  # Keep
    "metaphor_calls_limit": 100,  # Keep
    "firecrawl_calls_limit": 100,  # Keep
    "exa_calls_limit": 500,  # Keep
    
    # Media Generation (OSS Models via WaveSpeed)
    "stability_calls_limit": 50,  # INCREASED from 5 (using Qwen Image OSS $0.03)
    "image_edit_calls_limit": 50,  # INCREASED from 30 (using Qwen Edit OSS $0.02)
    "video_calls_limit": 30,  # INCREASED from 20 (using WAN 2.5 OSS $0.25)
    "audio_calls_limit": 100,  # INCREASED from 50 (using Minimax Speech OSS)
    
    # Cost Protection
    "monthly_cost_limit": 45.0,  # ADJUSTED from 50.0 (aligns with $40-50 target)
    
    # OSS Model Defaults
    "default_image_model": "qwen-image",  # OSS model via WaveSpeed
    "default_image_edit_model": "qwen-edit",  # OSS model via WaveSpeed
    "default_video_model": "wan-2.5",  # OSS model via WaveSpeed
    "default_audio_model": "minimax-speech-02-hd",  # OSS model via WaveSpeed
    
    # Features
    "features": [
        "full_content_generation",
        "advanced_research", 
        "basic_analytics",
        "all_tools_access",  # All ALwrity tools accessible
        "billing_dashboard",
        "usage_tracking",
        "oss_models_priority"  # NEW: OSS models prioritized for cost efficiency
    ],
    "description": "Perfect for individuals and small teams. Access all ALwrity features with generous limits powered by OSS AI models."
}
```

---

## Tool Usage Scenarios & Limits

### Scenario 1: Blog Writer User
- **Workflow**: 1 blog post = 3-5 LLM calls + 3-5 search calls + 1-2 images
- **Monthly Capacity**: ~10-16 blog posts (with 50 LLM calls)
- **Cost**: ~$0.50-$1.00 per blog post
- **Status**: ✅ **FEASIBLE**

### Scenario 2: Story Writer User
- **Workflow**: 1 story = 2-3 LLM calls + 5-10 images + 5-10 audio + 5-10 videos
- **Monthly Capacity**: ~16-25 stories (LLM limit) OR ~3-6 stories (image/video limits)
- **Cost**: ~$2.00-$5.00 per story
- **Status**: ✅ **FEASIBLE** (limited by media, not LLM)

### Scenario 3: Podcast Maker User
- **Workflow**: 1 podcast = 3-4 LLM calls + 3-5 search calls + 5-10 audio + optional 5-10 videos
- **Monthly Capacity**: ~12-16 podcasts (LLM limit) OR ~5-10 podcasts (audio limit)
- **Cost**: ~$1.00-$3.00 per podcast (without video)
- **Status**: ✅ **FEASIBLE**

### Scenario 4: Social Media Content Creator
- **Workflow**: 1 post = 1-2 LLM calls + 1 image (optional)
- **Monthly Capacity**: ~25-50 posts (LLM limit) OR ~30 posts (image limit)
- **Cost**: ~$0.10-$0.15 per post
- **Status**: ✅ **FEASIBLE**

### Scenario 5: Video Creator (YouTube Creator)
- **Workflow**: 1 video = 2-3 LLM calls + 5 scenes × (1 image + 1 audio + 1 video)
- **Monthly Capacity**: ~4-5 full videos (video limit) OR ~16-25 videos (LLM limit)
- **Cost**: ~$3.00-$5.00 per video
- **Status**: ✅ **FEASIBLE** (limited by video limit, not LLM)

---

## Risk Mitigation Strategies

### 1. **Cost Cap Enforcement**
- **Monthly cost cap**: $50.00 (hard limit)
- **Behavior**: When cap reached, all API calls blocked until next billing period
- **Protection**: Prevents losses from extreme usage

### 2. **Pre-flight Validation**
- **Implementation**: Already in place
- **Function**: Validates limits BEFORE making API calls
- **Benefit**: Prevents wasted API calls on operations that would fail

### 3. **Usage Monitoring & Alerts**
- **80% Warning**: Alert users at 80% of limits
- **100% Block**: Block operations at 100% of limits
- **Dashboard**: Real-time usage tracking

### 4. **Optimized Default Models**
- **Strategy**: Use cost-effective models by default (Gemini Flash, GPT-4o Mini)
- **Benefit**: Reduces costs while maintaining quality
- **User Control**: Allow model selection for power users

### 5. **Efficient API Usage**
- **Batching**: Batch multiple operations where possible
- **Caching**: Cache research results and common queries
- **Optimization**: Continue optimizing tool workflows to reduce API calls

---

## Pricing Page Updates Required

### Current Issues
1. Pricing page shows outdated limits
2. Missing unified `ai_text_generation_calls_limit` explanation
3. Token limits don't match code (shows 1M/500K, code has 20K)
4. Missing video/audio/image editing limits
5. Missing cost transparency information

### Required Updates

#### Basic Tier Display
```
💰 Basic Plan - $29/month ($290/year)

✨ All ALwrity Features Included:
✅ Blog Writer, Story Writer, Podcast Maker
✅ Image Generator & Editor
✅ Video Studio & YouTube Creator
✅ Audio Generator
✅ All Social Media Writers
✅ All SEO Tools & Dashboards
✅ Content Planning & Strategy Tools

📊 Usage Limits:
• 50 AI Text Generations/month (unified across all LLM providers)
• 100,000 tokens per provider (Gemini, OpenAI, Anthropic, Mistral)
• 200 Research Searches/month (Tavily, Serper)
• 500 Neural Searches/month (Exa)
• 30 AI Images/month
• 30 Image Edits/month
• 20 AI Videos/month
• 50 AI Audio Generations/month
• $50 Monthly Cost Cap (protects you from overages)

💡 Perfect for: Individuals, content creators, small teams
```

---

## Implementation Checklist

### Phase 1: Update Code Limits
- [ ] Update `pricing_service.py` Basic tier limits:
  - [ ] `ai_text_generation_calls_limit`: 10 → 50
  - [ ] `gemini_tokens_limit`: 20,000 → 100,000
  - [ ] `openai_tokens_limit`: 20,000 → 100,000
  - [ ] `anthropic_tokens_limit`: 20,000 → 100,000
  - [ ] `mistral_tokens_limit`: 20,000 → 100,000
  - [ ] `stability_calls_limit`: 5 → 30
- [ ] Run database migration script
- [ ] Test limit enforcement

### Phase 2: Update Pricing Page
- [ ] Update `docs-site/docs/features/subscription/pricing.md`
- [ ] Update frontend pricing page component
- [ ] Add cost transparency section
- [ ] Add tool usage examples
- [ ] Add FAQ section

### Phase 3: Update Documentation
- [ ] Update subscription rule file (`.cursor/rules/subscription.mdc`)
- [ ] Update API documentation
- [ ] Create user-facing pricing guide

### Phase 4: Testing
- [ ] Test all tools with new limits
- [ ] Verify cost calculations
- [ ] Test limit enforcement
- [ ] Test cost cap enforcement
- [ ] Verify pre-flight validation

---

## Cost Calculation Examples

### Example 1: Blog Writer - 1 Blog Post (OSS Models)
```
Research: 3 Exa searches = $0.015
Outline: 1 LLM call (Gemini Flash) = $0.0056
Content: 2 LLM calls (Gemini Flash) = $0.0112
Image: 1 Qwen Image OSS = $0.03 (vs $0.04 Stability)
Total: ~$0.06 per blog post (saved $0.01 with OSS)
```

### Example 2: Story Writer - 1 Story (5 scenes, OSS Models)
```
Outline: 1 LLM call = $0.0056
Script: 1 LLM call = $0.0056
Images: 5 × $0.03 (Qwen Image OSS) = $0.15 (vs $0.20)
Audio: 5 × $0.10 = $0.50
Videos: 5 × $0.25 (WAN 2.5 OSS) = $1.25 (vs $0.50-$2.10)
Total: ~$1.96 per story (higher video cost, but better quality)
```

### Example 3: Podcast Maker - 1 Episode (10 min, 5 scenes, OSS Models)
```
Research: 3 Exa searches = $0.015
Script: 1 LLM call = $0.0056
Outline: 1 LLM call = $0.0056
Audio: 5 × $0.20 (Minimax Speech OSS) = $1.00
Video (optional): 5 × $0.25 (WAN 2.5 OSS) = $1.25
Total: ~$1.03 per podcast (without video)
Total: ~$2.28 per podcast (with video, OSS models)
```

### Example 4: Social Media - 10 Posts (OSS Models)
```
Generation: 10 × 1 LLM call = 10 calls × $0.0056 = $0.056
Images: 10 × $0.03 (Qwen Image OSS) = $0.30 (vs $0.40)
Total: ~$0.36 for 10 posts (saved $0.10 with OSS)
```

---

## Competitive Analysis

### Similar AI Content Platforms

| Platform | Price | Limits | Notes |
|----------|-------|--------|-------|
| **Jasper** | $49/month | 50K words | Text-focused |
| **Copy.ai** | $49/month | Unlimited words | Text-focused |
| **Writesonic** | $19/month | 100K words | Text-focused |
| **ALwrity Basic** | $29/month | 50 LLM calls + media | **Full platform** |

**ALwrity Advantage**: 
- Lower price point ($29 vs $49)
- Includes video, image, audio generation (competitors don't)
- Comprehensive tool suite (not just text)
- Better value proposition

---

## Recommendations Summary

### ✅ **APPROVED: Production-Ready Basic Tier (OSS-Focused)**

**Price**: $29/month ($290/year) - **KEEP**

**Key Changes** (OSS-Focused):
1. ✅ **Increase AI Text Generation**: 10 → **50 calls/month**
2. ✅ **Increase Token Limits**: 20K → **100K per provider**
3. ✅ **Increase Image Generation**: 5 → **50 images/month** (OSS: Qwen Image $0.03)
4. ✅ **Increase Image Editing**: 30 → **50 edits/month** (OSS: Qwen Edit $0.02)
5. ✅ **Increase Video Generation**: 20 → **30 videos/month** (OSS: WAN 2.5 $0.25)
6. ✅ **Increase Audio Generation**: 50 → **100 generations/month** (OSS: Minimax Speech)
7. ✅ **Adjust Cost Cap**: $50 → **$45** (aligns with $40-50 target)
8. ✅ **Default to OSS Models**: Qwen, WAN 2.5, Minimax Speech (cost-efficient)

**Expected Outcomes**:
- Users can experience all ALwrity features with generous limits
- Sustainable cost structure (~$20-35/user/month average with OSS models)
- Competitive pricing ($29 vs competitors $49+)
- Room for margin ($4-17/user/month average)
- Cost cap ($45) protects against losses (hard limit $40-50)
- **OSS models provide 25-50% cost savings** vs proprietary alternatives

**Risk Level**: 🟢 **LOW** (with cost cap enforcement and OSS model defaults)

---

## Implementation Plan

### Phase 1: Update Pricing Service & Database (Priority: HIGH)

#### 1.1 Update `pricing_service.py` Basic Tier Limits
**File**: `backend/services/subscription/pricing_service.py`

**Changes Required**:
```python
# In initialize_default_plans() method
{
    "name": "Basic",
    "tier": SubscriptionTier.BASIC,
    "price_monthly": 29.0,
    "price_yearly": 290.0,
    
    # AI Text Generation (Unified Limit)
    "ai_text_generation_calls_limit": 50,  # Changed from 10
    
    # Token Limits (Per Provider)
    "gemini_tokens_limit": 100000,  # Changed from 20,000
    "openai_tokens_limit": 100000,  # Changed from 20,000
    "anthropic_tokens_limit": 100000,  # Changed from 20,000
    "mistral_tokens_limit": 100000,  # Changed from 20,000
    
    # Search APIs (Keep existing)
    "tavily_calls_limit": 200,
    "serper_calls_limit": 200,
    "metaphor_calls_limit": 100,
    "firecrawl_calls_limit": 100,
    "exa_calls_limit": 500,
    
    # Media Generation (OSS Models via WaveSpeed)
    "stability_calls_limit": 50,  # Changed from 5 (now includes WaveSpeed OSS)
    "image_edit_calls_limit": 50,  # Changed from 30
    "video_calls_limit": 30,  # Changed from 20
    "audio_calls_limit": 100,  # Changed from 50
    
    # Cost Protection
    "monthly_cost_limit": 45.0,  # Changed from 50.0
}
```

**Action Items**:
- [ ] Update `initialize_default_plans()` method in `pricing_service.py`
- [ ] Run database migration to update existing Basic tier subscriptions
- [ ] Test limit enforcement with new values
- [ ] Verify cost calculations reflect OSS model pricing

#### 1.2 Update WaveSpeed Model Pricing in `pricing_service.py`
**File**: `backend/services/subscription/pricing_service.py`

**Changes Required**:
```python
# In initialize_default_pricing() method, update/add WaveSpeed OSS model pricing:

# Image Generation (OSS Models via WaveSpeed)
{
    "provider": APIProvider.IMAGE,
    "model_name": "qwen-image",
    "cost_per_request": 0.03,  # OSS model via WaveSpeed
    "description": "WaveSpeed Qwen Image (OSS) - Fast generation"
},
{
    "provider": APIProvider.IMAGE,
    "model_name": "ideogram-v3-turbo",
    "cost_per_request": 0.05,  # OSS model via WaveSpeed
    "description": "WaveSpeed Ideogram V3 Turbo (OSS) - Photorealistic"
},

# Image Editing (OSS Models via WaveSpeed)
{
    "provider": APIProvider.IMAGE_EDIT,
    "model_name": "qwen-edit",
    "cost_per_request": 0.02,  # OSS model via WaveSpeed
    "description": "WaveSpeed Qwen Image Edit (OSS) - Budget editing"
},
{
    "provider": APIProvider.IMAGE_EDIT,
    "model_name": "qwen-edit-plus",
    "cost_per_request": 0.02,  # OSS model via WaveSpeed
    "description": "WaveSpeed Qwen Image Edit Plus (OSS) - Multi-image"
},
{
    "provider": APIProvider.IMAGE_EDIT,
    "model_name": "flux-kontext-pro",
    "cost_per_request": 0.04,  # OSS model via WaveSpeed
    "description": "WaveSpeed FLUX Kontext Pro (OSS) - Professional"
},

# Video Generation (OSS Models via WaveSpeed)
{
    "provider": APIProvider.VIDEO,
    "model_name": "wan-2.5",
    "cost_per_request": 0.25,  # OSS model via WaveSpeed (~5 seconds)
    "description": "WaveSpeed WAN 2.5 (OSS) - Text-to-Video, Image-to-Video"
},
{
    "provider": APIProvider.VIDEO,
    "model_name": "seedance-1.5-pro",
    "cost_per_request": 0.40,  # OSS model via WaveSpeed (~5 seconds)
    "description": "WaveSpeed Seedance 1.5 Pro (OSS) - Longer duration"
},

# Audio Generation (OSS Models via WaveSpeed)
{
    "provider": APIProvider.AUDIO,
    "model_name": "minimax-speech-02-hd",
    "cost_per_input_token": 0.00005,  # $0.05 per 1K chars
    "cost_per_output_token": 0.0,
    "cost_per_request": 0.0,
    "description": "WaveSpeed Minimax Speech 02 HD (OSS) - High-quality TTS"
},
```

**Action Items**:
- [ ] Add WaveSpeed OSS model pricing entries
- [ ] Update default model selection logic to prefer OSS models
- [ ] Test cost calculation with OSS models
- [ ] Verify pricing accuracy against WaveSpeed API documentation

#### 1.3 Update Default Model Selection Logic
**Files**: 
- `backend/services/llm_providers/main_image_generation.py`
- `backend/services/image_studio/create_service.py`
- `backend/services/image_studio/edit_service.py`
- `backend/services/video_studio/video_service.py`
- `backend/services/audio_generation/audio_service.py`

**Changes Required**:
- Default image generation to `qwen-image` (OSS) instead of Stability
- Default image editing to `qwen-edit` (OSS) instead of Stability
- Default video generation to `wan-2.5` (OSS) instead of HuggingFace
- Default audio generation to `minimax-speech-02-hd` (OSS)

**Action Items**:
- [ ] Update `get_default_provider()` methods to prefer WaveSpeed OSS models
- [ ] Update model selection UI to show OSS models as default/recommended
- [ ] Add cost comparison tooltips showing OSS model savings
- [ ] Test all tools with OSS model defaults

### Phase 2: Update Frontend & Documentation (Priority: HIGH)

#### 2.1 Update Pricing Page
**File**: `docs-site/docs/features/subscription/pricing.md`

**Changes Required**:
- Update Basic tier limits to reflect new values (50 images, 50 edits, 30 videos, 100 audio)
- Add OSS model information and cost savings messaging
- Update cost examples to use OSS model pricing
- Add FAQ about OSS models and cost efficiency

**Action Items**:
- [ ] Update pricing page markdown
- [ ] Update frontend pricing component (if exists)
- [ ] Add OSS model badges/indicators
- [ ] Add cost comparison table (OSS vs proprietary)

#### 2.2 Update Subscription Context & Components
**Files**:
- `frontend/src/contexts/SubscriptionContext.tsx`
- `frontend/src/components/billing/EnhancedBillingDashboard.tsx`
- `frontend/src/components/shared/UsageDashboard.tsx`

**Changes Required**:
- Display OSS model indicators in usage dashboard
- Show cost savings from using OSS models
- Update limit displays to show new Basic tier limits
- Add tooltips explaining OSS model benefits

**Action Items**:
- [ ] Update limit displays in billing dashboard
- [ ] Add OSS model indicators in cost breakdown
- [ ] Update usage statistics to reflect new limits
- [ ] Test UI with new limit values

### Phase 3: Testing & Validation (Priority: CRITICAL)

#### 3.1 Limit Enforcement Testing
**Test Cases**:
- [ ] Test 50 AI text generation calls limit
- [ ] Test 50 image generation limit (OSS models)
- [ ] Test 50 image editing limit (OSS models)
- [ ] Test 30 video generation limit (OSS models)
- [ ] Test 100 audio generation limit (OSS models)
- [ ] Test $45 monthly cost cap enforcement
- [ ] Test pre-flight validation with new limits
- [ ] Test limit exceeded error messages

#### 3.2 Cost Calculation Testing
**Test Cases**:
- [ ] Verify Qwen Image cost: $0.03 per image
- [ ] Verify Qwen Edit cost: $0.02 per edit
- [ ] Verify WAN 2.5 video cost: $0.25 per video
- [ ] Verify Minimax Speech cost: $0.05 per 1K chars
- [ ] Test cost aggregation across all operations
- [ ] Test cost cap enforcement at $45
- [ ] Verify cost display in billing dashboard

#### 3.3 OSS Model Integration Testing
**Test Cases**:
- [ ] Test Qwen Image generation via WaveSpeed
- [ ] Test Qwen Edit editing via WaveSpeed
- [ ] Test WAN 2.5 video generation via WaveSpeed
- [ ] Test Minimax Speech audio generation via WaveSpeed
- [ ] Verify default model selection uses OSS models
- [ ] Test model fallback if OSS model unavailable
- [ ] Verify cost tracking for OSS models

### Phase 4: Database Migration (Priority: HIGH)

#### 4.1 Create Migration Script
**File**: `backend/database/migrations/update_basic_tier_limits_oss.py`

**Script Requirements**:
```python
"""
Migration: Update Basic Tier Limits for OSS-Focused Pricing Strategy
- Increase AI text generation: 10 → 50
- Increase token limits: 20K → 100K per provider
- Increase image generation: 5 → 50
- Increase image editing: 30 → 50
- Increase video generation: 20 → 30
- Increase audio generation: 50 → 100
- Adjust cost cap: $50 → $45
"""

def upgrade():
    # Update SubscriptionPlan for Basic tier
    # Update existing UserSubscription records
    # Clear pricing service cache
    pass

def downgrade():
    # Revert to previous limits if needed
    pass
```

**Action Items**:
- [ ] Create migration script
- [ ] Test migration on staging database
- [ ] Backup production database before migration
- [ ] Run migration during maintenance window
- [ ] Verify all subscriptions updated correctly

### Phase 5: Monitoring & Adjustment (Priority: MEDIUM)

#### 5.1 Set Up Monitoring
**Metrics to Track**:
- Average cost per user per month
- Users hitting $45 cost cap
- Users hitting individual limits
- OSS model usage vs proprietary model usage
- Cost savings from OSS models

**Action Items**:
- [ ] Set up cost monitoring dashboard
- [ ] Create alerts for cost cap breaches
- [ ] Track OSS model adoption rate
- [ ] Monitor user satisfaction with limits

#### 5.2 Adjustment Plan
**Triggers for Adjustment**:
- If average cost > $35/user: Consider reducing limits
- If >15% users hit cost cap: Consider increasing cost cap to $50
- If <20% users use video/audio: Consider reducing those limits
- If OSS models unavailable: Fallback to proprietary models

**Action Items**:
- [ ] Define adjustment criteria
- [ ] Create adjustment workflow
- [ ] Plan communication strategy for limit changes

---

## Next Steps (Priority Order)

1. **CRITICAL**: Update `pricing_service.py` with new Basic tier limits
2. **CRITICAL**: Add WaveSpeed OSS model pricing to `pricing_service.py`
3. **HIGH**: Update default model selection to prefer OSS models
4. **HIGH**: Create and run database migration
5. **HIGH**: Update pricing page documentation
6. **HIGH**: Test limit enforcement and cost calculations
7. **MEDIUM**: Update frontend components with new limits
8. **MEDIUM**: Set up monitoring and alerts
9. **LOW**: Add OSS model indicators to UI

---

## Monitoring & Adjustment Plan

### Key Metrics to Track
- Average LLM calls per user per month
- Average media generation per user per month
- Average cost per user per month
- Users hitting cost cap
- Users hitting individual limits

### Adjustment Triggers
- **If average cost > $25/user**: Consider reducing limits
- **If >20% users hit cost cap**: Consider increasing cost cap
- **If <10% users use video/audio**: Consider reducing those limits
- **If churn rate high**: Consider increasing limits

### Review Schedule
- **Week 1-2**: Daily monitoring
- **Month 1**: Weekly review
- **Month 2-3**: Bi-weekly review
- **Month 4+**: Monthly review

---

## Conclusion

The proposed Basic tier limits (OSS-Focused) provide:
- ✅ **Access to all ALwrity features** with generous limits
- ✅ **Sustainable cost structure** using OSS models (25-50% savings)
- ✅ **Competitive pricing** ($29 vs competitors $49+)
- ✅ **Protection against losses** ($45 cost cap, hard limit $40-50)
- ✅ **Room for growth** (can adjust based on usage)
- ✅ **OSS-first strategy** (Qwen, FLUX, Ideogram, WAN 2.5, Minimax Speech)
- ✅ **Maximum user value** while staying within cost constraints

**Key Advantages of OSS-Focused Strategy**:
1. **Cost Efficiency**: 25-50% cost savings vs proprietary models
2. **Better Limits**: Can offer more generations due to lower costs
3. **User Value**: More value for the same $29/month price
4. **Sustainability**: Lower costs = better margins = sustainable business
5. **Flexibility**: Can adjust limits based on actual usage patterns

**Recommendation**: **APPROVE** for production launch with OSS-focused strategy.

**Confidence Level**: 🟢 **HIGH** (with proper monitoring, cost cap enforcement, and OSS model defaults)

**Risk Mitigation**:
- $45 cost cap protects against losses (hard limit $40-50)
- OSS model defaults ensure cost efficiency
- Monitoring allows quick adjustment if needed
- Realistic usage assumptions (60-70% of limits)
