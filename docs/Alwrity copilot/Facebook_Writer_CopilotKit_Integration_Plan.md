
# Facebook Writer + CopilotKit: Feature Set and Implementation Plan

## 0) Current Implementation Status (Updated)
- Core page and routing: `/facebook-writer` implemented with `CopilotSidebar` and scoped styling.
- Readables: `postDraft`, `notes` exposed to Copilot; preferences summarized into system message.
- Predictive state updates: live typing with progressive diff preview (green adds, red strikethrough deletes), then auto-commit.
- Edit actions: `editFacebookDraft` (Casual, Professional, Upbeat, Shorten, Lengthen, TightenHook, AddCTA) with HITL micro-form; applies live preview via custom events.
- Generation actions: `generateFacebookPost`, `generateFacebookHashtags`, `generateFacebookAdCopy` integrated with FastAPI endpoints; results synced to editor via window events.
- Facebook Story: `generateFacebookStory` added with advanced and visual options (tone, include/avoid, CTA, stickers, text overlay, interactive types, etc.). Backend returns `content` plus one 9:16 image (`images_base64[0]`) generated via Gemini and the UI renders a Story Images panel.
- Image generation module refactor: `gen_gemini_images.py` made backend-safe (removed Streamlit), added base64-first API, light retries, aligned with Gemini best practices.
- Input robustness: frontend normalization/mapping to backend enum strings (prevents 422); friendly HITL validation.
- Suggestions: progressive suggestions switch from “create” to “edit” when draft exists; stage-aware heuristics in place.
- Chat memory and preferences: localStorage persistence of last 50 messages; recent conversation and saved preferences injected into `makeSystemMessage`; “Clear chat memory” button.
- Confirm/Reject: explicit controls for predictive edits (Confirm changes / Discard) implemented.
- Observability: Facebook writer requests flow through existing middleware; compact header control already live app-wide. Route-specific counters verification pending (planned below).

Gaps / Remaining:
- Context-aware suggestions need further refinement (e.g., based on draft length, tone, goal, time of day).
- Tests for actions/handlers, reducer-like state transitions, and suggestion sets.
- Observability counters and tags for `/api/facebook-writer/*` endpoints.
- Backend session persistence (server-side conversation memory) for cross-device continuity (optional, phase-able).
- Image generation controls (toggle, retries, error UX), caching, and cost guardrails.


## 1) Goals
- Provide a specialized Facebook Writer surface powered by CopilotKit.
- Deliver intelligent, HITL (human-in-the-loop) workflows using Facebook Writer PR endpoints.
- Reuse CopilotKit best practices (predictive state updates) as demonstrated in the example demo.
- Ensure observability via existing middleware so system status appears in the main header control.

Reference demo: https://demo-viewer-five.vercel.app/feature/predictive_state_updates

---

## 2) Feature Set

### A. Core Copilot sidebar (Facebook Writer page)
- Personalized title and greeting (brand/tenant aware when available).
- Progressive suggestion groups:
  - Social content
  - Ads & campaigns
  - Engagement & optimization
- Always-on context-aware quick actions based on draft state (empty vs non-empty vs long draft).

### B. Predictive state + collaborative editing
- Readables
  - draft: current post text
  - notes/context: campaign intent, audience, key points
  - preferences: tone, objective, hashtags on/off (persisted locally; summarized to system message)
- Actions
  - updateFacebookPostDraft(content)
  - appendToFacebookPostDraft(content)
  - editFacebookDraft(operation)
  - summarizeDraft() (planned)
  - rewriteDraft(style|objective) (planned)

### C. PR endpoint coverage (initial, minimal)
- POST /api/facebook-writer/post/generate (implemented)
- POST /api/facebook-writer/hashtags/generate (implemented)
- POST /api/facebook-writer/ad-copy/generate (implemented)
- POST /api/facebook-writer/story/generate (implemented)
- GET  /api/facebook-writer/tools (implemented)
- GET  /api/facebook-writer/health (implemented)

Next endpoints (planned):
- Subsequent additions: reel/carousel/event/group/page-about

