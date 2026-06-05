# API Authentication

ALwrity uses API key authentication to secure access to all endpoints. This guide explains how to authenticate your requests and manage your API keys.

## Authentication Methods

### API Key Authentication

ALwrity uses Bearer token authentication with API keys. Include your API key in the `Authorization` header of all requests.

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     https://your-domain.com/api/blog-writer
```

### Header Format

```http
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json
```

## Getting Your API Key

### 1. Access the Dashboard

1. **Sign in** to your ALwrity account
2. **Navigate** to the API section
3. **Click** "Generate API Key"

### 2. Generate New Key

```json
{
  "name": "My Application",
  "description": "API key for my content management app",
  "permissions": ["read", "write"],
  "expires": "2024-12-31"
}
```

### 3. Store Securely

- **Never expose** API keys in client-side code
- **Use environment variables** for storage
- **Rotate keys** regularly
- **Monitor usage** for security

## API Key Management

### Key Properties

```json
{
  "id": "key_123456789",
  "name": "My Application",
  "key": "alwrity_sk_...",
  "permissions": ["read", "write"],
  "created_at": "2024-01-15T10:30:00Z",
  "expires_at": "2024-12-31T23:59:59Z",
  "last_used": "2024-01-20T14:22:00Z",
  "usage_count": 1250
}
```

### Permissions

| Permission | Description |
|------------|-------------|
| `read` | Read access to content and analytics |
| `write` | Create and update content |
| `admin` | Full administrative access |

### Key Rotation

```bash
## Create new key
curl -X POST "https://your-domain.com/api/keys" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Key",
    "permissions": ["read", "write"]
  }'

## Revoke old key
curl -X DELETE "https://your-domain.com/api/keys/old_key_id" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

## Rate Limiting

### Rate Limits by Plan

| Plan | Requests per Minute | Requests per Day |
|------|-------------------|------------------|
| Free | 10 | 100 |
| Basic | 60 | 1,000 |
| Pro | 300 | 10,000 |
| Enterprise | 1,000 | 100,000 |

### Rate Limit Headers

```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 59
X-RateLimit-Reset: 1640995200
```

### Handling Rate Limits

```python
import time
import requests

def make_request_with_retry(url, headers, data):
    max_retries = 3
    retry_delay = 1
    
    for attempt in range(max_retries):
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 429:  # Rate limited
            retry_after = int(response.headers.get('Retry-After', retry_delay))
            time.sleep(retry_after)
            retry_delay *= 2  # Exponential backoff
        else:
            return response
    
    raise Exception("Max retries exceeded")
```

## Error Handling

### Authentication Errors

#### Invalid API Key
```json
{
  "error": {
    "code": "INVALID_API_KEY",
    "message": "The provided API key is invalid or expired",
    "details": {
      "key_id": "key_123456789"
    }
  }
}
```

#### Missing API Key
```json
{
  "error": {
    "code": "MISSING_API_KEY",
    "message": "API key is required for authentication",
    "details": {
      "header": "Authorization: Bearer YOUR_API_KEY"
    }
  }
}
```

#### Insufficient Permissions
```json
{
  "error": {
    "code": "INSUFFICIENT_PERMISSIONS",
    "message": "API key does not have required permissions",
    "details": {
      "required": ["write"],
      "granted": ["read"]
    }
  }
}
```

### Rate Limit Errors

```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Please try again later.",
    "details": {
      "limit": 60,
      "remaining": 0,
      "reset_time": "2024-01-15T10:31:00Z"
    }
  }
}
```

## Security Best Practices

### API Key Security

1. **Environment Variables**
   ```bash
   export ALWRITY_API_KEY="your_api_key_here"
   ```

2. **Secure Storage**
   ```python
   import os
   api_key = os.getenv('ALWRITY_API_KEY')
   ```

3. **Key Rotation**
   - Rotate keys every 90 days
   - Use different keys for different environments
   - Monitor key usage regularly

### Request Security

1. **HTTPS Only**
   - Always use HTTPS for API requests
   - Never send API keys over HTTP

2. **Request Validation**
   - Validate all input data
   - Sanitize user inputs
   - Use proper content types

3. **Error Handling**
   - Don't expose sensitive information in errors
   - Log security events
   - Monitor for suspicious activity

## SDK Authentication

### Python SDK

```python
from alwrity import AlwrityClient

## Initialize client with API key
client = AlwrityClient(api_key="your_api_key_here")

## Or use environment variable
import os
client = AlwrityClient(api_key=os.getenv('ALWRITY_API_KEY'))
```

### JavaScript SDK

```javascript
const AlwrityClient = require('alwrity-js');

// Initialize client with API key
const client = new AlwrityClient('your_api_key_here');

// Or use environment variable
const client = new AlwrityClient(process.env.ALWRITY_API_KEY);
```

### cURL Examples

```bash
## Set API key as environment variable
export ALWRITY_API_KEY="your_api_key_here"

## Use in requests
curl -H "Authorization: Bearer $ALWRITY_API_KEY" \
     -H "Content-Type: application/json" \
     https://your-domain.com/api/blog-writer
```

## Testing Authentication

### Health Check

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
     https://your-domain.com/api/health
```

### Response
```json
{
  "status": "healthy",
  "authenticated": true,
  "user_id": "user_123456789",
  "permissions": ["read", "write"],
  "rate_limit": {
    "limit": 60,
    "remaining": 59,
    "reset": 1640995200
  }
}
```

## Troubleshooting

### Common Issues

#### 401 Unauthorized
- **Check API key**: Verify key is correct and active
- **Check format**: Ensure proper "Bearer " prefix
- **Check expiration**: Verify key hasn't expired

#### 403 Forbidden
- **Check permissions**: Verify key has required permissions
- **Check scope**: Ensure key has access to requested resource

#### 429 Too Many Requests
- **Check rate limits**: Verify you're within rate limits
- **Implement backoff**: Use exponential backoff for retries
- **Upgrade plan**: Consider upgrading for higher limits

### Getting Help

- **API Documentation**: Check endpoint documentation
- **Support**: Contact support for authentication issues
- **Community**: Join developer community for help
- **Status Page**: Check API status for outages

---

*Ready to authenticate your requests? [Get your API key](https://dashboard.alwrity.com/api-keys) and [start building](overview.md) with the ALwrity API!*
