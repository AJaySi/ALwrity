# Subscription Documentation Update Plan

## 🔄 **SUPERSEDED BY NEW SSOT DOCUMENT**

**⚠️ IMPORTANT**: This document has been superseded by the comprehensive security review.

### **New Single Source of Truth (SSOT)**
📄 **Document**: `SUBSCRIPTION_SYSTEM_SECURITY_SSOT.md`
📅 **Date**: 2026-02-11
🎯 **Purpose**: Complete security review, architecture documentation, and implementation guidelines

### **What's Covered in New SSOT**
✅ **Complete Security Review**: All security findings and recommendations
✅ **Architecture Documentation**: System components and data flow
✅ **Implementation Guidelines**: Security patterns and best practices
✅ **Production Readiness**: Checklist and roadmap
✅ **Maintenance Procedures**: Ongoing security processes
✅ **Related Documentation**: Links to all existing docs

### **Previous Issues (Now Addressed in SSOT)**
1. **Pricing Page Discrepancies** → ✅ Covered in SSOT security review
2. **Missing Billing Dashboard Documentation** → ✅ Referenced in SSOT architecture
3. **Outdated Implementation Status** → ✅ Current state documented in SSOT

### **Migration Status**
🔄 **COMPLETE**: All relevant information migrated to new SSOT document
📋 **Action**: Use `SUBSCRIPTION_SYSTEM_SECURITY_SSOT.md` as primary reference
🗑️ **Archive**: This document retained for historical reference only

---

## 📚 **Recommended Reference Path**

**For all subscription system documentation:**
1. **Primary**: `SUBSCRIPTION_SYSTEM_SECURITY_SSOT.md` (Security & Architecture)
2. **Pricing**: `PRODUCTION_PRICING_STRATEGY.md` (Pricing strategy)
3. **Implementation**: `PRE_FLIGHT_CHECKLIST.md` (Feature validation)
4. **Historical**: This document (Archive reference only)

---

## 🎯 **Next Steps**

Refer to `SUBSCRIPTION_SYSTEM_SECURITY_SSOT.md` for:
- 🚨 Critical security issues requiring immediate attention
- 📋 Implementation guidelines for security improvements
- 🏗️ Complete system architecture documentation
- 📊 Production readiness checklist and timeline

## Actual Values from Code

### Subscription Plans (from `pricing_service.py`)

#### Free Tier
- Price: $0/month, $0/year
- Gemini calls: 100/month
- OpenAI calls: 0
- Anthropic calls: 0
- Mistral calls: 50/month
- Tavily calls: 20/month
- Serper calls: 20/month
- Metaphor calls: 10/month
- Firecrawl calls: 10/month
- Stability calls: 5/month
- Exa calls: 100/month
- Video calls: 0
- Gemini tokens: 100,000/month
- Monthly cost limit: $0.0
- Features: ["basic_content_generation", "limited_research"]

#### Basic Tier
- Price: $29/month, $290/year
- **ai_text_generation_calls_limit: 10** (unified limit for all LLM providers)
- Gemini calls: 1000/month (legacy, not used for enforcement)
- OpenAI calls: 500/month (legacy)
- Anthropic calls: 200/month (legacy)
- Mistral calls: 500/month (legacy)
- Tavily calls: 200/month
- Serper calls: 200/month
- Metaphor calls: 100/month
- Firecrawl calls: 100/month
- Stability calls: 5/month
- Exa calls: 500/month
- Video calls: 20/month
- Gemini tokens: 20,000/month (increased from 5,000)
- OpenAI tokens: 20,000/month
- Anthropic tokens: 20,000/month
- Mistral tokens: 20,000/month
- Monthly cost limit: $50.0
- Features: ["full_content_generation", "advanced_research", "basic_analytics"]

#### Pro Tier
- Price: $79/month, $790/year
- Gemini calls: 5000/month
- OpenAI calls: 2500/month
- Anthropic calls: 1000/month
- Mistral calls: 2500/month
- Tavily calls: 1000/month
- Serper calls: 1000/month
- Metaphor calls: 500/month
- Firecrawl calls: 500/month
- Stability calls: 200/month
- Exa calls: 2000/month
- Video calls: 50/month
- Gemini tokens: 5,000,000/month
- OpenAI tokens: 2,500,000/month
- Anthropic tokens: 1,000,000/month
- Mistral tokens: 2,500,000/month
- Monthly cost limit: $150.0
- Features: ["unlimited_content_generation", "premium_research", "advanced_analytics", "priority_support"]

#### Enterprise Tier
- Price: $199/month, $1990/year
- All calls: Unlimited (0 = unlimited)
- All tokens: Unlimited (0 = unlimited)
- Video calls: Unlimited
- Monthly cost limit: $500.0
- Features: ["unlimited_everything", "white_label", "dedicated_support", "custom_integrations"]

### API Pricing (from `pricing_service.py`)

