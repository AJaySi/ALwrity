"""Story setup generation helpers."""

from __future__ import annotations

import json
from typing import Any, Dict, List

from fastapi import HTTPException
from loguru import logger

from services.llm_providers.main_text_generation import llm_text_gen

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
                    "minItems": 1,
                    "maxItems": 1,
                }
            },
            "required": ["options"],
        }

    def _build_idea_enhance_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "suggestions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "idea": {"type": "string"},
                            "whats_missing": {"type": "string"},
                            "why_choose": {"type": "string"},
                        },
                        "required": ["idea", "whats_missing", "why_choose"],
                    },
                    "minItems": 3,
                    "maxItems": 3,
                }
            },
            "required": ["suggestions"],
        }

    def generate_story_setup_options(
        self,
        *,
        story_idea: str,
        story_mode: str | None,
        story_template: str | None,
        brand_context: Dict[str, Any] | None,
        user_id: str,
    ) -> List[Dict[str, Any]]:
        """Generate a single story setup option from a user's story idea."""

        suggested_writing_styles = ['Formal', 'Casual', 'Poetic', 'Humorous', 'Academic', 'Journalistic', 'Narrative']
        suggested_story_tones = ['Dark', 'Uplifting', 'Suspenseful', 'Whimsical', 'Melancholic', 'Mysterious', 'Romantic', 'Adventurous']
        suggested_narrative_povs = ['First Person', 'Third Person Limited', 'Third Person Omniscient']
        suggested_audience_age_groups = ['Children (5-12)', 'Young Adults (13-17)', 'Adults (18+)', 'All Ages']
        suggested_content_ratings = ['G', 'PG', 'PG-13', 'R']
        suggested_ending_preferences = ['Happy', 'Tragic', 'Cliffhanger', 'Twist', 'Open-ended', 'Bittersweet']

        mode_label = None
        if story_mode == "marketing":
            mode_label = "Non-fiction marketing story (brand or product campaign)"
        elif story_mode == "pure":
            mode_label = "Fiction story"

        template_label = None
        if story_template == "product_story":
            template_label = "Product Story"
        elif story_template == "brand_manifesto":
            template_label = "Brand Manifesto"
        elif story_template == "founder_story":
            template_label = "Founder Story"
        elif story_template == "customer_story":
            template_label = "Customer Story"
        elif story_template == "short_fiction":
            template_label = "Short Fiction"
        elif story_template == "long_fiction":
            template_label = "Long Fiction"
        elif story_template == "anime_fiction":
            template_label = "Anime Fiction"
        elif story_template == "experimental_fiction":
            template_label = "Experimental Fiction"

        brand_name = None
        writing_tone = None
        audience_description = None
        if isinstance(brand_context, dict):
            brand_name = brand_context.get("brand_name")
            writing_tone = brand_context.get("writing_tone")
            target_audience = brand_context.get("target_audience")
            if isinstance(target_audience, dict):
                audience_description = target_audience.get("description") or target_audience.get("summary")
            elif isinstance(target_audience, str):
                audience_description = target_audience

        setup_prompt = f"""\
You are an expert story writer and creative writing assistant.

{"This is a " + mode_label + "." if mode_label else ""}
{("The user selected the template: " + template_label + ".") if template_label else ""}

The story should stay consistent with the brand and audience context below when relevant:

- Brand name or site: {brand_name or "Not specified"}
- Headline/overall writing tone: {writing_tone or "Not specified"}
- Audience description: {audience_description or "Not specified"}

The user has provided the following story idea or information:

{story_idea}

Based on this story idea, generate exactly 1 well-thought-out story setup option. The setup should be CREATIVE, PERSONALIZED, and perfectly tailored to the user's specific story idea.

**CRITICAL - Creative Freedom:**
- You have COMPLETE FREEDOM to craft personalized values that best fit the user's story idea
- Do NOT limit yourself to predefined options - create custom, creative values that perfectly match the story concept
- For example, if the user wants "a story about how stars are made for a 5-year-old", you might create:
  - Writing Style: "Educational Playful" or "Simple Scientific" (not just "Casual" or "Poetic")
  - Story Tone: "Wonder-filled" or "Curious Discovery" (not just "Whimsical" or "Uplifting")
  - Narrative POV: "Second Person (You)" or "Omniscient Narrator as Guide" (not just standard options)
- The goal is to create the PERFECT setup for THIS specific story, not to fit into generic categories

The setup should:
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

Return exactly 1 option as a JSON array with a single object in "options". The object must include a "premise" field with the story premise.
"""

        setup_schema = self._build_setup_schema()

        try:
            logger.info(f"[StoryWriter] Generating story setup option for user {user_id}")
            response = self.load_json_response(
                llm_text_gen(prompt=setup_prompt, json_struct=setup_schema, user_id=user_id)
            )

            options = response.get("options", [])
            if len(options) != 1:
                logger.warning(f"[StoryWriter] Expected 1 option but got {len(options)}, correcting count")
                if len(options) < 1:
                    raise ValueError(f"Expected 1 option but got {len(options)}")
                options = options[:1]

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

            logger.info(f"[StoryWriter] Generated {len(options)} story setup option(s) with premise for user {user_id}")
            return options
        except HTTPException:
            raise
        except json.JSONDecodeError as exc:
            logger.error(f"[StoryWriter] Failed to parse JSON response for story setup: {exc}")
            raise RuntimeError(f"Failed to parse story setup options: {exc}") from exc
        except Exception as exc:
            logger.error(f"[StoryWriter] Error generating story setup options: {exc}")
            raise RuntimeError(f"Failed to generate story setup options: {exc}") from exc

    def enhance_story_idea(
        self,
        *,
        story_idea: str,
        story_mode: str | None,
        story_template: str | None,
        brand_context: Dict[str, Any] | None,
        user_id: str,
        fiction_variant: str | None = None,
        narrative_energy: str | None = None,
    ) -> List[Dict[str, Any]]:
        mode_label = None
        if story_mode == "marketing":
            mode_label = "Non-fiction marketing story (brand or product campaign)"
        elif story_mode == "pure":
            mode_label = "Fiction story"

        template_label = None
        if story_template == "product_story":
            template_label = "Product Story"
        elif story_template == "brand_manifesto":
            template_label = "Brand Manifesto"
        elif story_template == "founder_story":
            template_label = "Founder Story"
        elif story_template == "customer_story":
            template_label = "Customer Story"
        elif story_template == "short_fiction":
            template_label = "Short Fiction"
        elif story_template == "long_fiction":
            template_label = "Long Fiction"
        elif story_template == "anime_fiction":
            template_label = "Anime Fiction"
        elif story_template == "experimental_fiction":
            template_label = "Experimental Fiction"

        brand_name = None
        writing_tone = None
        audience_description = None
        if isinstance(brand_context, dict):
            brand_name = brand_context.get("brand_name")
            writing_tone = brand_context.get("writing_tone")
            target_audience = brand_context.get("target_audience")
            if isinstance(target_audience, dict):
                audience_description = target_audience.get("description") or target_audience.get("summary")
            elif isinstance(target_audience, str):
                audience_description = target_audience

        fiction_focus_line = ""
        if fiction_variant:
            fiction_focus_line = f'Treat the story as "{fiction_variant}" and lean into that creative focus.'

        energy_line = ""
        if narrative_energy:
            energy_line = f'Target narrative energy: {narrative_energy}.'

        enhance_prompt = f"""You are a creative writing coach helping a user refine and expand a story idea.

{"This is a " + mode_label + "." if mode_label else ""}
{("The user selected the template: " + template_label + ".") if template_label else ""}
{fiction_focus_line}
{energy_line}

When relevant, keep the idea aligned with this brand and audience context:
- Brand name or site: {brand_name or "Not specified"}
- Headline/overall writing tone: {writing_tone or "Not specified"}
- Audience description: {audience_description or "Not specified"}

The user has written the following story idea or concept:

{story_idea}

Your task is to propose exactly 3 alternative enhanced story idea options.

Each option must:
- Preserve the user's core premise and intent.
- Make the premise clearer and more compelling.
- Surface the central conflict or tension.
- Clarify the main characters and their goals.
- Strengthen the setting and stakes.
- Stay at the "idea" level, not a full outline or beat-by-beat breakdown.

For each option, return three fields:
- "idea": 2-4 sentences describing the improved story idea, suitable for a single textarea input.
- "whats_missing": 2-4 sentences explaining what important details are missing or underspecified in the current brief. Focus on gaps such as: protagonist details, antagonist or opposing force, stakes, setting and time period, audience/age group, subgenre or type of fiction (for example, anime vs grounded sci-fi), language or tone preferences, and any format constraints.
- "why_choose": 1-3 sentences explaining how this option interprets the original idea and why it might be a strong direction for the story.

Do not write a full story outline.
Do not output numbered lists or markdown formatting.

Return a single JSON object with a "suggestions" array of 3 items, where each item has the keys "idea", "whats_missing", and "why_choose"."""

        schema = self._build_idea_enhance_schema()

        try:
            logger.info(f"[StoryWriter] Enhancing story idea with structured suggestions for user {user_id}")
            response = self.load_json_response(
                llm_text_gen(prompt=enhance_prompt, json_struct=schema, user_id=user_id)
            )
            suggestions = response.get("suggestions", [])
            if len(suggestions) != 3:
                logger.warning(
                    f"[StoryWriter] Expected 3 idea suggestions but got {len(suggestions)}, correcting count"
                )
                if len(suggestions) < 3:
                    raise ValueError(f"Expected 3 suggestions but got {len(suggestions)}")
                suggestions = suggestions[:3]
            return suggestions
        except HTTPException:
            raise
        except json.JSONDecodeError as exc:
            logger.error(f"[StoryWriter] Failed to parse JSON response for story idea enhancement: {exc}")
            raise RuntimeError(f"Failed to parse story idea enhancement suggestions: {exc}") from exc
        except Exception as exc:
            logger.error(f"[StoryWriter] Error enhancing story idea: {exc}")
            raise RuntimeError(f"Failed to enhance story idea: {exc}") from exc

