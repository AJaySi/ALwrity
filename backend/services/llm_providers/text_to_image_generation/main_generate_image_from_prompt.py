#########################################################
#
# This module will generate images for the blogs using APIs
# from Dall-E and other free resources. Given a prompt, the
# images will be stored in local directory.
# Required: openai API key.
#
#########################################################

# imports
import os
import sys
import datetime
import streamlit as st

import openai  # OpenAI Python library to make API calls
from loguru import logger
from utils.logger_utils import get_service_logger

# Use service-specific logger to avoid conflicts
logger = get_service_logger("text_to_image_generation")

#from .gen_dali2_images
from .gen_dali3_images import generate_dalle3_images
from .gen_stabl_diff_img import generate_stable_diffusion_image
from ..text_generation.main_text_generation import llm_text_gen
from .gen_gemini_images import generate_gemini_image

def generate_image(user_prompt, title=None, description=None, tags=None, content=None, aspect_ratio="16:9"):
    """
    The generation API endpoint creates an image based on a text prompt.

    Required inputs:
    prompt (str): A text description of the desired image(s). The maximum length is 1000 characters.

    Optional inputs:
    --> image_engine: dalle2, dalle3, stable diffusion are supported.
    --> num_images (int): The number of images to generate. Must be between 1 and 10. Defaults to 1.
    --> size (str): The size of the generated images. Must be one of "256x256", "512x512", or "1024x1024". 
    Smaller images are faster. Defaults to "1024x1024".
    -->response_format (str): The format in which the generated images are returned. 
    Must be one of "url" or "b64_json". Defaults to "url".
    --> user (str): A unique identifier representing your end-user, which will help OpenAI to monitor and detect abuse.
    --> aspect_ratio (str): The aspect ratio for the generated image. Must be one of "16:9", "4:3", or "1:1". Defaults to "16:9".
    """
    # FIXME: Need to remove default value to match sidebar input.
    image_engine = 'Gemini-AI'
    image_stored_at = None

    if user_prompt:
        try:
            # Use enhanced prompt generator with all available parameters
            img_prompt = generate_enhanced_img_prompt(user_prompt, title, description, tags, content)
            
            # Add aspect ratio to the prompt
            if aspect_ratio:
                img_prompt += f"\n\nAspect ratio: {aspect_ratio}"
            
            if 'Dalle3' in image_engine:
                logger.info(f"Calling Dalle3 text-to-image with prompt: {img_prompt}")
                image_stored_at = generate_dalle3_images(img_prompt)
            elif 'Stability-AI' in image_engine:
                logger.info(f"Calling Stable diffusion text-to-image with prompt: \n{img_prompt}")
                image_stored_at = generate_stable_diffusion_image(img_prompt)
            elif 'Gemini-AI' in image_engine:
                logger.info(f"Calling Gemini text-to-image with prompt: \n{img_prompt}")
                image_stored_at = generate_gemini_image(img_prompt, aspect_ratio=aspect_ratio)
            return image_stored_at
        except Exception as err:
            logger.error(f"Failed to generate Image: {err}")
            st.warning(f"Failed to generate Image: {err}")
    else:
        logger.error("Skipping Image creation, No prompt provided.")


def generate_img_prompt(user_prompt):
    """
    Given prompt, this functions generated a prompt for image generation.
    """
    prompt = f"""
        As an expert prompt generator for AI text to image models and artist, I will provide you with 'user text' for creating images.
        Your task is to create a prompt for a highly relevant image from given 'user text'.
        \n
        Choose from various art styles, utilize light & shadow effects etc.
        Make sure to avoid common image generation mistakes.
        Reply with only one answer, no descrition and in plaintext.
        Make sure your prompt is detailed and creative descriptions that will inspire unique and interesting images from the AI. 
        
        \n\nuser text:  
        '''{user_prompt}'''"""

    response = llm_text_gen(prompt)
    return response


def generate_enhanced_img_prompt(user_prompt, title=None, description=None, tags=None, content=None):
    """
    Given user prompt and additional context (title, description, tags, content),
    this function generates an enhanced prompt for better image generation.
    
    Args:
        user_prompt (str): Base prompt from the user
        title (str, optional): Blog title or content title
        description (str, optional): Blog or content description/summary
        tags (list, optional): List of tags related to the content
        content (str, optional): Actual content or excerpt
        
    Returns:
        str: Enhanced prompt for image generation
    """
    # Start with the base prompt
    context_parts = [user_prompt]
    
    # Add relevant context if available
    if title:
        context_parts.append(f"Title: {title}")
    
    if description:
        context_parts.append(f"Description: {description}")
    
    if tags and len(tags) > 0:
        tag_text = ", ".join(tags[:5])  # Limit to 5 tags to avoid too much noise
        context_parts.append(f"Tags: {tag_text}")
    
    # Create a combined context
    combined_context = "\n".join(context_parts)
    
    # Add some content excerpt if available (limited to avoid token limits)
    content_excerpt = ""
    if content:
        # Just use the first few hundred characters as excerpt
        content_excerpt = content[:300] + "..." if len(content) > 300 else content
    
    # Create the prompt for LLM
    prompt = f"""
        As an expert prompt engineer for AI image generation models, create a detailed, creative prompt
        for generating a high-quality, relevant image based on the following context:
        
        {combined_context}
        
        Additional content excerpt:
        {content_excerpt}
        
        Your task is to:
        1. Analyze the context and content to understand the main theme and subject
        2. Create a rich, detailed prompt for image generation (50-75 words)
        3. Include specific visual details, art style, mood, lighting, composition
        4. Make sure the prompt is highly relevant to the original context
        5. Avoid prohibited content or anything that violates image generation guidelines
        
        Reply with ONLY the final prompt. No explanations or other text.
    """
    
    # Generate the enhanced prompt
    try:
        enhanced_prompt = llm_text_gen(prompt)
        logger.info(f"Generated enhanced image prompt: {enhanced_prompt[:100]}...")
        return enhanced_prompt
    except Exception as e:
        logger.error(f"Error generating enhanced prompt: {e}")
        # Fall back to the simple prompt generation if enhanced fails
        return generate_img_prompt(user_prompt)
