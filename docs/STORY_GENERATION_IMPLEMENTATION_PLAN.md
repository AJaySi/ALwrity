# Story Generation Feature - Implementation Plan

## Executive Summary

This document reviews the existing story generation backend modules and provides a comprehensive plan to complete the story generation feature with a modern UI using CopilotKit, similar to the AI Blog Writer implementation.

## 1. Current State Review

### 1.1 Existing Backend Modules

#### 1.1.1 Story Writer (`ToBeMigrated/ai_writers/ai_story_writer/`)
**Status**: ✅ Functional but needs migration
**Location**: `ToBeMigrated/ai_writers/ai_story_writer/ai_story_generator.py`

**Features**:
- Prompt chaining approach (premise → outline → starting draft → continuation)
- Supports multiple personas/genres (11 predefined)
- Configurable story parameters:
  - Story setting
  - Characters
  - Plot elements
  - Writing style (Formal, Casual, Poetic, Humorous)
  - Story tone (Dark, Uplifting, Suspenseful, Whimsical)
  - Narrative POV (First Person, Third Person Limited/Omniscient)
  - Audience age group
  - Content rating
  - Ending preference

**Current Implementation**:
- Uses legacy `lib/gpt_providers/text_generation/main_text_generation.py` (needs update)
- Streamlit-based UI (needs React migration)
- Iterative generation until "IAMDONE" marker

**Issues to Address**:
1. ❌ Uses old import path (`...gpt_providers.text_generation.main_text_generation`)
2. ❌ No subscription/user_id integration
3. ❌ No task management/polling support
4. ❌ Streamlit UI (needs React/CopilotKit migration)

#### 1.1.2 Story Illustrator (`ToBeMigrated/ai_writers/ai_story_illustrator/`)
**Status**: ✅ Functional but needs migration
**Location**: `ToBeMigrated/ai_writers/ai_story_illustrator/story_illustrator.py`

**Features**:
- Story segmentation for illustration
- Scene element extraction using LLM
- Multiple illustration styles (12+ options)
- PDF storybook generation
- ZIP export of illustrations

**Current Implementation**:
- Uses legacy import paths
- Streamlit UI
- Integrates with image generation (Gemini)

**Issues to Address**:
1. ❌ Uses old import paths
2. ❌ No subscription integration
3. ❌ Streamlit UI (needs React migration)

#### 1.1.3 Story Video Generator (`ToBeMigrated/ai_writers/ai_story_video_generator/`)
**Status**: ✅ Functional but needs migration
**Location**: `ToBeMigrated/ai_writers/ai_story_video_generator/story_video_generator.py`

**Features**:
- Story generation with scene breakdown
- Image generation per scene
- Text overlay on images
- Video compilation with audio
- Multiple story styles

**Current Implementation**:
- Uses legacy import paths
- Streamlit UI
- MoviePy for video generation

**Issues to Address**:
1. ❌ Uses old import paths
2. ❌ No subscription integration
3. ❌ Streamlit UI (needs React migration)
4. ❌ Heavy dependencies (MoviePy, imageio)

### 1.2 Core Infrastructure Available

#### 1.2.1 Main Text Generation (`backend/services/llm_providers/main_text_generation.py`)
**Status**: ✅ Production-ready
**Features**:
- ✅ Supports Gemini and HuggingFace
- ✅ Subscription/user_id integration
- ✅ Usage tracking
- ✅ Automatic fallback between providers
- ✅ Structured JSON response support

**Usage Pattern**:
```python
from services.llm_providers.main_text_generation import llm_text_gen

response = llm_text_gen(
    prompt="...",
    system_prompt="...",
    json_struct={...},  # Optional
    user_id="clerk_user_id"  # Required
)
```

#### 1.2.2 Subscription System (`backend/models/subscription_models.py`)
**Status**: ✅ Production-ready
**Features**:
- Usage tracking per provider
- Token limits
- Call limits
- Billing period management
- Already integrated with `main_text_generation`

#### 1.2.3 Blog Writer Architecture (Reference)
**Status**: ✅ Production-ready reference implementation

