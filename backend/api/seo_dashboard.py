"""SEO Dashboard API endpoints for ALwrity."""

from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import os
from utils.logging import get_logger
logger = get_logger("seo_dashboard_api", migration_mode=True)
import time

# Import existing services
from services.onboarding.api_key_manager import APIKeyManager
from services.validation import check_all_api_keys
from services.seo_analyzer import ComprehensiveSEOAnalyzer, SEOAnalysisResult, SEOAnalysisService
from services.user_data_service import UserDataService
from services.database import get_db_session, get_session_for_user
from services.seo import SEODashboardService
from middleware.auth_middleware import get_current_user
from services.llm_providers.main_text_generation import llm_text_gen
from api.content_planning.services.content_strategy.onboarding import OnboardingDataIntegrationService
from models.onboarding import SEOPageAudit, WebsiteAnalysis, OnboardingSession
from sqlalchemy.orm.attributes import flag_modified

# Phase 2B: Import semantic monitoring
from services.intelligence.monitoring.semantic_dashboard import RealTimeSemanticMonitor, SemanticHealthMetric

# Initialize the SEO analyzer
seo_analyzer = ComprehensiveSEOAnalyzer()

# Pydantic models for SEO Dashboard
class SEOHealthScore(BaseModel):
    score: int
    change: int
    trend: str
    label: str
    color: str

class SEOMetric(BaseModel):
    value: float
    change: float
    trend: str
    description: str
    color: str

class PlatformStatus(BaseModel):
    status: str
    connected: bool
    last_sync: Optional[str] = None
    data_points: Optional[int] = None

class AIInsight(BaseModel):
    insight: str
    priority: str
    category: str
    action_required: bool
    tool_path: Optional[str] = None

class SEODashboardData(BaseModel):
    health_score: SEOHealthScore
    key_insight: str
    priority_alert: str
    metrics: Dict[str, SEOMetric]
    platforms: Dict[str, PlatformStatus]
    ai_insights: List[AIInsight]
    last_updated: str
    website_url: Optional[str] = None  # User's website URL from onboarding

# New models for comprehensive SEO analysis
class SEOAnalysisRequest(BaseModel):
    url: str
    target_keywords: Optional[List[str]] = None

class AnalyzeURLsRequest(BaseModel):
    urls: List[str]

class SEOAnalysisResponse(BaseModel):
    url: str
    timestamp: datetime
    overall_score: int
    health_status: str
    critical_issues: List[Dict[str, Any]]
    warnings: List[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]
    data: Dict[str, Any]
    success: bool
    message: str

class SEOMetricsResponse(BaseModel):
    metrics: Dict[str, Any]
    critical_issues: List[Dict[str, Any]]
    warnings: List[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]
    detailed_analysis: Dict[str, Any]
    timestamp: str
    url: str

# Mock data for Phase 1
def get_mock_seo_data() -> SEODashboardData:
    """Get mock SEO dashboard data for Phase 1."""
    # Try to get the user's website URL from the database
    website_url = None
    db_session = get_db_session()
    if db_session:
        try:
            user_data_service = UserDataService(db_session)
            website_url = user_data_service.get_user_website_url()
            logger.info(f"Retrieved website URL from database: {website_url}")
        except Exception as e:
            logger.error(f"Error fetching website URL from database: {e}")
        finally:
            db_session.close()
    
    return SEODashboardData(
        health_score=SEOHealthScore(
            score=78,
            change=12,
            trend="up",
            label="Good",
            color="#FF9800"
        ),
        key_insight="Your content strategy is working! Focus on technical SEO to reach 90+ score",
        priority_alert="Mobile speed needs attention - 2.8s load time",
        website_url=website_url,  # Include the user's website URL
        metrics={
            "traffic": SEOMetric(
                value=23450,
                change=23,
                trend="up",
                description="Strong growth!",
                color="#4CAF50"
            ),
            "rankings": SEOMetric(
                value=8,
                change=8,
                trend="up",
                description="Great work on content",
                color="#2196F3"
            ),
            "mobile": SEOMetric(
                value=2.8,
                change=-0.3,
                trend="down",
                description="Needs attention",
                color="#FF9800"
            ),
            "keywords": SEOMetric(
                value=156,
                change=5,
                trend="up",
                description="5 new opportunities",
                color="#9C27B0"
            )
        },
        platforms={
            "google_search_console": PlatformStatus(
                status="excellent",
                connected=True,
                last_sync="2024-01-15T10:30:00Z",
                data_points=1250
            ),
            "google_analytics": PlatformStatus(
                status="good",
                connected=True,
                last_sync="2024-01-15T10:25:00Z",
                data_points=890
            ),
            "bing_webmaster": PlatformStatus(
                status="needs_attention",
                connected=False,
                last_sync=None,
                data_points=0
            )
        },
        ai_insights=[
            AIInsight(
                insight="Your mobile page speed is 2.8s - optimize images and enable compression",
                priority="high",
                category="performance",
                action_required=True,
                tool_path="/seo-tools/page-speed-optimizer"
            ),
            AIInsight(
                insight="Add structured data to improve rich snippet opportunities",
                priority="medium",
                category="technical",
                action_required=False,
                tool_path="/seo-tools/schema-generator"
            ),
            AIInsight(
                insight="Content quality score improved by 15% - great work!",
                priority="low",
                category="content",
                action_required=False
            )
        ],
        last_updated="2024-01-15T10:30:00Z"
    )

