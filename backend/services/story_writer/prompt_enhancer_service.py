"""
Prompt Enhancement Service for HunyuanVideo Generation

Uses AI to deeply understand story context and generate optimized
HunyuanVideo prompts following best practices with 7 components.
"""

from typing import Dict, Any, List, Optional
from loguru import logger
from fastapi import HTTPException
from services.llm_providers.main_text_generation import llm_text_gen


class PromptEnhancerService:
    """Service for generating HunyuanVideo-optimized prompts from story context."""
    
    def __init__(self):
        """Initialize the prompt enhancer service."""
        logger.info("[PromptEnhancer] Service initialized")
    
    def enhance_scene_prompt(
        self,
        current_scene: Dict[str, Any],
        story_context: Dict[str, Any],
        all_scenes: List[Dict[str, Any]],
        user_id: str
    ) -> str:
        """
        Generate a HunyuanVideo-optimized prompt for a scene using two-stage AI analysis.
        
        Args:
            current_scene: Scene data for the scene being processed
            story_context: Complete story context (setup, premise, outline, story text)
            all_scenes: List of all scenes for consistency analysis
            user_id: Clerk user ID for subscription checking
        
        Returns:
            str: Optimized HunyuanVideo prompt (300-500 words) with 7 components
        """
        try:
            logger.info(f"[PromptEnhancer] Enhancing prompt for scene {current_scene.get('scene_number', 'unknown')}")
            
            # Stage 1: Deep story context analysis
            story_insights = self._analyze_story_context(
                current_scene=current_scene,
                story_context=story_context,
                all_scenes=all_scenes,
                user_id=user_id
            )
            
            # Stage 2: Generate optimized HunyuanVideo prompt
            optimized_prompt = self._generate_hunyuan_prompt(
                current_scene=current_scene,
                story_context=story_context,
                story_insights=story_insights,
                all_scenes=all_scenes,
                user_id=user_id
            )
            
            logger.info(f"[PromptEnhancer] Generated prompt length: {len(optimized_prompt)} characters")
            return optimized_prompt
            
        except HTTPException as http_err:
            # Propagate subscription limit errors (429) to frontend for modal display
            # Only fallback for other HTTP errors (5xx, etc.)
            if http_err.status_code == 429:
                error_msg = self._extract_error_message(http_err)
                logger.warning(f"[PromptEnhancer] Subscription limit exceeded (HTTP 429): {error_msg}")
                # Re-raise to propagate to frontend for subscription modal
                raise
            else:
                # For other HTTP errors, log and fallback
                error_msg = self._extract_error_message(http_err)
                logger.error(f"[PromptEnhancer] Error enhancing prompt (HTTP {http_err.status_code}): {error_msg}", exc_info=True)
                return self._generate_fallback_prompt(current_scene, story_context)
        except Exception as e:
            logger.error(f"[PromptEnhancer] Error enhancing prompt: {str(e)}", exc_info=True)
            # Fallback to basic prompt if enhancement fails
            return self._generate_fallback_prompt(current_scene, story_context)
    
    def _analyze_story_context(
        self,
        current_scene: Dict[str, Any],
        story_context: Dict[str, Any],
        all_scenes: List[Dict[str, Any]],
        user_id: str
    ) -> str:
        """
        Stage 1: Use AI to analyze complete story context and extract insights.
        
        Returns:
            str: Story insights as JSON string for use in prompt generation
        """
        # Build comprehensive context for analysis
        analysis_prompt = f"""You are analyzing a complete story to extract key insights for AI video generation.

**STORY SETUP:**
- Persona: {story_context.get('persona', 'N/A')}
- Setting: {story_context.get('story_setting', 'N/A')}
- Characters: {story_context.get('characters', 'N/A')}
- Plot Elements: {story_context.get('plot_elements', 'N/A')}
- Writing Style: {story_context.get('writing_style', 'N/A')}
- Tone: {story_context.get('story_tone', 'N/A')}
- Narrative POV: {story_context.get('narrative_pov', 'N/A')}
- Audience: {story_context.get('audience_age_group', 'N/A')}
- Content Rating: {story_context.get('content_rating', 'N/A')}

**STORY PREMISE:**
{story_context.get('premise', 'N/A')}

**STORY CONTENT:**
{story_context.get('story_content', 'N/A')[:2000]}...

**ALL SCENES OVERVIEW:**
"""
        # Add summary of all scenes
        for idx, scene in enumerate(all_scenes, 1):
            scene_num = scene.get('scene_number', idx)
            analysis_prompt += f"\nScene {scene_num}: {scene.get('title', 'Untitled')}"
            analysis_prompt += f"\n  Description: {scene.get('description', '')[:150]}..."
            analysis_prompt += f"\n  Image Prompt: {scene.get('image_prompt', '')[:150]}..."
            if scene.get('character_descriptions'):
                chars = ', '.join(scene.get('character_descriptions', [])[:3])
                analysis_prompt += f"\n  Characters: {chars}"
            analysis_prompt += "\n"
        
        analysis_prompt += f"""
**CURRENT SCENE FOR VIDEO GENERATION:**
Scene {current_scene.get('scene_number', 'N/A')}: {current_scene.get('title', 'Untitled')}
Description: {current_scene.get('description', '')}
Image Prompt: {current_scene.get('image_prompt', '')}
Key Events: {', '.join(current_scene.get('key_events', [])[:5])}
Character Descriptions: {', '.join(current_scene.get('character_descriptions', [])[:5])}

**YOUR TASK:**
Analyze this story and extract key insights for video generation. Focus on:
1. Narrative arc and position of current scene within it
2. Character consistency (how characters appear across scenes)
3. Visual style patterns from image prompts
4. Tone and atmosphere progression
5. Key themes and motifs
6. Visual narrative flow
7. Camera and composition needs for this specific scene

Provide your analysis as structured insights that can guide prompt generation.
"""
        
        try:
            insights = llm_text_gen(
                prompt=analysis_prompt,
                system_prompt="You are an expert story analyst specializing in visual narrative and cinematic storytelling. Provide detailed, actionable insights for video generation.",
                user_id=user_id
            )
            logger.debug(f"[PromptEnhancer] Story insights extracted: {insights[:200]}...")
            return insights
        except HTTPException as http_err:
            # Propagate subscription limit errors (429) to frontend
            if http_err.status_code == 429:
                error_msg = self._extract_error_message(http_err)
                logger.warning(f"[PromptEnhancer] Subscription limit exceeded during story analysis (HTTP 429): {error_msg}")
                # Re-raise to propagate to frontend for subscription modal
                raise
            else:
                # For other HTTP errors, log and fallback
                error_msg = self._extract_error_message(http_err)
                logger.warning(f"[PromptEnhancer] Story analysis failed (HTTP {http_err.status_code}): {error_msg}, using basic context")
                return "Standard narrative flow with consistent character presentation"
        except Exception as e:
            logger.warning(f"[PromptEnhancer] Story analysis failed, using basic context: {str(e)}")
            return "Standard narrative flow with consistent character presentation"
    
    def _generate_hunyuan_prompt(
        self,
        current_scene: Dict[str, Any],
        story_context: Dict[str, Any],
        story_insights: str,
        all_scenes: List[Dict[str, Any]],
        user_id: str
    ) -> str:
        """
        Stage 2: Generate scene-specific HunyuanVideo prompt with all 7 components.
        
        Returns:
            str: Complete HunyuanVideo prompt (300-500 words)
        """
        # Collect character descriptions across all scenes for consistency
        all_characters = {}
        for scene in all_scenes:
            for char_desc in scene.get('character_descriptions', []):
                if char_desc and char_desc not in all_characters:
                    all_characters[char_desc] = scene.get('scene_number', 0)
        
        # Collect image prompts for visual style reference
        image_prompts = [scene.get('image_prompt', '') for scene in all_scenes if scene.get('image_prompt')]
        
        # Determine scene position in narrative arc
        current_scene_num = current_scene.get('scene_number', 0)
        total_scenes = len(all_scenes)
        scene_position = "beginning" if current_scene_num <= total_scenes // 3 else ("middle" if current_scene_num <= 2 * total_scenes // 3 else "climax")
        
        prompt_generation_request = f"""Generate a professional HunyuanVideo prompt for this story scene.

**STORY INSIGHTS (from deep analysis):**
{story_insights}

**STORY SETUP:**
- Setting: {story_context.get('story_setting', 'N/A')}
- Tone: {story_context.get('story_tone', 'N/A')}
- Style: {story_context.get('writing_style', 'N/A')}
- Audience: {story_context.get('audience_age_group', 'N/A')}

**VISUAL STYLE REFERENCE (from generated images):**
{chr(10).join([f"- {prompt[:100]}..." for prompt in image_prompts[:3]])}

**CHARACTER CONSISTENCY (across all scenes):**
{chr(10).join([f"- {char}" for char in list(all_characters.keys())[:5]])}

**CURRENT SCENE DETAILS:**
- Scene {current_scene.get('scene_number', 'N/A')} of {total_scenes} (narrative position: {scene_position})
- Title: {current_scene.get('title', 'Untitled')}
- Description: {current_scene.get('description', '')}
- Image Prompt: {current_scene.get('image_prompt', '')}
- Key Events: {', '.join(current_scene.get('key_events', [])[:5])}
- Characters in scene: {', '.join(current_scene.get('character_descriptions', [])[:5])}
- Audio Narration: {current_scene.get('audio_narration', '')[:200]}

**REQUIREMENTS:**
Create a comprehensive HunyuanVideo prompt (300-500 words) following the 7-component structure:

1. **SUBJECT**: Clearly define the main focus - characters, objects, or action. Include character descriptions that match the visual style from image prompts and maintain consistency across scenes.

2. **SCENE**: Describe the environment and setting. Ensure it matches the story_setting and aligns with the visual style established in previous scenes.

3. **MOTION**: Detail the specific actions and movements. Reference key_events and ensure motion fits the narrative flow and story_insights about the scene's position in the arc.

4. **CAMERA MOVEMENT**: Specify cinematic camera work appropriate for this moment in the story. Consider the narrative position ({scene_position}) - use establishing shots for beginning, dynamic shots for climax.

5. **ATMOSPHERE**: Set the emotional tone. This should reflect the story_tone but also consider where we are in the narrative arc based on story_insights.

6. **LIGHTING**: Define lighting that matches the visual style from image prompts and supports the atmosphere. Ensure consistency with the established visual aesthetic.

7. **SHOT COMPOSITION**: Describe framing and composition that serves the visual narrative. Consider the story's visual style and ensure it flows naturally with the overall story.

Write the prompt as a flowing, detailed description (not a list) that integrates all 7 components naturally. Make it vivid, cinematic, and consistent with the story's established visual and narrative style. The prompt should be between 300-500 words.
"""
        
        try:
            optimized_prompt = llm_text_gen(
                prompt=prompt_generation_request,
                system_prompt="You are an expert video prompt engineer specializing in HunyuanVideo text-to-video generation. Create detailed, cinematic prompts that follow best practices and ensure high-quality video output.",
                user_id=user_id
            )
            
            # Clean up and validate prompt length
            optimized_prompt = optimized_prompt.strip()
            word_count = len(optimized_prompt.split())
            
            if word_count < 200:
                logger.warning(f"[PromptEnhancer] Generated prompt is too short ({word_count} words), enhancing...")
                # Add more detail if too short
                optimized_prompt += self._add_cinematic_details(current_scene, story_context)
            elif word_count > 600:
                logger.warning(f"[PromptEnhancer] Generated prompt is too long ({word_count} words), trimming...")
                # Trim if too long (keep first ~500 words)
                words = optimized_prompt.split()
                optimized_prompt = ' '.join(words[:500])
            
            logger.info(f"[PromptEnhancer] Generated prompt: {len(optimized_prompt.split())} words")
            return optimized_prompt
            
        except HTTPException as http_err:
            # Propagate subscription limit errors (429) to frontend
            if http_err.status_code == 429:
                error_msg = self._extract_error_message(http_err)
                logger.warning(f"[PromptEnhancer] Subscription limit exceeded during prompt generation (HTTP 429): {error_msg}")
                # Re-raise to propagate to frontend for subscription modal
                raise
            else:
                # For other HTTP errors, log and fallback
                error_msg = self._extract_error_message(http_err)
                logger.error(f"[PromptEnhancer] Prompt generation failed (HTTP {http_err.status_code}): {error_msg}", exc_info=True)
                return self._generate_fallback_prompt(current_scene, story_context)
        except Exception as e:
            logger.error(f"[PromptEnhancer] Prompt generation failed: {str(e)}", exc_info=True)
            return self._generate_fallback_prompt(current_scene, story_context)
    
    def _add_cinematic_details(
        self,
        current_scene: Dict[str, Any],
        story_context: Dict[str, Any]
    ) -> str:
        """Add cinematic details to enhance a too-short prompt."""
        return f"""

The scene unfolds with careful attention to visual storytelling. The {story_context.get('story_setting', 'environment')} serves as more than background - it actively participates in the narrative. Lighting and composition work together to emphasize the emotional weight of this moment, with camera movements that guide the viewer's attention naturally through the space. Every element - from the way light falls to the positioning of characters - contributes to the overall narrative impact.
"""
    
    def _extract_error_message(self, http_err: HTTPException) -> str:
        """
        Extract meaningful error message from HTTPException.
        
        Handles both dict-based details (from subscription limit errors) and string details.
        """
        if isinstance(http_err.detail, dict):
            # For subscription limit errors, extract the 'message' or 'error' field
            return http_err.detail.get('message') or http_err.detail.get('error') or str(http_err.detail)
        elif isinstance(http_err.detail, str):
            return http_err.detail
        else:
            return str(http_err.detail)
    
    def _generate_fallback_prompt(
        self,
        current_scene: Dict[str, Any],
        story_context: Dict[str, Any]
    ) -> str:
        """Generate a basic fallback prompt if AI enhancement fails."""
        scene_title = current_scene.get('title', 'Untitled Scene')
        scene_desc = current_scene.get('description', '')
        image_prompt = current_scene.get('image_prompt', '')
        setting = story_context.get('story_setting', 'the scene')
        tone = story_context.get('story_tone', 'engaging')
        
        return f"""A cinematic scene titled "{scene_title}" set in {setting}. {scene_desc[:200]}. 
The scene features {', '.join(current_scene.get('character_descriptions', [])[:2]) if current_scene.get('character_descriptions') else 'the main characters'}.
Visual style follows: {image_prompt[:150]}. 
The {tone} atmosphere is enhanced by natural lighting and dynamic camera movements that follow the action. 
Shot composition emphasizes the narrative importance of this moment, with careful framing that draws attention to key elements. 
The scene maintains visual consistency with previous moments while advancing the story's visual narrative."""


def enhance_scene_prompt_for_video(
    current_scene: Dict[str, Any],
    story_context: Dict[str, Any],
    all_scenes: List[Dict[str, Any]],
    user_id: str
) -> str:
    """
    Convenience function to enhance a scene prompt for HunyuanVideo generation.
    
    Args:
        current_scene: Scene data for the scene being processed
        story_context: Complete story context dictionary
        all_scenes: List of all scenes for consistency
        user_id: Clerk user ID for subscription checking
    
    Returns:
        str: Optimized HunyuanVideo prompt
    """
    service = PromptEnhancerService()
    return service.enhance_scene_prompt(current_scene, story_context, all_scenes, user_id)

