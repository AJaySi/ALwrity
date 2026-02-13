"""
Pre-flight Validation Utility for Multi-Operation Workflows

Provides transparent validation for operations that involve multiple API calls.
Services can use this to validate entire workflows before making any external API calls.
"""

from typing import Dict, Any, List, Optional, Tuple
from fastapi import HTTPException
from utils.logging import get_logger
logger = get_logger("subscription_preflight_validator", migration_mode=True)

from services.subscription.pricing_service import PricingService
from models.subscription_models import APIProvider


def validate_research_operations(
    pricing_service: PricingService,
    user_id: str,
    gpt_provider: str = "google"
) -> None:
    """
    Validate all operations for a research workflow before making ANY API calls.
    
    This prevents wasteful external API calls (like Google Grounding) if subsequent
    LLM calls would fail due to token or call limits.
    
    Args:
        pricing_service: PricingService instance
        user_id: User ID for subscription checking
        gpt_provider: GPT provider from env var (defaults to "google")
        
    Returns:
        (can_proceed, error_message, error_details)
        If can_proceed is False, raises HTTPException with 429 status
    """
    try:
        # Determine actual provider for LLM calls based on GPT_PROVIDER env var
        gpt_provider_lower = gpt_provider.lower()
        if gpt_provider_lower == "huggingface":
            llm_provider_enum = APIProvider.MISTRAL  # Maps to HuggingFace
            llm_provider_name = "huggingface"
        else:
            llm_provider_enum = APIProvider.GEMINI
            llm_provider_name = "gemini"
        
        # Estimate tokens for each operation in research workflow
        # Google Grounding call: ~1200 tokens (input: ~500 tokens, output: ~700 tokens for research results)
        # Keyword analyzer: ~1000 tokens (input: 3000 chars research, output: structured JSON)
        # Competitor analyzer: ~1000 tokens (input: 3000 chars research, output: structured JSON)
        # Content angle generator: ~1000 tokens (input: 3000 chars research, output: list of angles)
        # Note: These are conservative estimates. Actual usage may be lower, but we use these for pre-flight validation
        # to prevent wasteful API calls if the workflow would exceed limits.
        
        operations_to_validate = [
            {
                'provider': APIProvider.GEMINI,  # Google Grounding uses Gemini
                'tokens_requested': 1200,  # Reduced from 2000 to more realistic estimate
                'actual_provider_name': 'gemini',
                'operation_type': 'google_grounding'
            },
            {
                'provider': llm_provider_enum,
                'tokens_requested': 1000,
                'actual_provider_name': llm_provider_name,
                'operation_type': 'keyword_analysis'
            },
            {
                'provider': llm_provider_enum,
                'tokens_requested': 1000,
                'actual_provider_name': llm_provider_name,
                'operation_type': 'competitor_analysis'
            },
            {
                'provider': llm_provider_enum,
                'tokens_requested': 1000,
                'actual_provider_name': llm_provider_name,
                'operation_type': 'content_angle_generation'
            }
        ]
        
        logger.info(f"[Pre-flight Validator] 🚀 Starting Research Workflow Validation")
        logger.info(f"   ├─ User: {user_id}")
        logger.info(f"   ├─ LLM Provider: {llm_provider_name} (GPT_PROVIDER={gpt_provider})")
        logger.info(f"   └─ Operations to validate: {len(operations_to_validate)}")
        
        can_proceed, message, error_details = pricing_service.check_comprehensive_limits(
            user_id=user_id,
            operations=operations_to_validate
        )
        
        if not can_proceed:
            usage_info = error_details.get('usage_info', {}) if error_details else {}
            provider = usage_info.get('provider', llm_provider_name) if usage_info else llm_provider_name
            operation_type = usage_info.get('operation_type', 'unknown')
            
            logger.warning(f"[Pre-flight] Research blocked for user {user_id}: {operation_type} ({provider}) - {message}")
            
            # Raise HTTPException immediately - frontend gets immediate response, no API calls made
            raise HTTPException(
                status_code=429,
                detail={
                    'error': message,
                    'message': message,
                    'provider': provider,
                    'usage_info': usage_info if usage_info else error_details
                }
            )
        
        logger.info(f"[Pre-flight Validator] ✅ RESEARCH WORKFLOW APPROVED")
        logger.info(f"   ├─ User: {user_id}")
        logger.info(f"   └─ All {len(operations_to_validate)} operations validated - proceeding with API calls")
        # Validation passed - no return needed (function raises HTTPException if validation fails)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Pre-flight Validator] Error validating research operations: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                'error': f"Failed to validate operations: {str(e)}",
                'message': f"Failed to validate operations: {str(e)}"
            }
        )


