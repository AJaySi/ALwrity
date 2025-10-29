# Subscription Services Package

## Overview

This package consolidates all subscription, billing, and usage tracking related services and middleware into a single, well-organized module. This follows the same architectural pattern as the onboarding package for consistency and maintainability.

## Package Structure

```
backend/services/subscription/
├── __init__.py                          # Package exports
├── pricing_service.py                   # API pricing and cost calculations
├── usage_tracking_service.py            # Usage tracking and limits
├── exception_handler.py                 # Exception handling
├── monitoring_middleware.py             # API monitoring with usage tracking
└── README.md                           # This documentation
```

## Services

### PricingService
- **File**: `pricing_service.py`
- **Purpose**: Manages API pricing, cost calculation, and subscription limits
- **Key Features**:
  - Dynamic pricing based on API provider and model
  - Cost calculation for input/output tokens
  - Subscription limit enforcement
  - Billing period management

### UsageTrackingService
- **File**: `usage_tracking_service.py`
- **Purpose**: Comprehensive tracking of API usage, costs, and subscription limits
- **Key Features**:
  - Real-time usage tracking
  - Cost calculation and billing
  - Usage limit enforcement with TTL caching
  - Usage alerts and notifications

### SubscriptionExceptionHandler
- **File**: `exception_handler.py`
- **Purpose**: Centralized exception handling for subscription-related errors
- **Key Features**:
  - Custom exception types
  - Error handling decorators
  - Consistent error responses

### Monitoring Middleware
- **File**: `monitoring_middleware.py`
- **Purpose**: FastAPI middleware for API monitoring and usage tracking
- **Key Features**:
  - Request/response monitoring
  - Usage tracking integration
  - Performance metrics
  - Database API monitoring

## Usage

### Import Pattern

Always use the consolidated package for subscription-related imports:

```python
# ✅ Correct - Use consolidated package
from services.subscription import PricingService, UsageTrackingService
from services.subscription import SubscriptionExceptionHandler
from services.subscription import check_usage_limits_middleware

# ❌ Incorrect - Old scattered imports
from services.pricing_service import PricingService
from services.usage_tracking_service import UsageTrackingService
from middleware.monitoring_middleware import check_usage_limits_middleware
```

### Service Initialization

```python
from services.subscription import PricingService, UsageTrackingService
from services.database import get_db

# Get database session
db = next(get_db())

# Initialize services
pricing_service = PricingService(db)
usage_service = UsageTrackingService(db)
```

### Middleware Registration

```python
from services.subscription import monitoring_middleware

# Register middleware in FastAPI app
app.middleware("http")(monitoring_middleware)
```

## Database Models

The subscription services use the following database models (defined in `backend/models/subscription_models.py`):

- `APIProvider` - API provider enumeration
- `SubscriptionPlan` - Subscription plan definitions
- `UserSubscription` - User subscription records
- `UsageSummary` - Usage summary by billing period
- `APIUsageLog` - Individual API usage logs
- `APIProviderPricing` - Pricing configuration
- `UsageAlert` - Usage limit alerts
- `SubscriptionTier` - Subscription tier definitions
- `BillingCycle` - Billing cycle enumeration
- `UsageStatus` - Usage status enumeration

## Key Features

### 1. Database-Only Persistence
- All data stored in database tables
- No file-based storage
- User-isolated data access

### 2. TTL Caching
- In-memory caching for performance
- 30-second TTL for usage limit checks
- 10-minute TTL for dashboard data

### 3. Real-time Monitoring
- Live API usage tracking
- Performance metrics collection
- Error rate monitoring

### 4. Flexible Pricing
- Per-provider pricing configuration
- Model-specific pricing
- Dynamic cost calculation

## Error Handling

The package provides comprehensive error handling:

```python
from services.subscription import (
    SubscriptionException,
    UsageLimitExceededException,
    PricingException,
    TrackingException
)

try:
    # Subscription operation
    pass
except UsageLimitExceededException as e:
    # Handle usage limit exceeded
    pass
except PricingException as e:
    # Handle pricing error
    pass
```

## Configuration

The services use environment variables for configuration:

- `SUBSCRIPTION_DASHBOARD_NOCACHE` - Bypass dashboard cache
- `ENABLE_ALPHA` - Enable alpha features (default: false)

## Migration from Old Structure

This package consolidates the following previously scattered files:

- `backend/services/pricing_service.py` → `subscription/pricing_service.py`
- `backend/services/usage_tracking_service.py` → `subscription/usage_tracking_service.py`
- `backend/services/subscription_exception_handler.py` → `subscription/exception_handler.py`
- `backend/middleware/monitoring_middleware.py` → `subscription/monitoring_middleware.py`

## Benefits

1. **Single Package**: All subscription logic in one location
2. **Clear Ownership**: Easy to find subscription-related code
3. **Better Organization**: Follows same pattern as onboarding
4. **Easier Maintenance**: Single source of truth for billing logic
5. **Consistent Architecture**: Matches onboarding consolidation

## Related Packages

- `services.onboarding` - Onboarding and user setup
- `models.subscription_models` - Database models
- `api.subscription_api` - API endpoints