**Key Components**:
1. **Phase Navigation** (`frontend/src/hooks/usePhaseNavigation.ts`)
   - Multi-phase workflow (Research → Outline → Content → SEO → Publish)
   - Phase state management
   - Auto-progression logic

2. **CopilotKit Integration** (`frontend/src/components/BlogWriter/BlogWriterUtils/useBlogWriterCopilotActions.ts`)
   - Action handlers for AI interactions
   - Sidebar suggestions
   - Context-aware actions

3. **Backend Router** (`backend/api/blog_writer/router.py`)
   - RESTful endpoints
   - Task management with polling
   - Cache management
   - Error handling

4. **Task Management** (`backend/api/blog_writer/task_manager.py`)
   - Async task execution
   - Status tracking
   - Result caching

## 2. Implementation Plan

### 2.1 Phase 1: Backend Migration & Enhancement

#### 2.1.1 Create Story Writer Service
**File**: `backend/services/story_writer/story_service.py`

**Tasks**:
1. Migrate `ai_story_generator.py` logic to new service
2. Update imports to use `main_text_generation`
3. Add `user_id` parameter to all LLM calls
4. Implement prompt chaining with proper error handling
5. Add structured JSON response support for outline generation
6. Support both Gemini and HuggingFace through `main_text_generation`

**Key Functions**:
```python
async def generate_story_premise(
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
    user_id: str
) -> str

async def generate_story_outline(
    premise: str,
    persona: str,
    story_setting: str,
    character_input: str,
    plot_elements: str,
    user_id: str
) -> Dict[str, Any]  # Structured outline

async def generate_story_start(
    premise: str,
    outline: str,
    persona: str,
    guidelines: str,
    user_id: str
) -> str

async def continue_story(
    premise: str,
    outline: str,
    story_text: str,
    persona: str,
    guidelines: str,
    user_id: str
) -> str
```

#### 2.1.2 Create Story Writer Router
**File**: `backend/api/story_writer/router.py`

**Endpoints**:
```
POST /api/story/generate-premise
POST /api/story/generate-outline
POST /api/story/generate-start
POST /api/story/continue
POST /api/story/generate-full  # Complete story generation with task management
GET  /api/story/task/{task_id}/status
GET  /api/story/task/{task_id}/result
```

**Request Models**:
```python
class StoryGenerationRequest(BaseModel):
    persona: str
    story_setting: str
    character_input: str
    plot_elements: str
    writing_style: str
    story_tone: str
    narrative_pov: str
    audience_age_group: str
    content_rating: str
    ending_preference: str
```

#### 2.1.3 Task Management Integration
**File**: `backend/api/story_writer/task_manager.py`

**Features**:
- Async story generation with polling
- Progress tracking (premise → outline → start → continuation → done)
- Result caching
- Error recovery

### 2.2 Phase 2: Frontend Implementation

#### 2.2.1 Story Writer Component Structure
**File**: `frontend/src/components/StoryWriter/StoryWriter.tsx`

**Phases** (similar to Blog Writer):
1. **Setup** - Story parameters input
2. **Premise** - Review and refine premise
3. **Outline** - Review and refine outline
4. **Writing** - Generate and edit story content
5. **Illustration** (Optional) - Generate illustrations
6. **Export** - Download/export story

#### 2.2.2 Phase Navigation Hook
**File**: `frontend/src/hooks/useStoryWriterPhaseNavigation.ts`

**Based on**: `usePhaseNavigation.ts` from Blog Writer

**Phases**:
```typescript
interface StoryPhase {
  id: 'setup' | 'premise' | 'outline' | 'writing' | 'illustration' | 'export';
  name: string;
  icon: string;
  description: string;
  completed: boolean;
  current: boolean;
  disabled: boolean;
}
```

#### 2.2.3 CopilotKit Actions
**File**: `frontend/src/components/StoryWriter/StoryWriterUtils/useStoryWriterCopilotActions.ts`

**Actions**:
- `generateStoryPremise` - Generate story premise
- `generateStoryOutline` - Generate outline from premise
- `startStoryWriting` - Begin story generation
- `continueStoryWriting` - Continue story generation
- `refineStoryOutline` - Refine outline based on feedback
- `generateIllustrations` - Generate illustrations for story
- `exportStory` - Export story in various formats

