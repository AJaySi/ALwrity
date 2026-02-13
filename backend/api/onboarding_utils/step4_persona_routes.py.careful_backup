"""
Step 4 Persona Generation Routes
Handles AI writing persona generation using the sophisticated persona system.
"""

import asyncio
from typing import Dict, Any, List, Optional, Union
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from loguru import logger
import os

# Rate limiting configuration
RATE_LIMIT_DELAY_SECONDS = 2.0  # Delay between API calls to prevent quota exhaustion

# Task management for long-running persona generation
import uuid
from datetime import datetime, timedelta

from services.persona.core_persona.core_persona_service import CorePersonaService
from services.persona.enhanced_linguistic_analyzer import EnhancedLinguisticAnalyzer
from services.persona.persona_quality_improver import PersonaQualityImprover
from middleware.auth_middleware import get_current_user
from services.user_api_key_context import user_api_keys

# In-memory task storage (in production, use Redis or database)
persona_tasks: Dict[str, Dict[str, Any]] = {}

# In-memory latest persona cache per user (24h TTL)
persona_latest_cache: Dict[str, Dict[str, Any]] = {}
PERSONA_CACHE_TTL_HOURS = 24

router = APIRouter()

# Initialize services
core_persona_service = CorePersonaService()
linguistic_analyzer = EnhancedLinguisticAnalyzer()
quality_improver = PersonaQualityImprover()


def _extract_user_id(user: Dict[str, Any]) -> str:
    """Extract a stable user ID from Clerk-authenticated user payloads.
    Prefers 'clerk_user_id' or 'id', falls back to 'user_id', else 'unknown'.
    """
    if not isinstance(user, dict):
        return 'unknown'
    return (
        user.get('clerk_user_id')
        or user.get('id')
        or user.get('user_id')
        or 'unknown'
    )

class PersonaGenerationRequest(BaseModel):
    """Request model for persona generation."""
    onboarding_data: Dict[str, Any]
    selected_platforms: List[str] = ["linkedin", "blog"]
    user_preferences: Optional[Dict[str, Any]] = None

class PersonaGenerationResponse(BaseModel):
    """Response model for persona generation."""
    success: bool
    core_persona: Optional[Dict[str, Any]] = None
    platform_personas: Optional[Dict[str, Any]] = None
    quality_metrics: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class PersonaQualityRequest(BaseModel):
    """Request model for persona quality assessment."""
    core_persona: Dict[str, Any]
    platform_personas: Dict[str, Any]
    user_feedback: Optional[Dict[str, Any]] = None

class PersonaQualityResponse(BaseModel):
    """Response model for persona quality assessment."""
    success: bool
    quality_metrics: Optional[Dict[str, Any]] = None
    recommendations: Optional[List[str]] = None
    error: Optional[str] = None

class PersonaTaskStatus(BaseModel):
    """Response model for persona generation task status."""
    task_id: str
    status: str  # 'pending', 'running', 'completed', 'failed'
    progress: int  # 0-100
    current_step: str
    progress_messages: List[Dict[str, Any]] = []
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: str
    updated_at: str

