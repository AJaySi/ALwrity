"""Enhanced API Key Manager service for ALwrity backend."""

# This file contains the core business logic moved from lib/utils/api_key_manager/
# It includes the OnboardingProgress class and related functionality

import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum
from loguru import logger
from dotenv import load_dotenv

class StepStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"

@dataclass
class StepData:
    step_number: int
    title: str
    description: str
    status: StepStatus
    completed_at: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    validation_errors: List[str] = None

    def __post_init__(self):
        if self.validation_errors is None:
            self.validation_errors = []

class OnboardingProgress:
    """Manages onboarding progress with persistence and validation."""
    
    def __init__(self, progress_file: Optional[str] = None, user_id: Optional[str] = None):
        self.steps = self._initialize_steps()
        self.current_step = 1
        self.started_at = datetime.now().isoformat()
        self.last_updated = datetime.now().isoformat()
        self.is_completed = False
        self.completed_at = None
        self.user_id = user_id  # Add user_id for database isolation
        
        # Use user-specific file for backward compatibility
        if user_id:
            self.progress_file = progress_file or f".onboarding_progress_{user_id}.json"
        else:
            self.progress_file = progress_file or ".onboarding_progress.json"
        
        # Initialize database service for dual persistence
        try:
            from services.onboarding_database_service import OnboardingDatabaseService
            self.db_service = OnboardingDatabaseService()
            self.use_database = True
            logger.info(f"Database service initialized for user {user_id}")
        except Exception as e:
            logger.warning(f"Database service not available, using file only: {e}")
            self.db_service = None
            self.use_database = False
        
        # Load existing progress if available
        self.load_progress()
    
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
    
    def mark_step_skipped(self, step_number: int):
        """Mark a step as skipped."""
        step = self.get_step_data(step_number)
        if step:
            step.status = StepStatus.SKIPPED
            step.completed_at = datetime.now().isoformat()
            self.last_updated = datetime.now().isoformat()
            
            # Check if all steps are now completed
            all_completed = all(s.status in [StepStatus.COMPLETED, StepStatus.SKIPPED] for s in self.steps)
            
            if all_completed:
                # If all steps are completed, mark onboarding as complete
                self.is_completed = True
                self.completed_at = datetime.now().isoformat()
                self.current_step = len(self.steps)  # Set to last step number
                logger.info(f"[mark_step_skipped] All steps completed, marking onboarding as complete")
            else:
                # Only increment current_step if there are more steps to go
                self.current_step = step_number + 1
                # Ensure current_step doesn't exceed total steps
                if self.current_step > len(self.steps):
                    self.current_step = len(self.steps)
            
            logger.info(f"[mark_step_skipped] Step {step_number} skipped, new current_step: {self.current_step}, is_completed: {self.is_completed}")
            self.save_progress()
            logger.info(f"Step {step_number} marked as skipped")
    
    def can_proceed_to_step(self, step_number: int) -> bool:
        """Check if user can proceed to a specific step."""
        if step_number == 1:
            return True  # First step is always accessible
        
        # Check if all previous steps are completed
        for step in self.steps:
            if step.step_number < step_number:
                if step.status not in [StepStatus.COMPLETED, StepStatus.SKIPPED]:
                    return False
        
        return True
    
    def can_complete_onboarding(self) -> bool:
        """Check if onboarding can be completed."""
        required_steps = [1, 2, 3, 6]  # Steps 1, 2, 3, and 6 are required
        for step_num in required_steps:
            step = self.get_step_data(step_num)
            if step and step.status in [StepStatus.COMPLETED, StepStatus.SKIPPED]:
                continue

            # DB-aware fallback for steps 2 and 3
            try:
                from services.onboarding_database_service import OnboardingDatabaseService
                from services.database import get_db
                db = next(get_db())
                db_service = OnboardingDatabaseService(db)
                if step_num == 2:
                    w = db_service.get_website_analysis(self.user_id, db)
                    if w and (w.get('website_url') or w.get('writing_style')):
                        # Mark as completed to normalize state
                        try:
                            self.mark_step_completed(2, {'source': 'db-fallback'})
                        except Exception:
                            pass
                        continue
                if step_num == 3:
                    p = db_service.get_research_preferences(self.user_id, db)
                    if p and p.get('research_depth'):
                        try:
                            self.mark_step_completed(3, {'source': 'db-fallback'})
                        except Exception:
                            pass
                        continue
            except Exception:
                pass

            return False
        return True
    
    def get_completion_percentage(self) -> float:
        """Get the completion percentage."""
        completed_steps = sum(1 for step in self.steps if step.status in [StepStatus.COMPLETED, StepStatus.SKIPPED])
        return (completed_steps / len(self.steps)) * 100
    
    def get_next_incomplete_step(self) -> Optional[int]:
        """Get the next incomplete step number."""
        for step in self.steps:
            if step.status not in [StepStatus.COMPLETED, StepStatus.SKIPPED]:
                return step.step_number
        return None
    
    def get_resume_step(self) -> int:
        """Get the step to resume from."""
        logger.info(f"[get_resume_step] Checking resume step...")
        logger.info(f"[get_resume_step] Current step: {self.current_step}")
        logger.info(f"[get_resume_step] Steps status: {[f'{s.step_number}:{s.status.value}' for s in self.steps]}")
        
        for step in self.steps:
            if step.status not in [StepStatus.COMPLETED, StepStatus.SKIPPED]:
                logger.info(f"[get_resume_step] Found incomplete step: {step.step_number}")
                return step.step_number
        
        logger.warning(f"[get_resume_step] No incomplete steps found, defaulting to step 1")
        return 1  # Default to first step
    
    def complete_onboarding(self):
        """Complete the onboarding process."""
        self.is_completed = True
        self.completed_at = datetime.now().isoformat()
        self.last_updated = datetime.now().isoformat()
        self.save_progress()
        logger.info("Onboarding completed successfully")
    
    def save_progress(self):
        """Save progress to both file and database (dual persistence)."""
        try:
            # Save to JSON file (backward compatibility)
            progress_data = {
                "steps": [{
                    "step_number": step.step_number,
                    "title": step.title,
                    "description": step.description,
                    "status": step.status.value,  # Convert enum to string
                    "completed_at": step.completed_at,
                    "data": step.data,
                    "validation_errors": step.validation_errors
                } for step in self.steps],
                "current_step": self.current_step,
                "started_at": self.started_at,
                "last_updated": self.last_updated,
                "is_completed": self.is_completed,
                "completed_at": self.completed_at
            }
            
            with open(self.progress_file, 'w') as f:
                json.dump(progress_data, f, indent=2)
            
            logger.debug(f"Progress saved to {self.progress_file}")
            
            # Also save to database if available and user_id is set
            if self.use_database and self.db_service and self.user_id:
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
                        
                        logger.info(f"Progress also saved to database for user {self.user_id}")
                    finally:
                        db.close()
                except Exception as db_error:
                    logger.warning(f"Failed to save to database, JSON file still saved: {db_error}")
                    # Don't fail if database save fails - JSON is still working
            
        except Exception as e:
            logger.error(f"Error saving progress: {str(e)}")
    
    def load_progress(self):
        """Load progress from file."""
        try:
            if os.path.exists(self.progress_file):
                with open(self.progress_file, 'r') as f:
                    progress_data = json.load(f)
                
                # Restore step data
                for step_data in progress_data.get("steps", []):
                    step_num = step_data.get("step_number")
                    if step_num:
                        step = self.get_step_data(step_num)
                        if step:
                            step.status = StepStatus(step_data.get("status", "pending"))
                            step.completed_at = step_data.get("completed_at")
                            step.data = step_data.get("data")
                            step.validation_errors = step_data.get("validation_errors", [])
                
                # Restore other data
                self.current_step = progress_data.get("current_step", 1)
                self.started_at = progress_data.get("started_at", self.started_at)
                self.last_updated = progress_data.get("last_updated", self.last_updated)
                self.is_completed = progress_data.get("is_completed", False)
                self.completed_at = progress_data.get("completed_at")
                
                # Fix any corrupted state
                self._fix_corrupted_state()
                
                logger.info("Progress loaded from file")
        except Exception as e:
            logger.error(f"Error loading progress: {str(e)}")
    
    def _fix_corrupted_state(self):
        """Fix any corrupted progress state."""
        # Check if all steps are completed
        all_steps_completed = all(s.status in [StepStatus.COMPLETED, StepStatus.SKIPPED] for s in self.steps)
        
        if all_steps_completed:
            # If all steps are completed, ensure is_completed is True and current_step is valid
            if not self.is_completed:
                logger.info(f"[_fix_corrupted_state] All steps completed but is_completed was False, fixing...")
                self.is_completed = True
                self.completed_at = datetime.now().isoformat()
            
            # Ensure current_step doesn't exceed total steps
            if self.current_step > len(self.steps):
                logger.info(f"[_fix_corrupted_state] Current step {self.current_step} exceeds total steps {len(self.steps)}, fixing...")
                self.current_step = len(self.steps)
                self.save_progress()
        else:
            # If not all steps are completed, ensure is_completed is False
            if self.is_completed:
                logger.info(f"[_fix_corrupted_state] Not all steps completed but is_completed was True, fixing...")
                self.is_completed = False
                self.completed_at = None
                self.save_progress()
    
    def reset_progress(self):
        """Reset all progress."""
        self.steps = self._initialize_steps()
        self.current_step = 1
        self.started_at = datetime.now().isoformat()
        self.last_updated = datetime.now().isoformat()
        self.is_completed = False
        self.completed_at = None
        self.save_progress()
        logger.info("Progress reset successfully")

