"""
Asset Audit Service
Analyzes uploaded assets and recommends enhancement operations.
"""

from typing import Dict, Any, List, Optional
from loguru import logger
import base64
from io import BytesIO
from PIL import Image


class AssetAuditService:
    """Service to audit assets and recommend enhancements."""
    
    def __init__(self):
        """Initialize Asset Audit Service."""
        self.logger = logger
        logger.info("[Asset Audit] Service initialized")
    
    def audit_asset(
        self,
        image_base64: str,
        asset_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Audit an uploaded asset and recommend enhancement operations.
        
        Args:
            image_base64: Base64 encoded image
            asset_metadata: Optional metadata about the asset
            
        Returns:
            Audit results with recommendations
        """
        try:
            # Decode image
            image_bytes = self._decode_base64(image_base64)
            if not image_bytes:
                raise ValueError("Invalid image data")
            
            # Analyze image
            image = Image.open(BytesIO(image_bytes))
            width, height = image.size
            format_type = image.format or "PNG"
            mode = image.mode
            
            # Basic quality checks
            quality_score = self._assess_quality(image, width, height)
            
            # Generate recommendations
            recommendations = []
            
            # Resolution recommendations
            if width < 1080 or height < 1080:
                recommendations.append({
                    "operation": "upscale",
                    "priority": "high",
                    "reason": f"Image resolution ({width}x{height}) is below recommended 1080p for social media",
                    "suggested_mode": "fast" if width < 512 else "conservative",
                })
            
            # Background recommendations
            if mode == "RGBA" and self._has_transparency(image):
                recommendations.append({
                    "operation": "remove_background",
                    "priority": "low",
                    "reason": "Image already has transparency, background removal may not be needed",
                })
            else:
                recommendations.append({
                    "operation": "remove_background",
                    "priority": "medium",
                    "reason": "Background removal can create versatile product images",
                })
            
            # Enhancement recommendations based on quality
            if quality_score < 0.7:
                recommendations.append({
                    "operation": "enhance",
                    "priority": "high",
                    "reason": f"Image quality score ({quality_score:.2f}) suggests enhancement needed",
                    "suggested_operations": ["upscale", "general_edit"],
                })
            
            # Format recommendations
            if format_type not in ["PNG", "JPEG"]:
                recommendations.append({
                    "operation": "convert",
                    "priority": "low",
                    "reason": f"Format {format_type} may not be optimal for web/social media",
                    "suggested_format": "PNG" if mode == "RGBA" else "JPEG",
                })
            
            audit_result = {
                "asset_info": {
                    "width": width,
                    "height": height,
                    "format": format_type,
                    "mode": mode,
                    "quality_score": quality_score,
                },
                "recommendations": recommendations,
                "status": "usable" if quality_score > 0.6 else "needs_enhancement",
            }
            
            logger.info(f"[Asset Audit] Audited asset: {width}x{height}, quality: {quality_score:.2f}")
            return audit_result
            
        except Exception as e:
            logger.error(f"[Asset Audit] Error auditing asset: {str(e)}")
            return {
                "asset_info": {},
                "recommendations": [],
                "status": "error",
                "error": str(e),
            }
    
    def _decode_base64(self, image_base64: str) -> Optional[bytes]:
        """Decode base64 image data."""
        try:
            if image_base64.startswith("data:"):
                _, b64data = image_base64.split(",", 1)
            else:
                b64data = image_base64
            return base64.b64decode(b64data)
        except Exception as e:
            logger.error(f"[Asset Audit] Error decoding base64: {str(e)}")
            return None
    
    def _has_transparency(self, image: Image.Image) -> bool:
        """Check if image has transparency."""
        if image.mode in ("RGBA", "LA"):
            alpha = image.split()[-1]
            return any(pixel < 255 for pixel in alpha.getdata())
        return False
    
    def _assess_quality(self, image: Image.Image, width: int, height: int) -> float:
        """
        Assess image quality score (0.0 to 1.0).
        
        Simple heuristic based on resolution and format.
        """
        score = 0.5  # Base score
        
        # Resolution scoring
        min_dimension = min(width, height)
        if min_dimension >= 1080:
            score += 0.3
        elif min_dimension >= 512:
            score += 0.2
        elif min_dimension >= 256:
            score += 0.1
        
        # Format scoring
        if image.format in ["PNG", "JPEG"]:
            score += 0.1
        
        # Mode scoring
        if image.mode in ["RGB", "RGBA"]:
            score += 0.1
        
        return min(score, 1.0)
    
    def batch_audit_assets(
        self,
        assets: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Audit multiple assets in batch.
        
        Args:
            assets: List of asset dictionaries with 'image_base64' and optional 'metadata'
            
        Returns:
            Batch audit results
        """
        results = []
        for asset in assets:
            audit_result = self.audit_asset(
                asset.get('image_base64'),
                asset.get('metadata')
            )
            results.append({
                "asset_id": asset.get('id'),
                "audit": audit_result,
            })
        
        # Summary statistics
        total_assets = len(results)
        usable_count = sum(1 for r in results if r["audit"]["status"] == "usable")
        needs_enhancement_count = sum(
            1 for r in results if r["audit"]["status"] == "needs_enhancement"
        )
        
        return {
            "results": results,
            "summary": {
                "total_assets": total_assets,
                "usable": usable_count,
                "needs_enhancement": needs_enhancement_count,
                "error": total_assets - usable_count - needs_enhancement_count,
            },
        }

