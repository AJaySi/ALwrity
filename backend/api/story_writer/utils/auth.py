from typing import Any, Dict

from fastapi import HTTPException, status


def require_authenticated_user(current_user: Dict[str, Any] | None) -> str:
    """
    Validates the current user dictionary provided by Clerk middleware and
    returns the normalized user_id. Raises HTTP 401 if authentication fails.
    """
    # Guard against dependency injection issues where Depends object might be passed
    if current_user is None or not isinstance(current_user, dict):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    
    # Additional check: ensure it's actually a dict and not a Depends object or other type
    if not hasattr(current_user, 'get') or not callable(getattr(current_user, 'get')):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication context")
    
    user_id = str(current_user.get("id", "")).strip()
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in authentication token",
        )

    return user_id