### D. HITL micro-forms
- Minimal modals inline in chat for:
  - Objective (awareness, engagement, traffic, launch)
  - Tone (professional, casual, upbeat, custom)
  - Audience (free text)
  - Include/avoid (free text)
  - Hashtags on/off

### E. Intelligent suggestions
- Empty draft → “Create launch teaser”, “Benefit-first post”, “3 variants to A/B test”
- Non-empty draft → “Tighten hook”, “Add CTA”, “Rewrite for professional tone”, “Generate hashtags” (live)
- Long draft → “Summarize to 120-150 chars intro”, “Split into carousel captions” (future)

### F. Observability and status
- Ensure facebook endpoints counted in monitoring so the compact header “System • STATUS” reflects their activity.

---

## 3) Frontend Implementation Plan

### 3.1 Route and page
- Route: `/facebook-writer`
- Component: `frontend/src/components/FacebookWriter/FacebookWriter.tsx`
  - CopilotSidebar (scoped styling class)
  - Textareas for notes and postDraft
  - Readables: notes, postDraft
  - Actions: updateFacebookPostDraft, appendToFacebookPostDraft

### 3.2 API client
- File: `frontend/src/services/facebookWriterApi.ts`
  - postGenerate(req)
  - adCopyGenerate(req)
  - hashtagsGenerate(req)
  - storyGenerate(req) [advanced + visual options]
  - tools(), health()
- Types aligned with PR models (enum value strings must match server models).

### 3.3 Copilot actions (HITL + server calls)
- File: `frontend/src/components/FacebookWriter/RegisterFacebookActions.tsx`
  - Action: generateFacebookPost
    - renderAndWaitForResponse → prompt for goal, tone, audience, include/avoid, hashtags
    - Call api.postGenerate → update draft
  - Action: generateHashtags
    - renderAndWaitForResponse → topic or use draft
    - Call api.hashtagsGenerate → append to draft
  - Action: generateAdCopy (implemented)
    - renderAndWaitForResponse → prompt for business_type, product/service, objective, format, audience, targeting basics, USP, budget
    - Call api.adCopyGenerate → append primary text to draft; keep variations for UI
  - Action: generateFacebookStory (implemented)
    - renderAndWaitForResponse → advanced (hooks, CTA, etc.) and visual options (background type/prompt, overlay, interactive types)
    - Call api.storyGenerate → append story content; dispatch `fbwriter:storyImages` to render returned image(s)
- Helper: custom window events keep editor as single source of truth.

### 3.4 Suggestions and system message
- Suggestions computed from draft length, last action result, and notes presence.
- System message includes short brand tone guidance when available.

### 3.5 Demo parity (predictive state updates)
- Expose two local actions for state updates:
  - updateFacebookPostDraft
  - appendToFacebookPostDraft
- Ensure Copilot can call those without round-tripping to backend for quick edits.
- Confirm/Reject step before committing predictive edits (implemented)

---

## 4) Backend Integration Plan

### 4.1 Use PR structure
- Routers: `backend/api/facebook_writer/routers/facebook_router.py`.
- Services: `backend/api/facebook_writer/services/*`.
- Models: `backend/api/facebook_writer/models/*`.

### 4.2 Minimal requests for post.generate
- Map HITL selections to `FacebookPostRequest` fields:
  - post_goal: enum string value (e.g., “Build brand awareness”)
  - post_tone: enum string value (e.g., “Professional”)
  - media_type: “None” (default)
  - advanced_options: from toggles
- Handle 422 by ensuring exact enum text.

### 4.3 Monitoring
- No changes required if middleware already counts routes; confirm they appear in status.

---

## 5) UX details
- Sidebar personalized title: “ALwrity • Facebook Writer”.
- Glassomorphic style aligned with SEO assistant.
- Accessibility: focus-visible rings, reduced-motion respect.
- Error paths: concise toast + retry in HITL form.

---