class APIKeyManager:
    """Enhanced manager for handling API keys with setup instructions."""
    
    def __init__(self):
        self.api_keys = {
            "openai": None,
            "gemini": None,
            "anthropic": None,
            "mistral": None,
            "tavily": None,
            "serper": None,
            "metaphor": None,  # legacy mapping for Exa, kept for backward compatibility
            "exa": None,
            "firecrawl": None,
            "stability": None,
            "copilotkit": None,
        }
        self.load_api_keys()
        
        # Enhanced provider setup instructions
        self.api_key_groups = {
            "Create": {
                "GEMINI_API_KEY": {
                    "url": "https://makersuite.google.com/app/apikey",
                    "description": "Google's Gemini AI for content generation",
                    "setup_steps": [
                        "Visit Google AI Studio",
                        "Create a Google Cloud account",
                        "Enable Gemini API",
                        "Generate API key"
                    ]
                },
                "OPENAI_API_KEY": {
                    "url": "https://platform.openai.com/api-keys",
                    "description": "OpenAI's GPT models for content creation",
                    "setup_steps": [
                        "Go to OpenAI platform",
                        "Create an account",
                        "Navigate to API keys",
                        "Create new API key"
                    ]
                },
                "MISTRAL_API_KEY": {
                    "url": "https://console.mistral.ai/api-keys/",
                    "description": "Mistral AI for efficient content generation",
                    "setup_steps": [
                        "Visit Mistral AI website",
                        "Sign up for an account",
                        "Access API section",
                        "Generate API key"
                    ]
                },
                "ANTHROPIC_API_KEY": {
                    "url": "https://console.anthropic.com/",
                    "description": "Anthropic's Claude models for content creation",
                    "setup_steps": [
                        "Visit Anthropic console",
                        "Create an account",
                        "Navigate to API keys",
                        "Generate API key"
                    ]
                }
            },
            "Research": {
                "TAVILY_API_KEY": {
                    "url": "https://tavily.com/#api",
                    "description": "Powers intelligent web research features",
                    "setup_steps": [
                        "Go to Tavily's website",
                        "Create an account",
                        "Access your API dashboard",
                        "Generate a new API key"
                    ]
                },
                "SERPER_API_KEY": {
                    "url": "https://serper.dev/signup",
                    "description": "Enables Google search functionality",
                    "setup_steps": [
                        "Visit Serper.dev",
                        "Sign up for an account",
                        "Go to API section",
                        "Create your API key"
                    ]
                }
            },
            "Deep Search": {
                "EXA_API_KEY": {
                    "url": "https://dashboard.exa.ai/login",
                    "description": "Exa (formerly Metaphor) for advanced web search",
                    "setup_steps": [
                        "Visit the Exa AI dashboard",
                        "Sign up for a free account",
                        "Navigate to API Keys section",
                        "Create a new API key"
                    ]
                },
                "FIRECRAWL_API_KEY": {
                    "url": "https://www.firecrawl.dev/account",
                    "description": "Enables web content extraction",
                    "setup_steps": [
                        "Visit Firecrawl website",
                        "Sign up for an account",
                        "Access API dashboard",
                        "Create your API key"
                    ]
                }
            },
            "Integrations": {
                "STABILITY_API_KEY": {
                    "url": "https://platform.stability.ai/",
                    "description": "Enables AI image generation",
                    "setup_steps": [
                        "Access Stability AI platform",
                        "Create an account",
                        "Navigate to API settings",
                        "Generate your API key"
                    ]
                }
            },
            "UI": {
                "COPILOTKIT_API_KEY": {
                    "url": "https://copilotkit.ai",
                    "description": "CopilotKit public API key for in-app assistant",
                    "setup_steps": [
                        "Sign up or log in to CopilotKit",
                        "Navigate to API Keys",
                        "Generate a public API key (ck_pub_...)"
                    ]
                }
            }
        }
    
    def save_api_key(self, provider: str, api_key: str) -> bool:
        """Save an API key for a provider."""
        try:
            if provider in self.api_keys:
                self.api_keys[provider] = api_key
                
                # Save to database if available and user_id is set
                if hasattr(self, 'use_database') and self.use_database and hasattr(self, 'db_service') and self.db_service and hasattr(self, 'user_id') and self.user_id:
                    try:
                        from services.database import SessionLocal
                        db = SessionLocal()
                        try:
                            self.db_service.save_api_key(self.user_id, provider, api_key, db)
                            logger.info(f"✅ DATABASE: API key for {provider} saved to database for user {self.user_id}")
                        finally:
                            db.close()
                    except Exception as db_error:
                        logger.warning(f"Failed to save {provider} API key to database: {db_error}")
                
                # Also save to .env file in local mode
                is_local = os.getenv('DEPLOY_ENV', 'local') == 'local'
                if is_local:
                    # Special handling for CopilotKit - save to frontend/.env
                    if provider == 'copilotkit':
                        self._save_to_frontend_env(api_key)
                        logger.info(f"[LOCAL] CopilotKit API key saved to frontend/.env file")
                    else:
                        # Save other keys to backend/.env
                        self._save_to_env_file(provider, api_key)
                        logger.info(f"[LOCAL] API key for {provider} saved to backend/.env file")
                else:
                    logger.info(f"[PRODUCTION] API key for {provider} saved to memory only (database handles persistence)")
                
                return True
            else:
                logger.error(f"Unknown provider: {provider}")
                return False
        except Exception as e:
            logger.error(f"Error saving API key: {str(e)}")
            return False
    
    def get_api_key(self, provider: str) -> Optional[str]:
        """Get API key for a provider."""
        return self.api_keys.get(provider)
    
    def get_all_keys(self) -> Dict[str, str]:
        """Get all configured API keys."""
        return {k: v for k, v in self.api_keys.items() if v is not None}
    
    def check_ollama_availability(self) -> bool:
        """Check if Ollama is available locally.
        
        This method attempts to connect to the local Ollama service and
        verify that it's responding to API requests. If available, it
        sets the Ollama endpoint as a pseudo-key for provider detection.
        
        Returns:
            bool: True if Ollama service is available and responding,
                 False otherwise.
                 
        Side Effects:
            If Ollama is available, sets self.api_keys["ollama"] to the
            endpoint URL for provider detection purposes.
            
        Example:
            >>> api_manager = APIKeyManager()
            >>> if api_manager.check_ollama_availability():
            ...     print("Ollama is ready for local AI generation")
            ... else:
            ...     print("Ollama not available, using cloud providers")
            
        Note:
            This method uses a 5-second timeout to avoid blocking the
            application startup if Ollama is not running.
        """
        try:
            import requests
            endpoint = os.getenv("OLLAMA_ENDPOINT", "http://localhost:11434")
            response = requests.get(f"{endpoint}/api/tags", timeout=5)
            if response.status_code == 200:
                # If Ollama is available, set a pseudo-key for provider detection
                self.api_keys["ollama"] = endpoint
                return True
            return False
        except Exception:
            return False
    
    def load_api_keys(self):
        """Load API keys from environment variables."""
        # Reload environment variables first - use backend directory path
        import os
        backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        env_path = os.path.join(backend_dir, ".env")
        load_dotenv(env_path, override=True)
        
        env_mapping = {
            "OPENAI_API_KEY": "openai",
            "GEMINI_API_KEY": "gemini",
            "ANTHROPIC_API_KEY": "anthropic",
            "MISTRAL_API_KEY": "mistral",
            "TAVILY_API_KEY": "tavily",
            "SERPER_API_KEY": "serper",
            "METAPHOR_API_KEY": "metaphor",  # legacy
            "EXA_API_KEY": "exa",
            "FIRECRAWL_API_KEY": "firecrawl",
            "STABILITY_API_KEY": "stability",
            "COPILOTKIT_API_KEY": "copilotkit",
            "OLLAMA_ENDPOINT": "ollama",
            "DEEPSEEK_API_KEY": "deepseek",
        }
        
        for env_var, provider in env_mapping.items():
            api_key = os.getenv(env_var)
            if api_key:
                self.api_keys[provider] = api_key
        
        # Special handling for Ollama - check availability instead of API key
        self.check_ollama_availability()
    
    def get_provider_setup_info(self, provider: str) -> Optional[Dict[str, Any]]:
        """Get setup information for a specific provider."""
        for group_name, providers in self.api_key_groups.items():
            for env_var, info in providers.items():
                if env_var.lower().replace('_api_key', '').replace('_key', '') == provider:
                    return {
                        "provider": provider,
                        "group": group_name,
                        "url": info["url"],
                        "description": info["description"],
                        "setup_steps": info["setup_steps"]
                    }
        return None
    
    def get_all_providers_info(self) -> Dict[str, Any]:
        """Get information for all providers."""
        return {
            "groups": self.api_key_groups,
            "configured_providers": [k for k, v in self.api_keys.items() if v],
            "total_providers": len(self.api_keys)
        }
    
    def _save_to_frontend_env(self, api_key: str):
        """Save CopilotKit API key to frontend/.env file."""
        try:
            # Get the frontend directory path
            backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            frontend_dir = os.path.join(os.path.dirname(backend_dir), "frontend")
            env_path = os.path.join(frontend_dir, ".env")
            
            # Read existing .env file
            if os.path.exists(env_path):
                with open(env_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
            else:
                lines = []
            
            # Update or add REACT_APP_COPILOTKIT_API_KEY
            key_found = False
            updated_lines = []
            env_var = "REACT_APP_COPILOTKIT_API_KEY"
            
            for line in lines:
                if line.startswith(f"{env_var}="):
                    updated_lines.append(f"{env_var}={api_key}\n")
                    key_found = True
                else:
                    updated_lines.append(line)
            
            if not key_found:
                # Ensure the file ends with a newline before adding new key
                if updated_lines and not updated_lines[-1].endswith('\n'):
                    updated_lines[-1] += '\n'
                updated_lines.append(f"{env_var}={api_key}\n")
            
            # Write back to frontend .env file
            with open(env_path, 'w', encoding='utf-8') as f:
                f.writelines(updated_lines)
            
            logger.debug(f"CopilotKit API key saved to frontend .env file")
            
        except Exception as e:
            logger.error(f"Error saving to frontend .env file: {str(e)}")
    
    def _save_to_env_file(self, provider: str, api_key: str):
        """Save API key to backend .env file."""
        try:
            env_mapping = {
                "openai": "OPENAI_API_KEY",
                "gemini": "GEMINI_API_KEY",
                "anthropic": "ANTHROPIC_API_KEY",
                "mistral": "MISTRAL_API_KEY",
                "tavily": "TAVILY_API_KEY",
                "serper": "SERPER_API_KEY",
                "metaphor": "METAPHOR_API_KEY",  # legacy
                "exa": "EXA_API_KEY",
                "firecrawl": "FIRECRAWL_API_KEY",
                "stability": "STABILITY_API_KEY",
                "copilotkit": "COPILOTKIT_API_KEY",
                "ollama": "OLLAMA_ENDPOINT",
                "deepseek": "DEEPSEEK_API_KEY",
            }
            
            env_var = env_mapping.get(provider)
            if env_var:
                # Update environment variable
                os.environ[env_var] = api_key
                
                # Update .env file - use backend directory path
                backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                env_path = os.path.join(backend_dir, ".env")
                if os.path.exists(env_path):
                    with open(env_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                else:
                    lines = []
                
                key_found = False
                updated_lines = []
                for line in lines:
                    if line.startswith(f"{env_var}="):
                        updated_lines.append(f"{env_var}={api_key}\n")
                        key_found = True
                    else:
                        updated_lines.append(line)
                
                if not key_found:
                    # Ensure the file ends with a newline before adding new key
                    if updated_lines and not updated_lines[-1].endswith('\n'):
                        updated_lines[-1] += '\n'
                    updated_lines.append(f"{env_var}={api_key}\n")
                
                with open(env_path, 'w', encoding='utf-8') as f:
                    f.writelines(updated_lines)
                
                # Reload environment variables into current process
                load_dotenv(env_path, override=True)
                
                # Verify the key is now in environment
                loaded_key = os.environ.get(env_var)
                if loaded_key == api_key:
                    logger.info(f"✅ {env_var} loaded into environment (available for immediate use)")
                else:
                    logger.warning(f"⚠️ {env_var} written to .env but not in environment yet")
                
                logger.debug(f"API key saved to .env file for {provider}")
        except Exception as e:
            logger.error(f"Error saving to .env file: {str(e)}")

# Global instance for the application
_onboarding_progress = None
_user_onboarding_progress_cache: Dict[str, OnboardingProgress] = {}

def get_onboarding_progress() -> OnboardingProgress:
    """Get the global onboarding progress instance."""
    if not hasattr(get_onboarding_progress, '_instance'):
        get_onboarding_progress._instance = OnboardingProgress()
    return get_onboarding_progress._instance

def get_onboarding_progress_for_user(user_id: str) -> OnboardingProgress:
    """Get or create a per-user onboarding progress instance with database persistence."""
    global _user_onboarding_progress_cache
    safe_user_id = ''.join([c if c.isalnum() or c in ('-', '_') else '_' for c in str(user_id)])
    if safe_user_id in _user_onboarding_progress_cache:
        return _user_onboarding_progress_cache[safe_user_id]
    
    # Create user-specific progress file for backward compatibility
    progress_file = f".onboarding_progress_{safe_user_id}.json"
    
    # Pass user_id to enable database persistence
    instance = OnboardingProgress(progress_file=progress_file, user_id=user_id)
    _user_onboarding_progress_cache[safe_user_id] = instance
    return instance

def get_api_key_manager() -> APIKeyManager:
    """Get the global API key manager instance."""
    if not hasattr(get_api_key_manager, '_instance'):
        get_api_key_manager._instance = APIKeyManager()
    return get_api_key_manager._instance 