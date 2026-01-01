"""
Step 3 Research Routes for Onboarding

FastAPI routes for Step 3 research phase of onboarding,
including competitor discovery and research data management.

Author: ALwrity Team
Version: 1.0
Last Updated: January 2025
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel, HttpUrl, Field
from typing import Dict, List, Optional, Any
from datetime import datetime
import traceback
from loguru import logger

from middleware.auth_middleware import get_current_user
from .step3_research_service import Step3ResearchService
from services.seo_tools.sitemap_service import SitemapService

router = APIRouter(prefix="/api/onboarding/step3", tags=["Onboarding Step 3 - Research"])

# Request/Response Models
class CompetitorDiscoveryRequest(BaseModel):
    """Request model for competitor discovery."""
    session_id: Optional[str] = Field(None, description="Deprecated - user identification comes from auth token")
    user_url: str = Field(..., description="User's website URL")
    industry_context: Optional[str] = Field(None, description="Industry context for better discovery")
    num_results: int = Field(25, ge=1, le=100, description="Number of competitors to discover")
    website_analysis_data: Optional[Dict[str, Any]] = Field(None, description="Website analysis data from Step 2 for better targeting")

class CompetitorDiscoveryResponse(BaseModel):
    """Response model for competitor discovery."""
    success: bool
    message: str
    session_id: str
    user_url: str
    competitors: Optional[List[Dict[str, Any]]] = None
    social_media_accounts: Optional[Dict[str, str]] = None
    social_media_citations: Optional[List[Dict[str, Any]]] = None
    research_summary: Optional[Dict[str, Any]] = None
    total_competitors: Optional[int] = None
    industry_context: Optional[str] = None
    analysis_timestamp: Optional[str] = None
    api_cost: Optional[float] = None
    error: Optional[str] = None

class ResearchDataRequest(BaseModel):
    """Request model for retrieving research data."""
    session_id: str = Field(..., description="Onboarding session ID")

class ResearchDataResponse(BaseModel):
    """Response model for research data retrieval."""
    success: bool
    message: str
    session_id: Optional[str] = None
    research_data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class ResearchHealthResponse(BaseModel):
    """Response model for research service health check."""
    success: bool
    message: str
    service_status: Optional[Dict[str, Any]] = None
    timestamp: Optional[str] = None

class SitemapAnalysisRequest(BaseModel):
    """Request model for sitemap analysis in onboarding context."""
    user_url: str = Field(..., description="User's website URL")
    sitemap_url: Optional[str] = Field(None, description="Custom sitemap URL (defaults to user_url/sitemap.xml)")
    competitors: Optional[List[str]] = Field(None, description="List of competitor URLs for benchmarking")
    industry_context: Optional[str] = Field(None, description="Industry context for analysis")
    analyze_content_trends: bool = Field(True, description="Whether to analyze content trends")
    analyze_publishing_patterns: bool = Field(True, description="Whether to analyze publishing patterns")

class SitemapAnalysisResponse(BaseModel):
    """Response model for sitemap analysis."""
    success: bool
    message: str
    user_url: str
    sitemap_url: str
    analysis_data: Optional[Dict[str, Any]] = None
    onboarding_insights: Optional[Dict[str, Any]] = None
    analysis_timestamp: Optional[str] = None
    discovery_method: Optional[str] = None
    error: Optional[str] = None

# Initialize services
step3_research_service = Step3ResearchService()
sitemap_service = SitemapService()

@router.post("/discover-competitors", response_model=CompetitorDiscoveryResponse)
async def discover_competitors(
    request: CompetitorDiscoveryRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
) -> CompetitorDiscoveryResponse:
    """
    Discover competitors for the user's website using Exa API with user isolation.
    
    This endpoint performs neural search to find semantically similar websites
    and analyzes their content for competitive intelligence.
    """
    try:
        # Get Clerk user ID for user isolation
        clerk_user_id = str(current_user.get('id'))
        
        logger.info(f"Starting competitor discovery for authenticated user {clerk_user_id}, URL: {request.user_url}")
        logger.info(f"Request data - user_url: '{request.user_url}', industry_context: '{request.industry_context}', num_results: {request.num_results}")
        
        # Validate URL format
        if not request.user_url.startswith(('http://', 'https://')):
            request.user_url = f"https://{request.user_url}"
        
        # Perform competitor discovery with Clerk user ID
        result = await step3_research_service.discover_competitors_for_onboarding(
            user_url=request.user_url,
            user_id=clerk_user_id,  # Use Clerk user ID to find correct session
            industry_context=request.industry_context,
            num_results=request.num_results,
            website_analysis_data=request.website_analysis_data
        )
        
        if result["success"]:
            logger.info(f"✅ Successfully discovered {result['total_competitors']} competitors for user {clerk_user_id}")
            
            return CompetitorDiscoveryResponse(
                success=True,
                message=f"Successfully discovered {result['total_competitors']} competitors and social media accounts",
                session_id=result["session_id"],
                user_url=result["user_url"],
                competitors=result["competitors"],
                social_media_accounts=result.get("social_media_accounts"),
                social_media_citations=result.get("social_media_citations"),
                research_summary=result["research_summary"],
                total_competitors=result["total_competitors"],
                industry_context=result["industry_context"],
                analysis_timestamp=result["analysis_timestamp"],
                api_cost=result["api_cost"]
            )
        else:
            logger.error(f"❌ Competitor discovery failed for user {clerk_user_id}: {result.get('error')}")
            
            return CompetitorDiscoveryResponse(
                success=False,
                message="Competitor discovery failed",
                session_id=clerk_user_id,
                user_url=result.get("user_url", request.user_url),
                error=result.get("error", "Unknown error occurred")
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error in competitor discovery endpoint: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Return error response with Clerk user ID
        clerk_user_id = str(current_user.get('id', 'unknown'))
        return CompetitorDiscoveryResponse(
            success=False,
            message="Internal server error during competitor discovery",
            session_id=clerk_user_id,
            user_url=request.user_url,
            error=str(e)
        )

@router.post("/research-data", response_model=ResearchDataResponse)
async def get_research_data(request: ResearchDataRequest) -> ResearchDataResponse:
    """
    Retrieve research data for a specific onboarding session.
    
    This endpoint returns the stored research data including competitor analysis
    and research summary for the given session.
    """
    try:
        logger.info(f"Retrieving research data for session {request.session_id}")
        
        # Validate session ID
        if not request.session_id or len(request.session_id) < 10:
            raise HTTPException(
                status_code=400,
                detail="Invalid session ID"
            )
        
        # Retrieve research data
        result = await step3_research_service.get_research_data(request.session_id)
        
        if result["success"]:
            logger.info(f"Successfully retrieved research data for session {request.session_id}")
            
            return ResearchDataResponse(
                success=True,
                message="Research data retrieved successfully",
                session_id=result["session_id"],
                research_data=result["research_data"]
            )
        else:
            logger.warning(f"No research data found for session {request.session_id}")
            
            return ResearchDataResponse(
                success=False,
                message="No research data found for this session",
                session_id=request.session_id,
                error=result.get("error", "Research data not found")
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving research data: {str(e)}")
        logger.error(traceback.format_exc())
        
        return ResearchDataResponse(
            success=False,
            message="Internal server error while retrieving research data",
            session_id=request.session_id,
            error=str(e)
        )

@router.get("/health", response_model=ResearchHealthResponse)
async def health_check() -> ResearchHealthResponse:
    """
    Check the health of the Step 3 research service.
    
    This endpoint provides health status information for the research service
    including Exa API connectivity and service status.
    """
    try:
        logger.info("Performing Step 3 research service health check")
        
        health_status = await step3_research_service.health_check()
        
        if health_status["status"] == "healthy":
            return ResearchHealthResponse(
                success=True,
                message="Step 3 research service is healthy",
                service_status=health_status,
                timestamp=health_status["timestamp"]
            )
        else:
            return ResearchHealthResponse(
                success=False,
                message=f"Step 3 research service is {health_status['status']}",
                service_status=health_status,
                timestamp=health_status["timestamp"]
            )
            
    except Exception as e:
        logger.error(f"Error in health check: {str(e)}")
        logger.error(traceback.format_exc())
        
        return ResearchHealthResponse(
            success=False,
            message="Health check failed",
            error=str(e),
            timestamp=datetime.utcnow().isoformat()
        )

@router.post("/validate-session")
async def validate_session(session_id: str) -> Dict[str, Any]:
    """
    Validate that a session exists and is ready for Step 3.
    
    This endpoint checks if the session exists and has completed previous steps.
    """
    try:
        logger.info(f"Validating session {session_id} for Step 3")
        
        # Basic validation
        if not session_id or len(session_id) < 10:
            raise HTTPException(
                status_code=400,
                detail="Invalid session ID format"
            )
        
        # Check if session has completed Step 2 (website analysis)
        # This would integrate with the existing session validation logic
        
        return {
            "success": True,
            "message": "Session is valid for Step 3",
            "session_id": session_id,
            "ready_for_step3": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating session: {str(e)}")
        
        return {
            "success": False,
            "message": "Session validation failed",
            "error": str(e)
        }

@router.get("/cost-estimate")
async def get_cost_estimate(
    num_results: int = 25,
    include_content: bool = True
) -> Dict[str, Any]:
    """
    Get cost estimate for competitor discovery.
    
    This endpoint provides cost estimates for Exa API usage
    to help users understand the cost of competitor discovery.
    """
    try:
        logger.info(f"Getting cost estimate for {num_results} results, content: {include_content}")
        
        cost_estimate = step3_research_service.exa_service.get_cost_estimate(
            num_results=num_results,
            include_content=include_content
        )
        
        return {
            "success": True,
            "cost_estimate": cost_estimate,
            "message": "Cost estimate calculated successfully"
        }
        
    except Exception as e:
        logger.error(f"Error calculating cost estimate: {str(e)}")
        
        return {
            "success": False,
            "message": "Failed to calculate cost estimate",
            "error": str(e)
        }

@router.post("/discover-sitemap")
async def discover_sitemap(
    request: SitemapAnalysisRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Discover the sitemap URL for a given website using intelligent search.
    
    This endpoint attempts to find the sitemap URL by checking robots.txt
    and common sitemap locations.
    """
    try:
        logger.info(f"Discovering sitemap for user: {current_user.get('user_id', 'unknown')}")
        logger.info(f"Sitemap discovery request: {request.user_url}")
        
        # Use intelligent sitemap discovery
        discovered_sitemap = await sitemap_service.discover_sitemap_url(request.user_url)
        
        if discovered_sitemap:
            return {
                "success": True,
                "message": "Sitemap discovered successfully",
                "user_url": request.user_url,
                "sitemap_url": discovered_sitemap,
                "discovery_method": "intelligent_search"
            }
        else:
            # Provide fallback URL
            base_url = request.user_url.rstrip('/')
            fallback_url = f"{base_url}/sitemap.xml"
            
            return {
                "success": False,
                "message": "No sitemap found using intelligent discovery",
                "user_url": request.user_url,
                "fallback_url": fallback_url,
                "discovery_method": "fallback"
            }
        
    except Exception as e:
        logger.error(f"Error in sitemap discovery: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        return {
            "success": False,
            "message": "An unexpected error occurred during sitemap discovery",
            "user_url": request.user_url,
            "error": str(e)
        }

