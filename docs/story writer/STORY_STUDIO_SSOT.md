# Story Studio – Single Source of Truth (SSOT)

## 1. Vision and Positioning

- **Product name**: Story Studio (evolution of Story Writer).
- **What it is**: A narrative engine plus lightweight movie studio that turns brand and product context into structured stories, scenes, and multimedia assets.
- **Role in ALwrity**: One of several “surfaces” driven by the same contextual brain (onboarding data, personas, SEO, competitive analysis), alongside Blog Writer, YouTube Creator, Podcast Maker, and Video Studio.

### Core positioning

- **Campaign Story Engine** (primary):
  - Generates product stories, brand manifestos, founder narratives, and customer journey stories.
  - Uses onboarding + persona + SEO context so stories are on-brand and strategically aligned.
- **Story Studio / Fiction mode** (secondary):
  - High-quality freeform stories (including anime / fantasy), primarily for GSC traffic and creative users.
  - Lives “one click deeper” in the UI so marketing-first use cases stay front and center.

Story Studio is not just “a novelist playground”; it is the narrative layer that can feed:
- YouTube Creator (scripts and scenes),
- Podcast Maker (episodic story arcs),
- Video Studio (scene-wise video generation),
- Blog and social content (campaign narratives).

---

## 2. Modes and Templates

### 2.1 Modes

- **Marketing Narratives (default)**:
  - Entry path for ALwrity users arriving from the main app.
  - Story types:
    - Product Story (feature-driven but narrative-first).
    - Brand Manifesto / “Why we exist”.
    - Founder Story / Mission Arc.
    - Customer Case Story (problem → journey → outcome).
  - All marketing modes must:
    - Pull from onboarding canonical_profile (brand, product, audience, pain points).
    - Respect persona tone and style.
    - Optionally weave in SEO pillars and competitor differentiation language.

- **Pure Story Mode (creative)**:
  - Entry path for GSC traffic and direct Story Studio users.
  - Story types:
    - Freeform fiction.
    - Anime / manga stories.
    - Experimental narrative formats.
  - Marketing alignment:
    - Gently surfaces the idea: “Turn this into a video / campaign” via export options.

### 2.2 Template system

For each template, define:
- Required fields: goal, target audience, setting, length, POV, style, tone.
- Optional fields: persona to anchor voice, product/context attachments.
- Output shape:
  - Premise (1–2 sentences).
  - Outline (scenes with structured metadata).
  - Story text (segments).
  - Multimedia plan (per scene: image prompt, audio cue, video emphasis).

Initial templates:
- **Product Story**:
  - Uses onboarding product data (features, benefits, differentiators).
  - Structure: origin → tension → solution → proof → future.
- **Brand Manifesto**:
  - Uses canonical_profile (mission, values, audience).
  - Structure: problem with status quo → belief → promise → invitation.
- **Founder Story**:
  - Uses founder/persona context if available, otherwise guided questionnaire.
  - Structure: “before” life → trigger moment → struggle → insight → creation of the product.
- **Customer Case Story**:
  - Uses ICP + persona + pain-point data.
  - Structure: “Customer X had problem Y” → discovery of solution → implementation → quantified outcome.
- **Anime / Storyverse**:
  - Style, visuals, and multimedia prompts oriented toward anime / stylized output.

---

## 3. Context Inputs (Data and Signals)

Story Studio should treat ALwrity’s context as first-class inputs:

- **Onboarding / canonical_profile**:
  - brand_pitch, positioning, audience, products/services, content pillars.
- **Personas**:
  - core persona plus platform adaptations (tone, structure, constraints).
- **SEO and competitors**:
  - core keywords, sitemap analysis, competitive positioning and gaps.
- **User preferences**:
  - story length, style, tone, POV, “safe vs experimental”, multimedia intensity.

Implementation:
- Extend Story Setup to optionally show:
  - “Use my brand & product data” toggle.
  - Dropdown/select for which persona to write from.
  - Pre-filled prompts using SEO pillars and competitor gaps.
- State builder (`getRequest()` in useStoryWriterState) should:
  - Attach canonical_profile / persona IDs or snapshots when marketing templates are used.

---

## 4. Text Model Strategy

### 4.1 Roles

- **Structured outline + scenes**:
  - Use `llm_text_gen` with `json_struct` for:
    - Scene lists (scene_number, title, description).
    - Per-scene image_prompt, audio_narration, character_descriptions, key_events.
  - Requirements:
    - High reliability on JSON output.
    - Good adherence to scene progression instructions.

- **Narrative generation (story text)**:
  - Use `llm_text_gen` in text mode for:
    - Premise, story start, continuation until word-count targets.
  - Requirements:
    - Style controllability (tone, genre, age group).
    - Long-context coherence for medium/long stories.