#### Gemini API Models
- **gemini-2.5-pro**: $1.25/$10.00 per 1M input/output tokens
- **gemini-2.5-pro-large**: $2.50/$15.00 per 1M input/output tokens
- **gemini-2.5-flash**: $0.30/$2.50 per 1M input/output tokens
- **gemini-2.5-flash-audio**: $1.00/$2.50 per 1M input/output tokens
- **gemini-2.5-flash-lite**: $0.10/$0.40 per 1M input/output tokens
- **gemini-2.5-flash-lite-audio**: $0.30/$0.40 per 1M input/output tokens
- **gemini-1.5-flash**: $0.075/$0.30 per 1M input/output tokens
- **gemini-1.5-flash-large**: $0.15/$0.60 per 1M input/output tokens
- **gemini-1.5-flash-8b**: $0.0375/$0.15 per 1M input/output tokens
- **gemini-1.5-flash-8b-large**: $0.075/$0.30 per 1M input/output tokens
- **gemini-1.5-pro**: $1.25/$5.00 per 1M input/output tokens
- **gemini-1.5-pro-large**: $2.50/$10.00 per 1M input/output tokens
- **gemini-embedding**: $0.15 per 1M input tokens
- **gemini-grounding-search**: $35 per 1,000 requests (after free tier)

#### OpenAI Models
- **gpt-4o**: $2.50/$10.00 per 1M input/output tokens
- **gpt-4o-mini**: $0.15/$0.60 per 1M input/output tokens

#### Anthropic Models
- **claude-3.5-sonnet**: $3.00/$15.00 per 1M input/output tokens

#### HuggingFace/Mistral (GPT-OSS-120B via Groq)
- Configurable via env vars: `HUGGINGFACE_INPUT_TOKEN_COST` and `HUGGINGFACE_OUTPUT_TOKEN_COST`
- Default: $1/$3 per 1M input/output tokens

#### Search APIs
- **Tavily**: $0.001 per search
- **Serper**: $0.001 per search
- **Metaphor**: $0.003 per search
- **Exa**: $0.005 per search (1-25 results)
- **Firecrawl**: $0.002 per page

#### Other APIs
- **Stability AI**: $0.04 per image
- **Video Generation (HunyuanVideo)**: $0.10 per video generation

## Billing Dashboard Components

### Available Components
1. **BillingDashboard** (`components/billing/BillingDashboard.tsx`) - Main dashboard
2. **EnhancedBillingDashboard** (`components/billing/EnhancedBillingDashboard.tsx`) - Enhanced version
3. **CompactBillingDashboard** (`components/billing/CompactBillingDashboard.tsx`) - Compact version
4. **BillingPage** (`pages/BillingPage.tsx`) - Dedicated billing page route

### Features to Document
- Real-time usage monitoring
- Cost breakdown by provider
- Usage trends and projections
- System health indicators
- Usage alerts
- Subscription renewal history
- Usage logs table
- Comprehensive API breakdown

## Update Plan

### 1. Update Pricing Page (`docs-site/docs/features/subscription/pricing.md`)
- [ ] Update all subscription plan limits to match actual database values
- [ ] Add unified `ai_text_generation_calls_limit` explanation for Basic plan
- [ ] Update Gemini API pricing with all current models
- [ ] Update OpenAI pricing with actual values (gpt-4o, gpt-4o-mini)
- [ ] Update Anthropic pricing with actual values (claude-3.5-sonnet)
- [ ] Add Exa search pricing ($0.005 per search)
- [ ] Add video generation pricing and limits
- [ ] Add yearly pricing for all plans
- [ ] Update token limits to reflect actual values (20K for Basic, not 1M/500K)
- [ ] Add all search API limits per plan
- [ ] Add image generation limits per plan
- [ ] Add video generation limits per plan

### 2. Create/Update Billing Dashboard Documentation
- [ ] Create new page: `docs-site/docs/features/subscription/billing-dashboard.md`
- [ ] Document billing page route (`/billing`)
- [ ] Document all dashboard components (BillingDashboard, Enhanced, Compact)
- [ ] Document features: usage monitoring, cost breakdown, trends, alerts
- [ ] Document subscription renewal history component
- [ ] Document usage logs table
- [ ] Document comprehensive API breakdown component
- [ ] Add screenshots or descriptions of dashboard views
- [ ] Document how to access billing dashboard

### 3. Update Overview Page
- [ ] Add billing dashboard to features list
- [ ] Update supported API providers list (add Exa, Video generation)
- [ ] Update architecture to mention billing dashboard

### 4. Update Implementation Status
- [ ] Update to reflect billing dashboard implementation
- [ ] Add subscription renewal history feature
- [ ] Add usage logs table feature
- [ ] Update component count and features

### 5. Update API Reference
- [ ] Verify all endpoints are documented
- [ ] Add any missing endpoints for renewal history or usage logs

### 6. Update Navigation
- [ ] Add billing dashboard page to mkdocs.yml navigation

## Priority Order

1. **High Priority**: Update pricing page with correct values (users need accurate info)
2. **High Priority**: Create billing dashboard documentation (major feature missing)
3. **Medium Priority**: Update overview and implementation status
4. **Low Priority**: Update API reference and navigation

## Files to Update

1. `docs-site/docs/features/subscription/pricing.md` - Major update needed
2. `docs-site/docs/features/subscription/overview.md` - Minor updates
3. `docs-site/docs/features/subscription/implementation-status.md` - Updates needed
4. `docs-site/docs/features/subscription/billing-dashboard.md` - **NEW FILE**
5. `docs-site/mkdocs.yml` - Add billing dashboard to nav

## Notes

- The Basic plan has a critical unified limit: `ai_text_generation_calls_limit: 10` - this applies to ALL LLM providers combined (Gemini, OpenAI, Anthropic, Mistral)
- Token limits for Basic plan are much lower than documented: 20K per provider, not 1M/500K
- Video generation is a new feature with pricing and limits per plan
- Exa search is a separate provider from Metaphor with different pricing
- Multiple Gemini models exist with different pricing tiers
- Billing dashboard is a dedicated page, not just a component in main dashboard

