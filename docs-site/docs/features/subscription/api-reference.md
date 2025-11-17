# Subscription API Reference

Complete API endpoint documentation for the ALwrity subscription system.

## Base URL

All endpoints are prefixed with `/api/subscription`

## Authentication

All endpoints require user authentication. Include the user ID in the request path or headers as appropriate.

## Subscription Management Endpoints

### Get All Subscription Plans

Get a list of all available subscription plans.

```http
GET /api/subscription/plans
```

**Response:**

```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "Free",
      "price": 0.0,
      "billing_cycle": "monthly",
      "limits": {
        "gemini_calls": 100,
        "tokens": 100000
      }
    },
    {
      "id": 2,
      "name": "Basic",
      "price": 29.0,
      "billing_cycle": "monthly",
      "limits": {
        "gemini_calls": 1000,
        "openai_calls": 500,
        "tokens": 1500000,
        "monthly_cost": 50.0
      }
    }
  ]
}
```

### Get User Subscription

Get the current subscription details for a specific user.

```http
GET /api/subscription/user/{user_id}/subscription
```

**Parameters:**
- `user_id` (path): The user's unique identifier

**Response:**

```json
{
  "success": true,
  "data": {
    "user_id": "user123",
    "plan_name": "Pro",
    "plan_id": 3,
    "status": "active",
    "started_at": "2025-01-01T00:00:00Z",
    "expires_at": "2025-02-01T00:00:00Z",
    "limits": {
      "gemini_calls": 5000,
      "openai_calls": 2500,
      "monthly_cost": 150.0
    }
  }
}
```

### Get API Pricing Information

Get current pricing configuration for all API providers.

```http
GET /api/subscription/pricing
```

**Response:**

```json
{
  "success": true,
  "data": [
    {
      "provider": "gemini",
      "model": "gemini-2.5-flash",
      "input_cost_per_1m": 0.125,
      "output_cost_per_1m": 0.375
    },
    {
      "provider": "tavily",
      "cost_per_request": 0.001
    }
  ]
}
```

## Usage Tracking Endpoints

### Get Current Usage Statistics

Get current usage statistics for a user.

```http
GET /api/subscription/usage/{user_id}
```

**Parameters:**
- `user_id` (path): The user's unique identifier

**Response:**

```json
{
  "success": true,
  "data": {
    "billing_period": "2025-01",
    "total_calls": 1250,
    "total_tokens": 210000,
    "total_cost": 15.75,
    "usage_status": "active",
    "limits": {
      "gemini_calls": 5000,
      "monthly_cost": 150.0
    },
    "provider_breakdown": {
      "gemini": {
        "calls": 800,
        "tokens": 125000,
        "cost": 10.50
      },
      "openai": {
        "calls": 450,
        "tokens": 85000,
        "cost": 5.25
      }
    },
    "usage_percentages": {
      "gemini_calls": 16.0,
      "cost": 10.5
    }
  }
}
```

### Get Usage Trends

Get historical usage trends over time.

```http
GET /api/subscription/usage/{user_id}/trends?months=6
```

**Parameters:**
- `user_id` (path): The user's unique identifier
- `months` (query, optional): Number of months to retrieve (default: 6)

**Response:**

```json
{
  "success": true,
  "data": {
    "periods": [
      {
        "period": "2024-07",
        "total_calls": 850,
        "total_cost": 12.50,
        "provider_breakdown": {
          "gemini": {"calls": 600, "cost": 8.00},
          "openai": {"calls": 250, "cost": 4.50}
        }
      }
    ],
    "trends": {
      "calls_trend": "increasing",
      "cost_trend": "stable"
    }
  }
}
```

### Get Dashboard Data

Get comprehensive dashboard data including usage, limits, projections, and alerts.

```http
GET /api/subscription/dashboard/{user_id}
```

**Parameters:**
- `user_id` (path): The user's unique identifier

**Response:**

