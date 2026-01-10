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
    provider: Optional[str] = Field(None, pattern="^(gemini|huggingface|stability|wavespeed)$")
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
                
                # Create response with explicit success field
                # Note: Asset saving and usage tracking are non-blocking and won't affect this response
                response = ImageGenerateResponse(
                    success=True,
                    image_base64=image_b64,
                    image_url=image_url,
                    width=result.width,
                    height=result.height,
                    provider=result.provider,
                    model=result.model,
                    seed=result.seed,
                )
                
                logger.info(f"[images.generate] ✅ Returning successful response: provider={result.provider}, model={result.model}, size={len(image_b64)} chars")
                
                # Return response immediately - any post-processing errors won't affect the response
                return response
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
    provider: Optional[str] = Field(None, pattern="^(gemini|huggingface|stability|wavespeed)$")
    model: Optional[str] = None  # Specific model (e.g., "qwen-image", "ideogram-v3-turbo")
    image_type: Optional[str] = Field(None, pattern="^(realistic|chart|conceptual|diagram|illustration|background)$")
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


# Model-specific guidance for prompt optimization
MODEL_SPECIFIC_GUIDANCE = {
    "ideogram-v3-turbo": {
        "text_overlay": {
            "guidance": "Ideogram V3 excels at rendering readable text. Use simple, bold text (max 3-5 words). Avoid complex infographics - instead create clean backgrounds with designated text areas.",
            "best_practices": [
                "Use high contrast areas (top 20% or bottom 20%) for text placement",
                "Keep text simple: headlines, statistics, or short phrases only",
                "Avoid rendering text as part of complex graphics",
                "Design with 'text overlay zones' in mind, not embedded text"
            ],
            "negative_prompt_additions": "complex infographics, detailed charts with text, busy data visualizations"
        },
        "realistic": {
            "guidance": "Photorealistic generation with professional quality. Include camera settings and lighting cues.",
            "best_practices": [
                "Include camera settings: '50mm lens, f/2.8, professional photography'",
                "Specify lighting: 'natural lighting, soft shadows, rim light'",
                "Add quality descriptors: 'high quality, detailed, sharp focus'"
            ]
        },
        "chart": {
            "guidance": "Simple bar charts or pie charts with minimal text. Use high contrast areas for labels.",
            "best_practices": [
                "Avoid complex infographics - use simple visual representations",
                "Design with text overlay zones, not embedded text",
                "Use abstract data visualization elements"
            ],
            "warnings": ["Complex infographics are too difficult - use simple charts or conceptual representations"]
        },
        "conceptual": {
            "guidance": "Conceptual imagery with photorealistic elements. Clean compositions with text overlay areas.",
            "best_practices": [
                "Focus on visual metaphors and abstract concepts",
                "Design with text overlay zones in mind (top/bottom 30%)",
                "Use simple, clear compositions"
            ]
        }
    },
    "flux-kontext-pro": {
        "text_overlay": {
            "guidance": "FLUX Kontext Pro excels at typography and text rendering with improved prompt adherence. Best for professional designs with text elements.",
            "best_practices": [
                "Excellent for images requiring clear, readable text",
                "Superior typography rendering compared to other models",
                "Improved prompt adherence for consistent results",
                "Can handle text in various styles and sizes",
                "Best for professional blog images with embedded text or typography"
            ],
            "negative_prompt_additions": ""
        },
        "realistic": {
            "guidance": "Photorealistic generation with professional typography support. Include text elements naturally in the composition.",
            "best_practices": [
                "Can render text elements within realistic scenes",
                "Include typography naturally in the design",
                "Specify text style, size, and placement in prompts",
                "Use for professional designs requiring text integration"
            ]
        },
        "chart": {
            "guidance": "Excellent for data visualizations with text labels. Can render simple charts with clear typography.",
            "best_practices": [
                "Can render charts with text labels effectively",
                "Use for data visualizations requiring clear typography",
                "Specify chart type and label requirements clearly",
                "Design with text integration in mind"
            ],
            "warnings": ["Complex infographics may still be challenging - start with simple charts"]
        },
        "diagram": {
            "guidance": "Technical diagrams with clear text labels. Excellent typography for professional diagrams.",
            "best_practices": [
                "Can render diagrams with embedded text labels",
                "Specify text requirements clearly in prompts",
                "Use for technical illustrations requiring typography",
                "Design with text integration as a core element"
            ]
        },
        "illustration": {
            "guidance": "Stylized illustrations with typography support. Professional designs with text elements.",
            "best_practices": [
                "Can integrate text naturally into illustrations",
                "Specify typography style and placement",
                "Use for professional blog illustrations with text",
                "Design with text as a design element"
            ]
        },
        "conceptual": {
            "guidance": "Conceptual imagery with typography capabilities. Can include text elements naturally.",
            "best_practices": [
                "Can integrate text into conceptual designs",
                "Use for abstract concepts with text support",
                "Specify text requirements in prompts",
                "Design with typography as a visual element"
            ]
        }
    },
    "qwen-image": {
        "text_overlay": {
            "guidance": "Qwen Image does NOT render readable text well. Design for text overlay areas only - never ask for text in the image itself.",
            "best_practices": [
                "Create clean backgrounds with high-contrast safe zones",
                "Design simple compositions with space for text (top/bottom 30%)",
                "Use abstract or conceptual imagery that supports text",
                "NEVER request text, words, or labels in the image"
            ],
            "negative_prompt_additions": "text, words, letters, numbers, labels, captions, infographics with text"
        },
        "conceptual": {
            "guidance": "Best for abstract concepts, simple diagrams, and background imagery.",
            "best_practices": [
                "Focus on visual metaphors and abstract representations",
                "Use simple compositions with clear focal points",
                "Avoid complex details or fine textures"
            ]
        },
        "chart": {
            "guidance": "Abstract representation of data - avoid actual charts. Use shapes, colors, and patterns to represent data concepts.",
            "best_practices": [
                "Create visual metaphors for data, not actual charts",
                "Use abstract patterns and shapes",
                "Design with text overlay zones for data labels"
            ],
            "warnings": ["Do not request actual charts with text - use abstract representations instead"]
        },
        "background": {
            "guidance": "Perfect for background images with text overlay areas. Clean, simple compositions.",
            "best_practices": [
                "Focus on clean backgrounds with designated text zones",
                "Use simple, uncluttered compositions",
                "High contrast areas for text placement"
            ]
        }
    }
}


