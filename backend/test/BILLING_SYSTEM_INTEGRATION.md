# ALwrity Billing & Subscription System Integration

## Overview

The ALwrity backend now includes a comprehensive billing and subscription system that automatically tracks API usage, calculates costs, and manages subscription limits. This system is fully integrated into the startup process and provides real-time monitoring capabilities.

## 🚀 Quick Start

### 1. Start the Backend with Billing System

```bash
# From the backend directory
python start_alwrity_backend.py
```

The startup script will automatically:
- ✅ Create billing and subscription database tables
- ✅ Initialize default pricing and subscription plans
- ✅ Set up usage tracking middleware
- ✅ Verify all billing components are working
- ✅ Start the server with billing endpoints enabled

### 2. Verify Installation

```bash
# Run the comprehensive verification script
python verify_billing_setup.py
```

### 3. Test API Endpoints

```bash
# Get subscription plans
curl http://localhost:8000/api/subscription/plans

# Get user usage (replace 'demo' with actual user ID)
curl http://localhost:8000/api/subscription/usage/demo

# Get billing dashboard data
curl http://localhost:8000/api/subscription/dashboard/demo

# Get API pricing information
curl http://localhost:8000/api/subscription/pricing
```

## 📊 Database Tables

The billing system creates the following tables:

| Table Name | Purpose |
|------------|---------|
| `subscription_plans` | Available subscription tiers and pricing |
| `user_subscriptions` | User subscription assignments |
| `api_usage_logs` | Detailed API usage tracking |
| `usage_summaries` | Aggregated usage statistics |
| `api_provider_pricing` | Cost per token for each AI provider |
| `usage_alerts` | Usage limit warnings and notifications |
| `billing_history` | Historical billing records |

## 🔧 System Components

### 1. Database Models (`models/subscription_models.py`)
- **SubscriptionPlan**: Subscription tiers and pricing
- **UserSubscription**: User subscription assignments
- **APIUsageLog**: Detailed usage tracking
- **UsageSummary**: Aggregated statistics
- **APIProviderPricing**: Cost calculations
- **UsageAlert**: Limit notifications

### 2. Services
- **PricingService** (`services/pricing_service.py`): Cost calculations and plan management
- **UsageTrackingService** (`services/usage_tracking_service.py`): Usage monitoring and limits
- **SubscriptionExceptionHandler** (`services/subscription_exception_handler.py`): Error handling

### 3. API Endpoints (`api/subscription_api.py`)
- `GET /api/subscription/plans` - Available subscription plans
- `GET /api/subscription/usage/{user_id}` - User usage statistics
- `GET /api/subscription/dashboard/{user_id}` - Dashboard data
- `GET /api/subscription/pricing` - API pricing information
- `GET /api/subscription/trends/{user_id}` - Usage trends

### 4. Middleware Integration
- **Monitoring Middleware** (`middleware/monitoring_middleware.py`): Automatic usage tracking
- **Exception Handling**: Graceful error handling for billing issues

## 🎯 Frontend Integration

The billing system is fully integrated with the frontend dashboard:

### CompactBillingDashboard
- Real-time usage metrics
- Cost tracking
- System health monitoring
- Interactive tooltips and help text

### EnhancedBillingDashboard
- Detailed usage breakdowns
- Provider-specific costs
- Usage trends and analytics
- Alert management

## 📈 Usage Tracking

The system automatically tracks:

- **API Calls**: Number of requests to each provider
- **Token Usage**: Input and output tokens for each request
- **Costs**: Real-time cost calculations
- **Response Times**: Performance monitoring
- **Error Rates**: Failed request tracking
- **User Activity**: Per-user usage patterns

## 💰 Pricing Configuration

### Default AI Provider Pricing (per token)

| Provider | Model | Input Cost | Output Cost |
|----------|-------|------------|-------------|
| OpenAI | GPT-4 | $0.00003 | $0.00006 |
| OpenAI | GPT-3.5-turbo | $0.0000015 | $0.000002 |
| Gemini | Gemini Pro | $0.0000005 | $0.0000015 |
| Anthropic | Claude-3 | $0.000008 | $0.000024 |
| Mistral | Mistral-7B | $0.0000002 | $0.0000006 |

### Subscription Plans

| Plan | Monthly Price | Yearly Price | API Limits |
|------|---------------|--------------|------------|
| Free | $0 | $0 | 1,000 calls/month |
| Starter | $29 | $290 | 10,000 calls/month |
| Professional | $99 | $990 | 100,000 calls/month |
| Enterprise | $299 | $2,990 | Unlimited |

## 🔍 Monitoring & Alerts

### Real-time Monitoring
- Usage tracking for all API calls
- Cost calculations in real-time
- Performance metrics
- Error rate monitoring

### Alert System
- Usage approaching limits (80% threshold)
- Cost overruns
- System health issues
- Provider-specific problems

## 🛠️ Development Mode

For development with auto-reload:

```bash
# Development mode with auto-reload
python start_alwrity_backend.py --dev

# Or with explicit reload flag
python start_alwrity_backend.py --reload
```

## 📝 Configuration

### Environment Variables

The system uses the following environment variables:

```bash
# Database
DATABASE_URL=sqlite:///./alwrity.db

# API Keys (configured through onboarding)
OPENAI_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
MISTRAL_API_KEY=your_key_here

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=true
```

### Custom Pricing

To modify pricing, update the `PricingService.initialize_default_pricing()` method in `services/pricing_service.py`.

## 🧪 Testing

### Run Verification Script
```bash
python verify_billing_setup.py
```

### Test Individual Components
```bash
# Test subscription system
python test_subscription_system.py

# Test billing tables creation
python scripts/create_billing_tables.py
```

## 🚨 Troubleshooting

### Common Issues

1. **Tables not created**: Run `python scripts/create_billing_tables.py`
2. **Missing dependencies**: Run `pip install -r requirements.txt`
3. **Database errors**: Check `DATABASE_URL` in environment
4. **API key issues**: Verify API keys are configured

### Debug Mode

Enable debug logging by setting `DEBUG=true` in your environment.

## 📚 API Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

## 🔄 Updates and Maintenance

### Adding New Providers

1. Add provider to `APIProvider` enum in `models/subscription_models.py`
2. Update pricing in `PricingService.initialize_default_pricing()`
3. Add provider detection in middleware
4. Update frontend provider chips

### Modifying Plans

1. Update `PricingService.initialize_default_plans()`
2. Modify plan limits and pricing
3. Test with verification script

## 📞 Support

For issues or questions:

1. Check the verification script output
2. Review the startup logs
3. Test individual components
4. Check database table creation

## 🎉 Success Indicators

You'll know the billing system is working when:

- ✅ Startup script shows "Billing and subscription tables created successfully"
- ✅ Verification script passes all checks
- ✅ API endpoints return data
- ✅ Frontend dashboard shows usage metrics
- ✅ Usage tracking middleware is active

The billing system is now fully integrated and ready for production use!
