"""User Website Service for ALwrity website maker functionality."""
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import desc
from loguru import logger
from datetime import datetime

from models.onboarding import UserWebsite
from models.user_website_request import (
    UserWebsiteRequest, 
    UserWebsiteResponse, 
    WebsiteStatus,
    TemplateType,
    WebsiteStatusUpdate
)
from services.database import get_db


class UserWebsiteService:
    """Service for managing user website creation and deployment."""
    
    def __init__(self):
        logger.info("🔄 Initializing UserWebsiteService...")
    
    def create_user_website(self, request: UserWebsiteRequest) -> UserWebsiteResponse:
        """Create a new user website record."""
        try:
            logger.info(f"Creating website record for user {request.user_id}")
            
            # For testing, create a session directly
            from services.database import get_session_for_user
            db = get_session_for_user(str(request.user_id))
            
            if not db:
                logger.error(f"Could not create database session for user {request.user_id}")
                raise Exception("Database session creation failed")
            
            try:
                # Check if user already has a website
                existing_website = db.query(UserWebsite).filter(
                    UserWebsite.user_id == request.user_id
                ).first()
                
                if existing_website:
                    logger.info(f"User {request.user_id} already has website ID {existing_website.id}, updating it")
                    # Update existing record
                    existing_website.template_type = request.template_type.value
                    existing_website.business_name = request.business_name
                    existing_website.business_description = request.business_description
                    existing_website.status = request.status.value
                    existing_website.site_brief = request.site_brief
                    existing_website.theme_tokens = request.theme_tokens
                    existing_website.custom_css = request.custom_css
                    existing_website.deployment_config = request.deployment_config
                    existing_website.updated_at = datetime.utcnow()
                    
                    db.commit()
                    db.refresh(existing_website)
                    logger.success(f"Updated website record for user {request.user_id}")
                    return UserWebsiteResponse(**existing_website.to_dict())
                
                # Create new website record
                db_website = UserWebsite(
                    user_id=request.user_id,
                    template_type=request.template_type.value,
                    business_name=request.business_name,
                    business_description=request.business_description,
                    status=request.status.value,
                    site_brief=request.site_brief,
                    theme_tokens=request.theme_tokens,
                    custom_css=request.custom_css,
                    deployment_config=request.deployment_config
                )
                
                db.add(db_website)
                db.commit()
                db.refresh(db_website)
                
                logger.success(f"Created website record {db_website.id} for user {request.user_id}")
                return UserWebsiteResponse(**db_website.to_dict())
                
            finally:
                db.close()
            
        except Exception as e:
            logger.error(f"Failed to create website record for user {request.user_id}: {str(e)}")
            raise
    
    def get_user_website_by_user(self, user_id: int) -> Optional[UserWebsiteResponse]:
        """Get website record by user ID."""
        try:
            logger.debug(f"Retrieving website for user {user_id}")
            
            # For testing, create a session directly
            from services.database import get_session_for_user
            db = get_session_for_user(str(user_id))
            
            if not db:
                logger.warning(f"Could not create database session for user {user_id}")
                return None
            
            try:
                website = db.query(UserWebsite).filter(
                    UserWebsite.user_id == user_id
                ).first()
                
                if website:
                    logger.debug(f"Found website {website.id} for user {user_id}")
                    return UserWebsiteResponse(**website.to_dict())
                
                logger.debug(f"No website found for user {user_id}")
                return None
            finally:
                db.close()
            
        except Exception as e:
            logger.error(f"Failed to get website for user {user_id}: {str(e)}")
            return None
    
    def get_user_website_by_id(self, website_id: int) -> Optional[UserWebsiteResponse]:
        """Get website record by website ID."""
        db: Session = next(get_db())
        try:
            logger.debug(f"Retrieving website {website_id}")
            website = db.query(UserWebsite).filter(
                UserWebsite.id == website_id
            ).first()
            
            if website:
                logger.debug(f"Found website {website_id}")
                return UserWebsiteResponse(**website.to_dict())
            
            logger.debug(f"Website {website_id} not found")
            return None
            
        except Exception as e:
            logger.error(f"Failed to get website {website_id}: {str(e)}")
            return None
        finally:
            db.close()
    
    def update_user_website_status(
        self, 
        user_id: int, 
        status_update: WebsiteStatusUpdate
    ) -> Optional[UserWebsiteResponse]:
        """Update website status and related fields."""
        db: Session = next(get_db())
        try:
            logger.info(f"Updating website status for user {user_id} to {status_update.status}")
            
            website = db.query(UserWebsite).filter(
                UserWebsite.user_id == user_id
            ).first()
            
            if not website:
                logger.warning(f"No website found for user {user_id}")
                return None
            
            # Update fields
            website.status = status_update.status.value
            website.updated_at = datetime.utcnow()
            
            if status_update.github_repo_url is not None:
                website.github_repo_url = status_update.github_repo_url
            if status_update.netlify_site_url is not None:
                website.netlify_site_url = status_update.netlify_site_url
            if status_update.netlify_admin_url is not None:
                website.netlify_admin_url = status_update.netlify_admin_url
            if status_update.preview_url is not None:
                website.preview_url = status_update.preview_url
            if status_update.error_message is not None:
                website.error_message = status_update.error_message
            
            db.commit()
            db.refresh(website)
            
            logger.success(f"Updated website {website.id} status to {status_update.status}")
            return UserWebsiteResponse(**website.to_dict())
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to update website status for user {user_id}: {str(e)}")
            raise
        finally:
            db.close()
    
    def update_user_website_content(
        self,
        user_id: int,
        site_brief: Optional[Dict[str, Any]] = None,
        theme_tokens: Optional[Dict[str, Any]] = None,
        custom_css: Optional[str] = None
    ) -> Optional[UserWebsiteResponse]:
        """Update website content (site brief, theme, CSS)."""
        db: Session = next(get_db())
        try:
            logger.info(f"Updating website content for user {user_id}")
            
            website = db.query(UserWebsite).filter(
                UserWebsite.user_id == user_id
            ).first()
            
            if not website:
                logger.warning(f"No website found for user {user_id}")
                return None
            
            if site_brief is not None:
                website.site_brief = site_brief
            if theme_tokens is not None:
                website.theme_tokens = theme_tokens
            if custom_css is not None:
                website.custom_css = custom_css
            
            website.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(website)
            
            logger.success(f"Updated website {website.id} content")
            return UserWebsiteResponse(**website.to_dict())
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to update website content for user {user_id}: {str(e)}")
            raise
        finally:
            db.close()
    
    def delete_user_website(self, user_id: int) -> bool:
        """Delete user website record."""
        db: Session = next(get_db())
        try:
            logger.info(f"Deleting website for user {user_id}")
            
            website = db.query(UserWebsite).filter(
                UserWebsite.user_id == user_id
            ).first()
            
            if not website:
                logger.warning(f"No website found for user {user_id}")
                return False
            
            db.delete(website)
            db.commit()
            
            logger.success(f"Deleted website {website.id} for user {user_id}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to delete website for user {user_id}: {str(e)}")
            raise
        finally:
            db.close()
    
    def get_all_user_websites(self, user_id: int) -> List[UserWebsiteResponse]:
        """Get all websites for a user (for history/audit)."""
        db: Session = next(get_db())
        try:
            logger.debug(f"Retrieving all websites for user {user_id}")
            
            websites = db.query(UserWebsite).filter(
                UserWebsite.user_id == user_id
            ).order_by(desc(UserWebsite.created_at)).all()
            
            return [UserWebsiteResponse(**website.to_dict()) for website in websites]
            
        except Exception as e:
            logger.error(f"Failed to get websites for user {user_id}: {str(e)}")
            return []
        finally:
            db.close()
    
    def get_websites_by_status(self, status: WebsiteStatus) -> List[UserWebsiteResponse]:
        """Get all websites with a specific status (for admin/monitoring)."""
        db: Session = next(get_db())
        try:
            logger.debug(f"Retrieving websites with status {status}")
            
            websites = db.query(UserWebsite).filter(
                UserWebsite.status == status.value
            ).order_by(desc(UserWebsite.created_at)).all()
            
            return [UserWebsiteResponse(**website.to_dict()) for website in websites]
            
        except Exception as e:
            logger.error(f"Failed to get websites with status {status}: {str(e)}")
            return []
        finally:
            db.close()


# Singleton instance
user_website_service = UserWebsiteService()
