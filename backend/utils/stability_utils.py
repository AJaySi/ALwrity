"""Utility functions for Stability AI operations."""

import base64
import io
import json
import mimetypes
import os
from typing import Dict, Any, Optional, List, Union, Tuple
from PIL import Image, ImageStat
import numpy as np
from fastapi import UploadFile, HTTPException
import aiofiles
import asyncio
from datetime import datetime
import hashlib


class ImageValidator:
    """Validator for image files and parameters."""
    
    @staticmethod
    def validate_image_file(file: UploadFile) -> Dict[str, Any]:
        """Validate uploaded image file.
        
        Args:
            file: Uploaded file
            
        Returns:
            Validation result with file info
        """
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Check file extension
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.webp']
        if file.filename:
            ext = '.' + file.filename.split('.')[-1].lower()
            if ext not in allowed_extensions:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Unsupported file format. Allowed: {allowed_extensions}"
                )
        
        return {
            "filename": file.filename,
            "content_type": file.content_type,
            "is_valid": True
        }
    
    @staticmethod
    async def analyze_image_content(content: bytes) -> Dict[str, Any]:
        """Analyze image content and characteristics.
        
        Args:
            content: Image bytes
            
        Returns:
            Image analysis results
        """
        try:
            img = Image.open(io.BytesIO(content))
            
            # Basic info
            info = {
                "format": img.format,
                "mode": img.mode,
                "size": img.size,
                "width": img.width,
                "height": img.height,
                "total_pixels": img.width * img.height,
                "aspect_ratio": round(img.width / img.height, 3),
                "file_size": len(content),
                "has_alpha": img.mode in ("RGBA", "LA") or "transparency" in img.info
            }
            
            # Color analysis
            if img.mode == "RGB" or img.mode == "RGBA":
                img_rgb = img.convert("RGB")
                stat = ImageStat.Stat(img_rgb)
                
                info.update({
                    "brightness": round(sum(stat.mean) / 3, 2),
                    "color_variance": round(sum(stat.stddev) / 3, 2),
                    "dominant_colors": _extract_dominant_colors(img_rgb)
                })
            
            # Quality assessment
            info["quality_assessment"] = _assess_image_quality(img)
            
            return info
            
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error analyzing image: {str(e)}")
    
    @staticmethod
    def validate_dimensions(width: int, height: int, operation: str) -> None:
        """Validate image dimensions for specific operation.
        
        Args:
            width: Image width
            height: Image height
            operation: Operation type
        """
        from config.stability_config import IMAGE_LIMITS
        
        limits = IMAGE_LIMITS.get(operation, IMAGE_LIMITS["generate"])
        total_pixels = width * height
        
        if "min_pixels" in limits and total_pixels < limits["min_pixels"]:
            raise HTTPException(
                status_code=400,
                detail=f"Image must have at least {limits['min_pixels']} pixels for {operation}"
            )
        
        if "max_pixels" in limits and total_pixels > limits["max_pixels"]:
            raise HTTPException(
                status_code=400,
                detail=f"Image must have at most {limits['max_pixels']} pixels for {operation}"
            )
        
        if "min_dimension" in limits:
            min_dim = limits["min_dimension"]
            if width < min_dim or height < min_dim:
                raise HTTPException(
                    status_code=400,
                    detail=f"Both dimensions must be at least {min_dim} pixels for {operation}"
                )


class AudioValidator:
    """Validator for audio files and parameters."""
    
    @staticmethod
    def validate_audio_file(file: UploadFile) -> Dict[str, Any]:
        """Validate uploaded audio file.
        
        Args:
            file: Uploaded file
            
        Returns:
            Validation result with file info
        """
        if not file.content_type or not file.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="File must be an audio file")
        
        # Check file extension
        allowed_extensions = ['.mp3', '.wav']
        if file.filename:
            ext = '.' + file.filename.split('.')[-1].lower()
            if ext not in allowed_extensions:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Unsupported audio format. Allowed: {allowed_extensions}"
                )
        
        return {
            "filename": file.filename,
            "content_type": file.content_type,
            "is_valid": True
        }
    
    @staticmethod
    async def analyze_audio_content(content: bytes) -> Dict[str, Any]:
        """Analyze audio content and characteristics.
        
        Args:
            content: Audio bytes
            
        Returns:
            Audio analysis results
        """
        try:
            # Basic info
            info = {
                "file_size": len(content),
                "format": "unknown"  # Would need audio library to detect
            }
            
            # For actual implementation, you'd use libraries like librosa or pydub
            # to analyze audio characteristics like duration, sample rate, etc.
            
            return info
            
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error analyzing audio: {str(e)}")


