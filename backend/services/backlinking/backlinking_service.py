"""
AI Backlinking Service

Main service that orchestrates the complete backlinking workflow:
- Keyword research and opportunity discovery
- Website scraping and contact extraction
- Personalized email generation and automation
- Campaign tracking and analytics
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import asyncio
from loguru import logger

from .scraping_service import WebScrapingService
from .email_service import EmailAutomationService
from .campaign_service import CampaignManagementService
from .research_service import BacklinkingResearchService
from .config import get_config
from .logging_utils import backlinking_logger, log_operation, log_campaign_action
from .exceptions import (
    BacklinkingError,
    CampaignNotFoundError,
    CampaignValidationError,
    AIProcessingError,
    AIServiceUnavailableError,
    handle_service_error,
)
from services.database import SessionLocal
from services.llm_providers import get_llm_provider
from services.research_service import ResearchService


@dataclass
class BacklinkOpportunity:
    """Represents a potential backlinking opportunity."""
    url: str
    title: str
    description: str
    contact_email: Optional[str] = None
    contact_name: Optional[str] = None
    domain_authority: Optional[int] = None
    content_topics: List[str] = None
    submission_guidelines: Optional[str] = None
    status: str = "discovered"  # discovered, contacted, responded, published


@dataclass
class BacklinkingCampaign:
    """Represents a backlinking campaign."""
    campaign_id: str
    user_id: int
    name: str
    keywords: List[str]
    status: str = "active"  # active, paused, completed
    created_at: datetime = None
    opportunities: List[BacklinkOpportunity] = None
    email_stats: Dict[str, int] = None


class BacklinkingService:
    """
    Main service for AI-powered backlinking operations.

    Orchestrates the complete workflow from opportunity discovery
    to email outreach and campaign management.
    """

    def __init__(self):
        self.config = get_config()
        self.scraping_service = WebScrapingService()
        self.email_service = EmailAutomationService()
        self.campaign_service = CampaignManagementService()
        self.backlinking_research_service = BacklinkingResearchService()
        self.research_service = ResearchService()
        self.llm_provider = get_llm_provider()

    @log_operation("create_campaign")
    async def create_campaign(
        self,
        user_id: int,
        campaign_name: str,
        keywords: List[str],
        user_proposal: Dict[str, Any]
    ) -> BacklinkingCampaign:
        """
        Create a new backlinking campaign.

        Args:
            user_id: User ID
            campaign_name: Name of the campaign
            keywords: List of keywords to search for opportunities
            user_proposal: User's guest post proposal details

        Returns:
            BacklinkingCampaign: Created campaign object
        """
        try:
            # Validate input parameters
            self._validate_campaign_data(campaign_name, keywords, user_proposal)

            campaign = await self.campaign_service.create_campaign(
                user_id=user_id,
                name=campaign_name,
                keywords=keywords,
                user_proposal=user_proposal
            )

            log_campaign_action(
                campaign.campaign_id,
                "created",
                user_id=user_id,
                keyword_count=len(keywords)
            )
            return campaign

        except CampaignValidationError:
            raise  # Re-raise validation errors as-is
        except Exception as e:
            backlinking_logger.operation_error(
                "create_campaign",
                e,
                user_id=user_id,
                campaign_name=campaign_name
            )
            raise handle_service_error(e)

    async def discover_opportunities(
        self,
        campaign_id: str,
        keywords: List[str],
        industry: Optional[str] = None,
        target_audience: Optional[str] = None,
        max_opportunities: int = 50,
        enable_trend_analysis: bool = False
    ) -> Dict[str, Any]:
        """
        Discover backlinking opportunities using AI-powered research.

        Args:
            campaign_id: Campaign ID
            keywords: Keywords to search for opportunities
            industry: Industry context for better targeting
            target_audience: Target audience for relevance
            max_opportunities: Maximum opportunities to discover
            enable_trend_analysis: Whether to include Google Trends analysis

        Returns:
            Dictionary with discovery results and metadata
        """
        try:
            log_campaign_action(campaign_id, "opportunity_discovery_started", {
                "keywords": keywords,
                "industry": industry,
                "max_opportunities": max_opportunities
            })

            # Use the new AI-powered research service
            discovery_result = await self.backlinking_research_service.discover_opportunities(
                campaign_id=campaign_id,
                user_keywords=keywords,
                industry=industry,
                target_audience=target_audience,
                max_opportunities=max_opportunities,
                enable_trend_analysis=enable_trend_analysis
            )

            if not discovery_result.get("success"):
                backlinking_logger.error(f"Opportunity discovery failed for campaign {campaign_id}: {discovery_result.get('error')}")
                raise BacklinkingError(f"Discovery failed: {discovery_result.get('error')}")

            opportunities = discovery_result.get("opportunities", [])
            stats = discovery_result.get("stats", {})

            # Convert database models to service models for backward compatibility
            service_opportunities = []
            for opp in opportunities:
                service_opportunity = BacklinkOpportunity(
                    url=opp.url,
                    title=opp.title or "",
                    description=opp.description or "",
                    contact_email=opp.contact_email,
                    contact_name=opp.contact_name,
                    domain_authority=opp.domain_authority,
                    content_topics=opp.primary_topics or [],
                    submission_guidelines=opp.submission_guidelines,
                    status=opp.status
                )
                service_opportunities.append(service_opportunity)

            log_campaign_action(campaign_id, "opportunity_discovery_completed", {
                "opportunities_found": len(service_opportunities),
                "execution_time": stats.get("execution_time_seconds", 0),
                "queries_executed": stats.get("total_queries", 0)
            })

            backlinking_logger.info(f"Discovered {len(service_opportunities)} opportunities for campaign {campaign_id}")

            # Return both service models and detailed stats
            return {
                "opportunities": service_opportunities,
                "stats": stats,
                "success": True
            }

        except Exception as e:
            backlinking_logger.error(f"Failed to discover opportunities for campaign {campaign_id}: {e}")
            log_campaign_action(campaign_id, "opportunity_discovery_failed", {"error": str(e)})
            raise handle_service_error(e)

    async def generate_outreach_emails(
        self,
        campaign_id: str,
        user_proposal: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate personalized outreach emails for campaign opportunities.

        Args:
            campaign_id: Campaign ID
            user_proposal: User's guest post proposal

        Returns:
            List of generated emails
        """
        try:
            # Get campaign opportunities
            opportunities = await self.campaign_service.get_campaign_opportunities(campaign_id)

            generated_emails = []

            for opportunity in opportunities:
                if opportunity.contact_email and opportunity.status == "discovered":
                    # Generate personalized email
                    email_content = await self._generate_personalized_email(
                        opportunity=opportunity,
                        user_proposal=user_proposal
                    )

                    # Save email to campaign
                    email_record = await self.campaign_service.save_generated_email(
                        campaign_id=campaign_id,
                        opportunity_id=opportunity.url,
                        email_content=email_content
                    )

                    generated_emails.append({
                        "opportunity": opportunity,
                        "email": email_content,
                        "record_id": email_record.id
                    })

            logger.info(f"Generated {len(generated_emails)} outreach emails for campaign {campaign_id}")
            return generated_emails

        except Exception as e:
            logger.error(f"Failed to generate outreach emails: {e}")
            raise

    async def send_outreach_emails(
        self,
        campaign_id: str,
        email_records: List[Dict[str, Any]],
        smtp_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Send outreach emails for a campaign.

        Args:
            campaign_id: Campaign ID
            email_records: Email records to send
            smtp_config: SMTP configuration

        Returns:
            Email sending results
        """
        try:
            results = await self.email_service.send_bulk_emails(
                email_records=email_records,
                smtp_config=smtp_config
            )

            # Update campaign with sending results
            await self.campaign_service.update_email_stats(
                campaign_id=campaign_id,
                sent_count=results.get("sent", 0),
                failed_count=results.get("failed", 0)
            )

            logger.info(f"Sent {results.get('sent', 0)} emails for campaign {campaign_id}")
            return results

        except Exception as e:
            logger.error(f"Failed to send outreach emails: {e}")
            raise

    async def check_responses(
        self,
        campaign_id: str,
        imap_config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Check for email responses to outreach emails.

        Args:
            campaign_id: Campaign ID
            imap_config: IMAP configuration

        Returns:
            List of email responses
        """
        try:
            responses = await self.email_service.check_responses(imap_config)

            # Process responses and update opportunities
            processed_responses = await self._process_responses(
                campaign_id=campaign_id,
                responses=responses
            )

            logger.info(f"Processed {len(processed_responses)} responses for campaign {campaign_id}")
            return processed_responses

    def _validate_campaign_data(self, name: str, keywords: List[str], user_proposal: Dict[str, Any]) -> None:
        """
        Validate campaign creation data.

        Args:
            name: Campaign name
            keywords: List of keywords
            user_proposal: User's proposal data

        Raises:
            CampaignValidationError: If validation fails
        """
        # Validate campaign name
        if not name or not name.strip():
            raise CampaignValidationError("name", name, "Campaign name cannot be empty")

        if len(name.strip()) < 3:
            raise CampaignValidationError("name", name, "Campaign name must be at least 3 characters")

        if len(name.strip()) > 100:
            raise CampaignValidationError("name", name, "Campaign name cannot exceed 100 characters")

        # Validate keywords
        if not keywords or len(keywords) == 0:
            raise CampaignValidationError("keywords", keywords, "At least one keyword is required")

        if len(keywords) > 10:
            raise CampaignValidationError("keywords", keywords, "Cannot have more than 10 keywords")

        for keyword in keywords:
            if not keyword or not keyword.strip():
                raise CampaignValidationError("keywords", keywords, "Keywords cannot be empty")
            if len(keyword.strip()) > 50:
                raise CampaignValidationError("keywords", keyword, "Individual keywords cannot exceed 50 characters")

        # Validate user proposal
        if not user_proposal:
            raise CampaignValidationError("user_proposal", user_proposal, "User proposal is required")

        required_fields = ["user_name", "user_email", "topic"]
        for field in required_fields:
            if field not in user_proposal or not user_proposal[field] or not user_proposal[field].strip():
                raise CampaignValidationError(f"user_proposal.{field}", user_proposal.get(field), f"{field} is required")

        # Validate email format
        import re
        email = user_proposal.get("user_email", "").strip()
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise CampaignValidationError("user_proposal.user_email", email, "Invalid email format")

        # Validate topic length
        topic = user_proposal.get("topic", "").strip()
        if len(topic) > 200:
            raise CampaignValidationError("user_proposal.topic", topic, "Topic cannot exceed 200 characters")

        except Exception as e:
            logger.error(f"Failed to check responses: {e}")
            raise

    async def get_campaign_analytics(self, campaign_id: str) -> Dict[str, Any]:
        """
        Get analytics for a backlinking campaign.

        Args:
            campaign_id: Campaign ID

        Returns:
            Campaign analytics data
        """
        try:
            return await self.campaign_service.get_campaign_analytics(campaign_id)
        except Exception as e:
            logger.error(f"Failed to get campaign analytics: {e}")
            raise

    def _generate_search_queries(self, keyword: str) -> List[str]:
        """Generate search queries for finding backlinking opportunities."""
        return [
            f"{keyword} + 'Guest Contributor'",
            f"{keyword} + 'Add Guest Post'",
            f"{keyword} + 'Guest Bloggers Wanted'",
            f"{keyword} + 'Write for Us'",
            f"{keyword} + 'Submit Guest Post'",
            f"{keyword} + 'Become a Guest Blogger'",
            f"{keyword} + 'guest post opportunities'",
            f"{keyword} + 'Submit article'",
        ]

    async def _generate_personalized_email(
        self,
        opportunity: BacklinkOpportunity,
        user_proposal: Dict[str, Any]
    ) -> str:
        """Generate a personalized outreach email using AI."""

        prompt = f"""
        Compose a professional and personalized outreach email for guest posting.

        Target Website: {opportunity.title}
        Website URL: {opportunity.url}
        Content Topics: {', '.join(opportunity.content_topics or [])}
        Contact Name: {opportunity.contact_name or 'Webmaster'}
        Proposed Topic: {user_proposal.get('topic', 'a guest post')}
        User Name: {user_proposal.get('user_name', 'Your Name')}
        User Email: {user_proposal.get('user_email', 'your_email@example.com')}

        Guidelines:
        1. Professional and personalized introduction
        2. Reference the website's content and show genuine interest
        3. Clearly state the proposed guest post topic
        4. Include a call to action
        5. Keep the email concise but compelling
        6. End with professional contact information

        Write the complete email including subject line.
        """

        return await self.llm_provider.generate_text(prompt)

    async def _process_responses(
        self,
        campaign_id: str,
        responses: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Process email responses and update opportunity status."""
        processed = []

        for response in responses:
            # Match response to opportunity based on email addresses
            opportunity = await self.campaign_service.find_opportunity_by_email(
                campaign_id=campaign_id,
                email=response.get("from_email")
            )

            if opportunity:
                # Update opportunity status
                await self.campaign_service.update_opportunity_status(
                    campaign_id=campaign_id,
                    opportunity_url=opportunity.url,
                    status="responded"
                )

                processed.append({
                    "opportunity": opportunity,
                    "response": response,
                    "processed_at": datetime.now()
                })

        return processed