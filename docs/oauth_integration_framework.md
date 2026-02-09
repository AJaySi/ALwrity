# OAuth Integration Framework Documentation

## Overview

The ALwrity OAuth Integration Framework provides a unified, extensible architecture for managing OAuth connections across multiple platforms. This framework eliminates fragmented integration logic, provides PostgreSQL-only token storage, and ensures consistent connection validation across all supported platforms.

## Architecture

### Core Components

#### 1. Integration Provider Interface (`services/integrations/base.py`)
```python
class IntegrationProvider(Protocol):
    """Contract for integration providers used by the registry layer."""
    
    key: str
    display_name: str
    
    def get_auth_url(self, user_id: str) -> AuthUrlPayload: ...
    def get_connection_status(self, user_id: str) -> ConnectionStatus: ...
```

#### 2. Integration Registry (`services/integrations/registry.py`)
- Central registry for all integration providers
- Lazy loading with factory pattern
- Enhanced error handling and resilience

#### 3. Enhanced Provider Wrapper (`services/integrations/enhanced_integration_provider.py`)
- Circuit breaker pattern for fault tolerance
- Automatic retry with exponential backoff
- Comprehensive error handling and logging

#### 4. OAuth Redirect Management (`services/oauth_redirects.py`)
- Environment-driven redirect URI configuration
- Automatic validation of redirect origins
- Environment mismatch detection (dev/stage/prod)

#### 5. Token Storage Models (`models/oauth_token_models.py`)
- PostgreSQL-only token storage
- Unified token models for all platforms
- Proper indexing and relationships

## Supported Platforms

| Platform | Provider Class | Service Class | Token Model |
|-----------|-----------------|-----------------|--------------|
| Google Search Console | `GSCIntegrationProvider` | `GSCService` | `GscCredential` |
| Bing Webmaster Tools | `BingIntegrationProvider` | `BingOAuthService` | `BingOAuthToken` |
| WordPress.com | `WordPressIntegrationProvider` | `WordPressOAuthService` | `WordPressOAuthToken` |
| Wix | `WixIntegrationProvider` | `WixService` + `WixOAuthService` | `WixOAuthToken` |

## Environment Configuration

### Required Environment Variables

```bash
# Frontend Configuration
FRONTEND_URL=https://your-domain.com
DEPLOY_ENV=production  # development, staging, production

# OAuth Provider Configuration
GSC_CLIENT_ID=your_gsc_client_id
GSC_CLIENT_SECRET=your_gsc_client_secret
GSC_REDIRECT_URI=https://your-domain.com/oauth/gsc/callback

BING_CLIENT_ID=your_bing_client_id
BING_CLIENT_SECRET=your_bing_client_secret
BING_REDIRECT_URI=https://your-domain.com/oauth/bing/callback

WORDPRESS_CLIENT_ID=your_wordpress_client_id
WORDPRESS_CLIENT_SECRET=your_wordpress_client_secret
WORDPRESS_REDIRECT_URI=https://your-domain.com/oauth/wordpress/callback

WIX_CLIENT_ID=your_wix_client_id
WIX_CLIENT_SECRET=your_wix_client_secret
WIX_REDIRECT_URI=https://your-domain.com/oauth/wix/callback

# Database Configuration
PLATFORM_DATABASE_URL=postgresql://user:pass@host:5432/platform_db
USER_DATA_DATABASE_URL=postgresql://user:pass@host:5432/user_data_db
```

## Usage Examples

### Getting Connection Status for All Platforms

```python
from services.integrations.registry import get_provider

async def get_all_connection_status(user_id: str):
    """Get connection status for all supported platforms."""
    platforms = ['gsc', 'bing', 'wordpress', 'wix']
    results = {}
    
    for platform_key in platforms:
        provider = get_provider(platform_key)
        if provider:
            status = await provider.get_connection_status(user_id)
            results[platform_key] = {
                'connected': status.connected,
                'details': status.details,
                'error': status.error
            }
    
    return results
```

### Generating OAuth Authorization URLs

```python
from services.integrations.registry import get_provider

async def generate_auth_url(platform: str, user_id: str):
    """Generate OAuth authorization URL for a platform."""
    provider = get_provider(platform)
    if not provider:
        raise ValueError(f"Unsupported platform: {platform}")
    
    auth_payload = await provider.get_auth_url(user_id)
    return {
        'auth_url': auth_payload.auth_url,
        'state': auth_payload.state,
        'details': auth_payload.details
    }
```

### Validating Step 5 Completion

