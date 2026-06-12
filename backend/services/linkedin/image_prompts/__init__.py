"""
LinkedIn Image Prompts Package

This package provides AI-powered image prompt generation for LinkedIn content
using the provider-agnostic llm_text_gen gateway. It creates three distinct
prompt styles optimized for professional business image generation.
"""

from .linkedin_prompt_generator import LinkedInPromptGenerator

__all__ = [
    'LinkedInPromptGenerator'
]

# Version information
__version__ = "1.0.0"
__author__ = "Alwrity Team"
__description__ = "LinkedIn AI Image Prompt Generation Services"
