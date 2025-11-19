"""
Main Audio Generation Service for ALwrity Backend.

This service provides AI-powered text-to-speech functionality using WaveSpeed Minimax Speech 02 HD.
"""

from __future__ import annotations

import sys
from typing import Optional, Dict, Any
from datetime import datetime
from loguru import logger
from fastapi import HTTPException

from services.wavespeed.client import WaveSpeedClient
from services.onboarding.api_key_manager import APIKeyManager
from utils.logger_utils import get_service_logger

logger = get_service_logger("audio_generation")


class AudioGenerationResult:
    """Result of audio generation."""
    
    def __init__(
        self,
        audio_bytes: bytes,
        provider: str,
        model: str,
        voice_id: str,
        text_length: int,
        file_size: int,
    ):
        self.audio_bytes = audio_bytes
        self.provider = provider
        self.model = model
        self.voice_id = voice_id
        self.text_length = text_length
        self.file_size = file_size


def generate_audio(
    text: str,
    voice_id: str = "Wise_Woman",
    speed: float = 1.0,
    volume: float = 1.0,
    pitch: float = 0.0,
    emotion: str = "happy",
    user_id: Optional[str] = None,
    **kwargs
) -> AudioGenerationResult:
    """
    Generate audio using AI text-to-speech with subscription tracking.
    
    Args:
        text: Text to convert to speech (max 10000 characters)
        voice_id: Voice ID (default: "Wise_Woman")
        speed: Speech speed (0.5-2.0, default: 1.0)
        volume: Speech volume (0.1-10.0, default: 1.0)
        pitch: Speech pitch (-12 to 12, default: 0.0)
        emotion: Emotion (default: "happy")
        user_id: User ID for subscription checking (required)
        **kwargs: Additional parameters (sample_rate, bitrate, format, etc.)
        
    Returns:
        AudioGenerationResult: Generated audio result
        
    Raises:
        RuntimeError: If subscription limits are exceeded or user_id is missing.
    """
    try:
        logger.info("[audio_gen] Starting audio generation")
        logger.debug(f"[audio_gen] Text length: {len(text)} characters, voice: {voice_id}")
        
        # SUBSCRIPTION CHECK - Required and strict enforcement
        if not user_id:
            raise RuntimeError("user_id is required for subscription checking. Please provide Clerk user ID.")
        
        # Calculate cost based on character count (every character is 1 token)
        # Pricing: $0.05 per 1,000 characters
        character_count = len(text)
        cost_per_1000_chars = 0.05
        estimated_cost = (character_count / 1000.0) * cost_per_1000_chars
        
        try:
            from services.database import get_db
            from services.subscription import PricingService
            from models.subscription_models import UsageSummary, APIProvider
            
            db = next(get_db())
            try:
                pricing_service = PricingService(db)
                
                # Check limits using sync method from pricing service (strict enforcement)
                # Use AUDIO provider for audio generation
                can_proceed, message, usage_info = pricing_service.check_usage_limits(
                    user_id=user_id,
                    provider=APIProvider.AUDIO,
                    tokens_requested=character_count,  # Use character count as "tokens" for audio
                    actual_provider_name="wavespeed"  # Actual provider is WaveSpeed
                )
                
                if not can_proceed:
                    logger.warning(f"[audio_gen] Subscription limit exceeded for user {user_id}: {message}")
                    error_detail = {
                        'error': message,
                        'message': message,
                        'provider': 'wavespeed',
                        'usage_info': usage_info if usage_info else {}
                    }
                    raise HTTPException(status_code=429, detail=error_detail)
                
                # Get current usage for limit checking
                current_period = pricing_service.get_current_billing_period(user_id) or datetime.now().strftime("%Y-%m")
                usage = db.query(UsageSummary).filter(
                    UsageSummary.user_id == user_id,
                    UsageSummary.billing_period == current_period
                ).first()
                
            finally:
                db.close()
        except HTTPException:
            raise
        except RuntimeError:
            raise
        except Exception as sub_error:
            logger.error(f"[audio_gen] Subscription check failed for user {user_id}: {sub_error}")
            raise RuntimeError(f"Subscription check failed: {str(sub_error)}")
        
        # Generate audio using WaveSpeed
        try:
            client = WaveSpeedClient()
            audio_bytes = client.generate_speech(
                text=text,
                voice_id=voice_id,
                speed=speed,
                volume=volume,
                pitch=pitch,
                emotion=emotion,
                enable_sync_mode=True,
                **kwargs
            )
            
            logger.info(f"[audio_gen] ✅ API call successful, generated {len(audio_bytes)} bytes")
            
        except HTTPException:
            raise
        except Exception as api_error:
            logger.error(f"[audio_gen] Audio generation API failed: {api_error}")
            raise HTTPException(
                status_code=502,
                detail={
                    "error": "Audio generation failed",
                    "message": str(api_error)
                }
            )
        
        # TRACK USAGE after successful API call
        if audio_bytes:
            logger.info(f"[audio_gen] ✅ API call successful, tracking usage for user {user_id}")
            try:
                db_track = next(get_db())
                try:
                    from models.subscription_models import UsageSummary, APIUsageLog, APIProvider
                    from services.subscription import PricingService
                    
                    pricing = PricingService(db_track)
                    current_period = pricing.get_current_billing_period(user_id) or datetime.now().strftime("%Y-%m")
                    
                    # Get or create usage summary
                    summary = db_track.query(UsageSummary).filter(
                        UsageSummary.user_id == user_id,
                        UsageSummary.billing_period == current_period
                    ).first()
                    
                    if not summary:
                        summary = UsageSummary(
                            user_id=user_id,
                            billing_period=current_period
                        )
                        db_track.add(summary)
                        db_track.flush()
                    
                    # Get current values before update
                    current_calls_before = getattr(summary, "audio_calls", 0) or 0
                    current_cost_before = getattr(summary, "audio_cost", 0.0) or 0.0
                    
                    # Update audio calls and cost
                    new_calls = current_calls_before + 1
                    new_cost = current_cost_before + estimated_cost
                    
                    # Use direct SQL UPDATE for dynamic attributes
                    from sqlalchemy import text
                    update_query = text("""
                        UPDATE usage_summaries 
                        SET audio_calls = :new_calls,
                            audio_cost = :new_cost
                        WHERE user_id = :user_id AND billing_period = :period
                    """)
                    db_track.execute(update_query, {
                        'new_calls': new_calls,
                        'new_cost': new_cost,
                        'user_id': user_id,
                        'period': current_period
                    })
                    
                    # Update total cost
                    summary.total_cost = (summary.total_cost or 0.0) + estimated_cost
                    summary.total_calls = (summary.total_calls or 0) + 1
                    summary.updated_at = datetime.utcnow()
                    
                    # Create usage log
                    usage_log = APIUsageLog(
                        user_id=user_id,
                        provider=APIProvider.AUDIO,
                        endpoint="/audio-generation/wavespeed",
                        method="POST",
                        model_used="minimax/speech-02-hd",
                        tokens_input=character_count,
                        tokens_output=0,
                        tokens_total=character_count,
                        cost_input=0.0,
                        cost_output=0.0,
                        cost_total=estimated_cost,
                        response_time=0.0,
                        status_code=200,
                        request_size=len(text.encode("utf-8")),
                        response_size=len(audio_bytes),
                        billing_period=current_period,
                    )
                    db_track.add(usage_log)
                    
                    # Get plan details for unified log
                    limits = pricing.get_user_limits(user_id)
                    plan_name = limits.get('plan_name', 'unknown') if limits else 'unknown'
                    tier = limits.get('tier', 'unknown') if limits else 'unknown'
                    audio_limit = limits['limits'].get("audio_calls", 0) if limits else 0
                    # Only show ∞ for Enterprise tier when limit is 0 (unlimited)
                    audio_limit_display = audio_limit if (audio_limit > 0 or tier != 'enterprise') else '∞'
                    
                    # Get related stats for unified log
                    current_image_calls = getattr(summary, "stability_calls", 0) or 0
                    image_limit = limits['limits'].get("stability_calls", 0) if limits else 0
                    current_image_edit_calls = getattr(summary, "image_edit_calls", 0) or 0
                    image_edit_limit = limits['limits'].get("image_edit_calls", 0) if limits else 0
                    current_video_calls = getattr(summary, "video_calls", 0) or 0
                    video_limit = limits['limits'].get("video_calls", 0) if limits else 0
                    
                    db_track.commit()
                    logger.info(f"[audio_gen] ✅ Successfully tracked usage: user {user_id} -> audio -> {new_calls} calls, ${estimated_cost:.4f}")
                    
                    # UNIFIED SUBSCRIPTION LOG - Shows before/after state in one message
                    print(f"""
[SUBSCRIPTION] Audio Generation
├─ User: {user_id}
├─ Plan: {plan_name} ({tier})
├─ Provider: wavespeed
├─ Actual Provider: wavespeed
├─ Model: minimax/speech-02-hd
├─ Voice: {voice_id}
├─ Calls: {current_calls_before} → {new_calls} / {audio_limit_display}
├─ Cost: ${current_cost_before:.4f} → ${new_cost:.4f}
├─ Characters: {character_count}
├─ Images: {current_image_calls} / {image_limit if image_limit > 0 else '∞'}
├─ Image Editing: {current_image_edit_calls} / {image_edit_limit if image_edit_limit > 0 else '∞'}
├─ Videos: {current_video_calls} / {video_limit if video_limit > 0 else '∞'}
└─ Status: ✅ Allowed & Tracked
""", flush=True)
                    sys.stdout.flush()
                    
                except Exception as track_error:
                    logger.error(f"[audio_gen] ❌ Error tracking usage (non-blocking): {track_error}", exc_info=True)
                    db_track.rollback()
                finally:
                    db_track.close()
            except Exception as usage_error:
                logger.error(f"[audio_gen] ❌ Failed to track usage: {usage_error}", exc_info=True)
        
        return AudioGenerationResult(
            audio_bytes=audio_bytes,
            provider="wavespeed",
            model="minimax/speech-02-hd",
            voice_id=voice_id,
            text_length=character_count,
            file_size=len(audio_bytes),
        )
        
    except HTTPException:
        raise
    except RuntimeError:
        raise
    except Exception as e:
        logger.error(f"[audio_gen] Error generating audio: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Audio generation failed",
                "message": str(e)
            }
        )

