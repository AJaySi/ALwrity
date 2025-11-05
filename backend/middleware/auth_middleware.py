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
        self.clerk_secret_key = os.getenv('CLERK_SECRET_KEY', '').strip()
        # Check for both backend and frontend naming conventions
        publishable_key = (
            os.getenv('CLERK_PUBLISHABLE_KEY') or 
            os.getenv('REACT_APP_CLERK_PUBLISHABLE_KEY', '')
        )
        self.clerk_publishable_key = publishable_key.strip() if publishable_key else None
        self.disable_auth = os.getenv('DISABLE_AUTH', 'false').lower() == 'true'
        
        # Cache for PyJWKClient to avoid repeated JWKS fetches
        self._jwks_client_cache = {}
        self._jwks_url_cache = None

        if not self.clerk_secret_key and not self.disable_auth:
            logger.warning("CLERK_SECRET_KEY not found, authentication may fail")

        # Initialize fastapi-clerk-auth if available
        if CLERK_AUTH_AVAILABLE and not self.disable_auth:
            try:
                if self.clerk_secret_key and self.clerk_publishable_key:
                    # Extract instance from publishable key for JWKS URL
                    # Format: pk_test_<instance>.<domain> or pk_live_<instance>.<domain>
                    parts = self.clerk_publishable_key.replace('pk_test_', '').replace('pk_live_', '').split('.')
                    if len(parts) >= 1:
                        # Extract the domain from publishable key or use default
                        # Clerk URLs are typically: https://<instance>.clerk.accounts.dev
                        instance = parts[0]
                        jwks_url = f"https://{instance}.clerk.accounts.dev/.well-known/jwks.json"
                        
                        # Create Clerk configuration with JWKS URL
                        clerk_config = ClerkConfig(
                            secret_key=self.clerk_secret_key,
                            jwks_url=jwks_url
                        )
                        # Create ClerkHTTPBearer instance for dependency injection
                        self.clerk_bearer = ClerkHTTPBearer(clerk_config)
                        logger.info(f"fastapi-clerk-auth initialized successfully with JWKS URL: {jwks_url}")
                    else:
                        logger.warning("Could not extract instance from publishable key")
                        self.clerk_bearer = None
                else:
                    logger.warning("CLERK_SECRET_KEY or CLERK_PUBLISHABLE_KEY not found")
                    self.clerk_bearer = None
            except Exception as e:
                logger.error(f"Failed to initialize fastapi-clerk-auth: {e}")
                self.clerk_bearer = None
        else:
            self.clerk_bearer = None

        logger.info(f"ClerkAuthMiddleware initialized - Auth disabled: {self.disable_auth}, fastapi-clerk-auth: {CLERK_AUTH_AVAILABLE}")

    async def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify Clerk JWT using fastapi-clerk-auth or custom implementation."""
        try:
            if self.disable_auth:
                logger.info("Authentication disabled, returning mock user")
                return {
                    'id': 'mock_user_id',
                    'email': 'mock@example.com',
                    'first_name': 'Mock',
                    'last_name': 'User',
                    'clerk_user_id': 'mock_clerk_user_id'
                }

            if not self.clerk_secret_key:
                logger.error("CLERK_SECRET_KEY not configured")
                return None

            # Use fastapi-clerk-auth if available
            if self.clerk_bearer:
                try:
                    # Decode and verify the JWT token
                    import jwt
                    from jwt import PyJWKClient
                    
                    # Get the JWKS URL from the token header
                    unverified_header = jwt.get_unverified_header(token)
                    
                    # Decode token to get issuer for JWKS URL
                    unverified_claims = jwt.decode(token, options={"verify_signature": False})
                    issuer = unverified_claims.get('iss', '')
                    
                    # Construct JWKS URL from issuer
                    jwks_url = f"{issuer}/.well-known/jwks.json"
                    
                    # Use cached PyJWKClient to avoid repeated JWKS fetches
                    if jwks_url not in self._jwks_client_cache:
                        logger.info(f"Creating new PyJWKClient for {jwks_url} with caching enabled")
                        # Create client with caching enabled (cache_keys=True keeps keys in memory)
                        self._jwks_client_cache[jwks_url] = PyJWKClient(
                            jwks_url,
                            cache_keys=True,
                            max_cached_keys=16
                        )
                    
                    jwks_client = self._jwks_client_cache[jwks_url]
                    signing_key = jwks_client.get_signing_key_from_jwt(token)
                    
                    # Verify and decode the token with clock skew tolerance
                    # Add 300 seconds (5 minutes) leeway to handle clock skew and token refresh delays
                    decoded_token = jwt.decode(
                        token,
                        signing_key.key,
                        algorithms=["RS256"],
                        options={"verify_signature": True, "verify_exp": True},
                        leeway=300  # Allow 5 minutes leeway for token refresh during navigation
                    )
                    
                    # Extract user information
                    user_id = decoded_token.get('sub')
                    email = decoded_token.get('email')
                    first_name = decoded_token.get('first_name') or decoded_token.get('given_name')
                    last_name = decoded_token.get('last_name') or decoded_token.get('family_name')
                    
                    if user_id:
                        logger.info(f"Token verified successfully using fastapi-clerk-auth for user: {email} (ID: {user_id})")
                        return {
                            'id': user_id,
                            'email': email,
                            'first_name': first_name,
                            'last_name': last_name,
                            'clerk_user_id': user_id
                        }
                    else:
                        logger.warning("No user ID found in verified token")
                        return None
                except Exception as e:
                    # Expired tokens are expected - log at debug level to reduce noise
                    error_msg = str(e).lower()
                    if 'expired' in error_msg or 'signature has expired' in error_msg:
                        logger.debug(f"Token expired (expected): {e}")
                    else:
                        logger.warning(f"fastapi-clerk-auth verification error: {e}")
                    return None
            else:
                # Fallback to custom implementation (not secure for production)
                logger.warning("Using fallback JWT decoding without signature verification")
                try:
                    import jwt
                    # Decode the JWT without verification to get claims
                    # This is NOT secure for production - only for development
                    # Add leeway to handle clock skew
                    decoded_token = jwt.decode(
                        token, 
                        options={"verify_signature": False},
                        leeway=300  # Allow 5 minutes leeway for token refresh
                    )
                    
                    # Extract user information from the token
                    user_id = decoded_token.get('sub') or decoded_token.get('user_id')
                    email = decoded_token.get('email')
                    first_name = decoded_token.get('first_name')
                    last_name = decoded_token.get('last_name')
                    
                    if not user_id:
                        logger.warning("No user ID found in token")
                        return None
                    
                    logger.info(f"Token decoded successfully (fallback) for user: {email} (ID: {user_id})")
                    return {
                        'id': user_id,
                        'email': email,
                        'first_name': first_name,
                        'last_name': last_name,
                        'clerk_user_id': user_id
                    }
                    
                except Exception as e:
                    logger.warning(f"Fallback JWT decode error: {e}")
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
        user = await clerk_auth.verify_token(token)
        if not user:
            # Token verification failed (likely expired) - log at debug level to reduce noise
            # The HTTPException will still be raised, but we don't need to spam logs
            logger.debug("Token verification failed (likely expired token)")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed",
                headers={"WWW-Authenticate": "Bearer"},
            )

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