```python
from services.integrations.registry import get_provider

async def validate_step_5_completion(user_id: str):
    """Validate that user has at least one connected platform."""
    platforms = ['gsc', 'bing', 'wordpress', 'wix']
    connected_platforms = []
    
    for platform_key in platforms:
        provider = get_provider(platform_key)
        if provider:
            status = await provider.get_connection_status(user_id)
            if status.connected:
                connected_platforms.append({
                    'platform': platform_key,
                    'display_name': provider.display_name,
                    'details': status.details
                })
    
    if not connected_platforms:
        return {
            'valid': False,
            'error': 'At least one platform must be connected',
            'connected_platforms': []
        }
    
    return {
        'valid': True,
        'connected_platforms': connected_platforms,
        'message': f'Connected to {len(connected_platforms)} platform(s)'
    }
```

## Adding New Platforms

### Step 1: Create Token Model

Add a new model to `models/oauth_token_models.py`:

```python
class NewPlatformOAuthToken(Base):
    """OAuth tokens for New Platform."""
    
    __tablename__ = "new_platform_oauth_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=True)
    token_type = Column(String(50), default="bearer")
    expires_at = Column(DateTime, nullable=True)
    scope = Column(Text, nullable=True)
    # Add platform-specific fields
    platform_specific_field = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
```

### Step 2: Create Service Class

Create a service class to handle OAuth flow and API interactions:

```python
# services/integrations/new_platform_oauth.py
from services.oauth_redirects import get_redirect_uri
from loguru import logger

class NewPlatformOAuthService:
    """Manages New Platform OAuth2 authentication flow."""
    
    def __init__(self):
        self.client_id = os.getenv('NEW_PLATFORM_CLIENT_ID', '')
        self.client_secret = os.getenv('NEW_PLATFORM_CLIENT_SECRET', '')
        
        try:
            self.redirect_uri = get_redirect_uri("NewPlatform", "NEW_PLATFORM_REDIRECT_URI")
        except ValueError as exc:
            logger.error(f"NewPlatform OAuth redirect URI configuration error: {exc}")
            self.redirect_uri = None
    
    def generate_authorization_url(self, user_id: str) -> Dict[str, str]:
        """Generate OAuth authorization URL."""
        if not self.redirect_uri:
            raise ValueError("Redirect URI not configured")
        
        # Implement platform-specific OAuth flow
        auth_url = f"https://api.newplatform.com/oauth/authorize?client_id={self.client_id}&redirect_uri={self.redirect_uri}&state={user_id}"
        
        return {
            'auth_url': auth_url,
            'state': user_id
        }
    
    def handle_oauth_callback(self, authorization_code: str, state: str) -> Dict[str, Any]:
        """Handle OAuth callback and exchange code for tokens."""
        # Implement token exchange logic
        pass
    
    def get_connection_status(self, user_id: str) -> Dict[str, Any]:
        """Get connection status for user."""
        # Implement status checking logic
        pass
```

### Step 3: Create Integration Provider

```python
# In services/integrations/registry.py
class NewPlatformIntegrationProvider:
    key = "new_platform"
    display_name = "New Platform"
    
    def __init__(self, service: Optional[NewPlatformOAuthService] = None):
        self._service = service or NewPlatformOAuthService()
    
    def get_auth_url(self, user_id: str) -> AuthUrlPayload:
        payload = self._service.generate_authorization_url(user_id)
        if not payload or "auth_url" not in payload:
            return AuthUrlPayload(auth_url="", details={"error": "Unable to generate auth URL."})
        return AuthUrlPayload(auth_url=payload["auth_url"], state=payload.get("state"))
    
    def get_connection_status(self, user_id: str) -> ConnectionStatus:
        status = self._service.get_connection_status(user_id)
        return ConnectionStatus(
            connected=bool(status.get("connected")),
            details=status,
            error=status.get("error"),
        )
```

### Step 4: Register Provider

```python
# In services/integrations/registry.py

def ensure_default_providers_registered() -> None:
    """Register default providers for Week 3 migration bridge."""
    if _INTEGRATION_PROVIDER_FACTORIES:
        return
    register_provider_factory("gsc", GSCIntegrationProvider)
    register_provider_factory("bing", BingIntegrationProvider)
    register_provider_factory("wordpress", WordPressIntegrationProvider)
    register_provider_factory("wix", WixIntegrationProvider)
    register_provider_factory("new_platform", NewPlatformIntegrationProvider)  # Add this line
```

### Step 5: Add Environment Variables

Add to your `.env` file:

```bash
NEW_PLATFORM_CLIENT_ID=your_new_platform_client_id
NEW_PLATFORM_CLIENT_SECRET=your_new_platform_client_secret
NEW_PLATFORM_REDIRECT_URI=https://your-domain.com/oauth/new-platform/callback
```

## Token Monitoring

The framework includes automatic token monitoring via scheduled tasks:

### Monitoring Executor (`services/scheduler/executors/oauth_token_monitoring_executor.py`)

```python
# Token monitoring is automatically scheduled and handles:
# - Token expiration checking
# - Automatic token refresh
# - Failure logging and alerting
# - Circuit breaker activation for repeated failures
```

### Monitoring Configuration

