"""
Response Processor - Handles AI response processing and retry logic.

Processes AI responses, handles retries, and converts data to proper formats.
"""

from typing import Dict, Any, List
import asyncio
from loguru import logger

from models.blog_models import BlogOutlineSection


class ResponseProcessor:
    """Handles AI response processing, retry logic, and data conversion."""
    
    def __init__(self):
        """Initialize the response processor."""
        pass
    
    async def generate_with_retry(self, prompt: str, schema: Dict[str, Any], task_id: str = None) -> Dict[str, Any]:
        """Generate outline with retry logic for API failures."""
        from services.llm_providers.gemini_provider import gemini_structured_json_response
        from api.blog_writer.task_manager import task_manager
        
        max_retries = 2  # Conservative retry for expensive API calls
        retry_delay = 5  # 5 second delay between retries
        
        for attempt in range(max_retries + 1):
            try:
                if task_id:
                    await task_manager.update_progress(task_id, f"🤖 Calling Gemini API for outline generation (attempt {attempt + 1}/{max_retries + 1})...")
                
                outline_data = gemini_structured_json_response(
                    prompt=prompt,
                    schema=schema,
                    temperature=0.3,
                    max_tokens=6000  # Increased further to avoid truncation
                )
                
                # Log response for debugging
                logger.info(f"Gemini response received: {type(outline_data)}")
                
                # Check for errors in the response
                if isinstance(outline_data, dict) and 'error' in outline_data:
                    error_msg = str(outline_data['error'])
                    if "503" in error_msg and "overloaded" in error_msg and attempt < max_retries:
                        if task_id:
                            await task_manager.update_progress(task_id, f"⚠️ AI service overloaded, retrying in {retry_delay} seconds...")
                        logger.warning(f"Gemini API overloaded, retrying in {retry_delay} seconds (attempt {attempt + 1}/{max_retries + 1})")
                        await asyncio.sleep(retry_delay)
                        continue
                    elif "No valid structured response content found" in error_msg and attempt < max_retries:
                        if task_id:
                            await task_manager.update_progress(task_id, f"⚠️ Invalid response format, retrying in {retry_delay} seconds...")
                        logger.warning(f"Gemini response parsing failed, retrying in {retry_delay} seconds (attempt {attempt + 1}/{max_retries + 1})")
                        await asyncio.sleep(retry_delay)
                        continue
                    else:
                        logger.error(f"Gemini structured response error: {outline_data['error']}")
                        raise ValueError(f"AI outline generation failed: {outline_data['error']}")
                
                # Validate required fields
                if not isinstance(outline_data, dict) or 'outline' not in outline_data or not isinstance(outline_data['outline'], list):
                    if attempt < max_retries:
                        if task_id:
                            await task_manager.update_progress(task_id, f"⚠️ Invalid response structure, retrying in {retry_delay} seconds...")
                        logger.warning(f"Invalid response structure, retrying in {retry_delay} seconds (attempt {attempt + 1}/{max_retries + 1})")
                        await asyncio.sleep(retry_delay)
                        continue
                    else:
                        raise ValueError("Invalid outline structure in Gemini response")
                
                # If we get here, the response is valid
                return outline_data
                
            except Exception as e:
                error_str = str(e)
                if ("503" in error_str or "overloaded" in error_str) and attempt < max_retries:
                    if task_id:
                        await task_manager.update_progress(task_id, f"⚠️ AI service error, retrying in {retry_delay} seconds...")
                    logger.warning(f"Gemini API error, retrying in {retry_delay} seconds (attempt {attempt + 1}/{max_retries + 1}): {error_str}")
                    await asyncio.sleep(retry_delay)
                    continue
                else:
                    logger.error(f"Outline generation failed after {attempt + 1} attempts: {error_str}")
                    raise ValueError(f"AI outline generation failed: {error_str}")
    
    def convert_to_sections(self, outline_data: Dict[str, Any], sources: List) -> List[BlogOutlineSection]:
        """Convert outline data to BlogOutlineSection objects."""
        outline_sections = []
        for i, section_data in enumerate(outline_data.get('outline', [])):
            if not isinstance(section_data, dict) or 'heading' not in section_data:
                continue
                
            section = BlogOutlineSection(
                id=f"s{i+1}",
                heading=section_data.get('heading', f'Section {i+1}'),
                subheadings=section_data.get('subheadings', []),
                key_points=section_data.get('key_points', []),
                references=[],  # Will be populated by intelligent mapping
                target_words=section_data.get('target_words', 200),
                keywords=section_data.get('keywords', [])
            )
            outline_sections.append(section)
        
        return outline_sections
