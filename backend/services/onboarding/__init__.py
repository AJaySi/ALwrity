"""
Onboarding Services Package

This package contains all onboarding-related services and utilities.
All onboarding data is stored in the database with proper user isolation.

Services:
- OnboardingDatabaseService: Core database operations for onboarding data
- OnboardingProgressService: Progress tracking and step management
- OnboardingDataService: Data validation and processing
- OnboardingProgress: Progress tracking with database persistence (from api_key_manager)

Architecture:
- Database-first: All data stored in PostgreSQL with proper foreign keys
- User isolation: Each user's data is completely separate
- No file storage: Removed all JSON file operations for production scalability
- Local development: API keys still written to .env for convenience
"""

# Import all public classes for easy access
from .database_service import OnboardingDatabaseService
from .progress_service import OnboardingProgressService
from .data_service import OnboardingDataService
from .api_key_manager import OnboardingProgress, APIKeyManager, get_onboarding_progress, get_user_onboarding_progress, get_onboarding_progress_for_user

__all__ = [
    'OnboardingDatabaseService',
    'OnboardingProgressService', 
    'OnboardingDataService',
    'OnboardingProgress',
    'APIKeyManager',
    'get_onboarding_progress',
    'get_user_onboarding_progress',
    'get_onboarding_progress_for_user'
]
