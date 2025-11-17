from typing import Any, Dict

from fastapi import HTTPException, status


def require_authenticated_user(current_user: Dict[str, Any] | None) -> str:
    """
    Validates the current user dictionary provided by Clerk middleware and
    returns the normalized user_id. Raises HTTP 401 if authentication fails.
    """
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")

    user_id = str(current_user.get("id", "")).strip()
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in authentication token",
        )

    return user_id


