# Integrations Registry (Week 3 Migration Bridge)

## Overview
The integrations registry provides a lightweight abstraction layer that wraps the existing provider services (GSC, Bing, WordPress, Wix). It normalizes:

- OAuth authorization URL payloads.
- Connection status responses.

This registry is **non-breaking** and intended to coexist with legacy onboarding/monitoring flows until Week 3 of the migration plan.

## Files Added
- `backend/services/integrations/base.py`
  - `IntegrationProvider` protocol for provider contracts.
  - `ConnectionStatus` and `AuthUrlPayload` shared models.
- `backend/services/integrations/registry.py`
  - Adapter implementations for GSC, Bing, WordPress, Wix.
  - Central registry that exposes registered providers.

## Provider Adapters
Each adapter is a thin wrapper around existing services:

| Provider | Adapter | Legacy Service(s) |
| --- | --- | --- |
| Google Search Console | `GSCIntegrationProvider` | `GSCService` |
| Bing Webmaster Tools | `BingIntegrationProvider` | `BingOAuthService` |
| WordPress | `WordPressIntegrationProvider` | `WordPressOAuthService` |
| Wix | `WixIntegrationProvider` | `WixService`, `WixOAuthService` |

## Usage
```python
from services.integrations.registry import get_provider

provider = get_provider("gsc")
if provider:
    auth_payload = provider.get_auth_url(user_id)
    status = provider.get_connection_status(user_id)
```

## Migration Note
Onboarding and monitoring codepaths **must continue to use legacy services** until Week 3. The registry exists to introduce a normalized interface for future migrations without changing storage or endpoints today.