def validate_exa_research_operations(
    pricing_service: PricingService,
    user_id: str,
    gpt_provider: str = "google"
) -> None:
    """
    Validate all operations for an Exa research workflow before making ANY API calls.
    
    This prevents wasteful external API calls (like Exa search) if subsequent
    LLM calls would fail due to token or call limits.
    
    Args:
        pricing_service: PricingService instance
        user_id: User ID for subscription checking
        gpt_provider: GPT provider from env var (defaults to "google")
        
    Returns:
        None
        If validation fails, raises HTTPException with 429 status
    """
    try:
        # Determine actual provider for LLM calls based on GPT_PROVIDER env var
        gpt_provider_lower = gpt_provider.lower()
        if gpt_provider_lower == "huggingface":
            llm_provider_enum = APIProvider.MISTRAL  # Maps to HuggingFace
            llm_provider_name = "huggingface"
        else:
            llm_provider_enum = APIProvider.GEMINI
            llm_provider_name = "gemini"
        
        # Estimate tokens for each operation in Exa research workflow
        # Exa Search call: 1 Exa API call (not token-based)
        # Keyword analyzer: ~1000 tokens (input: research results, output: structured JSON)
        # Competitor analyzer: ~1000 tokens (input: research results, output: structured JSON)
        # Content angle generator: ~1000 tokens (input: research results, output: list of angles)
        # Note: These are conservative estimates for pre-flight validation
        
        operations_to_validate = [
            {
                'provider': APIProvider.EXA,  # Exa API call
                'tokens_requested': 0,
                'actual_provider_name': 'exa',
                'operation_type': 'exa_neural_search'
            },
            {
                'provider': llm_provider_enum,
                'tokens_requested': 1000,
                'actual_provider_name': llm_provider_name,
                'operation_type': 'keyword_analysis'
            },
            {
                'provider': llm_provider_enum,
                'tokens_requested': 1000,
                'actual_provider_name': llm_provider_name,
                'operation_type': 'competitor_analysis'
            },
            {
                'provider': llm_provider_enum,
                'tokens_requested': 1000,
                'actual_provider_name': llm_provider_name,
                'operation_type': 'content_angle_generation'
            }
        ]
        
        logger.info(f"[Pre-flight Validator] 🚀 Starting Exa Research Workflow Validation")
        logger.info(f"   ├─ User: {user_id}")
        logger.info(f"   ├─ LLM Provider: {llm_provider_name} (GPT_PROVIDER={gpt_provider})")
        logger.info(f"   └─ Operations to validate: {len(operations_to_validate)}")
        
        can_proceed, message, error_details = pricing_service.check_comprehensive_limits(
            user_id=user_id,
            operations=operations_to_validate
        )
        
        if not can_proceed:
            usage_info = error_details.get('usage_info', {}) if error_details else {}
            provider = usage_info.get('provider', llm_provider_name) if usage_info else llm_provider_name
            operation_type = usage_info.get('operation_type', 'unknown')
            
            logger.error(f"[Pre-flight Validator] ❌ EXA RESEARCH WORKFLOW BLOCKED")
            logger.error(f"   ├─ User: {user_id}")
            logger.error(f"   ├─ Blocked at: {operation_type}")
            logger.error(f"   ├─ Provider: {provider}")
            logger.error(f"   └─ Reason: {message}")
            
            # Raise HTTPException immediately - frontend gets immediate response, no API calls made
            raise HTTPException(
                status_code=429,
                detail={
                    'error': message,
                    'message': message,
                    'provider': provider,
                    'usage_info': usage_info if usage_info else error_details
                }
            )
        
        logger.info(f"[Pre-flight Validator] ✅ EXA RESEARCH WORKFLOW APPROVED")
        logger.info(f"   ├─ User: {user_id}")
        logger.info(f"   └─ All {len(operations_to_validate)} operations validated - proceeding with API calls")
        # Validation passed - no return needed (function raises HTTPException if validation fails)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Pre-flight Validator] Error validating Exa research operations: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                'error': f"Failed to validate operations: {str(e)}",
                'message': f"Failed to validate operations: {str(e)}"
            }
        )


