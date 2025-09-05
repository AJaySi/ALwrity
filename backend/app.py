"""Main FastAPI application for ALwrity backend."""

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional
import os
import time
from collections import defaultdict
from loguru import logger
from dotenv import load_dotenv
import asyncio
from datetime import datetime
from middleware.monitoring_middleware import monitoring_middleware

# Load environment variables
load_dotenv()

# Import the new enhanced functions
from api.onboarding import (
    health_check,
    get_onboarding_status,
    get_onboarding_progress_full,
    get_step_data,
    complete_step,
    skip_step,
    validate_step_access,
    get_api_keys,
    save_api_key,
    validate_api_keys,
    start_onboarding,
    complete_onboarding,
    reset_onboarding,
    get_resume_info,
    get_onboarding_config,
    get_provider_setup_info,
    get_all_providers_info,
    validate_provider_key,
    get_enhanced_validation_status,
    get_onboarding_summary,
    get_website_analysis_data,
    get_research_preferences_data,
    StepCompletionRequest,
    APIKeyRequest
)

# Import component logic endpoints
from api.component_logic import router as component_logic_router

# Import subscription API endpoints
from api.subscription_api import router as subscription_router

# Import SEO tools router
from routers.seo_tools import router as seo_tools_router
# Import Facebook Writer endpoints
from api.facebook_writer.routers import facebook_router
# Import LinkedIn content generation router
from routers.linkedin import router as linkedin_router
# Import LinkedIn image generation router
from api.linkedin_image_generation import router as linkedin_image_router
from api.brainstorm import router as brainstorm_router

# Import hallucination detector router
from api.hallucination_detector import router as hallucination_detector_router
from api.writing_assistant import router as writing_assistant_router

# Import user data endpoints
# Import content planning endpoints
from api.content_planning.api.router import router as content_planning_router
from api.user_data import router as user_data_router

# Import strategy copilot endpoints
from api.content_planning.strategy_copilot import router as strategy_copilot_router

# Import database service
from services.database import init_database, close_database

# Import SEO Dashboard endpoints
from api.seo_dashboard import (
    get_seo_dashboard_data,
    get_seo_health_score,
    get_seo_metrics,
    get_platform_status,
    get_ai_insights,
    seo_dashboard_health_check,
    analyze_seo_comprehensive,
    analyze_seo_full,
    get_seo_metrics_detailed,
    get_analysis_summary,
    batch_analyze_urls,
    SEOAnalysisRequest
)

