# Ensure typing constructs and models are available globally for FastAPI type annotation evaluation
import typing
import builtins

# Make common typing constructs available globally
builtins.Optional = typing.Optional
builtins.List = typing.List
builtins.Dict = typing.Dict
builtins.Any = typing.Any
builtins.Union = typing.Union

# Import onboarding models VERY early to ensure they're available before any services
from models.onboarding import APIKey, WebsiteAnalysis, ResearchPreferences, PersonaData, CompetitorAnalysis


from fastapi import FastAPI, HTTPException, Depends, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional
import os
from loguru import logger
from dotenv import load_dotenv
import asyncio
from datetime import datetime

# Import OnboardingSession right after basic imports to ensure it's available
from models.onboarding import OnboardingSession

from services.subscription import monitoring_middleware

# Import remaining onboarding models
from models import APIKey, WebsiteAnalysis, ResearchPreferences, PersonaData, CompetitorAnalysis

# Import modular utilities
from alwrity_utils import HealthChecker, RateLimiter, FrontendServing, RouterManager
from alwrity_utils import OnboardingManager

# Load environment variables
# Try multiple locations for .env file
from pathlib import Path
backend_dir = Path(__file__).parent
project_root = backend_dir.parent

# Load from backend/.env first (higher priority), then root .env
load_dotenv(backend_dir / '.env')  # backend/.env
load_dotenv(project_root / '.env')  # root .env (fallback)
load_dotenv()  # CWD .env (fallback)

# Set up clean logging for end users
from logging_config import setup_clean_logging
setup_clean_logging()

# Import middleware
from middleware.auth_middleware import get_current_user

# Import component logic endpoints (needs OnboardingSession, so import after models)
from api.component_logic import router as component_logic_router

# Import subscription API endpoints
from api.subscription import router as subscription_router

# Import Step 3 onboarding routes
from api.onboarding_utils.step3_routes import router as step3_routes

# Import SEO tools router
from routers.seo_tools import router as seo_tools_router
# Import Facebook Writer endpoints
from api.facebook_writer.routers import facebook_router
# Import LinkedIn content generation router
from routers.linkedin import router as linkedin_router
# Import LinkedIn image generation router
from api.linkedin_image_generation import router as linkedin_image_router
from api.brainstorm import router as brainstorm_router
from api.images import router as images_router
from routers.image_studio import router as image_studio_router
from routers.product_marketing import router as product_marketing_router
from routers.campaign_creator import router as campaign_creator_router

# Import hallucination detector router
from api.hallucination_detector import router as hallucination_detector_router
from api.writing_assistant import router as writing_assistant_router

# Import research configuration router
from api.research_config import router as research_config_router

# Import user data endpoints
# Import content planning endpoints
from api.content_planning.api.router import router as content_planning_router
from api.user_data import router as user_data_router

# Import user environment endpoints
from api.user_environment import router as user_environment_router

# Import strategy copilot endpoints
from api.content_planning.strategy_copilot import router as strategy_copilot_router

# Import database service
from services.database import init_database, close_database

# Import OAuth token monitoring routes
from api.oauth_token_monitoring_routes import router as oauth_token_monitoring_router

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
    SEOAnalysisRequest,
    get_seo_dashboard_overview,
    get_gsc_raw_data,
    get_bing_raw_data,
    get_competitive_insights,
    refresh_analytics_data
)

# Initialize FastAPI app
app = FastAPI(
    title="ALwrity Backend API",
    description="Backend API for ALwrity - AI-powered content creation platform",
    version="1.0.0"
)

# Add CORS middleware
# Build allowed origins list with env overrides to support dynamic tunnels (e.g., ngrok)
default_allowed_origins = [
    "http://localhost:3000",  # React dev server
    "http://localhost:8000",  # Backend dev server
    "http://localhost:3001",  # Alternative React port
    "https://alwrity-ai.vercel.app",  # Vercel frontend
]

# Optional dynamic origins from environment (comma-separated)
env_origins = os.getenv("ALWRITY_ALLOWED_ORIGINS", "").split(",") if os.getenv("ALWRITY_ALLOWED_ORIGINS") else []
env_origins = [o.strip() for o in env_origins if o.strip()]

# Convenience: NGROK_URL env var (single origin)
ngrok_origin = os.getenv("NGROK_URL")
if ngrok_origin:
    env_origins.append(ngrok_origin.strip())

allowed_origins = list(dict.fromkeys(default_allowed_origins + env_origins))  # de-duplicate, keep order

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize modular utilities
health_checker = HealthChecker()
rate_limiter = RateLimiter(window_seconds=60, max_requests=200)
frontend_serving = FrontendServing(app)
router_manager = RouterManager(app)

onboarding_manager = OnboardingManager(app)

# Middleware Order (FastAPI executes in REVERSE order of registration - LIFO):
# Registration order:  1. Monitoring  2. Rate Limit  3. API Key Injection
# Execution order:     1. API Key Injection (sets user_id)  2. Rate Limit  3. Monitoring (uses user_id)

# 1. FIRST REGISTERED (runs LAST) - Monitoring middleware
app.middleware("http")(monitoring_middleware)

