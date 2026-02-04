"""Service for managing user website automation records."""
from typing import Optional
from loguru import logger
from sqlalchemy.exc import SQLAlchemyError

from services.database import get_platform_db_session
from models.user_website import UserWebsite
from models.user_website_request import UserWebsiteRequest, UserWebsiteResponse


class UserWebsiteService:
    def __init__(self):
        logger.info("🆕 Initializing UserWebsiteService...")

    def create_user_website(self, website_request: UserWebsiteRequest) -> UserWebsiteResponse:
        logger.debug(f"Creating user website for user_id: {website_request.user_id}")
        db = get_platform_db_session()
        if db is None:
            raise RuntimeError("Platform database session unavailable")

        try:
            db_record = UserWebsite(
                user_id=website_request.user_id,
                github_repo_url=website_request.github_repo_url,
                netlify_site_id=website_request.netlify_site_id,
                netlify_site_url=website_request.netlify_site_url,
                template_type=website_request.template_type,
                status=website_request.status,
            )
            db.add(db_record)
            db.commit()
            db.refresh(db_record)
            logger.success(f"✅ User website created for user_id {website_request.user_id}, ID: {db_record.id}")
            return UserWebsiteResponse(**db_record.to_dict())
        except SQLAlchemyError as exc:
            db.rollback()
            logger.error(f"❌ Failed to create user website: {exc}")
            raise
        finally:
            db.close()

    def get_user_website_by_user(self, user_id: str) -> Optional[UserWebsiteResponse]:
        logger.debug(f"Fetching user website for user_id: {user_id}")
        db = get_platform_db_session()
        if db is None:
            raise RuntimeError("Platform database session unavailable")

        try:
            record = db.query(UserWebsite).filter(UserWebsite.user_id == user_id).first()
            if record:
                return UserWebsiteResponse(**record.to_dict())
            return None
        finally:
            db.close()

    def update_user_website_status(
        self,
        user_id: str,
        status: str,
        github_repo_url: Optional[str] = None,
        netlify_site_id: Optional[str] = None,
        netlify_site_url: Optional[str] = None,
        preview_url: Optional[str] = None,
    ) -> Optional[UserWebsiteResponse]:
        logger.debug(f"Updating user website for user_id: {user_id} with status: {status}")
        db = get_platform_db_session()
        if db is None:
            raise RuntimeError("Platform database session unavailable")

        try:
            record = db.query(UserWebsite).filter(UserWebsite.user_id == user_id).first()
            if not record:
                logger.warning(f"No user website found for user_id {user_id}")
                return None

            record.status = status
            if github_repo_url is not None:
                record.github_repo_url = github_repo_url
            if netlify_site_id is not None:
                record.netlify_site_id = netlify_site_id
            if netlify_site_url is not None:
                record.netlify_site_url = netlify_site_url
            if preview_url is not None:
                record.preview_url = preview_url

            db.commit()
            db.refresh(record)
            logger.success(f"✅ Updated user website for user_id {user_id}")
            return UserWebsiteResponse(**record.to_dict())
        except SQLAlchemyError as exc:
            db.rollback()
            logger.error(f"❌ Failed to update user website: {exc}")
            raise
        finally:
            db.close()


user_website_service = UserWebsiteService()
