from __future__ import annotations

import base64
import os
import uuid
from typing import Optional, Dict, Any
from datetime import datetime
from pathlib import Path
from sqlalchemy.orm import Session

from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from services.llm_providers.main_image_generation import generate_image
from services.llm_providers.main_image_editing import edit_image
from services.llm_providers.main_text_generation import llm_text_gen
from utils.logger_utils import get_service_logger
from middleware.auth_middleware import get_current_user
from services.database import get_db
from services.subscription import UsageTrackingService, PricingService
from models.subscription_models import APIProvider, UsageSummary
from utils.asset_tracker import save_asset_to_library
from utils.file_storage import save_file_safely, generate_unique_filename, sanitize_filename


router = APIRouter(prefix="/api/images", tags=["images"])
logger = get_service_logger("api.images")


class ImageGenerateRequest(BaseModel):
    prompt: str
    negative_prompt: Optional[str] = None
    provider: Optional[str] = Field(None, pattern="^(gemini|huggingface|stability)$")
    model: Optional[str] = None
    width: Optional[int] = Field(default=1024, ge=64, le=2048)
    height: Optional[int] = Field(default=1024, ge=64, le=2048)
    guidance_scale: Optional[float] = None
    steps: Optional[int] = None
    seed: Optional[int] = None


class ImageGenerateResponse(BaseModel):
    success: bool = True
    image_base64: str
    image_url: Optional[str] = None  # URL to saved image file
    width: int
    height: int
    provider: str
    model: Optional[str] = None
    seed: Optional[int] = None


