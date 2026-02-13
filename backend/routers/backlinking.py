"""API endpoints for AI Backlinking feature."""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime

from services.backlinking import (
    BacklinkingService,
    EmailAutomationService,
    CampaignManagementService
)
from services.backlinking.models import (
    CreateCampaignRequestModel,
    EmailConfigModel,
    validate_api_input
)
from middleware.auth_middleware import get_current_user
from utils.logger_utils import get_service_logger


logger = get_service_logger("api.backlinking")
router = APIRouter(prefix="/api/backlinking", tags=["backlinking"])


def _require_user_id(current_user: Dict[str, Any], operation: str) -> str:
    """Ensure user_id is available for protected operations."""
    user_id = current_user.get("sub") or current_user.get("user_id") or current_user.get("id")
    if not user_id:
        logger.error(
            "[Backlinking] ❌ Missing user_id for %s operation - blocking request",
            operation,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authenticated user required for backlinking operations.",
        )
    return str(user_id)


# ====================
# CAMPAIGN MANAGEMENT
# ====================

# Using Pydantic models from models.py instead of inline definitions


class CampaignResponse(BaseModel):
    """Response model for campaign data."""
    campaign_id: str
    user_id: str
    name: str
    keywords: List[str]
    status: str
    created_at: datetime
    email_stats: Dict[str, int]


@router.post("/campaigns", response_model=CampaignResponse)
async def create_campaign(
    request_data: Dict[str, Any],
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> CampaignResponse:
    """
    Create a new backlinking campaign.

    This endpoint initiates a new backlinking campaign with the specified
    keywords and user proposal. The campaign will automatically start
    discovering opportunities in the background.
    """
    user_id = _require_user_id(current_user, "create_campaign")

    try:
        # Validate input data using Pydantic model
        validated_request = validate_api_input(request_data, CreateCampaignRequestModel)

        service = BacklinkingService()
        campaign = await service.create_campaign(
            user_id=int(user_id),
            campaign_name=validated_request.name,
            keywords=validated_request.keywords,
            user_proposal=validated_request.user_proposal.dict()
        )

        # Start opportunity discovery in background
        background_tasks.add_task(
            service.discover_opportunities,
            campaign.campaign_id,
            validated_request.keywords
        )

        return CampaignResponse(
            campaign_id=campaign.campaign_id,
            user_id=str(campaign.user_id),
            name=campaign.name,
            keywords=campaign.keywords,
            status=campaign.status,
            created_at=campaign.created_at,
            email_stats=campaign.email_stats
        )

    except Exception as e:
        logger.error(f"Failed to create campaign: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create backlinking campaign"
        )


@router.get("/campaigns", response_model=List[CampaignResponse])
async def get_user_campaigns(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> List[CampaignResponse]:
    """Get all campaigns for the current user."""
    user_id = _require_user_id(current_user, "get_campaigns")

    try:
        service = CampaignManagementService()
        campaigns = await service.get_user_campaigns(int(user_id))

        return [
            CampaignResponse(
                campaign_id=c.campaign_id,
                user_id=str(c.user_id),
                name=c.name,
                keywords=c.keywords,
                status=c.status,
                created_at=c.created_at,
                email_stats=c.email_stats
            )
            for c in campaigns
        ]

    except Exception as e:
        logger.error(f"Failed to get user campaigns: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve campaigns"
        )


@router.get("/campaigns/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> CampaignResponse:
    """Get a specific campaign by ID."""
    user_id = _require_user_id(current_user, "get_campaign")

    try:
        service = CampaignManagementService()
        campaigns = await service.get_user_campaigns(int(user_id))
        campaign = next((c for c in campaigns if c.campaign_id == campaign_id), None)

        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )

        return CampaignResponse(
            campaign_id=campaign.campaign_id,
            user_id=str(campaign.user_id),
            name=campaign.name,
            keywords=campaign.keywords,
            status=campaign.status,
            created_at=campaign.created_at,
            email_stats=campaign.email_stats
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get campaign {campaign_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve campaign"
        )


# ====================
# OPPORTUNITY DISCOVERY
# ====================

class OpportunityResponse(BaseModel):
    """Response model for backlinking opportunity."""
    url: str
    title: str
    description: str
    contact_email: Optional[EmailStr]
    contact_name: Optional[str]
    domain_authority: Optional[int]
    content_topics: List[str]
    submission_guidelines: Optional[str]
    status: str


@router.post("/campaigns/{campaign_id}/discover", response_model=List[OpportunityResponse])
async def discover_opportunities(
    campaign_id: str,
    keywords: List[str],
    enable_trend_analysis: bool = False,
    enable_enhanced_analysis: bool = True,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> List[OpportunityResponse]:
    """
    Discover backlinking opportunities for a campaign.

    This endpoint searches for websites that accept guest posts based on
    the provided keywords and adds them to the campaign.

    Args:
        campaign_id: The ID of the campaign to discover opportunities for
        keywords: List of keywords to search for guest post opportunities
        enable_trend_analysis: Whether to include Google Trends analysis for enhanced prospecting
        enable_enhanced_analysis: Whether to use comprehensive website analysis for prospects
    """
    user_id = _require_user_id(current_user, "discover_opportunities")

    # Preflight validations
    if not campaign_id or not isinstance(campaign_id, str):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Valid campaign_id is required."
        )

    if not keywords or not isinstance(keywords, list) or len(keywords) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one keyword is required."
        )

    if len(keywords) > 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 50 keywords allowed."
        )

    # Validate keyword format
    for keyword in keywords:
        if not isinstance(keyword, str) or len(keyword.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="All keywords must be non-empty strings."
            )
        if len(keyword) > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Keywords must be 100 characters or less."
            )

    try:
        service = BacklinkingService()
        opportunities = await service.discover_opportunities(
            campaign_id, keywords, enable_trend_analysis=enable_trend_analysis,
            enable_enhanced_analysis=enable_enhanced_analysis, user_id=user_id
        )

        return [
            OpportunityResponse(
                url=opp.url,
                title=opp.title,
                description=opp.description,
                contact_email=opp.contact_email,
                contact_name=opp.contact_name,
                domain_authority=opp.domain_authority,
                content_topics=opp.content_topics or [],
                submission_guidelines=opp.submission_guidelines,
                status=opp.status
            )
            for opp in opportunities
        ]

    except Exception as e:
        logger.error(f"Failed to discover opportunities for campaign {campaign_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to discover opportunities"
        )


