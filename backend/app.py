# Ensure typing constructs and models are available globally for FastAPI type annotation evaluation
import typing
import builtins

# Make common typing constructs available globally
builtins.Optional = typing.Optional
builtins.List = typing.List
builtins.Dict = typing.Dict
builtins.Any = typing.Any
builtins.Union = typing.Union

# Load environment variables FIRST before any other imports
from pathlib import Path
from dotenv import load_dotenv
backend_dir = Path(__file__).parent
project_root = backend_dir.parent

# Load .env but DON'T override existing environment variables (especially PORT from Render)
# Use override=False to preserve Render-provided PORT
load_dotenv(backend_dir / '.env', override=False)
load_dotenv(project_root / '.env', override=False)
load_dotenv(override=False)

# Set LOG_LEVEL early to WARNING to suppress DEBUG persona logs in podcast mode
import os
if os.getenv("ALWRITY_ENABLED_FEATURES", "").strip().lower() == "podcast":
    os.environ["LOG_LEVEL"] = "WARNING"
    
print(f"[app.py] Starting... ALWRITY_ENABLED_FEATURES={os.getenv('ALWRITY_ENABLED_FEATURES')}", flush=True)


def get_enabled_features() -> set:
    """Get enabled features from ALWRITY_ENABLED_FEATURES env var."""
    env_value = os.getenv("ALWRITY_ENABLED_FEATURES", "all").strip().lower()
    if not env_value or env_value == "all":
        return {"all"}
    return {f.strip() for f in env_value.split(",") if f.strip()}


def is_podcast_only_demo_mode() -> bool:
    """Check if podcast-only mode is enabled."""
    enabled = get_enabled_features()
    return "podcast" in enabled and "all" not in enabled


# Import onboarding models (after env is loaded)
from models.onboarding import APIKey, WebsiteAnalysis, ResearchPreferences, PersonaData, CompetitorAnalysis


# Import FastAPI and related
from fastapi import FastAPI, HTTPException, Depends, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional
import os
import asyncio
from datetime import datetime
from loguru import logger

def _log_memory_usage():
    try:
        import psutil
        mem_mb = psutil.Process().memory_info().rss // (1024 * 1024)
        logger.info(f"Memory usage (MB): {mem_mb}")
    except Exception:
        # psutil not available or failed; skip silently
        pass

# Log memory early in app.py startup
_log_memory_usage()
logger.info("app.py: Early memory checkpoint after env load")


# Import modular utilities (skip OnboardingManager import in podcast-only mode)
from alwrity_utils import HealthChecker, RateLimiter, FrontendServing, RouterManager
if not is_podcast_only_demo_mode():
    from alwrity_utils import OnboardingManager

# Skip monitoring middleware in podcast-only mode to save memory
if not is_podcast_only_demo_mode():
    from services.subscription import monitoring_middleware
else:
    monitoring_middleware = None


def should_include_non_podcast_features() -> bool:
    """Check if non-podcast features should be included."""
    enabled = get_enabled_features()
    return "all" in enabled or "core" in enabled


# Legacy constant for backwards compatibility
PODCAST_ONLY_DEMO_MODE = is_podcast_only_demo_mode()


# Set up clean logging for end users
from logging_config import setup_clean_logging
setup_clean_logging()

# Import middleware
from middleware.auth_middleware import get_current_user

# Import component logic endpoints (needs OnboardingSession, so import after models)
from api.component_logic import router as component_logic_router

# Import subscription API endpoints
from api.subscription import router as subscription_router

# Import Step 3 onboarding routes (skip in podcast-only mode)
step3_routes = None
if not PODCAST_ONLY_DEMO_MODE:
    from api.onboarding_utils.step3_routes import router as step3_routes

# Import SEO tools router
from routers.seo_tools import router as seo_tools_router

# Skip Facebook Writer, LinkedIn, and other non-podcast routes in podcast-only mode
# Also skip other heavy services that trigger PersonaAnalysisService initialization
if not PODCAST_ONLY_DEMO_MODE:
    from api.facebook_writer.routers import facebook_router
    from routers.linkedin import router as linkedin_router
    from api.linkedin_image_generation import router as linkedin_image_router
    from api.brainstorm import router as brainstorm_router
    from api.images import router as images_router
    from api.assets_serving import router as assets_serving_router
    from routers.image_studio import router as image_studio_router
    from routers.product_marketing import router as product_marketing_router
    from routers.campaign_creator import router as campaign_creator_router
