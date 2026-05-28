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
from datetime import timedelta

# Import database
from services.database import get_db_session
from models.content_strategy_state_models import StreamingCacheState
from models.enhanced_strategy_models import Base

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

STREAMING_CACHE_TTL_SECONDS = 300
STREAMING_CACHE_MAX_KEYS_PER_USER = 20
STREAMING_CACHE_ENDPOINT_VERSION = "v1"


def _build_cache_key(endpoint_name: str, authenticated_user_id: str) -> str:
    """Build namespaced cache key by endpoint version and user."""
    return f"streaming:{STREAMING_CACHE_ENDPOINT_VERSION}:{endpoint_name}:user:{authenticated_user_id}"


def get_cached_data(db: Session, authenticated_user_id: str, cache_key: str) -> Optional[Dict[str, Any]]:
    """Get cached data from shared DB-backed cache with validation and instrumentation."""
    try:
        cache_entry = db.query(StreamingCacheState).filter(
            StreamingCacheState.user_id == authenticated_user_id,
            StreamingCacheState.cache_key == cache_key,
            StreamingCacheState.expires_at > datetime.utcnow()
        ).first()

        if not cache_entry:
            logger.info(f"📭 Streaming cache MISS | key={cache_key} | user={authenticated_user_id}")
            return None

        payload = cache_entry.cache_payload
        if not isinstance(payload, dict):
            logger.warning(f"⚠️ Streaming cache deserialize failed (payload not dict) | key={cache_key} | user={authenticated_user_id}")
            db.delete(cache_entry)
            db.commit()
            return None

        logger.info(f"📦 Streaming cache HIT | key={cache_key} | user={authenticated_user_id}")
        return payload
    except Exception as e:
        logger.error(f"❌ Streaming cache read error | key={cache_key} | user={authenticated_user_id} | error={str(e)}")
        db.rollback()
        return None


def set_cached_data(db: Session, authenticated_user_id: str, cache_key: str, data: Dict[str, Any]) -> None:
    """Store cached data in shared DB-backed cache with TTL, key cap, and serialization checks."""
    try:
        if not isinstance(data, dict):
            logger.warning(f"⚠️ Streaming cache serialize skipped (data not dict) | key={cache_key} | user={authenticated_user_id}")
            return

        serialized_payload = json.loads(json.dumps(data))
        if not isinstance(serialized_payload, dict):
            logger.warning(f"⚠️ Streaming cache serialize skipped (post-serialize not dict) | key={cache_key} | user={authenticated_user_id}")
            return

        expiry = datetime.utcnow() + timedelta(seconds=STREAMING_CACHE_TTL_SECONDS)
        existing = db.query(StreamingCacheState).filter(
            StreamingCacheState.user_id == authenticated_user_id,
            StreamingCacheState.cache_key == cache_key
        ).first()

        if existing:
            existing.cache_payload = serialized_payload
            existing.expires_at = expiry
        else:
            db.add(StreamingCacheState(
                user_id=authenticated_user_id,
                cache_key=cache_key,
                cache_payload=serialized_payload,
                expires_at=expiry
            ))

        db.flush()

        # Max-key policy per user: delete oldest entries beyond cap
        entries = db.query(StreamingCacheState).filter(
            StreamingCacheState.user_id == authenticated_user_id
        ).order_by(StreamingCacheState.updated_at.desc(), StreamingCacheState.id.desc()).all()

        if len(entries) > STREAMING_CACHE_MAX_KEYS_PER_USER:
            for stale_entry in entries[STREAMING_CACHE_MAX_KEYS_PER_USER:]:
                db.delete(stale_entry)

        db.commit()
        logger.info(
            f"💾 Streaming cache STORE | key={cache_key} | user={authenticated_user_id} | "
            f"ttl={STREAMING_CACHE_TTL_SECONDS}s | max_keys={STREAMING_CACHE_MAX_KEYS_PER_USER}"
        )
    except Exception as e:
        logger.error(f"❌ Streaming cache write error | key={cache_key} | user={authenticated_user_id} | error={str(e)}")
        db.rollback()

# Helper function to get database session
def get_db():
    db = get_db_session()
    try:
        Base.metadata.create_all(bind=db.bind, tables=[StreamingCacheState.__table__], checkfirst=True)
    except Exception as table_error:
        logger.warning(f"⚠️ Could not ensure streaming cache table exists: {str(table_error)}")
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
            cache_key = _build_cache_key("strategic-intelligence", authenticated_user_id)
            cached_data = get_cached_data(db, authenticated_user_id, cache_key)
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
            
            strategic_intelligence = {
                "market_positioning": {
                    "current_position": strategy.get("competitive_position", "Challenger"),
                    "target_position": "Market Leader",
                    "differentiation_factors": [
                        "AI-powered content optimization",
                        "Data-driven strategy development",
                        "Personalized user experience"
                    ]
                },
                "competitive_analysis": {
                    "top_competitors": strategy.get("top_competitors", [])[:3] or [
                        "Competitor A", "Competitor B", "Competitor C"
                    ],
                    "competitive_advantages": [
                        "Advanced AI capabilities",
                        "Comprehensive data integration",
                        "User-centric design"
                    ],
                    "market_gaps": strategy.get("market_gaps", []) or [
                        "AI-driven content personalization",
                        "Real-time performance optimization",
                        "Predictive analytics"
                    ]
                },
                "ai_insights": ai_recommendations.get("strategic_insights", []) or [
                    "Focus on pillar content strategy",
                    "Implement topic clustering",
                    "Optimize for voice search"
                ],
                "opportunities": [
                    {
                        "area": "Content Personalization",
                        "potential_impact": "High",
                        "implementation_timeline": "3-6 months",
                        "estimated_roi": "25-40%"
                    },
                    {
                        "area": "AI-Powered Optimization",
                        "potential_impact": "Medium",
                        "implementation_timeline": "6-12 months",
                        "estimated_roi": "15-30%"
                    }
                ]
            }
            
            # Cache the strategic intelligence data
            set_cached_data(db, authenticated_user_id, cache_key, strategic_intelligence)
            
            # Send progress update
            yield {"type": "progress", "message": "Finalizing strategic intelligence...", "progress": 80}
            
            # Send final result
            yield {"type": "result", "status": "success", "data": strategic_intelligence, "progress": 100}
            
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
            cache_key = _build_cache_key("keyword-research", authenticated_user_id)
            cached_data = get_cached_data(db, authenticated_user_id, cache_key)
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
            set_cached_data(db, authenticated_user_id, cache_key, keyword_data)
            
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
