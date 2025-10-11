"""Main Text Generation Service for ALwrity Backend.

This service provides the main LLM text generation functionality,
migrated from the legacy lib/gpt_providers/text_generation/main_text_generation.py
"""

import os
import json
from typing import Optional, Dict, Any
from loguru import logger
from ..api_key_manager import APIKeyManager

from .openai_provider import openai_chatgpt
from .gemini_provider import gemini_text_response, gemini_structured_json_response
from .anthropic_provider import anthropic_text_response
from .deepseek_provider import deepseek_text_response
from .ollama_provider import ollama_text_response, ollama_structured_json_response, check_ollama_availability
from .smart_model_selector import get_model_selector, TaskType

def llm_text_gen(prompt: str, system_prompt: Optional[str] = None, json_struct: Optional[Dict[str, Any]] = None, 
                 task_type: Optional[str] = None, priority: str = "balanced") -> str:
    """
    Generate text using Language Model (LLM) based on the provided prompt.
    
    Args:
        prompt (str): The prompt to generate text from.
        system_prompt (str, optional): Custom system prompt to use instead of the default one.
        json_struct (dict, optional): JSON schema structure for structured responses.
        task_type (str, optional): Type of task for smart model selection (analysis, reasoning, complex, coding, creative).
        priority (str): Selection priority - "speed", "quality", "cost", or "balanced".
        
    Returns:
        str: Generated text based on the prompt.
    """
    try:
        logger.info("[llm_text_gen] Starting text generation")
        logger.debug(f"[llm_text_gen] Prompt length: {len(prompt)} characters")
        
        # Initialize API key manager and reload keys from .env file
        api_key_manager = APIKeyManager()
        api_key_manager.load_api_keys()  # Force reload from .env file
        
        # Debug: Log loaded API keys
        logger.debug(f"[llm_text_gen] Loaded API keys: {api_key_manager.get_all_keys()}")
        
        # Set default blog characteristics (used in system prompt regardless of path)
        blog_tone = "Professional"
        blog_demographic = "Professional"
        blog_type = "Informational"
        blog_language = "English"
        blog_output_format = "markdown"
        blog_length = 2000
        
        # Use smart model selection if task_type is provided
        if task_type:
            try:
                model_selector = get_model_selector()
                
                # Convert string task_type to TaskType enum
                if isinstance(task_type, str):
                    try:
                        task_enum = TaskType(task_type.lower())
                    except ValueError:
                        # If not a valid enum, try to infer from prompt
                        task_enum = model_selector.get_task_type_from_prompt(prompt, system_prompt or "")
                else:
                    task_enum = model_selector.get_task_type_from_prompt(prompt, system_prompt or "")
                
                # Get available providers
                available_providers = []
                if api_key_manager.get_api_key("openai"):
                    available_providers.append("openai")
                if api_key_manager.get_api_key("gemini"):
                    available_providers.append("google")
                if api_key_manager.get_api_key("anthropic"):
                    available_providers.append("anthropic")
                if api_key_manager.get_api_key("deepseek"):
                    available_providers.append("deepseek")
                if api_key_manager.get_api_key("ollama"):
                    available_providers.append("ollama")
                
                if available_providers:
                    # Use smart selection
                    selected_provider, selected_model = model_selector.select_model_for_task(
                        task_enum, available_providers, priority=priority
                    )
                    gpt_provider = selected_provider
                    model = selected_model
                    logger.info(f"[llm_text_gen] Smart selection: {gpt_provider}:{model} for task {task_enum.value}")
                else:
                    raise RuntimeError("No API keys found")
                    
            except Exception as e:
                logger.warning(f"[llm_text_gen] Smart selection failed, using fallback: {str(e)}")
                # Fall back to original logic
                task_type = None
        
        if not task_type:
            # Original provider selection logic as fallback
            # Set default values for LLM parameters
            gpt_provider = "google"  # Default to Google Gemini
            model = "gemini-2.0-flash-001"
            temperature = 0.7
            max_tokens = 4000
            top_p = 0.9
            n = 1
            fp = 16
            frequency_penalty = 0.0
            presence_penalty = 0.0
            
            # Try to get provider from environment or config
            try:
                # Check which providers have API keys available
                available_providers = []
                if api_key_manager.get_api_key("openai"):
                    available_providers.append("openai")
                if api_key_manager.get_api_key("gemini"):
                    available_providers.append("google")
                if api_key_manager.get_api_key("anthropic"):
                    available_providers.append("anthropic")
                if api_key_manager.get_api_key("deepseek"):
                    available_providers.append("deepseek")
                if api_key_manager.get_api_key("ollama"):  # Ollama endpoint check
                    available_providers.append("ollama")
                
                # Prefer Google Gemini if available, then Ollama for free local AI, then others
                if "google" in available_providers:
                    gpt_provider = "google"
                    model = "gemini-2.0-flash-001"
                elif "ollama" in available_providers:
                    gpt_provider = "ollama"
                    model = "llama3.1:8b"  # Default reasoning model
                elif available_providers:
                    gpt_provider = available_providers[0]
                    if gpt_provider == "openai":
                        model = "gpt-4o"
                    elif gpt_provider == "anthropic":
                        model = "claude-3-5-sonnet-20241022"
                    elif gpt_provider == "deepseek":
                        model = "deepseek-chat"
                else:
                    logger.error("[llm_text_gen] No API keys found. Structured mock responses are disabled.")
                    raise RuntimeError("No LLM API keys configured. Configure provider API keys to enable AI responses.")
                    
                logger.debug(f"[llm_text_gen] Using provider: {gpt_provider}, model: {model}")
                
            except Exception as err:
                logger.warning(f"[llm_text_gen] Error determining provider, using defaults: {err}")
                gpt_provider = "google"
                model = "gemini-2.0-flash-001"
        
        # Set common parameters regardless of selection method
        temperature = temperature if 'temperature' in locals() else 0.7
        max_tokens = max_tokens if 'max_tokens' in locals() else 4000
        top_p = top_p if 'top_p' in locals() else 0.9
        n = n if 'n' in locals() else 1
        fp = fp if 'fp' in locals() else 16

        # Construct the system prompt if not provided
        if system_prompt is None:
            system_instructions = f"""You are a highly skilled content writer with a knack for creating engaging and informative content. 
                Your expertise spans various writing styles and formats.

                Writing Style Guidelines:
                - Tone: {blog_tone}
                - Target Audience: {blog_demographic}
                - Content Type: {blog_type}
                - Language: {blog_language}
                - Output Format: {blog_output_format}
                - Target Length: {blog_length} words

                Please provide responses that are:
                - Well-structured and easy to read
                - Engaging and informative
                - Tailored to the specified tone and audience
                - Professional yet accessible
                - Optimized for the target content type
            """
        else:
            system_instructions = system_prompt

        # Generate response based on provider
        try:
            if gpt_provider == "openai":
                return openai_chatgpt(
                    prompt=prompt,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    top_p=top_p,
                    n=n,
                    fp=fp,
                    system_prompt=system_instructions
                )
            elif gpt_provider == "google":
                if json_struct:
                    return gemini_structured_json_response(
                        prompt=prompt,
                        schema=json_struct,
                        temperature=temperature,
                        top_p=top_p,
                        top_k=n,
                        max_tokens=max_tokens,
                        system_prompt=system_instructions
                    )
                else:
                    return gemini_text_response(
                        prompt=prompt,
                        temperature=temperature,
                        top_p=top_p,
                        n=n,
                        max_tokens=max_tokens,
                        system_prompt=system_instructions
                    )
            elif gpt_provider == "anthropic":
                return anthropic_text_response(
                    prompt=prompt,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    system_prompt=system_instructions
                )
            elif gpt_provider == "deepseek":
                return deepseek_text_response(
                    prompt=prompt,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    system_prompt=system_instructions
                )
            elif gpt_provider == "ollama":
                if json_struct:
                    return ollama_structured_json_response(
                        prompt=prompt,
                        schema=json_struct,
                        model=model,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        system_prompt=system_instructions,
                        task_type="reasoning"  # Default task type
                    )
                else:
                    return ollama_text_response(
                        prompt=prompt,
                        model=model,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        system_prompt=system_instructions,
                        task_type="reasoning"  # Default task type
                    )
            else:
                logger.error(f"[llm_text_gen] Unknown provider: {gpt_provider}")
                raise RuntimeError("Unknown LLM provider.")
        except Exception as provider_error:
            logger.error(f"[llm_text_gen] Provider {gpt_provider} failed: {str(provider_error)}")
            # Try to fallback to another provider
            fallback_providers = ["ollama", "openai", "anthropic", "deepseek"]
            for fallback_provider in fallback_providers:
                if fallback_provider in available_providers and fallback_provider != gpt_provider:
                    try:
                        logger.info(f"[llm_text_gen] Trying fallback provider: {fallback_provider}")
                        if fallback_provider == "ollama":
                            if json_struct:
                                return ollama_structured_json_response(
                                    prompt=prompt,
                                    schema=json_struct,
                                    temperature=temperature,
                                    max_tokens=max_tokens,
                                    system_prompt=system_instructions,
                                    task_type="reasoning"
                                )
                            else:
                                return ollama_text_response(
                                    prompt=prompt,
                                    temperature=temperature,
                                    max_tokens=max_tokens,
                                    system_prompt=system_instructions,
                                    task_type="reasoning"
                                )
                        elif fallback_provider == "openai":
                            return openai_chatgpt(
                                prompt=prompt,
                                model="gpt-4o",
                                temperature=temperature,
                                max_tokens=max_tokens,
                                top_p=top_p,
                                n=n,
                                fp=fp,
                                system_prompt=system_instructions
                            )
                        elif fallback_provider == "anthropic":
                            return anthropic_text_response(
                                prompt=prompt,
                                model="claude-3-5-sonnet-20241022",
                                temperature=temperature,
                                max_tokens=max_tokens,
                                system_prompt=system_instructions
                            )
                        elif fallback_provider == "deepseek":
                            return deepseek_text_response(
                                prompt=prompt,
                                model="deepseek-chat",
                                temperature=temperature,
                                max_tokens=max_tokens,
                                system_prompt=system_instructions
                            )
                    except Exception as fallback_error:
                        logger.error(f"[llm_text_gen] Fallback provider {fallback_provider} also failed: {str(fallback_error)}")
                        continue
            
            # If all providers fail, raise an error (no mock)
            logger.error("[llm_text_gen] All providers failed. Structured mock responses are disabled.")
            raise RuntimeError("All LLM providers failed to generate a response.")

    except Exception as e:
        logger.error(f"[llm_text_gen] Error during text generation: {str(e)}")
        raise

