# OAuth Provider Integration Guide

**Document Version**: 1.0  
**Created**: 2026-02-11  
**Purpose**: Guide for integrating new OAuth providers with ALwrity's unified framework

---

## 🎯 **OVERVIEW**

The ALwrity OAuth Integration Framework provides a **unified, secure, and extensible** architecture for adding new OAuth providers. This guide walks through the complete integration process.

### **Framework Benefits**
- ✅ **Security-First**: Token redaction, origin validation, state management
- ✅ **Rapid Development**: Standard base classes and patterns
- ✅ **Consistent UX**: Unified router and response formats
- ✅ **Production Ready**: Circuit breaker, retry logic, monitoring
- ✅ **Easy Maintenance**: Single token service, unified storage

---

## 🏗️ **ARCHITECTURE COMPONENTS**

### **Core Framework Files**
```
backend/
├── services/integrations/
│   ├── base.py                    # Integration provider protocol
│   ├── standard_oauth_provider.py  # Base implementation class
│   ├── unified_token_service.py   # Unified token management
│   └── registry.py                # Provider registration
├── api/
│   └── oauth_unified_routes.py  # Unified OAuth router
└── scripts/
    └── migrate_oauth_tokens_to_unified.py  # Migration utilities
```

### **Integration Patterns**
1. **Inheritance-Based**: Extend `StandardOAuthProvider`
2. **Configuration-Driven**: Environment variables + optional YAML config
3. **Registry-Based**: Dynamic provider registration and discovery
4. **Unified Storage**: Single `UnifiedOAuthToken` model

---

## 🚀 **INTEGRATION STEPS**

### **Step 1: Provider Configuration**

#### **Environment Variables**
Add to your `.env` file:

```bash
# Provider Configuration
NEW_PROVIDER_CLIENT_ID=your_new_provider_client_id
NEW_PROVIDER_CLIENT_SECRET=your_new_provider_client_secret
NEW_PROVIDER_REDIRECT_URI=https://your-domain.com/oauth/new-provider/callback

# Optional: Custom scopes
NEW_PROVIDER_SCOPES=read,write,admin
```

#### **Optional YAML Configuration**
For complex providers, create `config/oauth_providers.yaml`:

```yaml
providers:
  new_provider:
    display_name: "New Provider"
    auth_url: "https://api.newprovider.com/oauth/authorize"
    token_url: "https://api.newprovider.com/oauth/token"
    scopes: ["read", "write", "admin"]
    client_id_env: "NEW_PROVIDER_CLIENT_ID"
    client_secret_env: "NEW_PROVIDER_CLIENT_SECRET"
    redirect_uri_env: "NEW_PROVIDER_REDIRECT_URI"
    custom_params:
      param1: "value1"
      param2: "value2"
```

### **Step 2: Provider Implementation**