# Initialize FastAPI app
app = FastAPI(
    title="ALwrity Backend API",
    description="Backend API for ALwrity - AI-powered content creation platform",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://localhost:8000",  # Backend dev server
        "http://localhost:3001",  # Alternative React port
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add API monitoring middleware
app.middleware("http")(monitoring_middleware)

# Simple rate limiting
request_counts = defaultdict(list)
RATE_LIMIT_WINDOW = 60  # 60 seconds
RATE_LIMIT_MAX_REQUESTS = 200  # Increased for testing - calendar generation polling

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Simple rate limiting middleware with exemptions for streaming endpoints."""
    try:
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()
        
        # Exempt streaming endpoints and frequently called endpoints from rate limiting
        path = request.url.path
        if any(streaming_path in path for streaming_path in [
            "/stream/strategies",
            "/stream/strategic-intelligence", 
            "/stream/keyword-research",
            "/latest-strategy",  # Exempt latest strategy endpoint from rate limiting
            "/ai-analytics",     # Exempt AI analytics endpoint from rate limiting
            "/gap-analysis",     # Exempt gap analysis endpoint from rate limiting
            "/calendar-events",  # Exempt calendar events endpoint from rate limiting
            "/calendar-generation/progress",  # Exempt calendar generation progress from rate limiting
            "/health"           # Exempt health check endpoints from rate limiting
        ]):
            # Allow streaming endpoints without rate limiting
            response = await call_next(request)
            return response
        
        # Clean old requests
        request_counts[client_ip] = [req_time for req_time in request_counts[client_ip] 
                                    if current_time - req_time < RATE_LIMIT_WINDOW]
        
        # Check rate limit
        if len(request_counts[client_ip]) >= RATE_LIMIT_MAX_REQUESTS:
            logger.warning(f"Rate limit exceeded for {client_ip}")
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests", "retry_after": RATE_LIMIT_WINDOW},
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "*",
                    "Access-Control-Allow-Headers": "*"
                }
            )
        
        # Add current request
        request_counts[client_ip].append(current_time)
        
        response = await call_next(request)
        return response
        
    except Exception as e:
        logger.error(f"Error in rate limiting middleware: {e}")
        # Continue without rate limiting if there's an error
        response = await call_next(request)
        return response

# Health check endpoint
@app.get("/health")
async def health():
    """Health check endpoint."""
    return health_check()

@app.get("/health/database")
async def database_health_check():
    """Database health check endpoint including persona tables verification."""
    try:
        from services.database import get_db_session
        from models.persona_models import WritingPersona, PlatformPersona, PersonaAnalysisResult, PersonaValidationResult
        
        session = get_db_session()
        if not session:
            return {"status": "error", "message": "Could not get database session"}
        
        # Test all persona tables
        tables_status = {}
        try:
            session.query(WritingPersona).first()
            tables_status["writing_personas"] = "ok"
        except Exception as e:
            tables_status["writing_personas"] = f"error: {str(e)}"
        
        try:
            session.query(PlatformPersona).first()
            tables_status["platform_personas"] = "ok"
        except Exception as e:
            tables_status["platform_personas"] = f"error: {str(e)}"
        
        try:
            session.query(PersonaAnalysisResult).first()
            tables_status["persona_analysis_results"] = "ok"
        except Exception as e:
            tables_status["persona_analysis_results"] = f"error: {str(e)}"
        
        try:
            session.query(PersonaValidationResult).first()
            tables_status["persona_validation_results"] = "ok"
        except Exception as e:
            tables_status["persona_validation_results"] = f"error: {str(e)}"
        
        session.close()
        
        # Check if all tables are ok
        all_ok = all(status == "ok" for status in tables_status.values())
        
        return {
            "status": "healthy" if all_ok else "warning",
            "message": "Database connection successful" if all_ok else "Some persona tables may have issues",
            "persona_tables": tables_status,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Database health check failed: {str(e)}",
            "timestamp": datetime.utcnow().isoformat()
        }

# Onboarding status endpoints
@app.get("/api/onboarding/status")
async def onboarding_status():
    """Get the current onboarding status."""
    try:
        return await get_onboarding_status()
    except Exception as e:
        logger.error(f"Error in onboarding_status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/onboarding/progress")
async def onboarding_progress():
    """Get the full onboarding progress data."""
    try:
        return await get_onboarding_progress_full()
    except Exception as e:
        logger.error(f"Error in onboarding_progress: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Step management endpoints
@app.get("/api/onboarding/step/{step_number}")
async def step_data(step_number: int):
    """Get data for a specific step."""
    try:
        return await get_step_data(step_number)
    except Exception as e:
        logger.error(f"Error in step_data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/onboarding/step/{step_number}/complete")
async def step_complete(step_number: int, request: StepCompletionRequest):
    """Mark a step as completed."""
    try:
        return await complete_step(step_number, request)
    except Exception as e:
        logger.error(f"Error in step_complete: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/onboarding/step/{step_number}/skip")
async def step_skip(step_number: int):
    """Skip a step (for optional steps)."""
    try:
        return await skip_step(step_number)
    except Exception as e:
        logger.error(f"Error in step_skip: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/onboarding/step/{step_number}/validate")
async def step_validate(step_number: int):
    """Validate if user can access a specific step."""
    try:
        return await validate_step_access(step_number)
    except Exception as e:
        logger.error(f"Error in step_validate: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# API key management endpoints
@app.get("/api/onboarding/api-keys")
async def api_keys():
    """Get all configured API keys (masked)."""
    try:
        return await get_api_keys()
    except Exception as e:
        logger.error(f"Error in api_keys: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/onboarding/api-keys")
async def api_key_save(request: APIKeyRequest):
    """Save an API key for a provider."""
    try:
        return await save_api_key(request)
    except Exception as e:
        logger.error(f"Error in api_key_save: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/onboarding/api-keys/validate")
async def api_key_validate():
    """Validate all configured API keys."""
    try:
        return await validate_api_keys()
    except Exception as e:
        logger.error(f"Error in api_key_validate: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Onboarding control endpoints
@app.post("/api/onboarding/start")
async def onboarding_start():
    """Start a new onboarding session."""
    try:
        return await start_onboarding()
    except Exception as e:
        logger.error(f"Error in onboarding_start: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/onboarding/complete")
async def onboarding_complete():
    """Complete the onboarding process."""
    try:
        return await complete_onboarding()
    except Exception as e:
        logger.error(f"Error in onboarding_complete: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/onboarding/reset")
async def onboarding_reset():
    """Reset the onboarding progress."""
    try:
        return await reset_onboarding()
    except Exception as e:
        logger.error(f"Error in onboarding_reset: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Resume functionality
@app.get("/api/onboarding/resume")
async def onboarding_resume():
    """Get information for resuming onboarding."""
    try:
        return await get_resume_info()
    except Exception as e:
        logger.error(f"Error in onboarding_resume: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Configuration endpoints
@app.get("/api/onboarding/config")
async def onboarding_config():
    """Get onboarding configuration and requirements."""
    try:
        return get_onboarding_config()
    except Exception as e:
        logger.error(f"Error in onboarding_config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Enhanced provider endpoints
@app.get("/api/onboarding/providers/{provider}/setup")
async def provider_setup_info(provider: str):
    """Get setup information for a specific provider."""
    try:
        return await get_provider_setup_info(provider)
    except Exception as e:
        logger.error(f"Error in provider_setup_info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/onboarding/providers")
async def all_providers_info():
    """Get setup information for all providers."""
    try:
        return await get_all_providers_info()
    except Exception as e:
        logger.error(f"Error in all_providers_info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/onboarding/providers/{provider}/validate")
async def validate_provider_key_endpoint(provider: str, request: APIKeyRequest):
    """Validate a specific provider's API key."""
    try:
        return await validate_provider_key(provider, request)
    except Exception as e:
        logger.error(f"Error in validate_provider_key: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/onboarding/validation/enhanced")
async def enhanced_validation_status():
    """Get enhanced validation status for all configured services."""
    try:
        return await get_enhanced_validation_status()
    except Exception as e:
        logger.error(f"Error in enhanced_validation_status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# New endpoints for FinalStep data loading
@app.get("/api/onboarding/summary")
async def onboarding_summary():
    """Get comprehensive onboarding summary for FinalStep."""
    try:
        return await get_onboarding_summary()
    except Exception as e:
        logger.error(f"Error in onboarding_summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/onboarding/website-analysis")
async def website_analysis_data():
    """Get website analysis data for FinalStep."""
    try:
        return await get_website_analysis_data()
    except Exception as e:
        logger.error(f"Error in website_analysis_data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/onboarding/research-preferences")
async def research_preferences_data():
    """Get research preferences data for FinalStep."""
    try:
        return await get_research_preferences_data()
    except Exception as e:
        logger.error(f"Error in research_preferences_data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Include component logic router
app.include_router(component_logic_router)

# Include subscription and usage tracking router
app.include_router(subscription_router)

# Include GSC router
from routers.gsc_auth import router as gsc_auth_router
app.include_router(gsc_auth_router)

# Include SEO tools router
app.include_router(seo_tools_router)
# Include Facebook Writer router
app.include_router(facebook_router)
# Include LinkedIn content generation router
app.include_router(linkedin_router)
# Include LinkedIn image generation router
app.include_router(linkedin_image_router)
app.include_router(brainstorm_router)

# Include hallucination detector router
app.include_router(hallucination_detector_router)
app.include_router(writing_assistant_router)

# Include user data router
# Include content planning router
app.include_router(content_planning_router)
app.include_router(user_data_router)
app.include_router(strategy_copilot_router)

# Include AI Blog Writer router
try:
    from api.blog_writer.router import router as blog_writer_router
    app.include_router(blog_writer_router)
except Exception as e:
    logger.warning(f"AI Blog Writer router not mounted: {e}")

# Include Blog Writer SEO Analysis router (comprehensive SEO analysis)
try:
    from api.blog_writer.seo_analysis import router as blog_seo_analysis_router
    app.include_router(blog_seo_analysis_router)
except Exception as e:
    logger.warning(f"Blog Writer SEO Analysis router not mounted: {e}")

# Include persona router
from api.persona_routes import router as persona_router
app.include_router(persona_router)

# Include Stability AI routers
from routers.stability import router as stability_router
from routers.stability_advanced import router as stability_advanced_router
from routers.stability_admin import router as stability_admin_router
app.include_router(stability_router)
app.include_router(stability_advanced_router)
app.include_router(stability_admin_router)

# SEO Dashboard endpoints
@app.get("/api/seo-dashboard/data")
async def seo_dashboard_data():
    """Get complete SEO dashboard data."""
    return await get_seo_dashboard_data()

@app.get("/api/seo-dashboard/health-score")
async def seo_health_score():
    """Get SEO health score."""
    return await get_seo_health_score()

@app.get("/api/seo-dashboard/metrics")
async def seo_metrics():
    """Get SEO metrics."""
    return await get_seo_metrics()

@app.get("/api/seo-dashboard/platforms")
async def seo_platforms():
    """Get platform status."""
    return await get_platform_status()

@app.get("/api/seo-dashboard/insights")
async def seo_insights():
    """Get AI insights."""
    return await get_ai_insights()

@app.get("/api/seo-dashboard/health")
async def seo_dashboard_health():
    """Health check for SEO dashboard."""
    return await seo_dashboard_health_check()

# Comprehensive SEO Analysis endpoints
@app.post("/api/seo-dashboard/analyze-comprehensive")
async def analyze_seo_comprehensive_endpoint(request: SEOAnalysisRequest):
    """Analyze a URL for comprehensive SEO performance."""
    return await analyze_seo_comprehensive(request)

@app.post("/api/seo-dashboard/analyze-full")
async def analyze_seo_full_endpoint(request: SEOAnalysisRequest):
    """Analyze a URL for comprehensive SEO performance."""
    return await analyze_seo_full(request)

@app.get("/api/seo-dashboard/metrics-detailed")
async def seo_metrics_detailed(url: str):
    """Get detailed SEO metrics for a URL."""
    return await get_seo_metrics_detailed(url)

@app.get("/api/seo-dashboard/analysis-summary")
async def seo_analysis_summary(url: str):
    """Get a quick summary of SEO analysis for a URL."""
    return await get_analysis_summary(url)

@app.post("/api/seo-dashboard/batch-analyze")
async def batch_analyze_urls_endpoint(urls: list[str]):
    """Analyze multiple URLs in batch."""
    return await batch_analyze_urls(urls)

# Serve React frontend (for production)
@app.get("/")
async def serve_frontend():
    """Serve the React frontend."""
    # Check if frontend build exists
    frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "build")
    index_html = os.path.join(frontend_path, "index.html")
    
    if os.path.exists(index_html):
        return FileResponse(index_html)
    else:
        return {
            "message": "Frontend not built. Please run 'npm run build' in the frontend directory.",
            "api_docs": "/api/docs"
        }

# Mount static files for React app (only if directory exists)
try:
    frontend_build_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "build")
    static_path = os.path.join(frontend_build_path, "static")
    if os.path.exists(static_path):
        app.mount("/static", StaticFiles(directory=static_path), name="static")
        logger.info("Frontend static files mounted successfully")
    else:
        logger.info("Frontend build directory not found. Static files not mounted.")
except Exception as e:
    logger.info(f"Could not mount static files: {e}")

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    try:
        # Initialize database
        init_database()
        logger.info("ALwrity backend started successfully")
    except Exception as e:
        logger.error(f"Error during startup: {e}")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    try:
        # Close database connections
        close_database()
        logger.info("ALwrity backend shutdown successfully")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}") 
