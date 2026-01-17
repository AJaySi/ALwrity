# ALwrity Onboarding System - API Reference

## Overview

This document provides a comprehensive API reference for the ALwrity Onboarding System. All endpoints require authentication and return JSON responses.

## 🔐 Authentication

All endpoints require a valid Clerk JWT token in the Authorization header:

```
Authorization: Bearer <clerk_jwt_token>
```

## 📋 Core Endpoints

### Onboarding Status

#### GET `/api/onboarding/status`
Get the current onboarding status for the authenticated user.

**Response:**
```json
{
  "is_completed": false,
  "current_step": 2,
  "completion_percentage": 33.33,
  "next_step": 3,
  "started_at": "2024-01-15T10:30:00Z",
  "completed_at": null,
  "can_proceed_to_final": false
}
```

#### GET `/api/onboarding/progress`
Get the full onboarding progress data.

**Response:**
```json
{
  "steps": [
    {
      "step_number": 1,
      "title": "AI LLM Providers Setup",
      "description": "Configure your AI services",
      "status": "completed",
      "completed_at": "2024-01-15T10:35:00Z",
      "data": {...},
      "validation_errors": []
    }
  ],
  "current_step": 2,
  "started_at": "2024-01-15T10:30:00Z",
  "last_updated": "2024-01-15T10:35:00Z",
  "is_completed": false,
  "completed_at": null
}
```

### Step Management

#### GET `/api/onboarding/step/{step_number}`
Get data for a specific step.

**Parameters:**
- `step_number` (int): The step number (1-6)

**Response:**
```json
{
  "step_number": 1,
  "title": "AI LLM Providers Setup",
  "description": "Configure your AI services",
  "status": "in_progress",
  "completed_at": null,
  "data": {...},
  "validation_errors": []
}
```

#### POST `/api/onboarding/step/{step_number}/complete`
Mark a step as completed.

**Parameters:**
- `step_number` (int): The step number (1-6)

**Request Body:**
```json
{
  "data": {
    "api_keys": {
      "gemini": "your_gemini_key",
      "exa": "your_exa_key",
      "copilotkit": "your_copilotkit_key"
    }
  },
  "validation_errors": []
}
```

**Response:**
```json
{
  "message": "Step 1 completed successfully",
  "step_number": 1,
  "data": {...}
}
```

#### POST `/api/onboarding/step/{step_number}/skip`
Skip a step (for optional steps).

**Parameters:**
- `step_number` (int): The step number (1-6)

**Response:**
```json
{
  "message": "Step 2 skipped successfully",
  "step_number": 2
}
```

#### GET `/api/onboarding/step/{step_number}/validate`
Validate if user can access a specific step.

**Parameters:**
- `step_number` (int): The step number (1-6)

**Response:**
```json
{
  "can_proceed": true,
  "validation_errors": [],
  "step_status": "available"
}
```

### Onboarding Control

#### POST `/api/onboarding/start`
Start a new onboarding session.

**Response:**
```json
{
  "message": "Onboarding started successfully",
  "current_step": 1,
  "started_at": "2024-01-15T10:30:00Z"
}
```

#### POST `/api/onboarding/reset`
Reset the onboarding progress.

**Response:**
```json
{
  "message": "Onboarding progress reset successfully",
  "current_step": 1,
  "started_at": "2024-01-15T10:30:00Z"
}
```

#### GET `/api/onboarding/resume`
Get information for resuming onboarding.

**Response:**
```json
{
  "can_resume": true,
  "resume_step": 2,
  "current_step": 2,
  "completion_percentage": 33.33,
  "started_at": "2024-01-15T10:30:00Z",
  "last_updated": "2024-01-15T10:35:00Z"
}
```

#### POST `/api/onboarding/complete`
Complete the onboarding process.

**Response:**
```json
{
  "message": "Onboarding completed successfully",
  "completion_data": {...},
  "persona_generated": true,
  "environment_setup": true
}
```

## 🔑 API Key Management

### GET `/api/onboarding/api-keys`
Get all configured API keys (masked for security).

**Response:**
```json
{
  "api_keys": {
    "gemini": "********************abcd",
    "exa": "********************efgh",
    "copilotkit": "********************ijkl"
  },
  "total_providers": 3,
  "configured_providers": ["gemini", "exa", "copilotkit"]
}
```

### POST `/api/onboarding/api-keys`
Save an API key for a provider.

**Request Body:**
```json
{
  "provider": "gemini",
  "api_key": "your_api_key_here",
  "description": "Gemini API key for content generation"
}
```

**Response:**
```json
{
  "message": "API key for gemini saved successfully",
  "provider": "gemini",
  "status": "saved"
}
```

### GET `/api/onboarding/api-keys/validate`
Validate all configured API keys.