class PromptOptimizer:
    """Optimizer for text prompts."""
    
    @staticmethod
    def analyze_prompt(prompt: str) -> Dict[str, Any]:
        """Analyze prompt structure and content.
        
        Args:
            prompt: Text prompt
            
        Returns:
            Prompt analysis
        """
        words = prompt.split()
        
        analysis = {
            "length": len(prompt),
            "word_count": len(words),
            "sentence_count": len([s for s in prompt.split('.') if s.strip()]),
            "has_style_descriptors": _has_style_descriptors(prompt),
            "has_quality_terms": _has_quality_terms(prompt),
            "has_technical_terms": _has_technical_terms(prompt),
            "complexity_score": _calculate_complexity_score(prompt)
        }
        
        return analysis
    
    @staticmethod
    def optimize_prompt(
        prompt: str, 
        target_model: str = "ultra",
        target_style: Optional[str] = None,
        quality_level: str = "high"
    ) -> Dict[str, Any]:
        """Optimize prompt for better results.
        
        Args:
            prompt: Original prompt
            target_model: Target model
            target_style: Target style
            quality_level: Desired quality level
            
        Returns:
            Optimization results
        """
        optimizations = []
        optimized_prompt = prompt.strip()
        
        # Add style if not present
        if target_style and not _has_style_descriptors(prompt):
            optimized_prompt += f", {target_style} style"
            optimizations.append(f"Added style: {target_style}")
        
        # Add quality terms if needed
        if quality_level == "high" and not _has_quality_terms(prompt):
            optimized_prompt += ", high quality, detailed, sharp"
            optimizations.append("Added quality enhancers")
        
        # Model-specific optimizations
        if target_model == "ultra":
            if len(prompt.split()) < 10:
                optimized_prompt += ", professional photography, detailed composition"
                optimizations.append("Added detail for Ultra model")
        elif target_model == "core":
            # Keep concise for Core model
            if len(prompt.split()) > 30:
                optimizations.append("Consider shortening prompt for Core model")
        
        return {
            "original_prompt": prompt,
            "optimized_prompt": optimized_prompt,
            "optimizations_applied": optimizations,
            "improvement_estimate": len(optimizations) * 15  # Rough percentage
        }
    
    @staticmethod
    def generate_negative_prompt(
        prompt: str, 
        style: Optional[str] = None
    ) -> str:
        """Generate appropriate negative prompt.
        
        Args:
            prompt: Original prompt
            style: Target style
            
        Returns:
            Suggested negative prompt
        """
        base_negative = "blurry, low quality, distorted, deformed, pixelated"
        
        # Add style-specific negatives
        if style:
            if "photographic" in style.lower():
                base_negative += ", cartoon, anime, illustration"
            elif "anime" in style.lower():
                base_negative += ", realistic, photographic"
            elif "art" in style.lower():
                base_negative += ", photograph, realistic"
        
        # Add content-specific negatives based on prompt
        if "person" in prompt.lower() or "human" in prompt.lower():
            base_negative += ", extra limbs, malformed hands, duplicate"
        
        return base_negative