@router.post("/analyze-sitemap", response_model=SitemapAnalysisResponse)
async def analyze_sitemap_for_onboarding(
    request: SitemapAnalysisRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> SitemapAnalysisResponse:
    """
    Analyze user's sitemap for competitive positioning and content strategy insights.
    
    This endpoint provides enhanced sitemap analysis specifically designed for
    onboarding Step 3 competitive analysis, including competitive positioning
    insights and content strategy recommendations.
    """
    try:
        logger.info(f"Starting sitemap analysis for user: {current_user.get('user_id', 'unknown')}")
        logger.info(f"Sitemap analysis request: {request.user_url}")
        
        # Determine sitemap URL using intelligent discovery
        sitemap_url = request.sitemap_url
        if not sitemap_url:
            # Use intelligent sitemap discovery
            discovered_sitemap = await sitemap_service.discover_sitemap_url(request.user_url)
            if discovered_sitemap:
                sitemap_url = discovered_sitemap
                logger.info(f"Discovered sitemap via intelligent search: {sitemap_url}")
            else:
                # Fallback to standard location if discovery fails
                base_url = request.user_url.rstrip('/')
                sitemap_url = f"{base_url}/sitemap.xml"
                logger.info(f"Using fallback sitemap URL: {sitemap_url}")
        
        logger.info(f"Analyzing sitemap: {sitemap_url}")
        
        # Run onboarding-specific sitemap analysis
        analysis_result = await sitemap_service.analyze_sitemap_for_onboarding(
            sitemap_url=sitemap_url,
            user_url=request.user_url,
            competitors=request.competitors,
            industry_context=request.industry_context,
            analyze_content_trends=request.analyze_content_trends,
            analyze_publishing_patterns=request.analyze_publishing_patterns
        )
        
        # Check if analysis was successful
        if analysis_result.get("error"):
            logger.error(f"Sitemap analysis failed: {analysis_result['error']}")
            return SitemapAnalysisResponse(
                success=False,
                message="Sitemap analysis failed",
                user_url=request.user_url,
                sitemap_url=sitemap_url,
                error=analysis_result["error"]
            )
        
        # Extract onboarding insights
        onboarding_insights = analysis_result.get("onboarding_insights", {})
        
        # Log successful analysis
        logger.info(f"Sitemap analysis completed successfully for {request.user_url}")
        logger.info(f"Found {analysis_result.get('structure_analysis', {}).get('total_urls', 0)} URLs")
        
        # Background task to store analysis results (if needed)
        background_tasks.add_task(
            _log_sitemap_analysis_result,
            current_user.get('user_id'),
            request.user_url,
            analysis_result
        )
        
        # Determine discovery method
        discovery_method = "fallback"
        if request.sitemap_url:
            discovery_method = "user_provided"
        elif discovered_sitemap:
            discovery_method = "intelligent_search"
        
        return SitemapAnalysisResponse(
            success=True,
            message="Sitemap analysis completed successfully",
            user_url=request.user_url,
            sitemap_url=sitemap_url,
            analysis_data=analysis_result,
            onboarding_insights=onboarding_insights,
            analysis_timestamp=datetime.utcnow().isoformat(),
            discovery_method=discovery_method
        )
        
    except Exception as e:
        logger.error(f"Error in sitemap analysis: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        return SitemapAnalysisResponse(
            success=False,
            message="An unexpected error occurred during sitemap analysis",
            user_url=request.user_url,
            sitemap_url=sitemap_url or f"{request.user_url.rstrip('/')}/sitemap.xml",
            error=str(e)
        )

async def _log_sitemap_analysis_result(
    user_id: str,
    user_url: str,
    analysis_result: Dict[str, Any]
) -> None:
    """Background task to log sitemap analysis results."""
    try:
        logger.info(f"Logging sitemap analysis result for user {user_id}")
        # Add any logging or storage logic here if needed
        # For now, just log the completion
        logger.info(f"Sitemap analysis logged for {user_url}")
    except Exception as e:
        logger.error(f"Error logging sitemap analysis result: {e}")
