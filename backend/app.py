"""Main FastAPI application for ALwrity backend."""

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
from middleware.monitoring_middleware import monitoring_middleware

# Import modular utilities
from alwrity_utils import HealthChecker, RateLimiter, FrontendServing, RouterManager, OnboardingManager

# Load environment variables
load_dotenv()

# Import middleware
from middleware.auth_middleware import get_current_user

# Import component logic endpoints
from api.component_logic import router as component_logic_router

# Import subscription API endpoints
from api.subscription_api import router as subscription_router

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

# Import hallucination detector router
from api.hallucination_detector import router as hallucination_detector_router
from api.writing_assistant import router as writing_assistant_router

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
        "https://alwrity-ai.vercel.app",
        "https://littery-sonny-unscrutinisingly.ngrok-free.dev",  # ngrok frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add API monitoring middleware
# Temporarily disabled for Wix testing
# app.middleware("http")(monitoring_middleware)

# Initialize modular utilities
health_checker = HealthChecker()
rate_limiter = RateLimiter(window_seconds=60, max_requests=200)
frontend_serving = FrontendServing(app)
router_manager = RouterManager(app)
onboarding_manager = OnboardingManager(app)

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware using modular utilities."""
    return await rate_limiter.rate_limit_middleware(request, call_next)

# API key injection middleware for production (user-specific keys)
@app.middleware("http")
async def inject_user_api_keys(request: Request, call_next):
    """
    Inject user-specific API keys into environment for the request duration.
    This allows existing code using os.getenv() to work in production.
    """
    from middleware.api_key_injection_middleware import api_key_injection_middleware
    return await api_key_injection_middleware(request, call_next)

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