else:
    # In podcast-only mode, only load essential podcast assets router
    from api.assets_serving import router as assets_serving_router
    brainstorm_router = None
    images_router = None
    image_studio_router = None
    product_marketing_router = None
    campaign_creator_router = None

# Import hallucination detector router (skip in podcast-only mode - triggers heavy ML)
if not PODCAST_ONLY_DEMO_MODE:
    from api.hallucination_detector import router as hallucination_detector_router
    from api.writing_assistant import router as writing_assistant_router
else:
    hallucination_detector_router = None
    writing_assistant_router = None

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
from services.database import close_database
from services.startup_health import (
    get_startup_status,
    readiness_under_auth_context,
    run_startup_health_routine,
)

# Trigger reload for monitoring fix

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
    get_deep_competitor_analysis,
    run_strategic_insights,
    get_strategic_insights_history,
    refresh_analytics_data,
    analyze_urls_ai,
    AnalyzeURLsRequest,
    get_analyzed_pages,
    get_semantic_health,
    get_semantic_cache_stats,
    get_sif_indexing_health,
    get_onboarding_task_health,
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
    "https://alwrity-5vac2n9su-ajsis-projects.vercel.app",  # Current Vercel deployment
    "https://alwrity.vercel.app",  # Vercel app
]

# Optional dynamic origins from environment (comma-separated)
env_origins = os.getenv("ALWRITY_ALLOWED_ORIGINS", "").split(",") if os.getenv("ALWRITY_ALLOWED_ORIGINS") else []
env_origins = [o.strip() for o in env_origins if o.strip()]

# Convenience: NGROK_URL env var (single origin)
ngrok_origin = os.getenv("NGROK_URL")
if ngrok_origin:
    env_origins.append(ngrok_origin.strip())

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
router_group_status: Dict[str, Dict[str, Any]] = {}

onboarding_manager = None
# Only create OnboardingManager if NOT in podcast-only mode
if not PODCAST_ONLY_DEMO_MODE:
    from alwrity_utils import OnboardingManager
    onboarding_manager = OnboardingManager(app)

# Middleware Order (FastAPI executes in REVERSE order of registration - LIFO):
# Registration order:  1. Monitoring  2. Rate Limit  3. API Key Injection
# Execution order:     1. API Key Injection (sets user_id)  2. Rate Limit  3. Monitoring (uses user_id)

# 1. FIRST REGISTERED (runs LAST) - Monitoring middleware (skip in podcast-only mode)
if monitoring_middleware:
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
    health_data = health_checker.basic_health_check()
    health_data["podcast_only_demo_mode"] = PODCAST_ONLY_DEMO_MODE
    return health_data

@app.get("/health/database")
async def database_health():
    """Database health check endpoint."""
    return health_checker.database_health_check()

@app.get("/health/comprehensive")
async def comprehensive_health():
    """Comprehensive health check endpoint."""
    return health_checker.comprehensive_health_check()

@app.get("/health/readiness")
async def readiness(current_user: dict = Depends(get_current_user)):
    """Readiness check that validates tenant DB resolution/session under auth context."""
    return {
        "podcast_only_demo_mode": PODCAST_ONLY_DEMO_MODE,
        "startup": get_startup_status(),
        "tenant": readiness_under_auth_context(current_user),
    }

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
    status = router_manager.get_router_status()
    status.update(
        {
            "podcast_only_demo_mode": PODCAST_ONLY_DEMO_MODE,
            "router_groups": router_group_status,
        }
    )
    return status

@app.get("/api/feature-profile/status")
async def feature_profile_status():
    """Get feature profile status and enabled modules."""
    return router_manager.get_feature_profile_status()

# Onboarding management endpoints
@app.get("/api/onboarding/status")
async def onboarding_status():
    """Get onboarding manager status (or demo-mode disabled state)."""
    if PODCAST_ONLY_DEMO_MODE:
        return {
            "enabled": False,
            "status": "disabled",
            "message": "Onboarding is disabled for podcast-only demo mode.",
            "demo_mode": "podcast_only",
        }
    return onboarding_manager.get_onboarding_status()