def validate_image_generation_operations(
    pricing_service: PricingService,
    user_id: str,
    num_images: int = 1
) -> None:
    """
    Validate image generation operation(s) before making API calls.
    
    Args:
        pricing_service: PricingService instance
        user_id: User ID for subscription checking
        num_images: Number of images to generate (for multiple variations)
        
    Returns:
        None
        If validation fails, raises HTTPException with 429 status
    """
    try:
        # Create validation operations for each image
        operations_to_validate = [
            {
                'provider': APIProvider.STABILITY,
                'tokens_requested': 0,
                'actual_provider_name': 'stability',
                'operation_type': 'image_generation'
            }
            for _ in range(num_images)
        ]
        
        logger.info(f"[Pre-flight Validator] 🚀 Validating {num_images} image generation(s) for user {user_id}")
        
        can_proceed, message, error_details = pricing_service.check_comprehensive_limits(
            user_id=user_id,
            operations=operations_to_validate
        )
        
        if not can_proceed:
            logger.error(f"[Pre-flight Validator] Image generation blocked for user {user_id}: {message}")
            
            usage_info = error_details.get('usage_info', {}) if error_details else {}
            provider = usage_info.get('provider', 'stability') if usage_info else 'stability'
            
            raise HTTPException(
                status_code=429,
                detail={
                    'error': message,
                    'message': message,
                    'provider': provider,
                    'usage_info': usage_info if usage_info else error_details
                }
            )
        
        logger.info(f"[Pre-flight Validator] ✅ Image generation validated for user {user_id}")
        # Validation passed - no return needed (function raises HTTPException if validation fails)
        
    except HTTPException:
        raise


def validate_image_upscale_operations(
    pricing_service: PricingService,
    user_id: str,
    num_images: int = 1
) -> None:
    """
    Validate image upscaling before making API calls.
    """
    try:
        operations_to_validate = [
            {
                'provider': APIProvider.STABILITY,
                'tokens_requested': 0,
                'actual_provider_name': 'stability',
                'operation_type': 'image_upscale'
            }
            for _ in range(num_images)
        ]

        logger.info(f"[Pre-flight Validator] 🚀 Validating {num_images} image upscale request(s) for user {user_id}")

        can_proceed, message, error_details = pricing_service.check_comprehensive_limits(
            user_id=user_id,
            operations=operations_to_validate
        )

        if not can_proceed:
            logger.error(f"[Pre-flight Validator] Image upscale blocked for user {user_id}: {message}")

            usage_info = error_details.get('usage_info', {}) if error_details else {}
            provider = usage_info.get('provider', 'stability') if usage_info else 'stability'

            raise HTTPException(
                status_code=429,
                detail={
                    'error': message,
                    'message': message,
                    'provider': provider,
                    'usage_info': usage_info if usage_info else error_details
                }
            )

        logger.info(f"[Pre-flight Validator] ✅ Image upscale validated for user {user_id}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Pre-flight Validator] Error validating image generation: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                'error': f"Failed to validate image generation: {str(e)}",
                'message': f"Failed to validate image generation: {str(e)}"
            }
        )


