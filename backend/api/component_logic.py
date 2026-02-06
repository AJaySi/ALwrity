"""Component Logic API endpoints for ALwrity Backend.

This module provides API endpoints for the extracted component logic services.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from utils.logging import get_logger
logger = get_logger("api_component_logic", migration_mode=True)
from typing import Dict, Any
from datetime import datetime
import hashlib

from models.component_logic import (
    UserInfoRequest, UserInfoResponse,
    ResearchPreferencesRequest, ResearchPreferencesResponse,
    ResearchRequest, ResearchResponse,
    ContentStyleRequest, ContentStyleResponse,
    BrandVoiceRequest, BrandVoiceResponse,
    PersonalizationSettingsRequest, PersonalizationSettingsResponse,
    ResearchTopicRequest, ResearchResultResponse,
    StyleAnalysisRequest, StyleAnalysisResponse,
    WebCrawlRequest, WebCrawlResponse,
    StyleDetectionRequest, StyleDetectionResponse
)
from models.onboarding import OnboardingSession

from services.component_logic.ai_research_logic import AIResearchLogic
from services.component_logic.personalization_logic import PersonalizationLogic
from services.component_logic.research_utilities import ResearchUtilities
from services.component_logic.style_detection_logic import StyleDetectionLogic
from services.component_logic.web_crawler_logic import WebCrawlerLogic
from services.research_preferences_service import ResearchPreferencesService
from services.database import get_db
from services.onboarding import OnboardingDatabaseService

# Import authentication for user isolation
from middleware.auth_middleware import get_current_user

# Import the website analysis service
from services.website_analysis_service import WebsiteAnalysisService
from services.database import get_db_session

# Initialize services
ai_research_logic = AIResearchLogic()
personalization_logic = PersonalizationLogic()
research_utilities = ResearchUtilities()

# Create router
router = APIRouter(prefix="/api/onboarding", tags=["component_logic"])

# Utility function for consistent user ID to integer conversion
def clerk_user_id_to_int(user_id: str) -> int:
    """
    Convert Clerk user ID to consistent integer for database session_id.
    Uses SHA256 hashing for deterministic, consistent results across all requests.
    
    Args:
        user_id: Clerk user ID (e.g., 'user_2qA6V8bFFnhPRGp8JYxP4YTJtHl')
    
    Returns:
        int: Deterministic integer derived from user ID
    """
    # Use SHA256 for consistent hashing (unlike Python's hash() which varies per process)
    user_id_hash = hashlib.sha256(user_id.encode()).hexdigest()
    # Take first 8 characters of hex and convert to int, mod to fit in INT range
    return int(user_id_hash[:8], 16) % 2147483647


def _get_onboarding_session(db_session: Session, user_id: str, create_if_missing: bool = False) -> Optional[OnboardingSession]:
    """Fetch onboarding session for a user, optionally creating one."""
    db_service = OnboardingDatabaseService(db_session)
    session = db_service.get_session_by_user(user_id, db_session)
    if not session and create_if_missing:
        session = db_service.get_or_create_session(user_id, db_session)
    return session

# AI Research Endpoints

@router.post("/ai-research/validate-user", response_model=UserInfoResponse)
async def validate_user_info(request: UserInfoRequest):
    """Validate user information for AI research configuration."""
    try:
        logger.info("Validating user information via API")
        
        user_data = {
            'full_name': request.full_name,
            'email': request.email,
            'company': request.company,
            'role': request.role
        }
        
        result = ai_research_logic.validate_user_info(user_data)
        
        return UserInfoResponse(
            valid=result['valid'],
            user_info=result.get('user_info'),
            errors=result.get('errors', [])
        )
        
    except Exception as e:
        logger.error(f"Error in validate_user_info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ai-research/configure-preferences", response_model=ResearchPreferencesResponse)
async def configure_research_preferences(
    request: ResearchPreferencesRequest, 
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Configure research preferences for AI research and save to database with user isolation."""
    try:
        user_id = str(current_user.get('id'))
        logger.info(f"Configuring research preferences for user: {user_id}")
        
        # Validate preferences using business logic
        preferences = {
            'research_depth': request.research_depth,
            'content_types': request.content_types,
            'auto_research': request.auto_research,
            'factual_content': request.factual_content
        }
        
        result = ai_research_logic.configure_research_preferences(preferences)
        
        if result['valid']:
            try:
                # Save to database
                preferences_service = ResearchPreferencesService(db)
                session = _get_onboarding_session(db, user_id, create_if_missing=True)
                if not session:
                    logger.warning(f"Could not resolve onboarding session for user {user_id}")
                else:
                    # Save preferences with onboarding session ID
                    preferences_id = preferences_service.save_preferences_with_style_data(session.id, preferences)
                
                if preferences_id:
                    logger.info(f"Research preferences saved to database with ID: {preferences_id}")
                    result['preferences']['id'] = preferences_id
                else:
                    logger.warning("Failed to save research preferences to database")
            except Exception as db_error:
                logger.error(f"Database error: {db_error}")
                # Don't fail the request if database save fails, just log it
                result['preferences']['database_save_failed'] = True
        
        return ResearchPreferencesResponse(
            valid=result['valid'],
            preferences=result.get('preferences'),
            errors=result.get('errors', [])
        )
        
    except Exception as e:
        logger.error(f"Error in configure_research_preferences: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ai-research/process-research", response_model=ResearchResponse)