#### 2.2.4 Story Writer UI Components

**Main Components**:
1. `StoryWriter.tsx` - Main container
2. `StorySetup.tsx` - Phase 1: Input story parameters
3. `StoryPremise.tsx` - Phase 2: Review premise
4. `StoryOutline.tsx` - Phase 3: Review/edit outline
5. `StoryContent.tsx` - Phase 4: Generated story content with editor
6. `StoryIllustration.tsx` - Phase 5: Illustration generation (optional)
7. `StoryExport.tsx` - Phase 6: Export options

**Utility Components**:
- `StoryWriterUtils/HeaderBar.tsx` - Phase navigation header
- `StoryWriterUtils/PhaseContent.tsx` - Phase-specific content wrapper
- `StoryWriterUtils/WriterCopilotSidebar.tsx` - CopilotKit sidebar
- `StoryWriterUtils/useStoryWriterState.ts` - State management hook

### 2.3 Phase 3: Integration with Gemini Examples

#### 2.3.1 Prompt Chaining Pattern
**Reference**: https://colab.research.google.com/github/google-gemini/cookbook/blob/main/examples/Story_Writing_with_Prompt_Chaining.ipynb

**Implementation**:
- Use the existing prompt chaining approach from `ai_story_generator.py`
- Enhance with structured JSON responses for outline
- Add better error handling and retry logic
- Support streaming responses (future enhancement)

#### 2.3.2 Illustration Integration
**Reference**: https://github.com/google-gemini/cookbook/blob/main/examples/Book_illustration.ipynb

**Implementation**:
- Migrate `story_illustrator.py` to backend service
- Create API endpoints for illustration generation
- Add illustration phase to frontend
- Support multiple illustration styles

#### 2.3.3 Video Generation (Optional/Future)
**Reference**: https://github.com/google-gemini/cookbook/blob/main/examples/Animated_Story_Video_Generation_gemini.ipynb

**Status**: Defer to Phase 4 (requires heavy dependencies)

### 2.4 Phase 4: Advanced Features (Future)

1. **Story Video Generation**
   - Migrate `story_video_generator.py`
   - Add video generation phase
   - Handle MoviePy dependencies

2. **Story Templates**
   - Pre-defined story templates
   - Genre-specific templates
   - Character templates

3. **Collaborative Editing**
   - Multi-user story editing
   - Version control
   - Comments and suggestions

4. **Story Analytics**
   - Readability metrics
   - Story structure analysis
   - Character development tracking

## 3. Technical Specifications

### 3.1 Backend API Models

```python
# backend/models/story_models.py

class StoryGenerationRequest(BaseModel):
    persona: str
    story_setting: str
    character_input: str
    plot_elements: str
    writing_style: str
    story_tone: str
    narrative_pov: str
    audience_age_group: str
    content_rating: str
    ending_preference: str

class StoryPremiseResponse(BaseModel):
    premise: str
    task_id: Optional[str] = None

class StoryOutlineResponse(BaseModel):
    outline: List[Dict[str, Any]]
    task_id: Optional[str] = None

class StoryContentResponse(BaseModel):
    content: str
    is_complete: bool
    task_id: Optional[str] = None

class StoryIllustrationRequest(BaseModel):
    story_text: str
    style: str = "digital art"
    aspect_ratio: str = "16:9"
    num_segments: int = 5

class StoryIllustrationResponse(BaseModel):
    illustrations: List[str]  # URLs or base64
    segments: List[str]
```

### 3.2 Frontend API Service

```typescript
// frontend/src/services/storyWriterApi.ts

export interface StoryGenerationRequest {
  persona: string;
  story_setting: string;
  character_input: string;
  plot_elements: string;
  writing_style: string;
  story_tone: string;
  narrative_pov: string;
  audience_age_group: string;
  content_rating: string;
  ending_preference: string;
}

export interface StoryPremiseResponse {
  premise: string;
  task_id?: string;
}

export interface StoryOutlineResponse {
  outline: Array<{
    scene_number: number;
    description: string;
    narration?: string;
  }>;
  task_id?: string;
}

export const storyWriterApi = {
  generatePremise: (request: StoryGenerationRequest) => Promise<StoryPremiseResponse>,
  generateOutline: (premise: string, request: StoryGenerationRequest) => Promise<StoryOutlineResponse>,
  generateFullStory: (request: StoryGenerationRequest) => Promise<{ task_id: string }>,
  getTaskStatus: (task_id: string) => Promise<TaskStatus>,
  getTaskResult: (task_id: string) => Promise<StoryContentResponse>,
  // ... more endpoints
};
```