```python
# Configuration options
expiration_warning_days = 7  # Warn 7 days before expiration
max_retries = 3  # Maximum retry attempts
retry_delay = 1.0  # Initial retry delay (seconds)
backoff_factor = 2.0  # Exponential backoff factor
```

## Error Handling & Resilience

### Circuit Breaker Pattern

The enhanced provider wrapper includes circuit breaker functionality:

```python
# Circuit breaker states
- CLOSED: Normal operation
- OPEN: Failing, requests blocked
- HALF_OPEN: Testing if service has recovered

# Configuration
failure_threshold = 5  # Open circuit after 5 failures
recovery_timeout = 60  # Wait 60 seconds before retrying
success_threshold = 3  # Need 3 successes to close circuit
```

### Retry Logic

```python
# Automatic retry with exponential backoff
max_retries = 3
initial_delay = 1.0 second
backoff_factor = 2.0  # 1s, 2s, 4s delays
```

## Database Schema

### Token Tables

All token tables follow a consistent pattern:

```sql
-- Common fields across all token tables
id SERIAL PRIMARY KEY
user_id VARCHAR(255) NOT NULL
access_token TEXT NOT NULL
refresh_token TEXT
token_type VARCHAR(50) DEFAULT 'bearer'
expires_at TIMESTAMP
scope TEXT
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
is_active BOOLEAN DEFAULT TRUE

-- Platform-specific fields (example for Wix)
expires_in INTEGER
site_id TEXT
member_id TEXT
```

### Indexes

```sql
-- Performance indexes
CREATE INDEX idx_oauth_tokens_user_id ON platform_oauth_tokens(user_id);
CREATE INDEX idx_oauth_tokens_expires_at ON platform_oauth_tokens(expires_at);
CREATE INDEX idx_oauth_tokens_active ON platform_oauth_tokens(is_active) WHERE is_active = TRUE;
```

## Security Considerations

### Redirect URI Validation

- Automatic origin validation against `FRONTEND_URL`
- Environment mismatch detection (dev/stage/prod)
- No hardcoded redirect URIs

### Token Storage

- PostgreSQL-only storage (no SQLite)
- Encrypted token storage (application-level)
- Proper indexing for performance
- Automatic expiration handling

### Error Handling

- No sensitive information in logs
- Circuit breaker prevents cascade failures
- Comprehensive error reporting
- Graceful degradation

## Performance Optimization

### Connection Pooling

```python
# Database connection pooling
pool_size = 20
max_overflow = 30
pool_timeout = 30
pool_recycle = 3600
pool_pre_ping = True
```

### Caching

- Token status caching (5-minute TTL)
- Connection status caching
- Provider instance caching (lazy loading)

## Monitoring & Analytics

### Health Checks

```python
# Provider health status
health_status = provider.get_health_status()
# Returns: circuit_breaker_state, failure_count, success_count, etc.
```

### Metrics

- Token refresh success/failure rates
- Connection establishment times
- Circuit breaker activation frequency
- Cache hit/miss ratios

## Troubleshooting

### Common Issues

1. **Redirect URI Mismatch**
   - Check `FRONTEND_URL` environment variable
   - Verify `*_REDIRECT_URI` variables
   - Ensure environment consistency

2. **Token Not Found**
   - Check database connection
   - Verify user_id consistency
   - Check token expiration

3. **Circuit Breaker Open**
   - Check service availability
   - Review recent error logs
   - Verify API credentials

### Debug Logging

```python
# Enable debug logging
import logging
logging.getLogger('services.integrations').setLevel(logging.DEBUG)
```

## Migration Guide

### From Legacy Services

1. Replace direct service calls with registry calls
2. Update error handling to use `ConnectionStatus`
3. Migrate token storage to PostgreSQL models
4. Update environment variable usage

### Database Migration

```bash
# Run migration script
python backend/scripts/backfill_oauth_tokens_to_postgres.py

# Verify migration
python -c "
from services.integrations.registry import get_provider
provider = get_provider('gsc')
print('GSC provider loaded successfully')
"
```

## Best Practices

1. **Always use the integration registry** - never instantiate providers directly
2. **Implement proper error handling** for all OAuth operations
3. **Use connection status** for Step 5 validation
4. **Implement token refresh** before expiration
5. **Log all OAuth events** for debugging
6. **Test circuit breaker** functionality
7. **Monitor token expiration** proactively
8. **Use environment variables** for all configuration
9. **Validate redirect URIs** in all environments
10. **Implement graceful degradation** when services are unavailable

## Support

For issues or questions about the OAuth Integration Framework:

1. Check logs for detailed error messages
2. Verify environment configuration
3. Test with individual providers
4. Check circuit breaker status
5. Review database connection status

## Version History

- **v2.0**: PostgreSQL-only storage, enhanced error handling, circuit breaker
- **v1.0**: Initial implementation with SQLite support