def check_gpt_provider(gpt_provider: str) -> bool:
    """Check if the specified GPT provider is supported."""
    supported_providers = ["openai", "google", "anthropic", "deepseek", "ollama"]
    return gpt_provider in supported_providers

def get_api_key(gpt_provider: str) -> Optional[str]:
    """Get API key for the specified provider."""
    try:
        api_key_manager = APIKeyManager()
        provider_mapping = {
            "openai": "openai",
            "google": "gemini",
            "anthropic": "anthropic",
            "deepseek": "deepseek",
            "ollama": "ollama"
        }
        
        mapped_provider = provider_mapping.get(gpt_provider, gpt_provider)
        return api_key_manager.get_api_key(mapped_provider)
    except Exception as e:
        logger.error(f"[get_api_key] Error getting API key for {gpt_provider}: {str(e)}")
        return None

# Convenience functions for task-specific generation
def llm_analysis_gen(prompt: str, system_prompt: Optional[str] = None, json_struct: Optional[Dict[str, Any]] = None) -> str:
    """Generate text optimized for analysis tasks (fast, efficient models)."""
    return llm_text_gen(prompt, system_prompt, json_struct, task_type="analysis", priority="speed")

def llm_reasoning_gen(prompt: str, system_prompt: Optional[str] = None, json_struct: Optional[Dict[str, Any]] = None) -> str:
    """Generate text optimized for general reasoning tasks (balanced models)."""
    return llm_text_gen(prompt, system_prompt, json_struct, task_type="reasoning", priority="balanced")