#### **Create Provider Service**
```python
# backend/services/integrations/new_provider_oauth.py
from .standard_oauth_provider import StandardOAuthProvider
from urllib.parse import urlencode
import httpx
from datetime import datetime, timedelta

class NewProviderOAuthService(StandardOAuthProvider):
    """New Provider OAuth implementation."""
    
    # Provider configuration
    key = "new_provider"
    display_name = "New Provider"
    auth_url = "https://api.newprovider.com/oauth/authorize"
    token_url = "https://api.newprovider.com/oauth/token"
    scopes = ["read", "write", "admin"]
    
    # Environment variables
    client_id_env = "NEW_PROVIDER_CLIENT_ID"
    client_secret_env = "NEW_PROVIDER_CLIENT_SECRET"
    redirect_uri_env = "NEW_PROVIDER_REDIRECT_URI"
    
    async def _exchange_code_for_tokens(self, code: str) -> dict:
        """Exchange authorization code for access tokens."""
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'redirect_uri': self.redirect_uri,
            'grant_type': 'authorization_code'
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(self.token_url, data=data)
            response.raise_for_status()
            
            tokens = response.json()
            
            # Calculate expiration
            expires_at = None
            if 'expires_in' in tokens:
                expires_at = datetime.utcnow() + timedelta(seconds=tokens['expires_in'])
            
            return {
                'access_token': tokens['access_token'],
                'refresh_token': tokens.get('refresh_token'),
                'expires_at': expires_at,
                'scope': ' '.join(self.scopes),
                'account_info': {
                    'user_id': tokens.get('user_id'),
                    'email': tokens.get('email'),
                    'name': tokens.get('name')
                }
            }
    
    async def _refresh_access_token(self, refresh_token: str) -> dict:
        """Refresh access token using refresh token."""
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token'
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(self.token_url, data=data)
            response.raise_for_status()
            
            tokens = response.json()
            
            # Calculate new expiration
            expires_at = None
            if 'expires_in' in tokens:
                expires_at = datetime.utcnow() + timedelta(seconds=tokens['expires_in'])
            
            return {
                'access_token': tokens['access_token'],
                'refresh_token': tokens.get('refresh_token', refresh_token),
                'expires_at': expires_at,
                'scope': tokens.get('scope', ' '.join(self.scopes))
            }
    
    def _get_auth_url_params(self) -> dict:
        """Get provider-specific authorization URL parameters."""
        return {
            'response_type': 'code',
            'access_type': 'offline',  # For refresh tokens
            'prompt': 'consent'  # Force consent dialog
        }
    
    async def _revoke_provider_token(self, user_id: str) -> None:
        """Revoke token on provider side (optional)."""
        # Implement if provider supports token revocation
        try:
            # Example revocation endpoint
            revoke_url = "https://api.newprovider.com/oauth/revoke"
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    revoke_url,
                    data={'token': self._get_current_token(user_id)}
                )
                # Don't raise for revocation failures - it's optional
                
        except Exception as e:
            logger.warning(f"Token revocation failed for new_provider: {e}")
```

### **Step 3: Provider Registration**

#### **Register in Registry**
```python
# backend/services/integrations/registry.py

# Add import
from .new_provider_oauth import NewProviderOAuthService

# Add to ensure_default_providers function
def ensure_default_providers_registered() -> None:
    """Register default providers."""
    if _INTEGRATION_PROVIDER_FACTORIES:
        return
    
    register_provider_factory("new_provider", NewProviderOAuthService)
    # ... existing providers ...
```

#### **Update Provider List**
```python
# backend/services/integrations/registry.py

# Add to SUPPORTED_PROVIDERS list
SUPPORTED_PROVIDERS = [
    "gsc", "bing", "wordpress", "wix", "new_provider"
]
```

### **Step 4: Database Migration (if needed)**

#### **Custom Token Fields**
If your provider needs custom fields, extend the unified token service:

```python
# In your provider service
async def _exchange_code_for_tokens(self, code: str) -> dict:
    # ... standard token exchange ...
    
    return {
        'access_token': tokens['access_token'],
        'refresh_token': tokens.get('refresh_token'),
        'expires_at': expires_at,
        'scope': ' '.join(self.scopes),
        'account_info': {
            'user_id': tokens.get('user_id'),
            'email': tokens.get('email'),
            'name': tokens.get('name')
        },
        'metadata': {
            'provider_specific_field': tokens.get('custom_field'),
            'api_version': tokens.get('version'),
            'permissions': tokens.get('permissions', [])
        }
    }
```

---

## 🧪 **TESTING YOUR INTEGRATION**

