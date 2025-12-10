# Podcast Maker External API Call Analysis

## Overview
This document analyzes all external API calls made during the podcast creation workflow and how they scale with duration, number of speakers, and other factors.

---

## External API Providers

1. **Gemini (Google)** - LLM for story setup and script generation
2. **Google Grounding** - Research via Gemini's native search grounding
3. **Exa** - Alternative neural search provider for research
4. **WaveSpeed** - API gateway for:
   - **Minimax Speech 02 HD** - Text-to-Speech (TTS)
   - **InfiniteTalk** - Avatar animation (image + audio → video)

---

## Workflow Phases & API Calls

### Phase 1: Project Creation (`createProject`)

**External API Calls:**
1. **Gemini LLM** - Story setup generation
   - **Endpoint**: `/api/story/generate-setup`
   - **Backend**: `storyWriterApi.generateStorySetup()`
   - **Service**: `backend/services/story_writer/service_components/setup.py`
   - **Function**: `llm_text_gen()` → Gemini API
   - **Calls per project**: **1 call**
   - **Scaling**: Fixed (1 call regardless of duration)

2. **Research Config** (Optional)
   - **Endpoint**: `/api/research-config`
   - **Calls per project**: **0-1 call** (cached)
   - **Scaling**: Fixed

**Total Phase 1**: **1-2 external API calls** (fixed)

---

### Phase 2: Research (`runResearch`)

**External API Calls:**
1. **Google Grounding** (via Gemini) OR **Exa Neural Search**
   - **Endpoint**: `/api/blog/research/start` → async task
   - **Backend**: `blogWriterApi.startResearch()`
   - **Service**: `backend/services/blog_writer/research/research_service.py`
   - **Provider Selection**:
     - **Google Grounding**: Uses Gemini's native Google Search grounding
     - **Exa**: Direct Exa API calls
   - **Calls per research**: **1 call** (handles all keywords in one request)
   - **Scaling**: 
     - **Fixed per research operation** (1 call regardless of number of queries)
     - **Queries are batched** into a single research request
     - **Number of queries**: Typically 1-6 (from `mapPersonaQueries`)

**Polling Calls:**
- **Internal task polling**: `blogWriterApi.pollResearchStatus()`
- **Not external API calls** (internal task status checks)
- **Polling frequency**: Every 2.5 seconds, max 120 attempts (5 minutes)

**Total Phase 2**: **1 external API call** (fixed per research operation)

---

### Phase 3: Script Generation (`generateScript`)

**External API Calls:**
1. **Gemini LLM** - Story outline generation
   - **Endpoint**: `/api/story/generate-outline`
   - **Backend**: `storyWriterApi.generateOutline()`
   - **Service**: `backend/services/story_writer/service_components/outline.py`
   - **Function**: `llm_text_gen()` → Gemini API
   - **Calls per script**: **1 call**
   - **Scaling**: 
     - **Fixed per script generation** (1 call regardless of duration)
     - **Duration affects output length** (more scenes), but not number of API calls

**Total Phase 3**: **1 external API call** (fixed)

---

### Phase 4: Audio Rendering (`renderSceneAudio`)

**External API Calls:**
1. **WaveSpeed → Minimax Speech 02 HD** - Text-to-Speech
   - **Endpoint**: `/api/story/generate-audio`
   - **Backend**: `storyWriterApi.generateAIAudio()`
   - **Service**: `backend/services/wavespeed/client.py::generate_speech()`
   - **External API**: WaveSpeed API → Minimax Speech 02 HD
   - **Calls per scene**: **1 call per scene**
   - **Scaling with duration**:
     - **Number of scenes** = `Math.ceil((duration * 60) / scene_length_target)`
     - **Default scene_length_target**: 45 seconds
     - **Example calculations**:
       - 5 minutes → `ceil(300 / 45)` = **7 scenes** = **7 TTS calls**
       - 10 minutes → `ceil(600 / 45)` = **14 scenes** = **14 TTS calls**
       - 15 minutes → `ceil(900 / 45)` = **20 scenes** = **20 TTS calls**
       - 30 minutes → `ceil(1800 / 45)` = **40 scenes** = **40 TTS calls**
   - **Scaling with speakers**:
     - **Fixed per scene** (1 call per scene regardless of speakers)
     - **Speakers affect text splitting** (lines per speaker), but not API calls
   - **Text length per call**:
     - **Characters per scene** ≈ `(scene_length_target * 15)` (assuming ~15 chars/second)
     - **5-minute podcast**: ~675 chars/scene × 7 scenes = ~4,725 total chars
     - **30-minute podcast**: ~675 chars/scene × 40 scenes = ~27,000 total chars

