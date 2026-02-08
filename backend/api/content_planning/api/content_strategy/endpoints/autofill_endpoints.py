"""
Autofill Endpoints
Handles autofill endpoints for enhanced content strategies.
CRITICAL PROTECTION ZONE - These endpoints are essential for autofill functionality.
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from loguru import logger
import json
import asyncio
from datetime import datetime

# Import database
from services.database import get_db_session

# Import services
from ....services.enhanced_strategy_service import EnhancedStrategyService
from ....services.enhanced_strategy_db_service import EnhancedStrategyDBService
from ....services.content_strategy.autofill.ai_refresh import AutoFillRefreshService

# Import utilities
from ....utils.error_handlers import ContentPlanningErrorHandler
from ....utils.response_builders import ResponseBuilder
from ....utils.constants import ERROR_MESSAGES, SUCCESS_MESSAGES

router = APIRouter(tags=["Strategy Autofill"])

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

@router.post("/{strategy_id}/autofill/accept")
async def accept_autofill_inputs(
    strategy_id: int,
    payload: Dict[str, Any],
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Persist end-user accepted auto-fill inputs and associate with the strategy."""
    try:
        logger.info(f"🚀 Accepting autofill inputs for strategy: {strategy_id}")
        user_id = str(payload.get('user_id') or "")
        accepted_fields = payload.get('accepted_fields') or {}
        # Optional transparency bundles
        sources = payload.get('sources') or {}
        input_data_points = payload.get('input_data_points') or {}
        quality_scores = payload.get('quality_scores') or {}
        confidence_levels = payload.get('confidence_levels') or {}
        data_freshness = payload.get('data_freshness') or {}

        if not accepted_fields:
            raise HTTPException(status_code=400, detail="accepted_fields is required")

        db_service = EnhancedStrategyDBService(db)
        record = await db_service.save_autofill_insights(
            strategy_id=strategy_id,
            user_id=user_id,
            payload={
                'accepted_fields': accepted_fields,
                'sources': sources,
                'input_data_points': input_data_points,
                'quality_scores': quality_scores,
                'confidence_levels': confidence_levels,
                'data_freshness': data_freshness,
            }
        )
        if not record:
            raise HTTPException(status_code=500, detail="Failed to persist autofill insights")

        return ResponseBuilder.create_success_response(
            message="Accepted autofill inputs persisted successfully",
            data={
                'id': record.id,
                'strategy_id': record.strategy_id,
                'user_id': record.user_id,
                'created_at': record.created_at.isoformat() if getattr(record, 'created_at', None) else None
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error accepting autofill inputs: {str(e)}")
        raise ContentPlanningErrorHandler.handle_general_error(e, "accept_autofill_inputs")

@router.get("/autofill/refresh/stream")
async def stream_autofill_refresh(
    user_id: Optional[int] = Query(None, description="User ID to build auto-fill for"),
    use_ai: bool = Query(True, description="Use AI augmentation during refresh"),
    ai_only: bool = Query(False, description="AI-first refresh: return AI overrides when available"),
    db: Session = Depends(get_db)
):
    """SSE endpoint to stream steps while generating a fresh auto-fill payload (no DB writes)."""
    async def refresh_generator():
        try:
            actual_user_id = user_id or 1
            start_time = datetime.utcnow()
            logger.info(f"🚀 Starting auto-fill refresh stream for user: {actual_user_id}")
            yield {"type": "status", "phase": "init", "message": "Starting…", "progress": 5}

            refresh_service = AutoFillRefreshService(db)

            # Phase: Collect onboarding context
            yield {"type": "progress", "phase": "context", "message": "Collecting context…", "progress": 15}
            # We deliberately do not emit DB-derived values; context is used inside the service

            # Phase: Build prompt
            yield {"type": "progress", "phase": "prompt", "message": "Preparing prompt…", "progress": 30}

            # Phase: AI call with transparency - run in background and yield transparency messages
            yield {"type": "progress", "phase": "ai", "message": "Calling AI…", "progress": 45}

            import asyncio
            
            # Create a queue to collect transparency messages
            transparency_messages = []
            
            async def yield_transparency_message(message):
                transparency_messages.append(message)
                logger.info(f"📊 Transparency message collected: {message.get('type', 'unknown')} - {message.get('message', 'no message')}")
                return message
            
            # Run the transparency-enabled payload generation
            ai_task = asyncio.create_task(
                refresh_service.build_fresh_payload_with_transparency(
                    actual_user_id, 
                    use_ai=use_ai, 
                    ai_only=ai_only,
                    yield_callback=yield_transparency_message
                )
            )

            # Heartbeat loop while AI is running
            heartbeat_progress = 50
            while not ai_task.done():
                elapsed = (datetime.utcnow() - start_time).total_seconds()
                heartbeat_progress = min(heartbeat_progress + 3, 85)
                yield {"type": "progress", "phase": "ai_running", "message": f"AI running… {int(elapsed)}s", "progress": heartbeat_progress}
                
                # Yield any transparency messages that have been collected
                while transparency_messages:
                    message = transparency_messages.pop(0)
                    logger.info(f"📤 Yielding transparency message: {message.get('type', 'unknown')}")
                    yield message
                
                await asyncio.sleep(1)  # Check more frequently

            # Retrieve result or error
            final_payload = await ai_task
            
            # Yield any remaining transparency messages after task completion
            while transparency_messages:
                message = transparency_messages.pop(0)
                logger.info(f"📤 Yielding remaining transparency message: {message.get('type', 'unknown')}")
                yield message

            # Phase: Validate & map
            yield {"type": "progress", "phase": "validate", "message": "Validating…", "progress": 92}

            # Phase: Transparency
            yield {"type": "progress", "phase": "finalize", "message": "Finalizing…", "progress": 96}

            total_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            meta = final_payload.get('meta') or {}
            meta.update({
                'sse_total_ms': total_ms,
                'sse_started_at': start_time.isoformat()
            })
            final_payload['meta'] = meta

            yield {"type": "result", "status": "success", "data": final_payload, "progress": 100}
            logger.info(f"✅ Auto-fill refresh stream completed for user: {actual_user_id} in {total_ms} ms")
        except Exception as e:
            logger.error(f"❌ Error in auto-fill refresh stream: {str(e)}")
            yield {"type": "error", "message": str(e), "timestamp": datetime.utcnow().isoformat()}

    return StreamingResponse(
        stream_data(refresh_generator()),
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

@router.post("/autofill/refresh")
async def refresh_autofill(
    user_id: Optional[int] = Query(None, description="User ID to build auto-fill for"),
    use_ai: bool = Query(True, description="Use AI augmentation during refresh"),
    ai_only: bool = Query(False, description="AI-first refresh: return AI overrides when available"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Non-stream endpoint to return a fresh auto-fill payload (no DB writes)."""
    try:
        actual_user_id = user_id or 1
        started = datetime.utcnow()
        refresh_service = AutoFillRefreshService(db)
        payload = await refresh_service.build_fresh_payload_with_transparency(actual_user_id, use_ai=use_ai, ai_only=ai_only)
        total_ms = int((datetime.utcnow() - started).total_seconds() * 1000)
        meta = payload.get('meta') or {}
        meta.update({'http_total_ms': total_ms, 'http_started_at': started.isoformat()})
        payload['meta'] = meta
        return ResponseBuilder.create_success_response(
            message="Fresh auto-fill payload generated successfully",
            data=payload
        )
    except Exception as e:
        logger.error(f"❌ Error generating fresh auto-fill payload: {str(e)}")
        raise ContentPlanningErrorHandler.handle_general_error(e, "refresh_autofill") 