@router.post("/generate", response_model=ImageGenerateResponse)
def generate(
    req: ImageGenerateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> ImageGenerateResponse:
    """Generate image with subscription checking."""
    try:
        # Extract Clerk user ID (required)
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        user_id = str(current_user.get('id', ''))
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid user ID in authentication token")
        
        # Validation is now handled inside generate_image function
        last_error: Optional[Exception] = None
        result = None
        for attempt in range(2):  # simple single retry
            try:
                result = generate_image(
                    prompt=req.prompt,
                    options={
                        "negative_prompt": req.negative_prompt,
                        "provider": req.provider,
                        "model": req.model,
                        "width": req.width,
                        "height": req.height,
                        "guidance_scale": req.guidance_scale,
                        "steps": req.steps,
                        "seed": req.seed,
                    },
                    user_id=user_id,  # Pass user_id for validation inside generate_image
                )
                image_b64 = base64.b64encode(result.image_bytes).decode("utf-8")
                
                # Save image to disk and track in asset library
                image_url = None
                image_filename = None
                image_path = None
                
                try:
                    # Create output directory for image studio images
                    base_dir = Path(__file__).parent.parent
                    output_dir = base_dir / "image_studio_images"
                    
                    # Generate safe filename from prompt
                    clean_prompt = sanitize_filename(req.prompt[:50], max_length=50)
                    image_filename = generate_unique_filename(
                        prefix=f"img_{clean_prompt}",
                        extension=".png",
                        include_uuid=True
                    )
                    
                    # Save file safely
                    image_path, save_error = save_file_safely(
                        content=result.image_bytes,
                        directory=output_dir,
                        filename=image_filename,
                        max_file_size=50 * 1024 * 1024  # 50MB for images
                    )
                    
                    if image_path and not save_error:
                        # Generate file URL (will be served via API endpoint)
                        image_url = f"/api/images/image-studio/images/{image_path.name}"
                        
                        logger.info(f"[images.generate] Saved image to: {image_path} ({len(result.image_bytes)} bytes)")
                        
                        # Save to asset library (non-blocking)
                        try:
                            asset_id = save_asset_to_library(
                                db=db,
                                user_id=user_id,
                                asset_type="image",
                                source_module="image_studio",
                                filename=image_path.name,
                                file_url=image_url,
                                file_path=str(image_path),
                                file_size=len(result.image_bytes),
                                mime_type="image/png",
                                title=req.prompt[:100] if len(req.prompt) <= 100 else req.prompt[:97] + "...",
                                description=f"Generated image: {req.prompt[:200]}" if len(req.prompt) > 200 else req.prompt,
                                prompt=req.prompt,
                                tags=["image_studio", "generated", result.provider] if result.provider else ["image_studio", "generated"],
                                provider=result.provider,
                                model=result.model,
                                asset_metadata={
                                    "width": result.width,
                                    "height": result.height,
                                    "seed": result.seed,
                                    "status": "completed",
                                    "negative_prompt": req.negative_prompt
                                }
                            )
                            if asset_id:
                                logger.info(f"[images.generate] ✅ Asset saved to library: ID={asset_id}, filename={image_path.name}")
                            else:
                                logger.warning(f"[images.generate] Asset tracking returned None (may have failed silently)")
                        except Exception as asset_error:
                            logger.error(f"[images.generate] Failed to save asset to library: {asset_error}", exc_info=True)
                            # Don't fail the request if asset tracking fails
                    else:
                        logger.warning(f"[images.generate] Failed to save image to disk: {save_error}")
                        # Continue without failing the request - base64 is still available
                except Exception as save_error:
                    logger.error(f"[images.generate] Unexpected error saving image: {save_error}", exc_info=True)
                    # Continue without failing the request
                
                # TRACK USAGE after successful image generation
                if result:
                    logger.info(f"[images.generate] ✅ Image generation successful, tracking usage for user {user_id}")
                    try:
                        db_track = next(get_db())
                        try:
                            # Get or create usage summary
                            pricing = PricingService(db_track)
                            current_period = pricing.get_current_billing_period(user_id) or datetime.now().strftime("%Y-%m")
                            
                            logger.debug(f"[images.generate] Looking for usage summary: user_id={user_id}, period={current_period}")
                            
                            summary = db_track.query(UsageSummary).filter(
                                UsageSummary.user_id == user_id,
                                UsageSummary.billing_period == current_period
                            ).first()
                            
                            if not summary:
                                logger.info(f"[images.generate] Creating new usage summary for user {user_id}, period {current_period}")
                                summary = UsageSummary(
                                    user_id=user_id,
                                    billing_period=current_period
                                )
                                db_track.add(summary)
                                db_track.flush()  # Ensure summary is persisted before updating
                            
                            # Get "before" state for unified log
                            current_calls_before = getattr(summary, "stability_calls", 0) or 0
                            
                            # Update provider-specific counters (stability for image generation)
                            # Note: All image generation goes through STABILITY provider enum regardless of actual provider
                            new_calls = current_calls_before + 1
                            setattr(summary, "stability_calls", new_calls)
                            logger.debug(f"[images.generate] Updated stability_calls: {current_calls_before} -> {new_calls}")
                            
                            # Update totals
                            old_total_calls = summary.total_calls or 0
                            summary.total_calls = old_total_calls + 1
                            logger.debug(f"[images.generate] Updated totals: calls {old_total_calls} -> {summary.total_calls}")
                            
                            # Get plan details for unified log
                            limits = pricing.get_user_limits(user_id)
                            plan_name = limits.get('plan_name', 'unknown') if limits else 'unknown'
                            tier = limits.get('tier', 'unknown') if limits else 'unknown'
                            call_limit = limits['limits'].get("stability_calls", 0) if limits else 0
                            
                            # Get image editing stats for unified log
                            current_image_edit_calls = getattr(summary, "image_edit_calls", 0) or 0
                            image_edit_limit = limits['limits'].get("image_edit_calls", 0) if limits else 0
                            
                            # Get video stats for unified log
                            current_video_calls = getattr(summary, "video_calls", 0) or 0
                            video_limit = limits['limits'].get("video_calls", 0) if limits else 0
                            
                            # Get audio stats for unified log
                            current_audio_calls = getattr(summary, "audio_calls", 0) or 0
                            audio_limit = limits['limits'].get("audio_calls", 0) if limits else 0
                            # Only show ∞ for Enterprise tier when limit is 0 (unlimited)
                            audio_limit_display = audio_limit if (audio_limit > 0 or tier != 'enterprise') else '∞'
                            
                            db_track.commit()
                            logger.info(f"[images.generate] ✅ Successfully tracked usage: user {user_id} -> stability -> {new_calls} calls")
                            
                            # UNIFIED SUBSCRIPTION LOG - Shows before/after state in one message
                            print(f"""
[SUBSCRIPTION] Image Generation
├─ User: {user_id}
├─ Plan: {plan_name} ({tier})
├─ Provider: stability
├─ Actual Provider: {result.provider}
├─ Model: {result.model or 'default'}
├─ Calls: {current_calls_before} → {new_calls} / {call_limit if call_limit > 0 else '∞'}
├─ Image Editing: {current_image_edit_calls} / {image_edit_limit if image_edit_limit > 0 else '∞'}
├─ Videos: {current_video_calls} / {video_limit if video_limit > 0 else '∞'}
├─ Audio: {current_audio_calls} / {audio_limit_display}
└─ Status: ✅ Allowed & Tracked
""")
                        except Exception as track_error:
                            logger.error(f"[images.generate] ❌ Error tracking usage (non-blocking): {track_error}", exc_info=True)
                            db_track.rollback()
                        finally:
                            db_track.close()
                    except Exception as usage_error:
                        # Non-blocking: log error but don't fail the request
                        logger.error(f"[images.generate] ❌ Failed to track usage: {usage_error}", exc_info=True)
                
                return ImageGenerateResponse(
                    image_base64=image_b64,
                    image_url=image_url,
                    width=result.width,
                    height=result.height,
                    provider=result.provider,
                    model=result.model,
                    seed=result.seed,
                )
            except Exception as inner:
                last_error = inner
                logger.error(f"Image generation attempt {attempt+1} failed: {inner}")
                # On first failure, try provider auto-remap by clearing provider to let facade decide
                if attempt == 0 and req.provider:
                    req.provider = None
                    continue
                break
        raise last_error or RuntimeError("Unknown image generation error")
    except Exception as e:
        logger.error(f"Image generation failed: {e}")
        # Provide a clean, actionable message to the client
        raise HTTPException(
            status_code=500,
            detail="Image generation service is temporarily unavailable or the connection was reset. Please try again."
        )


class PromptSuggestion(BaseModel):
    prompt: str
    negative_prompt: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    overlay_text: Optional[str] = None


class ImagePromptSuggestRequest(BaseModel):
    provider: Optional[str] = Field(None, pattern="^(gemini|huggingface|stability)$")
    title: Optional[str] = None
    section: Optional[Dict[str, Any]] = None
    research: Optional[Dict[str, Any]] = None
    persona: Optional[Dict[str, Any]] = None
    include_overlay: Optional[bool] = True


class ImagePromptSuggestResponse(BaseModel):
    suggestions: list[PromptSuggestion]


class ImageEditRequest(BaseModel):
    image_base64: str
    prompt: str
    provider: Optional[str] = Field(None, pattern="^(huggingface)$")
    model: Optional[str] = None
    guidance_scale: Optional[float] = None
    steps: Optional[int] = None
    seed: Optional[int] = None


class ImageEditResponse(BaseModel):
    success: bool = True
    image_base64: str
    image_url: Optional[str] = None  # URL to saved edited image file
    width: int
    height: int
    provider: str
    model: Optional[str] = None
    seed: Optional[int] = None


@router.post("/suggest-prompts", response_model=ImagePromptSuggestResponse)
def suggest_prompts(
    req: ImagePromptSuggestRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> ImagePromptSuggestResponse:
    try:
        provider = (req.provider or ("gemini" if (os.getenv("GPT_PROVIDER") or "").lower().startswith("gemini") else "huggingface")).lower()
        section = req.section or {}
        title = (req.title or section.get("heading") or "").strip()
        subheads = section.get("subheadings", []) or []
        key_points = section.get("key_points", []) or []
        keywords = section.get("keywords", []) or []
        if not keywords and req.research:
            keywords = (
                req.research.get("keywords", {}).get("primary_keywords")
                or req.research.get("keywords", {}).get("primary")
                or []
            )

        persona = req.persona or {}
        audience = persona.get("audience", "content creators and digital marketers")
        industry = persona.get("industry", req.research.get("domain") if req.research else "your industry")
        tone = persona.get("tone", "professional, trustworthy")

        schema = {
            "type": "object",
            "properties": {
                "suggestions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "prompt": {"type": "string"},
                            "negative_prompt": {"type": "string"},
                            "width": {"type": "number"},
                            "height": {"type": "number"},
                            "overlay_text": {"type": "string"},
                        },
                        "required": ["prompt"]
                    },
                    "minItems": 3,
                    "maxItems": 5
                }
            },
            "required": ["suggestions"]
        }

        system = (
            "You are an expert image prompt engineer for text-to-image models. "
            "Given blog section context, craft 3-5 hyper-personalized prompts optimized for the specified provider. "
            "Return STRICT JSON matching the provided schema, no extra text."
        )

        provider_guidance = {
            "huggingface": "Photorealistic Flux 1 Krea Dev; include camera/lighting cues (e.g., 50mm, f/2.8, rim light).",
            "gemini": "Editorial, brand-safe, crisp edges, balanced lighting; avoid artifacts.",
            "stability": "SDXL coherent details, sharp focus, cinematic contrast; readable text if present."
        }.get(provider, "")

        best_practices = (
            "Best Practices: one clear focal subject; clean, uncluttered background; rule-of-thirds or center-weighted composition; "
            "text-safe margins if overlay text is included; neutral lighting if unsure; realistic skin tones; avoid busy patterns; "
            "no brand logos or watermarks; no copyrighted characters; avoid low-res, blur, noise, banding, oversaturation, over-sharpening; "
            "ensure hands and text are coherent if present; prefer 1024px+ on shortest side for quality."
        )

        # Harvest a few concise facts from research if available
        facts: list[str] = []
        try:
            if req.research:
                # try common shapes used in research service
                top_stats = req.research.get("key_facts") or req.research.get("highlights") or []
                if isinstance(top_stats, list):
                    facts = [str(x) for x in top_stats[:3]]
                elif isinstance(top_stats, dict):
                    facts = [f"{k}: {v}" for k, v in list(top_stats.items())[:3]]
        except Exception:
            facts = []

        facts_line = ", ".join(facts) if facts else ""

        overlay_hint = "Include an on-image short title or fact if it improves communication; ensure clean, high-contrast safe area for text." if (req.include_overlay is None or req.include_overlay) else "Do not include on-image text."

        prompt = f"""
        Provider: {provider}
        Title: {title}
        Subheadings: {', '.join(subheads[:5])}
        Key Points: {', '.join(key_points[:5])}
        Keywords: {', '.join([str(k) for k in keywords[:8]])}
        Research Facts: {facts_line}
        Audience: {audience}
        Industry: {industry}
        Tone: {tone}

        Craft prompts that visually reflect this exact section (not generic blog topic). {provider_guidance}
        {best_practices}
        {overlay_hint}
        Include a suitable negative_prompt where helpful. Suggest width/height when relevant (e.g., 1024x1024 or 1920x1080).
        If including on-image text, return it in overlay_text (short: <= 8 words).
        """

        # Get user_id for llm_text_gen subscription check (required)
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        user_id_for_llm = str(current_user.get('id', ''))
        if not user_id_for_llm:
            raise HTTPException(status_code=401, detail="Invalid user ID in authentication token")
        
        raw = llm_text_gen(prompt=prompt, system_prompt=system, json_struct=schema, user_id=user_id_for_llm)
        data = raw if isinstance(raw, dict) else {}
        suggestions = data.get("suggestions") or []
        # basic fallback if provider returns string
        if not suggestions and isinstance(raw, str):
            suggestions = [{"prompt": raw}]

        return ImagePromptSuggestResponse(suggestions=[PromptSuggestion(**s) for s in suggestions])
    except Exception as e:
        logger.error(f"Prompt suggestion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/edit", response_model=ImageEditResponse)
