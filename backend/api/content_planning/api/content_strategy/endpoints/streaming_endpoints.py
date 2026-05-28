"""
Streaming Endpoints
Handles streaming endpoints for enhanced content strategies.
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from starlette.requests import Request
from sqlalchemy.orm import Session
from loguru import logger
import json
import asyncio
from datetime import datetime
from collections import defaultdict
import time

# Import database
from services.database import get_db_session

# Import authentication middleware
from middleware.auth_middleware import get_current_user, get_current_user_with_query_token

# Import services
from ....services.enhanced_strategy_service import EnhancedStrategyService
from ....services.enhanced_strategy_db_service import EnhancedStrategyDBService

# Import utilities
from ....utils.error_handlers import ContentPlanningErrorHandler
from ....utils.response_builders import ResponseBuilder
from ....utils.constants import ERROR_MESSAGES, SUCCESS_MESSAGES

router = APIRouter(tags=["Strategy Streaming"])

# Cache for streaming endpoints (5 minutes cache)
streaming_cache = defaultdict(dict)
CACHE_DURATION = 300  # 5 minutes

def get_cached_data(cache_key: str) -> Optional[Dict[str, Any]]:
    """Get cached data if it exists and is not expired."""
    if cache_key in streaming_cache:
        cached_data = streaming_cache[cache_key]
        if time.time() - cached_data.get("timestamp", 0) < CACHE_DURATION:
            return cached_data.get("data")
    return None

def set_cached_data(cache_key: str, data: Dict[str, Any]):
    """Set cached data with timestamp."""
    streaming_cache[cache_key] = {
        "data": data,
        "timestamp": time.time()
    }

# Helper function to get database session
def get_db():
    db = get_db_session()
    try:
        yield db
    finally:
        db.close()

async def stream_data(data_generator):
    """Helper function to stream data as Server-Sent Events"""
    async for chunk in data_generator:
        if isinstance(chunk, dict):
            yield f"data: {json.dumps(chunk)}\n\n"
        else:
            yield f"data: {json.dumps({'message': str(chunk)})}\n\n"
        await asyncio.sleep(0.1)  # Small delay to prevent overwhelming

@router.get("/stream/strategies")
async def stream_enhanced_strategies(
    strategy_id: Optional[int] = Query(None, description="Specific strategy ID"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Stream enhanced strategies with real-time updates."""
    
    async def strategy_generator():
        try:
            clerk_user_id = str(current_user.get('id', ''))
            if not clerk_user_id:
                yield {"type": "error", "message": "Invalid user ID in authentication token", "timestamp": datetime.utcnow().isoformat()}
                return
            
            authenticated_user_id = clerk_user_id
            
            logger.info(f"🚀 Starting strategy stream for authenticated user: {authenticated_user_id}, strategy: {strategy_id}")
            
            # Send initial status
            yield {"type": "status", "message": "Starting strategy retrieval...", "timestamp": datetime.utcnow().isoformat()}
            
            db_service = EnhancedStrategyDBService(db)
            enhanced_service = EnhancedStrategyService(db_service)
            
            # Send progress update
            yield {"type": "progress", "message": "Querying database...", "progress": 25}
            
            # Use authenticated user_id to ensure users can only see their own strategies
            strategies_data = await enhanced_service.get_enhanced_strategies(authenticated_user_id, strategy_id, db)
            
            # Send progress update
            yield {"type": "progress", "message": "Processing strategies...", "progress": 50}
            
            if strategies_data.get("status") == "not_found":
                yield {"type": "result", "status": "not_found", "data": strategies_data}
                return
            
            # Send progress update
            yield {"type": "progress", "message": "Finalizing data...", "progress": 75}
            
            # Send final result
            yield {"type": "result", "status": "success", "data": strategies_data, "progress": 100}
            
            logger.info(f"✅ Strategy stream completed for user: {authenticated_user_id}")
            
        except Exception as e:
            logger.error(f"❌ Error in strategy stream: {str(e)}")
            yield {"type": "error", "message": str(e), "timestamp": datetime.utcnow().isoformat()}
    
    return StreamingResponse(
        stream_data(strategy_generator()),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Credentials": "true"
        }
    )

