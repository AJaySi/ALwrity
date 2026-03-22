"""User Data API endpoints for ALwrity."""

from fastapi import APIRouter, HTTPException, Depends
from loguru import logger

from services.user_data_service import UserDataService
from services.database import get_db_session
from middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/api/user-data", tags=["user-data"])

@router.get("/")
async def get_user_data(current_user: dict = Depends(get_current_user)):
    """Get comprehensive user data from onboarding."""
    db_session = None
    try:
        user_id = str(current_user.get("id"))
        db_session = get_db_session()
        if not db_session:
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        user_data_service = UserDataService(db_session)
        user_data = user_data_service.get_user_onboarding_data(user_id)
        
        if not user_data:
            raise HTTPException(status_code=404, detail="No onboarding data found for user")

        website_url = user_data_service.get_user_website_url(user_id)
        if user_data.get("website_analysis"):
            user_data["website_url"] = website_url
        
        return user_data

    except HTTPException:
        raise
        
    except Exception as e:
        logger.error(f"Error getting user data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting user data: {str(e)}")
    finally:
        if db_session:
            db_session.close()

@router.get("/website-url")
async def get_website_url(current_user: dict = Depends(get_current_user)):
    """Get the user's website URL from onboarding data."""
    db_session = None
    try:
        user_id = str(current_user.get("id"))
        db_session = get_db_session()
        if not db_session:
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        user_data_service = UserDataService(db_session)
        onboarding_data = user_data_service.get_user_onboarding_data(user_id)
        if not onboarding_data:
            raise HTTPException(status_code=404, detail="No onboarding data found for user")

        website_url = user_data_service.get_user_website_url(user_id)
        
        if not website_url:
            return {"website_url": None, "message": "No website URL found"}
        
        return {"website_url": website_url}

    except HTTPException:
        raise
        
    except Exception as e:
        logger.error(f"Error getting website URL: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting website URL: {str(e)}")
    finally:
        if db_session:
            db_session.close()

@router.get("/onboarding")
async def get_onboarding_data(current_user: dict = Depends(get_current_user)):
    """Get onboarding data for the user."""
    db_session = None
    try:
        user_id = str(current_user.get("id"))
        db_session = get_db_session()
        if not db_session:
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        user_data_service = UserDataService(db_session)
        onboarding_data = user_data_service.get_user_onboarding_data(user_id)
        
        if not onboarding_data:
            raise HTTPException(status_code=404, detail="No onboarding data found for user")

        website_url = user_data_service.get_user_website_url(user_id)
        if onboarding_data.get("website_analysis"):
            onboarding_data["website_url"] = website_url
        
        return onboarding_data

    except HTTPException:
        raise
        
    except Exception as e:
        logger.error(f"Error getting onboarding data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting onboarding data: {str(e)}")
    finally:
        if db_session:
            db_session.close() 
