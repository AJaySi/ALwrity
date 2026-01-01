"""
Research API Router

Standalone API endpoints for the Research Engine.
These endpoints can be used by:
- Frontend Research UI
- Blog Writer (via adapter)
- Podcast Maker
- YouTube Creator
- Any other content tool

Author: ALwrity Team
Version: 2.0
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from loguru import logger
import uuid
import asyncio

from services.database import get_db
from services.research.core import (
    ResearchEngine,
    ResearchContext,
    ResearchPersonalizationContext,
    ContentType,
    ResearchGoal,
    ResearchDepth,
    ProviderPreference,
)
from services.research.core.research_context import ResearchResult
from middleware.auth_middleware import get_current_user

# Intent-driven research imports
from models.research_intent_models import (
    ResearchIntent,
    IntentInferenceRequest,
    IntentInferenceResponse,
    IntentDrivenResearchResult,
    ResearchQuery,
    ExpectedDeliverable,
    ResearchPurpose,
    ContentOutput,
    ResearchDepthLevel,
)
from services.research.intent import (
    ResearchIntentInference,
    IntentQueryGenerator,
    IntentAwareAnalyzer,
)

router = APIRouter(prefix="/api/research", tags=["Research Engine"])


# Request/Response models
class ResearchRequest(BaseModel):
    """API request for research."""
    query: str = Field(..., description="Main research query or topic")
    keywords: List[str] = Field(default_factory=list, description="Additional keywords")
    
    # Research configuration
    goal: Optional[str] = Field(default="factual", description="Research goal: factual, trending, competitive, etc.")
    depth: Optional[str] = Field(default="standard", description="Research depth: quick, standard, comprehensive, expert")
    provider: Optional[str] = Field(default="auto", description="Provider preference: auto, exa, tavily, google")
    
    # Personalization
    content_type: Optional[str] = Field(default="general", description="Content type: blog, podcast, video, etc.")
    industry: Optional[str] = None
    target_audience: Optional[str] = None
    tone: Optional[str] = None
    
    # Constraints
    max_sources: int = Field(default=10, ge=1, le=25)
    recency: Optional[str] = None  # day, week, month, year
    
    # Domain filtering
    include_domains: List[str] = Field(default_factory=list)
    exclude_domains: List[str] = Field(default_factory=list)
    
    # Advanced mode
    advanced_mode: bool = False
    
    # Raw provider parameters (only if advanced_mode=True)
    exa_category: Optional[str] = None
    exa_search_type: Optional[str] = None
    tavily_topic: Optional[str] = None
    tavily_search_depth: Optional[str] = None
    tavily_include_answer: bool = False
    tavily_time_range: Optional[str] = None


class ResearchResponse(BaseModel):
    """API response for research."""
    success: bool
    task_id: Optional[str] = None  # For async requests
    
    # Results (if synchronous)
    sources: List[Dict[str, Any]] = Field(default_factory=list)
    keyword_analysis: Dict[str, Any] = Field(default_factory=dict)
    competitor_analysis: Dict[str, Any] = Field(default_factory=dict)
    suggested_angles: List[str] = Field(default_factory=list)
    
    # Metadata
    provider_used: Optional[str] = None
    search_queries: List[str] = Field(default_factory=list)
    
    # Error handling
    error_message: Optional[str] = None
    error_code: Optional[str] = None


class ProviderStatusResponse(BaseModel):
    """API response for provider status."""
    exa: Dict[str, Any]
    tavily: Dict[str, Any]
    google: Dict[str, Any]


# In-memory task storage for async research
_research_tasks: Dict[str, Dict[str, Any]] = {}


def _convert_to_research_context(request: ResearchRequest, user_id: str) -> ResearchContext:
    """Convert API request to ResearchContext."""
    
    # Map string enums
    goal_map = {
        "factual": ResearchGoal.FACTUAL,
        "trending": ResearchGoal.TRENDING,
        "competitive": ResearchGoal.COMPETITIVE,
        "educational": ResearchGoal.EDUCATIONAL,
        "technical": ResearchGoal.TECHNICAL,
        "inspirational": ResearchGoal.INSPIRATIONAL,
    }
    
    depth_map = {
        "quick": ResearchDepth.QUICK,
        "standard": ResearchDepth.STANDARD,
        "comprehensive": ResearchDepth.COMPREHENSIVE,
        "expert": ResearchDepth.EXPERT,
    }
    
    provider_map = {
        "auto": ProviderPreference.AUTO,
        "exa": ProviderPreference.EXA,
        "tavily": ProviderPreference.TAVILY,
        "google": ProviderPreference.GOOGLE,
        "hybrid": ProviderPreference.HYBRID,
    }
    
    content_type_map = {
        "blog": ContentType.BLOG,
        "podcast": ContentType.PODCAST,
        "video": ContentType.VIDEO,
        "social": ContentType.SOCIAL,
        "email": ContentType.EMAIL,
        "newsletter": ContentType.NEWSLETTER,
        "whitepaper": ContentType.WHITEPAPER,
        "general": ContentType.GENERAL,
    }
    
    # Build personalization context
    personalization = ResearchPersonalizationContext(
        creator_id=user_id,
        content_type=content_type_map.get(request.content_type or "general", ContentType.GENERAL),
        industry=request.industry,
        target_audience=request.target_audience,
        tone=request.tone,
    )
    
    return ResearchContext(
        query=request.query,
        keywords=request.keywords,
        goal=goal_map.get(request.goal or "factual", ResearchGoal.FACTUAL),
        depth=depth_map.get(request.depth or "standard", ResearchDepth.STANDARD),
        provider_preference=provider_map.get(request.provider or "auto", ProviderPreference.AUTO),
        personalization=personalization,
        max_sources=request.max_sources,
        recency=request.recency,
        include_domains=request.include_domains,
        exclude_domains=request.exclude_domains,
        advanced_mode=request.advanced_mode,
        exa_category=request.exa_category,
        exa_search_type=request.exa_search_type,
        tavily_topic=request.tavily_topic,
        tavily_search_depth=request.tavily_search_depth,
        tavily_include_answer=request.tavily_include_answer,
        tavily_time_range=request.tavily_time_range,
    )


@router.get("/providers/status", response_model=ProviderStatusResponse)
async def get_provider_status():
    """
    Get status of available research providers.
    
    Returns availability and priority of Exa, Tavily, and Google providers.
    """
    engine = ResearchEngine()
    return engine.get_provider_status()


@router.post("/execute", response_model=ResearchResponse)
async def execute_research(
    request: ResearchRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Execute research synchronously.
    
    For quick research needs. For longer research, use /start endpoint.
    """
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        user_id = str(current_user.get('id', ''))
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid user ID in authentication token")
        
        logger.info(f"[Research API] Execute request: {request.query[:50]}...")
        
        engine = ResearchEngine()
        context = _convert_to_research_context(request, user_id)
        
        result = await engine.research(context)
        
        return ResearchResponse(
            success=result.success,
            sources=result.sources,
            keyword_analysis=result.keyword_analysis,
            competitor_analysis=result.competitor_analysis,
            suggested_angles=result.suggested_angles,
            provider_used=result.provider_used,
            search_queries=result.search_queries,
            error_message=result.error_message,
            error_code=result.error_code,
        )
        
    except Exception as e:
        logger.error(f"[Research API] Execute failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/start", response_model=ResearchResponse)
