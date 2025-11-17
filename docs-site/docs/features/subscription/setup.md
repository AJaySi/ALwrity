# Subscription System Setup

Complete guide for installing and configuring the ALwrity usage-based subscription system.

## Prerequisites

- Python 3.8+
- PostgreSQL database (or SQLite for development)
- FastAPI backend environment
- Required Python packages: `sqlalchemy`, `loguru`, `fastapi`

## Installation

### 1. Database Migration

Run the database setup script to create all subscription tables:

```bash
cd backend
python scripts/create_subscription_tables.py
```

This script will:
- Create all subscription-related database tables
- Initialize default subscription plans (Free, Basic, Pro, Enterprise)
- Configure API pricing for all providers
- Verify the setup

### 2. Verify Installation

Test the subscription system:

```bash
python test_subscription_system.py
```

This will verify:
- Database table creation
- Pricing calculations
- Usage tracking
- Limit enforcement
- Error handling
- API endpoints

### 3. Start the Server

```bash
python start_alwrity_backend.py
```

## Configuration

### Environment Variables

Create or update your `.env` file with the following:

```env
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost/alwrity
# For development, you can use SQLite:
# DATABASE_URL=sqlite:///./alwrity.db

# API Keys (required for usage tracking)
GEMINI_API_KEY=your_gemini_key
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
# ... other API keys as needed

# HuggingFace Pricing (optional, for GPT-OSS-120B via Groq)
HUGGINGFACE_INPUT_TOKEN_COST=0.000001
HUGGINGFACE_OUTPUT_TOKEN_COST=0.000003
```

### HuggingFace Pricing Configuration

HuggingFace API calls (specifically for GPT-OSS-120B model via Groq) are tracked and billed using configurable pricing.

#### Environment Variables

- `HUGGINGFACE_INPUT_TOKEN_COST`: Cost per input token (default: `0.000001` = $1 per 1M tokens)
- `HUGGINGFACE_OUTPUT_TOKEN_COST`: Cost per output token (default: `0.000003` = $3 per 1M tokens)

#### Updating Pricing

The pricing is automatically initialized when the database is set up. To update pricing after changing environment variables:

1. **Option 1**: Restart the backend server (pricing will be updated on next initialization)
2. **Option 2**: Run the database setup script again:
   ```bash
   python backend/scripts/create_subscription_tables.py
   ```

#### Verify Pricing

Check that pricing is correctly configured by:
1. Checking the database `api_provider_pricing` table
2. Making a test API call and checking the cost in usage logs
3. Viewing the billing dashboard to see cost calculations

## Production Setup

### 1. Database

Use PostgreSQL for production:

```env
DATABASE_URL=postgresql://user:password@host:5432/alwrity_prod
```

### 2. Caching

Set up Redis for caching (optional but recommended):

```env
REDIS_URL=redis://localhost:6379/0
```

### 3. Email Notifications

Configure email service for usage alerts:

```env
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=alerts@alwrity.com
SMTP_PASSWORD=your_password
```

### 4. Monitoring and Alerting

Set up monitoring and alerting systems:
- Configure log aggregation
- Set up performance monitoring
- Configure alert thresholds

### 5. Payment Processing

Implement payment processing integration:
- Stripe integration
- Payment gateway setup
- Billing cycle management

## Middleware Integration

The subscription system automatically tracks API usage through enhanced middleware. The middleware:

- Detects API provider from request patterns
- Estimates token usage from request/response content
- Validates usage limits before processing
- Calculates costs in real-time
- Logs all API calls for tracking

No additional configuration is required - the middleware is automatically active once the subscription system is installed.

## Usage Limit Enforcement

The system enforces usage limits automatically:

```python
# Usage limits are checked before processing requests
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

## Testing

### Run Tests

```bash
python test_subscription_system.py
```

### Test Coverage

The test suite covers:
- Database table creation
- Pricing calculations
- Usage tracking
- Limit enforcement
- Error handling
- API endpoints

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Check `DATABASE_URL` configuration
   - Verify database is running
   - Check network connectivity

2. **Missing API Keys**
   - Verify all required keys are set in `.env`
   - Check environment variable names match exactly

3. **Usage Not Tracking**
   - Verify middleware is integrated
   - Check database connection
   - Review logs for errors

4. **Pricing Errors**
   - Verify provider pricing configuration in database
   - Check `api_provider_pricing` table
   - Review pricing initialization logs

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Support

For issues and questions:
1. Check the logs in `logs/subscription_errors.log`
2. Run the test suite to identify problems
3. Review the error handling documentation
4. Contact the development team

## Next Steps

- [API Reference](api-reference.md) - Endpoint documentation and examples
- [Pricing](pricing.md) - Subscription plans and API pricing details
- [Frontend Integration](frontend-integration.md) - Technical specifications for frontend

---

**Last Updated**: January 2025

