"""
YouTube Video Planner Service

Generates video plans, outlines, and insights using AI with persona integration.
"""

from typing import Dict, Any, Optional, List
from loguru import logger
from fastapi import HTTPException

from services.llm_providers.main_text_generation import llm_text_gen
from utils.logger_utils import get_service_logger

logger = get_service_logger("youtube.planner")


class YouTubePlannerService:
    """Service for planning YouTube videos with AI assistance."""
    
    def __init__(self):
        """Initialize the planner service."""
        logger.info("[YouTubePlanner] Service initialized")
    
    def generate_video_plan(
        self,
        user_idea: str,
        duration_type: str,  # "shorts", "medium", "long"
        persona_data: Optional[Dict[str, Any]] = None,
        reference_image_description: Optional[str] = None,
        source_content_id: Optional[str] = None,  # For blog/story conversion
        source_content_type: Optional[str] = None,  # "blog", "story"
        user_id: str = None,
        include_scenes: bool = False,  # For shorts: combine plan + scenes in one call
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive video plan from user input.
        
        Args:
            user_idea: User's video idea or topic
            duration_type: "shorts" (≤60s), "medium" (1-4min), "long" (4-10min)
            persona_data: Optional persona data for tone/style
            reference_image_description: Optional description of reference image
            source_content_id: Optional ID of source content (blog/story)
            source_content_type: Type of source content
            user_id: Clerk user ID for subscription checking
            
        Returns:
            Dictionary with video plan, outline, insights, and metadata
        """
        try:
            logger.info(
                f"[YouTubePlanner] Generating plan: idea={user_idea[:50]}..., "
                f"duration={duration_type}, user={user_id}"
            )
            
            # Build persona context
            persona_context = self._build_persona_context(persona_data)
            
            # Build duration context
            duration_context = self._get_duration_context(duration_type)
            
            # Build source content context if provided
            source_context = ""
            if source_content_id and source_content_type:
                source_context = f"""
**Source Content:**
- Type: {source_content_type}
- ID: {source_content_id}
- Note: This video should be based on the existing {source_content_type} content.
"""
            
            # Build reference image context
            image_context = ""
            if reference_image_description:
                image_context = f"""
**Reference Image:**
{reference_image_description}
- Use this as visual inspiration for the video
"""
            
            # Generate comprehensive video plan
            planning_prompt = f"""You are an expert YouTube content strategist. Create a comprehensive video plan based on the user's idea.

**User's Video Idea:**
{user_idea}

**Video Duration Type:**
{duration_type} ({duration_context['description']})

**Duration Guidelines:**
- Target length: {duration_context['target_seconds']} seconds
- Hook duration: {duration_context['hook_seconds']} seconds
- Main content: {duration_context['main_seconds']} seconds
- CTA duration: {duration_context['cta_seconds']} seconds
- Maximum scenes: {duration_context['max_scenes']} (for shorts, keep 2-4 scenes total)

{persona_context}

{source_context}

{image_context}

**Your Task:**
Create a detailed video plan that includes:

1. **Video Summary**: A 2-3 sentence overview of what the video will cover
2. **Target Audience**: Who this video is for
3. **Video Goal**: Primary objective (educate, entertain, sell, inspire, etc.)
4. **Key Message**: The main takeaway viewers should remember
5. **Hook Strategy**: Attention-grabbing opening (first {duration_context['hook_seconds']} seconds)
6. **Content Outline**: High-level structure with 3-5 main sections
7. **Call-to-Action**: Clear CTA that fits the video goal
8. **Visual Style**: Recommended visual approach (cinematic, tutorial, vlog, etc.)
9. **Tone**: Recommended tone (professional, casual, energetic, etc.)
10. **SEO Keywords**: 5-7 relevant keywords for YouTube SEO

**Format your response as JSON:**
{{
  "video_summary": "...",
  "target_audience": "...",
  "video_goal": "...",
  "key_message": "...",
  "hook_strategy": "...",
  "content_outline": [
    {{"section": "Section 1", "description": "...", "duration_estimate": 30}},
    {{"section": "Section 2", "description": "...", "duration_estimate": 45}}
  ],
  "call_to_action": "...",
  "visual_style": "...",
  "tone": "...",
  "seo_keywords": ["keyword1", "keyword2", ...]
}}

Make sure the content outline fits within the {duration_type} duration constraints.
"""
            
            system_prompt = (
                "You are an expert YouTube content strategist specializing in creating "
                "engaging, well-structured video plans. Your plans are data-driven, "
                "audience-focused, and optimized for YouTube's algorithm."
            )
            
            # For shorts, combine plan + scenes in one call to save API calls
            if include_scenes and duration_type == "shorts":
                planning_prompt += f"""

**IMPORTANT: Since this is a SHORTS video, also generate the complete scene breakdown in the same response.**

**Additional Task - Generate Detailed Scenes:**
Create detailed scenes (up to {duration_context['max_scenes']} scenes) that include:
1. Scene number and title
2. Narration text (what will be spoken) - keep it concise for shorts
3. Visual description (what viewers will see)
4. Duration estimate (2-8 seconds each)
5. Emphasis tags (hook, main_content, transition, cta)

**Scene Format:**
Each scene should be detailed enough for video generation. Total duration must fit within {duration_context['target_seconds']} seconds.

**Update JSON structure to include "scenes" array:**
Add a "scenes" field with the complete scene breakdown.
"""
                
                json_struct = {
                    "type": "object",
                    "properties": {
                        "video_summary": {"type": "string"},
                        "target_audience": {"type": "string"},
                        "video_goal": {"type": "string"},
                        "key_message": {"type": "string"},
                        "hook_strategy": {"type": "string"},
                        "content_outline": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "section": {"type": "string"},
                                    "description": {"type": "string"},
                                    "duration_estimate": {"type": "number"}
                                }
                            }
                        },
                        "call_to_action": {"type": "string"},
                        "visual_style": {"type": "string"},
                        "tone": {"type": "string"},
                        "seo_keywords": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "scenes": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "scene_number": {"type": "number"},
                                    "title": {"type": "string"},
                                    "narration": {"type": "string"},
                                    "visual_description": {"type": "string"},
                                    "duration_estimate": {"type": "number"},
                                    "emphasis": {"type": "string"},
                                    "visual_cues": {
                                        "type": "array",
                                        "items": {"type": "string"}
                                    }
                                },
                                "required": [
                                    "scene_number", "title", "narration", "visual_description",
                                    "duration_estimate", "emphasis"
                                ]
                            }
                        }
                    },
                    "required": [
                        "video_summary", "target_audience", "video_goal", "key_message",
                        "hook_strategy", "content_outline", "call_to_action",
                        "visual_style", "tone", "seo_keywords", "scenes"
                    ]
                }
            else:
                json_struct = {
                    "type": "object",
                    "properties": {
                        "video_summary": {"type": "string"},
                        "target_audience": {"type": "string"},
                        "video_goal": {"type": "string"},
                        "key_message": {"type": "string"},
                        "hook_strategy": {"type": "string"},
                        "content_outline": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "section": {"type": "string"},
                                    "description": {"type": "string"},
                                    "duration_estimate": {"type": "number"}
                                }
                            }
                        },
                        "call_to_action": {"type": "string"},
                        "visual_style": {"type": "string"},
                        "tone": {"type": "string"},
                        "seo_keywords": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    },
                    "required": [
                        "video_summary", "target_audience", "video_goal", "key_message",
                        "hook_strategy", "content_outline", "call_to_action",
                        "visual_style", "tone", "seo_keywords"
                    ]
                }
            
            # Generate plan using LLM
            response = llm_text_gen(
                prompt=planning_prompt,
                system_prompt=system_prompt,
                user_id=user_id,
                json_struct=json_struct
            )
            
            # Parse response (handle both dict and JSON string)
            if isinstance(response, dict):
                plan_data = response
            else:
                import json
                plan_data = json.loads(response)
            
            # Add metadata
            plan_data["duration_type"] = duration_type
            plan_data["duration_metadata"] = duration_context
            plan_data["user_idea"] = user_idea
            
            # If scenes were included, mark them for scene builder
            if include_scenes and duration_type == "shorts" and "scenes" in plan_data:
                plan_data["_scenes_included"] = True
                logger.info(
                    f"[YouTubePlanner] ✅ Plan + {len(plan_data.get('scenes', []))} scenes "
                    f"generated in 1 AI call (optimized for shorts)"
                )
            else:
                if include_scenes and duration_type == "shorts":
                    # LLM did not return scenes; downstream will regenerate
                    plan_data["_scenes_included"] = False
                    logger.warning(
                        "[YouTubePlanner] Shorts optimization requested but no scenes returned; "
                        "scene builder will generate scenes separately."
                    )
                logger.info(f"[YouTubePlanner] ✅ Plan generated successfully")
            
            return plan_data
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"[YouTubePlanner] Error generating plan: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate video plan: {str(e)}"
            )
    
    def _build_persona_context(self, persona_data: Optional[Dict[str, Any]]) -> str:
        """Build persona context string for prompts."""
        if not persona_data:
            return """
**Persona Context:**
- Using default professional tone
- No specific persona constraints
"""
        
        core_persona = persona_data.get("core_persona", {})
        tone = core_persona.get("tone", "professional")
        voice = core_persona.get("voice_characteristics", {})
        
        return f"""
**Persona Context:**
- Tone: {tone}
- Voice Style: {voice.get('style', 'professional')}
- Communication Style: {voice.get('communication_style', 'clear and direct')}
- Brand Values: {core_persona.get('core_belief', 'value-driven content')}
- Use this persona to guide the video's tone, style, and messaging approach.
"""
    
    def _get_duration_context(self, duration_type: str) -> Dict[str, Any]:
        """Get duration-specific context and constraints."""
        contexts = {
            "shorts": {
                "description": "YouTube Shorts (15-60 seconds)",
                "target_seconds": 30,
                "hook_seconds": 3,
                "main_seconds": 24,
                "cta_seconds": 3,
                # Keep scenes tight for shorts to control cost and pacing
                "max_scenes": 4,
                "scene_duration_range": (2, 8)
            },
            "medium": {
                "description": "Medium-length video (1-4 minutes)",
                "target_seconds": 150,  # 2.5 minutes
                "hook_seconds": 10,
                "main_seconds": 130,
                "cta_seconds": 10,
                "max_scenes": 12,
                "scene_duration_range": (5, 15)
            },
            "long": {
                "description": "Long-form video (4-10 minutes)",
                "target_seconds": 420,  # 7 minutes
                "hook_seconds": 15,
                "main_seconds": 380,
                "cta_seconds": 25,
                "max_scenes": 20,
                "scene_duration_range": (10, 30)
            }
        }
        
        return contexts.get(duration_type, contexts["medium"])