async def start_research(
    request: ResearchRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Start research asynchronously.
    
    Returns a task_id that can be used to poll for status.
    Use this for comprehensive research that may take longer.
    """
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        user_id = str(current_user.get('id', ''))
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid user ID in authentication token")
        
        logger.info(f"[Research API] Start async request: {request.query[:50]}...")
        
        task_id = str(uuid.uuid4())
        
        # Initialize task
        _research_tasks[task_id] = {
            "status": "pending",
            "progress_messages": [],
            "result": None,
            "error": None,
        }
        
        # Start background task
        context = _convert_to_research_context(request, user_id)
        background_tasks.add_task(_run_research_task, task_id, context)
        
        return ResearchResponse(
            success=True,
            task_id=task_id,
        )
        
    except Exception as e:
        logger.error(f"[Research API] Start failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def _run_research_task(task_id: str, context: ResearchContext):
    """Background task to run research."""
    try:
        _research_tasks[task_id]["status"] = "running"
        
        def progress_callback(message: str):
            _research_tasks[task_id]["progress_messages"].append(message)
        
        engine = ResearchEngine()
        result = await engine.research(context, progress_callback=progress_callback)
        
        _research_tasks[task_id]["status"] = "completed"
        _research_tasks[task_id]["result"] = result
        
    except Exception as e:
        logger.error(f"[Research API] Task {task_id} failed: {e}")
        _research_tasks[task_id]["status"] = "failed"
        _research_tasks[task_id]["error"] = str(e)


@router.get("/status/{task_id}")
async def get_research_status(task_id: str):
    """
    Get status of an async research task.
    
    Poll this endpoint to get progress updates and final results.
    """
    if task_id not in _research_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = _research_tasks[task_id]
    
    response = {
        "task_id": task_id,
        "status": task["status"],
        "progress_messages": task["progress_messages"],
    }
    
    if task["status"] == "completed" and task["result"]:
        result = task["result"]
        response["result"] = {
            "success": result.success,
            "sources": result.sources,
            "keyword_analysis": result.keyword_analysis,
            "competitor_analysis": result.competitor_analysis,
            "suggested_angles": result.suggested_angles,
            "provider_used": result.provider_used,
            "search_queries": result.search_queries,
        }
        
        # Clean up completed task after returning
        # In production, use Redis or database for persistence
        
    elif task["status"] == "failed":
        response["error"] = task["error"]
    
    return response


@router.delete("/status/{task_id}")
async def cancel_research(task_id: str):
    """
    Cancel a running research task.
    """
    if task_id not in _research_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = _research_tasks[task_id]
    
    if task["status"] in ["pending", "running"]:
        task["status"] = "cancelled"
        return {"message": "Task cancelled", "task_id": task_id}
    
    return {"message": f"Task already {task['status']}", "task_id": task_id}


# ============================================================================
# Intent-Driven Research Endpoints
# ============================================================================

class AnalyzeIntentRequest(BaseModel):
    """Request to analyze user research intent."""
    user_input: str = Field(..., description="User's keywords, question, or goal")
    keywords: List[str] = Field(default_factory=list, description="Extracted keywords")
    use_persona: bool = Field(True, description="Use research persona for context")
    use_competitor_data: bool = Field(True, description="Use competitor data for context")


class AnalyzeIntentResponse(BaseModel):
    """Response from intent analysis."""
    success: bool
    intent: Dict[str, Any]
    analysis_summary: str
    suggested_queries: List[Dict[str, Any]]
    suggested_keywords: List[str]
    suggested_angles: List[str]
    quick_options: List[Dict[str, Any]]
    error_message: Optional[str] = None


class IntentDrivenResearchRequest(BaseModel):
    """Request for intent-driven research."""
    # Intent from previous analyze step, or minimal input for auto-inference
    user_input: str = Field(..., description="User's original input")
    
    # Optional: Confirmed intent from UI (if user modified the inferred intent)
    confirmed_intent: Optional[Dict[str, Any]] = None
    
    # Optional: Specific queries to run (if user selected from suggested)
    selected_queries: Optional[List[Dict[str, Any]]] = None
    
    # Research configuration
    max_sources: int = Field(default=10, ge=1, le=25)
    include_domains: List[str] = Field(default_factory=list)
    exclude_domains: List[str] = Field(default_factory=list)
    
    # Skip intent inference (for re-runs with same intent)
    skip_inference: bool = False


class IntentDrivenResearchResponse(BaseModel):
    """Response from intent-driven research."""
    success: bool
    
    # Direct answers
    primary_answer: str = ""
    secondary_answers: Dict[str, str] = Field(default_factory=dict)
    
    # Deliverables
    statistics: List[Dict[str, Any]] = Field(default_factory=list)
    expert_quotes: List[Dict[str, Any]] = Field(default_factory=list)
    case_studies: List[Dict[str, Any]] = Field(default_factory=list)
    trends: List[Dict[str, Any]] = Field(default_factory=list)
    comparisons: List[Dict[str, Any]] = Field(default_factory=list)
    best_practices: List[str] = Field(default_factory=list)
    step_by_step: List[str] = Field(default_factory=list)
    pros_cons: Optional[Dict[str, Any]] = None
    definitions: Dict[str, str] = Field(default_factory=dict)
    examples: List[str] = Field(default_factory=list)
    predictions: List[str] = Field(default_factory=list)
    
    # Content-ready outputs
    executive_summary: str = ""
    key_takeaways: List[str] = Field(default_factory=list)
    suggested_outline: List[str] = Field(default_factory=list)
    
    # Sources and metadata
    sources: List[Dict[str, Any]] = Field(default_factory=list)
    confidence: float = 0.8
    gaps_identified: List[str] = Field(default_factory=list)
    follow_up_queries: List[str] = Field(default_factory=list)
    
    # The inferred/confirmed intent
    intent: Optional[Dict[str, Any]] = None
    
    # Error handling
    error_message: Optional[str] = None


@router.post("/intent/analyze", response_model=AnalyzeIntentResponse)
async def analyze_research_intent(
    request: AnalyzeIntentRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Analyze user input to understand research intent.
    
    This endpoint uses AI to infer what the user really wants from their research:
    - What questions need answering
    - What deliverables they expect (statistics, quotes, case studies, etc.)
    - What depth and focus is appropriate
    
    The response includes quick options that can be shown in the UI for user confirmation.
    """
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        user_id = str(current_user.get('id', ''))
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid user ID")
        
        logger.info(f"[Intent API] Analyzing intent for: {request.user_input[:50]}...")
        
        # Get research persona if requested
        research_persona = None
        competitor_data = None
        
        if request.use_persona or request.use_competitor_data:
            from services.research.research_persona_service import ResearchPersonaService
            from services.onboarding_service import OnboardingService
            from sqlalchemy.orm import Session
            
            # Get database session
            db = next(get_db())
            try:
                persona_service = ResearchPersonaService(db)
                onboarding_service = OnboardingService()
                
                if request.use_persona:
                    research_persona = persona_service.get_or_generate(user_id)
                
                if request.use_competitor_data:
                    competitor_data = onboarding_service.get_competitor_analysis(user_id, db)
            finally:
                db.close()
        
        # Infer intent
        intent_service = ResearchIntentInference()
        response = await intent_service.infer_intent(
            user_input=request.user_input,
            keywords=request.keywords,
            research_persona=research_persona,
            competitor_data=competitor_data,
            industry=research_persona.default_industry if research_persona else None,
            target_audience=research_persona.default_target_audience if research_persona else None,
        )
        
        # Generate targeted queries
        query_generator = IntentQueryGenerator()
        query_result = await query_generator.generate_queries(
            intent=response.intent,
            research_persona=research_persona,
        )
        
        # Update response with queries
        response.suggested_queries = [q.dict() for q in query_result.get("queries", [])]
        response.suggested_keywords = query_result.get("enhanced_keywords", [])
        response.suggested_angles = query_result.get("research_angles", [])
        
        return AnalyzeIntentResponse(
            success=True,
            intent=response.intent.dict(),
            analysis_summary=response.analysis_summary,
            suggested_queries=response.suggested_queries,
            suggested_keywords=response.suggested_keywords,
            suggested_angles=response.suggested_angles,
            quick_options=response.quick_options,
        )
        
    except Exception as e:
        logger.error(f"[Intent API] Analyze failed: {e}")
        return AnalyzeIntentResponse(
            success=False,
            intent={},
            analysis_summary="",
            suggested_queries=[],
            suggested_keywords=[],
            suggested_angles=[],
            quick_options=[],
            error_message=str(e),
        )


@router.post("/intent/research", response_model=IntentDrivenResearchResponse)
async def execute_intent_driven_research(
    request: IntentDrivenResearchRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Execute research based on user intent.
    
    This is the main endpoint for intent-driven research. It:
    1. Uses the confirmed intent (or infers from user_input if not provided)
    2. Generates targeted queries for each expected deliverable
    3. Executes research using Exa/Tavily/Google
    4. Analyzes results through the lens of user intent
    5. Returns exactly what the user needs
    
    The response is organized by deliverable type (statistics, quotes, case studies, etc.)
    instead of generic search results.
    """
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        user_id = str(current_user.get('id', ''))
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid user ID")
        
        logger.info(f"[Intent API] Executing intent-driven research for: {request.user_input[:50]}...")
        
        # Get database session
        db = next(get_db())
        
        try:
            # Get research persona
            from services.research.research_persona_service import ResearchPersonaService
            persona_service = ResearchPersonaService(db)
            research_persona = persona_service.get_or_generate(user_id)
            
            # Determine intent
            if request.confirmed_intent:
                # Use confirmed intent from UI
                intent = ResearchIntent(**request.confirmed_intent)
            elif not request.skip_inference:
                # Infer intent from user input
                intent_service = ResearchIntentInference()
                intent_response = await intent_service.infer_intent(
                    user_input=request.user_input,
                    research_persona=research_persona,
                )
                intent = intent_response.intent
            else:
                # Create basic intent from input
                intent = ResearchIntent(
                    primary_question=f"What are the key insights about: {request.user_input}?",
                    purpose="learn",
                    content_output="general",
                    expected_deliverables=["key_statistics", "best_practices", "examples"],
                    depth="detailed",
                    original_input=request.user_input,
                    confidence=0.6,
                )
            
            # Generate or use provided queries
            if request.selected_queries:
                queries = [ResearchQuery(**q) for q in request.selected_queries]
            else:
                query_generator = IntentQueryGenerator()
                query_result = await query_generator.generate_queries(
                    intent=intent,
                    research_persona=research_persona,
                )
                queries = query_result.get("queries", [])
            
            # Execute research using the Research Engine
            engine = ResearchEngine(db_session=db)
            
            # Build context from intent
            personalization = ResearchPersonalizationContext(
                creator_id=user_id,
                industry=research_persona.default_industry if research_persona else None,
                target_audience=research_persona.default_target_audience if research_persona else None,
            )
            
            # Use the highest priority query for the main search
            # (In a more advanced version, we could run multiple queries and merge)
            primary_query = queries[0] if queries else ResearchQuery(
                query=request.user_input,
                purpose=ExpectedDeliverable.KEY_STATISTICS,
                provider="exa",
                priority=5,
                expected_results="General research results",
            )
            
            context = ResearchContext(
                query=primary_query.query,
                keywords=request.user_input.split()[:10],
                goal=_map_purpose_to_goal(intent.purpose),
                depth=_map_depth_to_engine_depth(intent.depth),
                provider_preference=_map_provider_to_preference(primary_query.provider),
                personalization=personalization,
                max_sources=request.max_sources,
                include_domains=request.include_domains,
                exclude_domains=request.exclude_domains,
            )
            
            # Execute research
            raw_result = await engine.research(context)
            
            # Analyze results using intent-aware analyzer
            analyzer = IntentAwareAnalyzer()
            analyzed_result = await analyzer.analyze(
                raw_results={
                    "content": raw_result.raw_content or "",
                    "sources": raw_result.sources,
                    "grounding_metadata": raw_result.grounding_metadata,
                },
                intent=intent,
                research_persona=research_persona,
            )
            
            # Build response
            return IntentDrivenResearchResponse(
                success=True,
                primary_answer=analyzed_result.primary_answer,
                secondary_answers=analyzed_result.secondary_answers,
                statistics=[s.dict() for s in analyzed_result.statistics],
                expert_quotes=[q.dict() for q in analyzed_result.expert_quotes],
                case_studies=[cs.dict() for cs in analyzed_result.case_studies],
                trends=[t.dict() for t in analyzed_result.trends],
                comparisons=[c.dict() for c in analyzed_result.comparisons],
                best_practices=analyzed_result.best_practices,
                step_by_step=analyzed_result.step_by_step,
                pros_cons=analyzed_result.pros_cons.dict() if analyzed_result.pros_cons else None,
                definitions=analyzed_result.definitions,
                examples=analyzed_result.examples,
                predictions=analyzed_result.predictions,
                executive_summary=analyzed_result.executive_summary,
                key_takeaways=analyzed_result.key_takeaways,
                suggested_outline=analyzed_result.suggested_outline,
                sources=[s.dict() for s in analyzed_result.sources],
                confidence=analyzed_result.confidence,
                gaps_identified=analyzed_result.gaps_identified,
                follow_up_queries=analyzed_result.follow_up_queries,
                intent=intent.dict(),
            )
            
        finally:
            db.close()
        
    except Exception as e:
        logger.error(f"[Intent API] Research failed: {e}")
        import traceback
        traceback.print_exc()
        return IntentDrivenResearchResponse(
            success=False,
            error_message=str(e),
        )


def _map_purpose_to_goal(purpose: str) -> ResearchGoal:
    """Map intent purpose to research goal."""
    mapping = {
        "learn": ResearchGoal.EDUCATIONAL,
        "create_content": ResearchGoal.FACTUAL,
        "make_decision": ResearchGoal.FACTUAL,
        "compare": ResearchGoal.COMPETITIVE,
        "solve_problem": ResearchGoal.EDUCATIONAL,
        "find_data": ResearchGoal.FACTUAL,
        "explore_trends": ResearchGoal.TRENDING,
        "validate": ResearchGoal.FACTUAL,
        "generate_ideas": ResearchGoal.INSPIRATIONAL,
    }
    return mapping.get(purpose, ResearchGoal.FACTUAL)


def _map_depth_to_engine_depth(depth: str) -> ResearchDepth:
    """Map intent depth to research engine depth."""
    mapping = {
        "overview": ResearchDepth.QUICK,
        "detailed": ResearchDepth.STANDARD,
        "expert": ResearchDepth.COMPREHENSIVE,
    }
    return mapping.get(depth, ResearchDepth.STANDARD)


def _map_provider_to_preference(provider: str) -> ProviderPreference:
    """Map query provider to engine preference."""
    mapping = {
        "exa": ProviderPreference.EXA,
        "tavily": ProviderPreference.TAVILY,
        "google": ProviderPreference.GOOGLE,
    }
    return mapping.get(provider, ProviderPreference.AUTO)

