"""
Research Configuration API
Provides provider availability and persona-aware defaults for research.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, Any, Optional, List
from loguru import logger
from pydantic import BaseModel

from middleware.auth_middleware import get_current_user
from services.user_api_key_context import get_exa_key, get_gemini_key, get_tavily_key
from services.onboarding.database_service import OnboardingDatabaseService
from services.onboarding.progress_service import get_onboarding_progress_service
from services.database import get_db
from sqlalchemy.orm import Session
from services.research.research_persona_service import ResearchPersonaService
from services.research.research_persona_scheduler import schedule_research_persona_generation
from models.research_persona_models import ResearchPersona


router = APIRouter()


class ProviderAvailability(BaseModel):
    """Provider availability status."""
    google_available: bool
    exa_available: bool
    tavily_available: bool
    gemini_key_status: str  # 'configured' | 'missing'
    exa_key_status: str  # 'configured' | 'missing'
    tavily_key_status: str  # 'configured' | 'missing'


class PersonaDefaults(BaseModel):
    """Persona-aware research defaults."""
    industry: Optional[str] = None
    target_audience: Optional[str] = None
    suggested_domains: list[str] = []
    suggested_exa_category: Optional[str] = None


class ResearchConfigResponse(BaseModel):
    """Combined research configuration response."""
    provider_availability: ProviderAvailability
    persona_defaults: PersonaDefaults
    research_persona: Optional[ResearchPersona] = None
    onboarding_completed: bool = False
    persona_scheduled: bool = False


class CompetitorAnalysisResponse(BaseModel):
    """Response model for competitor analysis data."""
    success: bool
    competitors: Optional[List[Dict[str, Any]]] = None
    social_media_accounts: Optional[Dict[str, str]] = None
    social_media_citations: Optional[List[Dict[str, Any]]] = None
    research_summary: Optional[Dict[str, Any]] = None
    analysis_timestamp: Optional[str] = None
    error: Optional[str] = None


@router.get("/provider-availability", response_model=ProviderAvailability)
async def get_provider_availability(
    current_user: Dict = Depends(get_current_user)
):
    """
    Check which research providers are available for the current user.
    
    Returns:
        - google_available: True if Gemini key is configured
        - exa_available: True if Exa key is configured
        - tavily_available: True if Tavily key is configured
        - Key status for each provider
    """
    try:
        user_id = str(current_user.get('id'))
        
        # Check API key availability
        gemini_key = get_gemini_key(user_id)
        exa_key = get_exa_key(user_id)
        tavily_key = get_tavily_key(user_id)
        
        google_available = bool(gemini_key and gemini_key.strip())
        exa_available = bool(exa_key and exa_key.strip())
        tavily_available = bool(tavily_key and tavily_key.strip())
        
        return ProviderAvailability(
            google_available=google_available,
            exa_available=exa_available,
            tavily_available=tavily_available,
            gemini_key_status='configured' if google_available else 'missing',
            exa_key_status='configured' if exa_available else 'missing',
            tavily_key_status='configured' if tavily_available else 'missing'
        )
    except Exception as e:
        logger.error(f"[ResearchConfig] Error checking provider availability for user {user_id if 'user_id' in locals() else 'unknown'}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to check provider availability: {str(e)}")


@router.get("/persona-defaults", response_model=PersonaDefaults)
async def get_persona_defaults(
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get persona-aware research defaults for the current user.
    
    Returns industry, target audience, and smart suggestions based on onboarding data.
    """
    try:
        user_id = str(current_user.get('id'))
        
        # Add explicit null check for database session
        if not db:
            logger.error(f"[ResearchConfig] Database session is None for user {user_id} in get_persona_defaults")
            # Return defaults rather than error
            return PersonaDefaults()
        
        db_service = OnboardingDatabaseService(db=db)
        
        # Try to get persona data first (most reliable source for industry/target_audience)
        persona_data = db_service.get_persona_data(user_id, db)
        industry = 'General'
        target_audience = 'General'
        
        if persona_data:
            core_persona = persona_data.get('corePersona') or persona_data.get('core_persona')
            if core_persona:
                if core_persona.get('industry'):
                    industry = core_persona['industry']
                if core_persona.get('target_audience'):
                    target_audience = core_persona['target_audience']
        
        # Fallback to website analysis if persona data doesn't have industry info
        if industry == 'General':
            website_analysis = db_service.get_website_analysis(user_id, db)
            if website_analysis:
                target_audience_data = website_analysis.get('target_audience', {})
                if isinstance(target_audience_data, dict):
                    # Extract from target_audience JSON field
                    industry_focus = target_audience_data.get('industry_focus')
                    if industry_focus:
                        industry = industry_focus
                    demographics = target_audience_data.get('demographics')
                    if demographics:
                        target_audience = demographics if isinstance(demographics, str) else str(demographics)
        
        # Suggest domains based on industry
        suggested_domains = _get_domain_suggestions(industry)
        
        # Suggest Exa category based on industry
        suggested_exa_category = _get_exa_category_suggestion(industry)
        
        return PersonaDefaults(
            industry=industry,
            target_audience=target_audience,
            suggested_domains=suggested_domains,
            suggested_exa_category=suggested_exa_category
        )
    except Exception as e:
        logger.error(f"[ResearchConfig] Error getting persona defaults for user {user_id if 'user_id' in locals() else 'unknown'}: {e}", exc_info=True)
        # Return defaults rather than error
        return PersonaDefaults()


