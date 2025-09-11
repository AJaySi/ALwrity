"""Advanced Stability AI endpoints with specialized features."""

from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, BackgroundTasks
from fastapi.responses import Response, StreamingResponse
from typing import Optional, List, Dict, Any
import asyncio
import base64
import io
import json
from datetime import datetime, timedelta

from services.stability_service import get_stability_service, StabilityAIService

router = APIRouter(prefix="/api/stability/advanced", tags=["Stability AI Advanced"])


# ==================== ADVANCED GENERATION WORKFLOWS ====================

@router.post("/workflow/image-enhancement", summary="Complete Image Enhancement Workflow")
async def image_enhancement_workflow(
    image: UploadFile = File(..., description="Image to enhance"),
    enhancement_type: str = Form("auto", description="Enhancement type: auto, upscale, denoise, sharpen"),
    prompt: Optional[str] = Form(None, description="Optional prompt for guided enhancement"),
    target_resolution: Optional[str] = Form("4k", description="Target resolution: 4k, 2k, hd"),
    preserve_style: Optional[bool] = Form(True, description="Preserve original style"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    stability_service: StabilityAIService = Depends(get_stability_service)
):
    """Complete image enhancement workflow with automatic optimization.
    
    This workflow automatically determines the best enhancement approach based on
    the input image characteristics and user preferences.
    """
    async with stability_service:
        # Analyze image first
        content = await image.read()
        img_info = await _analyze_image(content)
        
        # Reset file pointer
        await image.seek(0)
        
        # Determine enhancement strategy
        strategy = _determine_enhancement_strategy(img_info, enhancement_type, target_resolution)
        
        # Execute enhancement workflow
        results = []
        
        for step in strategy["steps"]:
            if step["operation"] == "upscale_fast":
                result = await stability_service.upscale_fast(image=image)
            elif step["operation"] == "upscale_conservative":
                result = await stability_service.upscale_conservative(
                    image=image, 
                    prompt=prompt or step["default_prompt"]
                )
            elif step["operation"] == "upscale_creative":
                result = await stability_service.upscale_creative(
                    image=image, 
                    prompt=prompt or step["default_prompt"]
                )
            
            results.append({
                "step": step["name"],
                "operation": step["operation"],
                "status": "completed",
                "result_size": len(result) if isinstance(result, bytes) else None
            })
            
            # Use result as input for next step if needed
            if isinstance(result, bytes) and len(strategy["steps"]) > 1:
                # Convert bytes back to UploadFile-like object for next step
                image = _bytes_to_upload_file(result, image.filename)
        
        # Return final result
        if isinstance(result, bytes):
            return Response(
                content=result, 
                media_type="image/png",
                headers={
                    "X-Enhancement-Strategy": json.dumps(strategy),
                    "X-Processing-Steps": str(len(results))
                }
            )
        
        return {
            "strategy": strategy,
            "steps_completed": results,
            "generation_id": result.get("id") if isinstance(result, dict) else None
        }


@router.post("/workflow/creative-suite", summary="Creative Suite Multi-Step Workflow")
async def creative_suite_workflow(
    base_image: Optional[UploadFile] = File(None, description="Base image (optional for text-to-image)"),
    prompt: str = Form(..., description="Main creative prompt"),
    style_reference: Optional[UploadFile] = File(None, description="Style reference image"),
    workflow_steps: str = Form(..., description="JSON array of workflow steps"),
    output_format: Optional[str] = Form("png", description="Output format"),
    stability_service: StabilityAIService = Depends(get_stability_service)
):
    """Execute a multi-step creative workflow combining various Stability AI services.
    
    This endpoint allows you to chain multiple operations together for complex
    creative workflows.
    """
    try:
        steps = json.loads(workflow_steps)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in workflow_steps")
    
    async with stability_service:
        current_image = base_image
        results = []
        
        for i, step in enumerate(steps):
            operation = step.get("operation")
            params = step.get("parameters", {})
            
            try:
                if operation == "generate_core" and not current_image:
                    result = await stability_service.generate_core(prompt=prompt, **params)
                elif operation == "control_style" and style_reference:
                    result = await stability_service.control_style(
                        image=style_reference, prompt=prompt, **params
                    )
                elif operation == "inpaint" and current_image:
                    result = await stability_service.inpaint(
                        image=current_image, prompt=prompt, **params
                    )
                elif operation == "upscale_fast" and current_image:
                    result = await stability_service.upscale_fast(image=current_image, **params)
                else:
                    raise ValueError(f"Unsupported operation or missing requirements: {operation}")
                
                # Convert result to next step input if needed
                if isinstance(result, bytes):
                    current_image = _bytes_to_upload_file(result, f"step_{i}_output.png")
                
                results.append({
                    "step": i + 1,
                    "operation": operation,
                    "status": "completed",
                    "result_type": "image" if isinstance(result, bytes) else "json"
                })
                
            except Exception as e:
                results.append({
                    "step": i + 1,
                    "operation": operation,
                    "status": "error",
                    "error": str(e)
                })
                break
        
        # Return final result
        if isinstance(result, bytes):
            return Response(
                content=result,
                media_type=f"image/{output_format}",
                headers={"X-Workflow-Steps": json.dumps(results)}
            )
        
        return {"workflow_results": results, "final_result": result}


# ==================== COMPARISON ENDPOINTS ====================

@router.post("/compare/models", summary="Compare Different Models")
async def compare_models(
    prompt: str = Form(..., description="Text prompt for comparison"),
    models: str = Form(..., description="JSON array of models to compare"),
    seed: Optional[int] = Form(42, description="Seed for consistent comparison"),
    stability_service: StabilityAIService = Depends(get_stability_service)
):
    """Generate images using different models for comparison.
    
    This endpoint generates the same prompt using different Stability AI models
    to help you compare quality and style differences.
    """
    try:
        model_list = json.loads(models)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in models")
    
    async with stability_service:
        results = {}
        
        for model in model_list:
            try:
                if model == "ultra":
                    result = await stability_service.generate_ultra(
                        prompt=prompt, seed=seed, output_format="webp"
                    )
                elif model == "core":
                    result = await stability_service.generate_core(
                        prompt=prompt, seed=seed, output_format="webp"
                    )
                elif model.startswith("sd3"):
                    result = await stability_service.generate_sd3(
                        prompt=prompt, model=model, seed=seed, output_format="webp"
                    )
                else:
                    continue
                
                if isinstance(result, bytes):
                    results[model] = {
                        "status": "success",
                        "image": base64.b64encode(result).decode(),
                        "size": len(result)
                    }
                else:
                    results[model] = {"status": "async", "generation_id": result.get("id")}
                    
            except Exception as e:
                results[model] = {"status": "error", "error": str(e)}
        
        return {
            "prompt": prompt,
            "seed": seed,
            "comparison_results": results,
            "timestamp": datetime.utcnow().isoformat()
        }


# ==================== STYLE TRANSFER WORKFLOWS ====================

@router.post("/style/multi-style-transfer", summary="Multi-Style Transfer")
async def multi_style_transfer(
    content_image: UploadFile = File(..., description="Content image"),
    style_images: List[UploadFile] = File(..., description="Multiple style reference images"),
    blend_weights: Optional[str] = Form(None, description="JSON array of blend weights"),
    output_format: Optional[str] = Form("png", description="Output format"),
    stability_service: StabilityAIService = Depends(get_stability_service)
):
    """Apply multiple styles to a single content image with blending.
    
    This endpoint applies multiple style references to a content image,
    optionally with specified blend weights.
    """
    weights = None
    if blend_weights:
        try:
            weights = json.loads(blend_weights)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON in blend_weights")
    
    if weights and len(weights) != len(style_images):
        raise HTTPException(status_code=400, detail="Number of weights must match number of style images")
    
    async with stability_service:
        results = []
        
        for i, style_image in enumerate(style_images):
            weight = weights[i] if weights else 1.0
            
            result = await stability_service.control_style_transfer(
                init_image=content_image,
                style_image=style_image,
                style_strength=weight,
                output_format=output_format
            )
            
            if isinstance(result, bytes):
                results.append({
                    "style_index": i,
                    "weight": weight,
                    "image": base64.b64encode(result).decode(),
                    "size": len(result)
                })
            
            # Reset content image file pointer for next iteration
            await content_image.seek(0)
        
        return {
            "content_image": content_image.filename,
            "style_count": len(style_images),
            "results": results
        }


# ==================== ANIMATION & SEQUENCE ENDPOINTS ====================

@router.post("/animation/image-sequence", summary="Generate Image Sequence")
async def generate_image_sequence(
    base_prompt: str = Form(..., description="Base prompt for sequence"),
    sequence_prompts: str = Form(..., description="JSON array of sequence variations"),
    seed_start: Optional[int] = Form(42, description="Starting seed"),
    seed_increment: Optional[int] = Form(1, description="Seed increment per frame"),
    output_format: Optional[str] = Form("png", description="Output format"),
    stability_service: StabilityAIService = Depends(get_stability_service)
):
    """Generate a sequence of related images for animation or storytelling.
    
    This endpoint generates a series of images with slight variations to create
    animation frames or story sequences.
    """
    try:
        prompts = json.loads(sequence_prompts)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in sequence_prompts")
    
    async with stability_service:
        sequence_results = []
        current_seed = seed_start
        
        for i, variation in enumerate(prompts):
            full_prompt = f"{base_prompt}, {variation}"
            
            result = await stability_service.generate_core(
                prompt=full_prompt,
                seed=current_seed,
                output_format=output_format
            )
            
            if isinstance(result, bytes):
                sequence_results.append({
                    "frame": i + 1,
                    "prompt": full_prompt,
                    "seed": current_seed,
                    "image": base64.b64encode(result).decode(),
                    "size": len(result)
                })
            
            current_seed += seed_increment
        
        return {
            "base_prompt": base_prompt,
            "frame_count": len(sequence_results),
            "sequence": sequence_results
        }


# ==================== QUALITY ANALYSIS ENDPOINTS ====================

@router.post("/analysis/generation-quality", summary="Analyze Generation Quality")
async def analyze_generation_quality(
    image: UploadFile = File(..., description="Generated image to analyze"),
    original_prompt: str = Form(..., description="Original generation prompt"),
    model_used: str = Form(..., description="Model used for generation")
):
    """Analyze the quality and characteristics of a generated image.
    
    This endpoint provides detailed analysis of generated images including
    quality metrics, style adherence, and improvement suggestions.
    """
    from PIL import Image, ImageStat
    import numpy as np
    
    try:
        content = await image.read()
        img = Image.open(io.BytesIO(content))
        
        # Basic image statistics
        stat = ImageStat.Stat(img)
        
        # Convert to RGB if needed for analysis
        if img.mode != "RGB":
            img = img.convert("RGB")
        
        # Calculate quality metrics
        img_array = np.array(img)
        
        # Brightness analysis
        brightness = np.mean(img_array)
        
        # Contrast analysis
        contrast = np.std(img_array)
        
        # Color distribution
        color_channels = np.mean(img_array, axis=(0, 1))
        
        # Sharpness estimation (using Laplacian variance)
        gray = img.convert('L')
        gray_array = np.array(gray)
        laplacian_var = np.var(np.gradient(gray_array))
        
        quality_score = min(100, (contrast / 50) * (laplacian_var / 1000) * 100)
        
        analysis = {
            "image_info": {
                "dimensions": f"{img.width}x{img.height}",
                "format": img.format,
                "mode": img.mode,
                "file_size": len(content)
            },
            "quality_metrics": {
                "overall_score": round(quality_score, 2),
                "brightness": round(brightness, 2),
                "contrast": round(contrast, 2),
                "sharpness": round(laplacian_var, 2)
            },
            "color_analysis": {
                "red_channel": round(float(color_channels[0]), 2),
                "green_channel": round(float(color_channels[1]), 2),
                "blue_channel": round(float(color_channels[2]), 2),
                "color_balance": "balanced" if max(color_channels) - min(color_channels) < 30 else "imbalanced"
            },
            "generation_info": {
                "original_prompt": original_prompt,
                "model_used": model_used,
                "analysis_timestamp": datetime.utcnow().isoformat()
            },
            "recommendations": _generate_quality_recommendations(quality_score, brightness, contrast)
        }
        
        return analysis
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error analyzing image: {str(e)}")


@router.post("/analysis/prompt-optimization", summary="Optimize Text Prompts")
async def optimize_prompt(
    prompt: str = Form(..., description="Original prompt to optimize"),
    target_style: Optional[str] = Form(None, description="Target style"),
    target_quality: Optional[str] = Form("high", description="Target quality level"),
    model: Optional[str] = Form("ultra", description="Target model"),
    include_negative: Optional[bool] = Form(True, description="Include negative prompt suggestions")
):
    """Analyze and optimize text prompts for better generation results.
    
    This endpoint analyzes your prompt and provides suggestions for improvement
    based on best practices and model-specific optimizations.
    """
    analysis = {
        "original_prompt": prompt,
        "prompt_length": len(prompt),
        "word_count": len(prompt.split()),
        "optimization_suggestions": []
    }
    
    # Analyze prompt structure
    suggestions = []
    
    # Check for style descriptors
    style_keywords = ["photorealistic", "digital art", "oil painting", "watercolor", "sketch"]
    has_style = any(keyword in prompt.lower() for keyword in style_keywords)
    if not has_style and target_style:
        suggestions.append(f"Add style descriptor: {target_style}")
    
    # Check for quality enhancers
    quality_keywords = ["high quality", "detailed", "sharp", "crisp", "professional"]
    has_quality = any(keyword in prompt.lower() for keyword in quality_keywords)
    if not has_quality and target_quality == "high":
        suggestions.append("Add quality enhancers: 'high quality, detailed, sharp'")
    
    # Check for composition elements
    composition_keywords = ["composition", "lighting", "perspective", "framing"]
    has_composition = any(keyword in prompt.lower() for keyword in composition_keywords)
    if not has_composition:
        suggestions.append("Consider adding composition details: lighting, perspective, framing")
    
    # Model-specific optimizations
    if model == "ultra":
        suggestions.append("For Ultra model: Use detailed, specific descriptions")
    elif model == "core":
        suggestions.append("For Core model: Keep prompts concise but descriptive")
    
    # Generate optimized prompt
    optimized_prompt = prompt
    if suggestions:
        optimized_prompt = _apply_prompt_optimizations(prompt, suggestions, target_style)
    
    # Generate negative prompt suggestions
    negative_suggestions = []
    if include_negative:
        negative_suggestions = _generate_negative_prompt_suggestions(prompt, target_style)
    
    analysis.update({
        "optimization_suggestions": suggestions,
        "optimized_prompt": optimized_prompt,
        "negative_prompt_suggestions": negative_suggestions,
        "estimated_improvement": len(suggestions) * 10,  # Rough estimate
        "model_compatibility": _check_model_compatibility(optimized_prompt, model)
    })
    
    return analysis


# ==================== BATCH PROCESSING ENDPOINTS ====================

@router.post("/batch/process-folder", summary="Process Multiple Images")
async def batch_process_folder(
    images: List[UploadFile] = File(..., description="Multiple images to process"),
    operation: str = Form(..., description="Operation to perform on all images"),
    operation_params: str = Form("{}", description="JSON parameters for operation"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    stability_service: StabilityAIService = Depends(get_stability_service)
):
    """Process multiple images with the same operation in batch.
    
    This endpoint allows you to apply the same operation to multiple images
    efficiently.
    """
    try:
        params = json.loads(operation_params)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in operation_params")
    
    # Validate operation
    supported_operations = [
        "upscale_fast", "remove_background", "erase", "generate_ultra", "generate_core"
    ]
    if operation not in supported_operations:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported operation. Supported: {supported_operations}"
        )
    
    # Start batch processing in background
    batch_id = f"batch_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    
    background_tasks.add_task(
        _process_batch_images,
        batch_id,
        images,
        operation,
        params,
        stability_service
    )
    
    return {
        "batch_id": batch_id,
        "status": "started",
        "image_count": len(images),
        "operation": operation,
        "estimated_completion": (datetime.utcnow() + timedelta(minutes=len(images) * 2)).isoformat()
    }


@router.get("/batch/{batch_id}/status", summary="Get Batch Processing Status")
async def get_batch_status(batch_id: str):
    """Get the status of a batch processing operation.
    
    Returns the current status and progress of a batch operation.
    """
    # In a real implementation, you'd store batch status in a database
    # For now, return a mock response
    return {
        "batch_id": batch_id,
        "status": "processing",
        "progress": {
            "completed": 2,
            "total": 5,
            "percentage": 40
        },
        "estimated_completion": (datetime.utcnow() + timedelta(minutes=5)).isoformat()
    }


# ==================== HELPER FUNCTIONS ====================

async def _analyze_image(content: bytes) -> Dict[str, Any]:
    """Analyze image characteristics."""
    from PIL import Image
    
    img = Image.open(io.BytesIO(content))
    total_pixels = img.width * img.height
    
    return {
        "width": img.width,
        "height": img.height,
        "total_pixels": total_pixels,
        "aspect_ratio": img.width / img.height,
        "format": img.format,
        "mode": img.mode,
        "is_low_res": total_pixels < 500000,  # Less than 0.5MP
        "is_high_res": total_pixels > 2000000,  # More than 2MP
        "needs_upscaling": total_pixels < 1000000  # Less than 1MP
    }


def _determine_enhancement_strategy(img_info: Dict[str, Any], enhancement_type: str, target_resolution: str) -> Dict[str, Any]:
    """Determine the best enhancement strategy based on image characteristics."""
    strategy = {"steps": []}
    
    if enhancement_type == "auto":
        if img_info["is_low_res"]:
            if img_info["total_pixels"] < 100000:  # Very low res
                strategy["steps"].append({
                    "name": "Creative Upscale",
                    "operation": "upscale_creative",
                    "default_prompt": "high quality, detailed, sharp"
                })
            else:
                strategy["steps"].append({
                    "name": "Conservative Upscale",
                    "operation": "upscale_conservative",
                    "default_prompt": "enhance quality, preserve details"
                })
        else:
            strategy["steps"].append({
                "name": "Fast Upscale",
                "operation": "upscale_fast",
                "default_prompt": ""
            })
    elif enhancement_type == "upscale":
        if target_resolution == "4k":
            strategy["steps"].append({
                "name": "Conservative Upscale to 4K",
                "operation": "upscale_conservative",
                "default_prompt": "4K resolution, high quality"
            })
        else:
            strategy["steps"].append({
                "name": "Fast Upscale",
                "operation": "upscale_fast",
                "default_prompt": ""
            })
    
    return strategy


def _bytes_to_upload_file(content: bytes, filename: str):
    """Convert bytes to UploadFile-like object."""
    from fastapi import UploadFile
    from io import BytesIO
    
    file_obj = BytesIO(content)
    file_obj.seek(0)
    
    # Create a mock UploadFile
    class MockUploadFile:
        def __init__(self, file_obj, filename):
            self.file = file_obj
            self.filename = filename
            self.content_type = "image/png"
        
        async def read(self):
            return self.file.read()
        
        async def seek(self, position):
            self.file.seek(position)
    
    return MockUploadFile(file_obj, filename)


def _generate_quality_recommendations(quality_score: float, brightness: float, contrast: float) -> List[str]:
    """Generate quality improvement recommendations."""
    recommendations = []
    
    if quality_score < 50:
        recommendations.append("Consider using a higher quality model like Ultra")
    
    if brightness < 100:
        recommendations.append("Image appears dark, consider adjusting lighting in prompt")
    elif brightness > 200:
        recommendations.append("Image appears bright, consider reducing exposure in prompt")
    
    if contrast < 30:
        recommendations.append("Low contrast detected, add 'high contrast' to prompt")
    
    if not recommendations:
        recommendations.append("Image quality looks good!")
    
    return recommendations


def _apply_prompt_optimizations(prompt: str, suggestions: List[str], target_style: Optional[str]) -> str:
    """Apply optimization suggestions to prompt."""
    optimized = prompt
    
    # Add style if suggested
    if target_style and f"Add style descriptor: {target_style}" in suggestions:
        optimized = f"{optimized}, {target_style} style"
    
    # Add quality enhancers if suggested
    if any("quality enhancer" in s for s in suggestions):
        optimized = f"{optimized}, high quality, detailed, sharp"
    
    return optimized.strip()


def _generate_negative_prompt_suggestions(prompt: str, target_style: Optional[str]) -> List[str]:
    """Generate negative prompt suggestions based on prompt analysis."""
    suggestions = []
    
    # Common negative prompts
    suggestions.extend([
        "blurry, low quality, pixelated",
        "distorted, deformed, malformed",
        "oversaturated, undersaturated"
    ])
    
    # Style-specific negative prompts
    if target_style:
        if "photorealistic" in target_style.lower():
            suggestions.append("cartoon, anime, illustration")
        elif "anime" in target_style.lower():
            suggestions.append("realistic, photographic")
    
    return suggestions


def _check_model_compatibility(prompt: str, model: str) -> Dict[str, Any]:
    """Check prompt compatibility with specific models."""
    compatibility = {"score": 100, "notes": []}
    
    if model == "ultra":
        if len(prompt.split()) < 5:
            compatibility["score"] -= 20
            compatibility["notes"].append("Ultra model works best with detailed prompts")
    elif model == "core":
        if len(prompt) > 500:
            compatibility["score"] -= 10
            compatibility["notes"].append("Core model works well with concise prompts")
    
    return compatibility


async def _process_batch_images(
    batch_id: str,
    images: List[UploadFile],
    operation: str,
    params: Dict[str, Any],
    stability_service: StabilityAIService
):
    """Background task for processing multiple images."""
    # In a real implementation, you'd store progress in a database
    # This is a simplified version for demonstration
    
    async with stability_service:
        for i, image in enumerate(images):
            try:
                if operation == "upscale_fast":
                    await stability_service.upscale_fast(image=image, **params)
                elif operation == "remove_background":
                    await stability_service.remove_background(image=image, **params)
                # Add other operations as needed
                
                # Log progress (in real implementation, update database)
                logger.info(f"Batch {batch_id}: Completed image {i+1}/{len(images)}")
                
            except Exception as e:
                logger.error(f"Batch {batch_id}: Error processing image {i+1}: {str(e)}")


# ==================== EXPERIMENTAL ENDPOINTS ====================

@router.post("/experimental/ai-director", summary="AI Director Mode")
async def ai_director_mode(
    concept: str = Form(..., description="High-level creative concept"),
    target_audience: Optional[str] = Form(None, description="Target audience"),
    mood: Optional[str] = Form(None, description="Desired mood"),
    color_palette: Optional[str] = Form(None, description="Preferred color palette"),
    iterations: Optional[int] = Form(3, description="Number of iterations"),
    stability_service: StabilityAIService = Depends(get_stability_service)
):
    """AI Director mode for automated creative decision making.
    
    This experimental endpoint acts as an AI creative director, making
    intelligent decisions about style, composition, and execution based on
    high-level creative concepts.
    """
    # Generate detailed prompts based on concept
    director_prompts = _generate_director_prompts(concept, target_audience, mood, color_palette)
    
    async with stability_service:
        iterations_results = []
        
        for i in range(iterations):
            prompt = director_prompts[i % len(director_prompts)]
            
            result = await stability_service.generate_ultra(
                prompt=prompt,
                output_format="webp"
            )
            
            if isinstance(result, bytes):
                iterations_results.append({
                    "iteration": i + 1,
                    "prompt": prompt,
                    "image": base64.b64encode(result).decode(),
                    "size": len(result)
                })
        
        return {
            "concept": concept,
            "director_analysis": {
                "target_audience": target_audience,
                "mood": mood,
                "color_palette": color_palette
            },
            "generated_prompts": director_prompts,
            "iterations": iterations_results
        }


def _generate_director_prompts(concept: str, audience: Optional[str], mood: Optional[str], colors: Optional[str]) -> List[str]:
    """Generate creative prompts based on director inputs."""
    base_prompt = concept
    
    # Add audience-specific elements
    if audience:
        if "professional" in audience.lower():
            base_prompt += ", professional, clean, sophisticated"
        elif "creative" in audience.lower():
            base_prompt += ", artistic, innovative, expressive"
        elif "casual" in audience.lower():
            base_prompt += ", friendly, approachable, relaxed"
    
    # Add mood elements
    if mood:
        base_prompt += f", {mood} mood"
    
    # Add color palette
    if colors:
        base_prompt += f", {colors} color palette"
    
    # Generate variations
    variations = [
        f"{base_prompt}, high quality, detailed",
        f"{base_prompt}, cinematic lighting, professional photography",
        f"{base_prompt}, artistic composition, creative perspective"
    ]
    
    return variations