### 4.2 Providers and models

Use the existing provider abstraction:

- **OSS/primary**: HF-backed models (Llama 3.1 8B, Mistral 7B, Qwen2.5) for cost-effective long-form and experimental modes.

Decisions:
- Keep model selection internal for now (no UI dropdown).
- Introduce a simple “Quality vs Speed vs Cost” preset internally mapped to:
  - High quality: Gemini or best OSS model.
  - Balanced: OSS instruct model (e.g., Llama 3.1 8B, Mistral 7B).
  - Experimental: more creative / higher-temperature models.

Story length control remains as defined in story-writer-architecture.mdc:
- Short (~1k words): one-shot.
- Medium (<5k): multi-step.
- Long (~10k): multi-step with IAMDONE marker.

---

## 5. Multimedia Model Strategy

Multimedia generation must reuse existing studio infrastructure rather than invent new stacks.

### 5.1 Images

- Use StoryImageGenerationService as primary:
  - Provider: stability / other configured HF/Gemini image models.
  - Inputs: per-scene `image_prompt` derived from outline and template.
  - Templates:
    - Realistic marketing visuals (product-focused).
    - Anime / stylized visuals (for anime mode).

### 5.2 Audio

- Use StoryAudioGenerationService:
  - Providers: gTTS, pyttsx3, or any configured TTS provider.
  - Inputs: `audio_narration` per scene (or compressed scene text).
  - For campaign stories:
    - Voice selection aligned with brand persona (calm, energetic, authoritative).

### 5.3 Video

- Use StoryVideoGenerationService for stitching scenes:
  - Inputs:
    - `image_urls` or `video_urls` per scene.
    - `audio_urls` per scene.
    - `fps`, `transition_duration`.
  - For advanced/hero scenes, optionally integrate Video Studio models:
    - text-to-video models (Hunyuan, LTX-2) for key moments.
    - image-to-video (WAN 2.5, Kandinsky 5 Pro) for stylized sequences.

### 5.4 Modes

- **Standard story video**:
  - Use existing story video pipeline.
  - Emphasis on timeline, readability, and voiceover.
- **Anime / stylized video**:
  - Switch scene prompts + model selection to anime-friendly setups.
  - Use more dynamic transitions for “story trailer” feel.

---

## 6. Phase Flow (Reframed for Story Studio)

Core phases remain as in story-writer-architecture.mdc but with clarified responsibilities:

1. **Setup**:
   - Choose mode: Marketing Narrative vs Pure Story.
   - Select template (Product Story, Brand Manifesto, etc.).
   - Toggle/use brand context (onboarding, personas, SEO).
   - Configure image/audio/video settings.

2. **Outline**:
   - Generate structured outline with scenes via `json_struct`.
   - For marketing templates:
     - Ensure each scene maps to a stage in the campaign story arc.
   - For anime/fiction:
     - Emphasize “world, characters, conflicts” and visual richness.

3. **Writing**:
   - Generate story text based on length settings.
   - Enforce length controls and completion detection.
   - Show word count and target in UI.

4. **Multimedia / Export**:
   - Generate scene images, audio, and video using configured settings.
   - Allow:
     - Export as story video (using StoryVideoGenerationService).
     - Export scenes and script to:
       - YouTube Creator (for adaptation to YouTube-specific script + scenes).
       - Video Studio (for advanced editing or alternative visual styles).

5. **Reset**:
   - Keep existing reset semantics (clears state, localStorage, phases).

---

## 7. Implementation Plan

### Phase 1 – Positioning and UX tweaks

- Rename surface in UI copy to “Story Studio” where appropriate (keep routes/IDs stable to preserve GSC).
- Add mode selector in Setup:
  - Marketing Narratives (default).
  - Pure Story.
- Add template selector for marketing mode:
  - Product Story, Brand Manifesto, Founder Story, Customer Story.
- Adjust landing screen messaging to emphasize:
  - “Turn your brand and product into narrative campaigns.”

### Phase 2 – Context integration

- Extend Story Setup state to store:
  - `useBrandContext` flag.
  - `selectedPersonaId` (optional).
  - `selectedProductId` or product context stub.
- Update `getRequest()` to include:
  - References or snapshots from canonical_profile (where available).
- Update backend story_service to:
  - Accept and pass context into prompts (premise, outline, story start, continuation).

### Phase 3 – Template-specific prompts

- Design prompt templates per marketing template:
  - Product Story, Brand Manifesto, Founder Story, Customer Story.
- Encode:
  - Clear arcs (setup → conflict → resolution).
  - Use of brand and persona parameters.
  - Explicit constraints on tone, length, POV.
