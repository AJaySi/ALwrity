"""
API Key Management Service
Handles API key operations for onboarding.
"""

import time
from typing import Dict, Any
from fastapi import HTTPException
from loguru import logger

from services.onboarding.api_key_manager import APIKeyManager
from services.validation import check_all_api_keys

class APIKeyManagementService:
    """Service for handling API key management operations."""
    
    def __init__(self):
        # Initialize APIKeyManager with database support
        self.api_key_manager = APIKeyManager()
        # Ensure database service is available
        if not hasattr(self.api_key_manager, 'use_database'):
            self.api_key_manager.use_database = True
            # Legacy service removed - using direct DB access
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
    
    async def get_api_keys_for_onboarding(self, user_id: str | None = None) -> Dict[str, Any]:
        """Get all configured API keys for onboarding (unmasked), user-aware.

        In production, keys are per-user and stored in DB; in local, we use env.
        """
        try:
            # Prefer DB per-user keys when user_id is provided and DB is available
            if user_id and getattr(self.api_key_manager, 'use_database', False):
                try:
                    from services.database import SessionLocal
                    from models.onboarding import APIKey
                    
                    db = SessionLocal()
                    try:
                        # Direct DB query instead of legacy service
                        api_keys_records = db.query(APIKey).filter(
                            APIKey.user_id == user_id,
                            APIKey.is_active == True
                        ).all()
                        
                        api_keys = {k.provider: k.api_key for k in api_keys_records}
                        
                        if api_keys:
                            logger.info(f"Loaded {len(api_keys)} API keys from database for user {user_id}")
                            return {
                                "api_keys": api_keys,
                                "total_providers": len(api_keys),
                                "configured_providers": [k for k, v in api_keys.items() if v]
                            }
                    finally:
                        db.close()
                except Exception as db_err:
                    logger.warning(f"DB lookup for API keys failed, falling back to env: {db_err}")

            # Fallback: load from environment/in-memory
            self.api_key_manager.load_api_keys()
            api_keys = self.api_key_manager.api_keys
            return {
                "api_keys": api_keys,
                "total_providers": len(api_keys),
                "configured_providers": [k for k, v in api_keys.items() if v]
            }
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