@router.get("/research-persona")
async def get_research_persona(
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    force_refresh: bool = Query(False, description="Force regenerate persona even if cache is valid")
):
    """
    Get or generate research persona for the current user.
    
    Query params:
    - force_refresh: If true, regenerate persona even if cache is valid (default: false)
    
    Returns research persona with personalized defaults, suggestions, and configurations.
    """
    try:
        user_id = str(current_user.get('id'))
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        # Add explicit null check for database session
        if not db:
            logger.error(f"[ResearchConfig] Database session is None for user {user_id} in get_research_persona")
            raise HTTPException(status_code=500, detail="Database not available")
        
        persona_service = ResearchPersonaService(db_session=db)
        research_persona = persona_service.get_or_generate(user_id, force_refresh=force_refresh)
        
        if not research_persona:
            raise HTTPException(
                status_code=404,
                detail="Research persona not available. Complete onboarding to generate one."
            )
        
        return research_persona.dict()
        
    except HTTPException:
        # Re-raise HTTPExceptions (e.g., 429 subscription limit) to preserve status code and details
        raise
    except Exception as e:
        logger.error(f"[ResearchConfig] Error getting research persona for user {user_id if 'user_id' in locals() else 'unknown'}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get research persona: {str(e)}")


@router.get("/config", response_model=ResearchConfigResponse)
async def get_research_config(
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get complete research configuration including provider availability and persona defaults.
    """
    user_id = None
    try:
        user_id = str(current_user.get('id'))
        logger.info(f"[ResearchConfig] Starting get_research_config for user {user_id}")
        
        # Add explicit null check for database session
        if not db:
            logger.error(f"[ResearchConfig] Database session is None for user {user_id} in get_research_config")
            raise HTTPException(status_code=500, detail="Database session not available")
        
        # Get provider availability
        logger.debug(f"[ResearchConfig] Getting provider availability for user {user_id}")
        gemini_key = get_gemini_key(user_id)
        exa_key = get_exa_key(user_id)
        tavily_key = get_tavily_key(user_id)
        
        google_available = bool(gemini_key and gemini_key.strip())
        exa_available = bool(exa_key and exa_key.strip())
        tavily_available = bool(tavily_key and tavily_key.strip())
        
        provider_availability = ProviderAvailability(
            google_available=google_available,
            exa_available=exa_available,
            tavily_available=tavily_available,
            gemini_key_status='configured' if google_available else 'missing',
            exa_key_status='configured' if exa_available else 'missing',
            tavily_key_status='configured' if tavily_available else 'missing'
        )
        
        # Get persona defaults
        logger.debug(f"[ResearchConfig] Getting persona defaults for user {user_id}")
        db_service = OnboardingDatabaseService(db=db)
        
        # Try to get persona data first (most reliable source for industry/target_audience)
        try:
            persona_data = db_service.get_persona_data(user_id, db)
        except Exception as e:
            logger.error(f"[ResearchConfig] Error getting persona data for user {user_id}: {e}", exc_info=True)
            persona_data = None
        
        industry = 'General'
        target_audience = 'General'
        
        if persona_data:
            core_persona = persona_data.get('corePersona') or persona_data.get('core_persona')
            if core_persona:
                if core_persona.get('industry'):
                    industry = core_persona['industry']
                if core_persona.get('target_audience'):
                    target_audience = core_persona['target_audience']
        
        # Fallback to website analysis if persona data doesn't have industry info
        if industry == 'General':
            website_analysis = db_service.get_website_analysis(user_id, db)
            if website_analysis:
                target_audience_data = website_analysis.get('target_audience', {})
                if isinstance(target_audience_data, dict):
                    # Extract from target_audience JSON field
                    industry_focus = target_audience_data.get('industry_focus')
                    if industry_focus:
                        industry = industry_focus
                    demographics = target_audience_data.get('demographics')
                    if demographics:
                        target_audience = demographics if isinstance(demographics, str) else str(demographics)
        
        persona_defaults = PersonaDefaults(
            industry=industry,
            target_audience=target_audience,
            suggested_domains=_get_domain_suggestions(industry),
            suggested_exa_category=_get_exa_category_suggestion(industry)
        )
        
        # Check onboarding completion status
        onboarding_completed = False
        try:
            logger.debug(f"[ResearchConfig] Checking onboarding status for user {user_id}")
            progress_service = get_onboarding_progress_service()
            onboarding_status = progress_service.get_onboarding_status(user_id)
            onboarding_completed = onboarding_status.get('is_completed', False)
            logger.info(
                f"[ResearchConfig] Onboarding status check for user {user_id}: "
                f"is_completed={onboarding_completed}, "
                f"current_step={onboarding_status.get('current_step')}, "
                f"progress={onboarding_status.get('completion_percentage')}"
            )
        except Exception as e:
            logger.error(f"[ResearchConfig] Could not check onboarding status for user {user_id}: {e}", exc_info=True)
            # Continue with onboarding_completed=False
        
        # Get research persona (optional, may not exist for all users)
        # CRITICAL: Use get_cached_only() to avoid triggering rate limit checks
        # Only return persona if it's already cached - don't generate on config load
        research_persona = None
        persona_scheduled = False
        try:
            logger.debug(f"[ResearchConfig] Getting cached research persona for user {user_id}")
            persona_service = ResearchPersonaService(db_session=db)
            research_persona = persona_service.get_cached_only(user_id)
            
            logger.info(
                f"[ResearchConfig] Research persona check for user {user_id}: "
                f"persona_exists={research_persona is not None}, "
                f"onboarding_completed={onboarding_completed}"
            )
            
            # If onboarding is completed but persona doesn't exist, schedule generation
            if onboarding_completed and not research_persona:
                try:
                    # Check if persona data exists (to ensure we have data to generate from)
                    db_service = OnboardingDatabaseService(db=db)
                    persona_data = db_service.get_persona_data(user_id, db)
                    if persona_data and (persona_data.get('corePersona') or persona_data.get('platformPersonas') or 
                                        persona_data.get('core_persona') or persona_data.get('platform_personas')):
                        # Schedule persona generation (20 minutes from now)
                        schedule_research_persona_generation(user_id, delay_minutes=20)
                        logger.info(f"Scheduled research persona generation for user {user_id} (onboarding already completed)")
                        persona_scheduled = True
                    else:
                        logger.info(f"Onboarding completed but no persona data found for user {user_id} - cannot schedule persona generation")
                except Exception as e:
                    logger.warning(f"Failed to schedule research persona generation: {e}", exc_info=True)
        except Exception as e:
            # get_cached_only() never raises HTTPException, but catch any unexpected errors
            logger.warning(f"[ResearchConfig] Could not load cached research persona for user {user_id}: {e}", exc_info=True)
        
        # FastAPI will automatically serialize the ResearchPersona Pydantic model
        # If there's a serialization issue, we catch it and log it
        try:
            response = ResearchConfigResponse(
                provider_availability=provider_availability,
                persona_defaults=persona_defaults,
                research_persona=research_persona,
                onboarding_completed=onboarding_completed,
                persona_scheduled=persona_scheduled
            )
        except Exception as serialization_error:
            logger.error(f"[ResearchConfig] Failed to create ResearchConfigResponse for user {user_id}: {serialization_error}", exc_info=True)
            # Try without research_persona as fallback
            response = ResearchConfigResponse(
                provider_availability=provider_availability,
                persona_defaults=persona_defaults,
                research_persona=None,
                onboarding_completed=onboarding_completed,
                persona_scheduled=persona_scheduled
            )

        logger.info(
            f"[ResearchConfig] Response for user {user_id}: "
            f"onboarding_completed={onboarding_completed}, "
            f"persona_exists={research_persona is not None}, "
            f"persona_scheduled={persona_scheduled}"
        )

        return response
    except HTTPException:
        # Re-raise HTTPExceptions (e.g., 429, 401, etc.) to preserve status codes
        raise
    except Exception as e:
        logger.error(f"[ResearchConfig] CRITICAL ERROR getting research config for user {user_id if user_id else 'unknown'}: {e}", exc_info=True)
        import traceback
        logger.error(f"[ResearchConfig] Full traceback:\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get research config: {str(e)}"
        )


@router.get("/competitor-analysis", response_model=CompetitorAnalysisResponse)
async def get_competitor_analysis(
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get competitor analysis data from onboarding for the current user.
    
    Returns competitor data including competitors list, social media accounts,
    social media citations, and research summary that was collected during onboarding step 3.
    """
    user_id = None
    try:
        user_id = str(current_user.get('id'))
        print(f"\n[COMPETITOR_ANALYSIS] ===== START: Getting competitor analysis for user_id={user_id} =====")
        print(f"[COMPETITOR_ANALYSIS] Current user dict keys: {list(current_user.keys())}")
        logger.info(f"[ResearchConfig] Getting competitor analysis for user {user_id}")

        if not db:
            print(f"[COMPETITOR_ANALYSIS] ❌ ERROR: Database session is None for user {user_id}")
            logger.error(f"[ResearchConfig] Database session is None for user {user_id}")
            raise HTTPException(status_code=500, detail="Database session not available")

        db_service = OnboardingDatabaseService(db=db)

        # Get onboarding session - using same pattern as onboarding completion check
        print(f"[COMPETITOR_ANALYSIS] Looking up onboarding session for user_id={user_id} (Clerk ID)")
        session = db_service.get_session_by_user(user_id, db)
        if not session:
            print(f"[COMPETITOR_ANALYSIS] ❌ WARNING: No onboarding session found for user_id={user_id}")
            logger.warning(f"[ResearchConfig] No onboarding session found for user {user_id}")
            return CompetitorAnalysisResponse(
                success=False,
                error="No onboarding session found. Please complete onboarding first."
            )
        
        print(f"[COMPETITOR_ANALYSIS] ✅ Found onboarding session: id={session.id}, user_id={session.user_id}, current_step={session.current_step}")

        # Check if step 3 is completed - same pattern as elsewhere (check current_step >= 3 or research_preferences exists)
        research_preferences = db_service.get_research_preferences(user_id, db)
        print(f"[COMPETITOR_ANALYSIS] Step check: current_step={session.current_step}, research_preferences exists={research_preferences is not None}")
        if not research_preferences and session.current_step < 3:
            print(f"[COMPETITOR_ANALYSIS] ❌ Step 3 not completed for user_id={user_id} (current_step={session.current_step})")
            logger.info(f"[ResearchConfig] Step 3 not completed for user {user_id} (current_step={session.current_step})")
            return CompetitorAnalysisResponse(
                success=False,
                error="Onboarding step 3 (Competitor Analysis) is not completed. Please complete onboarding step 3 first."
            )
        
        print(f"[COMPETITOR_ANALYSIS] ✅ Step 3 is completed (current_step={session.current_step} or research_preferences exists)")

        # Try Method 1: Get competitor data from CompetitorAnalysis table using OnboardingDatabaseService
        # This follows the same pattern as get_website_analysis()
        print(f"[COMPETITOR_ANALYSIS] 🔍 Method 1: Querying CompetitorAnalysis table using OnboardingDatabaseService...")
        try:
            competitors = db_service.get_competitor_analysis(user_id, db)
            
            if competitors:
                print(f"[COMPETITOR_ANALYSIS] ✅ Found {len(competitors)} competitor records from CompetitorAnalysis table")
                logger.info(f"[ResearchConfig] Found {len(competitors)} competitors from CompetitorAnalysis table for user {user_id}")
                
                # Map competitor fields to match frontend expectations
                mapped_competitors = []
                for comp in competitors:
                    mapped_comp = {
                        **comp,  # Keep all original fields
                        "name": comp.get("title") or comp.get("name") or comp.get("domain", ""),
                        "description": comp.get("summary") or comp.get("description", ""),
                        "similarity_score": comp.get("relevance_score") or comp.get("similarity_score", 0.5)
                    }
                    mapped_competitors.append(mapped_comp)
                
                print(f"[COMPETITOR_ANALYSIS] ✅ SUCCESS: Returning {len(mapped_competitors)} competitors for user_id={user_id}")
                return CompetitorAnalysisResponse(
                    success=True,
                    competitors=mapped_competitors,
                    social_media_accounts={},
                    social_media_citations=[],
                    research_summary={
                        "total_competitors": len(mapped_competitors),
                        "market_insights": f"Found {len(mapped_competitors)} competitors analyzed during onboarding"
                    },
                    analysis_timestamp=None
                )
            else:
                print(f"[COMPETITOR_ANALYSIS] ⚠️ No competitor records found in CompetitorAnalysis table for user_id={user_id}")
                
        except Exception as e:
            print(f"[COMPETITOR_ANALYSIS] ❌ EXCEPTION in Method 1: {e}")
            import traceback
            print(f"[COMPETITOR_ANALYSIS] Traceback:\n{traceback.format_exc()}")
            logger.warning(f"[ResearchConfig] Could not retrieve competitor data from CompetitorAnalysis table: {e}", exc_info=True)

        # Try Method 2: Get data from Step3ResearchService (which accesses step_data)
        # This is where step3_research_service._store_research_data() saves the data
        print(f"[COMPETITOR_ANALYSIS] 🔄 Method 2: Trying Step3ResearchService.get_research_data()...")
        try:
            from api.onboarding_utils.step3_research_service import Step3ResearchService
            
            # Step3ResearchService.get_research_data() expects session_id (integer), but we have user_id (string)
            # The service uses session.id internally, so we need to pass the session.id
            step3_service = Step3ResearchService()
            research_data_result = await step3_service.get_research_data(str(session.id))
            
            print(f"[COMPETITOR_ANALYSIS] Step3ResearchService.get_research_data() result: success={research_data_result.get('success')}")
            
            if research_data_result.get('success'):
                # Handle both 'research_data' and 'step3_research_data' keys
                research_data = research_data_result.get('step3_research_data') or research_data_result.get('research_data', {})
                print(f"[COMPETITOR_ANALYSIS] Research data keys: {list(research_data.keys()) if isinstance(research_data, dict) else 'Not a dict'}")
                
                if isinstance(research_data, dict) and research_data.get('competitors'):
                    competitors_list = research_data.get('competitors', [])
                    print(f"[COMPETITOR_ANALYSIS] ✅ Found {len(competitors_list)} competitors in step_data via Step3ResearchService")
                    
                    if competitors_list:
                        analysis_metadata = research_data.get('analysis_metadata', {})
                        social_media_data = analysis_metadata.get('social_media_data', {})
                        
                        # Map competitor fields to match frontend expectations
                        mapped_competitors = []
                        for comp in competitors_list:
                            mapped_comp = {
                                **comp,  # Keep all original fields
                                "name": comp.get("title") or comp.get("name") or comp.get("domain", ""),
                                "description": comp.get("summary") or comp.get("description", ""),
                                "similarity_score": comp.get("relevance_score") or comp.get("similarity_score", 0.5)
                            }
                            mapped_competitors.append(mapped_comp)
                        
                        print(f"[COMPETITOR_ANALYSIS] ✅ SUCCESS: Returning {len(mapped_competitors)} competitors from step_data for user_id={user_id}")
                        logger.info(f"[ResearchConfig] Found {len(mapped_competitors)} competitors from step_data via Step3ResearchService for user {user_id}")
                        return CompetitorAnalysisResponse(
                            success=True,
                            competitors=mapped_competitors,
                            social_media_accounts=social_media_data.get('social_media_accounts', {}),
                            social_media_citations=social_media_data.get('citations', []),
                            research_summary=research_data.get('research_summary'),
                            analysis_timestamp=research_data.get('completed_at')
                        )
                    else:
                        print(f"[COMPETITOR_ANALYSIS] ⚠️ Step3ResearchService returned competitors list but it's empty")
                else:
                    print(f"[COMPETITOR_ANALYSIS] ⚠️ Step3ResearchService returned success=True but no competitors in data")
            else:
                error_msg = research_data_result.get('error', 'Unknown error')
                print(f"[COMPETITOR_ANALYSIS] ⚠️ Step3ResearchService returned success=False, error: {error_msg}")
                
        except Exception as e:
            print(f"[COMPETITOR_ANALYSIS] ❌ EXCEPTION in Method 2: {e}")
            import traceback
            print(f"[COMPETITOR_ANALYSIS] Traceback:\n{traceback.format_exc()}")
            logger.warning(f"[ResearchConfig] Could not retrieve competitor data from Step3ResearchService: {e}", exc_info=True)

        # Fallback: Return empty response with helpful message
        print(f"[COMPETITOR_ANALYSIS] ❌ FALLBACK: No competitor analysis data found for user_id={user_id}")
        print(f"[COMPETITOR_ANALYSIS] Step 3 is completed (current_step={session.current_step}) but no data found in either source")
        logger.info(f"[ResearchConfig] No competitor analysis data found for user {user_id} (step 3 completed but no data found)")
        return CompetitorAnalysisResponse(
            success=False,
            error="Competitor analysis data was not found in the database. Please re-run competitor discovery in Step 3 of onboarding to generate and save competitor data."
        )
        
    except HTTPException:
        print(f"[COMPETITOR_ANALYSIS] ❌ HTTPException raised (will be re-raised)")
        raise
    except Exception as e:
        print(f"[COMPETITOR_ANALYSIS] ❌ CRITICAL ERROR: {e}")
        import traceback
        print(f"[COMPETITOR_ANALYSIS] Traceback:\n{traceback.format_exc()}")
        logger.error(f"[ResearchConfig] Error getting competitor analysis for user {user_id if user_id else 'unknown'}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get competitor analysis: {str(e)}"
        )
    finally:
        print(f"[COMPETITOR_ANALYSIS] ===== END: Getting competitor analysis for user_id={user_id} =====\n")


# Helper functions from RESEARCH_AI_HYPERPERSONALIZATION.md

def _get_domain_suggestions(industry: str) -> list[str]:
    """Get domain suggestions based on industry."""
    domain_map = {
        'Healthcare': ['pubmed.gov', 'nejm.org', 'thelancet.com', 'nih.gov'],
        'Technology': ['techcrunch.com', 'wired.com', 'arstechnica.com', 'theverge.com'],
        'Finance': ['wsj.com', 'bloomberg.com', 'ft.com', 'reuters.com'],
        'Science': ['nature.com', 'sciencemag.org', 'cell.com', 'pnas.org'],
        'Business': ['hbr.org', 'forbes.com', 'businessinsider.com', 'mckinsey.com'],
        'Marketing': ['marketingland.com', 'adweek.com', 'hubspot.com', 'moz.com'],
        'Education': ['edutopia.org', 'chronicle.com', 'insidehighered.com'],
        'Real Estate': ['realtor.com', 'zillow.com', 'forbes.com'],
        'Entertainment': ['variety.com', 'hollywoodreporter.com', 'deadline.com'],
        'Travel': ['lonelyplanet.com', 'nationalgeographic.com', 'travelandleisure.com'],
        'Fashion': ['vogue.com', 'elle.com', 'wwd.com'],
        'Sports': ['espn.com', 'si.com', 'bleacherreport.com'],
        'Law': ['law.com', 'abajournal.com', 'scotusblog.com'],
    }
    return domain_map.get(industry, [])


def _get_exa_category_suggestion(industry: str) -> Optional[str]:
    """Get Exa category suggestion based on industry."""
    category_map = {
        'Healthcare': 'research paper',
        'Science': 'research paper',
        'Finance': 'financial report',
        'Technology': 'company',
        'Business': 'company',
        'Marketing': 'company',
        'Education': 'research paper',
        'Law': 'pdf',
    }
    return category_map.get(industry)