# Include routers using modular utilities
if PODCAST_ONLY_DEMO_MODE:
    router_group_status["modular_core"] = {
        "mounted": False,
        "reason": "Skipped in podcast-only demo mode",
    }
    router_group_status["modular_optional"] = {
        "mounted": False,
        "reason": "Skipped in podcast-only demo mode",
    }
else:
    router_group_status["modular_core"] = {
        "mounted": router_manager.include_core_routers(),
        "reason": "Full mode",
    }
    router_group_status["modular_optional"] = {
        "mounted": router_manager.include_optional_routers(),
        "reason": "Full mode",
    }

# Log startup summary
router_manager.log_startup_summary()

# Safety net: keep subscription routes available even if core inclusion flow changes
# in special modes (e.g., demo mode). De-dup is handled by RouterManager.
router_manager.include_router_safely(subscription_router, "subscription")

# Include assets serving router (must be mounted to serve generated images)
app.include_router(assets_serving_router)
router_group_status["assets_serving"] = {
    "mounted": True,
    "reason": "Required for podcast media assets",
}

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

@app.get("/api/seo-dashboard/deep-competitor-analysis")
async def deep_competitor_analysis_endpoint(current_user: dict = Depends(get_current_user), site_url: str = None):
    """Get deep competitor analysis results (auto-scheduled post-onboarding)."""
    return await get_deep_competitor_analysis(current_user, site_url)

@app.post("/api/seo-dashboard/strategic-insights/run")
async def run_strategic_insights_endpoint(current_user: dict = Depends(get_current_user)):
    """Run AI-powered strategic insights analysis manually."""
    return await run_strategic_insights(current_user)

@app.get("/api/seo-dashboard/strategic-insights/history")
async def get_strategic_insights_history_endpoint(current_user: dict = Depends(get_current_user)):
    """Fetch the history of strategic insights for the user."""
    return await get_strategic_insights_history(current_user)

@app.post("/api/seo-dashboard/refresh")
async def refresh_analytics_data_endpoint(current_user: dict = Depends(get_current_user), site_url: str = None):
    """Refresh analytics data by invalidating cache and fetching fresh data."""
    return await refresh_analytics_data(current_user, site_url)



@app.get("/api/seo-dashboard/onboarding-task-health")
async def onboarding_task_health_endpoint(current_user: dict = Depends(get_current_user), site_url: str = None):
    """Get consolidated health for onboarding-scheduled SEO tasks."""
    return await get_onboarding_task_health(current_user, site_url)

@app.get("/api/seo-dashboard/health")
async def seo_dashboard_health():
    """Health check for SEO dashboard."""
    return await seo_dashboard_health_check()

# Phase 2B: Semantic health monitoring endpoint (24-hour polling)
@app.get("/api/seo-dashboard/semantic-health")
async def semantic_health_endpoint(current_user: dict = Depends(get_current_user)):
    """
    Get real-time semantic health metrics for content and competitors.
    This endpoint provides Phase 2B semantic intelligence monitoring data.
    
    Returns semantic health score, status, and recommendations.
    Data is cached and updated every 24 hours via scheduler.
    """
    return await get_semantic_health(current_user)


@app.get("/api/seo-dashboard/cache-stats")
async def semantic_cache_stats_endpoint(current_user: dict = Depends(get_current_user)):
    """
    Get semantic cache performance statistics.
    Returns hit rate, memory usage, and eviction counts.
    """
    return await get_semantic_cache_stats(current_user)


@app.get("/api/seo-dashboard/sif-health")
async def sif_indexing_health_endpoint(current_user: dict = Depends(get_current_user)):
    """
    Get SIF indexing health summary for the current user.
    Used by the Semantic Indexing Status widget on the dashboard.
    """
    return await get_sif_indexing_health(current_user)

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

@app.post("/api/seo-dashboard/analyze-urls-ai")
async def analyze_urls_ai_endpoint(request: AnalyzeURLsRequest, current_user: dict = Depends(get_current_user)):
    """Run AI-powered SEO analysis on selected URLs."""
    return await analyze_urls_ai(request, current_user)