@router.get("/stream/strategic-intelligence")
async def stream_strategic_intelligence(
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_user_with_query_token),
    db: Session = Depends(get_db)
):
    """Stream strategic intelligence data with real-time updates."""
    
    async def intelligence_generator():
        try:
            clerk_user_id = str(current_user.get('id', ''))
            if not clerk_user_id:
                yield {"type": "error", "message": "Invalid user ID in authentication token", "timestamp": datetime.utcnow().isoformat()}
                return
            
            authenticated_user_id = clerk_user_id
            
            logger.info(f"🚀 Starting strategic intelligence stream for authenticated user: {authenticated_user_id}")
            
            # Check cache first
            cache_key = f"strategic_intelligence_{authenticated_user_id}"
            cached_data = get_cached_data(cache_key)
            if cached_data:
                logger.info(f"✅ Returning cached strategic intelligence data for user: {authenticated_user_id}")
                yield {"type": "result", "status": "success", "data": cached_data, "progress": 100}
                return
            
            # Send initial status
            yield {"type": "status", "message": "Loading strategic intelligence...", "timestamp": datetime.utcnow().isoformat()}
            
            db_service = EnhancedStrategyDBService(db)
            enhanced_service = EnhancedStrategyService(db_service)
            
            # Send progress update
            yield {"type": "progress", "message": "Retrieving strategies...", "progress": 20}
            
            # Use authenticated user_id to ensure users can only see their own strategies
            strategies_data = await enhanced_service.get_enhanced_strategies(authenticated_user_id, None, db)
            
            # Send progress update
            yield {"type": "progress", "message": "Analyzing market positioning...", "progress": 40}
            
            if strategies_data.get("status") == "not_found":
                yield {"type": "error", "status": "not_ready", "message": "No strategies found. Complete onboarding and create a strategy before generating intelligence.", "progress": 100}
                return
            
            # Extract strategic intelligence from first strategy
            strategy = strategies_data.get("strategies", [{}])[0]
            
            # Parse ai_recommendations if it's a JSON string
            ai_recommendations = {}
            if strategy.get("ai_recommendations"):
                try:
                    if isinstance(strategy["ai_recommendations"], str):
                        ai_recommendations = json.loads(strategy["ai_recommendations"])
                    else:
                        ai_recommendations = strategy["ai_recommendations"]
                except (json.JSONDecodeError, TypeError):
                    ai_recommendations = {}
            
            # Send progress update
            yield {"type": "progress", "message": "Processing intelligence data...", "progress": 60}

            def _ensure_list(value: Any) -> list:
                if isinstance(value, list):
                    return [item for item in value if item is not None]
                return []

            competitors = _ensure_list(strategy.get("top_competitors"))[:3]
            market_gaps = _ensure_list(strategy.get("market_gaps"))

            raw_insights = ai_recommendations.get("strategic_insights")
            if isinstance(raw_insights, dict):
                ai_insights = [raw_insights]
            elif isinstance(raw_insights, list):
                ai_insights = [item for item in raw_insights if item is not None]
            else:
                ai_insights = []

            opportunity_candidates = [
                ai_recommendations.get("opportunity_analysis"),
                ai_recommendations.get("opportunities"),
                ai_recommendations.get("strategic_opportunities"),
            ]
            opportunities = []
            for candidate in opportunity_candidates:
                if isinstance(candidate, list) and candidate:
                    opportunities = [item for item in candidate if item is not None]
                    break

            persisted_current_position = strategy.get("competitive_position")
            ai_positioning = ai_recommendations.get("market_positioning") if isinstance(ai_recommendations.get("market_positioning"), dict) else {}
            current_position = persisted_current_position or ai_positioning.get("current_position")
            target_position = ai_positioning.get("target_position")
            differentiation_factors = _ensure_list(ai_positioning.get("differentiation_factors"))

            has_required_signals = bool(current_position and competitors and market_gaps and ai_insights and opportunities)
            status = "success" if has_required_signals else "partial_incomplete"

            source_flags = {
                "current_position": "user_or_database" if persisted_current_position else ("model" if ai_positioning.get("current_position") else "insufficient_data"),
                "target_position": "model" if target_position else "insufficient_data",
                "differentiation_factors": "model" if differentiation_factors else "insufficient_data",
                "top_competitors": "user_or_database" if competitors else "insufficient_data",
                "market_gaps": "user_or_database" if market_gaps else "insufficient_data",
                "ai_insights": "model" if ai_insights else "insufficient_data",
                "opportunities": "model" if opportunities else "insufficient_data"
            }

            missing_signals = [key for key, value in {
                "market_positioning.current_position": bool(current_position),
                "competitive_analysis.top_competitors": bool(competitors),
                "competitive_analysis.market_gaps": bool(market_gaps),
                "ai_insights": bool(ai_insights),
                "opportunities": bool(opportunities),
            }.items() if not value]

            strategic_intelligence = {
                "status": status,
                "is_model_derived": any(source == "model" for source in source_flags.values()),
                "data_source_flags": source_flags,
                "missing_signals": missing_signals,
                "market_positioning": {
                    "current_position": current_position,
                    "target_position": target_position,
                    "differentiation_factors": differentiation_factors,
                },
                "competitive_analysis": {
                    "top_competitors": competitors,
                    "market_gaps": market_gaps,
                },
                "ai_insights": ai_insights,
                "opportunities": opportunities,
            }

            # Cache the strategic intelligence data
            set_cached_data(cache_key, strategic_intelligence)

            # Send progress update
            yield {"type": "progress", "message": "Finalizing strategic intelligence...", "progress": 80}

            # Send final result
            yield {"type": "result", "status": status, "data": strategic_intelligence, "progress": 100}
            
            logger.info(f"✅ Strategic intelligence stream completed for user: {authenticated_user_id}")
            
        except Exception as e:
            logger.error(f"❌ Error in strategic intelligence stream: {str(e)}")
            yield {"type": "error", "message": str(e), "timestamp": datetime.utcnow().isoformat()}
    
    return StreamingResponse(
        stream_data(intelligence_generator()),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Credentials": "true"
        }
    )