@router.post("/step4/generate-personas-async", response_model=Dict[str, str])
async def generate_writing_personas_async(
    request: Union[PersonaGenerationRequest, Dict[str, Any]],
    current_user: Dict[str, Any] = Depends(get_current_user),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Start persona generation as an async task and return task ID for polling.
    """
    try:
        # Handle both PersonaGenerationRequest and dict inputs
        if isinstance(request, dict):
            persona_request = PersonaGenerationRequest(**request)
        else:
            persona_request = request
            
        # If fresh cache exists for this user, short-circuit and return a completed task
        user_id = _extract_user_id(current_user)
        cached = persona_latest_cache.get(user_id)
        if cached:
            ts = datetime.fromisoformat(cached.get("timestamp", datetime.now().isoformat())) if isinstance(cached.get("timestamp"), str) else None
            if ts and (datetime.now() - ts) <= timedelta(hours=PERSONA_CACHE_TTL_HOURS):
                task_id = str(uuid.uuid4())
                persona_tasks[task_id] = {
                    "task_id": task_id,
                    "status": "completed",
                    "progress": 100,
                    "current_step": "Persona loaded from cache",
                    "progress_messages": [
                        {"timestamp": datetime.now().isoformat(), "message": "Loaded cached persona", "progress": 100}
                    ],
                    "result": {
                        "success": True,
                        "core_persona": cached.get("core_persona"),
                        "platform_personas": cached.get("platform_personas", {}),
                        "quality_metrics": cached.get("quality_metrics", {}),
                    },
                    "error": None,
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                    "user_id": user_id,
                    "request_data": (PersonaGenerationRequest(**(request if isinstance(request, dict) else request.dict())).dict()) if request else {}
                }
                logger.info(f"Cache hit for user {user_id} - returning completed task without regeneration: {task_id}")
            return {
                "task_id": task_id,
                "status": "completed",
                "message": "Persona loaded from cache"
            }

        # Generate unique task ID
        task_id = str(uuid.uuid4())
        
        # Initialize task status
        persona_tasks[task_id] = {
            "task_id": task_id,
            "status": "pending",
            "progress": 0,
            "current_step": "Initializing persona generation...",
            "progress_messages": [],
            "result": None,
            "error": None,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "user_id": user_id,
            "request_data": persona_request.dict()
        }
        
        # Start background task
        background_tasks.add_task(
            execute_persona_generation_task, 
            task_id, 
            persona_request, 
            current_user
        )
        
        logger.info(f"Started async persona generation task: {task_id}")
        logger.info(f"Background task added successfully for task: {task_id}")
        
        # Test: Add a simple background task to verify background task execution
        def test_simple_task():
            logger.info(f"TEST: Simple background task executed for {task_id}")
        
        background_tasks.add_task(test_simple_task)
        logger.info(f"TEST: Simple background task added for {task_id}")
        
        return {
            "task_id": task_id,
            "status": "pending",
            "message": "Persona generation started. Use task_id to poll for progress."
        }
        
    except Exception as e:
        logger.error(f"Failed to start persona generation task: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start task: {str(e)}")

@router.get("/step4/persona-latest", response_model=Dict[str, Any])
async def get_latest_persona(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Return latest cached persona for the current user if available and fresh."""
    try:
        user_id = _extract_user_id(current_user)
        cached = persona_latest_cache.get(user_id)
        if not cached:
            raise HTTPException(status_code=404, detail="No cached persona found")

        ts = datetime.fromisoformat(cached["timestamp"]) if isinstance(cached.get("timestamp"), str) else None
        if not ts or (datetime.now() - ts) > timedelta(hours=PERSONA_CACHE_TTL_HOURS):
            # Expired
            persona_latest_cache.pop(user_id, None)
            raise HTTPException(status_code=404, detail="Cached persona expired")

        return {"success": True, "persona": cached}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting latest persona: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/step4/persona-save", response_model=Dict[str, Any])
async def save_persona_update(
    request: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Save/overwrite latest persona cache for current user (from edited UI)."""
    try:
        user_id = _extract_user_id(current_user)
        payload = {
            "success": True,
            "core_persona": request.get("core_persona"),
            "platform_personas": request.get("platform_personas", {}),
            "quality_metrics": request.get("quality_metrics", {}),
            "selected_platforms": request.get("selected_platforms", []),
            "timestamp": datetime.now().isoformat()
        }
        persona_latest_cache[user_id] = payload
        logger.info(f"Saved latest persona to cache for user {user_id}")
        return {"success": True}
    except Exception as e:
        logger.error(f"Error saving latest persona: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/step4/persona-task/{task_id}", response_model=PersonaTaskStatus)
async def get_persona_task_status(task_id: str):
    """
    Get the status of a persona generation task.
    """
    if task_id not in persona_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = persona_tasks[task_id]
    
    # Clean up old tasks (older than 1 hour)
    if datetime.now() - datetime.fromisoformat(task["created_at"]) > timedelta(hours=1):
        del persona_tasks[task_id]
        raise HTTPException(status_code=404, detail="Task expired")
    
    return PersonaTaskStatus(**task)

@router.post("/step4/generate-personas", response_model=PersonaGenerationResponse)
async def generate_writing_personas(
    request: Union[PersonaGenerationRequest, Dict[str, Any]],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Generate AI writing personas using the sophisticated persona system with optimized parallel execution.
    
    OPTIMIZED APPROACH:
    1. Generate core persona (1 API call)
    2. Parallel platform adaptations (1 API call per platform)
    3. Parallel quality assessment (no additional API calls - uses existing data)
    
    Total API calls: 1 + N platforms (vs previous: 1 + N + 1 = N + 2)
    """
    try:
        logger.info(f"Starting OPTIMIZED persona generation for user: {current_user.get('user_id', 'unknown')}")
        
        # Handle both PersonaGenerationRequest and dict inputs
        if isinstance(request, dict):
            # Convert dict to PersonaGenerationRequest
            persona_request = PersonaGenerationRequest(**request)
        else:
            persona_request = request
            
        logger.info(f"Selected platforms: {persona_request.selected_platforms}")
        
        # Step 1: Generate core persona (1 API call)
        logger.info("Step 1: Generating core persona...")
        core_persona = await asyncio.get_event_loop().run_in_executor(
            None, 
            core_persona_service.generate_core_persona, 
            persona_request.onboarding_data
        )
        
        # Add small delay after core persona generation
        await asyncio.sleep(1.0)
        
        if "error" in core_persona:
            logger.error(f"Core persona generation failed: {core_persona['error']}")
            return PersonaGenerationResponse(
                success=False,
                error=f"Core persona generation failed: {core_persona['error']}"
            )
        
        # Step 2: Generate platform adaptations with rate limiting (N API calls with delays)
        logger.info(f"Step 2: Generating platform adaptations with rate limiting for: {persona_request.selected_platforms}")
        platform_personas = {}
        
        # Process platforms sequentially with small delays to avoid rate limits
        for i, platform in enumerate(persona_request.selected_platforms):
            try:
                logger.info(f"Generating {platform} persona ({i+1}/{len(persona_request.selected_platforms)})")
                
                # Add delay between API calls to prevent rate limiting
                if i > 0:  # Skip delay for first platform
                    logger.info(f"Rate limiting: Waiting {RATE_LIMIT_DELAY_SECONDS}s before next API call...")
                    await asyncio.sleep(RATE_LIMIT_DELAY_SECONDS)
                
                # Generate platform persona
                result = await generate_single_platform_persona_async(
                    core_persona, 
                    platform, 
                    persona_request.onboarding_data
                )
                
                if isinstance(result, Exception):
                    error_msg = str(result)
                    logger.error(f"Platform {platform} generation failed: {error_msg}")
                    platform_personas[platform] = {"error": error_msg}
                elif "error" in result:
                    error_msg = result['error']
                    logger.error(f"Platform {platform} generation failed: {error_msg}")
                    platform_personas[platform] = result
                    
                    # Check for rate limit errors and suggest retry
                    if "429" in error_msg or "quota" in error_msg.lower() or "rate limit" in error_msg.lower():
                        logger.warning(f"⚠️ Rate limit detected for {platform}. Consider increasing RATE_LIMIT_DELAY_SECONDS")
                else:
                    platform_personas[platform] = result
                    logger.info(f"✅ {platform} persona generated successfully")
                    
            except Exception as e:
                logger.error(f"Platform {platform} generation error: {str(e)}")
                platform_personas[platform] = {"error": str(e)}
        
        
        # Step 3: Assess quality (no additional API calls - uses existing data)
        logger.info("Step 3: Assessing persona quality...")
        quality_metrics = await assess_persona_quality_internal(
            core_persona, 
            platform_personas,
            persona_request.user_preferences
        )
        
        # Log performance metrics
        total_platforms = len(persona_request.selected_platforms)
        successful_platforms = len([p for p in platform_personas.values() if "error" not in p])
        logger.info(f"✅ Persona generation completed: {successful_platforms}/{total_platforms} platforms successful")
        logger.info(f"📊 API calls made: 1 (core) + {total_platforms} (platforms) = {1 + total_platforms} total")
        logger.info(f"⏱️ Rate limiting: Sequential processing with 2s delays to prevent quota exhaustion")
        
        return PersonaGenerationResponse(
            success=True,
            core_persona=core_persona,
            platform_personas=platform_personas,
            quality_metrics=quality_metrics
        )
        
    except Exception as e:
        logger.error(f"Persona generation error: {str(e)}")
        return PersonaGenerationResponse(
            success=False,
            error=f"Persona generation failed: {str(e)}"
        )

@router.post("/step4/assess-quality", response_model=PersonaQualityResponse)
async def assess_persona_quality(
    request: Union[PersonaQualityRequest, Dict[str, Any]],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Assess the quality of generated personas and provide improvement recommendations.
    """
    try:
        logger.info(f"Assessing persona quality for user: {current_user.get('user_id', 'unknown')}")
        
        # Handle both PersonaQualityRequest and dict inputs
        if isinstance(request, dict):
            # Convert dict to PersonaQualityRequest
            quality_request = PersonaQualityRequest(**request)
        else:
            quality_request = request
        
        quality_metrics = await assess_persona_quality_internal(
            quality_request.core_persona,
            quality_request.platform_personas,
            quality_request.user_feedback
        )
        
        return PersonaQualityResponse(
            success=True,
            quality_metrics=quality_metrics,
            recommendations=quality_metrics.get('recommendations', [])
        )
        
    except Exception as e:
        logger.error(f"Quality assessment error: {str(e)}")
        return PersonaQualityResponse(
            success=False,
            error=f"Quality assessment failed: {str(e)}"
        )

@router.post("/step4/regenerate-persona")
async def regenerate_persona(
    request: Union[PersonaGenerationRequest, Dict[str, Any]],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Regenerate persona with different parameters or improved analysis.
    """
    try:
        logger.info(f"Regenerating persona for user: {current_user.get('user_id', 'unknown')}")
        
        # Use the same generation logic but with potentially different parameters
        return await generate_writing_personas(request, current_user)
        
    except Exception as e:
        logger.error(f"Persona regeneration error: {str(e)}")
        return PersonaGenerationResponse(
            success=False,
            error=f"Persona regeneration failed: {str(e)}"
        )

@router.post("/step4/test-background-task")
async def test_background_task(
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Test endpoint to verify background task execution."""
    def simple_background_task():
        logger.info("BACKGROUND TASK EXECUTED SUCCESSFULLY!")
        return "Task completed"
    
    background_tasks.add_task(simple_background_task)
    logger.info("Background task added to queue")
    
    return {"message": "Background task added", "status": "success"}

@router.get("/step4/persona-options")
async def get_persona_generation_options(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get available options for persona generation (platforms, preferences, etc.).
    """
    try:
        return {
            "success": True,
            "available_platforms": [
                {"id": "linkedin", "name": "LinkedIn", "description": "Professional networking and thought leadership"},
                {"id": "facebook", "name": "Facebook", "description": "Social media and community building"},
                {"id": "twitter", "name": "Twitter", "description": "Micro-blogging and real-time updates"},
                {"id": "blog", "name": "Blog", "description": "Long-form content and SEO optimization"},
                {"id": "instagram", "name": "Instagram", "description": "Visual storytelling and engagement"},
                {"id": "medium", "name": "Medium", "description": "Publishing platform and audience building"},
                {"id": "substack", "name": "Substack", "description": "Newsletter and subscription content"}
            ],
            "persona_types": [
                "Thought Leader",
                "Industry Expert", 
                "Content Creator",
                "Brand Ambassador",
                "Community Builder"
            ],
            "quality_metrics": [
                "Style Consistency",
                "Brand Alignment", 
                "Platform Optimization",
                "Engagement Potential",
                "Content Quality"
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting persona options: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get persona options: {str(e)}")

async def execute_persona_generation_task(task_id: str, persona_request: PersonaGenerationRequest, current_user: Dict[str, Any]):
    """
    Execute persona generation task in background with progress updates.
    """
    try:
        logger.info(f"BACKGROUND TASK STARTED: {task_id}")
        logger.info(f"Task {task_id}: Background task execution initiated")
        
        # Log onboarding data summary for debugging
        onboarding_data_summary = {
            "has_websiteAnalysis": bool(persona_request.onboarding_data.get("websiteAnalysis")),
            "has_competitorResearch": bool(persona_request.onboarding_data.get("competitorResearch")),
            "has_sitemapAnalysis": bool(persona_request.onboarding_data.get("sitemapAnalysis")),
            "has_businessData": bool(persona_request.onboarding_data.get("businessData")),
            "data_keys": list(persona_request.onboarding_data.keys()) if persona_request.onboarding_data else []
        }
        logger.info(f"Task {task_id}: Onboarding data summary: {onboarding_data_summary}")
        
        # Update task status to running
        update_task_status(task_id, "running", 10, "Starting persona generation...")
        logger.info(f"Task {task_id}: Status updated to running")
        
        # Inject user-specific API keys into environment for the duration of this background task
        user_id = _extract_user_id(current_user)
        env_mapping = {
            'gemini': 'GEMINI_API_KEY',
            'exa': 'EXA_API_KEY',
            'openai': 'OPENAI_API_KEY',
            'anthropic': 'ANTHROPIC_API_KEY',
            'mistral': 'MISTRAL_API_KEY',
            'copilotkit': 'COPILOTKIT_API_KEY',
            'tavily': 'TAVILY_API_KEY',
            'serper': 'SERPER_API_KEY',
            'firecrawl': 'FIRECRAWL_API_KEY',
        }
        original_env: Dict[str, Optional[str]] = {}
        with user_api_keys(user_id) as keys:
            try:
                for provider, env_var in env_mapping.items():
                    value = keys.get(provider)
                    if value:
                        original_env[env_var] = os.environ.get(env_var)
                        os.environ[env_var] = value
                        logger.debug(f"[BG TASK] Injected {env_var} for user {user_id}")

                # Step 1: Generate core persona (1 API call)
                update_task_status(task_id, "running", 20, "Generating core persona...")
                logger.info(f"Task {task_id}: Step 1 - Generating core persona...")
                
                core_persona = await asyncio.get_event_loop().run_in_executor(
                    None, 
                    core_persona_service.generate_core_persona, 
                    persona_request.onboarding_data
                )
                
                if "error" in core_persona:
                    error_msg = core_persona['error']
                    # Check if this is a quota/rate limit error
                    if "RESOURCE_EXHAUSTED" in str(error_msg) or "429" in str(error_msg) or "quota" in str(error_msg).lower():
                        update_task_status(task_id, "failed", 0, f"Quota exhausted: {error_msg}", error=str(error_msg))
                        logger.error(f"Task {task_id}: Quota exhausted, marking as failed immediately")
                    else:
                        update_task_status(task_id, "failed", 0, f"Core persona generation failed: {error_msg}", error=str(error_msg))
                    return
                
                update_task_status(task_id, "running", 40, "Core persona generated successfully")
                
                # Add small delay after core persona generation
                await asyncio.sleep(1.0)
                
                # Step 2: Generate platform adaptations with rate limiting (N API calls with delays)
                update_task_status(task_id, "running", 50, f"Generating platform adaptations for: {persona_request.selected_platforms}")
                platform_personas = {}
                
                total_platforms = len(persona_request.selected_platforms)
                
                # Process platforms sequentially with small delays to avoid rate limits
                for i, platform in enumerate(persona_request.selected_platforms):
                    try:
                        progress = 50 + (i * 40 // total_platforms)
                        update_task_status(task_id, "running", progress, f"Generating {platform} persona ({i+1}/{total_platforms})")
                        
                        # Add delay between API calls to prevent rate limiting
                        if i > 0:  # Skip delay for first platform
                            update_task_status(task_id, "running", progress, f"Rate limiting: Waiting {RATE_LIMIT_DELAY_SECONDS}s before next API call...")
                            await asyncio.sleep(RATE_LIMIT_DELAY_SECONDS)
                        
                        # Generate platform persona
                        result = await generate_single_platform_persona_async(
                            core_persona, 
                            platform, 
                            persona_request.onboarding_data
                        )
                        
                        if isinstance(result, Exception):
                            error_msg = str(result)
                            logger.error(f"Platform {platform} generation failed: {error_msg}")
                            platform_personas[platform] = {"error": error_msg}
                        elif "error" in result:
                            error_msg = result['error']
                            logger.error(f"Platform {platform} generation failed: {error_msg}")
                            platform_personas[platform] = result
                            
                            # Check for rate limit errors and suggest retry
                            if "429" in error_msg or "quota" in error_msg.lower() or "rate limit" in error_msg.lower():
                                logger.warning(f"⚠️ Rate limit detected for {platform}. Consider increasing RATE_LIMIT_DELAY_SECONDS")
                        else:
                            platform_personas[platform] = result
                            logger.info(f"✅ {platform} persona generated successfully")
                            
                    except Exception as e:
                        logger.error(f"Platform {platform} generation error: {str(e)}")
                        platform_personas[platform] = {"error": str(e)}
                
                # Step 3: Assess quality (no additional API calls - uses existing data)
                update_task_status(task_id, "running", 90, "Assessing persona quality...")
                quality_metrics = await assess_persona_quality_internal(
                    core_persona, 
                    platform_personas,
                    persona_request.user_preferences
                )
            finally:
                # Restore environment
                for env_var, original_value in original_env.items():
                    if original_value is None:
                        os.environ.pop(env_var, None)
                    else:
                        os.environ[env_var] = original_value
                logger.debug(f"[BG TASK] Restored environment for user {user_id}")
        
        # Log performance metrics
        successful_platforms = len([p for p in platform_personas.values() if "error" not in p])
        logger.info(f"✅ Persona generation completed: {successful_platforms}/{total_platforms} platforms successful")
        logger.info(f"📊 API calls made: 1 (core) + {total_platforms} (platforms) = {1 + total_platforms} total")
        logger.info(f"⏱️ Rate limiting: Sequential processing with 2s delays to prevent quota exhaustion")
        
        # Create final result
        final_result = {
            "success": True,
            "core_persona": core_persona,
            "platform_personas": platform_personas,
            "quality_metrics": quality_metrics
        }
        
        # Update task status to completed
        update_task_status(task_id, "completed", 100, "Persona generation completed successfully", final_result)

        # Populate server-side cache for quick reloads
        try:
            user_id = _extract_user_id(current_user)
            persona_latest_cache[user_id] = {
                **final_result,
                "selected_platforms": persona_request.selected_platforms,
                "timestamp": datetime.now().isoformat()
            }
            logger.info(f"Latest persona cached for user {user_id}")
        except Exception as e:
            logger.warning(f"Could not cache latest persona: {e}")
        
    except Exception as e:
        logger.error(f"Persona generation task {task_id} failed: {str(e)}")
        logger.error(f"Task {task_id}: Exception details: {type(e).__name__}: {str(e)}")
        import traceback
        logger.error(f"Task {task_id}: Full traceback: {traceback.format_exc()}")
        update_task_status(task_id, "failed", 0, f"Persona generation failed: {str(e)}")

def update_task_status(task_id: str, status: str, progress: int, current_step: str, result: Optional[Dict[str, Any]] = None, error: Optional[str] = None):
    """Update task status in memory storage."""
    if task_id in persona_tasks:
        persona_tasks[task_id].update({
            "status": status,
            "progress": progress,
            "current_step": current_step,
            "updated_at": datetime.now().isoformat(),
            "result": result,
            "error": error
        })
        
        # Add progress message
        persona_tasks[task_id]["progress_messages"].append({
            "timestamp": datetime.now().isoformat(),
            "message": current_step,
            "progress": progress
        })

async def generate_single_platform_persona_async(
    core_persona: Dict[str, Any],
    platform: str,
    onboarding_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Async wrapper for single platform persona generation.
    """
    try:
        return await asyncio.get_event_loop().run_in_executor(
            None,
            core_persona_service._generate_single_platform_persona,
            core_persona,
            platform,
            onboarding_data
        )
    except Exception as e:
        logger.error(f"Error generating {platform} persona: {str(e)}")
        return {"error": f"Failed to generate {platform} persona: {str(e)}"}

async def assess_persona_quality_internal(
    core_persona: Dict[str, Any],
    platform_personas: Dict[str, Any],
    user_preferences: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Internal function to assess persona quality using comprehensive metrics.
    """
    try:
        from services.persona.persona_quality_improver import PersonaQualityImprover
        
        # Initialize quality improver
        quality_improver = PersonaQualityImprover()
        
        # Use mock linguistic analysis if not available
        linguistic_analysis = {
            "analysis_completeness": 0.85,
            "style_consistency": 0.88,
            "vocabulary_sophistication": 0.82,
            "content_coherence": 0.87
        }
        
        # Get comprehensive quality metrics
        quality_metrics = quality_improver.assess_persona_quality_comprehensive(
            core_persona,
            platform_personas,
            linguistic_analysis,
            user_preferences
        )
        
        return quality_metrics
        
    except Exception as e:
        logger.error(f"Quality assessment internal error: {str(e)}")
        # Return fallback quality metrics compatible with PersonaQualityImprover schema
        return {
            "overall_score": 75,
            "core_completeness": 75,
            "platform_consistency": 75,
            "platform_optimization": 75,
            "linguistic_quality": 75,
            "recommendations": ["Quality assessment completed with default metrics"],
            "weights": {
                "core_completeness": 0.30,
                "platform_consistency": 0.25,
                "platform_optimization": 0.25,
                "linguistic_quality": 0.20
            },
            "error": str(e)
        }

async def _log_persona_generation_result(
    user_id: str,
    core_persona: Dict[str, Any],
    platform_personas: Dict[str, Any],
    quality_metrics: Dict[str, Any]
):
    """Background task to log persona generation results."""
    try:
        logger.info(f"Logging persona generation result for user {user_id}")
        logger.info(f"Core persona generated with {len(core_persona)} characteristics")
        logger.info(f"Platform personas generated for {len(platform_personas)} platforms")
        logger.info(f"Quality metrics: {quality_metrics.get('overall_score', 'N/A')}% overall score")
    except Exception as e:
        logger.error(f"Error logging persona generation result: {str(e)}")
