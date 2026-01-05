"""Edit Studio service for AI-powered image editing and transformations."""

from __future__ import annotations

import asyncio
import base64
import io
from dataclasses import dataclass, field
from typing import Any, Dict, Literal, Optional

from PIL import Image

from services.llm_providers.main_image_editing import edit_image as huggingface_edit_image
from services.llm_providers.main_image_generation import generate_image_edit
from services.stability_service import StabilityAIService
from utils.logger_utils import get_service_logger


logger = get_service_logger("image_studio.edit")


EditOperationType = Literal[
    "remove_background",
    "inpaint",
    "outpaint",
    "search_replace",
    "search_recolor",
    "relight",
    "general_edit",
]


@dataclass
class EditStudioRequest:
    """Normalized request payload for Edit Studio operations."""

    image_base64: str
    operation: EditOperationType
    prompt: Optional[str] = None
    negative_prompt: Optional[str] = None
    mask_base64: Optional[str] = None
    search_prompt: Optional[str] = None
    select_prompt: Optional[str] = None
    background_image_base64: Optional[str] = None
    lighting_image_base64: Optional[str] = None
    expand_left: Optional[int] = None
    expand_right: Optional[int] = None
    expand_up: Optional[int] = None
    expand_down: Optional[int] = None
    provider: Optional[str] = None
    model: Optional[str] = None
    style_preset: Optional[str] = None
    guidance_scale: Optional[float] = None
    steps: Optional[int] = None
    seed: Optional[int] = None
    output_format: str = "png"
    options: Dict[str, Any] = field(default_factory=dict)


