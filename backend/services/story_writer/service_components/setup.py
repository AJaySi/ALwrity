"""Story setup generation helpers."""

from __future__ import annotations

import json
from typing import Any, Dict, List

from fastapi import HTTPException
from loguru import logger

from .base import StoryServiceBase


class StorySetupMixin(StoryServiceBase):
    """Provides story setup generation behaviour."""

    def generate_premise(
        self,
        *,
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
        user_id: str,
    ) -> str:
        """Generate a story premise."""
        persona_prompt = self.build_persona_prompt(
            persona,
            story_setting,
            character_input,
            plot_elements,
            writing_style,
            story_tone,
            narrative_pov,
            audience_age_group,
            content_rating,
            ending_preference,
        )

        parameter_guidance = self._get_parameter_interaction_guidance(
            writing_style, story_tone, audience_age_group, content_rating
        )

        premise_prompt = f"""\
{persona_prompt}

{parameter_guidance}

**TASK: Write a SINGLE, BRIEF premise sentence (1-2 sentences maximum, approximately 20-40 words) for this story.**

The premise MUST:
1. Be written in the specified {writing_style} writing style
   - Interpret and apply this style appropriately for {audience_age_group}
   - Match the language complexity, sentence structure, and narrative approach of this style
2. Match the {story_tone} story tone exactly
   - Express the emotional atmosphere and mood indicated by this tone
   - Ensure the tone is age-appropriate for {audience_age_group}
3. Be appropriate for {audience_age_group} with {content_rating} content rating
   - Use language complexity that matches this audience's reading level
   - Use vocabulary that is understandable to this age group
   - Present concepts that are relatable and explainable to this audience
   - Respect the {content_rating} content rating boundaries
4. Briefly describe the story elements:
   - Setting: {story_setting}
   - Characters: {character_input}
   - Main plot: {plot_elements}
5. Be clear, engaging, and set up the story without telling the whole story
6. Be written from the {narrative_pov} point of view
7. Set up for a {ending_preference} ending

**CRITICAL: This is a PREMISE, not the full story.**
- Keep it to 1-2 sentences maximum (approximately 20-40 words)
- Do NOT write the full story or multiple paragraphs
- Do NOT reveal the resolution or ending
- Focus on the setup: who, where, and what the main challenge/adventure is
- Use ALL story setup parameters to guide your language and content choices
- Tailor every word to the target audience ({audience_age_group}) and writing style ({writing_style})

Write ONLY the premise sentence(s). Do not write anything else.
"""

        try:
            premise = self.generate_with_retry(premise_prompt, user_id=user_id).strip()
            sentences = premise.split(". ")
            if len(sentences) > 2:
                premise = ". ".join(sentences[:2])
                if not premise.endswith("."):
                    premise += "."
            return premise
        except HTTPException:
            raise
        except Exception as exc:
            logger.error(f"Premise Generation Error: {exc}")
            raise RuntimeError(f"Failed to generate premise: {exc}") from exc

    # ------------------------------------------------------------------ #
    # Setup options
    # ------------------------------------------------------------------ #

    def _build_setup_schema(self) -> Dict[str, Any]:
        """Return JSON schema for structured setup options."""
        return {
            "type": "object",
            "properties": {
                "options": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "persona": {"type": "string"},
                            "story_setting": {"type": "string"},
                            "character_input": {"type": "string"},
                            "plot_elements": {"type": "string"},
                            "writing_style": {"type": "string"},
                            "story_tone": {"type": "string"},
                            "narrative_pov": {"type": "string"},
                            "audience_age_group": {"type": "string"},
                            "content_rating": {"type": "string"},
                            "ending_preference": {"type": "string"},
                            "story_length": {"type": "string"},
                            "premise": {"type": "string"},
                            "reasoning": {"type": "string"},
                        },
                        "required": [
                            "persona",
                            "story_setting",
                            "character_input",
                            "plot_elements",
                            "writing_style",
                            "story_tone",
                            "narrative_pov",
                            "audience_age_group",
                            "content_rating",
                            "ending_preference",
                            "story_length",
                            "premise",
                            "reasoning",
                        ],
                    },
                    "minItems": 3,
                    "maxItems": 3,
                }
            },
            "required": ["options"],
        }

    def generate_story_setup_options(
        self,
        *,
        story_idea: str,
        user_id: str,
    ) -> List[Dict[str, Any]]:
        """Generate 3 story setup options from a user's story idea."""

        suggested_writing_styles = ['Formal', 'Casual', 'Poetic', 'Humorous', 'Academic', 'Journalistic', 'Narrative']
        suggested_story_tones = ['Dark', 'Uplifting', 'Suspenseful', 'Whimsical', 'Melancholic', 'Mysterious', 'Romantic', 'Adventurous']
        suggested_narrative_povs = ['First Person', 'Third Person Limited', 'Third Person Omniscient']
        suggested_audience_age_groups = ['Children (5-12)', 'Young Adults (13-17)', 'Adults (18+)', 'All Ages']
        suggested_content_ratings = ['G', 'PG', 'PG-13', 'R']
        suggested_ending_preferences = ['Happy', 'Tragic', 'Cliffhanger', 'Twist', 'Open-ended', 'Bittersweet']

        setup_prompt = f"""\
You are an expert story writer and creative writing assistant. A user has provided the following story idea or information:

{story_idea}

Based on this story idea, generate exactly 3 different, well-thought-out story setup options. Each option should be CREATIVE, PERSONALIZED, and perfectly tailored to the user's specific story idea. 

**CRITICAL - Creative Freedom:**
- You have COMPLETE FREEDOM to craft personalized values that best fit the user's story idea
- Do NOT limit yourself to predefined options - create custom, creative values that perfectly match the story concept
- For example, if the user wants "a story about how stars are made for a 5-year-old", you might create:
  - Writing Style: "Educational Playful" or "Simple Scientific" (not just "Casual" or "Poetic")
  - Story Tone: "Wonder-filled" or "Curious Discovery" (not just "Whimsical" or "Uplifting")
  - Narrative POV: "Second Person (You)" or "Omniscient Narrator as Guide" (not just standard options)
- The goal is to create the PERFECT setup for THIS specific story, not to fit into generic categories

Each option should:
1. Have a unique and creative persona that fits the story idea perfectly
2. Define a compelling story setting that brings the idea to life
3. Describe interesting and engaging characters
4. Include key plot elements that drive the narrative
5. Create CUSTOM, PERSONALIZED values for writing style, story tone, narrative POV, audience age group, content rating, and ending preference that best serve the story idea
6. Select an appropriate story length: "Short (>1000 words)" for brief stories, "Medium (>5000 words)" for standard-length stories, or "Long (>10000 words)" for extended, detailed stories
7. Generate a brief story premise (1-2 sentences, approximately 20-40 words) that summarizes the story concept
8. Provide a brief reasoning (2-3 sentences) explaining why this setup works well for the story idea

**IMPORTANT - Premise Requirements:**
- The premise MUST be age-appropriate for the selected audience_age_group
- For Children (5-12): Use simple, everyday words. Avoid complex vocabulary like "nebular", "ionized", "cosmic", "stellar", "melancholic", "bittersweet"
- The premise MUST match the selected writing_style (e.g., if custom style is "Educational Playful", use playful educational language)
- The premise MUST match the selected story_tone (e.g., if custom tone is "Wonder-filled", create a sense of wonder)
- Keep the premise to 1-2 sentences maximum
- Focus on who, where, and what the main challenge/adventure is

**Suggested Options (for reference only - feel free to create better custom values):**
- Writing Styles (suggestions): {', '.join(suggested_writing_styles)}
- Story Tones (suggestions): {', '.join(suggested_story_tones)}
- Narrative POVs (suggestions): {', '.join(suggested_narrative_povs)}
- Audience Age Groups (suggestions): {', '.join(suggested_audience_age_groups)}
- Content Ratings (suggestions): {', '.join(suggested_content_ratings)}
- Ending Preferences (suggestions): {', '.join(suggested_ending_preferences)}
- Story Lengths: "Short (>1000 words)", "Medium (>5000 words)", "Long (>10000 words)"

**Remember:** These are ONLY suggestions. If a custom value better serves the story idea, CREATE IT!

Return exactly 3 options as a JSON array. Each option must include a "premise" field with the story premise.
"""

        setup_schema = self._build_setup_schema()

        try:
            logger.info(f"[StoryWriter] Generating story setup options for user {user_id}")
            response = self.load_json_response(
                llm_text_gen(prompt=setup_prompt, json_struct=setup_schema, user_id=user_id)
            )

            options = response.get("options", [])
            if len(options) != 3:
                logger.warning(f"[StoryWriter] Expected 3 options but got {len(options)}, correcting count")
                if len(options) < 3:
                    raise ValueError(f"Expected 3 options but got {len(options)}")
                options = options[:3]

            for idx, option in enumerate(options):
                if not option.get("premise") or not option.get("premise", "").strip():
                    logger.info(f"[StoryWriter] Generating premise for option {idx + 1}")
                    try:
                        option["premise"] = self.generate_premise(
                            persona=option.get("persona", ""),
                            story_setting=option.get("story_setting", ""),
                            character_input=option.get("character_input", ""),
                            plot_elements=option.get("plot_elements", ""),
                            writing_style=option.get("writing_style", "Narrative"),
                            story_tone=option.get("story_tone", "Adventurous"),
                            narrative_pov=option.get("narrative_pov", "Third Person Limited"),
                            audience_age_group=option.get("audience_age_group", "All Ages"),
                            content_rating=option.get("content_rating", "G"),
                            ending_preference=option.get("ending_preference", "Happy"),
                            user_id=user_id,
                        )
                    except Exception as exc:  # pragma: no cover - fallback clause
                        logger.warning(f"[StoryWriter] Failed to generate premise for option {idx + 1}: {exc}")
                        option["premise"] = (
                            f"A {option.get('story_setting', 'story')} story featuring "
                            f"{option.get('character_input', 'characters')}."
                        )
                else:
                    premise = option["premise"].strip()
                    sentences = premise.split(". ")
                    if len(sentences) > 2:
                        premise = ". ".join(sentences[:2])
                        if not premise.endswith("."):
                            premise += "."
                    option["premise"] = premise

            logger.info(f"[StoryWriter] Generated {len(options)} story setup options with premises for user {user_id}")
            return options
        except HTTPException:
            raise
        except json.JSONDecodeError as exc:
            logger.error(f"[StoryWriter] Failed to parse JSON response for story setup: {exc}")
            raise RuntimeError(f"Failed to parse story setup options: {exc}") from exc
        except Exception as exc:
            logger.error(f"[StoryWriter] Error generating story setup options: {exc}")
            raise RuntimeError(f"Failed to generate story setup options: {exc}") from exc

