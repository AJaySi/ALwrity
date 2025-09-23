# ALwrity Usage-Based Subscription System

A comprehensive usage-based subscription system with API cost tracking, usage limits, and real-time monitoring for the ALwrity platform.

## 🚀 Features

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

## 📊 Database Schema

### Core Tables
- `subscription_plans`: Available subscription tiers and limits
- `user_subscriptions`: User subscription information
- `api_usage_logs`: Detailed log of every API call
- `usage_summaries`: Aggregated usage per user per billing period
- `api_provider_pricing`: Pricing configuration for all providers
- `usage_alerts`: Usage notifications and warnings
- `billing_history`: Historical billing records

## 🛠️ Installation & Setup

### 1. Database Migration
```bash
cd backend
python scripts/create_subscription_tables.py
```

### 2. Verify Installation
```bash
python test_subscription_system.py
```

### 3. Start the Server
```bash
python start_alwrity_backend.py
```

## 🔧 Configuration

### Default Subscription Plans

#### Free Tier
- **Price**: $0/month
- **Gemini Calls**: 100/month
- **Tokens**: 100,000/month
- **Features**: Basic content generation

#### Basic Tier
- **Price**: $29/month
- **Gemini Calls**: 1,000/month
- **OpenAI Calls**: 500/month
- **Tokens**: 1M Gemini, 500K OpenAI
- **Cost Limit**: $50/month

#### Pro Tier
- **Price**: $79/month
- **Gemini Calls**: 5,000/month
- **OpenAI Calls**: 2,500/month
- **Tokens**: 5M Gemini, 2.5M OpenAI
- **Cost Limit**: $150/month

#### Enterprise Tier
- **Price**: $199/month
- **Unlimited API calls** (with cost limits)
- **Cost Limit**: $500/month
- **Premium features**: White-label, dedicated support

### API Pricing (Current)

#### Gemini API
- **Gemini 2.0 Flash Lite**: $0.075/$0.30 per 1M input/output tokens
- **Gemini 2.5 Flash**: $0.125/$0.375 per 1M input/output tokens
- **Gemini 2.5 Pro**: $1.25/$10.00 per 1M input/output tokens

#### Search APIs
- **Tavily**: $0.001 per search
- **Serper**: $0.001 per search
- **Metaphor**: $0.003 per search

## 📡 API Endpoints

### Subscription Management
```
GET  /api/subscription/plans                    # Get all subscription plans
GET  /api/subscription/user/{user_id}/subscription  # Get user subscription
GET  /api/subscription/pricing                  # Get API pricing info
```

### Usage Tracking
```
GET  /api/subscription/usage/{user_id}          # Get current usage stats
GET  /api/subscription/usage/{user_id}/trends   # Get usage trends
GET  /api/subscription/dashboard/{user_id}      # Get dashboard data
```

### Alerts & Notifications
```
GET  /api/subscription/alerts/{user_id}         # Get usage alerts
POST /api/subscription/alerts/{alert_id}/mark-read  # Mark alert as read
```

## 🔍 Usage Monitoring

### Middleware Integration
The system automatically tracks API usage through enhanced middleware:

```python
# Automatic usage tracking for all API calls
await usage_service.track_api_usage(
    user_id=user_id,
    provider=APIProvider.GEMINI,
    endpoint="/api/generate",
    method="POST",
    tokens_input=1000,
    tokens_output=500,
    cost=0.00125,
    response_time=2.5
)
```

### Usage Limit Enforcement
```python
# Check limits before processing requests
can_proceed, message, usage_info = await usage_service.enforce_usage_limits(
    user_id=user_id,
    provider=APIProvider.GEMINI,
    tokens_requested=1000
)

if not can_proceed:
    return JSONResponse(
        status_code=429,
        content={"error": "Usage limit exceeded", "message": message}
    )
```

## 📈 Dashboard Integration

### Usage Statistics
```javascript
// Get comprehensive usage data
const response = await fetch(`/api/subscription/dashboard/${userId}`);
const data = await response.json();

console.log(data.data.summary);
// {
//   total_api_calls_this_month: 1250,
//   total_cost_this_month: 15.75,
//   usage_status: "active",
//   unread_alerts: 2
// }
```