# Include platform analytics router
if not PODCAST_ONLY_DEMO_MODE:
    from routers.platform_analytics import router as platform_analytics_router
    app.include_router(platform_analytics_router)
    # Include Bing Analytics Storage router to expose storage-backed endpoints
    from routers.bing_analytics_storage import router as bing_analytics_storage_router
    app.include_router(bing_analytics_storage_router)
    if images_router:
        app.include_router(images_router)
    if image_studio_router:
        app.include_router(image_studio_router)
    if product_marketing_router:
        app.include_router(product_marketing_router)
    if campaign_creator_router:
        app.include_router(campaign_creator_router)

    # Include content assets router
    from api.content_assets.router import router as content_assets_router
    app.include_router(content_assets_router)
    router_group_status["platform_extensions"] = {
        "mounted": True,
        "reason": "Full mode",
    }
else:
    router_group_status["platform_extensions"] = {
        "mounted": False,
        "reason": "Skipped in podcast-only demo mode",
    }

# Include Podcast Maker router (always needed for podcast mode)
from api.podcast.router import router as podcast_router
app.include_router(podcast_router)
router_group_status["podcast_maker"] = {
    "mounted": True,
    "reason": "Always mounted",
}

if not PODCAST_ONLY_DEMO_MODE:
    # Include YouTube Creator Studio router
    from api.youtube.router import router as youtube_router
    app.include_router(youtube_router, prefix="/api")

    # Include research configuration router
    app.include_router(research_config_router, prefix="/api/research", tags=["research"])

    # Include Research Engine router (standalone AI research module)
    from api.research.router import router as research_engine_router
    app.include_router(research_engine_router, tags=["Research Engine"])

    # Scheduler dashboard routes
    from api.scheduler_dashboard import router as scheduler_dashboard_router
    app.include_router(scheduler_dashboard_router)
    app.include_router(oauth_token_monitoring_router)

    # Autonomous Agents API routes (Phase 3A)
    from api.agents_api import router as agents_router
    app.include_router(agents_router)

    # Today workflow routes
    from api.today_workflow import router as today_workflow_router
    app.include_router(today_workflow_router)
    router_group_status["advanced_workflows"] = {
        "mounted": True,
        "reason": "Full mode",
    }
else:
    router_group_status["advanced_workflows"] = {
        "mounted": False,
        "reason": "Skipped in podcast-only demo mode",
    }

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
        _log_memory_usage()
        # Skip startup health checks in podcast-only mode to avoid unnecessary DB errors
        if not is_podcast_only_demo_mode():
            startup_report = run_startup_health_routine(app)
            if startup_report.get("status") != "healthy":
                logger.error(f"Startup readiness finished with failures: {startup_report.get('errors', [])}")
        else:
            logger.info("[Podcast] Skipping startup health routine (podcast-only mode)")

        # Start task scheduler only if NOT in podcast-only mode
        if not is_podcast_only_demo_mode():
            from services.scheduler import get_scheduler
            await get_scheduler().start()
        else:
            logger.info("[Podcast] Skipping scheduler startup (podcast-only mode)")

        # Check Wix API key configuration
        wix_api_key = os.getenv('WIX_API_KEY')
        if wix_api_key:
            logger.warning(f"✅ WIX_API_KEY loaded ({len(wix_api_key)} chars, starts with '{wix_api_key[:10]}...')")
        else:
            logger.warning("⚠️ WIX_API_KEY not found in environment - Wix publishing may fail")

        logger.info("ALwrity backend started successfully")
        
        # Critical router mount assertions for podcast-only demo mode
        _assert_router_mounted("subscription")
        _assert_router_mounted("podcast")
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        # Don't raise - let the server start anyway


def _assert_router_mounted(router_name: str) -> None:
    """Assert that a critical router is mounted. Fails startup if not found."""
    from fastapi import routing
    mounted_routes = [route.path for route in app.routes]
    
    # Check for router-specific paths
    router_path_indicators = {
        "subscription": ["/api/subscription/plans", "/api/subscription/preflight"],
        "podcast": ["/api/podcast/projects", "/api/podcast/"],
    }
    
    expected_paths = router_path_indicators.get(router_name, [])
    found = any(path in mounted_routes for path in expected_paths)
    
    if found:
        logger.info(f"✅ Critical router '{router_name}' is mounted")
    else:
        error_msg = f"❌ CRITICAL: Router '{router_name}' is NOT mounted! Expected paths: {expected_paths}"
        logger.error(error_msg)
        if PODCAST_ONLY_DEMO_MODE:
            # In demo mode, podcast router MUST be mounted
            if router_name == "podcast":
                raise RuntimeError(error_msg)

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
