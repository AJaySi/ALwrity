"""
Unified Token Service for OAuth Integrations
Centralized token management for all OAuth providers.
"""

from typing import Optional, Dict, Any
import os
from datetime import datetime, timedelta


class UnifiedTokenService:
    """Centralized token management for OAuth integrations."""
    
    def __init__(self):
        self._tokens = {}
    
    def get_token(self, provider: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get token for a specific provider and user."""
        key = f"{provider}:{user_id}"
        return self._tokens.get(key)
    
    def set_token(self, provider: str, user_id: str, token_data: Dict[str, Any]) -> None:
        """Set token for a specific provider and user."""
        key = f"{provider}:{user_id}"
        self._tokens[key] = token_data
    
    def delete_token(self, provider: str, user_id: str) -> bool:
        """Delete token for a specific provider and user."""
        key = f"{provider}:{user_id}"
        if key in self._tokens:
            del self._tokens[key]
            return True
        return False
    
    def is_token_valid(self, provider: str, user_id: str) -> bool:
        """Check if token is valid and not expired."""
        token_data = self.get_token(provider, user_id)
        if not token_data:
            return False
        
        # Check expiration if available
        if 'expires_at' in token_data:
            expires_at = token_data['expires_at']
            if isinstance(expires_at, str):
                expires_at = datetime.fromisoformat(expires_at)
            
            if datetime.utcnow() > expires_at:
                return False
        
        return True
    
    def refresh_token(self, provider: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Refresh token if possible."""
        # This would implement token refresh logic
        # For now, just return the existing token
        return self.get_token(provider, user_id)


# Create a singleton instance
unified_token_service = UnifiedTokenService()