def validate_image_editing_operations(
    pricing_service: PricingService,
    user_id: str
) -> None:
    """
    Validate image editing operation before making API calls.
    
    Args:
        pricing_service: PricingService instance
        user_id: User ID for subscription checking
        
    Returns:
        None - raises HTTPException with 429 status if validation fails
    """
    try:
        operations_to_validate = [
            {
                'provider': APIProvider.IMAGE_EDIT,
                'tokens_requested': 0,
                'actual_provider_name': 'image_edit',
                'operation_type': 'image_editing'
            }
        ]
        
        can_proceed, message, error_details = pricing_service.check_comprehensive_limits(
            user_id=user_id,
            operations=operations_to_validate
        )
        
        if not can_proceed:
            logger.error(f"[Pre-flight Validator] Image editing blocked for user {user_id}: {message}")
            
            usage_info = error_details.get('usage_info', {}) if error_details else {}
            provider = usage_info.get('provider', 'image_edit') if usage_info else 'image_edit'
            
            raise HTTPException(
                status_code=429,
                detail={
                    'error': message,
                    'message': message,
                    'provider': provider,
                    'usage_info': usage_info if usage_info else error_details
                }
            )
        
        logger.info(f"[Pre-flight Validator] ✅ Image editing validated for user {user_id}")
        # Validation passed - no return needed (function raises HTTPException if validation fails)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Pre-flight Validator] Error validating image editing: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                'error': f"Failed to validate image editing: {str(e)}",
                'message': f"Failed to validate image editing: {str(e)}"
            }
        )


def validate_image_control_operations(
    pricing_service: PricingService,
    user_id: str,
    num_images: int = 1
) -> None:
    """
    Validate image control operations (sketch-to-image, structure control, style transfer) before making API calls.
    
    Control operations use Stability AI for image generation with control inputs, so they use
    the same validation as image generation operations.
    
    Args:
        pricing_service: PricingService instance
        user_id: User ID for subscription checking
        num_images: Number of images to generate (for multiple variations)
        
    Returns:
        None - raises HTTPException with 429 status if validation fails
    """
    try:
        # Control operations use Stability AI, same as image generation
        operations_to_validate = [
            {
                'provider': APIProvider.STABILITY,
                'tokens_requested': 0,
                'actual_provider_name': 'stability',
                'operation_type': 'image_generation'  # Control ops use image generation limits
            }
            for _ in range(num_images)
        ]
        
        logger.info(f"[Pre-flight Validator] 🚀 Validating {num_images} image control operation(s) for user {user_id}")
        
        can_proceed, message, error_details = pricing_service.check_comprehensive_limits(
            user_id=user_id,
            operations=operations_to_validate
        )
        
        if not can_proceed:
            logger.error(f"[Pre-flight Validator] Image control blocked for user {user_id}: {message}")
            
            usage_info = error_details.get('usage_info', {}) if error_details else {}
            provider = usage_info.get('provider', 'stability') if usage_info else 'stability'
            
            raise HTTPException(
                status_code=429,
                detail={
                    'error': message,
                    'message': message,
                    'provider': provider,
                    'usage_info': usage_info if usage_info else error_details
                }
            )
        
        logger.info(f"[Pre-flight Validator] ✅ Image control validated for user {user_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Pre-flight Validator] Error validating image control: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                'error': f"Failed to validate image control: {str(e)}",
                'message': f"Failed to validate image control: {str(e)}"
            }
        )


def validate_video_generation_operations(
    pricing_service: PricingService,
    user_id: str
) -> None:
    """
    Validate video generation operation before making API calls.
    
    Args:
        pricing_service: PricingService instance
        user_id: User ID for subscription checking
        
    Returns:
        None - raises HTTPException with 429 status if validation fails
    """
    try:
        operations_to_validate = [
            {
                'provider': APIProvider.VIDEO,
                'tokens_requested': 0,
                'actual_provider_name': 'video',
                'operation_type': 'video_generation'
            }
        ]
        
        can_proceed, message, error_details = pricing_service.check_comprehensive_limits(
            user_id=user_id,
            operations=operations_to_validate
        )
        
        if not can_proceed:
            logger.error(f"[Pre-flight Validator] Video generation blocked for user {user_id}: {message}")
            
            usage_info = error_details.get('usage_info', {}) if error_details else {}
            provider = usage_info.get('provider', 'video') if usage_info else 'video'
            
            raise HTTPException(
                status_code=429,
                detail={
                    'error': message,
                    'message': message,
                    'provider': provider,
                    'usage_info': usage_info if usage_info else error_details
                }
            )
        
        logger.info(f"[Pre-flight Validator] ✅ Video generation validated for user {user_id}")
        # Validation passed - no return needed (function raises HTTPException if validation fails)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Pre-flight Validator] Error validating video generation: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                'error': f"Failed to validate video generation: {str(e)}",
                'message': f"Failed to validate video generation: {str(e)}"
            }
        )


