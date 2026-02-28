# Anime Story Bible – Design & Implementation (Story Writer SSOT)

This document is the single source of truth for the **Anime Story Bible** in Story Writer: what it is, where it lives in the codebase, how it is generated, and how it is used across outline, story text, images, and motion/animation.

---

## 1. Core Concepts

- **Anime Story Bible**: Structured description of characters, world, and visual style for anime-style stories. It is designed to be:
  - Stable across the whole story (single bible per story)
  - Machine-readable (Pydantic/TypeScript models)
  - Reusable for text, image, and video prompts

- **Design Goals**
  - Maintain **character consistency** across scenes and media
  - Maintain **world rules** (tech/magic, constraints) throughout the narrative
  - Maintain a **coherent anime visual style** across images and motion clips
  - Allow future reuse for other story templates and media pipelines

---

## 2. Data Model (Backend & Frontend)

### 2.1 Backend Models

File: [story_models.py](file:///c:/Users/diksha%20rawat/Desktop/ALwrity/backend/models/story_models.py)

Key classes:

- `AnimeCharacter`
- `AnimeWorld`
- `AnimeVisualStyle`
- `AnimeStoryBible`

They are defined as:

- `AnimeCharacter`
  - `id`: stable snake_case identifier
  - `name`
  - `age_range`
  - `role` (protagonist, antagonist, mentor, etc.)
  - `look` (key visual details)
  - `outfit_palette`
  - `personality_tags: List[str]`

- `AnimeWorld`
  - `setting` (locations and general world description)
  - `era` (near-future, alt 1990s, etc.)
  - `tech_or_magic_level`
  - `core_rules: List[str]` (constraints and consistent rules)

- `AnimeVisualStyle`
  - `style_preset` (anime_manga, cinematic_anime, cozy_slice_of_life, etc.)
  - `camera_style`
  - `color_mood`
  - `lighting`
  - `line_style`
  - `extra_tags: List[str]`

- `AnimeStoryBible`
  - `story_id?: str`
  - `main_cast: List[AnimeCharacter]`
  - `world: AnimeWorld`
  - `visual_style: AnimeVisualStyle`

The bible is attached to:

- `StorySetupOption.anime_bible: Optional[AnimeStoryBible]`
- `StoryOutlineResponse.anime_bible: Optional[AnimeStoryBible]`

Additionally, for downstream usage:

- `StoryGenerationRequest.anime_bible: Optional[Dict[str, Any]]`
- `StoryContinueRequest.anime_bible: Optional[Dict[str, Any]]`

This allows story-start and continuation to receive a JSON-serializable bible blob without strict coupling to the `AnimeStoryBible` class.

### 2.2 Frontend Models

File: [storyWriterApi.ts](file:///c:/Users/diksha%20rawat/Desktop/ALwrity/frontend/src/services/storyWriterApi.ts)

Types mirror the backend:

- `AnimeCharacter`
- `AnimeWorld`
- `AnimeVisualStyle`
- `AnimeStoryBible`

The bible flows through:

- `StoryOutlineResponse.anime_bible?: AnimeStoryBible`
- `StoryGenerationRequest.anime_bible?: AnimeStoryBible | null`
- `StoryStartRequest` and `StoryContinueRequest` (via `StoryGenerationRequest`)

State layer:

File: [useStoryWriterState.ts](file:///c:/Users/diksha%20rawat/Desktop/ALwrity/frontend/src/hooks/useStoryWriterState.ts)

- `StoryWriterState.animeBible: any | null`
- `setAnimeBible` setter
- Persisted and restored via `localStorage`:
  - Saved under `animeBible` key in the serialized state
  - Ensures the bible survives refreshes

---

## 3. Bible Lifecycle & Generation

### 3.1 Generation Source

The Anime Story Bible is generated in the **story setup / outline** pipeline on the backend:

- The story setup step produces a single `StorySetupOption` enriched with `anime_bible` when the selected template is anime-focused.
- The outline generation step (`StoryOutlineResponse`) carries `anime_bible` so the UI can display it and store it in Story Writer state.

SSOT:

- Models: [story_models.py](file:///c:/Users/diksha%20rawat/Desktop/ALwrity/backend/models/story_models.py)
- Outline response: `StoryOutlineResponse.anime_bible`

### 3.2 Frontend Storage and Access

The frontend receives `anime_bible` from `StoryOutlineResponse` and:

- Stores it in `StoryWriterState.animeBible`
- Persists it in `localStorage` with the rest of the story writer state
- Exposes it to:
  - Director chip / bible viewer UI
  - Story generation (start/continue)
  - Scene animation (via `story_context`)

Key locations:

- State hook: [useStoryWriterState.ts](file:///c:/Users/diksha%20rawat/Desktop/ALwrity/frontend/src/hooks/useStoryWriterState.ts)
- Outline phase UI: [StoryOutline.tsx](file:///c:/Users/diksha%20rawat/Desktop/ALwrity/frontend/src/components/StoryWriter/Phases/StoryOutline.tsx)

---

## 4. Integration Points (Current Implementation)

This section documents how the Anime Story Bible is currently used across the Story Writer pipelines.

### 4.1 Story Text Generation (Start & Continue)

#### 4.1.1 Requests

Frontend:

- `StoryGenerationRequest` (base)
  - Now includes `anime_bible?: AnimeStoryBible | null`
- `getRequest()` in `useStoryWriterState` adds `anime_bible` automatically:

  - [useStoryWriterState.ts:getRequest](file:///c:/Users/diksha%20rawat/Desktop/ALwrity/frontend/src/hooks/useStoryWriterState.ts#L420-L461)

Story start:

- `StoryWriting.handleGenerateStart`:
  - Builds `request = state.getRequest()`
  - Calls `storyWriterApi.generateStoryStart(premise, outline, request)`
  - [StoryWriting.tsx](file:///c:/Users/diksha%20rawat/Desktop/ALwrity/frontend/src/components/StoryWriter/Phases/StoryWriting.tsx#L308-L328)

Story continue:

- `StoryWriting.handleContinue`:
  - `request = state.getRequest()`
  - Builds `continueRequest = { ...request, premise, outline, story_text }`
  - Calls `storyWriterApi.continueStory(continueRequest)`
  - [StoryWriting.tsx](file:///c:/Users/diksha%20rawat/Desktop/ALwrity/frontend/src/components/StoryWriter/Phases/StoryWriting.tsx#L377-L388)

Backend:

- `StoryGenerationRequest` / `StoryContinueRequest` include `anime_bible: Optional[Dict[str, Any]]`
  - [story_models.py](file:///c:/Users/diksha%20rawat/Desktop/ALwrity/backend/models/story_models.py#L11-L43)
  - [story_models.py](file:///c:/Users/diksha%20rawat/Desktop/ALwrity/backend/models/story_models.py#L243-L259)

#### 4.1.2 Routing Layer

File: [api/story_writer/routes/story_content.py](file:///c:/Users/diksha%20rawat/Desktop/ALwrity/backend/api/story_writer/routes/story_content.py)

- `generate_story_start`:

  ```python
  story_start = story_service.generate_story_start(
      premise=request.premise,
      outline=outline_data,
      persona=request.persona,
      story_setting=request.story_setting,
      character_input=request.character_input,
      plot_elements=request.plot_elements,
      writing_style=request.writing_style,
      story_tone=request.story_tone,
      narrative_pov=request.narrative_pov,
      audience_age_group=request.audience_age_group,
      content_rating=request.content_rating,
      ending_preference=request.ending_preference,
      story_length=story_length,
      anime_bible=getattr(request, "anime_bible", None),
      user_id=user_id,
  )
  ```

- `continue_story`:

  ```python
  continuation = story_service.continue_story(
      premise=request.premise,
      outline=outline_data,
      story_text=request.story_text,
      persona=request.persona,
      story_setting=request.story_setting,
      character_input=request.character_input,
      plot_elements=request.plot_elements,
      writing_style=request.writing_style,
      story_tone=request.story_tone,
      narrative_pov=request.narrative_pov,
      audience_age_group=request.audience_age_group,
      content_rating=request.content_rating,
      ending_preference=request.ending_preference,
      anime_bible=getattr(request, "anime_bible", None),
      story_length=story_length,
      user_id=user_id,
  )
  ```

#### 4.1.3 Service Layer Prompts

File: [story_content.py](file:///c:/Users/diksha%20rawat/Desktop/ALwrity/backend/services/story_writer/service_components/story_content.py)

- `StoryContentMixin.generate_story_start(...)` now accepts `anime_bible: Optional[Dict[str, Any]]` and injects a serialized bible block right after the persona prompt:

  ```python
  anime_bible_context = ""
  if anime_bible:
      try:
          serialized_bible = json.dumps(anime_bible, ensure_ascii=False, indent=2)
      except Exception:
          serialized_bible = str(anime_bible)
      anime_bible_context = f"""

  You also have a structured ANIME STORY BIBLE that defines the main cast, world rules, and visual style. Use it as a hard constraint for character consistency, worldbuilding, and visual storytelling:

  {serialized_bible}
  """
  ```

  The context is included for both short-story and longer-story prompts. This ensures:

  - Character, world, and style constraints are explicitly visible to the LLM
  - The same bible is applied consistently for start and continuation

- `StoryContentMixin.continue_story(...)` similarly accepts `anime_bible` and injects the same `anime_bible_context` into the continuation prompt, directly after `persona_prompt`.

This means every text generation step (start and continue) is conditioned on the bible when present.

### 4.2 Scene Animation (Image-to-Video)

The current bible-aware integration is focused on **motion prompts** for Kling image-to-video.

#### 4.2.1 Frontend: story_context payload

File: [StoryOutline.tsx](file:///c:/Users/diksha%20rawat/Desktop/ALwrity/frontend/src/components/StoryWriter/Phases/StoryOutline.tsx)

`createStoryContextPayload` includes `anime_bible`:

```ts
const createStoryContextPayload = () => ({
  persona: state.persona,
  story_setting: state.storySetting,
  characters: state.characters,
  plot_elements: state.plotElements,
  writing_style: state.writingStyle,
  story_tone: state.storyTone,
  narrative_pov: state.narrativePOV,
  audience_age_group: state.audienceAgeGroup,
  content_rating: state.contentRating,
  story_length: state.storyLength,
  premise: state.premise,
  outline: state.outline,
  story_content: state.storyContent,
  anime_bible: state.animeBible,
});
```

This payload is passed to:

- `storyWriterApi.animateScene(...)`
- `storyWriterApi.animateSceneVoiceover(...)`

#### 4.2.2 Backend: Kling animation service

File: [kling_animation.py](file:///c:/Users/diksha%20rawat/Desktop/ALwrity/backend/services/wavespeed/kling_animation.py)

- `animate_scene_image(...)` is unchanged in signature but passes `story_context` to `generate_animation_prompt(...)`.

- `_build_fallback_prompt(scene_data, story_context)`:
  - Reads `anime_bible = story_context.get("anime_bible")`
  - Extracts:
    - Visual style details (`style_preset`, `camera_style`, `color_mood`, `lighting`, `line_style`, `extra_tags`)
    - World `setting`
    - `main_cast` names
  - Appends a concise style text to the deterministic fallback prompt to preserve:
    - Visual style
    - World flavor
    - Character design consistency (names only)

- `generate_animation_prompt(scene_data, story_context, user_id)`:
  - Builds an `ANIME STORY BIBLE VISUAL GUIDANCE` block when `anime_bible` is present, e.g.:
    - Visual style preset and camera style
    - Color mood, lighting, line style
    - Extra style tags
    - Main cast names to keep visually consistent
    - World/setting context
  - Inserts this block between `Setting` and the “Focus on” bullet list in the LLM prompt.
  - Both structured JSON responses and fallback text generation flows see this block.

Result:

- Motion prompts for Kling image-to-video are constrained by the bible, making animations conform to:
  - The same anime visual style
  - The same character set
  - The same world tone

### 4.3 Images (Current State)

Image generation currently uses:

- `StoryScene.image_prompt` generated during outline generation
- Image provider settings (width, height, model)

The anime bible is not yet used in a **second-pass image prompt rewriter**. However:

- The bible is already aligned with the same outline and template that produced `image_prompt`.
- The bible is threaded into Story Writer’s state and can be used later to refine image prompts or add style constraints.

Planned enhancement (not yet implemented):

- Add a lightweight prompt refinement step that:
  - Takes `scene.image_prompt` + `AnimeStoryBible.visual_style`
  - Emits a style-constrained `final_image_prompt`
  - Passes that to the image generation service

This document should be updated when that enhancement is implemented.

---

## 5. Adapting the Bible to Other Story Types

Although the Anime Story Bible is currently wired for anime-focused stories, the architecture is intentionally reusable.

### 5.1 Reuse Strategy

- **Data model**:
  - `AnimeStoryBible` is anime-specific, but the concept of a structured “story bible” (cast + world + style) is general.
  - Future story types can introduce sibling models (e.g., `NovelStoryBible`, `ComicStoryBible`) reusing similar patterns.

- **Transport layer**:
  - Requests use a flexible `anime_bible: Optional[Dict[str, Any]]` at the story-generation level.
  - This can be generalized to a `story_bible` field if we want cross-template reuse.

- **Prompt patterns**:
  - Both text and motion pipelines use the same pattern:
    - Serialize the bible
    - Inject a dedicated paragraph or bullet block
    - Explicitly instruct the model to treat it as a hard constraint
  - This pattern is template-agnostic and can be reused for other story modes.

### 5.2 Extension Guidelines

When adapting the bible pattern to other story types:

1. **Define the bible model**
   - Add a dedicated Pydantic model under `story_models.py`.
   - Mirror it with a TypeScript interface in `storyWriterApi.ts`.

2. **Attach it to responses**
   - Extend the relevant response models (setup, outline, etc.) with an optional bible field.
   - Ensure the generating service populates it when the template supports it.

3. **Thread through state**
   - Add a field to `StoryWriterState`.
   - Persist it in `localStorage`.
   - Provide setter(s) and ensure it is included in `getRequest()` when relevant.

4. **Inject into prompts**
   - Text: add a serialized bible context block after the persona prompt for:
     - Story start
     - Story continuation
   - Media: add a structured guidance block to:
     - Image prompt generation (if using AI to build prompts)
     - Motion/animation prompts

5. **Document the flow**
   - Update this document (or a sibling doc) with:
     - Model definitions
     - Where the bible is generated
     - Where and how it is injected into prompts

---

## 6. Summary of Recent Changes (Bible Wiring)

This section summarizes the concrete changes made for the initial Anime Story Bible integration:

- **Backend models**
  - Added `anime_bible` to `StoryGenerationRequest` and `StoryContinueRequest` as `Optional[Dict[str, Any]]`.
  - Confirmed `AnimeStoryBible` and related classes in [story_models.py](file:///c:/Users/diksha%20rawat/Desktop/ALwrity/backend/models/story_models.py).

- **Frontend models & state**
  - Added `anime_bible?: AnimeStoryBible | null` to `StoryGenerationRequest`.
  - `useStoryWriterState.getRequest()` now includes `anime_bible: state.animeBible || null`.
  - `createStoryContextPayload` for outline/animation includes `anime_bible: state.animeBible`.

- **Story text prompts**
  - `generate_story_start` and `continue_story` accept `anime_bible` and inject a serialized “ANIME STORY BIBLE” context block directly after `persona_prompt`.
  - Routing layer passes `request.anime_bible` through from API to service.

- **Motion prompts (Kling image-to-video)**
  - `story_context.anime_bible` is used in:
    - `_build_fallback_prompt` to append style/world/cast hints to deterministic prompts.
    - `generate_animation_prompt` to add an explicit `ANIME STORY BIBLE VISUAL GUIDANCE` block for the LLM.

- **Not yet implemented**
  - Second-pass enrichment of per-scene `image_prompt` using the bible.
  - Generalization beyond anime templates (would require broader “story bible” abstraction).

This document should be kept up to date whenever the Anime Story Bible is:

- Extended to new story templates
- Used for additional media types (e.g., storyboard export, trailers)
- Modified in structure or prompt integration