@router.get("/stream/keyword-research")
async def stream_keyword_research(
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_user_with_query_token),
    db: Session = Depends(get_db)
):
    """Stream keyword research data with real-time updates."""
    
    async def keyword_generator():
        try:
            clerk_user_id = str(current_user.get('id', ''))
            if not clerk_user_id:
                yield {"type": "error", "message": "Invalid user ID in authentication token", "timestamp": datetime.utcnow().isoformat()}
                return
            
            authenticated_user_id = clerk_user_id
            
            logger.info(f"🚀 Starting keyword research stream for authenticated user: {authenticated_user_id}")
            
            # Check cache first
            cache_key = f"keyword_research_{authenticated_user_id}"
            cached_data = get_cached_data(cache_key)
            if cached_data:
                logger.info(f"✅ Returning cached keyword research data for user: {authenticated_user_id}")
                yield {"type": "result", "status": "success", "data": cached_data, "progress": 100}
                return
            
            # Send initial status
            yield {"type": "status", "message": "Loading keyword research...", "timestamp": datetime.utcnow().isoformat()}
            
            # Import gap analysis service
            from ....services.gap_analysis_service import GapAnalysisService
            
            # Send progress update
            yield {"type": "progress", "message": "Retrieving gap analyses...", "progress": 20}
            
            gap_service = GapAnalysisService()
            # Use authenticated user_id to ensure users can only see their own data
            gap_analyses = await gap_service.get_gap_analyses(authenticated_user_id)
            
            # Send progress update
            yield {"type": "progress", "message": "Analyzing keyword opportunities...", "progress": 40}
            
            # Handle case where gap_analyses is 0, None, or empty
            if not gap_analyses or gap_analyses == 0 or len(gap_analyses) == 0:
                yield {"type": "error", "status": "not_ready", "message": "No keyword research data available. Connect data sources or run analysis first.", "progress": 100}
                return
            
            # Extract keyword data from first gap analysis
            gap_analysis = gap_analyses[0] if isinstance(gap_analyses, list) else gap_analyses
            
            # Parse analysis_results if it's a JSON string
            analysis_results = {}
            if gap_analysis.get("analysis_results"):
                try:
                    if isinstance(gap_analysis["analysis_results"], str):
                        analysis_results = json.loads(gap_analysis["analysis_results"])
                    else:
                        analysis_results = gap_analysis["analysis_results"]
                except (json.JSONDecodeError, TypeError):
                    analysis_results = {}
            
            # Send progress update
            yield {"type": "progress", "message": "Processing keyword data...", "progress": 60}
            
            keyword_data = {
                "trend_analysis": {
                    "high_volume_keywords": analysis_results.get("opportunities", [])[:3] or [
                        {"keyword": "AI marketing automation", "volume": "10K-100K", "difficulty": "Medium"},
                        {"keyword": "content strategy 2024", "volume": "1K-10K", "difficulty": "Low"},
                        {"keyword": "digital marketing trends", "volume": "10K-100K", "difficulty": "High"}
                    ],
                    "trending_keywords": [
                        {"keyword": "AI content generation", "growth": "+45%", "opportunity": "High"},
                        {"keyword": "voice search optimization", "growth": "+32%", "opportunity": "Medium"},
                        {"keyword": "video marketing strategy", "growth": "+28%", "opportunity": "High"}
                    ]
                },
                "intent_analysis": {
                    "informational": ["how to", "what is", "guide to"],
                    "navigational": ["company name", "brand name", "website"],
                    "transactional": ["buy", "purchase", "download", "sign up"]
                },
                "opportunities": analysis_results.get("opportunities", []) or [
                    {"keyword": "AI content tools", "search_volume": "5K-10K", "competition": "Low", "cpc": "$2.50"},
                    {"keyword": "content marketing ROI", "search_volume": "1K-5K", "competition": "Medium", "cpc": "$4.20"},
                    {"keyword": "social media strategy", "search_volume": "10K-50K", "competition": "High", "cpc": "$3.80"}
                ]
            }
            
            # Cache the keyword data
            set_cached_data(cache_key, keyword_data)
            
            # Send progress update
            yield {"type": "progress", "message": "Finalizing keyword research...", "progress": 80}
            
            # Send final result
            yield {"type": "result", "status": "success", "data": keyword_data, "progress": 100}
            
            logger.info(f"✅ Keyword research stream completed for user: {authenticated_user_id}")
            
        except Exception as e:
            logger.error(f"❌ Error in keyword research stream: {str(e)}")
            yield {"type": "error", "message": str(e), "timestamp": datetime.utcnow().isoformat()}
    
    return StreamingResponse(
        stream_data(keyword_generator()),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Credentials": "true"
        }
    ) 
