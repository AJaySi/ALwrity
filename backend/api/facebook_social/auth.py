import os
import httpx
from fastapi import HTTPException, Depends, Header
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class ClerkAuthError(Exception):
    pass

async def verify_clerk_session(authorization: Optional[str] = Header(None)) -> dict:
    """
    Verify Clerk session token and return user data.
    Uses Clerk's Sessions API with secret key for server-side verification.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format")
    
    session_token = authorization[7:]  # Remove "Bearer " prefix
    
    clerk_secret_key = os.getenv("CLERK_SECRET_KEY")
    if not clerk_secret_key:
        logger.error("CLERK_SECRET_KEY not found in environment")
        raise HTTPException(status_code=500, detail="Authentication service not configured")
    
    try:
        # Call Clerk Sessions API to verify the session
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.clerk.com/v1/sessions",
                headers={
                    "Authorization": f"Bearer {clerk_secret_key}",
                    "Content-Type": "application/json"
                },
                params={"session_token": session_token}
            )
            
            if response.status_code == 200:
                sessions = response.json()
                if sessions and len(sessions) > 0:
                    session = sessions[0]
                    user_id = session.get("user_id")
                    if user_id:
                        return {
                            "clerk_user_id": user_id,
                            "session_id": session.get("id"),
                            "status": session.get("status")
                        }
            
            logger.warning(f"Clerk session verification failed: {response.status_code}")
            raise HTTPException(status_code=401, detail="Invalid or expired session")
            
    except httpx.RequestError as e:
        logger.error(f"Error calling Clerk API: {str(e)}")
        raise HTTPException(status_code=500, detail="Authentication service unavailable")
    except Exception as e:
        logger.error(f"Unexpected error in Clerk verification: {str(e)}")
        raise HTTPException(status_code=500, detail="Authentication error")

def require_clerk_user(auth_data: dict = Depends(verify_clerk_session)) -> dict:
    """
    Dependency that requires a valid Clerk user session.
    """
    if not auth_data.get("clerk_user_id"):
        raise HTTPException(status_code=401, detail="User not authenticated")
    
    return auth_data