@router.get("/campaigns/{campaign_id}/opportunities", response_model=List[OpportunityResponse])
async def get_campaign_opportunities(
    campaign_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> List[OpportunityResponse]:
    """Get all opportunities for a campaign."""
    user_id = _require_user_id(current_user, "get_opportunities")

    try:
        service = CampaignManagementService()
        opportunities = await service.get_campaign_opportunities(campaign_id)

        return [
            OpportunityResponse(
                url=opp.url,
                title=opp.title,
                description=opp.description,
                contact_email=opp.contact_email,
                contact_name=opp.contact_name,
                domain_authority=opp.domain_authority,
                content_topics=opp.content_topics or [],
                submission_guidelines=opp.submission_guidelines,
                status=opp.status
            )
            for opp in opportunities
        ]

    except Exception as e:
        logger.error(f"Failed to get opportunities for campaign {campaign_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve opportunities"
        )


# ====================
# EMAIL OPERATIONS
# ====================

class GenerateEmailsRequest(BaseModel):
    """Request model for generating outreach emails."""
    user_proposal: Dict[str, Any] = Field(..., description="User's guest post proposal")


class EmailGenerationResponse(BaseModel):
    """Response model for generated emails."""
    opportunity: OpportunityResponse
    email_subject: str
    email_body: str
    record_id: int


class EmailConfig(BaseModel):
    """Email configuration model."""
    server: str = Field(..., description="SMTP/IMAP server")
    port: int = Field(..., description="Server port")
    user: EmailStr = Field(..., description="Email username")
    password: str = Field(..., description="Email password")


@router.post("/campaigns/{campaign_id}/generate-emails", response_model=List[EmailGenerationResponse])
async def generate_outreach_emails(
    campaign_id: str,
    request: GenerateEmailsRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> List[EmailGenerationResponse]:
    """
    Generate personalized outreach emails for campaign opportunities.

    This endpoint uses AI to create customized emails for each discovered
    opportunity based on the website content and user proposal.
    """
    user_id = _require_user_id(current_user, "generate_emails")

    # Preflight validations
    if not campaign_id or not isinstance(campaign_id, str):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Valid campaign_id is required."
        )

    if not request.user_proposal or not isinstance(request.user_proposal, dict):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Valid user_proposal is required."
        )

    try:
        service = BacklinkingService()
        generated_emails = await service.generate_outreach_emails(
            campaign_id=campaign_id,
            user_proposal=request.user_proposal,
            user_id=user_id
        )

        return [
            EmailGenerationResponse(
                opportunity=OpportunityResponse(
                    url=email["opportunity"].url,
                    title=email["opportunity"].title,
                    description=email["opportunity"].description,
                    contact_email=email["opportunity"].contact_email,
                    contact_name=email["opportunity"].contact_name,
                    domain_authority=email["opportunity"].domain_authority,
                    content_topics=email["opportunity"].content_topics or [],
                    submission_guidelines=email["opportunity"].submission_guidelines,
                    status=email["opportunity"].status
                ),
                email_subject=email["email"].split('\n', 1)[0].replace('Subject:', '').strip(),
                email_body=email["email"],
                record_id=email["record_id"]
            )
            for email in generated_emails
        ]

    except Exception as e:
        logger.error(f"Failed to generate emails for campaign {campaign_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate outreach emails"
        )