- For pure story mode:
  - Provide genre/style toggles, including anime.

### Phase 4 – Multimedia presets

- Define multimedia presets for:
  - Marketing Story (clean product visuals, muted transitions).
  - Anime Story (bold colors, stylized prompts, dynamic transitions).
  - Trailer Mode (shorter, punchier video composition).
- Map presets to:
  - Image generation prompt scaffolds.
  - Video settings (fps, transition_duration).
  - Potential future mapping into Video Studio model choices.

### Phase 5 – Cross-surface exports

- Implement export from Story Studio to:
  - YouTube Creator:
    - Export scenes as a JSON payload that can seed plan/scenes.
  - Video Studio:
    - Export scenes with associated image/audio references to pre-populate a project.
- Add UI affordances:
  - “Send to YouTube Creator”.
  - “Open in Video Studio”.

### Phase 6 – Hardening and metrics

- Ensure:
  - Subscription / usage checks per story generation and multimedia call.
  - Caching behavior for repeated outline/story generations when context unchanged.
  - Task management and polling remain consistent with existing story_writer architecture.
- Add metrics:
  - How many Story Studio sessions start in marketing vs pure modes.
  - How many flows export to YouTube/Video Studio.

---

## 9. Current Implementation Status (Feb 2026)

- Modes and templates:
  - Marketing vs Pure Story modes are wired through Story Setup state and backend prompts.
  - Template identifiers (e.g. `product_story`, `brand_manifesto`, `founder_story`, `customer_story`, `short_fiction`, `long_fiction`, `anime_fiction`, `experimental_fiction`) are resolved in service components for label-aware prompts.
- Context integration:
  - Story context endpoint exposes `canonical_profile`-derived `brand_context` and `brand_assets` for Story Studio.
  - Story Setup modal can toggle use of onboarding brand persona when in marketing mode, and surfaces avatar and voice preview where available.
- AI Setup modal:
  - Dedicated AI Setup modal drives an idea → setup flow.
  - “Enhance Story Idea” uses a dedicated backend endpoint to enhance only the freeform idea text, preserving intent and avoiding premature setup field generation.
  - “Continue to Story Setup” generates exactly three structured setup options and, on selection, pre-fills Story Setup fields (persona, setting, characters, plot, style, tone, POV, audience, rating, ending, length, premise) plus image/video/audio defaults.
  - UI includes rotating, mode-aware idea placeholders and an AI-style, animated glow frame around the story idea textarea to emphasize the primary input surface while keeping the overall theme light and readable.
- Multimedia defaults:
  - Story Setup state carries image/video/audio settings and can accept per-option overrides from generated setups.
  - Story Outline and StoryImageGenerationModal integrate with the shared image generation stack, including provider/model selection and cost-awareness.
- Video integrations:
  - HD video configuration section exposes provider/model dropdowns with story-based defaults, aligned with the broader Video Studio architecture.

---

## 10. Next Steps for Story Studio

- Deepen template-specific prompts:
  - Tighten prompt templates per marketing template so setup options encode clearer arcs and brand positioning, especially for product_story and customer_story.
  - Expand fiction/anime prompt variants to better control pacing and recurring characters across scenes.
- Refine idea-to-setup bridge:
  - Add light-touch guidance in the AI Setup modal to help users iterate between idea enhancement and setup generation (e.g. suggested follow-up edits based on the last enhancement).
  - Capture telemetry on how often users enhance the idea before generating setups to tune prompts and thresholds.
- Multimedia and cross-surface flows:
  - Wire Story Studio’s outline and scene structures into “Send to YouTube Creator” and “Open in Video Studio” actions, including carrying over multimedia presets.
  - Introduce preset bundles for “Standard Story”, “Anime Story”, and “Trailer Mode” that automatically adjust image/video defaults and, where available, Video Studio model choices.
- Reliability and guardrails:
  - Add targeted monitoring around the AI Setup endpoints (idea enhancement and setup generation) for latency, error rates, and JSON validity.
  - Continue to enforce subscription and usage checks consistently across Story Studio, Blog Writer, and Video Studio so billing and limits remain unified.

---

## 8. Guardrails and Non-Goals

- Do not:
  - Turn Story Studio into a separate codebase; keep it within the existing Story Writer architecture and services.
  - Fragment context handling; continue to use canonical_profile and existing persona services as SSOTs.
- Guardrails:
  - Maintain strict story length controls.
  - Keep subscription handling centralized via `triggerSubscriptionError`.
  - Continue to use structured JSON for outlines and scene metadata wherever possible.

This document, together with `story-writer-architecture.mdc` and the existing Story Writer implementation docs in `docs/story writer/`, serves as the SSOT for evolving Story Writer into Story Studio.