**Response:**
```json
{
  "validation_results": {
    "gemini": {
      "valid": true,
      "status": "active",
      "quota_remaining": 1000
    },
    "exa": {
      "valid": true,
      "status": "active",
      "quota_remaining": 500
    }
  },
  "all_valid": true,
  "total_providers": 2
}
```

## ⚙️ Configuration

### GET `/api/onboarding/config`
Get onboarding configuration and requirements.

**Response:**
```json
{
  "total_steps": 6,
  "required_steps": [1, 2, 3, 4, 6],
  "optional_steps": [5],
  "step_requirements": {
    "1": ["gemini", "exa", "copilotkit"],
    "2": ["website_url"],
    "3": ["research_preferences"],
    "4": ["personalization_settings"],
    "5": ["integrations"],
    "6": ["persona_generation"]
  }
}
```

### GET `/api/onboarding/providers`
Get setup information for all providers.

**Response:**
```json
{
  "providers": {
    "gemini": {
      "name": "Gemini AI",
      "description": "Advanced content generation",
      "setup_url": "https://ai.google.dev/",
      "required": true,
      "validation_endpoint": "https://generativelanguage.googleapis.com/v1beta/models"
    },
    "exa": {
      "name": "Exa AI",
      "description": "Intelligent web research",
      "setup_url": "https://exa.ai/",
      "required": true,
      "validation_endpoint": "https://api.exa.ai/v1/search"
    }
  }
}
```

### GET `/api/onboarding/providers/{provider}`
Get setup information for a specific provider.

**Parameters:**
- `provider` (string): Provider name (gemini, exa, copilotkit)

**Response:**
```json
{
  "name": "Gemini AI",
  "description": "Advanced content generation",
  "setup_url": "https://ai.google.dev/",
  "required": true,
  "validation_endpoint": "https://generativelanguage.googleapis.com/v1beta/models",
  "setup_instructions": [
    "Visit Google AI Studio",
    "Create a new API key",
    "Copy the API key",
    "Paste it in the form above"
  ]
}
```

### POST `/api/onboarding/providers/{provider}/validate`
Validate a specific provider's API key.

**Parameters:**
- `provider` (string): Provider name (gemini, exa, copilotkit)

**Request Body:**
```json
{
  "api_key": "your_api_key_here"
}
```

**Response:**
```json
{
  "valid": true,
  "status": "active",
  "quota_remaining": 1000,
  "provider": "gemini"
}
```

## 📊 Summary & Analytics

### GET `/api/onboarding/summary`
Get comprehensive onboarding summary for the final step.

**Response:**
```json
{
  "user_info": {
    "user_id": "user_123",
    "onboarding_started": "2024-01-15T10:30:00Z",
    "current_step": 6
  },
  "api_keys": {
    "gemini": "configured",
    "exa": "configured",
    "copilotkit": "configured"
  },
  "website_analysis": {
    "url": "https://example.com",
    "status": "completed",
    "style_analysis": "professional",
    "content_count": 25
  },
  "research_preferences": {
    "depth": "comprehensive",
    "auto_research": true,
    "fact_checking": true
  },
  "personalization": {
    "brand_voice": "professional",
    "target_audience": "B2B professionals",
    "content_types": ["blog_posts", "social_media"]
  }
}
```

### GET `/api/onboarding/website-analysis`
Get website analysis data.

**Response:**
```json
{
  "url": "https://example.com",
  "analysis_status": "completed",
  "content_analyzed": 25,
  "style_characteristics": {
    "tone": "professional",
    "voice": "authoritative",
    "complexity": "intermediate"
  },
  "target_audience": "B2B professionals",
  "content_themes": ["technology", "business", "innovation"]
}
```

### GET `/api/onboarding/research-preferences`
Get research preferences data.

**Response:**
```json
{
  "research_depth": "comprehensive",
  "auto_research_enabled": true,
  "fact_checking_enabled": true,
  "content_types": ["blog_posts", "articles", "social_media"],
  "research_sources": ["web", "academic", "news"]
}
```

## 👤 Business Information

### POST `/api/onboarding/business-info`
Save business information for users without websites.

**Request Body:**
```json
{
  "business_name": "Acme Corp",
  "industry": "Technology",
  "description": "AI-powered solutions",
  "target_audience": "B2B professionals",
  "brand_voice": "professional",
  "content_goals": ["lead_generation", "brand_awareness"]
}
```

**Response:**
```json
{
  "id": 1,
  "business_name": "Acme Corp",
  "industry": "Technology",
  "description": "AI-powered solutions",
  "target_audience": "B2B professionals",
  "brand_voice": "professional",
  "content_goals": ["lead_generation", "brand_awareness"],
  "created_at": "2024-01-15T10:30:00Z"
}
```

### GET `/api/onboarding/business-info/{id}`
Get business information by ID.

**Parameters:**
- `id` (int): Business information ID