def validate_scene_animation_operation(
    pricing_service: PricingService,
    user_id: str,
) -> None:
    """
    Validate the per-scene animation workflow before API calls.
    """
    try:
        operations_to_validate = [
            {
                'provider': APIProvider.VIDEO,
                'tokens_requested': 0,
                'actual_provider_name': 'wavespeed',
                'operation_type': 'scene_animation',
            }
        ]

        can_proceed, message, error_details = pricing_service.check_comprehensive_limits(
            user_id=user_id,
            operations=operations_to_validate,
        )

        if not can_proceed:
            logger.error(f"[Pre-flight Validator] Scene animation blocked for user {user_id}: {message}")
            usage_info = error_details.get('usage_info', {}) if error_details else {}
            provider = usage_info.get('provider', 'video') if usage_info else 'video'
            raise HTTPException(
                status_code=429,
                detail={
                    'error': message,
                    'message': message,
                    'provider': provider,
                    'usage_info': usage_info if usage_info else error_details,
                }
            )

        logger.info(f"[Pre-flight Validator] ✅ Scene animation validated for user {user_id}")
        # Validation passed - no return needed (function raises HTTPException if validation fails)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Pre-flight Validator] Error validating scene animation: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                'error': f"Failed to validate scene animation: {str(e)}",
                'message': f"Failed to validate scene animation: {str(e)}"
            }
        )


def validate_image_control_operations(
    pricing_service: PricingService,
    user_id: str,
    num_images: int = 1
) -> None:
    """
    Validate image control operations (sketch-to-image, structure control, style transfer) before making API calls.
    
    Control operations use Stability AI for image generation with control inputs, so they use
    the same validation as image generation operations.
    
    Args:
        pricing_service: PricingService instance
        user_id: User ID for subscription checking
        num_images: Number of images to generate (for multiple variations)
        
    Returns:
        None - raises HTTPException with 429 status if validation fails
    """
    try:
        # Control operations use Stability AI, same as image generation
        operations_to_validate = [
            {
                'provider': APIProvider.STABILITY,
                'tokens_requested': 0,
                'actual_provider_name': 'stability',
                'operation_type': 'image_generation'  # Control ops use image generation limits
            }
            for _ in range(num_images)
        ]
        
        logger.info(f"[Pre-flight Validator] 🚀 Validating {num_images} image control operation(s) for user {user_id}")
        
        can_proceed, message, error_details = pricing_service.check_comprehensive_limits(
            user_id=user_id,
            operations=operations_to_validate
        )
        
        if not can_proceed:
            logger.error(f"[Pre-flight Validator] Image control blocked for user {user_id}: {message}")
            
            usage_info = error_details.get('usage_info', {}) if error_details else {}
            provider = usage_info.get('provider', 'stability') if usage_info else 'stability'
            
            raise HTTPException(
                status_code=429,
                detail={
                    'error': message,
                    'message': message,
                    'provider': provider,
                    'usage_info': usage_info if usage_info else error_details
                }
            )
        
        logger.info(f"[Pre-flight Validator] ✅ Image control validated for user {user_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Pre-flight Validator] Error validating image control: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                'error': f"Failed to validate image control: {str(e)}",
                'message': f"Failed to validate image control: {str(e)}"
            }
        )


def validate_video_generation_operations(
    pricing_service: PricingService,
    user_id: str
) -> None:
    """
    Validate video generation operation before making API calls.
    
    Args:
        pricing_service: PricingService instance
        user_id: User ID for subscription checking
        
    Returns:
        None - raises HTTPException with 429 status if validation fails
    """
    try:
        operations_to_validate = [
            {
                'provider': APIProvider.VIDEO,
                'tokens_requested': 0,
                'actual_provider_name': 'video',
                'operation_type': 'video_generation'
            }
        ]
        
        can_proceed, message, error_details = pricing_service.check_comprehensive_limits(
            user_id=user_id,
            operations=operations_to_validate
        )
        
        if not can_proceed:
            logger.error(f"[Pre-flight Validator] Video generation blocked for user {user_id}: {message}")
            
            usage_info = error_details.get('usage_info', {}) if error_details else {}
            provider = usage_info.get('provider', 'video') if usage_info else 'video'
            
            raise HTTPException(
                status_code=429,
                detail={
                    'error': message,
                    'message': message,
                    'provider': provider,
                    'usage_info': usage_info if usage_info else error_details
                }
            )
        
        logger.info(f"[Pre-flight Validator] ✅ Video generation validated for user {user_id}")
        # Validation passed - no return needed (function raises HTTPException if validation fails)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Pre-flight Validator] Error validating video generation: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                'error': f"Failed to validate video generation: {str(e)}",
                'message': f"Failed to validate video generation: {str(e)}"
            }
        )