def llm_creative_gen(prompt: str, system_prompt: Optional[str] = None, json_struct: Optional[Dict[str, Any]] = None) -> str:
    """Generate text optimized for creative tasks (quality-focused models)."""
    return llm_text_gen(prompt, system_prompt, json_struct, task_type="creative", priority="quality")

def llm_coding_gen(prompt: str, system_prompt: Optional[str] = None, json_struct: Optional[Dict[str, Any]] = None) -> str:
    """Generate text optimized for coding tasks (code-specialized models)."""
    return llm_text_gen(prompt, system_prompt, json_struct, task_type="coding", priority="quality")

def llm_complex_gen(prompt: str, system_prompt: Optional[str] = None, json_struct: Optional[Dict[str, Any]] = None) -> str:
    """Generate text optimized for complex tasks (high-performance models)."""
    return llm_text_gen(prompt, system_prompt, json_struct, task_type="complex", priority="quality")

def llm_seo_analysis_gen(prompt: str, system_prompt: Optional[str] = None, json_struct: Optional[Dict[str, Any]] = None) -> str:
    """Generate text optimized for SEO analysis tasks (fast, analytical models)."""
    return llm_text_gen(prompt, system_prompt, json_struct, task_type="seo_analysis", priority="speed")

def llm_cost_optimized_gen(prompt: str, system_prompt: Optional[str] = None, json_struct: Optional[Dict[str, Any]] = None) -> str:
    """Generate text with cost optimization priority (prefer free/local models)."""
    return llm_text_gen(prompt, system_prompt, json_struct, task_type="reasoning", priority="cost")