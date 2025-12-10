"""
YouTube Scene Builder Service

Converts video plans into structured scenes with narration, visual prompts, and timing.
"""

from typing import Dict, Any, Optional, List
from loguru import logger
from fastapi import HTTPException

from services.llm_providers.main_text_generation import llm_text_gen
from services.story_writer.prompt_enhancer_service import PromptEnhancerService
from utils.logger_utils import get_service_logger

logger = get_service_logger("youtube.scene_builder")


class YouTubeSceneBuilderService:
    """Service for building structured video scenes from plans."""
    
    def __init__(self):
        """Initialize the scene builder service."""
        self.prompt_enhancer = PromptEnhancerService()
        logger.info("[YouTubeSceneBuilder] Service initialized")
    
    def build_scenes_from_plan(
        self,
        video_plan: Dict[str, Any],
        user_id: str,
        custom_script: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Build structured scenes from a video plan.
        
        Args:
            video_plan: Video plan from planner service
            user_id: Clerk user ID for subscription checking
            custom_script: Optional custom script to use instead of generating
            
        Returns:
            List of scene dictionaries with narration, visual prompts, timing, etc.
        """
        try:
            logger.info(
                f"[YouTubeSceneBuilder] Building scenes from plan: "
                f"duration={video_plan.get('duration_type')}, "
                f"sections={len(video_plan.get('content_outline', []))}"
            )
            
            duration_metadata = video_plan.get("duration_metadata", {})
            max_scenes = duration_metadata.get("max_scenes", 10)
            
            # If custom script provided, parse it into scenes
            if custom_script:
                scenes = self._parse_custom_script(
                    custom_script, video_plan, duration_metadata, user_id
                )
            # For shorts, check if scenes were already generated in plan (optimization)
            elif video_plan.get("_scenes_included") and video_plan.get("duration_type") == "shorts":
                prebuilt = video_plan.get("scenes") or []
                if prebuilt:
                    logger.info(
                        f"[YouTubeSceneBuilder] Using scenes from optimized plan+scenes call "
                        f"({len(prebuilt)} scenes)"
                    )
                    scenes = self._normalize_scenes_from_plan(video_plan, duration_metadata)
                else:
                    logger.warning(
                        "[YouTubeSceneBuilder] Plan marked _scenes_included but no scenes present; "
                        "regenerating scenes normally."
                    )
                    scenes = self._generate_scenes_from_plan(
                        video_plan, duration_metadata, user_id
                    )
            else:
                # Generate scenes from plan
                scenes = self._generate_scenes_from_plan(
                    video_plan, duration_metadata, user_id
                )
            
            # Limit to max scenes
            if len(scenes) > max_scenes:
                logger.warning(
                    f"[YouTubeSceneBuilder] Truncating {len(scenes)} scenes to {max_scenes}"
                )
                scenes = scenes[:max_scenes]
            
            # Enhance visual prompts efficiently based on duration type
            duration_type = video_plan.get("duration_type", "medium")
            scenes = self._enhance_visual_prompts_batch(
                scenes, video_plan, user_id, duration_type
            )
            
            logger.info(f"[YouTubeSceneBuilder] ✅ Built {len(scenes)} scenes")
            return scenes
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"[YouTubeSceneBuilder] Error building scenes: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to build scenes: {str(e)}"
            )
    
    def _generate_scenes_from_plan(
        self,
        video_plan: Dict[str, Any],
        duration_metadata: Dict[str, Any],
        user_id: str,
    ) -> List[Dict[str, Any]]:
        """Generate scenes from video plan using AI."""
        
        content_outline = video_plan.get("content_outline", [])
        hook_strategy = video_plan.get("hook_strategy", "")
        call_to_action = video_plan.get("call_to_action", "")
        visual_style = video_plan.get("visual_style", "cinematic")
        tone = video_plan.get("tone", "professional")
        
        scene_duration_range = duration_metadata.get("scene_duration_range", (5, 15))
        
        scene_generation_prompt = f"""You are an expert video scriptwriter. Create detailed scenes for a YouTube video based on this plan.

**Video Plan:**
- Summary: {video_plan.get('video_summary', '')}
- Goal: {video_plan.get('video_goal', '')}
- Key Message: {video_plan.get('key_message', '')}
- Visual Style: {visual_style}
- Tone: {tone}

**Hook Strategy:**
{hook_strategy}

**Content Outline:**
{chr(10).join([f"- {section.get('section', '')}: {section.get('description', '')} ({section.get('duration_estimate', 0)}s)" for section in content_outline])}

**Call-to-Action:**
{call_to_action}

**Duration Constraints:**
- Scene duration: {scene_duration_range[0]}-{scene_duration_range[1]} seconds each
- Total target: {duration_metadata.get('target_seconds', 150)} seconds

**Your Task:**
Create detailed scenes that include:
1. Scene number and title
2. Narration text (what will be spoken)
3. Visual description (what viewers will see)
4. Duration estimate
5. Emphasis tags (hook, main_content, transition, cta)

**Format as JSON array:**
[
  {{
    "scene_number": 1,
    "title": "Hook - Attention Grabber",
    "narration": "The spoken text for this scene...",
    "visual_description": "Detailed description of what viewers see...",
    "duration_estimate": 5,
    "emphasis": "hook",
    "visual_cues": ["close-up", "dynamic", "bright"]
  }},
  ...
]

Make sure:
- First scene is a strong hook ({duration_metadata.get('hook_seconds', 10)}s)
- Last scene includes the CTA ({duration_metadata.get('cta_seconds', 10)}s)
- Each scene has clear narration and visual description
- Total duration fits within {duration_metadata.get('target_seconds', 150)} seconds
- Scenes flow naturally from one to the next
"""
        
        system_prompt = (
            "You are an expert video scriptwriter specializing in YouTube content. "
            "Your scenes are engaging, well-paced, and optimized for viewer retention."
        )
        
        response = llm_text_gen(
            prompt=scene_generation_prompt,
            system_prompt=system_prompt,
            user_id=user_id,
            json_struct={
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
        )
        
        # Parse response
        if isinstance(response, list):
            scenes = response
        elif isinstance(response, dict) and "scenes" in response:
            scenes = response["scenes"]
        else:
            import json
            scenes = json.loads(response) if isinstance(response, str) else response
        
        # Normalize scene data
        normalized_scenes = []
        for idx, scene in enumerate(scenes, 1):
            normalized_scenes.append({
                "scene_number": scene.get("scene_number", idx),
                "title": scene.get("title", f"Scene {idx}"),
                "narration": scene.get("narration", ""),
                "visual_description": scene.get("visual_description", ""),
                "duration_estimate": scene.get("duration_estimate", scene_duration_range[0]),
                "emphasis": scene.get("emphasis", "main_content"),
                "visual_cues": scene.get("visual_cues", []),
                "visual_prompt": scene.get("visual_description", ""),  # Initial prompt
            })
        
        return normalized_scenes
    
    def _normalize_scenes_from_plan(
        self,
        video_plan: Dict[str, Any],
        duration_metadata: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Normalize scenes that were generated as part of the plan (optimization for shorts)."""
        scenes = video_plan.get("scenes", [])
        scene_duration_range = duration_metadata.get("scene_duration_range", (2, 8))
        
        normalized_scenes = []
        for idx, scene in enumerate(scenes, 1):
            normalized_scenes.append({
                "scene_number": scene.get("scene_number", idx),
                "title": scene.get("title", f"Scene {idx}"),
                "narration": scene.get("narration", ""),
                "visual_description": scene.get("visual_description", ""),
                "duration_estimate": scene.get("duration_estimate", scene_duration_range[0]),
                "emphasis": scene.get("emphasis", "main_content"),
                "visual_cues": scene.get("visual_cues", []),
                "visual_prompt": scene.get("visual_description", ""),  # Initial prompt
            })
        
        logger.info(
            f"[YouTubeSceneBuilder] ✅ Normalized {len(normalized_scenes)} scenes "
            f"from optimized plan (saved 1 AI call)"
        )
        return normalized_scenes
    
    def _parse_custom_script(
        self,
        custom_script: str,
        video_plan: Dict[str, Any],
        duration_metadata: Dict[str, Any],
        user_id: str,
    ) -> List[Dict[str, Any]]:
        """Parse a custom script into structured scenes."""
        # Simple parsing: split by double newlines or scene markers
        import re
        
        # Try to detect scene markers
        scene_pattern = r'(?:Scene\s+\d+|#\s*\d+\.|^\d+\.)\s*(.+?)(?=(?:Scene\s+\d+|#\s*\d+\.|^\d+\.|$))'
        matches = re.finditer(scene_pattern, custom_script, re.MULTILINE | re.DOTALL)
        
        scenes = []
        for idx, match in enumerate(matches, 1):
            scene_text = match.group(1).strip()
            # Extract narration (first paragraph or before visual markers)
            narration_match = re.search(r'^(.*?)(?:\n\n|Visual:|Image:)', scene_text, re.DOTALL)
            narration = narration_match.group(1).strip() if narration_match else scene_text.split('\n')[0]
            
            # Extract visual description
            visual_match = re.search(r'(?:Visual:|Image:)\s*(.+?)(?:\n\n|$)', scene_text, re.DOTALL)
            visual_description = visual_match.group(1).strip() if visual_match else narration
            
            scenes.append({
                "scene_number": idx,
                "title": f"Scene {idx}",
                "narration": narration,
                "visual_description": visual_description,
                "duration_estimate": duration_metadata.get("scene_duration_range", [5, 15])[0],
                "emphasis": "hook" if idx == 1 else ("cta" if idx == len(list(matches)) else "main_content"),
                "visual_cues": [],
                "visual_prompt": visual_description,
            })
        
        # Fallback: split by paragraphs if no scene markers
        if not scenes:
            paragraphs = [p.strip() for p in custom_script.split('\n\n') if p.strip()]
            for idx, para in enumerate(paragraphs[:duration_metadata.get("max_scenes", 10)], 1):
                scenes.append({
                    "scene_number": idx,
                    "title": f"Scene {idx}",
                    "narration": para,
                    "visual_description": para,
                    "duration_estimate": duration_metadata.get("scene_duration_range", [5, 15])[0],
                    "emphasis": "hook" if idx == 1 else ("cta" if idx == len(paragraphs) else "main_content"),
                    "visual_cues": [],
                    "visual_prompt": para,
                })
        
        return scenes
    
    def _enhance_visual_prompts_batch(
        self,
        scenes: List[Dict[str, Any]],
        video_plan: Dict[str, Any],
        user_id: str,
        duration_type: str,
    ) -> List[Dict[str, Any]]:
        """
        Efficiently enhance visual prompts based on video duration type.
        
        Strategy:
        - Shorts: Skip enhancement (use original descriptions) - 0 AI calls
        - Medium: Batch enhance all scenes in 1 call - 1 AI call
        - Long: Batch enhance in 2 calls (split scenes) - 2 AI calls max
        """
        # For shorts, skip enhancement to save API calls
        if duration_type == "shorts":
            logger.info(
                f"[YouTubeSceneBuilder] Skipping prompt enhancement for shorts "
                f"({len(scenes)} scenes) to save API calls"
            )
            for scene in scenes:
                scene["enhanced_visual_prompt"] = scene.get(
                    "visual_prompt", scene.get("visual_description", "")
                )
            return scenes
        
        # Build story context for prompt enhancer
        story_context = {
            "story_setting": video_plan.get("visual_style", "cinematic"),
            "story_tone": video_plan.get("tone", "professional"),
            "writing_style": video_plan.get("visual_style", "cinematic"),
        }
        
        # Convert scenes to format expected by enhancer
        scene_data_list = [
            {
                "scene_number": scene.get("scene_number", idx + 1),
                "title": scene.get("title", ""),
                "description": scene.get("visual_description", ""),
                "image_prompt": scene.get("visual_prompt", ""),
            }
            for idx, scene in enumerate(scenes)
        ]
        
        # For medium videos, enhance all scenes in one batch call
        if duration_type == "medium":
            logger.info(
                f"[YouTubeSceneBuilder] Batch enhancing {len(scenes)} scenes "
                f"for medium video in 1 AI call"
            )
            try:
                # Use a single batch enhancement call
                enhanced_prompts = self._batch_enhance_prompts(
                    scene_data_list, story_context, user_id
                )
                for idx, scene in enumerate(scenes):
                    scene["enhanced_visual_prompt"] = enhanced_prompts.get(
                        idx, scene.get("visual_prompt", scene.get("visual_description", ""))
                    )
            except Exception as e:
                logger.warning(
                    f"[YouTubeSceneBuilder] Batch enhancement failed: {e}, "
                    f"using original prompts"
                )
                for scene in scenes:
                    scene["enhanced_visual_prompt"] = scene.get(
                        "visual_prompt", scene.get("visual_description", "")
                    )
            return scenes
        
        # For long videos, split into 2 batches to avoid token limits
        if duration_type == "long":
            logger.info(
                f"[YouTubeSceneBuilder] Batch enhancing {len(scenes)} scenes "
                f"for long video in 2 AI calls"
            )
            mid_point = len(scenes) // 2
            batches = [
                scene_data_list[:mid_point],
                scene_data_list[mid_point:],
            ]
            
            all_enhanced = {}
            for batch_idx, batch in enumerate(batches):
                try:
                    enhanced = self._batch_enhance_prompts(
                        batch, story_context, user_id
                    )
                    start_idx = 0 if batch_idx == 0 else mid_point
                    for local_idx, enhanced_prompt in enhanced.items():
                        all_enhanced[start_idx + local_idx] = enhanced_prompt
                except Exception as e:
                    logger.warning(
                        f"[YouTubeSceneBuilder] Batch {batch_idx + 1} enhancement "
                        f"failed: {e}, using original prompts"
                    )
                    start_idx = 0 if batch_idx == 0 else mid_point
                    for local_idx, scene_data in enumerate(batch):
                        all_enhanced[start_idx + local_idx] = scene_data.get(
                            "image_prompt", scene_data.get("description", "")
                        )
            
            for idx, scene in enumerate(scenes):
                scene["enhanced_visual_prompt"] = all_enhanced.get(
                    idx, scene.get("visual_prompt", scene.get("visual_description", ""))
                )
            return scenes
        
        # Fallback: use original prompts
        logger.warning(
            f"[YouTubeSceneBuilder] Unknown duration type '{duration_type}', "
            f"using original prompts"
        )
        for scene in scenes:
            scene["enhanced_visual_prompt"] = scene.get(
                "visual_prompt", scene.get("visual_description", "")
            )
        return scenes
    
    def _batch_enhance_prompts(
        self,
        scene_data_list: List[Dict[str, Any]],
        story_context: Dict[str, Any],
        user_id: str,
    ) -> Dict[int, str]:
        """
        Enhance multiple scene prompts in a single AI call.
        
        Returns:
            Dictionary mapping scene index to enhanced prompt
        """
        try:
            # Build batch enhancement prompt
            scenes_text = "\n\n".join([
                f"Scene {scene.get('scene_number', idx + 1)}: {scene.get('title', '')}\n"
                f"Description: {scene.get('description', '')}\n"
                f"Current Prompt: {scene.get('image_prompt', '')}"
                for idx, scene in enumerate(scene_data_list)
            ])
            
            batch_prompt = f"""You are optimizing visual prompts for AI video generation. Enhance the following scenes to be more detailed and video-optimized.

**Video Style Context:**
- Setting: {story_context.get('story_setting', 'cinematic')}
- Tone: {story_context.get('story_tone', 'professional')}
- Style: {story_context.get('writing_style', 'cinematic')}

**Scenes to Enhance:**
{scenes_text}

**Your Task:**
For each scene, create an enhanced visual prompt (200-300 words) that:
1. Is detailed and specific for video generation
2. Includes camera movements, lighting, composition
3. Maintains consistency with the video style
4. Is optimized for WAN 2.5 text-to-video model

**Format as JSON array with enhanced prompts:**
[
  {{"scene_index": 0, "enhanced_prompt": "detailed enhanced prompt for scene 1..."}},
  {{"scene_index": 1, "enhanced_prompt": "detailed enhanced prompt for scene 2..."}},
  ...
]

Make sure the array length matches the number of scenes provided ({len(scene_data_list)}).
"""
            
            system_prompt = (
                "You are an expert at creating detailed visual prompts for AI video generation. "
                "Your prompts are specific, cinematic, and optimized for video models."
            )
            
            response = llm_text_gen(
                prompt=batch_prompt,
                system_prompt=system_prompt,
                user_id=user_id,
                json_struct={
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "scene_index": {"type": "number"},
                            "enhanced_prompt": {"type": "string"}
                        },
                        "required": ["scene_index", "enhanced_prompt"]
                    }
                }
            )
            
            # Parse response
            if isinstance(response, list):
                enhanced_list = response
            elif isinstance(response, str):
                import json
                enhanced_list = json.loads(response)
            else:
                enhanced_list = response
            
            # Build result dictionary
            result = {}
            for item in enhanced_list:
                idx = item.get("scene_index", 0)
                prompt = item.get("enhanced_prompt", "")
                if prompt:
                    result[idx] = prompt
                else:
                    # Fallback to original
                    original_scene = scene_data_list[idx] if idx < len(scene_data_list) else {}
                    result[idx] = original_scene.get(
                        "image_prompt", original_scene.get("description", "")
                    )
            
            # Fill in any missing scenes with original prompts
            for idx in range(len(scene_data_list)):
                if idx not in result:
                    original_scene = scene_data_list[idx]
                    result[idx] = original_scene.get(
                        "image_prompt", original_scene.get("description", "")
                    )
            
            logger.info(
                f"[YouTubeSceneBuilder] ✅ Batch enhanced {len(result)} prompts "
                f"in 1 AI call"
            )
            return result
            
        except Exception as e:
            logger.error(
                f"[YouTubeSceneBuilder] Batch enhancement failed: {e}",
                exc_info=True
            )
            # Return original prompts as fallback
            return {
                idx: scene.get("image_prompt", scene.get("description", ""))
                for idx, scene in enumerate(scene_data_list)
            }