async def process_research_request(request: ResearchRequest):
    """Process research request with configured preferences."""
    try:
        logger.info("Processing research request via API")
        
        preferences = {
            'research_depth': request.preferences.research_depth,
            'content_types': request.preferences.content_types,
            'auto_research': request.preferences.auto_research
        }
        
        result = ai_research_logic.process_research_request(request.topic, preferences)
        
        return ResearchResponse(
            success=result['success'],
            topic=result['topic'],
            results=result.get('results'),
            error=result.get('error')
        )
        
    except Exception as e:
        logger.error(f"Error in process_research_request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ai-research/configuration-options")
async def get_research_configuration_options():
    """Get available configuration options for AI research."""
    try:
        logger.info("Getting research configuration options via API")
        
        options = ai_research_logic.get_research_configuration_options()
        
        return {
            'success': True,
            'options': options
        }
        
    except Exception as e:
        logger.error(f"Error in get_research_configuration_options: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Personalization Endpoints

@router.post("/personalization/validate-style", response_model=ContentStyleResponse)
async def validate_content_style(request: ContentStyleRequest):
    """Validate content style configuration."""
    try:
        logger.info("Validating content style via API")
        
        style_data = {
            'writing_style': request.writing_style,
            'tone': request.tone,
            'content_length': request.content_length
        }
        
        result = personalization_logic.validate_content_style(style_data)
        
        return ContentStyleResponse(
            valid=result['valid'],
            style_config=result.get('style_config'),
            errors=result.get('errors', [])
        )
        
    except Exception as e:
        logger.error(f"Error in validate_content_style: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/personalization/configure-brand", response_model=BrandVoiceResponse)
async def configure_brand_voice(request: BrandVoiceRequest):
    """Configure brand voice settings."""
    try:
        logger.info("Configuring brand voice via API")
        
        brand_data = {
            'personality_traits': request.personality_traits,
            'voice_description': request.voice_description,
            'keywords': request.keywords
        }
        
        result = personalization_logic.configure_brand_voice(brand_data)
        
        return BrandVoiceResponse(
            valid=result['valid'],
            brand_config=result.get('brand_config'),
            errors=result.get('errors', [])
        )
        
    except Exception as e:
        logger.error(f"Error in configure_brand_voice: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/personalization/process-settings", response_model=PersonalizationSettingsResponse)
async def process_personalization_settings(request: PersonalizationSettingsRequest):
    """Process complete personalization settings."""
    try:
        logger.info("Processing personalization settings via API")
        
        settings = {
            'content_style': {
                'writing_style': request.content_style.writing_style,
                'tone': request.content_style.tone,
                'content_length': request.content_style.content_length
            },
            'brand_voice': {
                'personality_traits': request.brand_voice.personality_traits,
                'voice_description': request.brand_voice.voice_description,
                'keywords': request.brand_voice.keywords
            },
            'advanced_settings': {
                'seo_optimization': request.advanced_settings.seo_optimization,
                'readability_level': request.advanced_settings.readability_level,
                'content_structure': request.advanced_settings.content_structure
            }
        }
        
        result = personalization_logic.process_personalization_settings(settings)
        
        return PersonalizationSettingsResponse(
            valid=result['valid'],
            settings=result.get('settings'),
            errors=result.get('errors', [])
        )
        
    except Exception as e:
        logger.error(f"Error in process_personalization_settings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/personalization/configuration-options")
async def get_personalization_configuration_options():
    """Get available configuration options for personalization."""
    try:
        logger.info("Getting personalization configuration options via API")
        
        options = personalization_logic.get_personalization_configuration_options()
        
        return {
            'success': True,
            'options': options
        }
        
    except Exception as e:
        logger.error(f"Error in get_personalization_configuration_options: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/personalization/generate-guidelines")
async def generate_content_guidelines(settings: Dict[str, Any]):
    """Generate content guidelines from personalization settings."""
    try:
        logger.info("Generating content guidelines via API")
        
        result = personalization_logic.generate_content_guidelines(settings)
        
        return result
        
    except Exception as e:
        logger.error(f"Error in generate_content_guidelines: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Research Utilities Endpoints

@router.post("/research/process-topic", response_model=ResearchResultResponse)
async def process_research_topic(request: ResearchTopicRequest):
    """Process research for a specific topic."""
    try:
        logger.info("Processing research topic via API")
        
        result = await research_utilities.research_topic(request.topic, request.api_keys)
        
        return ResearchResultResponse(
            success=result['success'],
            topic=result['topic'],
            data=result.get('results'),
            error=result.get('error'),
            metadata=result.get('metadata')
        )
        
    except Exception as e:
        logger.error(f"Error in process_research_topic: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/research/process-results")
async def process_research_results(results: Dict[str, Any]):
    """Process and format research results."""
    try:
        logger.info("Processing research results via API")
        
        result = research_utilities.process_research_results(results)
        
        return result
        
    except Exception as e:
        logger.error(f"Error in process_research_results: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/research/validate-request")
async def validate_research_request(topic: str, api_keys: Dict[str, str]):
    """Validate a research request before processing."""
    try:
        logger.info("Validating research request via API")
        
        result = research_utilities.validate_research_request(topic, api_keys)
        
        return result
        
    except Exception as e:
        logger.error(f"Error in validate_research_request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/research/providers-info")
async def get_research_providers_info():
    """Get information about available research providers."""
    try:
        logger.info("Getting research providers info via API")
        
        result = research_utilities.get_research_providers_info()
        
        return {
            'success': True,
            'providers_info': result
        }
        
    except Exception as e:
        logger.error(f"Error in get_research_providers_info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/research/generate-report")
async def generate_research_report(results: Dict[str, Any]):
    """Generate a formatted research report from processed results."""
    try:
        logger.info("Generating research report via API")
        
        result = research_utilities.generate_research_report(results)
        
        return result
        
    except Exception as e:
        logger.error(f"Error in generate_research_report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 

# Style Detection Endpoints
@router.post("/style-detection/analyze", response_model=StyleAnalysisResponse)
async def analyze_content_style(request: StyleAnalysisRequest):
    """Analyze content style using AI."""
    try:
        logger.info("[analyze_content_style] Starting style analysis")
        
        # Initialize style detection logic
        style_logic = StyleDetectionLogic()
        
        # Validate request
        validation = style_logic.validate_style_analysis_request(request.dict())
        if not validation['valid']:
            return StyleAnalysisResponse(
                success=False,
                error=f"Validation failed: {', '.join(validation['errors'])}",
                timestamp=datetime.now().isoformat()
            )
        
        # Perform style analysis
        if request.analysis_type == "comprehensive":
            result = style_logic.analyze_content_style(validation['content'])
        elif request.analysis_type == "patterns":
            result = style_logic.analyze_style_patterns(validation['content'])
        else:
            return StyleAnalysisResponse(
                success=False,
                error="Invalid analysis type",
                timestamp=datetime.now().isoformat()
            )
        
        if not result['success']:
            return StyleAnalysisResponse(
                success=False,
                error=result.get('error', 'Analysis failed'),
                timestamp=datetime.now().isoformat()
            )
        
        # Return appropriate response based on analysis type
        if request.analysis_type == "comprehensive":
            return StyleAnalysisResponse(
                success=True,
                analysis=result['analysis'],
                timestamp=result['timestamp']
            )
        elif request.analysis_type == "patterns":
            return StyleAnalysisResponse(
                success=True,
                patterns=result['patterns'],
                timestamp=result['timestamp']
            )
        
    except Exception as e:
        logger.error(f"[analyze_content_style] Error: {str(e)}")
        return StyleAnalysisResponse(
            success=False,
            error=f"Analysis error: {str(e)}",
            timestamp=datetime.now().isoformat()
        )

@router.post("/style-detection/crawl", response_model=WebCrawlResponse)
async def crawl_website_content(request: WebCrawlRequest):
    """Crawl website content for style analysis."""
    try:
        logger.info("[crawl_website_content] Starting web crawl")
        
        # Initialize web crawler logic
        crawler_logic = WebCrawlerLogic()
        
        # Validate request
        validation = crawler_logic.validate_crawl_request(request.dict())
        if not validation['valid']:
            return WebCrawlResponse(
                success=False,
                error=f"Validation failed: {', '.join(validation['errors'])}",
                timestamp=datetime.now().isoformat()
            )
        
        # Perform crawling
        if validation['url']:
            # Crawl website
            result = await crawler_logic.crawl_website(validation['url'])
        else:
            # Process text sample
            result = crawler_logic.extract_content_from_text(validation['text_sample'])
        
        if not result['success']:
            return WebCrawlResponse(
                success=False,
                error=result.get('error', 'Crawling failed'),
                timestamp=datetime.now().isoformat()
            )
        
        # Calculate metrics
        metrics = crawler_logic.get_crawl_metrics(result['content'])
        
        return WebCrawlResponse(
            success=True,
            content=result['content'],
            metrics=metrics.get('metrics') if metrics['success'] else None,
            timestamp=result['timestamp']
        )
        
    except Exception as e:
        logger.error(f"[crawl_website_content] Error: {str(e)}")
        return WebCrawlResponse(
            success=False,
            error=f"Crawling error: {str(e)}",
            timestamp=datetime.now().isoformat()
        )

@router.post("/style-detection/complete", response_model=StyleDetectionResponse)
async def complete_style_detection(
    request: StyleDetectionRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Complete style detection workflow (crawl + analyze + guidelines) with database storage and user isolation."""
    try:
        user_id = str(current_user.get('id'))
        logger.info(f"[complete_style_detection] Starting complete style detection for user: {user_id}")
        
        # Get database session
        db_session = get_db_session()
        if not db_session:
            return StyleDetectionResponse(
                success=False,
                error="Database connection not available",
                timestamp=datetime.now().isoformat()
            )
        
        # Initialize services
        crawler_logic = WebCrawlerLogic()
        style_logic = StyleDetectionLogic()
        analysis_service = WebsiteAnalysisService(db_session)
        
        session = _get_onboarding_session(db_session, user_id, create_if_missing=True)
        if not session:
            return StyleDetectionResponse(
                success=False,
                error="Onboarding session not available",
                timestamp=datetime.now().isoformat()
            )
        
        # Check for existing analysis if URL is provided
        existing_analysis = None
        if request.url:
            existing_analysis = analysis_service.check_existing_analysis(session.id, request.url)
        
        # Step 1: Crawl content
        if request.url:
            crawl_result = await crawler_logic.crawl_website(request.url)
        elif request.text_sample:
            crawl_result = crawler_logic.extract_content_from_text(request.text_sample)
        else:
            return StyleDetectionResponse(
                success=False,
                error="Either URL or text sample is required",
                timestamp=datetime.now().isoformat()
            )
        
        if not crawl_result['success']:
            # Save error analysis
            analysis_service.save_error_analysis(session.id, request.url or "text_sample", 
                                              crawl_result.get('error', 'Crawling failed'))
            return StyleDetectionResponse(
                success=False,
                error=f"Crawling failed: {crawl_result.get('error', 'Unknown error')}",
                timestamp=datetime.now().isoformat()
            )
        
        # Step 2-4: Parallelize AI API calls for performance (3 calls → 1 parallel batch)
        import asyncio
        from functools import partial
        
        # Prepare parallel tasks
        logger.info("[complete_style_detection] Starting parallel AI analysis...")
        
        async def run_style_analysis():
            """Run style analysis in executor"""
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, partial(style_logic.analyze_content_style, crawl_result['content']))
        
        async def run_patterns_analysis():
            """Run patterns analysis in executor (if requested)"""
            if not request.include_patterns:
                return None
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, partial(style_logic.analyze_style_patterns, crawl_result['content']))
        
        # Execute style and patterns analysis in parallel
        style_analysis, patterns_result = await asyncio.gather(
            run_style_analysis(),
            run_patterns_analysis(),
            return_exceptions=True
        )
        
        # Check if style_analysis failed
        if isinstance(style_analysis, Exception):
            error_msg = str(style_analysis)
            logger.error(f"Style analysis failed with exception: {error_msg}")
            analysis_service.save_error_analysis(session.id, request.url or "text_sample", error_msg)
            return StyleDetectionResponse(
                success=False,
                error=f"Style analysis failed: {error_msg}",
                timestamp=datetime.now().isoformat()
            )
        
        if not style_analysis or not style_analysis.get('success'):
            error_msg = style_analysis.get('error', 'Unknown error') if style_analysis else 'Analysis failed'
            if 'API key' in error_msg or 'configure' in error_msg:
                return StyleDetectionResponse(
                    success=False,
                    error="API keys not configured. Please complete step 1 of onboarding to configure your AI provider API keys.",
                    timestamp=datetime.now().isoformat()
                )
            else:
                analysis_service.save_error_analysis(session.id, request.url or "text_sample", error_msg)
                return StyleDetectionResponse(
                    success=False,
                    error=f"Style analysis failed: {error_msg}",
                    timestamp=datetime.now().isoformat()
                )
        
        # Process patterns result
        style_patterns = None
        if request.include_patterns and patterns_result and not isinstance(patterns_result, Exception):
            if patterns_result.get('success'):
                style_patterns = patterns_result.get('patterns')
        
        # Step 4: Generate guidelines (depends on style_analysis, must run after)
        style_guidelines = None
        if request.include_guidelines:
            loop = asyncio.get_event_loop()
            guidelines_result = await loop.run_in_executor(
                None, 
                partial(style_logic.generate_style_guidelines, style_analysis.get('analysis', {}))
            )
            if guidelines_result and guidelines_result.get('success'):
                style_guidelines = guidelines_result.get('guidelines')
        
        # Check if there's a warning about fallback data
        warning = None
        if style_analysis and 'warning' in style_analysis:
            warning = style_analysis['warning']
        
        # Prepare response data
        response_data = {
            'crawl_result': crawl_result,
            'style_analysis': style_analysis.get('analysis') if style_analysis else None,
            'style_patterns': style_patterns,
            'style_guidelines': style_guidelines,
            'warning': warning
        }
        
        # Save analysis to database
        if request.url:  # Only save for URL-based analysis
            analysis_id = analysis_service.save_analysis(session.id, request.url, response_data)
            if analysis_id:
                response_data['analysis_id'] = analysis_id
        
        return StyleDetectionResponse(
            success=True,
            crawl_result=crawl_result,
            style_analysis=style_analysis.get('analysis') if style_analysis else None,
            style_patterns=style_patterns,
            style_guidelines=style_guidelines,
            warning=warning,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"[complete_style_detection] Error: {str(e)}")
        return StyleDetectionResponse(
            success=False,
            error=f"Style detection error: {str(e)}",
            timestamp=datetime.now().isoformat()
        )

@router.get("/style-detection/check-existing/{website_url:path}")
async def check_existing_analysis(
    website_url: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Check if analysis exists for a website URL with user isolation."""
    try:
        user_id = str(current_user.get('id'))
        logger.info(f"[check_existing_analysis] Checking for URL: {website_url} (user: {user_id})")
        
        # Get database session
        db_session = get_db_session()
        if not db_session:
            return {"error": "Database connection not available"}
        
        # Initialize service
        analysis_service = WebsiteAnalysisService(db_session)
        
        # Use authenticated Clerk user ID for proper user isolation
        # Use consistent SHA256-based conversion
        user_id_int = clerk_user_id_to_int(user_id)
        
        # Check for existing analysis for THIS USER ONLY
        existing_analysis = analysis_service.check_existing_analysis(user_id_int, website_url)
        
        return existing_analysis
        
    except Exception as e:
        logger.error(f"[check_existing_analysis] Error: {str(e)}")
        return {"error": f"Error checking existing analysis: {str(e)}"}

@router.get("/style-detection/analysis/{analysis_id}")
async def get_analysis_by_id(analysis_id: int):
    """Get analysis by ID."""
    try:
        logger.info(f"[get_analysis_by_id] Getting analysis: {analysis_id}")
        
        # Get database session
        db_session = get_db_session()
        if not db_session:
            return {"error": "Database connection not available"}
        
        # Initialize service
        analysis_service = WebsiteAnalysisService(db_session)
        
        # Get analysis
        analysis = analysis_service.get_analysis(analysis_id)
        
        if analysis:
            return {"success": True, "analysis": analysis}
        else:
            return {"success": False, "error": "Analysis not found"}
        
    except Exception as e:
        logger.error(f"[get_analysis_by_id] Error: {str(e)}")
        return {"error": f"Error retrieving analysis: {str(e)}"}

@router.get("/style-detection/session-analyses")
async def get_session_analyses(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get all analyses for the current user with proper user isolation."""
    try:
        user_id = str(current_user.get('id'))
        logger.info(f"[get_session_analyses] Getting analyses for user: {user_id}")
        
        # Get database session
        db_session = get_db_session()
        if not db_session:
            return {"error": "Database connection not available"}
        
        # Initialize service
        analysis_service = WebsiteAnalysisService(db_session)
        
        # Use authenticated Clerk user ID for proper user isolation
        # Use consistent SHA256-based conversion
        user_id_int = clerk_user_id_to_int(user_id)
        
        # Get analyses for THIS USER ONLY (not all users!)
        analyses = analysis_service.get_session_analyses(user_id_int)
        
        logger.info(f"[get_session_analyses] Found {len(analyses) if analyses else 0} analyses for user {user_id}")
        return {"success": True, "analyses": analyses}
        
    except Exception as e:
        logger.error(f"[get_session_analyses] Error: {str(e)}")
        return {"error": f"Error retrieving session analyses: {str(e)}"}

@router.delete("/style-detection/analysis/{analysis_id}")
async def delete_analysis(analysis_id: int):
    """Delete an analysis."""
    try:
        logger.info(f"[delete_analysis] Deleting analysis: {analysis_id}")
        
        # Get database session
        db_session = get_db_session()
        if not db_session:
            return {"error": "Database connection not available"}
        
        # Initialize service
        analysis_service = WebsiteAnalysisService(db_session)
        
        # Delete analysis
        success = analysis_service.delete_analysis(analysis_id)
        
        if success:
            return {"success": True, "message": "Analysis deleted successfully"}
        else:
            return {"success": False, "error": "Analysis not found or could not be deleted"}
        
    except Exception as e:
        logger.error(f"[delete_analysis] Error: {str(e)}")
        return {"error": f"Error deleting analysis: {str(e)}"}

@router.get("/style-detection/configuration-options")
async def get_style_detection_configuration():
    """Get configuration options for style detection."""
    try:
        return {
            "analysis_types": [
                {"value": "comprehensive", "label": "Comprehensive Analysis", "description": "Full writing style analysis"},
                {"value": "patterns", "label": "Pattern Analysis", "description": "Focus on writing patterns"}
            ],
            "content_sources": [
                {"value": "url", "label": "Website URL", "description": "Analyze content from a website"},
                {"value": "text", "label": "Text Sample", "description": "Analyze provided text content"}
            ],
            "limits": {
                "max_content_length": 10000,
                "min_content_length": 50,
                "max_urls_per_request": 1
            },
            "features": {
                "style_analysis": True,
                "pattern_analysis": True,
                "guidelines_generation": True,
                "metrics_calculation": True
            }
        }
    except Exception as e:
        logger.error(f"[get_style_detection_configuration] Error: {str(e)}")
        return {"error": f"Configuration error: {str(e)}"} 