### **Unit Tests**
```python
# backend/tests/integrations/test_new_provider.py
import pytest
from services.integrations.new_provider_oauth import NewProviderOAuthService

class TestNewProviderOAuth:
    def test_auth_url_generation(self):
        """Test OAuth URL generation."""
        service = NewProviderOAuthService()
        
        # Mock environment variables
        os.environ['NEW_PROVIDER_CLIENT_ID'] = 'test_client_id'
        os.environ['NEW_PROVIDER_REDIRECT_URI'] = 'https://test.com/callback'
        
        result = await service.get_auth_url('test_user')
        
        assert result.auth_url.startswith('https://api.newprovider.com/oauth/authorize')
        assert 'test_user' in result.state
        assert 'client_id=test_client_id' in result.auth_url
    
    def test_callback_handling(self):
        """Test OAuth callback handling."""
        service = NewProviderOAuthService()
        
        # Mock token exchange
        with patch.object(service, '_exchange_code_for_tokens') as mock_exchange:
            mock_exchange.return_value = {
                'access_token': 'test_access_token',
                'refresh_token': 'test_refresh_token',
                'expires_in': 3600
            }
            
            result = await service.handle_callback('test_code', 'test_user:test_state')
            
            assert result.success is True
            assert result.access_token == 'test_access_token'
            assert result.user_id == 'test_user'
    
    def test_token_refresh(self):
        """Test token refresh."""
        service = NewProviderOAuthService()
        
        # Mock refresh endpoint
        with patch.object(service, '_refresh_access_token') as mock_refresh:
            mock_refresh.return_value = {
                'access_token': 'new_access_token',
                'expires_in': 3600
            }
            
            result = await service.refresh_token('test_user')
            
            assert result.success is True
            assert result.access_token == 'new_access_token'
```

### **Integration Tests**
```python
# backend/tests/integrations/test_new_provider_integration.py
import pytest
from fastapi.testclient import TestClient
from backend.api.oauth_unified_routes import router

class TestNewProviderIntegration:
    def test_full_oauth_flow(self):
        """Test complete OAuth flow through unified router."""
        client = TestClient(app)
        
        # Test auth URL generation
        response = client.get("/oauth/new_provider/auth?user_id=test_user")
        assert response.status_code == 200
        
        auth_data = response.json()
        assert auth_data['provider_key'] == 'new_provider'
        assert auth_data['auth_url'].startswith('https://api.newprovider.com')
        
        # Test callback handling
        response = client.post(
            "/oauth/new_provider/callback",
            data={"code": "test_code", "state": "test_user:test_state"}
        )
        assert response.status_code == 200
        
        callback_data = response.json()
        assert callback_data['success'] is True
        
        # Test status checking
        response = client.get("/oauth/new_provider/status?user_id=test_user")
        assert response.status_code == 200
        
        status_data = response.json()
        assert status_data['connected'] is True
        assert 'access_token' not in str(status_data)  # Token redacted
```

---

## 🔒 **SECURITY CHECKLIST**

### **✅ Required Security Measures**

#### **1. Token Redaction**
- [ ] Never include `access_token` in frontend responses
- [ ] Never include `refresh_token` in frontend responses  
- [ ] Use `_sanitize_response_data()` in router responses
- [ ] Test token redaction in integration tests

#### **2. State Management**
- [ ] Use secure state format: `user_id:random_token`
- [ ] Validate state in callback handler
- [ ] Implement atomic state consumption
- [ ] Set reasonable state TTL (20 minutes)

#### **3. Origin Validation**
- [ ] Use `get_trusted_origins_for_redirect()` for redirect URIs
- [ ] Validate postMessage origins in frontend
- [ ] Implement environment mismatch detection
- [ ] No hardcoded redirect URIs

#### **4. Error Handling**
- [ ] Never log sensitive token information
- [ ] Use generic error messages for users
- [ ] Implement proper HTTP status codes
- [ ] Include correlation IDs for debugging

#### **5. Token Storage**
- [ ] Use `unified_token_service` for all token operations
- [ ] Implement proper token expiration handling
- [ ] Support token refresh where applicable
- [ ] Include provider-specific metadata

---

## 🚀 **DEPLOYMENT CHECKLIST**

### **Pre-Deployment**
- [ ] All unit tests passing
- [ ] Integration tests passing
- [ ] Security checklist complete
- [ ] Environment variables documented
- [ ] Provider registered in registry