# 2. SECOND REGISTERED (runs SECOND) - Rate limiting
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware using modular utilities."""
    return await rate_limiter.rate_limit_middleware(request, call_next)

# 3. LAST REGISTERED (runs FIRST) - API key injection
from middleware.api_key_injection_middleware import api_key_injection_middleware
app.middleware("http")(api_key_injection_middleware)

# Health check endpoints using modular utilities
@app.get("/health")
async def health():
    """Health check endpoint."""
    return health_checker.basic_health_check()

@app.get("/health/database")
async def database_health():
    """Database health check endpoint."""
    return health_checker.database_health_check()

@app.get("/health/comprehensive")
async def comprehensive_health():
    """Comprehensive health check endpoint."""
    return health_checker.comprehensive_health_check()

# Rate limiting management endpoints
@app.get("/api/rate-limit/status")
async def rate_limit_status(request: Request):
    """Get current rate limit status for the requesting client."""
    client_ip = request.client.host if request.client else "unknown"
    return rate_limiter.get_rate_limit_status(client_ip)

@app.post("/api/rate-limit/reset")
async def reset_rate_limit(request: Request, client_ip: Optional[str] = None):
    """Reset rate limit for a specific client or all clients."""
    if client_ip is None:
        client_ip = request.client.host if request.client else "unknown"
    return rate_limiter.reset_rate_limit(client_ip)

# Frontend serving management endpoints
@app.get("/api/frontend/status")
async def frontend_status():
    """Get frontend serving status."""
    return frontend_serving.get_frontend_status()

# Router management endpoints
@app.get("/api/routers/status")
async def router_status():
    """Get router inclusion status."""
    return router_manager.get_router_status()

# Onboarding management endpoints
@app.get("/api/onboarding/status")
async def onboarding_status():
    """Get onboarding manager status."""
    return onboarding_manager.get_onboarding_status()

# Include routers using modular utilities
router_manager.include_core_routers()
router_manager.include_optional_routers()

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
async def seo_platforms(current_user: dict = Depends(get_current_user)):
    """Get platform status."""
    return await get_platform_status(current_user)

@app.get("/api/seo-dashboard/insights")
async def seo_insights():
    """Get AI insights."""
    return await get_ai_insights()

# New SEO Dashboard endpoints with real data
@app.get("/api/seo-dashboard/overview")
async def seo_dashboard_overview_endpoint(current_user: dict = Depends(get_current_user), site_url: str = None):
    """Get comprehensive SEO dashboard overview with real GSC/Bing data."""
    return await get_seo_dashboard_overview(current_user, site_url)

@app.get("/api/seo-dashboard/gsc/raw")
async def gsc_raw_data_endpoint(current_user: dict = Depends(get_current_user), site_url: str = None):
    """Get raw GSC data for the specified site."""
    return await get_gsc_raw_data(current_user, site_url)

@app.get("/api/seo-dashboard/bing/raw")
async def bing_raw_data_endpoint(current_user: dict = Depends(get_current_user), site_url: str = None):
    """Get raw Bing data for the specified site."""
    return await get_bing_raw_data(current_user, site_url)

@app.get("/api/seo-dashboard/competitive-insights")
async def competitive_insights_endpoint(current_user: dict = Depends(get_current_user), site_url: str = None):
    """Get competitive insights from onboarding step 3 data."""
    return await get_competitive_insights(current_user, site_url)

@app.post("/api/seo-dashboard/refresh")
async def refresh_analytics_data_endpoint(current_user: dict = Depends(get_current_user), site_url: str = None):
    """Refresh analytics data by invalidating cache and fetching fresh data."""
    return await refresh_analytics_data(current_user, site_url)

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

# Include platform analytics router
from routers.platform_analytics import router as platform_analytics_router
app.include_router(platform_analytics_router)
app.include_router(images_router)
app.include_router(image_studio_router)
app.include_router(product_marketing_router)
app.include_router(campaign_creator_router)

# Include content assets router
from api.content_assets.router import router as content_assets_router
app.include_router(content_assets_router)

# Include Podcast Maker router
from api.podcast.router import router as podcast_router
app.include_router(podcast_router)

# Include YouTube Creator Studio router
from api.youtube import router as youtube_router
app.include_router(youtube_router, prefix="/api")

# Include research configuration router
app.include_router(research_config_router, prefix="/api/research", tags=["research"])

# Include Research Engine router (standalone AI research module)
from api.research.router import router as research_engine_router
app.include_router(research_engine_router, tags=["Research Engine"])

# Scheduler dashboard routes
from api.scheduler import router as scheduler_router
app.include_router(scheduler_router)
app.include_router(oauth_token_monitoring_router)

# Include scheduler monitoring API
from api.scheduler_monitoring import router as scheduler_monitoring_router
app.include_router(scheduler_monitoring_router)

# Setup frontend serving using modular utilities
frontend_serving.setup_frontend_serving()

# Serve React frontend (for production)
@app.get("/")
async def serve_frontend():
    """Serve the React frontend."""
    return frontend_serving.serve_frontend()

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    try:
        # Initialize database
        init_database()
        
        # Start task scheduler
        from services.scheduler import get_scheduler
        await get_scheduler().start()
        
        # Check Wix API key configuration
        wix_api_key = os.getenv('WIX_API_KEY')
        if wix_api_key:
            logger.warning(f"✅ WIX_API_KEY loaded ({len(wix_api_key)} chars, starts with '{wix_api_key[:10]}...')")
        else:
            logger.warning("⚠️ WIX_API_KEY not found in environment - Wix publishing may fail")
        
        logger.info("ALwrity backend started successfully")
    except Exception as e:
        logger.error(f"Error during startup: {e}")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    try:
        # Stop task scheduler
        from services.scheduler import get_scheduler
        await get_scheduler().stop()
        
        # Close database connections
        close_database()
        logger.info("ALwrity backend shutdown successfully")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}") 
