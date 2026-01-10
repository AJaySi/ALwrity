# Subscription Plans & API Pricing

End-to-end reference for ALwrity's usage-based subscription tiers, API cost configuration, and plan-specific limits. All data is sourced from `backend/services/subscription/pricing_service.py`.

## Subscription Plans

> **Legend**: `∞` = Unlimited. Limits reset at the start of each billing cycle.

| Plan | Price (Monthly / Yearly) | AI Text Generation Calls* | Token Limits (per provider) | Key API Limits | Video Generation | Image Editing | Audio Generation | Monthly Cost Cap | Highlights |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Free** | `$0 / $0` | 100 Gemini • 50 Mistral (legacy enforcement) | 100K Gemini tokens | 20 Tavily • 20 Serper • 10 Metaphor • 10 Firecrawl • 5 Stability • 100 Exa | Not included | 10 edits/mo | 20 generations/mo | `$0` | Basic content generation & limited research |
| **Basic** | `$29 / $290` | **50 unified LLM calls** (Gemini + OpenAI + Anthropic + Mistral combined) | 100K tokens each (Gemini, OpenAI, Anthropic, Mistral) | 200 Tavily • 200 Serper • 100 Metaphor • 100 Firecrawl • **50 Images** (OSS models) • 500 Exa | **30 videos/mo** (OSS: WAN 2.5) | **50 edits/mo** (OSS: Qwen Edit) | **100 generations/mo** (OSS: Minimax Speech) | `$45` | **OSS-powered**: Full content generation, advanced research, all tools access |
| **Pro** | `$79 / $790` | 5K Gemini • 2.5K OpenAI • 1K Anthropic • 2.5K Mistral | 5M Gemini • 2.5M OpenAI • 1M Anthropic • 2.5M Mistral | 1K Tavily • 1K Serper • 500 Metaphor • 500 Firecrawl • 200 Stability • 2K Exa | 50 videos/mo | 100 edits/mo | 200 generations/mo | `$150` | Premium research, advanced analytics, priority support |
| **Enterprise** | `$199 / $1,990` | ∞ across all LLM providers | ∞ | ∞ across every research/media API | ∞ | ∞ | ∞ | `$500` | White-label, dedicated support, custom integrations |

\*The Basic plan enforces a **unified** `ai_text_generation_calls_limit` of **50 requests** across all LLM providers (increased from 10). Legacy per-provider columns remain for analytics dashboards but do not control enforcement.

**OSS Models**: Basic tier prioritizes Open-Source AI models via WaveSpeed for cost efficiency:
- **Image Generation**: Qwen Image ($0.03) or Ideogram V3 Turbo ($0.05)
- **Image Editing**: Qwen Edit ($0.02) or FLUX Kontext Pro ($0.04)
- **Video Generation**: WAN 2.5 ($0.25 per ~5s video)
- **Audio Generation**: Minimax Speech 02 HD ($0.05 per 1K characters)

### Plan Feature Notes

#### OSS-First Strategy (Basic Tier)
The Basic tier prioritizes **Open-Source AI models** via WaveSpeed for cost efficiency, allowing more generous limits:
- **Image Generation**: Defaults to **Qwen Image OSS** ($0.03/image) vs Stability ($0.04/image) - **25% savings**
- **Image Editing**: Defaults to **Qwen Edit OSS** ($0.02/edit) vs Stability ($0.04/edit) - **50% savings**
- **Video Generation**: Defaults to **WAN 2.5 OSS** ($0.25/video) - Better quality/value than HuggingFace
- **Audio Generation**: Uses **Minimax Speech 02 HD OSS** ($0.05 per 1K chars) - High-quality TTS

#### Other Features
- **Video Generation**: Basic tier uses WAN 2.5 OSS ($0.25 per ~5s video). Pro/Enterprise can use HuggingFace `tencent/HunyuanVideo` ($0.10) or premium models.
- **Image Generation**: Basic tier uses OSS models (Qwen Image $0.03, Ideogram V3 Turbo $0.05). Pro/Enterprise can use Stability AI ($0.04/image) or premium models.
- **Research APIs**: Tavily, Serper, Metaphor, Exa, and Firecrawl are individually rate-limited per plan.
- **Cost Caps**: `monthly_cost_limit` hard stops spend at $45 (Basic) / $150 (Pro) / $500 (Enterprise). Enterprise caps are adjustable via support.

## Provider Pricing Matrix

### Gemini 2.5 & 1.5 (Google)
- `gemini-2.5-pro` — $0.00000125 input / $0.00001 output per token ($1.25 / $10 per 1M tokens)
- `gemini-2.5-pro-large` — $0.0000025 / $0.000015 per token (large context)
- `gemini-2.5-flash` — $0.0000003 / $0.0000025 per token
- `gemini-2.5-flash-audio` — $0.000001 / $0.0000025 per token
- `gemini-2.5-flash-lite` — $0.0000001 / $0.0000004 per token
- `gemini-2.5-flash-lite-audio` — $0.0000003 / $0.0000004 per token
- `gemini-1.5-flash` — $0.000000075 / $0.0000003 per token
- `gemini-1.5-flash-8b` — $0.0000000375 / $0.00000015 per token
- `gemini-1.5-pro` — $0.00000125 / $0.000005 per token
- `gemini-1.5-pro-large` — $0.0000025 / $0.00001 per token
- `gemini-embedding` — $0.00000015 per input token
- `gemini-grounding-search` — $35 per 1,000 requests after the free tier

