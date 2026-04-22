# ALwrity Project

## What This Is
ALwrity is an AI-powered content creation platform that helps users generate various types of content including podcasts, videos, blogs, and social media content. The platform features a React frontend and a FastAPI backend with onboarding workflows, API key management, and content generation capabilities.

## Core Value
To provide an all-in-one AI content creation suite that simplifies the content production process for creators, marketers, and businesses.

## Current Focus
Based on recent git commits, the team has been working on:
- Podcast production features (voice cloning, avatar generation, B-roll integration)
- Onboarding flow improvements
- Backend stability and debugging
- Frontend UI/UX enhancements

## Requirements

### Validated
- User authentication (Clerk)
- API key management for AI providers
- Basic podcast generation workflow
- File storage and media handling

### Active
- Podcast script generation and editing
- Voice cloning and avatar creation
- B-roll scene rendering and integration
- Onboarding flow completion tracking
- API endpoint stability and debugging

### Out of Scope
- Mobile applications (currently web-only)
- Enterprise team collaboration features
- Advanced analytics dashboard

## Key Decisions
- Using FastAPI for backend performance
- React with Material-UI for frontend consistency
- Modular API design for extensibility
- Database-first approach for persistence

## Constraints
- Must maintain backward compatibility with existing API
- Deployment targets include both development and production environments
- Must support multiple AI providers (OpenAI, HuggingFace, etc.)
- Budget-conscious resource usage for AI API calls