**Total Phase 4**: **N external API calls** where **N = number of scenes**

---

### Phase 5: Video Rendering (`generateVideo`) - Optional

**External API Calls:**
1. **WaveSpeed → InfiniteTalk** - Avatar animation
   - **Endpoint**: `/api/podcast/render/video`
   - **Backend**: `podcastApi.generateVideo()`
   - **Service**: `backend/services/wavespeed/infinitetalk.py::animate_scene_with_voiceover()`
   - **External API**: WaveSpeed API → InfiniteTalk
   - **Calls per scene**: **1 call per scene** (if video is generated)
   - **Scaling with duration**:
     - **Same as audio rendering**: 1 call per scene
     - **5 minutes**: **7 video calls**
     - **10 minutes**: **14 video calls**
     - **15 minutes**: **20 video calls**
     - **30 minutes**: **40 video calls**
   - **Scaling with speakers**:
     - **Fixed per scene** (1 call per scene regardless of speakers)
     - **Avatar image is provided** (not generated per speaker)

**Polling Calls:**
- **Internal task polling**: `podcastApi.pollTaskStatus()`
- **Not external API calls** (internal task status checks)
- **Polling frequency**: Every 2.5 seconds until completion (can take up to 10 minutes per video)

**Total Phase 5**: **N external API calls** where **N = number of scenes** (if video is enabled)

---

## Summary: Total External API Calls

### Minimum Workflow (No Video, 5-minute podcast)
1. Project Creation: **1 call** (Gemini - story setup)
2. Research: **1 call** (Google Grounding or Exa)
3. Script Generation: **1 call** (Gemini - outline)
4. Audio Rendering: **7 calls** (Minimax TTS - 7 scenes)
5. Video Rendering: **0 calls** (not enabled)

**Total**: **10 external API calls** for a 5-minute podcast

### Full Workflow (With Video, 5-minute podcast)
1. Project Creation: **1 call** (Gemini - story setup)
2. Research: **1 call** (Google Grounding or Exa)
3. Script Generation: **1 call** (Gemini - outline)
4. Audio Rendering: **7 calls** (Minimax TTS - 7 scenes)
5. Video Rendering: **7 calls** (InfiniteTalk - 7 scenes)

**Total**: **17 external API calls** for a 5-minute podcast

### Scaling with Duration

| Duration | Scenes | Audio Calls | Video Calls | Total (Audio Only) | Total (Audio + Video) |
|----------|--------|-------------|-------------|-------------------|----------------------|
| 5 min    | 7      | 7           | 7           | 10                | 17                   |
| 10 min   | 14     | 14          | 14          | 17                | 31                   |
| 15 min   | 20     | 20          | 20          | 23                | 43                   |
| 30 min   | 40     | 40          | 40          | 43                | 83                   |

**Formula**: 
- **Scenes** = `ceil((duration_minutes * 60) / scene_length_target)`
- **Total (Audio Only)** = `3 + scenes` (3 fixed + N scenes)
- **Total (Audio + Video)** = `3 + (scenes * 2)` (3 fixed + N audio + N video)

---

## Scaling Factors

### 1. Duration
- **Impact**: Linear scaling of rendering calls (audio + video)
- **Fixed calls**: 3 (setup, research, script)
- **Variable calls**: `2 * scenes` (if video enabled) or `1 * scenes` (audio only)
- **Scene count formula**: `ceil((duration * 60) / scene_length_target)`