**Response:**
```json
{
  "id": 1,
  "business_name": "Acme Corp",
  "industry": "Technology",
  "description": "AI-powered solutions",
  "target_audience": "B2B professionals",
  "brand_voice": "professional",
  "content_goals": ["lead_generation", "brand_awareness"],
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### GET `/api/onboarding/business-info/user/{user_id}`
Get business information by user ID.

**Parameters:**
- `user_id` (int): User ID

**Response:**
```json
{
  "id": 1,
  "business_name": "Acme Corp",
  "industry": "Technology",
  "description": "AI-powered solutions",
  "target_audience": "B2B professionals",
  "brand_voice": "professional",
  "content_goals": ["lead_generation", "brand_awareness"],
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### PUT `/api/onboarding/business-info/{id}`
Update business information.

**Parameters:**
- `id` (int): Business information ID

**Request Body:**
```json
{
  "business_name": "Acme Corp Updated",
  "industry": "Technology",
  "description": "Updated AI-powered solutions",
  "target_audience": "B2B professionals",
  "brand_voice": "professional",
  "content_goals": ["lead_generation", "brand_awareness", "thought_leadership"]
}
```

**Response:**
```json
{
  "id": 1,
  "business_name": "Acme Corp Updated",
  "industry": "Technology",
  "description": "Updated AI-powered solutions",
  "target_audience": "B2B professionals",
  "brand_voice": "professional",
  "content_goals": ["lead_generation", "brand_awareness", "thought_leadership"],
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T11:00:00Z"
}
```

## 🎭 Persona Management

### GET `/api/onboarding/persona/readiness/{user_id}`
Check if user has sufficient data for persona generation.

**Parameters:**
- `user_id` (int): User ID

**Response:**
```json
{
  "ready": true,
  "missing_data": [],
  "completion_percentage": 100,
  "recommendations": []
}
```

### GET `/api/onboarding/persona/preview/{user_id}`
Generate a preview of the writing persona without saving.

**Parameters:**
- `user_id` (int): User ID

**Response:**
```json
{
  "persona_preview": {
    "name": "Professional Content Creator",
    "voice": "authoritative",
    "tone": "professional",
    "style_characteristics": {
      "formality": "high",
      "complexity": "intermediate",
      "engagement": "informative"
    },
    "content_preferences": {
      "length": "medium",
      "format": "structured",
      "research_depth": "comprehensive"
    }
  },
  "generation_time": "2.5s",
  "confidence_score": 0.95
}
```

### POST `/api/onboarding/persona/generate/{user_id}`
Generate and save a writing persona from onboarding data.

**Parameters:**
- `user_id` (int): User ID

**Response:**
```json
{
  "persona_id": 1,
  "name": "Professional Content Creator",
  "voice": "authoritative",
  "tone": "professional",
  "style_characteristics": {...},
  "content_preferences": {...},
  "created_at": "2024-01-15T10:30:00Z",
  "status": "active"
}
```

### GET `/api/onboarding/persona/user/{user_id}`
Get all writing personas for the user.

**Parameters:**
- `user_id` (int): User ID

**Response:**
```json
{
  "personas": [
    {
      "id": 1,
      "name": "Professional Content Creator",
      "voice": "authoritative",
      "tone": "professional",
      "status": "active",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total_count": 1,
  "active_persona": 1
}
```

## 🚨 Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid request data",
  "error_code": "INVALID_REQUEST",
  "validation_errors": [
    "Field 'api_key' is required",
    "Field 'provider' must be one of: gemini, exa, copilotkit"
  ]
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication required",
  "error_code": "UNAUTHORIZED"
}
```

### 404 Not Found
```json
{
  "detail": "Step 7 not found",
  "error_code": "STEP_NOT_FOUND"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error",
  "error_code": "INTERNAL_ERROR"
}
```

## 📝 Request/Response Models

### StepCompletionRequest
```json
{
  "data": {
    "api_keys": {
      "gemini": "string",
      "exa": "string",
      "copilotkit": "string"
    }
  },
  "validation_errors": ["string"]
}
```

### APIKeyRequest
```json
{
  "provider": "string",
  "api_key": "string",
  "description": "string"
}
```

### BusinessInfoRequest
```json
{
  "business_name": "string",
  "industry": "string",
  "description": "string",
  "target_audience": "string",
  "brand_voice": "string",
  "content_goals": ["string"]
}
```

## 🔄 Rate Limiting

- **Standard endpoints**: 100 requests per minute
- **API key validation**: 10 requests per minute
- **Persona generation**: 5 requests per minute

## 📊 Response Times

- **Status checks**: < 100ms
- **Step completion**: < 500ms
- **API key validation**: < 2s
- **Persona generation**: < 10s
- **Website analysis**: < 30s

---

*This API reference provides comprehensive documentation for all onboarding endpoints. For additional support, please refer to the main project documentation or contact the development team.*
