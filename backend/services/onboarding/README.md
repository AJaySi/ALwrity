# Onboarding Services Package

This package contains all onboarding-related services and utilities for ALwrity. All onboarding data is stored in the database with proper user isolation, replacing the previous file-based JSON storage system.

## Architecture

### Database-First Design
- **Primary Storage**: PostgreSQL database with proper foreign keys and relationships
- **User Isolation**: Each user's onboarding data is completely separate
- **No File Storage**: Removed all JSON file operations for production scalability
- **Local Development**: API keys still written to `.env` for developer convenience

### Service Structure

```
backend/services/onboarding/
├── __init__.py                      # Package exports
├── database_service.py              # Core database operations
├── progress_service.py              # Progress tracking and step management
├── data_service.py                  # Data validation and processing
├── api_key_manager.py               # API key management + progress tracking
└── README.md                        # This documentation
```

## Services

### 1. OnboardingDatabaseService (`database_service.py`)
**Purpose**: Core database operations for onboarding data with user isolation.

**Key Features**:
- User-specific session management
- API key storage and retrieval
- Website analysis persistence
- Research preferences management
- Persona data storage
- Brand analysis support (feature-flagged)

**Main Methods**:
- `get_or_create_session(user_id)` - Get or create user session
- `save_api_key(user_id, provider, key)` - Store API keys
- `save_website_analysis(user_id, data)` - Store website analysis
- `save_research_preferences(user_id, prefs)` - Store research settings
- `save_persona_data(user_id, data)` - Store persona information

### 2. OnboardingProgressService (`progress_service.py`)
**Purpose**: High-level progress tracking and step management.

**Key Features**:
- Database-only progress tracking
- Step completion validation
- Progress percentage calculation
- Onboarding completion management

**Main Methods**:
- `get_onboarding_status(user_id)` - Get current status
- `update_step(user_id, step_number)` - Update current step
- `update_progress(user_id, percentage)` - Update progress
- `complete_onboarding(user_id)` - Mark as complete

### 3. OnboardingDataService (`data_service.py`)
**Purpose**: Extract and use onboarding data for AI personalization.

**Key Features**:
- Personalized AI input generation
- Website analysis data extraction
- Research preferences integration
- Default fallback data

**Main Methods**:
- `get_personalized_ai_inputs(user_id)` - Generate personalized inputs
- `get_user_website_analysis(user_id)` - Get website data
- `get_user_research_preferences(user_id)` - Get research settings

### 4. OnboardingProgress + APIKeyManager (`api_key_manager.py`)
**Purpose**: Combined API key management and progress tracking with database persistence.

**Key Features**:
- Database-only progress persistence (no JSON files)
- API key management with environment integration
- Step-by-step progress tracking
- User-specific progress instances

**Main Classes**:
- `OnboardingProgress` - Progress tracking with database persistence
- `APIKeyManager` - API key management
- `StepData` - Individual step data structure
- `StepStatus` - Step status enumeration

## Database Schema

### Core Tables
- `onboarding_sessions` - User session tracking
- `api_keys` - User-specific API key storage
- `website_analyses` - Website analysis data
- `research_preferences` - User research settings
- `persona_data` - Generated persona information

### Relationships
- All data tables reference `onboarding_sessions.id`
- User isolation via `user_id` foreign key
- Proper cascade deletion and updates

## Usage Examples

### Basic Progress Tracking
```python
from services.onboarding import OnboardingProgress

# Get user-specific progress
progress = OnboardingProgress(user_id="user123")

# Mark step as completed
progress.mark_step_completed(1, {"api_keys": {"openai": "sk-..."}})

# Get progress summary
summary = progress.get_progress_summary()
```

### Database Operations
```python
from services.onboarding import OnboardingDatabaseService
from services.database import SessionLocal

db = SessionLocal()
service = OnboardingDatabaseService(db)

# Save API key
service.save_api_key("user123", "openai", "sk-...")

# Get website analysis
analysis = service.get_website_analysis("user123", db)
```

### Progress Service
```python
from services.onboarding import OnboardingProgressService

service = OnboardingProgressService()

# Get status
status = service.get_onboarding_status("user123")

# Update progress
service.update_step("user123", 2)
service.update_progress("user123", 50.0)
```

## Migration from File-Based Storage

### What Was Removed
- JSON file operations (`.onboarding_progress*.json`)
- File-based progress persistence
- Dual persistence system (file + database)

### What Was Kept
- Database persistence (enhanced)
- Local development `.env` API key writing
- All existing functionality and APIs

### Benefits
- **Production Ready**: No ephemeral file storage
- **Scalable**: Database-backed with proper indexing
- **User Isolated**: Complete data separation
- **Maintainable**: Single source of truth

## Environment Variables

### Required
- Database connection (via `services.database`)
- User authentication system

### Optional
- `ENABLE_WEBSITE_BRAND_COLUMNS=true` - Enable brand analysis features
- `DEPLOY_ENV=local` - Enable local `.env` API key writing

## Error Handling

All services include comprehensive error handling:
- Database connection failures
- User not found scenarios
- Invalid data validation
- Graceful fallbacks to defaults

## Performance Considerations

- Database queries are optimized with proper indexing
- User-specific caching where appropriate
- Minimal database calls through efficient service design
- Connection pooling via SQLAlchemy

## Testing

Each service can be tested independently:
- Unit tests for individual methods
- Integration tests with database
- Mock database sessions for isolated testing

## Future Enhancements

- Real-time progress updates via WebSocket
- Progress analytics and reporting
- Bulk user operations
- Advanced validation rules
- Progress recovery mechanisms