### 2. Number of Speakers
- **Impact**: **No impact on external API calls**
- **Reason**: 
  - Text is split into lines per speaker **before** API calls
  - Each scene makes **1 TTS call** regardless of speaker count
  - Video uses **1 avatar image** (not per speaker)

### 3. Scene Length Target
- **Impact**: Affects number of scenes (and thus rendering calls)
- **Default**: 45 seconds
- **Shorter scenes** = More scenes = More API calls
- **Longer scenes** = Fewer scenes = Fewer API calls

### 4. Research Provider
- **Impact**: **No impact on call count**
- **Google Grounding**: 1 call (batched)
- **Exa**: 1 call (batched)
- **Both**: Same number of calls

### 5. Video Generation
- **Impact**: **Doubles rendering calls** (adds 1 call per scene)
- **Audio only**: `N` calls (N = scenes)
- **Audio + Video**: `2N` calls (N audio + N video)

---

## Cost Implications

### API Call Costs (Estimated)

1. **Gemini LLM** (Story Setup & Script):
   - **Setup**: ~2,000 tokens → ~$0.001-0.002
   - **Outline**: ~3,000-5,000 tokens → ~$0.002-0.005
   - **Total**: ~$0.003-0.007 per podcast

2. **Google Grounding** (Research):
   - **Per research**: ~1,200 tokens → ~$0.001-0.002
   - **Fixed cost** regardless of query count

3. **Exa Neural Search** (Alternative):
   - **Per research**: ~$0.005 (flat rate)
   - **Fixed cost** regardless of query count

4. **Minimax TTS** (Audio):
   - **Per scene**: ~$0.05 per 1,000 characters
   - **5-minute podcast**: ~4,725 chars → ~$0.24
   - **30-minute podcast**: ~27,000 chars → ~$1.35
   - **Scales linearly with duration**

5. **InfiniteTalk** (Video):
   - **Per scene**: ~$0.03-0.06 per second (depending on resolution)
   - **5-minute podcast**: 7 scenes × 45s × $0.03 = ~$9.45
   - **30-minute podcast**: 40 scenes × 45s × $0.03 = ~$54.00
   - **Scales linearly with duration**

### Total Cost Examples

| Duration | Audio Only | Audio + Video (720p) |
|----------|-----------|---------------------|
| 5 min    | ~$0.25    | ~$9.50              |
| 10 min   | ~$0.50    | ~$19.00             |
| 15 min   | ~$0.75    | ~$28.50             |
| 30 min   | ~$1.50    | ~$57.00             |

**Note**: Costs are estimates and may vary based on actual API pricing, text length, and video resolution.

---

## Optimization Opportunities

1. **Batch TTS Calls**: Currently 1 call per scene. Could batch multiple scenes if API supports it.
2. **Cache Research Results**: Already implemented for exact keyword matches.
3. **Parallel Rendering**: Audio and video rendering could be parallelized per scene.
4. **Scene Length Optimization**: Longer scenes = fewer API calls (but may reduce quality).
5. **Video Optional**: Video generation doubles costs - make it optional/on-demand.

---

## Internal vs External Calls

### Internal (Not Counted as External)
- Preflight validation checks (`/api/billing/preflight`)
- Task status polling (`/api/story/task/{taskId}/status`)
- Project persistence (`/api/podcast/projects/*`)
- Content asset library (`/api/content-assets/*`)

### External (Counted)
- Gemini LLM (story setup, script generation)
- Google Grounding (research)
- Exa (research alternative)
- WaveSpeed → Minimax TTS (audio)
- WaveSpeed → InfiniteTalk (video)

---

## Conclusion

**Key Findings:**
1. **Fixed overhead**: 3 external API calls per podcast (setup, research, script)
2. **Variable overhead**: 1-2 calls per scene (audio, optionally video)
3. **Duration is the primary scaling factor** for rendering calls
4. **Number of speakers does NOT affect API call count**
5. **Video generation doubles rendering API calls**

**Recommendations:**
- Monitor API call counts and costs per podcast duration
- Consider batching strategies for TTS calls if supported
- Make video generation optional/on-demand to reduce costs
- Optimize scene length to balance quality vs. API call count