def edit(
    req: ImageEditRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> ImageEditResponse:
    """Edit image with subscription checking."""
    try:
        # Extract Clerk user ID (required)
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        user_id = str(current_user.get('id', ''))
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid user ID in authentication token")
        
        # Decode base64 image
        try:
            input_image_bytes = base64.b64decode(req.image_base64)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid image_base64: {str(e)}")
        
        # Validation is now handled inside edit_image function
        result = edit_image(
            input_image_bytes=input_image_bytes,
            prompt=req.prompt,
            options={
                "provider": req.provider,
                "model": req.model,
                "guidance_scale": req.guidance_scale,
                "steps": req.steps,
                "seed": req.seed,
            },
            user_id=user_id,  # Pass user_id for validation inside edit_image
        )
        edited_image_b64 = base64.b64encode(result.image_bytes).decode("utf-8")
        
        # Save edited image to disk and track in asset library
        image_url = None
        image_filename = None
        image_path = None
        
        try:
            # Create output directory for image studio edited images
            base_dir = Path(__file__).parent.parent
            output_dir = base_dir / "image_studio_images" / "edited"
            
            # Generate safe filename from prompt
            clean_prompt = sanitize_filename(req.prompt[:50], max_length=50)
            image_filename = generate_unique_filename(
                prefix=f"edited_{clean_prompt}",
                extension=".png",
                include_uuid=True
            )
            
            # Save file safely
            image_path, save_error = save_file_safely(
                content=result.image_bytes,
                directory=output_dir,
                filename=image_filename,
                max_file_size=50 * 1024 * 1024  # 50MB for images
            )
            
            if image_path and not save_error:
                # Generate file URL
                image_url = f"/api/images/image-studio/images/edited/{image_path.name}"
                
                logger.info(f"[images.edit] Saved edited image to: {image_path} ({len(result.image_bytes)} bytes)")
                
                # Save to asset library (non-blocking)
                try:
                    asset_id = save_asset_to_library(
                        db=db,
                        user_id=user_id,
                        asset_type="image",
                        source_module="image_studio",
                        filename=image_path.name,
                        file_url=image_url,
                        file_path=str(image_path),
                        file_size=len(result.image_bytes),
                        mime_type="image/png",
                        title=f"Edited: {req.prompt[:100]}" if len(req.prompt) <= 100 else f"Edited: {req.prompt[:97]}...",
                        description=f"Edited image with prompt: {req.prompt[:200]}" if len(req.prompt) > 200 else f"Edited image with prompt: {req.prompt}",
                        prompt=req.prompt,
                        tags=["image_studio", "edited", result.provider] if result.provider else ["image_studio", "edited"],
                        provider=result.provider,
                        model=result.model,
                        asset_metadata={
                            "width": result.width,
                            "height": result.height,
                            "seed": result.seed,
                            "status": "completed",
                            "operation": "edit"
                        }
                    )
                    if asset_id:
                        logger.info(f"[images.edit] ✅ Asset saved to library: ID={asset_id}, filename={image_path.name}")
                    else:
                        logger.warning(f"[images.edit] Asset tracking returned None (may have failed silently)")
                except Exception as asset_error:
                    logger.error(f"[images.edit] Failed to save asset to library: {asset_error}", exc_info=True)
                    # Don't fail the request if asset tracking fails
            else:
                logger.warning(f"[images.edit] Failed to save edited image to disk: {save_error}")
                # Continue without failing the request - base64 is still available
        except Exception as save_error:
            logger.error(f"[images.edit] Unexpected error saving edited image: {save_error}", exc_info=True)
            # Continue without failing the request
        
        # TRACK USAGE after successful image editing
        if result:
            logger.info(f"[images.edit] ✅ Image editing successful, tracking usage for user {user_id}")
            try:
                db_track = next(get_db())
                try:
                    # Get or create usage summary
                    pricing = PricingService(db_track)
                    current_period = pricing.get_current_billing_period(user_id) or datetime.now().strftime("%Y-%m")
                    
                    logger.debug(f"[images.edit] Looking for usage summary: user_id={user_id}, period={current_period}")
                    
                    summary = db_track.query(UsageSummary).filter(
                        UsageSummary.user_id == user_id,
                        UsageSummary.billing_period == current_period
                    ).first()
                    
                    if not summary:
                        logger.info(f"[images.edit] Creating new usage summary for user {user_id}, period {current_period}")
                        summary = UsageSummary(
                            user_id=user_id,
                            billing_period=current_period
                        )
                        db_track.add(summary)
                        db_track.flush()  # Ensure summary is persisted before updating
                    
                    # Get "before" state for unified log
                    current_calls_before = getattr(summary, "image_edit_calls", 0) or 0
                    
                    # Update image editing counters (separate from image generation)
                    new_calls = current_calls_before + 1
                    setattr(summary, "image_edit_calls", new_calls)
                    logger.debug(f"[images.edit] Updated image_edit_calls: {current_calls_before} -> {new_calls}")
                    
                    # Update totals
                    old_total_calls = summary.total_calls or 0
                    summary.total_calls = old_total_calls + 1
                    logger.debug(f"[images.edit] Updated totals: calls {old_total_calls} -> {summary.total_calls}")
                    
                    # Get plan details for unified log
                    limits = pricing.get_user_limits(user_id)
                    plan_name = limits.get('plan_name', 'unknown') if limits else 'unknown'
                    tier = limits.get('tier', 'unknown') if limits else 'unknown'
                    call_limit = limits['limits'].get("image_edit_calls", 0) if limits else 0
                    
                    # Get image generation stats for unified log
                    current_image_gen_calls = getattr(summary, "stability_calls", 0) or 0
                    image_gen_limit = limits['limits'].get("stability_calls", 0) if limits else 0
                    
                    # Get video stats for unified log
                    current_video_calls = getattr(summary, "video_calls", 0) or 0
                    video_limit = limits['limits'].get("video_calls", 0) if limits else 0
                    
                    # Get audio stats for unified log
                    current_audio_calls = getattr(summary, "audio_calls", 0) or 0
                    audio_limit = limits['limits'].get("audio_calls", 0) if limits else 0
                    # Only show ∞ for Enterprise tier when limit is 0 (unlimited)
                    audio_limit_display = audio_limit if (audio_limit > 0 or tier != 'enterprise') else '∞'
                    
                    db_track.commit()
                    logger.info(f"[images.edit] ✅ Successfully tracked usage: user {user_id} -> image_edit -> {new_calls} calls")
                    
                    # UNIFIED SUBSCRIPTION LOG - Shows before/after state in one message
                    print(f"""
[SUBSCRIPTION] Image Editing
├─ User: {user_id}
├─ Plan: {plan_name} ({tier})
├─ Provider: image_edit
├─ Actual Provider: {result.provider}
├─ Model: {result.model or 'default'}
├─ Calls: {current_calls_before} → {new_calls} / {call_limit if call_limit > 0 else '∞'}
├─ Images: {current_image_gen_calls} / {image_gen_limit if image_gen_limit > 0 else '∞'}
├─ Videos: {current_video_calls} / {video_limit if video_limit > 0 else '∞'}
├─ Audio: {current_audio_calls} / {audio_limit_display}
└─ Status: ✅ Allowed & Tracked
""")
                except Exception as track_error:
                    logger.error(f"[images.edit] ❌ Error tracking usage (non-blocking): {track_error}", exc_info=True)
                    db_track.rollback()
                finally:
                    db_track.close()
            except Exception as usage_error:
                # Non-blocking: log error but don't fail the request
                logger.error(f"[images.edit] ❌ Failed to track usage: {usage_error}", exc_info=True)
        
        return ImageEditResponse(
            image_base64=edited_image_b64,
            image_url=image_url,
            width=result.width,
            height=result.height,
            provider=result.provider,
            model=result.model,
            seed=result.seed,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Image editing failed: {e}", exc_info=True)
        # Provide a clean, actionable message to the client
        raise HTTPException(
            status_code=500,
            detail="Image editing service is temporarily unavailable or the connection was reset. Please try again."
        )


# ---------------------------
# Image Serving Endpoints
# ---------------------------

@router.get("/image-studio/images/{image_filename:path}")
async def serve_image_studio_image(
    image_filename: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Serve a generated or edited image from Image Studio."""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        # Determine if it's an edited image or regular image
        base_dir = Path(__file__).parent.parent
        image_studio_dir = (base_dir / "image_studio_images").resolve()
        
        if image_filename.startswith("edited/"):
            # Remove "edited/" prefix and serve from edited directory
            actual_filename = image_filename.replace("edited/", "", 1)
            image_path = (image_studio_dir / "edited" / actual_filename).resolve()
            base_subdir = (image_studio_dir / "edited").resolve()
        else:
            image_path = (image_studio_dir / image_filename).resolve()
            base_subdir = image_studio_dir
        
        # Security: Prevent directory traversal attacks
        # Ensure the resolved path is within the intended directory
        try:
            image_path.relative_to(base_subdir)
        except ValueError:
            raise HTTPException(
                status_code=403,
                detail="Access denied: Invalid image path"
            )
        
        if not image_path.exists():
            raise HTTPException(status_code=404, detail="Image not found")
        
        return FileResponse(
            path=str(image_path),
            media_type="image/png",
            filename=image_path.name
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[images] Failed to serve image: {e}")
        raise HTTPException(status_code=500, detail=str(e))