def calculate_health_score(metrics: Dict[str, Any]) -> SEOHealthScore:
    """Calculate SEO health score based on metrics."""
    # This would be replaced with actual calculation logic
    base_score = 75
    change = 12
    trend = "up"
    label = "Good"
    color = "#FF9800"
    
    return SEOHealthScore(
        score=base_score,
        change=change,
        trend=trend,
        label=label,
        color=color
    )

def generate_ai_insights(metrics: Dict[str, Any], platforms: Dict[str, Any]) -> List[AIInsight]:
    """Generate AI-powered insights based on metrics and platform data."""
    insights = []
    
    # Performance insights
    if metrics.get("mobile", {}).get("value", 0) > 2.5:
        insights.append(AIInsight(
            insight="Mobile page speed needs optimization - aim for under 2 seconds",
            priority="high",
            category="performance",
            action_required=True,
            tool_path="/seo-tools/page-speed-optimizer"
        ))
    
    # Technical insights
    if not platforms.get("google_search_console", {}).get("connected", False):
        insights.append(AIInsight(
            insight="Connect Google Search Console for better SEO monitoring",
            priority="medium",
            category="technical",
            action_required=True,
            tool_path="/seo-tools/search-console-setup"
        ))
    
    # Content insights
    if metrics.get("rankings", {}).get("change", 0) > 0:
        insights.append(AIInsight(
            insight="Rankings are improving - continue with current content strategy",
            priority="low",
            category="content",
            action_required=False
        ))
    
    return insights

from services.seo.deep_competitor_analysis_service import DeepCompetitorAnalysisService

