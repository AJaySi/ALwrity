"""Business Information Service for ALwrity backend."""
from sqlalchemy.orm import Session
from models.user_business_info import UserBusinessInfo
from models.business_info_request import BusinessInfoRequest, BusinessInfoResponse
from services.database import get_db
from loguru import logger
from typing import Optional

logger.info("🔄 Loading BusinessInfoService...")

class BusinessInfoService:
    def __init__(self):
        logger.info("🆕 Initializing BusinessInfoService...")

    def save_business_info(self, business_info: BusinessInfoRequest) -> BusinessInfoResponse:
        db: Session = next(get_db())
        logger.debug(f"Attempting to save business info for user_id: {business_info.user_id}")
        
        # Check if business info already exists for this user
        existing_info = db.query(UserBusinessInfo).filter(UserBusinessInfo.user_id == business_info.user_id).first()
        
        if existing_info:
            logger.info(f"Existing business info found for user_id {business_info.user_id}, updating it.")
            existing_info.business_description = business_info.business_description
            existing_info.industry = business_info.industry
            existing_info.target_audience = business_info.target_audience
            existing_info.business_goals = business_info.business_goals
            db.commit()
            db.refresh(existing_info)
            logger.success(f"Updated business info for user_id {business_info.user_id}, ID: {existing_info.id}")
            return BusinessInfoResponse(**existing_info.to_dict())
        else:
            logger.info(f"No existing business info for user_id {business_info.user_id}, creating new entry.")
            db_business_info = UserBusinessInfo(
                user_id=business_info.user_id,
                business_description=business_info.business_description,
                industry=business_info.industry,
                target_audience=business_info.target_audience,
                business_goals=business_info.business_goals
            )
            db.add(db_business_info)
            db.commit()
            db.refresh(db_business_info)
            logger.success(f"Saved new business info for user_id {business_info.user_id}, ID: {db_business_info.id}")
            return BusinessInfoResponse(**db_business_info.to_dict())

    def get_business_info(self, business_info_id: int) -> Optional[BusinessInfoResponse]:
        db: Session = next(get_db())
        logger.debug(f"Retrieving business info by ID: {business_info_id}")
        business_info = db.query(UserBusinessInfo).filter(UserBusinessInfo.id == business_info_id).first()
        if business_info:
            logger.debug(f"Found business info for ID: {business_info_id}")
            return BusinessInfoResponse(**business_info.to_dict())
        logger.warning(f"No business info found for ID: {business_info_id}")
        return None

    def get_business_info_by_user(self, user_id: int) -> Optional[BusinessInfoResponse]:
        db: Session = next(get_db())
        logger.debug(f"Retrieving business info by user ID: {user_id}")
        business_info = db.query(UserBusinessInfo).filter(UserBusinessInfo.user_id == user_id).first()
        if business_info:
            logger.debug(f"Found business info for user ID: {user_id}")
            return BusinessInfoResponse(**business_info.to_dict())
        logger.warning(f"No business info found for user ID: {user_id}")
        return None

    def update_business_info(self, business_info_id: int, business_info: BusinessInfoRequest) -> Optional[BusinessInfoResponse]:
        db: Session = next(get_db())
        logger.debug(f"Updating business info for ID: {business_info_id}")
        db_business_info = db.query(UserBusinessInfo).filter(UserBusinessInfo.id == business_info_id).first()
        if db_business_info:
            db_business_info.business_description = business_info.business_description
            db_business_info.industry = business_info.industry
            db_business_info.target_audience = business_info.target_audience
            db_business_info.business_goals = business_info.business_goals
            db.commit()
            db.refresh(db_business_info)
            logger.success(f"Updated business info for ID: {business_info_id}")
            return BusinessInfoResponse(**db_business_info.to_dict())
        logger.warning(f"No business info found to update for ID: {business_info_id}")
        return None

business_info_service = BusinessInfoService()
logger.info("✅ BusinessInfoService loaded successfully!")
