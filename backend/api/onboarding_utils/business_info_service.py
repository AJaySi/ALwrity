"""
Business Information Service
Handles business information management for users without websites.
"""

from typing import Dict, Any, Optional
from fastapi import HTTPException
from loguru import logger

class BusinessInfoService:
    """Service for handling business information operations."""
    
    def __init__(self):
        pass
    
    async def save_business_info(self, business_info: dict) -> Dict[str, Any]:
        """Save business information for users without websites."""
        try:
            from models.business_info_request import BusinessInfoRequest
            from services.business_info_service import business_info_service
            
            request_model = BusinessInfoRequest(**business_info)
            logger.info(f"🔄 Saving business info for user_id: {request_model.user_id}")
            result = business_info_service.save_business_info(request_model)
            logger.success(f"✅ Business info saved successfully for user_id: {request_model.user_id}")
            return result
        except Exception as e:
            logger.error(f"❌ Error saving business info: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to save business info: {str(e)}")
    
    async def get_business_info(self, business_info_id: int) -> Dict[str, Any]:
        """Get business information by ID."""
        try:
            from services.business_info_service import business_info_service
            
            logger.info(f"🔄 Getting business info for ID: {business_info_id}")
            result = business_info_service.get_business_info(business_info_id)
            if result:
                logger.success(f"✅ Business info retrieved for ID: {business_info_id}")
                return result
            else:
                logger.warning(f"⚠️ No business info found for ID: {business_info_id}")
                raise HTTPException(status_code=404, detail="Business info not found")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Error getting business info: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to get business info: {str(e)}")
    
    async def get_business_info_by_user(self, user_id: str) -> Dict[str, Any]:
        """Get business information by user ID."""
        try:
            from services.business_info_service import business_info_service
            
            logger.info(f"🔄 Getting business info for user ID: {user_id}")
            result = business_info_service.get_business_info_by_user(user_id)
            if result:
                logger.success(f"✅ Business info retrieved for user ID: {user_id}")
                return result
            else:
                logger.warning(f"⚠️ No business info found for user ID: {user_id}")
                raise HTTPException(status_code=404, detail="Business info not found")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Error getting business info: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to get business info: {str(e)}")
    
    async def update_business_info(self, business_info_id: int, business_info: dict) -> Dict[str, Any]:
        """Update business information."""
        try:
            from models.business_info_request import BusinessInfoRequest
            from services.business_info_service import business_info_service
            
            logger.info(f"🔄 Updating business info for ID: {business_info_id}")
            result = business_info_service.update_business_info(business_info_id, business_info)
            if result:
                logger.success(f"✅ Business info updated for ID: {business_info_id}")
                return result
            else:
                logger.warning(f"⚠️ No business info found to update for ID: {business_info_id}")
                raise HTTPException(status_code=404, detail="Business info not found")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Error updating business info: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to update business info: {str(e)}")