# API Endpoints
async def run_strategic_insights(
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Manually trigger AI-Powered Competitive Insights (Weekly Strategy Brief).
    """
    try:
        user_id = str(current_user.get('id'))
        db_session = get_db_session(user_id)
        
        if not db_session:
            raise HTTPException(status_code=500, detail="Database connection unavailable")
            
        try:
            # 1. Get Website Analysis (with fallback)
            website_analysis_data = None
            analysis_id = None
            
            # Try SSOT first
            integration_service = OnboardingDataIntegrationService()
            integrated_data = integration_service.get_integrated_data_sync(user_id, db_session)
            if integrated_data and integrated_data.get("website_analysis"):
                 website_analysis_data = integrated_data.get("website_analysis")
                 analysis_id = website_analysis_data.get("id")
            
            # Fallback: Find latest WebsiteAnalysis across sessions
            if not website_analysis_data:
                latest_analysis = db_session.query(WebsiteAnalysis).join(
                    OnboardingSession, WebsiteAnalysis.session_id == OnboardingSession.id
                ).filter(
                    OnboardingSession.user_id == user_id
                ).order_by(WebsiteAnalysis.updated_at.desc()).first()
                
                if latest_analysis:
                    # Convert to dict
                    from fastapi.encoders import jsonable_encoder
                    website_analysis_data = jsonable_encoder(latest_analysis)
                    analysis_id = latest_analysis.id
            
            if not website_analysis_data:
                raise HTTPException(status_code=400, detail="No website analysis found. Please complete Onboarding Step 2.")

            # 2. Get Competitors
            competitors = []
            if integrated_data:
                competitors = integrated_data.get("competitor_analysis", [])
                
            if not competitors:
                 # Fallback to research preferences
                 research_prefs = integrated_data.get("research_preferences", {})
                 competitors = research_prefs.get("competitors", [])

            if not competitors:
                 raise HTTPException(status_code=400, detail="No competitors found. Please complete Onboarding Step 3.")

            # 3. Run Analysis
            service = DeepCompetitorAnalysisService()
            report = await service.generate_weekly_strategy_brief(
                user_id=user_id,
                website_analysis=website_analysis_data,
                competitors=competitors
            )
            
            # 4. Persist to History
            if analysis_id:
                wa = db_session.query(WebsiteAnalysis).filter(WebsiteAnalysis.id == analysis_id).first()
                if wa:
                    history = wa.strategic_insights_history or []
                    # Ensure history is a list
                    if not isinstance(history, list):
                        history = []
                    
                    # Prepend new report
                    history.insert(0, report)
                    
                    # Keep last 52 weeks
                    wa.strategic_insights_history = history[:52]
                    flag_modified(wa, "strategic_insights_history")
                    db_session.commit()
            
            return report

        finally:
            db_session.close()

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error running strategic insights: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to run analysis: {str(e)}")

async def get_seo_dashboard_data(current_user: dict = Depends(get_current_user)) -> SEODashboardData:
    """Get comprehensive SEO dashboard data."""
    try:
        user_id = str(current_user.get('id'))
        db_session = get_db_session(user_id)
        
        if not db_session:
            logger.error("No database session available")
            return get_mock_seo_data()
        
        try:
            # Use new SEO dashboard service
            dashboard_service = SEODashboardService(db_session)
            overview_data = await dashboard_service.get_dashboard_overview(user_id)
            
            # Convert to SEODashboardData format
            return SEODashboardData(
                health_score=SEOHealthScore(**overview_data.get("health_score", {})),
                key_insight=overview_data.get("key_insight", "Connect your analytics accounts for personalized insights"),
                priority_alert=overview_data.get("priority_alert", "No alerts at this time"),
                metrics=_convert_metrics(overview_data.get("summary", {})),
                platforms=_convert_platforms(overview_data.get("platforms", {})),
                ai_insights=[AIInsight(**insight) for insight in overview_data.get("ai_insights", [])],
                last_updated=overview_data.get("last_updated", datetime.now().isoformat()),
                website_url=overview_data.get("website_url")
            )
        finally:
            db_session.close()
            
    except Exception as e:
        logger.error(f"Error getting SEO dashboard data: {e}")
        # Fallback to mock data
        return get_mock_seo_data()

async def get_seo_health_score(current_user: dict = Depends(get_current_user)) -> SEOHealthScore:
    """Get current SEO health score."""
    try:
        user_id = str(current_user.get('id'))
        db_session = get_db_session(user_id)
        
        if not db_session:
            raise HTTPException(status_code=500, detail="Database connection unavailable")
        
        try:
            dashboard_service = SEODashboardService(db_session)
            overview_data = await dashboard_service.get_dashboard_overview(user_id)
            health_score_data = overview_data.get("health_score", {})
            return SEOHealthScore(**health_score_data)
        finally:
            db_session.close()
            
    except Exception as e:
        logger.error(f"Error getting SEO health score: {e}")
        raise HTTPException(status_code=500, detail="Failed to get SEO health score")

async def get_seo_metrics(current_user: dict = Depends(get_current_user)) -> Dict[str, SEOMetric]:
    """Get SEO metrics."""
    try:
        user_id = str(current_user.get('id'))
        db_session = get_db_session(user_id)
        
        if not db_session:
            raise HTTPException(status_code=500, detail="Database connection unavailable")
        
        try:
            dashboard_service = SEODashboardService(db_session)
            overview_data = await dashboard_service.get_dashboard_overview(user_id)
            summary_data = overview_data.get("summary", {})
            return _convert_metrics(summary_data)
        finally:
            db_session.close()
            
    except Exception as e:
        logger.error(f"Error getting SEO metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get SEO metrics")

async def get_platform_status(
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get platform connection status."""
    try:
        user_id = str(current_user.get('id'))
        db_session = get_db_session(user_id)
        
        if not db_session:
            logger.error("No database session available")
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        try:
            # Use SEO dashboard service to get platform status
            dashboard_service = SEODashboardService(db_session)
            platform_status = await dashboard_service.get_platform_status(user_id)
            
            logger.info(f"Retrieved platform status for user {user_id}")
            return platform_status
            
        finally:
            db_session.close()
            
    except Exception as e:
        logger.error(f"Error getting platform status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get platform status")

async def get_ai_insights(current_user: dict = Depends(get_current_user)) -> List[AIInsight]:
    """Get AI-generated insights."""
    try:
        user_id = str(current_user.get('id'))
        db_session = get_db_session(user_id)
        
        if not db_session:
            raise HTTPException(status_code=500, detail="Database connection unavailable")
        
        try:
            dashboard_service = SEODashboardService(db_session)
            overview_data = await dashboard_service.get_dashboard_overview(user_id)
            ai_insights_data = overview_data.get("ai_insights", [])
            return [AIInsight(**insight) for insight in ai_insights_data]
        finally:
            db_session.close()
            
    except Exception as e:
        logger.error(f"Error getting AI insights: {e}")
        raise HTTPException(status_code=500, detail="Failed to get AI insights")

async def seo_dashboard_health_check():
    """Health check for SEO dashboard."""
    return {"status": "healthy", "service": "SEO Dashboard API"}

# Phase 2B: Semantic health monitoring endpoint
async def get_semantic_health(current_user: dict = Depends(get_current_user)) -> SemanticHealthMetric:
    """
    Get real-time semantic health metrics for the user's content and competitors.
    This endpoint provides Phase 2B semantic intelligence monitoring data.
    
    Returns:
        SemanticHealthMetric with current health status, score, and recommendations
    """
    try:
        user_id = str(current_user.get('id'))
        
        # Initialize semantic monitor for this user
        semantic_monitor = RealTimeSemanticMonitor(user_id)
        
        # Get current semantic health (will use cache if available)
        semantic_health = await semantic_monitor.check_semantic_health(user_id)
        
        logger.info(f"[Semantic Health API] Retrieved health data for user {user_id}: {semantic_health.status} (score: {semantic_health.value:.2f})")
        
        return semantic_health
        
    except Exception as e:
        logger.error(f"[Semantic Health API] Error retrieving semantic health for user: {e}")
        # Return a default healthy state with warning message
        return SemanticHealthMetric(
            metric_name="semantic_health",
            value=0.5,
            threshold=0.6,
            status="warning",
            timestamp=datetime.utcnow().isoformat(),
            description="Semantic monitoring temporarily unavailable",
            recommendations=["Please try again later", "Check system status"]
        )


async def get_semantic_cache_stats(current_user: dict = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Get statistics for the semantic cache.
    """
    try:
        user_id = str(current_user.get('id'))
        # Initialize semantic monitor to access its cache manager
        semantic_monitor = RealTimeSemanticMonitor(user_id)
        return await semantic_monitor.get_cache_stats()
    except Exception as e:
        logger.error(f"[Semantic Cache API] Error retrieving cache stats: {e}")
        return {
            "error": "Failed to retrieve cache statistics",
            "hit_rate": 0.0,
            "memory_usage_mb": 0.0
        }

# New comprehensive SEO analysis endpoints
async def analyze_seo_comprehensive(request: SEOAnalysisRequest) -> SEOAnalysisResponse:
    """
    Analyze a URL for comprehensive SEO performance (progressive mode)
    
    Args:
        request: SEOAnalysisRequest containing URL and optional target keywords
        
    Returns:
        SEOAnalysisResponse with detailed analysis results
    """
    try:
        logger.info(f"Starting progressive SEO analysis for URL: {request.url}")
        
        # Use progressive analysis for comprehensive results with timeout handling
        result = seo_analyzer.analyze_url_progressive(request.url, request.target_keywords)
        
        # Store result in database
        db_session = get_db_session()
        if db_session:
            try:
                seo_service = SEOAnalysisService(db_session)
                stored_analysis = seo_service.store_analysis_result(result)
                if stored_analysis:
                    logger.info(f"Stored progressive SEO analysis in database with ID: {stored_analysis.id}")
                else:
                    logger.warning("Failed to store SEO analysis in database")
            except Exception as db_error:
                logger.error(f"Database error during analysis storage: {str(db_error)}")
            finally:
                db_session.close()
        
        # Convert to response format
        response_data = {
            'url': result.url,
            'timestamp': result.timestamp,
            'overall_score': result.overall_score,
            'health_status': result.health_status,
            'critical_issues': result.critical_issues,
            'warnings': result.warnings,
            'recommendations': result.recommendations,
            'data': result.data,
            'success': True,
            'message': f"Progressive SEO analysis completed successfully for {result.url}"
        }
        
        logger.info(f"Progressive SEO analysis completed for {request.url}. Overall score: {result.overall_score}")
        return SEOAnalysisResponse(**response_data)
        
    except Exception as e:
        logger.error(f"Error analyzing SEO for {request.url}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing SEO: {str(e)}"
        )

async def analyze_seo_full(request: SEOAnalysisRequest) -> SEOAnalysisResponse:
    """
    Analyze a URL for comprehensive SEO performance (full analysis)
    
    Args:
        request: SEOAnalysisRequest containing URL and optional target keywords
        
    Returns:
        SEOAnalysisResponse with detailed analysis results
    """
    try:
        logger.info(f"Starting full SEO analysis for URL: {request.url}")
        
        # Use progressive analysis for comprehensive results
        result = seo_analyzer.analyze_url_progressive(request.url, request.target_keywords)
        
        # Store result in database
        db_session = get_db_session()
        if db_session:
            try:
                seo_service = SEOAnalysisService(db_session)
                stored_analysis = seo_service.store_analysis_result(result)
                if stored_analysis:
                    logger.info(f"Stored full SEO analysis in database with ID: {stored_analysis.id}")
                else:
                    logger.warning("Failed to store SEO analysis in database")
            except Exception as db_error:
                logger.error(f"Database error during analysis storage: {str(db_error)}")
            finally:
                db_session.close()
        
        # Convert to response format
        response_data = {
            'url': result.url,
            'timestamp': result.timestamp,
            'overall_score': result.overall_score,
            'health_status': result.health_status,
            'critical_issues': result.critical_issues,
            'warnings': result.warnings,
            'recommendations': result.recommendations,
            'data': result.data,
            'success': True,
            'message': f"Full SEO analysis completed successfully for {result.url}"
        }
        
        logger.info(f"Full SEO analysis completed for {request.url}. Overall score: {result.overall_score}")
        return SEOAnalysisResponse(**response_data)
        
    except Exception as e:
        logger.error(f"Error in full SEO analysis for {request.url}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error in full SEO analysis: {str(e)}"
        )

async def get_seo_metrics_detailed(url: str) -> SEOMetricsResponse:
    """
    Get detailed SEO metrics for dashboard display
    
    Args:
        url: The URL to analyze
        
    Returns:
        Detailed SEO metrics for React dashboard
    """
    try:
        # Ensure URL has protocol
        if not url.startswith(('http://', 'https://')):
            url = f"https://{url}"
        
        logger.info(f"Getting detailed SEO metrics for URL: {url}")
        
        # Perform analysis
        result = seo_analyzer.analyze_url_progressive(url)
        
        # Extract metrics for dashboard
        metrics = {
            "overall_score": result.overall_score,
            "health_status": result.health_status,
            "url_structure_score": result.data.get('url_structure', {}).get('score', 0),
            "meta_data_score": result.data.get('meta_data', {}).get('score', 0),
            "content_score": result.data.get('content_analysis', {}).get('score', 0),
            "technical_score": result.data.get('technical_seo', {}).get('score', 0),
            "performance_score": result.data.get('performance', {}).get('score', 0),
            "accessibility_score": result.data.get('accessibility', {}).get('score', 0),
            "user_experience_score": result.data.get('user_experience', {}).get('score', 0),
            "security_score": result.data.get('security_headers', {}).get('score', 0)
        }
        
        # Add detailed data for each category
        dashboard_data = {
            "metrics": metrics,
            "critical_issues": result.critical_issues,
            "warnings": result.warnings,
            "recommendations": result.recommendations,
            "detailed_analysis": {
                "url_structure": result.data.get('url_structure', {}),
                "meta_data": result.data.get('meta_data', {}),
                "content_analysis": result.data.get('content_analysis', {}),
                "technical_seo": result.data.get('technical_seo', {}),
                "performance": result.data.get('performance', {}),
                "accessibility": result.data.get('accessibility', {}),
                "user_experience": result.data.get('user_experience', {}),
                "security_headers": result.data.get('security_headers', {}),
                "keyword_analysis": result.data.get('keyword_analysis', {})
            },
            "timestamp": result.timestamp.isoformat(),
            "url": result.url
        }
        
        logger.info(f"Detailed SEO metrics retrieved for {url}")
        return SEOMetricsResponse(**dashboard_data)
        
    except Exception as e:
        logger.error(f"Error getting SEO metrics for {url}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting SEO metrics: {str(e)}"
        )

async def get_analysis_summary(url: str) -> Dict[str, Any]:
    """
    Get a quick summary of SEO analysis for a URL
    
    Args:
        url: The URL to analyze
        
    Returns:
        Summary of SEO analysis
    """
    try:
        # Ensure URL has protocol
        if not url.startswith(('http://', 'https://')):
            url = f"https://{url}"
        
        logger.info(f"Getting analysis summary for URL: {url}")
        
        # Perform analysis
        result = seo_analyzer.analyze_url_progressive(url)
        
        # Create summary
        summary = {
            "url": result.url,
            "overall_score": result.overall_score,
            "health_status": result.health_status,
            "critical_issues_count": len(result.critical_issues),
            "warnings_count": len(result.warnings),
            "recommendations_count": len(result.recommendations),
            "top_issues": result.critical_issues[:3],
            "top_recommendations": result.recommendations[:3],
            "analysis_timestamp": result.timestamp.isoformat()
        }
        
        logger.info(f"Analysis summary retrieved for {url}")
        return summary
        
    except Exception as e:
        logger.error(f"Error getting analysis summary for {url}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting analysis summary: {str(e)}"
        )

async def batch_analyze_urls(urls: List[str]) -> Dict[str, Any]:
    """
    Analyze multiple URLs in batch
    
    Args:
        urls: List of URLs to analyze
        
    Returns:
        Batch analysis results
    """
    try:
        logger.info(f"Starting batch analysis for {len(urls)} URLs")
        
        results = []
        
        for url in urls:
            try:
                # Ensure URL has protocol
                if not url.startswith(('http://', 'https://')):
                    url = f"https://{url}"
                
                # Perform analysis
                result = seo_analyzer.analyze_url_progressive(url)
                
                # Add to results
                results.append({
                    "url": result.url,
                    "overall_score": result.overall_score,
                    "health_status": result.health_status,
                    "critical_issues_count": len(result.critical_issues),
                    "warnings_count": len(result.warnings),
                    "success": True
                })
                
            except Exception as e:
                # Add error result
                results.append({
                    "url": url,
                    "overall_score": 0,
                    "health_status": "error",
                    "critical_issues_count": 0,
                    "warnings_count": 0,
                    "success": False,
                    "error": str(e)
                })
        
        batch_result = {
            "total_urls": len(urls),
            "successful_analyses": len([r for r in results if r['success']]),
            "failed_analyses": len([r for r in results if not r['success']]),
            "results": results
        }
        
        logger.info(f"Batch analysis completed. Success: {batch_result['successful_analyses']}/{len(urls)}")
        return batch_result
        
    except Exception as e:
        logger.error(f"Error in batch analysis: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error in batch analysis: {str(e)}"
        )

async def analyze_urls_ai(request: AnalyzeURLsRequest, current_user: dict) -> Dict[str, Any]:
    """Run AI analysis on selected URLs."""
    user_id = str(current_user.get('id'))
    db_session = get_db_session()
    results = []
    
    try:
        for url in request.urls:
            # Check if audit exists
            audit = db_session.query(SEOPageAudit).filter(
                SEOPageAudit.user_id == user_id,
                SEOPageAudit.page_url == url
            ).first()
            
            if not audit:
                results.append({"url": url, "status": "skipped", "reason": "No audit found"})
                continue
                
            # Prepare Prompt
            # We use the existing audit data (algorithmic) to feed the AI
            audit_summary = {
                "score": audit.overall_score,
                "issues": audit.issues,
                "warnings": audit.warnings
            }
            
            prompt = f"""
            As an expert SEO consultant, analyze these technical audit results for the page: {url}
            
            AUDIT DATA:
            {json.dumps(audit_summary, default=str)[:3000]}
            
            TASK:
            Provide 3 specific, high-impact AI recommendations to improve this page's SEO.
            Focus on content relevance, user intent, and semantic SEO, which the algorithmic audit might miss.
            
            OUTPUT JSON format:
            [
                {{ "category": "Content|Technical|UX", "recommendation": "...", "impact": "High|Medium", "effort": "Low|Medium" }}
            ]
            """
            
            try:
                ai_response = llm_text_gen(prompt, user_id=user_id)
                # Parse JSON
                import re
                cleaned = ai_response.strip().replace("```json", "").replace("```", "")
                # Simple regex to find the JSON array if extra text exists
                match = re.search(r'\[.*\]', cleaned, re.DOTALL)
                if match:
                    cleaned = match.group(0)
                
                recommendations = json.loads(cleaned)
                
                # Update audit
                current_recs = audit.recommendations or []
                if isinstance(current_recs, list):
                    # Tag new ones
                    for r in recommendations:
                        r['source'] = 'ai_on_demand'
                    current_recs.extend(recommendations)
                    audit.recommendations = current_recs
                
                audit.last_analyzed_at = datetime.utcnow()
                results.append({"url": url, "status": "success"})
                
            except Exception as e:
                logger.error(f"AI Analysis failed for {url}: {e}")
                results.append({"url": url, "status": "failed", "error": str(e)})
        
        db_session.commit()
        return {"results": results}
        
    finally:
        db_session.close()

async def get_analyzed_pages(current_user: dict = Depends(get_current_user)) -> Dict[str, Any]:
    """Get list of pages that have been analyzed by AI."""
    user_id = str(current_user.get('id'))
    db_session = get_db_session()
    
    try:
        audits = db_session.query(SEOPageAudit).filter(
            SEOPageAudit.user_id == user_id
        ).all()
        
        results = []
        for audit in audits:
            if audit.recommendations:
                results.append({
                    "url": audit.page_url,
                    "analyzed_at": audit.last_analyzed_at,
                    "score": audit.overall_score,
                    "recommendations_count": len(audit.recommendations)
                })
        
        return {"results": results}
    finally:
        db_session.close()


# New SEO Dashboard Endpoints with Real Data

async def get_seo_dashboard_overview(
    current_user: dict = Depends(get_current_user),
    site_url: Optional[str] = None
) -> Dict[str, Any]:
    """Get comprehensive SEO dashboard overview with real GSC/Bing data."""
    try:
        user_id = str(current_user.get('id'))
        db_session = get_session_for_user(user_id)
        
        if not db_session:
            logger.error("No database session available")
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        try:
            # Use SEO dashboard service to get real data
            dashboard_service = SEODashboardService(db_session)
            overview_data = await dashboard_service.get_dashboard_overview(user_id, site_url)
            
            logger.info(f"Retrieved SEO dashboard overview for user {user_id}")
            return overview_data
            
        finally:
            db_session.close()
            
    except Exception as e:
        logger.error(f"Error getting SEO dashboard overview: {e}")
        raise HTTPException(status_code=500, detail="Failed to get dashboard overview")

async def get_gsc_raw_data(
    current_user: dict = Depends(get_current_user),
    site_url: Optional[str] = None
) -> Dict[str, Any]:
    """Get raw GSC data for the specified site."""
    try:
        user_id = str(current_user.get('id'))
        db_session = get_db_session()
        
        if not db_session:
            logger.error("No database session available")
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        try:
            # Use SEO dashboard service to get GSC data
            dashboard_service = SEODashboardService(db_session)
            gsc_data = await dashboard_service.get_gsc_data(user_id, site_url)
            
            logger.info(f"Retrieved GSC raw data for user {user_id}")
            return gsc_data
            
        finally:
            db_session.close()
            
    except Exception as e:
        logger.error(f"Error getting GSC raw data: {e}")
        raise HTTPException(status_code=500, detail="Failed to get GSC data")

async def get_bing_raw_data(
    current_user: dict = Depends(get_current_user),
    site_url: Optional[str] = None
) -> Dict[str, Any]:
    """Get raw Bing data for the specified site."""
    try:
        user_id = str(current_user.get('id'))
        db_session = get_db_session(user_id)
        
        if not db_session:
            logger.error("No database session available")
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        try:
            # Use SEO dashboard service to get Bing data
            dashboard_service = SEODashboardService(db_session)
            bing_data = await dashboard_service.get_bing_data(user_id, site_url)
            
            logger.info(f"Retrieved Bing raw data for user {user_id}")
            return bing_data
            
        finally:
            db_session.close()
            
    except Exception as e:
        logger.error(f"Error getting Bing raw data: {e}")
        raise HTTPException(status_code=500, detail="Failed to get Bing data")

async def get_competitive_insights(
    current_user: dict = Depends(get_current_user),
    site_url: Optional[str] = None
) -> Dict[str, Any]:
    """Get competitive insights from onboarding step 3 data."""
    try:
        user_id = str(current_user.get('id'))
        db_session = get_db_session(user_id)
        
        if not db_session:
            logger.error("No database session available")
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        try:
            # Use SEO dashboard service to get competitive insights
            dashboard_service = SEODashboardService(db_session)
            insights_data = await dashboard_service.get_competitive_insights(user_id)
            
            logger.info(f"Retrieved competitive insights for user {user_id}")
            return insights_data
            
        finally:
            db_session.close()
            
    except Exception as e:
        logger.error(f"Error getting competitive insights: {e}")
        raise HTTPException(status_code=500, detail="Failed to get competitive insights")


async def get_deep_competitor_analysis(
    current_user: dict = Depends(get_current_user),
    site_url: Optional[str] = None
) -> Dict[str, Any]:
    try:
        user_id = str(current_user.get('id'))
        db_session = get_session_for_user(user_id)

        if not db_session:
            logger.error("No database session available")
            raise HTTPException(status_code=500, detail="Database connection failed")

        try:
            integration_service = OnboardingDataIntegrationService()
            integrated = integration_service.get_integrated_data_sync(user_id, db_session)
            deep = integrated.get("deep_competitor_analysis") if isinstance(integrated, dict) else None
            return deep or {
                "status": "not_available",
                "last_run": None,
                "report": None
            }
        finally:
            db_session.close()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting deep competitor analysis: {e}")
        raise HTTPException(status_code=500, detail="Failed to get deep competitor analysis")


async def run_strategic_insights(
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """Run AI-powered strategic insights analysis manually."""
    try:
        user_id = str(current_user.get('id'))
        db_session = get_session_for_user(user_id)
        
        if not db_session:
            raise HTTPException(status_code=500, detail="Database connection failed")

        try:
            integration_service = OnboardingDataIntegrationService()
            integrated = integration_service.get_integrated_data_sync(user_id, db_session)
            
            website_analysis_data = integrated.get("website_analysis")
            logger.info(f"Integrated data for user {user_id}: website_analysis found? {bool(website_analysis_data)}")
            
            # Fallback: If not found in integrated data (e.g. strict session mismatch), find latest analysis for user
            if not website_analysis_data:
                logger.info(f"Attempting fallback for user {user_id}")
                # Find latest WebsiteAnalysis for this user across all sessions
                latest_analysis = db_session.query(WebsiteAnalysis).join(
                    OnboardingSession, WebsiteAnalysis.session_id == OnboardingSession.id
                ).filter(
                    OnboardingSession.user_id == user_id
                ).order_by(WebsiteAnalysis.updated_at.desc()).first()
                
                if latest_analysis:
                    logger.info(f"Found fallback WebsiteAnalysis {latest_analysis.id} for user {user_id}")
                    website_analysis_data = latest_analysis.to_dict()
                    # Ensure ID is present for updates
                    website_analysis_data['id'] = latest_analysis.id
                else:
                    logger.warning(f"Fallback failed for user {user_id}. No WebsiteAnalysis found.")

            if not website_analysis_data:
                raise HTTPException(status_code=400, detail="Website analysis (Step 2) not found. Please complete onboarding.")
            
            research_prefs = integrated.get("research_preferences")
            competitors = (research_prefs.get("competitors") if isinstance(research_prefs, dict) else None)
            
            if not competitors:
                # Try competitor_analysis as fallback
                competitors = integrated.get("competitor_analysis") or []

            if not competitors:
                raise HTTPException(status_code=400, detail="No competitors found. Please add competitors in Step 3.")

            from services.seo.deep_competitor_analysis_service import DeepCompetitorAnalysisService
            analysis_service = DeepCompetitorAnalysisService()
            
            logger.info(f"Running manual strategic insights for user {user_id}")
            report = await analysis_service.generate_weekly_strategy_brief(
                user_id=user_id,
                website_analysis=website_analysis_data if isinstance(website_analysis_data, dict) else {},
                competitors=competitors if isinstance(competitors, list) else []
            )
            
            # Find the WebsiteAnalysis record to persist history
            analysis_id = website_analysis_data.get('id') if isinstance(website_analysis_data, dict) else None
            if analysis_id:
                website_analysis = db_session.query(WebsiteAnalysis).filter(WebsiteAnalysis.id == analysis_id).first()
                
                if website_analysis:
                    history = website_analysis.strategic_insights_history or []
                    if not isinstance(history, list):
                        history = []
                    
                    # Append new report at the beginning (latest first)
                    history.insert(0, report)
                    # Keep last 52 weeks (1 year)
                    website_analysis.strategic_insights_history = history[:52]
                    flag_modified(website_analysis, "strategic_insights_history")
                    db_session.commit()
                    logger.info(f"Persisted strategic insight for user {user_id} to history")
            
            return {"success": True, "report": report}
        finally:
            db_session.close()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error running strategic insights: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to run strategic insights: {str(e)}")


async def get_strategic_insights_history(
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """Fetch the history of strategic insights for the user."""
    try:
        user_id = str(current_user.get('id'))
        db_session = get_session_for_user(user_id)
        
        if not db_session:
            raise HTTPException(status_code=500, detail="Database connection failed")

        try:
            integration_service = OnboardingDataIntegrationService()
            integrated = integration_service.get_integrated_data_sync(user_id, db_session)
            
            website_analysis = integrated.get("website_analysis")
            if not website_analysis or not isinstance(website_analysis, dict):
                return {"history": []}
            
            history = website_analysis.get("strategic_insights_history") or []
            return {"history": history}
        finally:
            db_session.close()
    except Exception as e:
        logger.error(f"Error fetching strategic insights history: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch strategic insights history")

async def refresh_analytics_data(
    current_user: dict = Depends(get_current_user),
    site_url: Optional[str] = None
) -> Dict[str, Any]:
    """Refresh analytics data by invalidating cache and fetching fresh data."""
    try:
        user_id = str(current_user.get('id'))
        db_session = get_db_session(user_id)
        
        if not db_session:
            logger.error("No database session available")
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        try:
            # Use SEO dashboard service to refresh data
            dashboard_service = SEODashboardService(db_session)
            refresh_result = await dashboard_service.refresh_analytics_data(user_id, site_url)
            
            logger.info(f"Refreshed analytics data for user {user_id}")
            return refresh_result
            
        finally:
            db_session.close()
            
    except Exception as e:
        logger.error(f"Error refreshing analytics data: {e}")
        raise HTTPException(status_code=500, detail="Failed to refresh analytics data")

# Helper methods for data conversion
def _convert_metrics(summary_data: Dict[str, Any]) -> Dict[str, SEOMetric]:
    """Convert summary data to SEOMetric format."""
    try:
        return {
            "traffic": SEOMetric(
                value=summary_data.get("clicks", 0),
                change=0,  # Would calculate from historical data
                trend="up",
                description="Organic traffic",
                color="#4CAF50"
            ),
            "rankings": SEOMetric(
                value=summary_data.get("position", 0),
                change=0,  # Would calculate from historical data
                trend="up",
                description="Average ranking",
                color="#2196F3"
            ),
            "mobile": SEOMetric(
                value=0,  # Would get from performance data
                change=0,
                trend="stable",
                description="Mobile speed",
                color="#FF9800"
            ),
            "keywords": SEOMetric(
                value=0,  # Would count from query data
                change=0,
                trend="up",
                description="Keywords tracked",
                color="#9C27B0"
            )
        }
    except Exception as e:
        logger.error(f"Error converting metrics: {e}")
        return {}

def _convert_platforms(platform_data: Dict[str, Any]) -> Dict[str, PlatformStatus]:
    """Convert platform data to PlatformStatus format."""
    try:
        return {
            "google_search_console": PlatformStatus(
                status="connected" if platform_data.get("gsc", {}).get("connected", False) else "disconnected",
                connected=platform_data.get("gsc", {}).get("connected", False),
                last_sync=platform_data.get("gsc", {}).get("last_sync"),
                data_points=len(platform_data.get("gsc", {}).get("sites", []))
            ),
            "bing_webmaster": PlatformStatus(
                status="connected" if platform_data.get("bing", {}).get("connected", False) else "disconnected",
                connected=platform_data.get("bing", {}).get("connected", False),
                last_sync=platform_data.get("bing", {}).get("last_sync"),
                data_points=len(platform_data.get("bing", {}).get("sites", []))
            )
        }
    except Exception as e:
        logger.error(f"Error converting platforms: {e}")
        return {} 