class FileManager:
    """Manager for file operations and caching."""
    
    @staticmethod
    async def save_result(
        content: bytes, 
        filename: str, 
        operation: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Save generation result to file.
        
        Args:
            content: File content
            filename: Filename
            operation: Operation type
            metadata: Optional metadata
            
        Returns:
            File path
        """
        # Create directory structure
        base_dir = "generated_content"
        operation_dir = os.path.join(base_dir, operation)
        date_dir = os.path.join(operation_dir, datetime.now().strftime("%Y/%m/%d"))
        
        os.makedirs(date_dir, exist_ok=True)
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%H%M%S")
        file_hash = hashlib.md5(content).hexdigest()[:8]
        unique_filename = f"{timestamp}_{file_hash}_{filename}"
        
        file_path = os.path.join(date_dir, unique_filename)
        
        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)
        
        # Save metadata if provided
        if metadata:
            metadata_path = file_path + ".json"
            async with aiofiles.open(metadata_path, 'w') as f:
                await f.write(json.dumps(metadata, indent=2))
        
        return file_path
    
    @staticmethod
    def generate_cache_key(operation: str, parameters: Dict[str, Any]) -> str:
        """Generate cache key for operation and parameters.
        
        Args:
            operation: Operation type
            parameters: Operation parameters
            
        Returns:
            Cache key
        """
        # Create deterministic hash from operation and parameters
        key_data = f"{operation}:{json.dumps(parameters, sort_keys=True)}"
        return hashlib.sha256(key_data.encode()).hexdigest()


class ResponseFormatter:
    """Formatter for API responses."""
    
    @staticmethod
    def format_image_response(
        content: bytes, 
        output_format: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Format image response with metadata.
        
        Args:
            content: Image content
            output_format: Output format
            metadata: Optional metadata
            
        Returns:
            Formatted response
        """
        response = {
            "image": base64.b64encode(content).decode(),
            "format": output_format,
            "size": len(content),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if metadata:
            response["metadata"] = metadata
        
        return response
    
    @staticmethod
    def format_audio_response(
        content: bytes, 
        output_format: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Format audio response with metadata.
        
        Args:
            content: Audio content
            output_format: Output format
            metadata: Optional metadata
            
        Returns:
            Formatted response
        """
        response = {
            "audio": base64.b64encode(content).decode(),
            "format": output_format,
            "size": len(content),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if metadata:
            response["metadata"] = metadata
        
        return response
    
    @staticmethod
    def format_3d_response(
        content: bytes,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Format 3D model response with metadata.
        
        Args:
            content: 3D model content (GLB)
            metadata: Optional metadata
            
        Returns:
            Formatted response
        """
        response = {
            "model": base64.b64encode(content).decode(),
            "format": "glb",
            "size": len(content),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if metadata:
            response["metadata"] = metadata
        
        return response


class ParameterValidator:
    """Validator for operation parameters."""
    
    @staticmethod
    def validate_seed(seed: Optional[int]) -> int:
        """Validate and normalize seed parameter.
        
        Args:
            seed: Seed value
            
        Returns:
            Valid seed value
        """
        if seed is None:
            return 0
        
        if not isinstance(seed, int) or seed < 0 or seed > 4294967294:
            raise HTTPException(
                status_code=400,
                detail="Seed must be an integer between 0 and 4294967294"
            )
        
        return seed
    
    @staticmethod
    def validate_strength(strength: Optional[float], operation: str) -> Optional[float]:
        """Validate strength parameter for different operations.
        
        Args:
            strength: Strength value
            operation: Operation type
            
        Returns:
            Valid strength value
        """
        if strength is None:
            return None
        
        if not isinstance(strength, (int, float)) or strength < 0 or strength > 1:
            raise HTTPException(
                status_code=400,
                detail="Strength must be a float between 0 and 1"
            )
        
        # Operation-specific validation
        if operation == "audio_to_audio" and strength < 0.01:
            raise HTTPException(
                status_code=400,
                detail="Minimum strength for audio-to-audio is 0.01"
            )
        
        return float(strength)
    
    @staticmethod
    def validate_creativity(creativity: Optional[float], operation: str) -> Optional[float]:
        """Validate creativity parameter.
        
        Args:
            creativity: Creativity value
            operation: Operation type
            
        Returns:
            Valid creativity value
        """
        if creativity is None:
            return None
        
        # Different operations have different creativity ranges
        ranges = {
            "upscale": (0.1, 0.5),
            "outpaint": (0, 1),
            "conservative_upscale": (0.2, 0.5)
        }
        
        min_val, max_val = ranges.get(operation, (0, 1))
        
        if not isinstance(creativity, (int, float)) or creativity < min_val or creativity > max_val:
            raise HTTPException(
                status_code=400,
                detail=f"Creativity for {operation} must be between {min_val} and {max_val}"
            )
        
        return float(creativity)


class WorkflowManager:
    """Manager for complex workflows and pipelines."""
    
    @staticmethod
    def validate_workflow(workflow: List[Dict[str, Any]]) -> List[str]:
        """Validate workflow steps.
        
        Args:
            workflow: List of workflow steps
            
        Returns:
            List of validation errors
        """
        errors = []
        supported_operations = [
            "generate_ultra", "generate_core", "generate_sd3",
            "upscale_fast", "upscale_conservative", "upscale_creative",
            "inpaint", "outpaint", "erase", "search_and_replace",
            "control_sketch", "control_structure", "control_style"
        ]
        
        for i, step in enumerate(workflow):
            if "operation" not in step:
                errors.append(f"Step {i+1}: Missing 'operation' field")
                continue
            
            operation = step["operation"]
            if operation not in supported_operations:
                errors.append(f"Step {i+1}: Unsupported operation '{operation}'")
            
            # Validate step dependencies
            if i > 0 and operation.startswith("generate_") and i > 0:
                errors.append(f"Step {i+1}: Generate operations should be first in workflow")
        
        return errors
    
    @staticmethod
    def optimize_workflow(workflow: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Optimize workflow for better performance.
        
        Args:
            workflow: Original workflow
            
        Returns:
            Optimized workflow
        """
        optimized = workflow.copy()
        
        # Remove redundant operations
        operations_seen = set()
        filtered_workflow = []
        
        for step in optimized:
            operation = step["operation"]
            if operation not in operations_seen or operation.startswith("generate_"):
                filtered_workflow.append(step)
                operations_seen.add(operation)
        
        # Reorder for optimal execution
        # Generation operations first, then modifications, then upscaling
        order_priority = {
            "generate": 0,
            "control": 1,
            "edit": 2,
            "upscale": 3
        }
        
        def get_priority(step):
            operation = step["operation"]
            for key, priority in order_priority.items():
                if operation.startswith(key):
                    return priority
            return 999
        
        filtered_workflow.sort(key=get_priority)
        
        return filtered_workflow


# ==================== HELPER FUNCTIONS ====================

def _extract_dominant_colors(img: Image.Image, num_colors: int = 5) -> List[Tuple[int, int, int]]:
    """Extract dominant colors from image.
    
    Args:
        img: PIL Image
        num_colors: Number of dominant colors to extract
        
    Returns:
        List of RGB tuples
    """
    # Resize image for faster processing
    img_small = img.resize((150, 150))
    
    # Convert to numpy array
    img_array = np.array(img_small)
    pixels = img_array.reshape(-1, 3)
    
    # Use k-means clustering to find dominant colors
    from sklearn.cluster import KMeans
    
    kmeans = KMeans(n_clusters=num_colors, random_state=42, n_init=10)
    kmeans.fit(pixels)
    
    colors = kmeans.cluster_centers_.astype(int)
    return [tuple(color) for color in colors]


def _assess_image_quality(img: Image.Image) -> Dict[str, Any]:
    """Assess image quality metrics.
    
    Args:
        img: PIL Image
        
    Returns:
        Quality assessment
    """
    # Convert to grayscale for quality analysis
    gray = img.convert('L')
    gray_array = np.array(gray)
    
    # Calculate sharpness using Laplacian variance
    laplacian_var = np.var(np.gradient(gray_array))
    sharpness_score = min(100, laplacian_var / 100)
    
    # Calculate noise level
    noise_level = np.std(gray_array)
    
    # Overall quality score
    overall_score = (sharpness_score + max(0, 100 - noise_level)) / 2
    
    return {
        "sharpness_score": round(sharpness_score, 2),
        "noise_level": round(noise_level, 2),
        "overall_score": round(overall_score, 2),
        "needs_enhancement": overall_score < 70
    }


def _has_style_descriptors(prompt: str) -> bool:
    """Check if prompt contains style descriptors."""
    style_keywords = [
        "photorealistic", "realistic", "anime", "cartoon", "digital art",
        "oil painting", "watercolor", "sketch", "illustration", "3d render",
        "cinematic", "artistic", "professional"
    ]
    return any(keyword in prompt.lower() for keyword in style_keywords)


def _has_quality_terms(prompt: str) -> bool:
    """Check if prompt contains quality terms."""
    quality_keywords = [
        "high quality", "detailed", "sharp", "crisp", "clear",
        "professional", "masterpiece", "award winning"
    ]
    return any(keyword in prompt.lower() for keyword in quality_keywords)


def _has_technical_terms(prompt: str) -> bool:
    """Check if prompt contains technical photography terms."""
    technical_keywords = [
        "bokeh", "depth of field", "macro", "wide angle", "telephoto",
        "iso", "aperture", "shutter speed", "lighting", "composition"
    ]
    return any(keyword in prompt.lower() for keyword in technical_keywords)


def _calculate_complexity_score(prompt: str) -> float:
    """Calculate prompt complexity score.
    
    Args:
        prompt: Text prompt
        
    Returns:
        Complexity score (0-100)
    """
    words = prompt.split()
    
    # Base score from word count
    base_score = min(len(words) * 2, 50)
    
    # Add points for descriptive elements
    if _has_style_descriptors(prompt):
        base_score += 15
    if _has_quality_terms(prompt):
        base_score += 10
    if _has_technical_terms(prompt):
        base_score += 15
    
    # Add points for specific details
    if any(word in prompt.lower() for word in ["color", "lighting", "composition"]):
        base_score += 10
    
    return min(base_score, 100)


def create_batch_manifest(
    operation: str,
    files: List[UploadFile],
    parameters: Dict[str, Any]
) -> Dict[str, Any]:
    """Create manifest for batch processing.
    
    Args:
        operation: Operation type
        files: List of files to process
        parameters: Operation parameters
        
    Returns:
        Batch manifest
    """
    return {
        "batch_id": f"batch_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
        "operation": operation,
        "file_count": len(files),
        "files": [{"filename": f.filename, "size": f.size} for f in files],
        "parameters": parameters,
        "created_at": datetime.utcnow().isoformat(),
        "estimated_duration": len(files) * 30,  # 30 seconds per file estimate
        "estimated_cost": len(files) * _get_operation_cost(operation)
    }


def _get_operation_cost(operation: str) -> float:
    """Get estimated cost for operation.
    
    Args:
        operation: Operation type
        
    Returns:
        Estimated cost in credits
    """
    from config.stability_config import MODEL_PRICING
    
    # Map operation to pricing category
    if operation.startswith("generate_"):
        return MODEL_PRICING["generate"].get("core", 3)  # Default to core
    elif operation.startswith("upscale_"):
        upscale_type = operation.replace("upscale_", "")
        return MODEL_PRICING["upscale"].get(upscale_type, 5)
    elif operation.startswith("control_"):
        return MODEL_PRICING["control"].get("sketch", 5)  # Default
    else:
        return 5  # Default cost


def validate_file_size(file: UploadFile, max_size: int = 10 * 1024 * 1024) -> None:
    """Validate file size.
    
    Args:
        file: Uploaded file
        max_size: Maximum allowed size in bytes
    """
    if file.size and file.size > max_size:
        raise HTTPException(
            status_code=413,
            detail=f"File size ({file.size} bytes) exceeds maximum allowed size ({max_size} bytes)"
        )


async def convert_image_format(content: bytes, target_format: str) -> bytes:
    """Convert image to target format.
    
    Args:
        content: Image content
        target_format: Target format (jpeg, png, webp)
        
    Returns:
        Converted image bytes
    """
    try:
        img = Image.open(io.BytesIO(content))
        
        # Convert to RGB if saving as JPEG
        if target_format.lower() == "jpeg" and img.mode in ("RGBA", "LA"):
            img = img.convert("RGB")
        
        output = io.BytesIO()
        img.save(output, format=target_format.upper())
        return output.getvalue()
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error converting image: {str(e)}")


def estimate_processing_time(
    operation: str, 
    file_size: int,
    complexity: Optional[Dict[str, Any]] = None
) -> float:
    """Estimate processing time for operation.
    
    Args:
        operation: Operation type
        file_size: File size in bytes
        complexity: Optional complexity metrics
        
    Returns:
        Estimated time in seconds
    """
    # Base times by operation (in seconds)
    base_times = {
        "generate_ultra": 15,
        "generate_core": 5,
        "generate_sd3": 10,
        "upscale_fast": 2,
        "upscale_conservative": 30,
        "upscale_creative": 60,
        "inpaint": 10,
        "outpaint": 15,
        "control_sketch": 8,
        "control_structure": 8,
        "control_style": 10,
        "3d_fast": 10,
        "3d_point_aware": 20,
        "audio_text": 30,
        "audio_transform": 45
    }
    
    base_time = base_times.get(operation, 10)
    
    # Adjust for file size
    size_factor = max(1, file_size / (1024 * 1024))  # Size in MB
    adjusted_time = base_time * size_factor
    
    # Adjust for complexity if provided
    if complexity and complexity.get("complexity_score", 0) > 80:
        adjusted_time *= 1.5
    
    return round(adjusted_time, 1)