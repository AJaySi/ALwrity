"""Authentication middleware for ALwrity backend."""

import os
import jwt
import requests
from typing import Optional, Dict, Any
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from loguru import logger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize security scheme
security = HTTPBearer(auto_error=False)

class ClerkAuthMiddleware:
    """Clerk authentication middleware."""
    
    def __init__(self):
        """Initialize Clerk authentication middleware."""
        self.clerk_secret_key = os.getenv('CLERK_SECRET_KEY')
        self.disable_auth = os.getenv('DISABLE_AUTH', 'false').lower() == 'true'
        
        if not self.clerk_secret_key and not self.disable_auth:
            logger.warning("CLERK_SECRET_KEY not found, authentication may fail")
        
        logger.info(f"ClerkAuthMiddleware initialized - Auth disabled: {self.disable_auth}")
    
    async def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify Clerk JWT token."""
        try:
            if self.disable_auth:
                logger.info("Authentication disabled, returning mock user")
                return {
                    'id': 'mock_user_id',
                    'email': 'mock@example.com',
                    'first_name': 'Mock',
                    'last_name': 'User'
                }
            
            if not self.clerk_secret_key:
                logger.error("CLERK_SECRET_KEY not configured")
                return None
            
            # Temporary simplified token validation for development
            # This accepts any token that looks like a Clerk token
            if token and len(token) > 50 and token.startswith('eyJ'):
                logger.info("Token validation passed (simplified mode)")
                return {
                    'id': 'dev_user_id',
                    'email': 'dev@example.com',
                    'first_name': 'Dev',
                    'last_name': 'User'
                }
            
            logger.warning("Invalid token format")
            return None
            
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            return None

# Initialize middleware
clerk_auth = ClerkAuthMiddleware()

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Dict[str, Any]:
    """Get current authenticated user."""
    try:
        if not credentials:
            logger.warning("No credentials provided")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        token = credentials.credentials
        logger.info(f"Verifying token: {token[:20]}...")
        
        user = await clerk_auth.verify_token(token)
        if not user:
            logger.warning("Token verification failed")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.info(f"User authenticated: {user.get('email', 'unknown')}")
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[Dict[str, Any]]:
    """Get current user if authenticated, otherwise return None."""
    try:
        if not credentials:
            return None
        
        token = credentials.credentials
        user = await clerk_auth.verify_token(token)
        return user
        
    except Exception as e:
        logger.warning(f"Optional authentication failed: {e}")
        return None
