"""Core shared functionality for Story Writer service components."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from fastapi import HTTPException
from loguru import logger

from services.llm_providers.main_text_generation import llm_text_gen


class StoryServiceBase:
    """Base class providing shared helpers for story writer operations."""

    guidelines: str = """\
Writing Guidelines:

Delve deeper. Lose yourself in the world you're building. Unleash vivid
descriptions to paint the scenes in your reader's mind.
Develop your characters — let their motivations, fears, and complexities unfold naturally.
Weave in the threads of your outline, but don't feel constrained by it.
Allow your story to surprise you as you write. Use rich imagery, sensory details, and
evocative language to bring the setting, characters, and events to life.
Introduce elements subtly that can blossom into complex subplots, relationships,
or worldbuilding details later in the story.
Keep things intriguing but not fully resolved.
Avoid boxing the story into a corner too early.
Plant the seeds of subplots or potential character arc shifts that can be expanded later.

IMPORTANT: Respect the story length target. Write with appropriate detail and pacing
to reach the target word count, but do NOT exceed it. Once you've reached the target
length and provided satisfying closure, conclude the story by writing IAMDONE.
"""

    # ------------------------------------------------------------------ #
    # LLM Utilities
    # ------------------------------------------------------------------ #

    def generate_with_retry(
        self,
        prompt: str,
        *,
        system_prompt: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> str:
        """Generate content using llm_text_gen with retry handling and subscription support."""
        if not user_id:
            raise RuntimeError("user_id is required for subscription checking")

        try:
            return llm_text_gen(prompt=prompt, system_prompt=system_prompt, user_id=user_id)
        except HTTPException:
            raise
        except Exception as exc:
            logger.error(f"Error generating content: {exc}")
            raise RuntimeError(f"Failed to generate content: {exc}") from exc

    # ------------------------------------------------------------------ #
    # Prompt helpers
    # ------------------------------------------------------------------ #

    def build_persona_prompt(
        self,
        persona: str,
        story_setting: str,
        character_input: str,
        plot_elements: str,
        writing_style: str,
        story_tone: str,
        narrative_pov: str,
        audience_age_group: str,
        content_rating: str,
        ending_preference: str,
    ) -> str:
        """Build the persona prompt with all story parameters."""
        return f"""{persona}

**STORY SETUP CONTEXT:**

**Setting:**
{story_setting}
- Use this specific setting throughout the story
- Incorporate setting details naturally into scenes and descriptions
- Ensure the setting is clearly established and consistent

**Characters:**
{character_input}
- Use these specific characters in the story
- Develop these characters according to their descriptions
- Maintain character consistency across all scenes
- Create character arcs that align with the plot elements

**Plot Elements:**
{plot_elements}
- Incorporate these plot elements into the story structure
- Address each plot element in relevant scenes
- Build connections between plot elements logically
- Ensure the ending addresses the main plot elements

**Writing Style:**
{writing_style}
- This writing style should be reflected in EVERY aspect of the story
- The language, sentence structure, and narrative approach must match this style exactly
- If this is a custom or combined style, interpret it in the context of the audience age group
- Adapt the style's complexity to match {audience_age_group}

**Story Tone:**
{story_tone}
- This tone must be maintained consistently throughout the entire story
- The emotional atmosphere, mood, and overall feeling must match this tone
- If this is a custom or combined tone, interpret it age-appropriately for {audience_age_group}
- Ensure the tone is suitable for {content_rating} content rating

**Narrative Point of View:**
{narrative_pov}
- Use this perspective consistently throughout the story
- Maintain the chosen perspective in all narration
- Apply the perspective appropriately for {audience_age_group}

**Target Audience:**
{audience_age_group}
- ALL content must be age-appropriate for this audience
- Language complexity, vocabulary, sentence length, and themes must match this age group
- Concepts must be understandable and relatable to this audience
- Adjust all story elements (style, tone, plot) to be appropriate for this age group

**Content Rating:**
{content_rating}
- All content must stay within these content boundaries
- Themes, language, and subject matter must respect this rating
- Ensure the writing style and tone are compatible with this rating

**Ending Preference:**
{ending_preference}
- The story should build toward this type of ending
- All plot development should lead naturally to this ending style
- Create expectations that align with this ending preference
- Ensure the ending is appropriate for {audience_age_group} and {content_rating}

