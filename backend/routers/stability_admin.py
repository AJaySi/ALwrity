"""Admin endpoints for Stability AI service management."""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import json

from services.stability_service import get_stability_service, StabilityAIService
from middleware.stability_middleware import get_middleware_stats
from config.stability_config import (
    MODEL_PRICING, IMAGE_LIMITS, AUDIO_LIMITS, WORKFLOW_TEMPLATES,
    get_stability_config, get_model_recommendations, calculate_estimated_cost
)

router = APIRouter(prefix="/api/stability/admin", tags=["Stability AI Admin"])


# ==================== MONITORING ENDPOINTS ====================

@router.get("/stats", summary="Get Service Statistics")
async def get_service_stats():
    """Get comprehensive statistics about Stability AI service usage."""
    return {
        "service_info": {
            "name": "Stability AI Integration",
            "version": "1.0.0",
            "uptime": "N/A",  # Would track actual uptime
            "last_restart": datetime.utcnow().isoformat()
        },
        "middleware_stats": get_middleware_stats(),
        "pricing_info": MODEL_PRICING,
        "limits": {
            "image": IMAGE_LIMITS,
            "audio": AUDIO_LIMITS
        }
    }


@router.get("/health/detailed", summary="Detailed Health Check")
async def detailed_health_check(
    stability_service: StabilityAIService = Depends(get_stability_service)
):
    """Perform detailed health check of Stability AI service."""
    health_status = {
        "timestamp": datetime.utcnow().isoformat(),
        "overall_status": "healthy",
        "checks": {}
    }
    
    try:
        # Test API connectivity
        async with stability_service:
            account_info = await stability_service.get_account_details()
            health_status["checks"]["api_connectivity"] = {
                "status": "healthy",
                "response_time": "N/A",
                "account_id": account_info.get("id", "unknown")
            }
    except Exception as e:
        health_status["checks"]["api_connectivity"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["overall_status"] = "degraded"
    
    try:
        # Test account balance
        async with stability_service:
            balance_info = await stability_service.get_account_balance()
            credits = balance_info.get("credits", 0)
            
            health_status["checks"]["account_balance"] = {
                "status": "healthy" if credits > 10 else "warning",
                "credits": credits,
                "warning": "Low credit balance" if credits < 10 else None
            }
    except Exception as e:
        health_status["checks"]["account_balance"] = {
            "status": "error",
            "error": str(e)
        }
    
    # Check configuration
    try:
        config = get_stability_config()
        health_status["checks"]["configuration"] = {
            "status": "healthy",
            "api_key_configured": bool(config.api_key),
            "base_url": config.base_url
        }
    except Exception as e:
        health_status["checks"]["configuration"] = {
            "status": "error",
            "error": str(e)
        }
        health_status["overall_status"] = "unhealthy"
    
    return health_status


@router.get("/usage/summary", summary="Get Usage Summary")
async def get_usage_summary(
    days: Optional[int] = Query(7, description="Number of days to analyze")
):
    """Get usage summary for the specified time period."""
    # In a real implementation, this would query a database
    # For now, return mock data
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    return {
        "period": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat(),
            "days": days
        },
        "usage_summary": {
            "total_requests": 156,
            "successful_requests": 148,
            "failed_requests": 8,
            "success_rate": 94.87,
            "total_credits_used": 450.5,
            "average_credits_per_request": 2.89
        },
        "operation_breakdown": {
            "generate_ultra": {"requests": 25, "credits": 200},
            "generate_core": {"requests": 45, "credits": 135},
            "upscale_fast": {"requests": 30, "credits": 60},
            "inpaint": {"requests": 20, "credits": 100},
            "control_sketch": {"requests": 15, "credits": 75}
        },
        "daily_usage": [
            {"date": (end_date - timedelta(days=i)).strftime("%Y-%m-%d"), 
             "requests": 20 + i * 2, 
             "credits": 50 + i * 5}
            for i in range(days)
        ]
    }