### Real-Time Monitoring
```javascript
// Get current usage percentages
const usage = data.data.current_usage;
console.log(usage.usage_percentages);
// {
//   gemini_calls: 65.5,
//   openai_calls: 23.8,
//   cost: 31.5
// }
```

## 🚨 Error Handling

### Exception Types
- `UsageLimitExceededException`: When usage limits are reached
- `PricingException`: Pricing calculation errors
- `TrackingException`: Usage tracking failures
- `SubscriptionException`: General subscription errors

### Usage
```python
from services.subscription_exception_handler import handle_usage_limit_error

# Handle usage limit errors
error_response = handle_usage_limit_error(
    user_id="user123",
    provider=APIProvider.GEMINI,
    limit_type="api_calls",
    current_usage=1000,
    limit_value=1000
)
```

## 🔒 Security & Privacy

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

## 📊 Monitoring & Analytics

### Usage Trends
- Historical usage data over time
- Provider-specific breakdowns
- Cost projections and forecasting
- Performance metrics (response times, error rates)

### Alerts & Notifications
- Automatic threshold alerts (80%, 90%, 100%)
- Email notifications (configurable)
- Dashboard notifications
- Usage recommendations

## 🔧 Customization

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

## 🧪 Testing

### Run Tests
```bash
python test_subscription_system.py
```

### Test Coverage
- Database table creation
- Pricing calculations
- Usage tracking
- Limit enforcement
- Error handling
- API endpoints

## 🚀 Deployment

### Environment Variables
```env
DATABASE_URL=sqlite:///./alwrity.db
GEMINI_API_KEY=your_gemini_key
OPENAI_API_KEY=your_openai_key
# ... other API keys
```

### Production Setup
1. Use PostgreSQL for production database
2. Set up Redis for caching
3. Configure email notifications
4. Set up monitoring and alerting
5. Implement payment processing

## 📝 API Examples

### Get User Usage
```bash
curl -X GET "http://localhost:8000/api/subscription/usage/user123" \
  -H "Content-Type: application/json"
```

### Get Dashboard Data
```bash
curl -X GET "http://localhost:8000/api/subscription/dashboard/user123" \
  -H "Content-Type: application/json"
```

### Response Example
```json
{
  "success": true,
  "data": {
    "current_usage": {
      "billing_period": "2025-01",
      "total_calls": 1250,
      "total_cost": 15.75,
      "usage_status": "active",
      "provider_breakdown": {
        "gemini": {"calls": 800, "cost": 10.50},
        "openai": {"calls": 450, "cost": 5.25}
      }
    },
    "limits": {
      "plan_name": "Pro",
      "limits": {
        "gemini_calls": 5000,
        "monthly_cost": 150.0
      }
    },
    "projections": {
      "projected_monthly_cost": 47.25,
      "projected_usage_percentage": 31.5
    }
  }
}
```

## 🤝 Contributing

### Development Workflow
1. Create feature branch
2. Implement changes
3. Add tests
4. Update documentation
5. Submit pull request

### Code Standards
- Follow PEP 8 for Python code
- Use type hints
- Add comprehensive logging
- Include error handling
- Write unit tests

## 📚 Additional Resources

- [Gemini API Pricing](https://ai.google.dev/gemini-api/docs/pricing)
- [OpenAI API Pricing](https://openai.com/pricing)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)

## 🐛 Troubleshooting

### Common Issues
1. **Database Connection Errors**: Check DATABASE_URL configuration
2. **Missing API Keys**: Verify all required keys are set
3. **Usage Not Tracking**: Check middleware integration
4. **Pricing Errors**: Verify provider pricing configuration

### Debug Mode
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Support
For issues and questions:
1. Check the logs in `logs/subscription_errors.log`
2. Run the test suite to identify problems
3. Review the error handling documentation
4. Contact the development team

---

**Version**: 1.0.0  
**Last Updated**: January 2025  
**Maintainer**: ALwrity Development Team