def get_model_specific_guidance(model: Optional[str], image_type: Optional[str]) -> Dict[str, Any]:
    """Get model-specific guidance based on model and image type."""
    if not model:
        return {}
    
    model_lower = model.lower()
    image_type_lower = (image_type or "conceptual").lower()
    
    # Get model guidance
    model_guidance = MODEL_SPECIFIC_GUIDANCE.get(model_lower, {})
    
    # Get image type specific guidance
    type_guidance = model_guidance.get(image_type_lower, model_guidance.get("text_overlay", {}))
    
    return type_guidance


def extract_visual_data(section: Dict[str, Any], research: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Intelligently extract visual-relevant data from section and research."""
    visual_data = {
        "visual_keywords": [],
        "data_points": [],
        "concepts": [],
        "statistics": []
    }
    
    # Extract from section
    if section:
        # Key points that are visualizable
        key_points = section.get("key_points", []) or []
        for point in key_points[:5]:
            if isinstance(point, str):
                # Look for numbers, percentages, comparisons
                if any(char.isdigit() for char in point):
                    visual_data["statistics"].append(point)
                # Look for visual concepts
                elif any(word in point.lower() for word in ["increase", "decrease", "growth", "trend", "pattern", "comparison"]):
                    visual_data["data_points"].append(point)
                else:
                    visual_data["concepts"].append(point)
        
        # Subheadings that suggest visuals
        subheadings = section.get("subheadings", []) or []
        for subhead in subheadings[:3]:
            if isinstance(subhead, str):
                visual_data["concepts"].append(subhead)
        
        # Keywords
        keywords = section.get("keywords", []) or []
        visual_data["visual_keywords"].extend([str(k) for k in keywords[:8] if k])
    
    # Extract from research
    if research:
        # Key facts that are visualizable
        key_facts = research.get("key_facts", []) or research.get("highlights", []) or []
        for fact in key_facts[:3]:
            if isinstance(fact, str):
                if any(char.isdigit() for char in fact):
                    visual_data["statistics"].append(fact)
                else:
                    visual_data["data_points"].append(fact)
        
        # Research insights
        insights = research.get("insights", []) or research.get("summary", "")
        if isinstance(insights, str) and insights:
            # Extract key phrases
            sentences = insights.split('.')[:3]
            visual_data["concepts"].extend([s.strip() for s in sentences if s.strip()])
        elif isinstance(insights, list):
            visual_data["concepts"].extend([str(i) for i in insights[:3]])
    
    return visual_data


@router.post("/suggest-prompts", response_model=ImagePromptSuggestResponse)
def suggest_prompts(
    req: ImagePromptSuggestRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> ImagePromptSuggestResponse:
    try:
        provider = (req.provider or ("gemini" if (os.getenv("GPT_PROVIDER") or "").lower().startswith("gemini") else "huggingface")).lower()
        model = req.model or None
        image_type = req.image_type or "conceptual"
        
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
        
        # Extract visual-relevant data intelligently
        visual_data = extract_visual_data(section, req.research)

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

        # Get model-specific guidance
        model_guidance_data = get_model_specific_guidance(model, image_type)
        model_guidance_text = model_guidance_data.get("guidance", "")
        model_best_practices = model_guidance_data.get("best_practices", [])
        model_warnings = model_guidance_data.get("warnings", [])
        negative_prompt_additions = model_guidance_data.get("negative_prompt_additions", "")

        # Build provider guidance with model-specific details
        provider_guidance_base = {
            "huggingface": "Photorealistic Flux 1 Krea Dev; include camera/lighting cues (e.g., 50mm, f/2.8, rim light).",
            "gemini": "Editorial, brand-safe, crisp edges, balanced lighting; avoid artifacts.",
            "stability": "SDXL coherent details, sharp focus, cinematic contrast; readable text if present.",
            "wavespeed": "Blog-optimized imagery: focus on data visualization, infographics, clean layouts with text overlay areas, professional diagrams, charts, or conceptual illustrations. Avoid random people or poster-style images. Prefer clean backgrounds suitable for text overlays, data representations, or abstract concepts that support the blog content."
        }.get(provider, "")
        
        # Combine provider and model-specific guidance
        provider_guidance = provider_guidance_base
        if model_guidance_text:
            provider_guidance = f"{provider_guidance_base}\n\nMODEL-SPECIFIC GUIDANCE ({model}): {model_guidance_text}"
            if model_best_practices:
                provider_guidance += f"\nBest Practices:\n" + "\n".join([f"- {bp}" for bp in model_best_practices])
            if model_warnings:
                provider_guidance += f"\n⚠️ WARNINGS:\n" + "\n".join([f"- {w}" for w in model_warnings])

        # Build visual data summary from extracted data
        visual_summary_parts = []
        if visual_data["statistics"]:
            visual_summary_parts.append(f"Key Statistics: {', '.join(visual_data['statistics'][:3])}")
        if visual_data["data_points"]:
            visual_summary_parts.append(f"Data Points: {', '.join(visual_data['data_points'][:3])}")
        if visual_data["concepts"]:
            visual_summary_parts.append(f"Visual Concepts: {', '.join(visual_data['concepts'][:5])}")
        if visual_data["visual_keywords"]:
            visual_summary_parts.append(f"Keywords: {', '.join(visual_data['visual_keywords'][:8])}")
        
        visual_summary = "\n".join(visual_summary_parts) if visual_summary_parts else ""

        best_practices = (
            "BLOG IMAGE BEST PRACTICES: Create images optimized for blog content, not social media posters. "
            "Focus on: data visualization elements (charts, graphs, infographics), clean layouts with designated text overlay areas, "
            "professional diagrams, conceptual illustrations, or abstract representations of the topic. "
            "Avoid: random people posing, poster-style compositions, busy social media graphics, or trying to recreate text/words as images. "
            "Instead: use clean backgrounds, simple compositions, areas reserved for text overlays, data-driven visuals, or conceptual imagery. "
            "Technical: one clear focal subject; clean, uncluttered background; text-safe margins (20% padding on all sides for overlays); "
            "neutral or professional lighting; avoid busy patterns; no brand logos or watermarks; no copyrighted characters; "
            "avoid low-res, blur, noise, banding, oversaturation, over-sharpening; prefer 1024px+ on shortest side for quality."
        )

        overlay_hint = (
            "IMPORTANT FOR BLOG IMAGES: Design images with text overlay areas in mind. "
            "Include space for headlines, captions, or data labels. "
            "Suggest overlay_text (short title or key statistic, <= 8 words) that would work well as a text overlay. "
            "Ensure clean, high-contrast safe areas (top 20% or bottom 20% of image) for text placement. "
            "The image should complement text, not replace it - think data visualization, infographics, or clean conceptual imagery."
            if (req.include_overlay is None or req.include_overlay) 
            else "Do not include on-image text, but still design with text overlay areas in mind for blog use."
        )
        
        # Image type specific guidance
        image_type_guidance = {
            "realistic": "Photorealistic style with professional photography quality. Include camera settings and lighting details.",
            "chart": "⚠️ IMPORTANT: Complex infographics are too difficult for current AI models. Create simple visual representations with designated text overlay areas instead. Use abstract data visualization elements, not actual charts with embedded text.",
            "conceptual": "Abstract or conceptual imagery that represents the topic visually. Clean compositions with text overlay zones.",
            "diagram": "Technical diagrams with simple, clear visual elements. Design for text overlay areas, not embedded labels.",
            "illustration": "Stylized illustrations that support the content. Professional, clean aesthetic suitable for blog use.",
            "background": "Background images optimized for text overlays. Clean, uncluttered compositions with high-contrast text zones."
        }.get(image_type, "General blog image guidance.")

        # Build comprehensive prompt with visual data and model-specific guidance
        prompt = f"""
        Provider: {provider}
        Model: {model or 'auto-selected'}
        Image Type: {image_type}
        Title: {title}
        
        VISUAL DATA EXTRACTED FROM CONTENT:
        {visual_summary if visual_summary else f"Subheadings: {', '.join(subheads[:5])}\nKey Points: {', '.join(key_points[:5])}\nKeywords: {', '.join([str(k) for k in keywords[:8]])}"}
        
        CONTEXT:
        Audience: {audience}
        Industry: {industry}
        Tone: {tone}

        BLOG IMAGE GENERATION TASK: Create image prompts optimized for blog content, NOT social media posters.
        
        PROVIDER & MODEL GUIDANCE:
        {provider_guidance}
        
        IMAGE TYPE GUIDANCE:
        {image_type_guidance}
        
        BEST PRACTICES:
        {best_practices}
        
        TEXT OVERLAY GUIDANCE:
        {overlay_hint}
        
        PROMPT GENERATION INSTRUCTIONS:
        Generate 3-5 diverse, well-formed prompt variations that:
        1. Intelligently use the visual data provided above (statistics, data points, concepts, keywords)
        2. Focus on the most visually-relevant elements from the section subheadings, key points, and research
        3. Create prompts that are optimized for the selected image type ({image_type})
        4. Follow model-specific best practices and avoid model limitations
        5. Include clean backgrounds suitable for text overlays
        6. Avoid random people, poster compositions, or trying to render text as images
        7. Support the blog section's content with relevant visual metaphors or data representations
        8. Are optimized for blog article use (not social media)
        
        PROMPT QUALITY REQUIREMENTS:
        - Each prompt should be specific and detailed (50-100 words)
        - Use the visual data intelligently - prioritize statistics and data points for charts, concepts for conceptual images
        - Include visual composition guidance (layout, colors, style)
        - Specify lighting and quality descriptors when appropriate
        - Make prompts actionable and clear for the AI model
        
        NEGATIVE PROMPT:
        Include a suitable negative_prompt that excludes: people posing, social media graphics, posters, text rendered as images, busy compositions, watermarks, logos{f", {negative_prompt_additions}" if negative_prompt_additions else ""}.
        
        DIMENSIONS:
        Suggest width/height when relevant (e.g., 1024x1024 for square, 1920x1080 for landscape blog headers).
        
        OVERLAY TEXT:
        If including overlay text suggestion, return it in overlay_text (short: <= 8 words, typically a key statistic or section title). Use statistics from the visual data when available.
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