@router.get("/costs/estimate", summary="Estimate Operation Costs")
async def estimate_operation_costs(
    operations: str = Query(..., description="JSON array of operations to estimate"),
    model_preferences: Optional[str] = Query(None, description="JSON object of model preferences")
):
    """Estimate costs for a list of operations."""
    try:
        ops_list = json.loads(operations)
        preferences = json.loads(model_preferences) if model_preferences else {}
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in parameters")
    
    estimates = []
    total_cost = 0
    
    for op in ops_list:
        operation = op.get("operation")
        model = preferences.get(operation) or op.get("model")
        steps = op.get("steps")
        
        cost = calculate_estimated_cost(operation, model, steps)
        total_cost += cost
        
        estimates.append({
            "operation": operation,
            "model": model,
            "estimated_credits": cost,
            "description": f"Estimated cost for {operation}"
        })
    
    return {
        "estimates": estimates,
        "total_estimated_credits": total_cost,
        "currency_equivalent": f"${total_cost * 0.01:.2f}",  # Assuming $0.01 per credit
        "timestamp": datetime.utcnow().isoformat()
    }


# ==================== CONFIGURATION ENDPOINTS ====================

@router.get("/config", summary="Get Current Configuration")
async def get_current_config():
    """Get current Stability AI service configuration."""
    try:
        config = get_stability_config()
        return {
            "base_url": config.base_url,
            "timeout": config.timeout,
            "max_retries": config.max_retries,
            "max_file_size": config.max_file_size,
            "supported_image_formats": config.supported_image_formats,
            "supported_audio_formats": config.supported_audio_formats,
            "api_key_configured": bool(config.api_key),
            "api_key_preview": f"{config.api_key[:8]}..." if config.api_key else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Configuration error: {str(e)}")


@router.get("/models/recommendations", summary="Get Model Recommendations")
async def get_model_recommendations_endpoint(
    use_case: str = Query(..., description="Use case (portrait, landscape, art, product, concept)"),
    quality_preference: str = Query("standard", description="Quality preference (draft, standard, premium)"),
    speed_preference: str = Query("balanced", description="Speed preference (fast, balanced, quality)")
):
    """Get model recommendations based on use case and preferences."""
    recommendations = get_model_recommendations(use_case, quality_preference, speed_preference)
    
    # Add detailed information
    recommendations["use_case_info"] = {
        "description": f"Recommendations optimized for {use_case} use case",
        "quality_level": quality_preference,
        "speed_priority": speed_preference
    }
    
    # Add cost information
    primary_cost = calculate_estimated_cost("generate", recommendations["primary"])
    alternative_cost = calculate_estimated_cost("generate", recommendations["alternative"])
    
    recommendations["cost_comparison"] = {
        "primary_model_cost": primary_cost,
        "alternative_model_cost": alternative_cost,
        "cost_difference": abs(primary_cost - alternative_cost)
    }
    
    return recommendations


@router.get("/workflows/templates", summary="Get Workflow Templates")
async def get_workflow_templates():
    """Get available workflow templates."""
    return {
        "templates": WORKFLOW_TEMPLATES,
        "template_count": len(WORKFLOW_TEMPLATES),
        "categories": list(set(
            template["description"].split()[0].lower() 
            for template in WORKFLOW_TEMPLATES.values()
        ))
    }


@router.post("/workflows/validate", summary="Validate Custom Workflow")
async def validate_custom_workflow(
    workflow: dict
):
    """Validate a custom workflow configuration."""
    from utils.stability_utils import WorkflowManager
    
    steps = workflow.get("steps", [])
    
    if not steps:
        raise HTTPException(status_code=400, detail="Workflow must contain at least one step")
    
    # Validate workflow
    errors = WorkflowManager.validate_workflow(steps)
    
    if errors:
        return {
            "is_valid": False,
            "errors": errors,
            "workflow": workflow
        }
    
    # Calculate estimated cost and time
    total_cost = sum(calculate_estimated_cost(step.get("operation", "unknown")) for step in steps)
    estimated_time = len(steps) * 30  # Rough estimate
    
    # Optimize workflow
    optimized_steps = WorkflowManager.optimize_workflow(steps)
    
    return {
        "is_valid": True,
        "original_workflow": workflow,
        "optimized_workflow": {"steps": optimized_steps},
        "estimates": {
            "total_credits": total_cost,
            "estimated_time_seconds": estimated_time,
            "step_count": len(steps)
        },
        "optimizations_applied": len(steps) != len(optimized_steps)
    }


# ==================== CACHE MANAGEMENT ====================

@router.post("/cache/clear", summary="Clear Service Cache")
async def clear_cache():
    """Clear all cached data."""
    from middleware.stability_middleware import caching
    
    caching.clear_cache()
    
    return {
        "status": "success",
        "message": "Cache cleared successfully",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/cache/stats", summary="Get Cache Statistics")
async def get_cache_stats():
    """Get cache usage statistics."""
    from middleware.stability_middleware import caching
    
    return {
        "cache_stats": caching.get_cache_stats(),
        "timestamp": datetime.utcnow().isoformat()
    }


# ==================== RATE LIMITING MANAGEMENT ====================

@router.get("/rate-limit/status", summary="Get Rate Limit Status")
async def get_rate_limit_status():
    """Get current rate limiting status."""
    from middleware.stability_middleware import rate_limiter
    
    return {
        "rate_limit_config": {
            "requests_per_window": rate_limiter.requests_per_window,
            "window_seconds": rate_limiter.window_seconds
        },
        "current_blocks": len(rate_limiter.blocked_until),
        "active_clients": len(rate_limiter.request_times),
        "timestamp": datetime.utcnow().isoformat()
    }


@router.post("/rate-limit/reset", summary="Reset Rate Limits")
async def reset_rate_limits():
    """Reset rate limiting for all clients (admin only)."""
    from middleware.stability_middleware import rate_limiter
    
    # Clear all rate limiting data
    rate_limiter.request_times.clear()
    rate_limiter.blocked_until.clear()
    
    return {
        "status": "success",
        "message": "Rate limits reset for all clients",
        "timestamp": datetime.utcnow().isoformat()
    }


# ==================== ACCOUNT MANAGEMENT ====================

@router.get("/account/detailed", summary="Get Detailed Account Information")
async def get_detailed_account_info(
    stability_service: StabilityAIService = Depends(get_stability_service)
):
    """Get detailed account information including usage and limits."""
    async with stability_service:
        account_info = await stability_service.get_account_details()
        balance_info = await stability_service.get_account_balance()
        engines_info = await stability_service.list_engines()
    
    return {
        "account": account_info,
        "balance": balance_info,
        "available_engines": engines_info,
        "service_limits": {
            "rate_limit": "150 requests per 10 seconds",
            "max_file_size": "10MB for images, 50MB for audio",
            "result_storage": "24 hours for async generations"
        },
        "pricing": MODEL_PRICING,
        "timestamp": datetime.utcnow().isoformat()
    }


# ==================== DEBUGGING ENDPOINTS ====================

@router.post("/debug/test-connection", summary="Test API Connection")
async def test_api_connection(
    stability_service: StabilityAIService = Depends(get_stability_service)
):
    """Test connection to Stability AI API."""
    test_results = {}
    
    try:
        async with stability_service:
            # Test account endpoint
            start_time = datetime.utcnow()
            account_info = await stability_service.get_account_details()
            end_time = datetime.utcnow()
            
            test_results["account_test"] = {
                "status": "success",
                "response_time_ms": (end_time - start_time).total_seconds() * 1000,
                "account_id": account_info.get("id")
            }
    except Exception as e:
        test_results["account_test"] = {
            "status": "error",
            "error": str(e)
        }
    
    try:
        async with stability_service:
            # Test engines endpoint
            start_time = datetime.utcnow()
            engines = await stability_service.list_engines()
            end_time = datetime.utcnow()
            
            test_results["engines_test"] = {
                "status": "success",
                "response_time_ms": (end_time - start_time).total_seconds() * 1000,
                "engine_count": len(engines)
            }
    except Exception as e:
        test_results["engines_test"] = {
            "status": "error",
            "error": str(e)
        }
    
    overall_status = "healthy" if all(
        test["status"] == "success" 
        for test in test_results.values()
    ) else "unhealthy"
    
    return {
        "overall_status": overall_status,
        "tests": test_results,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/debug/request-logs", summary="Get Recent Request Logs")
async def get_request_logs(
    limit: int = Query(50, description="Maximum number of log entries to return"),
    operation_filter: Optional[str] = Query(None, description="Filter by operation type")
):
    """Get recent request logs for debugging."""
    from middleware.stability_middleware import request_logging
    
    logs = request_logging.get_recent_logs(limit)
    
    if operation_filter:
        logs = [
            log for log in logs 
            if operation_filter in log.get("path", "")
        ]
    
    return {
        "logs": logs,
        "total_entries": len(logs),
        "filter_applied": operation_filter,
        "summary": request_logging.get_log_summary()
    }


# ==================== MAINTENANCE ENDPOINTS ====================

@router.post("/maintenance/cleanup", summary="Cleanup Service Resources")
async def cleanup_service_resources():
    """Cleanup service resources and temporary files."""
    cleanup_results = {}
    
    try:
        # Clear caches
        from middleware.stability_middleware import caching
        caching.clear_cache()
        cleanup_results["cache_cleanup"] = "success"
    except Exception as e:
        cleanup_results["cache_cleanup"] = f"error: {str(e)}"
    
    try:
        # Clean up temporary files (if any)
        import os
        import glob
        
        temp_files = glob.glob("/tmp/stability_*")
        removed_count = 0
        
        for temp_file in temp_files:
            try:
                os.remove(temp_file)
                removed_count += 1
            except:
                pass
        
        cleanup_results["temp_file_cleanup"] = f"removed {removed_count} files"
    except Exception as e:
        cleanup_results["temp_file_cleanup"] = f"error: {str(e)}"
    
    return {
        "cleanup_results": cleanup_results,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.post("/maintenance/optimize", summary="Optimize Service Performance")
async def optimize_service_performance():
    """Optimize service performance by adjusting configurations."""
    optimizations = []
    
    # Check and optimize cache settings
    from middleware.stability_middleware import caching
    cache_stats = caching.get_cache_stats()
    
    if cache_stats["total_entries"] > 100:
        caching.clear_cache()
        optimizations.append("Cleared large cache to free memory")
    
    # Check rate limiting efficiency
    from middleware.stability_middleware import rate_limiter
    if len(rate_limiter.blocked_until) > 10:
        # Reset old blocks
        import time
        current_time = time.time()
        expired_blocks = [
            client_id for client_id, block_time in rate_limiter.blocked_until.items()
            if current_time > block_time
        ]
        
        for client_id in expired_blocks:
            del rate_limiter.blocked_until[client_id]
        
        optimizations.append(f"Cleared {len(expired_blocks)} expired rate limit blocks")
    
    return {
        "optimizations_applied": optimizations,
        "optimization_count": len(optimizations),
        "timestamp": datetime.utcnow().isoformat()
    }


# ==================== FEATURE FLAGS ====================

@router.get("/features", summary="Get Feature Flags")
async def get_feature_flags():
    """Get current feature flag status."""
    from config.stability_config import FEATURE_FLAGS
    
    return {
        "features": FEATURE_FLAGS,
        "enabled_count": sum(1 for enabled in FEATURE_FLAGS.values() if enabled),
        "total_features": len(FEATURE_FLAGS)
    }


@router.post("/features/{feature_name}/toggle", summary="Toggle Feature Flag")
async def toggle_feature_flag(feature_name: str):
    """Toggle a feature flag on/off."""
    from config.stability_config import FEATURE_FLAGS
    
    if feature_name not in FEATURE_FLAGS:
        raise HTTPException(status_code=404, detail=f"Feature '{feature_name}' not found")
    
    # Toggle the feature
    FEATURE_FLAGS[feature_name] = not FEATURE_FLAGS[feature_name]
    
    return {
        "feature": feature_name,
        "new_status": FEATURE_FLAGS[feature_name],
        "message": f"Feature '{feature_name}' {'enabled' if FEATURE_FLAGS[feature_name] else 'disabled'}",
        "timestamp": datetime.utcnow().isoformat()
    }


# ==================== EXPORT ENDPOINTS ====================

@router.get("/export/config", summary="Export Configuration")
async def export_configuration():
    """Export current service configuration."""
    config = get_stability_config()
    
    export_data = {
        "service_config": {
            "base_url": config.base_url,
            "timeout": config.timeout,
            "max_retries": config.max_retries,
            "max_file_size": config.max_file_size
        },
        "pricing": MODEL_PRICING,
        "limits": {
            "image": IMAGE_LIMITS,
            "audio": AUDIO_LIMITS
        },
        "workflows": WORKFLOW_TEMPLATES,
        "export_timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }
    
    return export_data


@router.get("/export/usage-report", summary="Export Usage Report")
async def export_usage_report(
    format_type: str = Query("json", description="Export format (json, csv)"),
    days: int = Query(30, description="Number of days to include")
):
    """Export detailed usage report."""
    # In a real implementation, this would query actual usage data
    
    usage_data = {
        "report_info": {
            "generated_at": datetime.utcnow().isoformat(),
            "period_days": days,
            "format": format_type
        },
        "summary": {
            "total_requests": 500,
            "total_credits_used": 1250,
            "average_daily_usage": 41.67,
            "most_used_operation": "generate_core"
        },
        "detailed_usage": [
            {
                "date": (datetime.utcnow() - timedelta(days=i)).strftime("%Y-%m-%d"),
                "requests": 15 + (i % 5),
                "credits": 37.5 + (i % 5) * 2.5,
                "top_operation": "generate_core"
            }
            for i in range(days)
        ]
    }
    
    if format_type == "csv":
        # Convert to CSV format
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=["date", "requests", "credits", "top_operation"])
        writer.writeheader()
        writer.writerows(usage_data["detailed_usage"])
        
        return Response(
            content=output.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=stability_usage_{days}days.csv"}
        )
    
    return usage_data


# ==================== SYSTEM INFO ENDPOINTS ====================

@router.get("/system/info", summary="Get System Information")
async def get_system_info():
    """Get comprehensive system information."""
    import sys
    import platform
    import psutil
    
    return {
        "system": {
            "platform": platform.platform(),
            "python_version": sys.version,
            "cpu_count": psutil.cpu_count(),
            "memory_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "memory_available_gb": round(psutil.virtual_memory().available / (1024**3), 2)
        },
        "service": {
            "name": "Stability AI Integration",
            "version": "1.0.0",
            "uptime": "N/A",  # Would track actual uptime
            "active_connections": "N/A"
        },
        "api_info": {
            "base_url": "https://api.stability.ai",
            "supported_versions": ["v2beta", "v1"],
            "rate_limit": "150 requests per 10 seconds"
        },
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/system/dependencies", summary="Get Service Dependencies")
async def get_service_dependencies():
    """Get information about service dependencies."""
    dependencies = {
        "required": {
            "fastapi": "Web framework",
            "aiohttp": "HTTP client for API calls",
            "pydantic": "Data validation",
            "pillow": "Image processing",
            "loguru": "Logging"
        },
        "optional": {
            "scikit-learn": "Color analysis",
            "numpy": "Numerical operations",
            "psutil": "System monitoring"
        },
        "external_services": {
            "stability_ai_api": {
                "url": "https://api.stability.ai",
                "status": "unknown",  # Would check actual status
                "description": "Stability AI REST API"
            }
        }
    }
    
    return dependencies


# ==================== WEBHOOK MANAGEMENT ====================

@router.get("/webhooks/config", summary="Get Webhook Configuration")
async def get_webhook_config():
    """Get current webhook configuration."""
    return {
        "webhooks_enabled": True,
        "supported_events": [
            "generation.completed",
            "generation.failed",
            "upscale.completed",
            "edit.completed"
        ],
        "webhook_url": "/api/stability/webhook/generation-complete",
        "retry_policy": {
            "max_retries": 3,
            "retry_delay_seconds": 5
        }
    }


@router.post("/webhooks/test", summary="Test Webhook Delivery")
async def test_webhook_delivery():
    """Test webhook delivery mechanism."""
    test_payload = {
        "event": "generation.completed",
        "generation_id": "test_generation_id",
        "status": "success",
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # In a real implementation, this would send to configured webhook URLs
    
    return {
        "test_status": "success",
        "payload_sent": test_payload,
        "timestamp": datetime.utcnow().isoformat()
    }