"""
Standard OAuth Provider Implementation
Base class that enforces complete IntegrationProvider protocol implementation
with standardized error handling, security, and token management.
"""

from __future__ import annotations

import os
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from urllib.parse import urlencode
import httpx

from loguru import logger

from .base import IntegrationProvider, AuthUrlPayload, ConnectionResult, RefreshResult, ConnectionStatus
from .unified_token_service import unified_token_service
from ..oauth_redirects import get_redirect_uri


class StandardOAuthProvider(IntegrationProvider):
    """
    Standard OAuth provider implementation with complete protocol compliance.
    
    All OAuth providers should inherit from this class to ensure:
    - Consistent interface implementation
    - Proper error handling and logging
    - Unified token storage
    - Security best practices
    """
    
    # Provider configuration (to be overridden by subclasses)
    key: str = ""
    display_name: str = ""
    
    # OAuth endpoints (to be overridden by subclasses)
    auth_url: str = ""
    token_url: str = ""
    scopes: list[str] = []
    
    # Environment variable names (to be overridden by subclasses)
    client_id_env: str = ""
    client_secret_env: str = ""
    redirect_uri_env: str = ""
    
    def __init__(self):
        """Initialize the standard OAuth provider."""
        self.client_id = os.getenv(self.client_id_env, '')
        self.client_secret = os.getenv(self.client_secret_env, '')
        
        try:
            self.redirect_uri = get_redirect_uri(self.display_name, self.redirect_uri_env)
        except ValueError as exc:
            logger.error(f"{self.display_name} OAuth redirect URI configuration error: {exc}")
            self.redirect_uri = None
        
        # Validate configuration
        if not self.client_id or not self.client_secret:
            logger.error(f"{self.display_name} OAuth client credentials not configured")
    
    async def get_auth_url(self, user_id: str) -> AuthUrlPayload:
        """
        Generate OAuth authorization URL with standardized error handling.
        
        Args:
            user_id: User identifier for state parameter
            
        Returns:
            AuthUrlPayload: Authorization URL and state
        """
        try:
            if not self.redirect_uri:
                return AuthUrlPayload(
                    auth_url="",
                    state=user_id,
                    details={"error": f"{self.display_name} redirect URI not configured"}
                )
            
            # Generate secure state with additional entropy
            state = f"{user_id}:{secrets.token_urlsafe(16)}"
            
            # Build authorization URL parameters
            params = {
                'client_id': self.client_id,
                'redirect_uri': self.redirect_uri,
                'state': state,
                'scope': ' '.join(self.scopes),
                'response_type': 'code'
            }
            
            # Add provider-specific parameters
            params.update(self._get_auth_url_params())
            
            auth_url = f"{self.auth_url}?{urlencode(params)}"
            
            logger.info(f"Generated {self.display_name} OAuth URL for user {user_id}")
            
            return AuthUrlPayload(
                auth_url=auth_url,
                state=state,
                details={
                    "provider": self.key,
                    "display_name": self.display_name,
                    "redirect_uri": self.redirect_uri
                }
            )
            
        except Exception as e:
            logger.error(f"{self.display_name} auth URL generation failed: {e}")
            return AuthUrlPayload(
                auth_url="",
                state=user_id,
                details={"error": f"Failed to generate {self.display_name} authorization URL: {str(e)}"}
            )
    
    async def handle_callback(self, code: str, state: str) -> ConnectionResult:
        """
        Handle OAuth callback with standardized validation and token storage.
        
        Args:
            code: Authorization code from OAuth provider
            state: State parameter from callback
            
        Returns:
            ConnectionResult: Result of connection attempt
        """
        try:
            # Extract user_id from state (format: "user_id:random_token")
            if ':' not in state:
                return ConnectionResult(
                    success=False,
                    user_id=state,
                    provider_id=self.key,
                    error="Invalid state format"
                )
            
            user_id, state_token = state.split(':', 1)
            
            # Validate state (basic validation - can be overridden)
            if not self._validate_state(user_id, state_token):
                return ConnectionResult(
                    success=False,
                    user_id=user_id,
                    provider_id=self.key,
                    error="Invalid or expired state"
                )
            
            # Exchange code for tokens
            tokens = await self._exchange_code_for_tokens(code)
            if not tokens or 'access_token' not in tokens:
                return ConnectionResult(
                    success=False,
                    user_id=user_id,
                    provider_id=self.key,
                    error="Failed to exchange authorization code for tokens"
                )
            
            # Calculate expiration time
            expires_at = None
            if 'expires_in' in tokens:
                expires_at = datetime.utcnow() + timedelta(seconds=tokens['expires_in'])
            
            # Store tokens using unified service
            unified_token_service.store_token(
                provider_id=self.key,
                user_id=user_id,
                access_token=tokens['access_token'],
                refresh_token=tokens.get('refresh_token'),
                expires_at=expires_at,
                scope=' '.join(self.scopes),
                account_info=tokens.get('account_info'),
                metadata=tokens.get('metadata')
            )
            
            logger.info(f"Successfully connected {self.display_name} for user {user_id}")
            
            return ConnectionResult(
                success=True,
                user_id=user_id,
                provider_id=self.key,
                access_token=tokens['access_token'],  # Will be redacted by router
                refresh_token=tokens.get('refresh_token'),  # Will be redacted by router
                expires_at=expires_at,
                scope=' '.join(self.scopes),
                account_info=tokens.get('account_info'),
                metadata=tokens.get('metadata')
            )
            
        except Exception as e:
            logger.error(f"{self.display_name} callback handling failed: {e}")
            return ConnectionResult(
                success=False,
                user_id=state,
                provider_id=self.key,
                error=f"Failed to connect to {self.display_name}: {str(e)}"
            )
    
    async def get_connection_status(self, user_id: str) -> ConnectionStatus:
        """
        Get connection status with standardized token checking.
        
        Args:
            user_id: User identifier
            
        Returns:
            ConnectionStatus: Current connection status
        """
        try:
            # Get token from unified storage
            token = unified_token_service.get_token(self.key, user_id)
            
            if not token:
                return ConnectionStatus(
                    connected=False,
                    details={"error": "No token found"},
                    error="Not connected"
                )
            
            # Check if token is expired
            if token.expires_at and datetime.utcnow() > token.expires_at:
                return ConnectionStatus(
                    connected=False,
                    details={"expired_at": token.expires_at.isoformat()},
                    error="Token expired"
                )
            
            # Get additional account details
            account_info = {}
            if token.account_email:
                account_info['email'] = token.account_email
            if token.account_name:
                account_info['name'] = token.account_name
            if token.account_id:
                account_info['account_id'] = token.account_id
            
            # Parse metadata for additional details
            metadata = {}
            if token.metadata_json:
                try:
                    import json
                    metadata = json.loads(token.metadata_json)
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON in metadata for {self.key} user {user_id}")
            
            return ConnectionStatus(
                connected=token.is_active,
                details={
                    "account_info": account_info,
                    "metadata": metadata,
                    "connected_at": token.created_at.isoformat() if token.created_at else None,
                    "expires_at": token.expires_at.isoformat() if token.expires_at else None
                },
                error=None
            )
            
        except Exception as e:
            logger.error(f"{self.display_name} status check failed: {e}")
            return ConnectionStatus(
                connected=False,
                details={"error": str(e)},
                error=f"Failed to check {self.display_name} status: {str(e)}"
            )
    
    async def refresh_token(self, user_id: str) -> RefreshResult:
        """
        Refresh OAuth token with standardized error handling.
        
        Args:
            user_id: User identifier
            
        Returns:
            RefreshResult: Result of token refresh
        """
        try:
            # Get current token
            current_token = unified_token_service.get_token(self.key, user_id)
            if not current_token:
                return RefreshResult(
                    success=False,
                    user_id=user_id,
                    provider_id=self.key,
                    error="No token found to refresh"
                )
            
            # Check if refresh token is available
            if not current_token.refresh_token:
                return RefreshResult(
                    success=False,
                    user_id=user_id,
                    provider_id=self.key,
                    error="No refresh token available"
                )
            
            # Perform token refresh
            new_tokens = await self._refresh_access_token(current_token.refresh_token)
            if not new_tokens or 'access_token' not in new_tokens:
                return RefreshResult(
                    success=False,
                    user_id=user_id,
                    provider_id=self.key,
                    error="Failed to refresh access token"
                )
            
            # Calculate new expiration time
            expires_at = None
            if 'expires_in' in new_tokens:
                expires_at = datetime.utcnow() + timedelta(seconds=new_tokens['expires_in'])
            
            # Update token in unified storage
            unified_token_service.store_token(
                provider_id=self.key,
                user_id=user_id,
                access_token=new_tokens['access_token'],
                refresh_token=new_tokens.get('refresh_token', current_token.refresh_token),
                expires_at=expires_at,
                scope=new_tokens.get('scope', ' '.join(self.scopes)),
                account_info=new_tokens.get('account_info'),
                metadata=new_tokens.get('metadata')
            )
            
            logger.info(f"Successfully refreshed {self.display_name} token for user {user_id}")
            
            return RefreshResult(
                success=True,
                user_id=user_id,
                provider_id=self.key,
                access_token=new_tokens['access_token'],
                refresh_token=new_tokens.get('refresh_token', current_token.refresh_token),
                expires_at=expires_at,
                error=None
            )
            
        except Exception as e:
            logger.error(f"{self.display_name} token refresh failed: {e}")
            return RefreshResult(
                success=False,
                user_id=user_id,
                provider_id=self.key,
                error=f"Failed to refresh {self.display_name} token: {str(e)}"
            )
    
    async def disconnect(self, user_id: str) -> bool:
        """
        Disconnect OAuth connection with standardized cleanup.
        
        Args:
            user_id: User identifier
            
        Returns:
            bool: True if disconnection was successful
        """
        try:
            # Revoke token on provider side if supported
            await self._revoke_provider_token(user_id)
            
            # Remove token from unified storage
            success = unified_token_service.revoke_token(self.key, user_id)
            
            if success:
                logger.info(f"Successfully disconnected {self.display_name} for user {user_id}")
            else:
                logger.warning(f"No active {self.display_name} token found for user {user_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"{self.display_name} disconnection failed: {e}")
            return False
    
    # Abstract methods for providers to implement
    def _get_auth_url_params(self) -> Dict[str, str]:
        """
        Get provider-specific authorization URL parameters.
        
        Returns:
            Dict[str, str]: Additional parameters for auth URL
        """
        return {}
    
    async def _exchange_code_for_tokens(self, code: str) -> Optional[Dict[str, Any]]:
        """
        Exchange authorization code for access tokens.
        
        Args:
            code: Authorization code from OAuth provider
            
        Returns:
            Optional[Dict[str, Any]]: Token response or None if failed
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement _exchange_code_for_tokens")
    
    async def _refresh_access_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """
        Refresh access token using refresh token.
        
        Args:
            refresh_token: Refresh token
            
        Returns:
            Optional[Dict[str, Any]]: New token response or None if failed
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement _refresh_access_token")
    
    async def _revoke_provider_token(self, user_id: str) -> None:
        """
        Revoke token on provider side (optional).
        
        Args:
            user_id: User identifier
        """
        # Default implementation - no provider-side revocation
        # Providers can override this to call provider-specific revocation endpoints
        pass
    
    def _validate_state(self, user_id: str, state_token: str) -> bool:
        """
        Validate OAuth state parameter.
        
        Args:
            user_id: User identifier from state
            state_token: Random token from state
            
        Returns:
            bool: True if state is valid
        """
        # Default implementation - just check that user_id is not empty
        # Providers can override for more sophisticated validation
        return bool(user_id and state_token)
