"""
API Key Manager with Database-Only Onboarding Progress
Manages API keys and onboarding progress with database persistence only.
Removed all file-based JSON storage for production scalability.
"""

import os
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from loguru import logger
from enum import Enum

from services.database import get_db_session


class StepStatus(Enum):
    """Onboarding step status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    FAILED = "failed"


class StepData:
    """Data structure for onboarding step."""
    
    def __init__(self, step_number: int, title: str, description: str, status: StepStatus = StepStatus.PENDING):
        self.step_number = step_number
        self.title = title
        self.description = description
        self.status = status
        self.completed_at = None
        self.data = None
        self.validation_errors = []


class OnboardingProgress:
    """Manages onboarding progress with database persistence only."""
    
    def __init__(self, user_id: Optional[str] = None):
        self.steps = self._initialize_steps()
        self.current_step = 1
        self.started_at = datetime.now().isoformat()
        self.last_updated = datetime.now().isoformat()
        self.is_completed = False
        self.completed_at = None
        self.user_id = user_id  # Add user_id for database isolation
        
        # Initialize database service for persistence
        try:
            from .database_service import OnboardingDatabaseService
            self.db_service = OnboardingDatabaseService()
            self.use_database = True
            logger.info(f"Database service initialized for user {user_id}")
        except Exception as e:
            logger.error(f"Database service not available: {e}")
            self.db_service = None
            self.use_database = False
            raise Exception(f"Database service required but not available: {e}")
        
        # Load existing progress from database if available
        if self.use_database and self.user_id:
            self.load_progress_from_db()
    
    def _initialize_steps(self) -> List[StepData]:
        """Initialize the 6-step onboarding process."""
        return [
            StepData(1, "AI LLM Providers", "Configure AI language model providers", StepStatus.PENDING),
            StepData(2, "Website Analysis", "Set up website analysis and crawling", StepStatus.PENDING),
            StepData(3, "AI Research", "Configure AI research capabilities", StepStatus.PENDING),
            StepData(4, "Personalization", "Set up personalization features", StepStatus.PENDING),
            StepData(5, "Integrations", "Configure ALwrity integrations", StepStatus.PENDING),
            StepData(6, "Complete Setup", "Finalize and complete onboarding", StepStatus.PENDING)
        ]
    
    def get_step_data(self, step_number: int) -> Optional[StepData]:
        """Get data for a specific step."""
        for step in self.steps:
            if step.step_number == step_number:
                return step
        return None
    
    def mark_step_completed(self, step_number: int, data: Optional[Dict[str, Any]] = None):
        """Mark a step as completed."""
        logger.info(f"[mark_step_completed] Marking step {step_number} as completed")
        step = self.get_step_data(step_number)
        if step:
            step.status = StepStatus.COMPLETED
            step.completed_at = datetime.now().isoformat()
            step.data = data
            self.last_updated = datetime.now().isoformat()
            
            # Check if all steps are now completed
            all_completed = all(s.status in [StepStatus.COMPLETED, StepStatus.SKIPPED] for s in self.steps)
            
            if all_completed:
                # If all steps are completed, mark onboarding as complete
                self.is_completed = True
                self.completed_at = datetime.now().isoformat()
                self.current_step = len(self.steps)  # Set to last step number
                logger.info(f"[mark_step_completed] All steps completed, marking onboarding as complete")
            else:
                # Only increment current_step if there are more steps to go
                self.current_step = step_number + 1
                # Ensure current_step doesn't exceed total steps
                if self.current_step > len(self.steps):
                    self.current_step = len(self.steps)
            
            logger.info(f"[mark_step_completed] Step {step_number} completed, new current_step: {self.current_step}, is_completed: {self.is_completed}")
            self.save_progress()
            logger.info(f"Step {step_number} marked as completed")
        else:
            logger.error(f"[mark_step_completed] Step {step_number} not found")
    
    def mark_step_in_progress(self, step_number: int):
        """Mark a step as in progress."""
        step = self.get_step_data(step_number)
        if step:
            step.status = StepStatus.IN_PROGRESS
            self.current_step = step_number
            self.last_updated = datetime.now().isoformat()
            self.save_progress()
            logger.info(f"Step {step_number} marked as in progress")
        else:
            logger.error(f"Step {step_number} not found")
    
    def mark_step_skipped(self, step_number: int):
        """Mark a step as skipped."""
        step = self.get_step_data(step_number)
        if step:
            step.status = StepStatus.SKIPPED
            step.completed_at = datetime.now().isoformat()
            self.last_updated = datetime.now().isoformat()
            self.save_progress()
            logger.info(f"Step {step_number} marked as skipped")
        else:
            logger.error(f"Step {step_number} not found")
    
    def mark_step_failed(self, step_number: int, error_message: str):
        """Mark a step as failed with error message."""
        step = self.get_step_data(step_number)
        if step:
            step.status = StepStatus.FAILED
            step.validation_errors.append(error_message)
            self.last_updated = datetime.now().isoformat()
            self.save_progress()
            logger.error(f"Step {step_number} marked as failed: {error_message}")
        else:
            logger.error(f"Step {step_number} not found")
    
    def get_progress_summary(self) -> Dict[str, Any]:
        """Get current progress summary."""
        completed_count = sum(1 for s in self.steps if s.status == StepStatus.COMPLETED)
        skipped_count = sum(1 for s in self.steps if s.status == StepStatus.SKIPPED)
        failed_count = sum(1 for s in self.steps if s.status == StepStatus.FAILED)
        
        return {
            "total_steps": len(self.steps),
            "completed_steps": completed_count,
            "skipped_steps": skipped_count,
            "failed_steps": failed_count,
            "current_step": self.current_step,
            "is_completed": self.is_completed,
            "progress_percentage": (completed_count + skipped_count) / len(self.steps) * 100
        }
    
    def get_next_step(self) -> Optional[StepData]:
        """Get the next step to work on."""
        for step in self.steps:
            if step.status == StepStatus.PENDING:
                return step
        return None
    
    def get_completed_steps(self) -> List[StepData]:
        """Get all completed steps."""
        return [step for step in self.steps if step.status == StepStatus.COMPLETED]
    
    def get_failed_steps(self) -> List[StepData]:
        """Get all failed steps."""
        return [step for step in self.steps if step.status == StepStatus.FAILED]
    
    def reset_step(self, step_number: int):
        """Reset a step to pending status."""
        step = self.get_step_data(step_number)
        if step:
            step.status = StepStatus.PENDING
            step.completed_at = None
            step.data = None
            step.validation_errors = []
            self.last_updated = datetime.now().isoformat()
            self.save_progress()
            logger.info(f"Step {step_number} reset to pending")
        else:
            logger.error(f"Step {step_number} not found")
    
    def reset_all_steps(self):
        """Reset all steps to pending status."""
        for step in self.steps:
            step.status = StepStatus.PENDING
            step.completed_at = None
            step.data = None
            step.validation_errors = []
        
        self.current_step = 1
        self.is_completed = False
        self.completed_at = None
        self.last_updated = datetime.now().isoformat()
        self.save_progress()
        logger.info("All steps reset to pending")
    
    def complete_onboarding(self):
        """Mark onboarding as complete."""
        self.is_completed = True
        self.completed_at = datetime.now().isoformat()
        self.current_step = len(self.steps)
        self.last_updated = datetime.now().isoformat()
        self.save_progress()
        logger.info("Onboarding completed successfully")
    
    def save_progress(self):
        """Save progress to database."""
        if not self.use_database or not self.db_service or not self.user_id:
            logger.error("Cannot save progress: database service not available or user_id not set")
            return
            
        try:
            from services.database import SessionLocal
            db = SessionLocal()
            try:
                # Update session progress
                self.db_service.update_step(self.user_id, self.current_step, db)
                
                # Calculate progress percentage
                completed_count = sum(1 for s in self.steps if s.status == StepStatus.COMPLETED)
                progress_pct = (completed_count / len(self.steps)) * 100
                self.db_service.update_progress(self.user_id, progress_pct, db)
                
                # Save step-specific data to appropriate tables
                for step in self.steps:
                    if step.status == StepStatus.COMPLETED and step.data:
                        if step.step_number == 1:  # API Keys
                            api_keys = step.data.get('api_keys', {})
                            for provider, key in api_keys.items():
                                if key:
                                    # Save to database (for user isolation in production)
                                    self.db_service.save_api_key(self.user_id, provider, key, db)
                                    
                                    # Also save to .env file ONLY in local development
                                    # This allows local developers to have keys in .env for convenience
                                    # In production, keys are fetched from database per user
                                    is_local = os.getenv('DEPLOY_ENV', 'local') == 'local'
                                    if is_local:
                                        try:
                                            from services.api_key_manager import APIKeyManager
                                            api_key_manager = APIKeyManager()
                                            api_key_manager.save_api_key(provider, key)
                                            logger.info(f"[LOCAL] API key for {provider} saved to .env file")
                                        except Exception as env_error:
                                            logger.warning(f"[LOCAL] Failed to save {provider} API key to .env file: {env_error}")
                                    else:
                                        logger.info(f"[PRODUCTION] API key for {provider} saved to database only (user: {self.user_id})")
                                    
                                    # Log database save confirmation
                                    logger.info(f"✅ DATABASE: API key for {provider} saved to database for user {self.user_id}")
                        elif step.step_number == 2:  # Website Analysis
                            self.db_service.save_website_analysis(self.user_id, step.data, db)
                            logger.info(f"✅ DATABASE: Website analysis saved to database for user {self.user_id}")
                        elif step.step_number == 3:  # Research Preferences
                            self.db_service.save_research_preferences(self.user_id, step.data, db)
                            logger.info(f"✅ DATABASE: Research preferences saved to database for user {self.user_id}")
                        elif step.step_number == 4:  # Persona Generation
                            self.db_service.save_persona_data(self.user_id, step.data, db)
                            logger.info(f"✅ DATABASE: Persona data saved to database for user {self.user_id}")
                
                logger.info(f"Progress saved to database for user {self.user_id}")
            finally:
                db.close()
            
        except Exception as e:
            logger.error(f"Error saving progress to database: {str(e)}")
            raise
    
    def load_progress_from_db(self):
        """Load progress from database."""
        if not self.use_database or not self.db_service or not self.user_id:
            logger.warning("Cannot load progress: database service not available or user_id not set")
            return
            
        try:
            from services.database import SessionLocal
            db = SessionLocal()
            try:
                # Get session data
                session = self.db_service.get_session_by_user(self.user_id, db)
                if not session:
                    logger.info(f"No existing onboarding session found for user {self.user_id}, starting fresh")
                    return
                
                # Restore session data
                self.current_step = session.current_step or 1
                self.started_at = session.started_at.isoformat() if session.started_at else self.started_at
                self.last_updated = session.last_updated.isoformat() if session.last_updated else self.last_updated
                self.is_completed = session.is_completed or False
                self.completed_at = session.completed_at.isoformat() if session.completed_at else None
                
                # Load step-specific data from database
                self._load_step_data_from_db(db)
                
                # Fix any corrupted state
                self._fix_corrupted_state()
                
                logger.info(f"Progress loaded from database for user {self.user_id}")
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error loading progress from database: {str(e)}")
            # Don't fail if database loading fails - start fresh
    
    def _load_step_data_from_db(self, db):
        """Load step-specific data from database tables."""
        try:
            # Load API keys (step 1)
            api_keys = self.db_service.get_api_keys(self.user_id, db)
            if api_keys:
                step1 = self.get_step_data(1)
                if step1:
                    step1.status = StepStatus.COMPLETED
                    step1.data = {'api_keys': api_keys}
                    step1.completed_at = datetime.now().isoformat()
            
            # Load website analysis (step 2)
            website_analysis = self.db_service.get_website_analysis(self.user_id, db)
            if website_analysis:
                step2 = self.get_step_data(2)
                if step2:
                    step2.status = StepStatus.COMPLETED
                    step2.data = website_analysis
                    step2.completed_at = datetime.now().isoformat()
            
            # Load research preferences (step 3)
            research_prefs = self.db_service.get_research_preferences(self.user_id, db)
            if research_prefs:
                step3 = self.get_step_data(3)
                if step3:
                    step3.status = StepStatus.COMPLETED
                    step3.data = research_prefs
                    step3.completed_at = datetime.now().isoformat()
            
            # Load persona data (step 4)
            persona_data = self.db_service.get_persona_data(self.user_id, db)
            if persona_data:
                step4 = self.get_step_data(4)
                if step4:
                    step4.status = StepStatus.COMPLETED
                    step4.data = persona_data
                    step4.completed_at = datetime.now().isoformat()
            
            logger.info("Step data loaded from database")
        except Exception as e:
            logger.error(f"Error loading step data from database: {str(e)}")
    
    def _fix_corrupted_state(self):
        """Fix any corrupted progress state."""
        # Check if all steps are completed
        all_steps_completed = all(s.status in [StepStatus.COMPLETED, StepStatus.SKIPPED] for s in self.steps)
        
        if all_steps_completed:
            self.is_completed = True
            self.completed_at = self.completed_at or datetime.now().isoformat()
            self.current_step = len(self.steps)
        else:
            # Find the first incomplete step
            for i, step in enumerate(self.steps):
                if step.status == StepStatus.PENDING:
                    self.current_step = step.step_number
                    break


class APIKeyManager:
    """Manages API keys for different providers."""
    
    def __init__(self):
        self.api_keys = {}
        self._load_from_env()
    
    def _load_from_env(self):
        """Load API keys from environment variables."""
        providers = [
            'GEMINI_API_KEY',
            'HF_TOKEN',
            'TAVILY_API_KEY',
            'SERPER_API_KEY',
            'METAPHOR_API_KEY',
            'FIRECRAWL_API_KEY',
            'STABILITY_API_KEY'
        ]
        
        for provider in providers:
            key = os.getenv(provider)
            if key:
                # Convert provider name to lowercase for consistency
                provider_name = provider.replace('_API_KEY', '').lower()
                self.api_keys[provider_name] = key
                logger.info(f"Loaded {provider_name} API key from environment")
    
    def get_api_key(self, provider: str) -> Optional[str]:
        """Get API key for a provider."""
        return self.api_keys.get(provider.lower())
    
    def save_api_key(self, provider: str, api_key: str):
        """Save API key to environment and memory."""
        provider_lower = provider.lower()
        self.api_keys[provider_lower] = api_key
        
        # Update environment variable
        env_var = f"{provider.upper()}_API_KEY"
        os.environ[env_var] = api_key
        
        logger.info(f"Saved {provider} API key")
    
    def has_api_key(self, provider: str) -> bool:
        """Check if API key exists for provider."""
        return provider.lower() in self.api_keys and bool(self.api_keys[provider.lower()])
    
    def get_all_keys(self) -> Dict[str, str]:
        """Get all API keys."""
        return self.api_keys.copy()
    
    def remove_api_key(self, provider: str):
        """Remove API key for provider."""
        provider_lower = provider.lower()
        if provider_lower in self.api_keys:
            del self.api_keys[provider_lower]
            
            # Remove from environment
            env_var = f"{provider.upper()}_API_KEY"
            if env_var in os.environ:
                del os.environ[env_var]
            
            logger.info(f"Removed {provider} API key")


# Global instances
_user_onboarding_progress_cache = {}

def get_user_onboarding_progress(user_id: str) -> OnboardingProgress:
    """Get user-specific onboarding progress instance."""
    global _user_onboarding_progress_cache
    safe_user_id = ''.join([c if c.isalnum() or c in ('-', '_') else '_' for c in str(user_id)])
    if safe_user_id in _user_onboarding_progress_cache:
        return _user_onboarding_progress_cache[safe_user_id]
    
    # Pass user_id to enable database persistence
    instance = OnboardingProgress(user_id=user_id)
    _user_onboarding_progress_cache[safe_user_id] = instance
    return instance

def get_onboarding_progress_for_user(user_id: str) -> OnboardingProgress:
    """Get user-specific onboarding progress instance (alias for compatibility)."""
    return get_user_onboarding_progress(user_id)

def get_onboarding_progress():
    """Get the global onboarding progress instance."""
    if not hasattr(get_onboarding_progress, '_instance'):
        get_onboarding_progress._instance = OnboardingProgress()
    return get_onboarding_progress._instance

def get_api_key_manager() -> APIKeyManager:
    """Get the global API key manager instance."""
    if not hasattr(get_api_key_manager, '_instance'):
        get_api_key_manager._instance = APIKeyManager()
    return get_api_key_manager._instance