### **Post-Deployment**
- [ ] OAuth flow tested in staging
- [ ] Token redaction verified in browser
- [ ] Error scenarios tested
- [ ] Performance tests passing
- [ ] Monitoring dashboards working

---

## 📈 **MONITORING & ANALYTICS**

### **Token Health Dashboard**
Access via unified router: `GET /oauth/providers`

```json
{
  "providers": [
    {
      "key": "new_provider",
      "display_name": "New Provider", 
      "connected": true,
      "details": {
        "connected_at": "2026-02-11T18:45:00Z",
        "expires_at": "2026-02-12T18:45:00Z"
      }
    }
  ]
}
```

### **Token Analytics**
```python
# Get comprehensive token statistics
from services.integrations.unified_token_service import unified_token_service

stats = unified_token_service.get_token_statistics()
print(f"Total tokens: {stats['total_tokens']}")
print(f"Expired tokens: {stats['expired_tokens']}")
print(f"Provider counts: {stats['provider_counts']}")
```

---

## 🛠️ **TROUBLESHOOTING**

### **Common Issues & Solutions**

#### **1. Import Errors**
```
ModuleNotFoundError: No module named 'services.integrations'
```
**Solution**: Check Python path and ensure `__init__.py` files exist

#### **2. Environment Variable Issues**
```
NEW_PROVIDER_CLIENT_ID not found
```
**Solution**: Verify `.env` file and environment variable names

#### **3. Redirect URI Mismatch**
```
redirect_uri_mismatch error
```
**Solution**: Check `NEW_PROVIDER_REDIRECT_URI` and provider app settings

#### **4. Token Exchange Failures**
```
invalid_grant error
```
**Solution**: Verify authorization code format and client credentials

#### **5. State Validation Failures**
```
Invalid state error
```
**Solution**: Check state format and TTL configuration

---

## 📚 **REFERENCES**

### **Framework Documentation**
- [OAuth Framework SSOT](./OAUTH_FRAMEWORK_SSOT.md)
- [Unified Token Service](../services/integrations/unified_token_service.py)
- [Standard Provider Base](../services/integrations/standard_oauth_provider.py)
- [Unified Router](../api/oauth_unified_routes.py)

### **OAuth Standards**
- [OAuth 2.0 RFC](https://tools.ietf.org/html/rfc6749)
- [OAuth 2.0 Security Best Practices](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-v2-31.html)
- [PostMessage Security](https://web.dev/specification/#postmessage-security)

### **Provider Examples**
- [Google OAuth 2.0](https://developers.google.com/identity/protocols/oauth2)
- [Microsoft OAuth 2.0](https://docs.microsoft.com/en-us/azure/active-directory/develop/v1-oauth2-authentication-code-flow)
- [Slack OAuth 2.0](https://api.slack.com/authentication/oauth-v2)

---

## 🎯 **SUCCESS METRICS**

### **Integration Time Estimates**
- **Simple OAuth 2.0**: 2-4 hours
- **Complex OAuth 2.0**: 4-8 hours  
- **OAuth 1.0a**: 6-12 hours
- **Custom Auth**: 8-16 hours

### **Quality Gates**
- [ ] All security checklist items complete
- [ ] Unit test coverage > 90%
- [ ] Integration tests passing
- [ ] Performance benchmarks met
- [ ] Documentation complete

---

## 🏆 **CONCLUSION**

The ALwrity OAuth Integration Framework provides **enterprise-grade foundation** for rapid, secure, and maintainable OAuth provider integration. By following this guide, developers can:

1. **Integrate new providers in hours, not days**
2. **Ensure consistent security across all integrations**
3. **Leverage unified monitoring and analytics**
4. **Maintain production-ready reliability and performance**

The framework's **security-first design**, **unified architecture**, and **comprehensive tooling** make it ideal for scaling to support dozens of third-party integrations while maintaining the highest security standards.
