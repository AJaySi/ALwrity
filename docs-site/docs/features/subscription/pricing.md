# Subscription Plans & API Pricing

End-to-end reference for ALwrity's usage-based subscription tiers, API cost configuration, and plan-specific limits. All data is sourced from `backend/services/subscription/pricing_service.py`.

## Subscription Plans

> **Legend**: `∞` = Unlimited. Limits reset at the start of each billing cycle.

| Plan | Price (Monthly / Yearly) | AI Text Generation Calls* | Token Limits (per provider) | Key API Limits | Video Generation | Monthly Cost Cap | Highlights |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **Free** | `$0 / $0` | 100 Gemini • 50 Mistral (legacy enforcement) | 100K Gemini tokens | 20 Tavily • 20 Serper • 10 Metaphor • 10 Firecrawl • 5 Stability • 100 Exa | Not included | `$0` | Basic content generation & limited research |
| **Basic** | `$29 / $290` | **10 unified LLM calls** (Gemini + OpenAI + Anthropic + Mistral combined) | 20K tokens each (Gemini, OpenAI, Anthropic, Mistral) | 200 Tavily • 200 Serper • 100 Metaphor • 100 Firecrawl • 5 Stability • 500 Exa | 20 videos/mo | `$50` | Full content generation, advanced research, basic analytics |
| **Pro** | `$79 / $790` | 5K Gemini • 2.5K OpenAI • 1K Anthropic • 2.5K Mistral | 5M Gemini • 2.5M OpenAI • 1M Anthropic • 2.5M Mistral | 1K Tavily • 1K Serper • 500 Metaphor • 500 Firecrawl • 200 Stability • 2K Exa | 50 videos/mo | `$150` | Premium research, advanced analytics, priority support |
| **Enterprise** | `$199 / $1,990` | ∞ across all LLM providers | ∞ | ∞ across every research/media API | ∞ | `$500` | White-label, dedicated support, custom integrations |

\*The Basic plan now enforces a **unified** `ai_text_generation_calls_limit` of 10 requests across all LLM providers. Legacy per-provider columns remain for analytics dashboards but do not control enforcement.

### Plan Feature Notes
- **Video Generation**: Powered by Hugging Face `tencent/HunyuanVideo` ($0.10 per request). Plan limits are shown above.
- **Image Generation**: Stability AI billed at $0.04/image. Limits shown under “Key API Limits”.
- **Research APIs**: Tavily, Serper, Metaphor, Exa, and Firecrawl are individually rate-limited per plan.
- **Cost Caps**: `monthly_cost_limit` hard stops spend at $50 / $150 / $500 for paid tiers. Enterprise caps are adjustable via support.

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
- Tavily — $0.001 per search
- Serper — $0.001 per search
- Metaphor — $0.003 per search
- Exa — $0.005 per search (1–25 results)
- Firecrawl — $0.002 per crawled page
- Stability AI — $0.04 per image
- Video Generation (HunyuanVideo) — $0.10 per video request

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
| Video Generation (Basic plan) | 1 request × $0.10 | **$0.10** (counts toward 20-video quota) |

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

**Last Updated**: November 2025

