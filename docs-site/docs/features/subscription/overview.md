# Subscription System Overview

ALwrity's usage-based subscription system provides comprehensive API cost tracking, usage limits, and real-time monitoring for all external API providers.

## Features

### Core Functionality
- **Usage-Based Billing**: Track API calls, tokens, and costs across all providers
- **Subscription Tiers**: Free, Basic, Pro, and Enterprise plans with different limits
- **Real-Time Monitoring**: Live usage tracking and limit enforcement
- **Cost Calculation**: Accurate pricing for Gemini, OpenAI, Anthropic, and other APIs
- **Usage Alerts**: Automatic notifications at 80%, 90%, and 100% usage thresholds
- **Robust Error Handling**: Comprehensive logging and exception management

### Supported API Providers
- **Gemini API**: Google's AI models with latest pricing
- **OpenAI**: GPT models and embeddings
- **Anthropic**: Claude models
- **Mistral AI**: Mistral models
- **Tavily**: AI-powered search
- **Serper**: Google search API
- **Metaphor/Exa**: Advanced search
- **Firecrawl**: Web content extraction
- **Stability AI**: Image generation
- **Hugging Face**: GPT-OSS-120B via Groq

## Architecture

### Database Schema

The system uses the following core tables:

- `subscription_plans`: Available subscription tiers and limits
- `user_subscriptions`: User subscription information
- `api_usage_logs`: Detailed log of every API call
- `usage_summaries`: Aggregated usage per user per billing period
- `api_provider_pricing`: Pricing configuration for all providers
- `usage_alerts`: Usage notifications and warnings
- `billing_history`: Historical billing records

### Service Structure

```
backend/services/subscription/
├── __init__.py              # Package exports
├── pricing_service.py       # API pricing and cost calculations
├── usage_tracking_service.py # Usage tracking and limits
├── exception_handler.py      # Exception handling
└── monitoring_middleware.py # API monitoring middleware
```

### Core Services

#### Pricing Service
- Real-time cost calculation for all API providers
- Subscription limit management
- Usage validation and enforcement
- Support for Gemini, OpenAI, Anthropic, Mistral, and search APIs

#### Usage Tracking Service
- Comprehensive API usage tracking
- Real-time usage statistics
- Trend analysis and projections
- Automatic alert generation at 80%, 90%, and 100% thresholds

#### Exception Handler
- Robust error handling with detailed logging
- Structured exception types for different scenarios
- Automatic alert creation for critical errors
- User-friendly error messages

### Enhanced Middleware

The system automatically tracks API usage through enhanced middleware:

- **Automatic API Provider Detection**: Identifies Gemini, OpenAI, Anthropic, etc.
- **Token Estimation**: Estimates usage from request/response content
- **Pre-Request Validation**: Enforces usage limits before processing
- **Cost Tracking**: Real-time cost calculation and logging
- **Usage Limit Enforcement**: Returns 429 errors when limits exceeded

## Key Capabilities

### Usage-Based Billing
- ✅ **Real-time cost tracking** for all API providers
- ✅ **Token-level precision** for LLM APIs (Gemini, OpenAI, Anthropic)
- ✅ **Request-based pricing** for search APIs (Tavily, Serper, Metaphor)
- ✅ **Automatic cost calculation** with configurable pricing

### Subscription Management
- ✅ **4 Subscription Tiers**: Free, Basic ($29/mo), Pro ($79/mo), Enterprise ($199/mo)
- ✅ **Flexible limits**: API calls, tokens, and monthly cost caps
- ✅ **Usage enforcement**: Pre-request validation and blocking
- ✅ **Billing cycle support**: Monthly and yearly options

### Monitoring & Analytics
- ✅ **Real-time dashboard** with usage statistics
- ✅ **Usage trends** and projections
- ✅ **Provider-specific breakdowns** (Gemini, OpenAI, etc.)
- ✅ **Performance metrics** (response times, error rates)

### Alert System
- ✅ **Automatic notifications** at 80%, 90%, and 100% usage
- ✅ **Multi-channel alerts** (database, logs, future email integration)
- ✅ **Alert management** (mark as read, severity levels)
- ✅ **Usage recommendations** and upgrade prompts

## Security & Privacy

### Data Protection
- User usage data is encrypted at rest
- API keys are never logged in usage tracking
- Sensitive information is excluded from error logs
- GDPR-compliant data handling

### Rate Limiting
- Pre-request usage validation
- Automatic limit enforcement
- Graceful degradation when limits are reached
- User-friendly error messages

## Exception Types

The system uses structured exception types:

- `UsageLimitExceededException`: When usage limits are reached
- `PricingException`: Pricing calculation errors
- `TrackingException`: Usage tracking failures
- `SubscriptionException`: General subscription errors

## Customization

### Adding New API Providers
1. Add provider to `APIProvider` enum
2. Configure pricing in `api_provider_pricing` table
3. Update detection patterns in middleware
4. Add usage tracking logic

### Modifying Subscription Plans
1. Update plans in database or via API
2. Modify limits and pricing
3. Add/remove features
4. Update billing integration

## Next Steps

- [Setup Guide](setup.md) - Installation and configuration
- [API Reference](api-reference.md) - Endpoint documentation
- [Pricing](pricing.md) - Subscription plans and API pricing
- [Frontend Integration](frontend-integration.md) - Technical specifications
- [Implementation Status](implementation-status.md) - Current features and metrics

---

**Version**: 1.0.0  
**Last Updated**: January 2025

