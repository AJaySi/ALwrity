"""Face Swap Studio service for AI-powered face swapping."""

from __future__ import annotations

import base64
import io
from dataclasses import dataclass
from typing import Any, Dict, Optional
from PIL import Image

from services.llm_providers.main_image_generation import generate_face_swap
from utils.logger_utils import get_service_logger

logger = get_service_logger("image_studio.face_swap")


@dataclass
class FaceSwapStudioRequest:
    """Request model for face swap operations."""
    base_image_base64: str
    face_image_base64: str
    model: Optional[str] = None
    target_face_index: Optional[int] = None
    target_gender: Optional[str] = None
    options: Optional[Dict[str, Any]] = None


class FaceSwapService:
    """Service for face swap operations."""
    
    def __init__(self):
        pass
    
    def get_available_models(
        self,
        tier: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get available WaveSpeed face swap models.
        
        Args:
            tier: Filter by tier ("budget", "mid", "premium")
            
        Returns:
            Dictionary with models and metadata
        """
        from services.llm_providers.image_generation.wavespeed_face_swap_provider import WaveSpeedFaceSwapProvider
        
        provider = WaveSpeedFaceSwapProvider()
        all_models = provider.get_available_models()
        
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
                "cost": model_info.get("cost", 0.025),
                "tier": model_info.get("tier", "mid"),
                "capabilities": model_info.get("capabilities", []),
                "use_cases": self._get_use_cases_for_model(model_id, model_info),
                "features": model_info.get("features", []),
                "max_faces": model_info.get("max_faces", 1),
            })
        
        return {
            "models": models_list,
            "total": len(models_list),
        }
    
    def recommend_model(
        self,
        base_image_resolution: Optional[Dict[str, int]] = None,
        face_image_resolution: Optional[Dict[str, int]] = None,
        user_tier: Optional[str] = None,
        preferences: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Recommend best model for face swap.
        
        Args:
            base_image_resolution: Dict with "width" and "height" of base image
            face_image_resolution: Dict with "width" and "height" of face image
            user_tier: User subscription tier ("free", "pro", "enterprise")
            preferences: Dict with "prioritize_cost" or "prioritize_quality"
            
        Returns:
            Dictionary with recommended model and alternatives
        """
        from services.llm_providers.image_generation.wavespeed_face_swap_provider import WaveSpeedFaceSwapProvider
        
        provider = WaveSpeedFaceSwapProvider()
        available_models = provider.get_available_models()
        
        if not available_models:
            raise ValueError("No models available")
        
        # Apply preferences
        prioritize_cost = preferences and preferences.get("prioritize_cost", False)
        prioritize_quality = preferences and preferences.get("prioritize_quality", False)
        
        # Score models
        scored_models = []
        for model_id, model_info in available_models.items():
            score = 0
            cost = model_info.get("cost", 0.025)
            tier = model_info.get("tier", "mid")
            
            # Cost scoring (lower is better)
            if prioritize_cost:
                score += (1.0 / cost) * 100
            else:
                score += (1.0 / cost) * 50
            
            # Quality scoring (higher cost = better quality for face swap)
            if prioritize_quality:
                score += cost * 20
            else:
                score += cost * 10
            
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
                "cost": model_info.get("cost", 0.025),
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
            "face_swap": ["Portrait editing", "Fun swaps", "Social media"],
            "head_swap": ["Casting and concept design", "Privacy and anonymization", "Photo exploration"],
            "full_head_replacement": ["Full head replacement", "Hair included", "Casting mockups"],
            "realistic_blending": ["Professional work", "Marketing", "Entertainment"],
            "multi_face": ["Group photos", "Family photos", "Team photos", "Creative projects", "Content creation"],
            "face_enhancement": ["High-quality results", "Professional work", "Marketing campaigns"],
            "identity_preservation": ["Character consistency", "Brand identity"],
        }
        
        capabilities = model_info.get("capabilities", [])
        use_cases = []
        for cap in capabilities:
            if cap in use_cases_map:
                use_cases.extend(use_cases_map[cap])
        
        return list(set(use_cases)) if use_cases else ["General face swapping"]
    
    async def process_face_swap(
        self,
        request: FaceSwapStudioRequest,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Process face swap request.
        
        Args:
            request: Face swap request
            user_id: User ID for tracking
            
        Returns:
            Dictionary with result image and metadata
        """
        # Auto-detect model if not specified
        selected_model = request.model
        if not selected_model:
            try:
                # Get image dimensions for recommendation
                base_img = Image.open(io.BytesIO(base64.b64decode(request.base_image_base64.split(",", 1)[1] if "," in request.base_image_base64 else request.base_image_base64)))
                face_img = Image.open(io.BytesIO(base64.b64decode(request.face_image_base64.split(",", 1)[1] if "," in request.face_image_base64 else request.face_image_base64)))
                
                base_resolution = {"width": base_img.width, "height": base_img.height}
                face_resolution = {"width": face_img.width, "height": face_img.height}
                
                recommendation = self.recommend_model(
                    base_image_resolution=base_resolution,
                    face_image_resolution=face_resolution,
                    preferences={"prioritize_cost": True},
                )
                selected_model = recommendation.get("recommended_model")
                logger.info(f"[Face Swap] Auto-selected model: {selected_model} (reason: {recommendation.get('reason')})")
            except Exception as e:
                logger.warning(f"[Face Swap] Auto-detection failed: {e}, using default model")
                # Use first available model as fallback
                from services.llm_providers.image_generation.wavespeed_face_swap_provider import WaveSpeedFaceSwapProvider
                provider = WaveSpeedFaceSwapProvider()
                all_models = provider.get_available_models()
                if all_models:
                    selected_model = list(all_models.keys())[0]
        
        # Prepare options
        options = request.options or {}
        if request.target_face_index is not None:
            options["target_face_index"] = request.target_face_index
        if request.target_gender:
            options["target_gender"] = request.target_gender
        
        # Call unified entry point
        result = generate_face_swap(
            base_image_base64=request.base_image_base64,
            face_image_base64=request.face_image_base64,
            model=selected_model,
            options=options,
            user_id=user_id,
        )
        
        # Convert result to base64
        result_base64 = base64.b64encode(result.image_bytes).decode("utf-8")
        result_data_url = f"data:image/png;base64,{result_base64}"
        
        return {
            "success": True,
            "image_base64": result_data_url,
            "width": result.width,
            "height": result.height,
            "provider": result.provider,
            "model": result.model,
            "metadata": result.metadata or {},
        }
