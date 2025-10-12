"""
API Key Management Service
Handles API key operations for onboarding.
"""

import time
from typing import Dict, Any
from fastapi import HTTPException
from loguru import logger

from services.api_key_manager import APIKeyManager
from services.validation import check_all_api_keys

class APIKeyManagementService:
    """Service for handling API key management operations."""
    
    def __init__(self):
        # Initialize APIKeyManager with database support
        self.api_key_manager = APIKeyManager()
        # Ensure database service is available
        if not hasattr(self.api_key_manager, 'use_database'):
            self.api_key_manager.use_database = True
            try:
                from services.onboarding_database_service import OnboardingDatabaseService
                self.api_key_manager.db_service = OnboardingDatabaseService()
                logger.info("Database service initialized for APIKeyManager")
            except Exception as e:
                logger.warning(f"Database service not available: {e}")
                self.api_key_manager.use_database = False
                self.api_key_manager.db_service = None
        
        # Simple cache for API keys
        self._api_keys_cache = None
        self._cache_timestamp = 0
        self.CACHE_DURATION = 30  # Cache for 30 seconds
    
    async def get_api_keys(self) -> Dict[str, Any]:
        """Get all configured API keys (masked)."""
        current_time = time.time()
        
        # Return cached result if still valid
        if self._api_keys_cache and (current_time - self._cache_timestamp) < self.CACHE_DURATION:
            logger.debug("Returning cached API keys")
            return self._api_keys_cache
        
        try:
            self.api_key_manager.load_api_keys()  # Load keys from environment
            api_keys = self.api_key_manager.api_keys  # Get the loaded keys
            
            # Mask the API keys for security
            masked_keys = {}
            for provider, key in api_keys.items():
                if key:
                    masked_keys[provider] = "*" * (len(key) - 4) + key[-4:] if len(key) > 4 else "*" * len(key)
                else:
                    masked_keys[provider] = None
            
            result = {
                "api_keys": masked_keys,
                "total_providers": len(api_keys),
                "configured_providers": [k for k, v in api_keys.items() if v]
            }
            
            # Cache the result
            self._api_keys_cache = result
            self._cache_timestamp = current_time
            
            return result
        except Exception as e:
            logger.error(f"Error getting API keys: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def get_api_keys_for_onboarding(self) -> Dict[str, Any]:
        """Get all configured API keys for onboarding (unmasked)."""
        try:
            self.api_key_manager.load_api_keys()  # Load keys from environment
            api_keys = self.api_key_manager.api_keys  # Get the loaded keys
            
            # Return actual API keys for onboarding pre-filling
            result = {
                "api_keys": api_keys,
                "total_providers": len(api_keys),
                "configured_providers": [k for k, v in api_keys.items() if v]
            }
            
            return result
        except Exception as e:
            logger.error(f"Error getting API keys for onboarding: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def save_api_key(self, provider: str, api_key: str, description: str = None, current_user: dict = None) -> Dict[str, Any]:
        """Save an API key for a provider."""
        try:
            logger.info(f"📝 save_api_key called for provider: {provider}")
            
            # Set user_id on the API key manager if available
            if current_user and current_user.get('id'):
                self.api_key_manager.user_id = current_user['id']
                logger.info(f"Set user_id on APIKeyManager: {current_user['id']}")
            
            success = self.api_key_manager.save_api_key(provider, api_key)
            
            if success:
                return {
                    "message": f"API key for {provider} saved successfully",
                    "provider": provider,
                    "status": "saved"
                }
            else:
                raise HTTPException(status_code=400, detail=f"Failed to save API key for {provider}")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error saving API key: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def validate_api_keys(self) -> Dict[str, Any]:
        """Validate all configured API keys."""
        try:
            validation_results = check_all_api_keys(self.api_key_manager)
            
            return {
                "validation_results": validation_results.get('results', {}),
                "all_valid": validation_results.get('all_valid', False),
                "total_providers": len(validation_results.get('results', {}))
            }
        except Exception as e:
            logger.error(f"Error validating API keys: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")