**CRITICAL INSTRUCTIONS:**
- Use ALL of the above story setup parameters to guide your writing
- The writing style, tone, narrative POV, audience age group, and content rating are NOT optional - they are REQUIRED constraints
- Every word, sentence, and description must align with these parameters
- When parameters interact (e.g., style + age group, tone + content rating), ensure they work together harmoniously
- Tailor the language complexity, vocabulary, and concepts to the specified audience age group
- Maintain consistency with the specified writing style and tone throughout
- Ensure all content is appropriate for the specified content rating
- Build the narrative toward the specified ending preference
- Use the setting, characters, and plot elements provided to create a coherent, engaging story

Make sure the story is engaging, well-crafted, and perfectly tailored to ALL of the specified parameters above.
"""

    def _get_parameter_interaction_guidance(
        self,
        writing_style: str,
        story_tone: str,
        audience_age_group: str,
        content_rating: str,
    ) -> str:
        """Generate guidance for interpreting custom/combined parameter values and their interactions."""
        guidance = "**PARAMETER INTERACTION GUIDANCE:**\n\n"

        style_words = writing_style.lower().split()
        if len(style_words) > 1:
            guidance += f"**Writing Style Analysis:** The style '{writing_style}' appears to combine multiple approaches:\n"
            for word in style_words:
                guidance += f"- '{word.title()}': Interpret this aspect in the context of {audience_age_group}\n"
            guidance += (
                "Combine all aspects naturally. For example, if 'Educational Playful':\n"
                f"  → Use playful, engaging language to teach concepts naturally\n"
                f"  → Make learning fun and interactive for {audience_age_group}\n"
                "  → Combine educational content with fun, magical elements\n\n"
            )
        else:
            guidance += f"**Writing Style:** '{writing_style}'\n"
            guidance += f"- Interpret this style appropriately for {audience_age_group}\n"
            guidance += "- Adapt the style's complexity to match the audience's reading level\n\n"

        tone_words = story_tone.lower().split()
        if len(tone_words) > 1:
            guidance += f"**Story Tone Analysis:** The tone '{story_tone}' combines multiple emotional qualities:\n"
            for word in tone_words:
                guidance += f"- '{word.title()}': Express this emotion in an age-appropriate way for {audience_age_group}\n"
            guidance += (
                "Blend these emotions throughout the story. For example, if 'Educational Whimsical':\n"
                "  → Use whimsical, playful language to convey educational concepts\n"
                "  → Make the tone both informative and magical\n"
                f"  → Combine wonder and learning in an age-appropriate way for {audience_age_group}\n\n"
            )
        else:
            guidance += f"**Story Tone:** '{story_tone}'\n"
            guidance += f"- Interpret this tone age-appropriately for {audience_age_group}\n"
            guidance += f"- Ensure the tone is suitable for {content_rating} content rating\n\n"

        guidance += "**PARAMETER INTERACTION EXAMPLES:**\n\n"

        if "Children (5-12)" in audience_age_group:
            guidance += f"- When writing_style is '{writing_style}' AND audience_age_group is 'Children (5-12)':\n"
            guidance += "  → Simplify the style's complexity while maintaining its essence\n"
            guidance += "  → Use age-appropriate vocabulary and sentence structure\n"
            guidance += "  → Make the style engaging and accessible for children\n\n"

        if "Children (5-12)" in audience_age_group and "dark" in story_tone.lower():
            guidance += f"- When story_tone is '{story_tone}' AND audience_age_group is 'Children (5-12)':\n"
            guidance += "  → Interpret 'dark' as mysterious and adventurous, not scary or frightening\n"
            guidance += "  → Use shadows, secrets, and puzzles rather than fear or horror\n"
            guidance += "  → Maintain a sense of wonder and excitement\n"
            guidance += "  → Keep it thrilling but age-appropriate\n\n"

        guidance += f"- When writing_style is '{writing_style}' AND story_tone is '{story_tone}':\n"
        guidance += "  → Combine the style and tone naturally\n"
        guidance += "  → Use the style to express the tone effectively\n"
        guidance += f"  → Ensure both work together harmoniously for {audience_age_group}\n\n"

        guidance += f"- When content_rating is '{content_rating}':\n"
        guidance += "  → Ensure the writing style and tone respect these content boundaries\n"
        guidance += "  → Adjust language, themes, and subject matter to fit the rating\n"
        guidance += f"  → Maintain age-appropriateness for {audience_age_group}\n\n"

        guidance += "**PARAMETER CONFLICT RESOLUTION:**\n"
        guidance += "If parameters seem to conflict, prioritize in this order:\n"
        guidance += "1. Audience age group appropriateness (safety and comprehension) - HIGHEST PRIORITY\n"
        guidance += "2. Content rating compliance (content boundaries)\n"
        guidance += "3. Writing style and tone (creative expression)\n"
        guidance += "4. Other parameters (narrative POV, ending preference)\n\n"
        guidance += "Always ensure that ALL parameters work together to create appropriate, engaging content.\n"

        return guidance

    # ------------------------------------------------------------------ #
    # Outline helpers shared across modules
    # ------------------------------------------------------------------ #

    def _format_outline_for_prompt(self, outline: Any) -> str:
        """Format outline (structured or text) for use in prompts."""
        if isinstance(outline, list):
            outline_text = "\n".join(
                [
                    f"Scene {scene.get('scene_number', idx + 1)}: {scene.get('title', 'Untitled')}\n"
                    f"  Description: {scene.get('description', '')}\n"
                    f"  Key Events: {', '.join(scene.get('key_events', []))}"
                    for idx, scene in enumerate(outline)
                ]
            )
            return outline_text
        return str(outline)

    def _parse_text_outline(self, outline_prompt: str, user_id: str) -> List[Dict[str, Any]]:
        """Fallback method to parse text outline if JSON parsing fails."""
        outline_text = self.generate_with_retry(outline_prompt, user_id=user_id)

        lines = outline_text.strip().split("\n")
        scenes: List[Dict[str, Any]] = []
        current_scene: Optional[Dict[str, Any]] = None

        for line in lines:
            cleaned = line.strip()
            if not cleaned:
                continue

            if cleaned[0].isdigit() or cleaned.startswith("Scene") or cleaned.startswith("Chapter"):
                if current_scene:
                    scenes.append(current_scene)

                scene_number = len(scenes) + 1
                title = cleaned.replace(f"{scene_number}.", "").replace("Scene", "").replace("Chapter", "").strip()
                current_scene = {
                    "scene_number": scene_number,
                    "title": title or f"Scene {scene_number}",
                    "description": "",
                    "image_prompt": f"A scene from the story: {title}",
                    "audio_narration": "",
                    "character_descriptions": [],
                    "key_events": [],
                }
                continue

            if current_scene:
                if current_scene["description"]:
                    current_scene["description"] += " " + cleaned
                else:
                    current_scene["description"] = cleaned

                if current_scene["image_prompt"].startswith("A scene from the story"):
                    current_scene["image_prompt"] = f"A detailed visual representation of: {current_scene['description'][:200]}"
                if not current_scene["audio_narration"]:
                    current_scene["audio_narration"] = (
                        current_scene["description"][:150] + "..."
                        if len(current_scene["description"]) > 150
                        else current_scene["description"]
                    )

        if current_scene:
            scenes.append(current_scene)

        if not scenes:
            scenes.append(
                {
                    "scene_number": 1,
                    "title": "Story Outline",
                    "description": outline_text.strip(),
                    "image_prompt": f"A scene from the story: {outline_text[:200]}",
                    "audio_narration": outline_text[:150] + "..." if len(outline_text) > 150 else outline_text,
                    "character_descriptions": [],
                    "key_events": [],
                }
            )

        logger.info(f"[StoryWriter] Parsed {len(scenes)} scenes from text outline")
        return scenes

    def _get_story_length_guidance(self, story_length: str) -> tuple[int, int]:
        """Return word count guidance based on story length."""
        story_length_lower = story_length.lower()
        if "short" in story_length_lower or "1000" in story_length_lower:
            return (1000, 0)
        if "long" in story_length_lower or "10000" in story_length_lower:
            return (3000, 2500)
        return (2000, 1500)

    @staticmethod
    def load_json_response(response_text: Any) -> Dict[str, Any]:
        """Normalize responses from llm_text_gen (dict or json string)."""
        if isinstance(response_text, dict):
            return response_text
        if isinstance(response_text, str):
            return json.loads(response_text)
        raise ValueError(f"Unexpected response type: {type(response_text)}")