class EditStudioService:
    """Service layer orchestrating Edit Studio operations."""

    SUPPORTED_OPERATIONS: Dict[EditOperationType, Dict[str, Any]] = {
        "remove_background": {
            "label": "Remove Background",
            "description": "Isolate the main subject and remove the background.",
            "provider": "stability",
            "async": False,
            "fields": {
                "prompt": False,
                "mask": False,
                "negative_prompt": False,
                "search_prompt": False,
                "select_prompt": False,
                "background": False,
                "lighting": False,
                "expansion": False,
            },
        },
        "inpaint": {
            "label": "Inpaint & Fix",
            "description": "Edit specific regions using prompts and optional masks.",
            "provider": "stability",
            "async": False,
            "fields": {
                "prompt": True,
                "mask": True,
                "negative_prompt": True,
                "search_prompt": False,
                "select_prompt": False,
                "background": False,
                "lighting": False,
                "expansion": False,
            },
        },
        "outpaint": {
            "label": "Outpaint",
            "description": "Extend the canvas in any direction with smart fill.",
            "provider": "stability",
            "async": False,
            "fields": {
                "prompt": False,
                "mask": False,
                "negative_prompt": True,
                "search_prompt": False,
                "select_prompt": False,
                "background": False,
                "lighting": False,
                "expansion": True,
            },
        },
        "search_replace": {
            "label": "Search & Replace",
            "description": "Locate objects via search prompt and replace them. Optional mask for precise control.",
            "provider": "stability",
            "async": False,
            "fields": {
                "prompt": True,
                "mask": True,  # Optional mask for precise region selection
                "negative_prompt": False,
                "search_prompt": True,
                "select_prompt": False,
                "background": False,
                "lighting": False,
                "expansion": False,
            },
        },
        "search_recolor": {
            "label": "Search & Recolor",
            "description": "Select elements via prompt and recolor them. Optional mask for exact region selection.",
            "provider": "stability",
            "async": False,
            "fields": {
                "prompt": True,
                "mask": True,  # Optional mask for precise region selection
                "negative_prompt": False,
                "search_prompt": False,
                "select_prompt": True,
                "background": False,
                "lighting": False,
                "expansion": False,
            },
        },
        "relight": {
            "label": "Replace Background & Relight",
            "description": "Swap backgrounds and relight using reference images.",
            "provider": "stability",
            "async": True,
            "fields": {
                "prompt": False,
                "mask": False,
                "negative_prompt": False,
                "search_prompt": False,
                "select_prompt": False,
                "background": True,
                "lighting": True,
                "expansion": False,
            },
        },
        "general_edit": {
            "label": "Prompt-based Edit",
            "description": "Free-form editing powered by Hugging Face image-to-image models. Optional mask for selective editing.",
            "provider": "huggingface",
            "async": False,
            "fields": {
                "prompt": True,
                "mask": True,  # Optional mask for selective region editing
                "negative_prompt": True,
                "search_prompt": False,
                "select_prompt": False,
                "background": False,
                "lighting": False,
                "expansion": False,
            },
        },
    }

    def __init__(self):
        logger.info("[Edit Studio] Initialized edit service")

    @staticmethod
    def _decode_base64_image(value: Optional[str]) -> Optional[bytes]:
        """Decode a base64 (or data URL) string to bytes."""
        if not value:
            return None

        try:
            # Handle data URLs (data:image/png;base64,...)
            if value.startswith("data:"):
                _, b64data = value.split(",", 1)
            else:
                b64data = value

            return base64.b64decode(b64data)
        except Exception as exc:
            logger.error(f"[Edit Studio] Failed to decode base64 image: {exc}")
            raise ValueError("Invalid base64 image payload") from exc

    @staticmethod
    def _image_bytes_to_metadata(image_bytes: bytes) -> Dict[str, Any]:
        """Extract width/height metadata from image bytes."""
        with Image.open(io.BytesIO(image_bytes)) as img:
            return {
                "width": img.width,
                "height": img.height,
            }

    @staticmethod
    def _bytes_to_base64(image_bytes: bytes, output_format: str = "png") -> str:
        """Convert raw bytes to base64 data URL."""
        b64 = base64.b64encode(image_bytes).decode("utf-8")
        return f"data:image/{output_format};base64,{b64}"

    def list_operations(self) -> Dict[str, Dict[str, Any]]:
        """Expose supported operations for UI rendering."""
        return self.SUPPORTED_OPERATIONS
    
    def get_available_models(
        self,
        operation: Optional[str] = None,
        tier: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get available WaveSpeed editing models.
        
        Args:
            operation: Filter by operation type (e.g., "general_edit")
            tier: Filter by tier ("budget", "mid", "premium")
            
        Returns:
            Dictionary with models and metadata
        """
        from services.llm_providers.image_generation.wavespeed_edit_provider import WaveSpeedEditProvider
        
        provider = WaveSpeedEditProvider()
        all_models = provider.get_available_models()
        
        # Filter by operation if specified
        if operation:
            filtered = provider.get_models_by_operation(operation)
            all_models = {k: v for k, v in all_models.items() if k in filtered}
        
        # Filter by tier if specified
        if tier:
            filtered = provider.get_models_by_tier(tier)
            all_models = {k: v for k, v in all_models.items() if k in filtered}
        
        # Format for API response
        models_list = []
        for model_id, model_info in all_models.items():
            models_list.append({
                "id": model_id,
                "name": model_info.get("name", model_id),
                "description": model_info.get("description", ""),
                "cost": model_info.get("cost", 0.02),
                "cost_8k": model_info.get("cost_8k"),  # Optional
                "tier": model_info.get("tier", "mid"),
                "max_resolution": model_info.get("max_resolution", [2048, 2048]),
                "capabilities": model_info.get("capabilities", []),
                "use_cases": self._get_use_cases_for_model(model_id, model_info),
                "features": self._get_features_for_model(model_info),
                "supports_multi_image": model_info.get("supports_multi_image", False),
                "supports_controlnet": model_info.get("supports_controlnet", False),
                "languages": model_info.get("languages", ["en"]),
            })
        
        return {
            "models": models_list,
            "total": len(models_list),
        }
    
    def recommend_model(
        self,
        operation: str,
        image_resolution: Optional[Dict[str, int]] = None,
        user_tier: Optional[str] = None,
        preferences: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Recommend best model for given operation and context.
        
        Args:
            operation: Operation type (e.g., "general_edit")
            image_resolution: Dict with "width" and "height"
            user_tier: User subscription tier ("free", "pro", "enterprise")
            preferences: Dict with "prioritize_cost" or "prioritize_quality"
            
        Returns:
            Dictionary with recommended model and alternatives
        """
        from services.llm_providers.image_generation.wavespeed_edit_provider import WaveSpeedEditProvider
        
        provider = WaveSpeedEditProvider()
        available_models = provider.get_models_by_operation(operation)
        
        if not available_models:
            # Fallback to all models if operation doesn't match
            available_models = provider.get_available_models()
        
        # Filter by resolution if provided
        if image_resolution:
            width = image_resolution.get("width", 0)
            height = image_resolution.get("height", 0)
            max_dimension = max(width, height)
            
            # Filter models that support this resolution
            filtered = {}
            for model_id, model_info in available_models.items():
                max_res = model_info.get("max_resolution", (2048, 2048))
                max_supported = max(max_res[0], max_res[1])
                if max_dimension <= max_supported:
                    filtered[model_id] = model_info
            available_models = filtered
        
        if not available_models:
            # No models match, return first available
            all_models = provider.get_available_models()
            if all_models:
                first_model_id = list(all_models.keys())[0]
                return {
                    "recommended_model": first_model_id,
                    "reason": "No specific match found, using default model",
                    "alternatives": [],
                }
            else:
                raise ValueError("No models available")
        
        # Apply preferences
        prioritize_cost = preferences and preferences.get("prioritize_cost", False)
        prioritize_quality = preferences and preferences.get("prioritize_quality", False)
        
        # Score models
        scored_models = []
        for model_id, model_info in available_models.items():
            score = 0
            cost = model_info.get("cost", 0.02)
            tier = model_info.get("tier", "mid")
            max_res = model_info.get("max_resolution", (2048, 2048))
            max_resolution = max(max_res[0], max_res[1])
            
            # Cost scoring (lower is better)
            if prioritize_cost:
                score += (1.0 / cost) * 100  # Invert cost for scoring
            else:
                score += (1.0 / cost) * 50  # Less weight if not prioritizing
            
            # Quality scoring (higher resolution = better)
            if prioritize_quality:
                score += max_resolution / 10  # Higher weight for quality
            else:
                score += max_resolution / 20  # Lower weight
            
            # Tier preference based on user tier
            if user_tier == "free":
                if tier == "budget":
                    score += 50
                elif tier == "mid":
                    score += 20
            elif user_tier in ["pro", "enterprise"]:
                if tier == "premium":
                    score += 50
                elif tier == "mid":
                    score += 30
            
            scored_models.append((model_id, model_info, score))
        
        # Sort by score (highest first)
        scored_models.sort(key=lambda x: x[2], reverse=True)
        
        # Get recommended model
        recommended_id, recommended_info, recommended_score = scored_models[0]
        
        # Build reason
        reasons = []
        if prioritize_cost:
            reasons.append("Lowest cost option")
        if prioritize_quality:
            reasons.append("Best quality")
        if image_resolution:
            reasons.append(f"Supports {image_resolution.get('width')}×{image_resolution.get('height')} resolution")
        if user_tier == "free" and recommended_info.get("tier") == "budget":
            reasons.append("Budget-friendly for free tier")
        
        reason = ", ".join(reasons) if reasons else "Best match for your requirements"
        
        # Get alternatives (top 2-3)
        alternatives = []
        for model_id, model_info, score in scored_models[1:4]:
            alt_reason = f"Alternative: {model_info.get('tier', 'mid').title()} tier"
            if model_info.get("cost", 0) < recommended_info.get("cost", 0):
                alt_reason += ", lower cost"
            elif model_info.get("cost", 0) > recommended_info.get("cost", 0):
                alt_reason += ", higher quality"
            alternatives.append({
                "model_id": model_id,
                "name": model_info.get("name", model_id),
                "cost": model_info.get("cost", 0.02),
                "reason": alt_reason,
            })
        
        return {
            "recommended_model": recommended_id,
            "reason": reason,
            "alternatives": alternatives,
        }
    
    def _get_use_cases_for_model(self, model_id: str, model_info: Dict[str, Any]) -> list:
        """Get use cases for a model based on its capabilities."""
        use_cases_map = {
            "general_edit": ["Quick edits", "Style changes", "Background replacement"],
            "style_transfer": ["Apply artistic styles", "Style transformations"],
            "text_edit": ["Add text to images", "Edit text in images"],
            "multi_image": ["Batch editing", "Consistent character work"],
            "high_res": ["Professional work", "Print materials", "4K/8K editing"],
            "professional": ["Marketing campaigns", "Brand assets"],
            "typography": ["Text-heavy edits", "Typography generation"],
            "portrait_retouching": ["Portrait edits", "Beauty retouching"],
            "fashion_edit": ["Fashion photography", "Outfit changes"],
            "product_edit": ["E-commerce", "Product photography"],
        }
        
        capabilities = model_info.get("capabilities", [])
        use_cases = []
        for cap in capabilities:
            if cap in use_cases_map:
                use_cases.extend(use_cases_map[cap])
        
        # Remove duplicates
        return list(set(use_cases)) if use_cases else ["General image editing"]
    
    def _get_features_for_model(self, model_info: Dict[str, Any]) -> list:
        """Get feature list for a model."""
        features = []
        
        if model_info.get("supports_multi_image"):
            max_images = model_info.get("api_params", {}).get("max_images", 0)
            if max_images:
                features.append(f"Multi-image ({max_images} images)")
            else:
                features.append("Multi-image support")
        
        if model_info.get("supports_controlnet"):
            features.append("ControlNet support")
        
        languages = model_info.get("languages", [])
        if len(languages) > 1:
            features.append(f"Multilingual ({', '.join(languages)})")
        elif "multilingual" in languages:
            features.append("Multilingual support")
        
        max_res = model_info.get("max_resolution", (2048, 2048))
        if max(max_res) >= 4096:
            features.append("4K/8K support")
        elif max(max_res) >= 2048:
            features.append("2K support")
        
        api_params = model_info.get("api_params", {})
        if api_params.get("supports_guidance_scale"):
            features.append("Guidance scale control")
        
        return features if features else ["Standard editing"]

    async def process_edit(
        self,
        request: EditStudioRequest,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Process edit request and return normalized response."""

        # Pre-flight validation: Use specific validator for editing operations
        # Note: Editing uses validate_image_editing_operations (different from generation)
        # This is intentional as editing may have different subscription limits
        if user_id:
            from services.database import get_db
            from services.subscription import PricingService
            from services.subscription.preflight_validator import validate_image_editing_operations
            from fastapi import HTTPException

            db = next(get_db())
            try:
                pricing_service = PricingService(db)
                logger.info(f"[Edit Studio] 🛂 Running pre-flight validation for user {user_id}")
                validate_image_editing_operations(
                    pricing_service=pricing_service,
                    user_id=user_id,
                )
                logger.info("[Edit Studio] ✅ Pre-flight validation passed")
            except HTTPException:
                logger.error("[Edit Studio] ❌ Pre-flight validation failed")
                raise
            finally:
                db.close()
        else:
            logger.warning("[Edit Studio] ⚠️ No user_id provided - skipping pre-flight validation")

        image_bytes = self._decode_base64_image(request.image_base64)
        if not image_bytes:
            raise ValueError("Primary image payload is required")

        mask_bytes = self._decode_base64_image(request.mask_base64)
        background_bytes = self._decode_base64_image(request.background_image_base64)
        lighting_bytes = self._decode_base64_image(request.lighting_image_base64)

        operation = request.operation
        logger.info("[Edit Studio] Processing operation='%s' for user=%s", operation, user_id)

        if operation not in self.SUPPORTED_OPERATIONS:
            raise ValueError(f"Unsupported edit operation: {operation}")

        if operation in {"remove_background", "inpaint", "outpaint", "search_replace", "search_recolor", "relight"}:
            image_bytes = await self._handle_stability_edit(
                operation=operation,
                request=request,
                image_bytes=image_bytes,
                mask_bytes=mask_bytes,
                background_bytes=background_bytes,
                lighting_bytes=lighting_bytes,
            )
        else:
            image_bytes = await self._handle_general_edit(
                request=request,
                image_bytes=image_bytes,
                mask_bytes=mask_bytes,
                user_id=user_id,
            )

        metadata = self._image_bytes_to_metadata(image_bytes)
        metadata.update(
            {
                "operation": operation,
                "style_preset": request.style_preset,
                "provider": self.SUPPORTED_OPERATIONS[operation]["provider"],
            }
        )

        response = {
            "success": True,
            "operation": operation,
            "provider": metadata["provider"],
            "image_base64": self._bytes_to_base64(image_bytes, request.output_format),
            "width": metadata["width"],
            "height": metadata["height"],
            "metadata": metadata,
        }

        logger.info("[Edit Studio] ✅ Operation '%s' completed", operation)
        return response

    async def _handle_stability_edit(
        self,
        operation: EditOperationType,
        request: EditStudioRequest,
        image_bytes: bytes,
        mask_bytes: Optional[bytes],
        background_bytes: Optional[bytes],
        lighting_bytes: Optional[bytes],
    ) -> bytes:
        """Execute Stability AI edit workflows."""
        stability_service = StabilityAIService()

        async with stability_service:
            if operation == "remove_background":
                result = await stability_service.remove_background(
                    image=image_bytes,
                    output_format=request.output_format,
                )
            elif operation == "inpaint":
                if not request.prompt:
                    raise ValueError("Prompt is required for inpainting")
                result = await stability_service.inpaint(
                    image=image_bytes,
                    prompt=request.prompt,
                    mask=mask_bytes,
                    negative_prompt=request.negative_prompt,
                    output_format=request.output_format,
                    style_preset=request.style_preset,
                    grow_mask=request.options.get("grow_mask", 5),
                )
            elif operation == "outpaint":
                result = await stability_service.outpaint(
                    image=image_bytes,
                    prompt=request.prompt,
                    negative_prompt=request.negative_prompt,
                    output_format=request.output_format,
                    left=request.expand_left or 0,
                    right=request.expand_right or 0,
                    up=request.expand_up or 0,
                    down=request.expand_down or 0,
                    style_preset=request.style_preset,
                )
            elif operation == "search_replace":
                if not (request.prompt and request.search_prompt):
                    raise ValueError("Both prompt and search_prompt are required for search & replace")
                result = await stability_service.search_and_replace(
                    image=image_bytes,
                    prompt=request.prompt,
                    search_prompt=request.search_prompt,
                    mask=mask_bytes,  # Optional mask for precise region selection
                    output_format=request.output_format,
                )
            elif operation == "search_recolor":
                if not (request.prompt and request.select_prompt):
                    raise ValueError("Both prompt and select_prompt are required for search & recolor")
                result = await stability_service.search_and_recolor(
                    image=image_bytes,
                    prompt=request.prompt,
                    select_prompt=request.select_prompt,
                    mask=mask_bytes,  # Optional mask for precise region selection
                    output_format=request.output_format,
                )
            elif operation == "relight":
                if not background_bytes and not lighting_bytes:
                    raise ValueError("At least one reference (background or lighting) is required for relight")
                result = await stability_service.replace_background_and_relight(
                    subject_image=image_bytes,
                    background_reference=background_bytes,
                    light_reference=lighting_bytes,
                    output_format=request.output_format,
                )
                if isinstance(result, dict) and result.get("id"):
                    result = await self._poll_stability_result(
                        stability_service,
                        generation_id=result["id"],
                        output_format=request.output_format,
                    )
            else:
                raise ValueError(f"Unsupported Stability operation: {operation}")

        return self._extract_image_bytes(result)

    async def _handle_general_edit(
        self,
        request: EditStudioRequest,
        image_bytes: bytes,
        mask_bytes: Optional[bytes],
        user_id: Optional[str],
    ) -> bytes:
        """Execute general editing - routes to WaveSpeed (unified entry) or HuggingFace (legacy).
        
        If model is a WaveSpeed model (qwen-edit-plus, nano-banana-pro-edit-ultra, seedream-v4.5-edit),
        uses unified entry point. Otherwise falls back to HuggingFace for backward compatibility.
        """
        if not request.prompt:
            raise ValueError("Prompt is required for general edits")

        # Check if model is a WaveSpeed editing model
        from services.llm_providers.image_generation.wavespeed_edit_provider import WaveSpeedEditProvider
        provider = WaveSpeedEditProvider()
        wavespeed_models = set(provider.get_available_models().keys())
        
        # Also check if provider is explicitly set to "wavespeed"
        is_wavespeed = (
            request.provider == "wavespeed" or
            (request.model and request.model in wavespeed_models)
        )
        
        # Auto-detect: If no model specified and operation is general_edit, recommend one
        if not request.model and not is_wavespeed and request.operation == "general_edit":
            # Auto-select recommended model
            try:
                # Get image dimensions for recommendation
                with Image.open(io.BytesIO(image_bytes)) as img:
                    image_resolution = {"width": img.width, "height": img.height}
                
                recommendation = self.recommend_model(
                    operation=request.operation,
                    image_resolution=image_resolution,
                    preferences={"prioritize_cost": True},  # Default to cost-optimized
                )
                recommended_model = recommendation.get("recommended_model")
                if recommended_model and recommended_model in wavespeed_models:
                    logger.info(f"[Edit Studio] Auto-selected model: {recommended_model} (reason: {recommendation.get('reason')})")
                    request.model = recommended_model
                    is_wavespeed = True
            except Exception as e:
                logger.warning(f"[Edit Studio] Auto-detection failed: {e}, falling back to HuggingFace")
        
        if is_wavespeed:
            # Use unified entry point for WaveSpeed models
            logger.info(f"[Edit Studio] Using WaveSpeed unified entry for model={request.model}")
            
            # Convert image bytes to base64
            import base64
            image_base64 = base64.b64encode(image_bytes).decode("utf-8")
            
            # Prepare options for unified entry point
            edit_options = {
                "mask_base64": None,
                "negative_prompt": request.negative_prompt,
                "width": None,  # Will be determined from image if needed
                "height": None,
                "guidance_scale": request.guidance_scale,
                "steps": request.steps,
                "seed": request.seed,
            }
            
            # Add mask if provided
            if mask_bytes:
                edit_options["mask_base64"] = base64.b64encode(mask_bytes).decode("utf-8")
            
            # Extract dimensions from image if needed
            with Image.open(io.BytesIO(image_bytes)) as img:
                edit_options["width"] = img.width
                edit_options["height"] = img.height
            
            # Call unified entry point (synchronous, so run in thread)
            result = await asyncio.to_thread(
                generate_image_edit,
                image_base64=image_base64,
                prompt=request.prompt,
                operation=request.operation or "general_edit",
                model=request.model,  # Will auto-select if None
                options=edit_options,
                user_id=user_id,
            )
            
            return result.image_bytes
        else:
            # Fall back to HuggingFace for backward compatibility
            logger.info("[Edit Studio] Using HuggingFace (legacy) for general edit")
            
            options = {
                "provider": request.provider or "huggingface",
                "model": request.model,
                "guidance_scale": request.guidance_scale,
                "steps": request.steps,
                "seed": request.seed,
            }

            # huggingface edit is synchronous - run in thread
            result = await asyncio.to_thread(
                huggingface_edit_image,
                image_bytes,
                request.prompt,
                options,
                user_id,
                mask_bytes,  # Optional mask for selective editing
            )

            return result.image_bytes

    @staticmethod
    def _extract_image_bytes(result: Any) -> bytes:
        """Normalize Stability responses into raw image bytes."""
        if isinstance(result, bytes):
            return result

        if isinstance(result, dict):
            artifacts = result.get("artifacts") or result.get("data") or result.get("images") or []
            for artifact in artifacts:
                if isinstance(artifact, dict):
                    if artifact.get("base64"):
                        return base64.b64decode(artifact["base64"])
                    if artifact.get("b64_json"):
                        return base64.b64decode(artifact["b64_json"])

        raise RuntimeError("Unable to extract image bytes from provider response")

    async def _poll_stability_result(
        self,
        stability_service: StabilityAIService,
        generation_id: str,
        output_format: str,
        timeout_seconds: int = 240,
        interval_seconds: float = 2.0,
    ) -> bytes:
        """Poll Stability async endpoint until result is ready."""
        elapsed = 0.0
        while elapsed < timeout_seconds:
            result = await stability_service.get_generation_result(
                generation_id=generation_id,
                accept_type="*/*",
            )

            if isinstance(result, bytes):
                return result

            if isinstance(result, dict):
                state = (result.get("state") or result.get("status") or "").lower()
                if state in {"succeeded", "success", "ready", "completed"}:
                    return self._extract_image_bytes(result)
                if state in {"failed", "error"}:
                    raise RuntimeError(f"Stability generation failed: {result}")

            await asyncio.sleep(interval_seconds)
            elapsed += interval_seconds

        raise RuntimeError("Timed out waiting for Stability generation result")


