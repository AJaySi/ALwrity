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
        
        This method is optimized to minimize AI calls:
        - For shorts: Reuses scenes if already generated in plan (0 AI calls)
        - For medium/long: Generates scenes + batch enhances (1-3 AI calls total)
        - Custom script: Parses script without AI calls (0 AI calls)
        
        Args:
            video_plan: Video plan from planner service
            user_id: Clerk user ID for subscription checking
            custom_script: Optional custom script to use instead of generating
            
        Returns:
            List of scene dictionaries with narration, visual prompts, timing, etc.
        """
        try:
            duration_type = video_plan.get('duration_type', 'medium')
            logger.info(
                f"[YouTubeSceneBuilder] Building scenes from plan: "
                f"duration={duration_type}, "
                f"sections={len(video_plan.get('content_outline', []))}, "
                f"user={user_id}"
            )
            
            duration_metadata = video_plan.get("duration_metadata", {})
            max_scenes = duration_metadata.get("max_scenes", 10)
            
            # Optimization: Check if scenes already exist in plan (prevents duplicate generation)
            # This can happen if plan was generated with include_scenes=True for shorts
            existing_scenes = video_plan.get("scenes", [])
            if existing_scenes and video_plan.get("_scenes_included"):
                # Scenes already generated in plan - reuse them (0 AI calls)
                logger.info(
                    f"[YouTubeSceneBuilder] ♻️ Reusing {len(existing_scenes)} scenes from plan "
                    f"(duration={duration_type}) - skipping generation to save AI calls"
                )
                scenes = self._normalize_scenes_from_plan(video_plan, duration_metadata)
            # If custom script provided, parse it into scenes (0 AI calls for parsing)
            elif custom_script:
                logger.info(
                    f"[YouTubeSceneBuilder] Parsing custom script for scene generation "
                    f"(0 AI calls required)"
                )
                scenes = self._parse_custom_script(
                    custom_script, video_plan, duration_metadata, user_id
                )
            # For shorts, check if scenes were already generated in plan (optimization)
            elif video_plan.get("_scenes_included") and duration_type == "shorts":
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
        
        scene_generation_prompt = f"""You are a top YouTube scriptwriter specializing in engaging, viral content. Create compelling scenes that captivate viewers and maximize watch time.

**VIDEO PLAN:**
📝 Summary: {video_plan.get('video_summary', '')}
🎯 Goal: {video_plan.get('video_goal', '')}
💡 Key Message: {video_plan.get('key_message', '')}
🎨 Visual Style: {visual_style}
🎭 Tone: {tone}

**🎣 HOOK STRATEGY:**
{hook_strategy}

**📋 CONTENT STRUCTURE:**
{chr(10).join([f"• {section.get('section', '')}: {section.get('description', '')} ({section.get('duration_estimate', 0)}s)" for section in content_outline])}

**🚀 CALL-TO-ACTION:**
{call_to_action}

**⏱️ TIMING CONSTRAINTS:**
• Scene duration: {scene_duration_range[0]}-{scene_duration_range[1]} seconds each
• Total target: {duration_metadata.get('target_seconds', 150)} seconds

**🎬 YOUR MISSION - CREATE VIRAL-WORTHY SCENES:**

Write narration that:
✨ **HOOKS IMMEDIATELY** - First {duration_metadata.get('hook_seconds', 10)}s must GRAB attention
🎭 **TELLS A STORY** - Each scene advances the narrative with emotional engagement
💡 **DELIVERS VALUE** - Provide insights, tips, or "aha!" moments in every scene
🔥 **BUILDS EXCITEMENT** - Use power words, questions, and cliffhangers
👥 **CONNECTS PERSONALLY** - Speak directly to the viewer's needs and desires
⚡ **MAINTAINS PACE** - Vary sentence length for natural rhythm
🎯 **DRIVES ACTION** - Build toward the CTA with increasing urgency

**REQUIRED SCENE ELEMENTS:**
1. **scene_number**: Sequential numbering
2. **title**: Catchy, descriptive title (5-8 words max)
3. **narration**: ENGAGING spoken script with:
   - Conversational language ("you know what I mean?")
   - Rhetorical questions ("Have you ever wondered...?")
   - Power transitions ("But here's the game-changer...")
   - Emotional hooks ("Imagine this...")
   - Action-oriented language ("Let's dive in...")
4. **visual_description**: Cinematic, professional YouTube visuals
5. **duration_estimate**: Realistic speaking time
6. **emphasis**: hook/main_content/transition/cta
7. **visual_cues**: ["dramatic_zoom", "text_overlay", "fast_cuts"]

**🎯 YOUTUBE OPTIMIZATION RULES:**
• **Hook Power**: First 3 seconds = make them stay or lose them
• **Value Density**: Every 10 seconds must deliver new insight
• **Emotional Arc**: Build curiosity → teach → inspire → convert
• **Natural Flow**: Scenes must connect seamlessly
• **CTA Momentum**: Final scene creates irresistible urge to act

**📊 FORMAT AS JSON ARRAY:**
[
  {{
    "scene_number": 1,
    "title": "The Shocking Truth They Hide",
    "narration": "You won't believe what just happened in my latest discovery! I was scrolling through the usual content when BAM - this completely changed everything I thought about [topic]. And get this - it could transform YOUR results too!",
    "visual_description": "Dynamic opening shot with shocking text overlay, fast cuts of social media feeds, energetic music swell, close-up of surprised reaction",
    "duration_estimate": 8,
    "emphasis": "hook",
    "visual_cues": ["shocking_text", "fast_cuts", "music_swell", "reaction_shot"]
  }},
  ...
]

**🔥 SUCCESS CRITERIA:**
✅ First scene hooks in 3 seconds
✅ Each scene delivers 1-2 key insights
✅ Narration feels like talking to a friend
✅ Total story arc creates emotional journey
✅ CTA feels like the natural next step
✅ Scenes fit duration perfectly"""
        
        system_prompt = (
            "You are a master YouTube scriptwriter who creates viral, engaging content that "
            "keeps viewers watching until the end. You understand YouTube algorithm optimization, "
            "emotional storytelling, and creating irresistible hooks that make viewers hit 'like' and 'subscribe'. "
            "Your scripts are conversational, valuable, and conversion-focused."
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