### OpenAI (estimates — update when official pricing changes)
- `gpt-4o` — $0.0000025 input / $0.00001 output per token
- `gpt-4o-mini` — $0.00000015 input / $0.0000006 output per token

### Anthropic
- `claude-3.5-sonnet` — $0.000003 input / $0.000015 output per token

### Hugging Face / Mistral (GPT-OSS-120B via Groq)
Pricing is configurable through environment variables:
```
HUGGINGFACE_INPUT_TOKEN_COST=0.000001   # $1 per 1M tokens
HUGGINGFACE_OUTPUT_TOKEN_COST=0.000003  # $3 per 1M tokens
```
Models covered: `openai/gpt-oss-120b:groq`, `gpt-oss-120b`, and `default` (fallback).

### Search, Image, and Video APIs

#### Search APIs
- Tavily — $0.001 per search
- Serper — $0.001 per search
- Metaphor — $0.003 per search
- Exa — $0.005 per search (1–25 results)
- Firecrawl — $0.002 per crawled page

#### Image Generation (OSS Models via WaveSpeed)
- **Qwen Image** (OSS) — $0.03 per image ⭐ **Default for Basic tier**
- **Ideogram V3 Turbo** (OSS) — $0.05 per image (photorealistic, text rendering)
- Stability AI — $0.04 per image (Pro/Enterprise)

#### Image Editing (OSS Models via WaveSpeed)
- **Qwen Image Edit** (OSS) — $0.02 per edit ⭐ **Default for Basic tier**
- **Qwen Image Edit Plus** (OSS) — $0.02 per edit (multi-image)
- **FLUX Kontext Pro** (OSS) — $0.04 per edit (professional, typography)

#### Video Generation
- **WAN 2.5** (OSS) — $0.25 per video (~5 seconds) ⭐ **Default for Basic tier**
- **Seedance 1.5 Pro** (OSS) — $0.40 per video (~5 seconds, longer duration)
- HunyuanVideo (HuggingFace) — $0.10 per video request
- Kling v2.5 Turbo (5s) — $0.21 per video
- Kling v2.5 Turbo (10s) — $0.42 per video

#### Audio Generation (OSS Models via WaveSpeed)
- **Minimax Speech 02 HD** (OSS) — $0.05 per 1,000 characters ⭐ **Default**

## Updating Pricing & Plans

1. **Initial Seed** — `python backend/scripts/create_subscription_tables.py` creates plans and pricing.
2. **Env Overrides** — Hugging Face pricing refreshes from `HUGGINGFACE_*` vars every boot.
3. **Scripts & Maintenance** — Use `backend/scripts/` utilities (e.g., `update_basic_plan_limits.py`, `cap_basic_plan_usage.py`) to roll forward changes.
4. **Direct DB Edits** — Modify `subscription_plans` or `api_provider_pricing` tables for emergency adjustments.

## Cost Examples

| Scenario | Calculation | Cost |
| --- | --- | --- |
| Gemini 2.5 Flash (1K input / 500 output tokens) | (1,000 × 0.0000003) + (500 × 0.0000025) | **$0.00155** |
| Tavily Search | 1 request × $0.001 | **$0.001** |
| Hugging Face GPT-OSS-120B (2K in / 1K out) | (2,000 × 0.000001) + (1,000 × 0.000003) | **$0.005** |
| Image Generation (Basic - Qwen Image OSS) | 1 image × $0.03 | **$0.03** (counts toward 50-image quota) |
| Image Editing (Basic - Qwen Edit OSS) | 1 edit × $0.02 | **$0.02** (counts toward 50-edit quota) |
| Video Generation (Basic - WAN 2.5 OSS) | 1 video × $0.25 | **$0.25** (counts toward 30-video quota) |
| Audio Generation (Basic - Minimax Speech OSS) | 2,000 chars × $0.05/1K | **$0.10** (counts toward 100-audio quota) |

## Enforcement & Monitoring

1. Middleware estimates usage and calls `UsageTrackingService.track_api_usage`.
2. `UsageService.enforce_usage_limits` validates the request before the downstream provider call.
3. When a limit would be exceeded, the API returns `429` with upgrade guidance.
4. The Billing Dashboard (`/billing`) shows real-time usage, cost projections, provider breakdowns, renewal history, and usage logs.

## Additional Resources

- [Billing Dashboard](billing-dashboard.md)
- [API Reference](api-reference.md)
- [Setup Guide](setup.md)
- [Gemini Pricing](https://ai.google.dev/gemini-api/docs/pricing)
- [OpenAI Pricing](https://openai.com/pricing)

---

**Last Updated**: January 2026

**Recent Changes** (OSS-Focused Strategy):
- ✅ Basic tier limits increased: 50 AI calls (was 10), 100K tokens (was 20K), 50 images (was 5), 50 edits (was 30), 30 videos (was 20), 100 audio (was 50)
- ✅ Cost cap adjusted: $45 (was $50) to align with $40-50 hard limit target
- ✅ OSS models prioritized: Qwen Image ($0.03), Qwen Edit ($0.02), WAN 2.5 ($0.25), Minimax Speech ($0.05/1K chars)
- ✅ 25-50% cost savings vs proprietary models enable more generous limits