@router.post("/campaigns/{campaign_id}/send-emails")
async def send_outreach_emails(
    campaign_id: str,
    email_records: List[Dict[str, Any]],
    smtp_config: EmailConfig,
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Send outreach emails for a campaign.

    This endpoint sends the generated emails using the provided SMTP configuration.
    The operation runs in the background for better performance.
    """
    user_id = _require_user_id(current_user, "send_emails")

    try:
        service = BacklinkingService()

        # Start email sending in background
        background_tasks.add_task(
            service.send_outreach_emails,
            campaign_id,
            email_records,
            smtp_config.dict()
        )

        return {
            "message": "Email sending started in background",
            "campaign_id": campaign_id,
            "emails_queued": len(email_records)
        }

    except Exception as e:
        logger.error(f"Failed to queue emails for campaign {campaign_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to queue emails for sending"
        )


@router.post("/campaigns/{campaign_id}/check-responses")
async def check_email_responses(
    campaign_id: str,
    imap_config: EmailConfig,
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Check for email responses to outreach emails.

    This endpoint connects to the IMAP server to check for replies
    to previously sent outreach emails.
    """
    user_id = _require_user_id(current_user, "check_responses")

    try:
        service = BacklinkingService()

        # Start response checking in background
        background_tasks.add_task(
            service.check_responses,
            campaign_id,
            imap_config.dict()
        )

        return {
            "message": "Response checking started in background",
            "campaign_id": campaign_id
        }

    except Exception as e:
        logger.error(f"Failed to check responses for campaign {campaign_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check email responses"
        )


# ====================
# ANALYTICS & REPORTING
# ====================

class CampaignAnalyticsResponse(BaseModel):
    """Response model for campaign analytics."""
    total_opportunities: int
    opportunities_by_status: Dict[str, int]
    email_stats: Dict[str, Any]
    top_performing_opportunities: List[Dict[str, Any]]
    campaign_progress: Dict[str, bool]


@router.get("/campaigns/{campaign_id}/analytics", response_model=CampaignAnalyticsResponse)
async def get_campaign_analytics(
    campaign_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> CampaignAnalyticsResponse:
    """Get analytics and performance metrics for a campaign."""
    user_id = _require_user_id(current_user, "get_analytics")

    try:
        service = BacklinkingService()
        analytics = await service.get_campaign_analytics(campaign_id)

        return CampaignAnalyticsResponse(**analytics)

    except Exception as e:
        logger.error(f"Failed to get analytics for campaign {campaign_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve campaign analytics"
        )


# ====================
# CAMPAIGN MANAGEMENT
# ====================

@router.post("/campaigns/{campaign_id}/pause")
async def pause_campaign(
    campaign_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, str]:
    """Pause a backlinking campaign."""
    user_id = _require_user_id(current_user, "pause_campaign")

    try:
        service = CampaignManagementService()
        await service.pause_campaign(campaign_id)

        return {"message": f"Campaign {campaign_id} paused successfully"}

    except Exception as e:
        logger.error(f"Failed to pause campaign {campaign_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to pause campaign"
        )


@router.post("/campaigns/{campaign_id}/resume")
async def resume_campaign(
    campaign_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, str]:
    """Resume a paused backlinking campaign."""
    user_id = _require_user_id(current_user, "resume_campaign")

    try:
        service = CampaignManagementService()
        await service.resume_campaign(campaign_id)

        return {"message": f"Campaign {campaign_id} resumed successfully"}

    except Exception as e:
        logger.error(f"Failed to resume campaign {campaign_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to resume campaign"
        )


@router.delete("/campaigns/{campaign_id}")
async def delete_campaign(
    campaign_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, str]:
    """Delete a backlinking campaign and all associated data."""
    user_id = _require_user_id(current_user, "delete_campaign")

    try:
        service = CampaignManagementService()
        await service.delete_campaign(campaign_id)

        return {"message": f"Campaign {campaign_id} deleted successfully"}

    except Exception as e:
        logger.error(f"Failed to delete campaign {campaign_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete campaign"
        )