### 3.3 State Management

```typescript
// frontend/src/hooks/useStoryWriterState.ts

interface StoryWriterState {
  // Setup phase
  persona: string;
  storySetting: string;
  characters: string;
  plotElements: string;
  writingStyle: string;
  storyTone: string;
  narrativePOV: string;
  audienceAgeGroup: string;
  contentRating: string;
  endingPreference: string;
  
  // Generation phases
  premise: string | null;
  outline: StoryOutlineSection[] | null;
  storyContent: string | null;
  isComplete: boolean;
  
  // Illustration (optional)
  illustrations: string[];
  
  // Task management
  currentTaskId: string | null;
  generationProgress: number;
}
```

## 4. Migration Checklist

### Backend
- [ ] Create `backend/services/story_writer/story_service.py`
- [ ] Migrate prompt chaining logic from `ai_story_generator.py`
- [ ] Update all imports to use `main_text_generation`
- [ ] Add `user_id` parameter to all LLM calls
- [ ] Create `backend/api/story_writer/router.py`
- [ ] Create `backend/models/story_models.py`
- [ ] Integrate task management (`backend/api/story_writer/task_manager.py`)
- [ ] Add caching support
- [ ] Create `backend/api/story_writer/illustration_service.py` (optional)
- [ ] Register router in `app.py`

### Frontend
- [ ] Create `frontend/src/components/StoryWriter/` directory structure
- [ ] Create `StoryWriter.tsx` main component
- [ ] Create `useStoryWriterPhaseNavigation.ts` hook
- [ ] Create `useStoryWriterState.ts` hook
- [ ] Create `useStoryWriterCopilotActions.ts` hook
- [ ] Create phase components (Setup, Premise, Outline, Writing, Illustration, Export)
- [ ] Create `frontend/src/services/storyWriterApi.ts`
- [ ] Add Story Writer route to App.tsx
- [ ] Style components to match Blog Writer design
- [ ] Add error handling and loading states
- [ ] Implement polling for async tasks

### Testing
- [ ] Unit tests for story service
- [ ] Integration tests for API endpoints
- [ ] E2E tests for complete story generation flow
- [ ] Test with both Gemini and HuggingFace providers
- [ ] Test subscription limits and error handling

## 5. Dependencies

### Backend
- ✅ `main_text_generation` (already available)
- ✅ `subscription_models` (already available)
- ✅ FastAPI (already available)
- ⚠️ Image generation (for illustrations - needs verification)

### Frontend
- ✅ CopilotKit (already available)
- ✅ React (already available)
- ✅ TypeScript (already available)
- ⚠️ Markdown editor (for story content editing - check if available)

## 6. Timeline Estimate

- **Phase 1 (Backend)**: 3-5 days
- **Phase 2 (Frontend Core)**: 5-7 days
- **Phase 3 (CopilotKit Integration)**: 2-3 days
- **Phase 4 (Illustration - Optional)**: 3-4 days
- **Testing & Polish**: 2-3 days

**Total**: ~15-22 days for core features + illustrations

## 7. Key Decisions

1. **Provider Support**: Use `main_text_generation` which supports both Gemini and HuggingFace automatically
2. **UI Pattern**: Follow Blog Writer pattern with phase navigation and CopilotKit integration
3. **Task Management**: Use async task pattern with polling (same as Blog Writer)
4. **Illustration**: Make optional/separate phase to keep core story generation focused
5. **Video Generation**: Defer to future phase due to heavy dependencies

## 8. Next Steps

1. Review and approve this plan
2. Set up backend service structure
3. Begin backend migration
4. Create frontend component structure
5. Implement phase navigation
6. Integrate CopilotKit actions
7. Test end-to-end flow
8. Add illustration support (optional)
9. Polish and documentation
