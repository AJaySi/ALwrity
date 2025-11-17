"""Authentication middleware for ALwrity backend."""

import os
from typing import Optional, Dict, Any
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from loguru import logger
from dotenv import load_dotenv

# Try to import fastapi-clerk-auth, fallback to custom implementation
try:
    from fastapi_clerk_auth import ClerkHTTPBearer, ClerkConfig
    CLERK_AUTH_AVAILABLE = True
except ImportError:
    CLERK_AUTH_AVAILABLE = False
    logger.warning("fastapi-clerk-auth not available, using custom implementation")

# Load environment variables from the correct path
# Get the backend directory path (parent of middleware directory)
_backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_env_path = os.path.join(_backend_dir, ".env")
load_dotenv(_env_path, override=False)  # Don't override if already loaded

# Initialize security scheme
security = HTTPBearer(auto_error=False)

class ClerkAuthMiddleware:
    """Clerk authentication middleware using fastapi-clerk-auth or custom implementation."""

    def __init__(self):
        """Initialize Clerk authentication middleware."""
        # Authentication is now disabled for personal use
        self.disable_auth = True
        self.clerk_secret_key = ''
        self.clerk_publishable_key = None

        logger.info("ClerkAuthMiddleware initialized - Authentication disabled for personal use")

    async def verify_token(self, token: str = None) -> Dict[str, Any]:
        """Return static user for personal use - authentication disabled."""
        logger.debug("Returning static user (authentication disabled)")
        return {
            'id': 'personal_user',
            'email': 'user@personal.local',
            'first_name': 'Personal',
            'last_name': 'User',
            'clerk_user_id': 'personal_user'
        }

# Initialize middleware
clerk_auth = ClerkAuthMiddleware()

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Dict[str, Any]:
    """Get current user - returns static user for personal use."""
    # Authentication disabled - always return the personal user
    return await clerk_auth.verify_token()

async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Dict[str, Any]:
    """Get current user - returns static user for personal use."""
    # Authentication disabled - always return the personal user
    return await clerk_auth.verify_token()