## 6) Milestones
- M1 (Done): Page + readables + predictive edits + suggestions (start/edit) + health/tools probe.
- M2 (Done): HITL for post.generate; integrate API; hashtags action; editor sync.
- M3 (Updated): Ad copy (done), Variations UI (done), Story (done), context-aware suggestions (ongoing), tests (pending).
- M4 (Planned): Reel/Carousel; variants pipeline; scheduling hooks; session persistence (optional).

### 6.1 Next-phase Tasks (Detailed)
- Ad Copy (M3)
  - Suggestion chips: “Create ad copy”, “Short ad variant (primary text)”, “Insert headline X”.
  - A/B insert UX: quick insert/replace buttons already present; add multi-insert queue.
- Story (M3)
  - HITL toggle for image generation on/off; regenerate button; image count (1–3) cap.
  - Gallery UX: copy/download, insert image markdown into draft, or upload to asset store.
  - Improve visual prompt composition from form fields (brand + tone + CTA region).
- Context-aware Suggestions (M3)
  - Derive stage features: draft length buckets, tone inferred from text, presence of CTA/hashtags.
  - Swap suggestion sets accordingly; include “Summarize intro” for long drafts.
- Confirm/Reject for Predictive Edits (M3)
  - Option: preference to auto-confirm future edits.
- Tests (M3)
  - Unit test action handlers (param mapping, event dispatch), reducer-like state transitions.
  - Snapshot test suggestion sets for start/edit/long-draft.
  - API client smoke tests for post/hashtags/ad-copy/story.
- Observability (M3)
  - Verify `/api/facebook-writer/*` counters in header; add tags for route family.
  - Log action success/error counts.
- Session Persistence (M4, optional)
  - Backend `copilot_sessions` + `messages` tables; persist assistant/user messages.
  - Provide `sessionId` per user/page; prehydrate sidebar from server.
- Next endpoints (M4)
  - Implement reel/carousel/event/group/page-about endpoints with parity HITL forms.

### 6.2 Known limitations / Non-goals (for now)
- Image generation: Gemini outputs include SynthID watermark; outputs not guaranteed each call; currently generates 1 image for story.
- Cost/quotas: No server-side budgeting/limits yet for image gen; add per-user caps and caching.
- Asset pipeline: No upload/CDN integration yet; images are rendered inline as base64.

---

## 7) Risks & Mitigations
- Enum mismatches → Use exact server enum strings; surface helpful errors.
- Long outputs → Clamp `max_tokens` server-side; provide “shorten” action client-side.
- Rate limiting → Respect retry/backoff; keep client timeouts reasonable.

Reference (Gemini image generation best practices): https://ai.google.dev/gemini-api/docs/image-generation

---

## 8) Success Criteria
- End-to-end draft creation via Copilot with a single click (HITL).
- Predictive state edits observable in real-time.
- Monitoring reflects API usage in the header control.
- Clean, reproducible flows for post + hashtags; extendable to ads and other tools.

---

## 9) Immediate Next Steps (Page About Implementation)

### 9.1 Frontend API Client
- Add `pageAboutGenerate` method to `frontend/src/services/facebookWriterApi.ts`
- Match payload structure with `FacebookPageAboutRequest` model
- Include proper TypeScript interfaces for request/response

### 9.2 CopilotKit Action
- Create `generateFacebookPageAbout` action in `frontend/src/components/FacebookWriter/RegisterFacebookActions.tsx`
- Implement HITL form with fields for:
  - `business_name`, `business_category`, `business_description`
  - `target_audience`, `unique_value_proposition`, `services_products`
  - `page_tone`, `contact_info`, `keywords`, `call_to_action`
- Add enum mapping for `business_category` and `page_tone` to prevent 422 errors
- Handle response with multiple sections and append to draft

### 9.3 UI Integration
- Add "Page About" suggestion chip in `FacebookWriter.tsx`
- Consider displaying generated sections in a structured format
- Ensure proper error handling and loading states

### 9.4 Testing
- Test the complete flow from CopilotKit action to backend response
- Verify enum mapping prevents 422 errors
- Check that generated content properly appends to draft

### 9.5 Documentation Update
- Update this document once Page About is implemented
- Mark all Facebook Writer endpoints as complete
- Plan next phase: testing, observability, and optimization