def validate_scene_animation_operation(
    pricing_service: PricingService,
    user_id: str,
) -> None:
    """
    Validate the per-scene animation workflow before API calls.
    """
    try:
        operations_to_validate = [
            {
                'provider': APIProvider.VIDEO,
                'tokens_requested': 0,
                'actual_provider_name': 'wavespeed',
                'operation_type': 'scene_animation',
            }
        ]

        can_proceed, message, error_details = pricing_service.check_comprehensive_limits(
            user_id=user_id,
            operations=operations_to_validate,
        )

        if not can_proceed:
            logger.error(f"[Pre-flight Validator] Scene animation blocked for user {user_id}: {message}")
            usage_info = error_details.get('usage_info', {}) if error_details else {}
            provider = usage_info.get('provider', 'video') if usage_info else 'video'
            raise HTTPException(
                status_code=429,
                detail={
                    'error': message,
                    'message': message,
                    'provider': provider,
                    'usage_info': usage_info if usage_info else error_details,
                }
            )

        logger.info(f"[Pre-flight Validator] ✅ Scene animation validated for user {user_id}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Pre-flight Validator] Error validating scene animation: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                'error': f"Failed to validate scene animation: {str(e)}",
                'message': f"Failed to validate scene animation: {str(e)}",
            },
        )


def validate_calendar_generation_operations(
    pricing_service: PricingService,
    user_id: str,
    gpt_provider: str = "google"
) -> None:
    """
    Validate calendar generation operations before making API calls.
    
    Args:
        pricing_service: PricingService instance
        user_id: User ID for subscription checking
        gpt_provider: GPT provider from env var (defaults to "google")
        
    Returns:
        None - raises HTTPException with 429 status if validation fails
    """
    try:
        # Determine actual provider for LLM calls based on GPT_PROVIDER env var
        gpt_provider_lower = gpt_provider.lower()
        if gpt_provider_lower == "huggingface":
            llm_provider_enum = APIProvider.MISTRAL
            llm_provider_name = "huggingface"
        else:
            llm_provider_enum = APIProvider.GEMINI
            llm_provider_name = "gemini"
            
        # Estimate tokens for 12-step process
        # This is a heavy operation involving multiple steps and analysis
        operations_to_validate = [
            {
                'provider': llm_provider_enum,
                'tokens_requested': 20000, # Conservative estimate for full calendar generation
                'actual_provider_name': llm_provider_name,
                'operation_type': 'calendar_generation'
            }
        ]
        
        logger.info(f"[Pre-flight Validator] 🚀 Validating Calendar Generation for user {user_id}")
        
        can_proceed, message, error_details = pricing_service.check_comprehensive_limits(
            user_id=user_id,
            operations=operations_to_validate
        )
        
        if not can_proceed:
            usage_info = error_details.get('usage_info', {}) if error_details else {}
            provider = usage_info.get('provider', llm_provider_name) if usage_info else llm_provider_name
            
            logger.warning(f"[Pre-flight Validator] Calendar generation blocked for user {user_id}: {message}")
            
            raise HTTPException(
                status_code=429,
                detail={
                    'error': message,
                    'message': message,
                    'provider': provider,
                    'usage_info': usage_info if usage_info else error_details
                }
            )
            
        logger.info(f"[Pre-flight Validator] ✅ Calendar Generation validated for user {user_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Pre-flight Validator] Error validating calendar generation: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                'error': f"Failed to validate calendar generation: {str(e)}",
                'message': f"Failed to validate calendar generation: {str(e)}"
            }
        )