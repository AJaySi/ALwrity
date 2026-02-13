"""
Database Service Layer for AI Backlinking

Provides database operations for all backlinking entities with proper
error handling, transaction management, and AI-first optimizations.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, text
from sqlalchemy.exc import SQLAlchemyError

from models.backlinking import (
    BacklinkingCampaign,
    BacklinkOpportunity,
    BacklinkingEmail,
    BacklinkingResponse,
    BacklinkingAnalytics,
    AILearningData,
    BacklinkingTemplate,
)
from services.database import SessionLocal
from .exceptions import (
    CampaignNotFoundError,
    OpportunityNotFoundError,
    BacklinkingError,
    handle_service_error,
)
from .logging_utils import campaign_logger, log_campaign_action


class BacklinkingDatabaseService:
    """
    Database service for AI backlinking operations.

    Provides CRUD operations for all backlinking entities with
    AI-first optimizations and proper error handling.
    """

    def __init__(self, db: Optional[Session] = None):
        self.db = db or SessionLocal()

    def _get_db(self) -> Session:
        """Get database session."""
        return self.db

    # =========================================
    # CAMPAIGN OPERATIONS
    # =========================================

    async def create_campaign(self, user_id: int, campaign_data: Dict[str, Any]) -> BacklinkingCampaign:
        """
        Create a new backlinking campaign.

        Args:
            user_id: User ID
            campaign_data: Campaign data dictionary

        Returns:
            Created campaign object

        Raises:
            BacklinkingError: For database errors
        """
        try:
            # Import here to avoid circular imports
            import uuid

            campaign = BacklinkingCampaign(
                id=str(uuid.uuid4()),
                user_id=user_id,
                **campaign_data
            )

            self._get_db().add(campaign)
            self._get_db().commit()
            self._get_db().refresh(campaign)

            log_campaign_action(campaign.id, "created", user_id=user_id)
            campaign_logger.info(f"Created campaign {campaign.id} for user {user_id}")

            return campaign

        except SQLAlchemyError as e:
            self._get_db().rollback()
            campaign_logger.error(f"Failed to create campaign for user {user_id}: {e}")
            raise handle_service_error(e)

    async def get_campaign(self, campaign_id: str) -> Optional[BacklinkingCampaign]:
        """
        Get a campaign by ID.

        Args:
            campaign_id: Campaign ID

        Returns:
            Campaign object or None if not found
        """
        try:
            campaign = self._get_db().query(BacklinkingCampaign).filter(
                BacklinkingCampaign.id == campaign_id
            ).first()

            return campaign

        except SQLAlchemyError as e:
            campaign_logger.error(f"Failed to get campaign {campaign_id}: {e}")
            raise handle_service_error(e)

    async def get_user_campaigns(self, user_id: int, status: Optional[str] = None) -> List[BacklinkingCampaign]:
        """
        Get all campaigns for a user.

        Args:
            user_id: User ID
            status: Optional status filter

        Returns:
            List of campaigns
        """
        try:
            query = self._get_db().query(BacklinkingCampaign).filter(
                BacklinkingCampaign.user_id == user_id
            )

            if status:
                query = query.filter(BacklinkingCampaign.status == status)

            campaigns = query.order_by(desc(BacklinkingCampaign.created_at)).all()
            return campaigns

        except SQLAlchemyError as e:
            campaign_logger.error(f"Failed to get campaigns for user {user_id}: {e}")
            raise handle_service_error(e)

    async def update_campaign(self, campaign_id: str, update_data: Dict[str, Any]) -> BacklinkingCampaign:
        """
        Update a campaign.

        Args:
            campaign_id: Campaign ID
            update_data: Data to update

        Returns:
            Updated campaign object

        Raises:
            CampaignNotFoundError: If campaign not found
        """
        try:
            campaign = await self.get_campaign(campaign_id)
            if not campaign:
                raise CampaignNotFoundError(campaign_id)

            # Update fields
            for key, value in update_data.items():
                if hasattr(campaign, key):
                    setattr(campaign, key, value)

            campaign.updated_at = datetime.utcnow()

            self._get_db().commit()
            self._get_db().refresh(campaign)

            log_campaign_action(campaign_id, "updated", updates=list(update_data.keys()))
            return campaign

        except SQLAlchemyError as e:
            self._get_db().rollback()
            campaign_logger.error(f"Failed to update campaign {campaign_id}: {e}")
            raise handle_service_error(e)

    async def delete_campaign(self, campaign_id: str) -> bool:
        """
        Delete a campaign and all related data.

        Args:
            campaign_id: Campaign ID

        Returns:
            True if deleted, False if not found

        Raises:
            BacklinkingError: For database errors
        """
        try:
            campaign = await self.get_campaign(campaign_id)
            if not campaign:
                return False

            # Delete campaign (cascade will handle related data)
            self._get_db().delete(campaign)
            self._get_db().commit()

            log_campaign_action(campaign_id, "deleted")
            campaign_logger.info(f"Deleted campaign {campaign_id}")

            return True

        except SQLAlchemyError as e:
            self._get_db().rollback()
            campaign_logger.error(f"Failed to delete campaign {campaign_id}: {e}")
            raise handle_service_error(e)

    # =========================================
    # OPPORTUNITY OPERATIONS
    # =========================================

    async def create_opportunity(self, campaign_id: str, opportunity_data: Dict[str, Any]) -> BacklinkOpportunity:
        """
        Create a new opportunity.

        Args:
            campaign_id: Campaign ID
            opportunity_data: Opportunity data

        Returns:
            Created opportunity object
        """
        try:
            opportunity = BacklinkOpportunity(
                campaign_id=campaign_id,
                **opportunity_data
            )

            self._get_db().add(opportunity)
            self._get_db().commit()
            self._get_db().refresh(opportunity)

            log_campaign_action(campaign_id, "opportunity_added", opportunity_id=opportunity.id)
            return opportunity

        except SQLAlchemyError as e:
            self._get_db().rollback()
            campaign_logger.error(f"Failed to create opportunity for campaign {campaign_id}: {e}")
            raise handle_service_error(e)

    async def get_opportunity(self, opportunity_id: int) -> Optional[BacklinkOpportunity]:
        """
        Get an opportunity by ID.

        Args:
            opportunity_id: Opportunity ID

        Returns:
            Opportunity object or None if not found
        """
        try:
            opportunity = self._get_db().query(BacklinkOpportunity).filter(
                BacklinkOpportunity.id == opportunity_id
            ).first()

            return opportunity

        except SQLAlchemyError as e:
            campaign_logger.error(f"Failed to get opportunity {opportunity_id}: {e}")
            raise handle_service_error(e)

    async def get_campaign_opportunities(
        self,
        campaign_id: str,
        status: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[BacklinkOpportunity]:
        """
        Get opportunities for a campaign.

        Args:
            campaign_id: Campaign ID
            status: Optional status filter
            limit: Optional result limit

        Returns:
            List of opportunities
        """
        try:
            query = self._get_db().query(BacklinkOpportunity).filter(
                BacklinkOpportunity.campaign_id == campaign_id
            )

            if status:
                query = query.filter(BacklinkOpportunity.status == status)

            query = query.order_by(desc(BacklinkOpportunity.discovered_at))

            if limit:
                query = query.limit(limit)

            opportunities = query.all()
            return opportunities

        except SQLAlchemyError as e:
            campaign_logger.error(f"Failed to get opportunities for campaign {campaign_id}: {e}")
            raise handle_service_error(e)

    async def update_opportunity(self, opportunity_id: int, update_data: Dict[str, Any]) -> BacklinkOpportunity:
        """
        Update an opportunity.

        Args:
            opportunity_id: Opportunity ID
            update_data: Data to update

        Returns:
            Updated opportunity object

        Raises:
            OpportunityNotFoundError: If opportunity not found
        """
        try:
            opportunity = await self.get_opportunity(opportunity_id)
            if not opportunity:
                raise OpportunityNotFoundError(str(opportunity_id))

            # Update fields
            for key, value in update_data.items():
                if hasattr(opportunity, key):
                    setattr(opportunity, key, value)

            self._get_db().commit()
            self._get_db().refresh(opportunity)

            log_campaign_action(
                opportunity.campaign_id,
                "opportunity_updated",
                opportunity_id=opportunity_id,
                updates=list(update_data.keys())
            )
            return opportunity

        except SQLAlchemyError as e:
            self._get_db().rollback()
            campaign_logger.error(f"Failed to update opportunity {opportunity_id}: {e}")
            raise handle_service_error(e)

    # =========================================
    # EMAIL OPERATIONS
    # =========================================

    async def create_email(self, campaign_id: str, opportunity_id: int, email_data: Dict[str, Any]) -> BacklinkingEmail:
        """
        Create a new email record.

        Args:
            campaign_id: Campaign ID
            opportunity_id: Opportunity ID
            email_data: Email data

        Returns:
            Created email object
        """
        try:
            email = BacklinkingEmail(
                campaign_id=campaign_id,
                opportunity_id=opportunity_id,
                **email_data
            )

            self._get_db().add(email)
            self._get_db().commit()
            self._get_db().refresh(email)

            log_campaign_action(campaign_id, "email_created", email_id=email.id)
            return email

        except SQLAlchemyError as e:
            self._get_db().rollback()
            campaign_logger.error(f"Failed to create email for campaign {campaign_id}: {e}")
            raise handle_service_error(e)

    async def get_campaign_emails(self, campaign_id: str, status: Optional[str] = None) -> List[BacklinkingEmail]:
        """
        Get emails for a campaign.

        Args:
            campaign_id: Campaign ID
            status: Optional status filter

        Returns:
            List of emails
        """
        try:
            query = self._get_db().query(BacklinkingEmail).filter(
                BacklinkingEmail.campaign_id == campaign_id
            )

            if status:
                query = query.filter(BacklinkingEmail.status == status)

            emails = query.order_by(desc(BacklinkingEmail.created_at)).all()
            return emails

        except SQLAlchemyError as e:
            campaign_logger.error(f"Failed to get emails for campaign {campaign_id}: {e}")
            raise handle_service_error(e)

    # =========================================
    # ANALYTICS OPERATIONS
    # =========================================

    async def create_analytics_record(self, campaign_id: str, analytics_data: Dict[str, Any]) -> BacklinkingAnalytics:
        """
        Create an analytics record.

        Args:
            campaign_id: Campaign ID
            analytics_data: Analytics data

        Returns:
            Created analytics object
        """
        try:
            analytics = BacklinkingAnalytics(
                campaign_id=campaign_id,
                **analytics_data
            )

            self._get_db().add(analytics)
            self._get_db().commit()
            self._get_db().refresh(analytics)

            return analytics

        except SQLAlchemyError as e:
            self._get_db().rollback()
            campaign_logger.error(f"Failed to create analytics for campaign {campaign_id}: {e}")
            raise handle_service_error(e)

    async def get_campaign_analytics(
        self,
        campaign_id: str,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> List[BacklinkingAnalytics]:
        """
        Get analytics for a campaign.

        Args:
            campaign_id: Campaign ID
            date_from: Start date filter
            date_to: End date filter

        Returns:
            List of analytics records
        """
        try:
            query = self._get_db().query(BacklinkingAnalytics).filter(
                BacklinkingAnalytics.campaign_id == campaign_id
            )

            if date_from:
                query = query.filter(BacklinkingAnalytics.date >= date_from)
            if date_to:
                query = query.filter(BacklinkingAnalytics.date <= date_to)

            analytics = query.order_by(desc(BacklinkingAnalytics.date)).all()
            return analytics

        except SQLAlchemyError as e:
            campaign_logger.error(f"Failed to get analytics for campaign {campaign_id}: {e}")
            raise handle_service_error(e)

    # =========================================
    # AI LEARNING OPERATIONS
    # =========================================

    async def store_ai_learning_data(
        self,
        user_id: int,
        data_type: str,
        data_key: str,
        data_value: Dict[str, Any],
        success_score: float = 0.0,
        source_campaign_id: Optional[str] = None,
        source_opportunity_id: Optional[int] = None
    ) -> AILearningData:
        """
        Store AI learning data.

        Args:
            user_id: User ID
            data_type: Type of learning data
            data_key: Data identifier
            data_value: Learning data
            success_score: Success score (0-1)
            source_campaign_id: Source campaign ID
            source_opportunity_id: Source opportunity ID

        Returns:
            Created learning data object
        """
        try:
            # Check if data already exists
            existing = self._get_db().query(AILearningData).filter(
                and_(
                    AILearningData.user_id == user_id,
                    AILearningData.data_type == data_type,
                    AILearningData.data_key == data_key
                )
            ).first()

            if existing:
                # Update existing data
                existing.data_value = data_value
                existing.success_score = success_score
                existing.usage_count += 1
                existing.last_used = datetime.utcnow()
                existing.updated_at = datetime.utcnow()

                if source_campaign_id:
                    existing.source_campaign_id = source_campaign_id
                if source_opportunity_id:
                    existing.source_opportunity_id = source_opportunity_id

                self._get_db().commit()
                return existing

            # Create new learning data
            learning_data = AILearningData(
                user_id=user_id,
                data_type=data_type,
                data_key=data_key,
                data_value=data_value,
                success_score=success_score,
                source_campaign_id=source_campaign_id,
                source_opportunity_id=source_opportunity_id
            )

            self._get_db().add(learning_data)
            self._get_db().commit()
            self._get_db().refresh(learning_data)

            return learning_data

        except SQLAlchemyError as e:
            self._get_db().rollback()
            campaign_logger.error(f"Failed to store AI learning data: {e}")
            raise handle_service_error(e)

    async def get_ai_learning_data(
        self,
        user_id: int,
        data_type: Optional[str] = None,
        limit: int = 100
    ) -> List[AILearningData]:
        """
        Get AI learning data for a user.

        Args:
            user_id: User ID
            data_type: Optional data type filter
            limit: Maximum results

        Returns:
            List of learning data
        """
        try:
            query = self._get_db().query(AILearningData).filter(
                AILearningData.user_id == user_id
            )

            if data_type:
                query = query.filter(AILearningData.data_type == data_type)

            learning_data = query.order_by(desc(AILearningData.last_used)).limit(limit).all()
            return learning_data

        except SQLAlchemyError as e:
            campaign_logger.error(f"Failed to get AI learning data for user {user_id}: {e}")
            raise handle_service_error(e)

    # =========================================
    # TEMPLATE OPERATIONS
    # =========================================

    async def get_email_templates(
        self,
        category: Optional[str] = None,
        is_active: bool = True
    ) -> List[BacklinkingTemplate]:
        """
        Get email templates.

        Args:
            category: Optional category filter
            is_active: Whether to get only active templates

        Returns:
            List of templates
        """
        try:
            query = self._get_db().query(BacklinkingTemplate)

            if is_active:
                query = query.filter(BacklinkingTemplate.is_active == True)

            if category:
                query = query.filter(BacklinkingTemplate.category == category)

            templates = query.order_by(desc(BacklinkingTemplate.usage_count)).all()
            return templates

        except SQLAlchemyError as e:
            campaign_logger.error(f"Failed to get email templates: {e}")
            raise handle_service_error(e)

    # =========================================
    # UTILITY METHODS
    # =========================================

    async def get_campaign_stats(self, campaign_id: str) -> Dict[str, Any]:
        """
        Get comprehensive statistics for a campaign.

        Args:
            campaign_id: Campaign ID

        Returns:
            Statistics dictionary
        """
        try:
            # Get basic counts
            opportunity_counts = self._get_db().query(
                func.count(BacklinkOpportunity.id),
                BacklinkOpportunity.status
            ).filter(
                BacklinkOpportunity.campaign_id == campaign_id
            ).group_by(BacklinkOpportunity.status).all()

            email_counts = self._get_db().query(
                func.count(BacklinkingEmail.id),
                BacklinkingEmail.status
            ).filter(
                BacklinkingEmail.campaign_id == campaign_id
            ).group_by(BacklinkingEmail.status).all()

            response_count = self._get_db().query(func.count(BacklinkingResponse.id)).filter(
                BacklinkingResponse.campaign_id == campaign_id
            ).scalar()

            # Calculate AI performance metrics
            ai_emails = self._get_db().query(func.count(BacklinkingEmail.id)).filter(
                and_(
                    BacklinkingEmail.campaign_id == campaign_id,
                    BacklinkingEmail.ai_model_used.isnot(None)
                )
            ).scalar()

            successful_links = self._get_db().query(func.count(BacklinkOpportunity.id)).filter(
                and_(
                    BacklinkOpportunity.campaign_id == campaign_id,
                    BacklinkOpportunity.link_acquired == True
                )
            ).scalar()

            return {
                "opportunities": dict(opportunity_counts),
                "emails": dict(email_counts),
                "responses": response_count or 0,
                "ai_emails": ai_emails or 0,
                "successful_links": successful_links or 0,
                "success_rate": (successful_links / max(len(opportunity_counts), 1)) * 100
            }

        except SQLAlchemyError as e:
            campaign_logger.error(f"Failed to get campaign stats for {campaign_id}: {e}")
            return {}

    def close(self):
        """Close the database session."""
        if self.db:
            self.db.close()