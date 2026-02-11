"""
Unified OAuth Validation API Endpoints
Provides endpoints for OAuth connection validation using unified token service.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from loguru import logger

from services.database import get_db_session
from middleware.auth_middleware import get_current_user
from services.onboarding.unified_oauth_validator import UnifiedOAuthValidator

router = APIRouter(prefix="/api/oauth-validation", tags=["oauth-validation"])


@router.get("/step5/{user_id}")
async def validate_step_5_completion(
    user_id: str,
    db: Session = Depends(get_db_session),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Validate Step 5 completion using unified OAuth token service.
    
    This endpoint provides comprehensive OAuth connection validation
    for onboarding Step 5 using the new unified framework.
    
    Args:
        user_id: User identifier
        
    Returns:
        Dict[str, Any]: Step 5 validation results with detailed connection info
    """
    try:
        # Verify user can only access their own data
        if str(current_user.get('id')) != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        logger.info(f"[OAuth Validation API] Validating Step 5 for user {user_id}")
        
        # Initialize unified OAuth validator
        validator = UnifiedOAuthValidator()
        
        # Validate Step 5 completion
        is_complete = validator.validate_step_5_completion(user_id)
        
        # Get comprehensive connection summary
        connection_summary = validator.get_connection_summary(user_id)
        
        # Build response
        response = {
            "success": True,
            "user_id": user_id,
            "step_5_complete": is_complete,
            "connection_summary": connection_summary,
            "validation_time": connection_summary.get('validation_time'),
            "message": "Step 5 validation completed successfully" if is_complete else "Step 5 validation failed - no valid OAuth connections found"
        }
        
        logger.info(f"[OAuth Validation API] Step 5 validation for user {user_id}: {is_complete}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[OAuth Validation API] Error validating Step 5 for user {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to validate Step 5: {str(e)}"
        )


@router.get("/connections/{user_id}")
async def get_oauth_connections(
    user_id: str,
    db: Session = Depends(get_db_session),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get comprehensive OAuth connection summary for a user.
    
    This endpoint provides detailed information about all OAuth connections
    using the unified token service.
    
    Args:
        user_id: User identifier
        
    Returns:
        Dict[str, Any]: Comprehensive connection summary
    """
    try:
        # Verify user can only access their own data
        if str(current_user.get('id')) != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        logger.info(f"[OAuth Validation API] Getting OAuth connections for user {user_id}")
        
        # Initialize unified OAuth validator
        validator = UnifiedOAuthValidator()
        
        # Get connection summary
        connection_summary = validator.get_connection_summary(user_id)
        
        response = {
            "success": True,
            "user_id": user_id,
            "connections": connection_summary,
            "message": "OAuth connections retrieved successfully"
        }
        
        logger.info(f"[OAuth Validation API] Retrieved {connection_summary['connected_platforms']} connections for user {user_id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[OAuth Validation API] Error getting OAuth connections for user {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve OAuth connections: {str(e)}"
        )


@router.get("/provider/{provider_id}/{user_id}")
async def validate_provider_connection(
    provider_id: str,
    user_id: str,
    db: Session = Depends(get_db_session),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Validate connection for a specific OAuth provider.
    
    This endpoint provides detailed validation for a specific provider
    using the unified token service.
    
    Args:
        provider_id: Provider identifier (gsc, bing, wordpress, wix)
        user_id: User identifier
        
    Returns:
        Dict[str, Any]: Provider-specific validation result
    """
    try:
        # Verify user can only access their own data
        if str(current_user.get('id')) != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        logger.info(f"[OAuth Validation API] Validating {provider_id} connection for user {user_id}")
        
        # Initialize unified OAuth validator
        validator = UnifiedOAuthValidator()
        
        # Validate specific provider
        provider_validation = validator.validate_provider_connection(user_id, provider_id)
        
        response = {
            "success": True,
            "user_id": user_id,
            "provider_id": provider_id,
            "validation": provider_validation,
            "message": f"Provider {provider_id} validation completed successfully"
        }
        
        logger.info(f"[OAuth Validation API] {provider_id} validation for user {user_id}: {provider_validation.get('valid', False)}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[OAuth Validation API] Error validating {provider_id} for user {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to validate provider {provider_id}: {str(e)}"
        )


@router.get("/health/{user_id}")
async def get_oauth_health_status(
    user_id: str,
    db: Session = Depends(get_db_session),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get health status for all OAuth providers.
    
    This endpoint provides comprehensive health monitoring for all OAuth
    connections using the unified token service.
    
    Args:
        user_id: User identifier
        
    Returns:
        Dict[str, Any]: Health status for all providers
    """
    try:
        # Verify user can only access their own data
        if str(current_user.get('id')) != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        logger.info(f"[OAuth Validation API] Getting OAuth health status for user {user_id}")
        
        # Initialize unified OAuth validator
        validator = UnifiedOAuthValidator()
        
        # Get health status
        health_status = validator.get_provider_health_status(user_id)
        
        response = {
            "success": True,
            "user_id": user_id,
            "health_status": health_status,
            "message": "OAuth health status retrieved successfully"
        }
        
        overall = health_status.get('overall', {})
        logger.info(f"[OAuth Validation API] Health status for user {user_id}:")
        logger.info(f"  - Healthy providers: {overall.get('healthy_providers', 0)}")
        logger.info(f"  - Warning providers: {overall.get('warning_providers', 0)}")
        logger.info(f"  - Critical providers: {overall.get('critical_providers', 0)}")
        logger.info(f"  - Average health score: {overall.get('average_health_score', 0):.1f}")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[OAuth Validation API] Error getting OAuth health status for user {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve OAuth health status: {str(e)}"
        )


@router.get("/expiring-soon/{user_id}")
async def get_expiring_tokens(
    user_id: str,
    days: Optional[int] = Query(7, description="Days until expiration to check"),
    db: Session = Depends(get_db_session),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get tokens that are expiring soon.
    
    This endpoint identifies tokens that need attention due to upcoming expiration.
    
    Args:
        user_id: User identifier
        days: Days until expiration to check (default: 7)
        
    Returns:
        Dict[str, Any]: List of expiring tokens
    """
    try:
        # Verify user can only access their own data
        if str(current_user.get('id')) != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        logger.info(f"[OAuth Validation API] Getting expiring tokens for user {user_id} (within {days} days)")
        
        # Initialize unified OAuth validator
        validator = UnifiedOAuthValidator()
        
        # Get connection summary which includes expiring tokens
        connection_summary = validator.get_connection_summary(user_id)
        
        # Filter for tokens expiring within specified days
        expiring_tokens = connection_summary.get('expiring_soon', [])
        if days != 7:
            # Filter based on custom days parameter
            expiring_tokens = [
                token for token in expiring_tokens
                if token.get('days_until_expiry', 0) <= days
            ]
        
        response = {
            "success": True,
            "user_id": user_id,
            "expiring_tokens": expiring_tokens,
            "days_threshold": days,
            "count": len(expiring_tokens),
            "message": f"Found {len(expiring_tokens)} tokens expiring within {days} days"
        }
        
        logger.info(f"[OAuth Validation API] Found {len(expiring_tokens)} tokens expiring within {days} days for user {user_id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[OAuth Validation API] Error getting expiring tokens for user {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve expiring tokens: {str(e)}"
        )