```json
{
  "success": true,
  "data": {
    "summary": {
      "total_api_calls_this_month": 1250,
      "total_cost_this_month": 15.75,
      "usage_status": "active",
      "unread_alerts": 2
    },
    "current_usage": {
      "billing_period": "2025-01",
      "total_calls": 1250,
      "total_cost": 15.75,
      "usage_status": "active",
      "provider_breakdown": {
        "gemini": {"calls": 800, "cost": 10.50, "tokens": 125000},
        "openai": {"calls": 450, "cost": 5.25, "tokens": 85000}
      },
      "usage_percentages": {
        "gemini_calls": 16.0,
        "openai_calls": 18.0,
        "cost": 10.5
      }
    },
    "limits": {
      "plan_name": "Pro",
      "limits": {
        "gemini_calls": 5000,
        "openai_calls": 2500,
        "monthly_cost": 150.0
      }
    },
    "projections": {
      "projected_monthly_cost": 47.25,
      "projected_usage_percentage": 31.5
    },
    "alerts": [
      {
        "id": 1,
        "title": "API Usage Notice - Gemini",
        "message": "You have used 800 of 5,000 Gemini API calls",
        "severity": "info",
        "created_at": "2025-01-15T10:30:00Z",
        "read": false
      }
    ]
  }
}
```

## Alerts & Notifications Endpoints

### Get Usage Alerts

Get usage alerts and notifications for a user.

```http
GET /api/subscription/alerts/{user_id}?unread_only=false
```

**Parameters:**
- `user_id` (path): The user's unique identifier
- `unread_only` (query, optional): Filter to only unread alerts (default: false)

**Response:**

```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "user_id": "user123",
      "title": "API Usage Notice - Gemini",
      "message": "You have used 800 of 5,000 Gemini API calls",
      "severity": "info",
      "alert_type": "usage_threshold",
      "created_at": "2025-01-15T10:30:00Z",
      "read": false
    },
    {
      "id": 2,
      "user_id": "user123",
      "title": "Usage Warning",
      "message": "You have reached 90% of your monthly cost limit",
      "severity": "warning",
      "alert_type": "cost_threshold",
      "created_at": "2025-01-20T14:15:00Z",
      "read": false
    }
  ]
}
```

### Mark Alert as Read

Mark a specific alert as read.

```http
POST /api/subscription/alerts/{alert_id}/mark-read
```

**Parameters:**
- `alert_id` (path): The alert's unique identifier

**Response:**

```json
{
  "success": true,
  "message": "Alert marked as read"
}
```

## Usage Examples

### Get User Usage (cURL)

```bash
curl -X GET "http://localhost:8000/api/subscription/usage/user123" \
  -H "Content-Type: application/json"
```

### Get Dashboard Data (cURL)

```bash
curl -X GET "http://localhost:8000/api/subscription/dashboard/user123" \
  -H "Content-Type: application/json"
```

### Get Usage Trends (cURL)

```bash
curl -X GET "http://localhost:8000/api/subscription/usage/user123/trends?months=6" \
  -H "Content-Type: application/json"
```

### JavaScript Example

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

// Get current usage percentages
const usage = data.data.current_usage;
console.log(usage.usage_percentages);
// {
//   gemini_calls: 16.0,
//   openai_calls: 18.0,
//   cost: 10.5
// }
```

### Python Example

```python
import requests

# Get user usage statistics
response = requests.get(
    f"http://localhost:8000/api/subscription/usage/{user_id}",
    headers={"Content-Type": "application/json"}
)

data = response.json()
usage = data["data"]

print(f"Total calls: {usage['total_calls']}")
print(f"Total cost: ${usage['total_cost']}")
print(f"Status: {usage['usage_status']}")
```

## Error Responses

All endpoints return consistent error responses:

```json
{
  "success": false,
  "error": "error_type",
  "message": "Human-readable error message",
  "details": "Additional error details",
  "user_id": "user123",
  "timestamp": "2025-01-15T10:30:00Z"
}
```

### Common Error Codes

- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Authentication required
- `404 Not Found`: Resource not found
- `429 Too Many Requests`: Usage limit exceeded
- `500 Internal Server Error`: Server error

## Rate Limiting

Usage limits are enforced automatically. When a limit is exceeded, the API returns a `429 Too Many Requests` response:

```json
{
  "success": false,
  "error": "UsageLimitExceededException",
  "message": "Usage limit exceeded for Gemini API calls",
  "details": {
    "provider": "gemini",
    "limit_type": "api_calls",
    "current_usage": 1000,
    "limit_value": 1000
  }
}
```

## Next Steps

- [Overview](overview.md) - System architecture and features
- [Setup](setup.md) - Installation and configuration
- [Pricing](pricing.md) - Subscription plans and API pricing

---

**Last Updated**: January 2025

