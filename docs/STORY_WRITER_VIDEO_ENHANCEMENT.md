# Story Writer Video Generation Enhancement Plan

## Executive Summary

This document outlines the immediate enhancement plan for ALwrity's Story Writer to replace problematic HuggingFace video generation with WaveSpeed AI models and upgrade basic gTTS audio to professional voice cloning. This provides immediate value to users while solving current technical issues.

---

## Current State Analysis

### Current Video Generation
- **Provider**: HuggingFace (tencent/HunyuanVideo via fal-ai)
- **Issues**: 
  - Unreliable API responses
  - Limited quality control
  - No audio synchronization
  - Single provider dependency
  - Poor error handling

### Current Audio Generation
- **Provider**: gTTS (Google Text-to-Speech)
- **Limitations**:
  - Robotic, non-natural voice
  - No brand voice consistency
  - Limited language options
  - No emotion control
  - Cannot clone user's voice

### Current Story Writer Workflow
1. User creates story outline with scenes
2. Each scene has `audio_narration` text
3. Audio generated via gTTS per scene
4. Video generated via HuggingFace per scene
5. Videos compiled into final story video

**Location**: `backend/api/story_writer/` and `frontend/src/components/StoryWriter/`

---

## Proposed Enhancements

### Core Principles

**Provider Abstraction**: 
- Users should NOT see provider names (HuggingFace, WaveSpeed, etc.)
- All provider routing/switching happens automatically in the background
- Users only see user-friendly options like "Standard Quality" or "Premium Quality"
- System automatically selects best available provider based on user's subscription and credits

**Preserve Existing Options**:
- gTTS remains available as free fallback when credits run out
- HuggingFace remains available as fallback option
- All existing functionality preserved
- New features are additions, not replacements

**Cost Transparency**:
- All buttons show cost information in tooltips
- Users make informed decisions before generating
- No surprise costs

---

### 1. Provider-Agnostic Video Generation System

#### 1.1 Smart Provider Routing

**Backend Implementation** (`backend/services/llm_providers/main_video_generation.py`):

```python
def ai_video_generate(
    prompt: str,
    quality: str = "standard",  # "standard" (480p), "high" (720p), "premium" (1080p)
    duration: int = 5,
    audio_file_path: Optional[str] = None,
    user_id: str,
    **kwargs,
) -> bytes:
    """
    Unified video generation entry point.
    Automatically routes to best available provider:
    - WaveSpeed WAN 2.5 (primary, if credits available)
    - HuggingFace (fallback, if WaveSpeed unavailable)
    
    Users never see provider names - only quality options.
    """
    # 1. Check user subscription and credits
    # 2. Select best available provider automatically
    # 3. Route to appropriate provider function
    # 4. Handle fallbacks transparently
    pass

def _select_video_provider(
    user_id: str,
    quality: str,
    pricing_service: PricingService,
) -> Tuple[str, str]:
    """
    Automatically select best video provider.
    Returns: (provider_name, model_name)
    
    Selection logic:
    1. Check user credits/subscription
    2. Prefer WaveSpeed if available and credits sufficient
    3. Fallback to HuggingFace if WaveSpeed unavailable
    4. Return error if no providers available
    """
    # Implementation details...
```

**Key Features**:
- Automatic provider selection (users don't choose)
- Seamless fallback between providers
- Quality-based options (Standard/High/Premium) instead of provider names
- Cost-aware routing (uses cheapest available option)
- Transparent error handling

**Quality Mapping**:
- **Standard Quality** (480p): $0.05/second - Uses WaveSpeed 480p or HuggingFace
- **High Quality** (720p): $0.10/second - Uses WaveSpeed 720p
- **Premium Quality** (1080p): $0.15/second - Uses WaveSpeed 1080p

**Cost Optimization**:
- Default to Standard Quality (480p) for cost-effectiveness
- Allow upgrade to High/Premium for final export
- Pre-flight validation prevents waste
- Automatic fallback to free options when credits exhausted

---

### 2. Enhanced Audio Generation with Voice Cloning

#### 2.1 User-Friendly Voice Selection

**Key Principle**: Users choose between "AI Clone Voice" or "Default Voice" (gTTS) - no provider names shown.

**Backend Implementation** (`backend/services/story_writer/audio_generation_service.py`):

```python
class StoryAudioGenerationService:
    def generate_scene_audio(
        self,
        scene: Dict[str, Any],
        user_id: str,
        use_ai_voice: bool = False,  # User's choice: AI Clone or Default
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Generate audio with automatic provider selection.
        
        If use_ai_voice=True:
            - Try persona voice clone (if trained)
            - Try Minimax voice clone (if credits available)
            - Fallback to gTTS if no credits
        
        If use_ai_voice=False:
            - Use gTTS (always free, always available)
        """
        if use_ai_voice:
            # Try AI voice options
            if self._has_persona_voice(user_id):
                return self._generate_with_persona_voice(scene, user_id)
            elif self._has_credits_for_voice_clone(user_id):
                return self._generate_with_minimax_voice_clone(scene, user_id)
            else:
                # Fallback to gTTS with notification
                logger.info(f"Credits exhausted, falling back to gTTS for user {user_id}")
                return self._generate_with_gtts(scene, **kwargs)
        else:
            # User explicitly chose default voice
            return self._generate_with_gtts(scene, **kwargs)
```

**Voice Options in Story Setup**:
- **Default Voice (gTTS)**: Free, always available, robotic but functional
- **AI Clone Voice**: Natural, human-like, requires credits ($0.02/minute)

**Cost Considerations**:
- Voice training: One-time cost (~$0.75) - only if user wants to train custom voice
- Voice generation: ~$0.02 per minute (only when AI Clone Voice selected)
- gTTS: Always free, always available as fallback
- Automatic fallback to gTTS when credits exhausted (with user notification)

---

### 3. Enhanced Story Setup UI

#### 3.1 Video Generation Settings (Provider-Agnostic)

**Location**: `frontend/src/components/StoryWriter/Phases/StorySetup/GenerationSettingsSection.tsx`

**User-Friendly Settings** (No Provider Names):
```typescript
interface VideoGenerationSettings {
  // Quality selection (NOT provider selection)
  videoQuality: 'standard' | 'high' | 'premium';  // Maps to 480p/720p/1080p
  
  // Duration
  videoDuration: 5 | 10;  // seconds
  
  // Cost estimation (shown in tooltip)
  estimatedCostPerScene: number;
  totalEstimatedCost: number;
  
  // Provider routing happens automatically in backend
  // Users never see "WaveSpeed" or "HuggingFace"
}
```

**UI Components**:
- Quality selector: "Standard" / "High" / "Premium" (with cost in tooltip)
- Duration selector: 5s (default) / 10s (premium)
- Cost tooltip: Shows estimated cost per scene and total
- Pre-flight validation warnings
- **No provider selector** - routing is automatic

**Tooltip Example**:
```
Standard Quality (480p)
├─ Cost: $0.25 per scene (5 seconds)
├─ Quality: Good for previews and testing
└─ Provider: Automatically selected based on credits
```

#### 3.2 Audio Generation Settings (Simple Choice)

**New Settings**:
```typescript
interface AudioGenerationSettings {
  // Simple user choice - no provider names
  voiceType: 'default' | 'ai_clone';  // "Default Voice" or "AI Clone Voice"
  
  // Only shown if ai_clone selected
  voiceTrainingStatus: 'not_trained' | 'training' | 'ready' | 'failed';
  
  // Existing gTTS settings (preserved)
  audioLang: string;
  audioSlow: boolean;
  audioRate: number;
}
```

**UI Components**:
- **Voice Type Selector**: 
  - "Default Voice (gTTS)" - Free, always available
  - "AI Clone Voice" - Natural, $0.02/minute (with cost tooltip)
- Voice training section (only if AI Clone Voice selected)
- Existing gTTS settings (preserved for Default Voice)
- Cost per minute display in tooltip

**Tooltip for "AI Clone Voice"**:
```
AI Clone Voice
├─ Cost: $0.02 per minute
├─ Quality: Natural, human-like narration
├─ Fallback: Automatically uses Default Voice if credits exhausted
└─ Training: One-time $0.75 to train your custom voice (optional)
```

**Tooltip for "Default Voice"**:
```
Default Voice (gTTS)
├─ Cost: Free
├─ Quality: Standard text-to-speech
└─ Always Available: Works even when credits exhausted
```

---

### 4. New "Animate Scene" Feature in Outline Phase

#### 4.1 Per-Scene Animation Preview

**Location**: `frontend/src/components/StoryWriter/Phases/StoryOutline.tsx`

**Feature**: Add "Animate Scene" hover option alongside existing scene actions

**Implementation**:
- Add to `OutlineHoverActions` component
- Appears on hover over scene cards
- Only generates for single scene (never bulk)
- Uses cheapest option (480p/Standard Quality) to give users a feel
- Shows cost in tooltip before generation

**UI Component**:
```typescript
// In OutlineHoverActions.tsx
const sceneHoverActions = [
  // Existing actions...
  {
    icon: <PlayArrowIcon />,
    label: 'Animate Scene',
    action: 'animate-scene',
    tooltip: `Animate this scene with video\nCost: ~$0.25 (5 seconds, Standard Quality)\nPreview only - uses cheapest option`,
    onClick: handleAnimateScene,
  },
];
```

**Backend Endpoint**:
```python
@router.post("/animate-scene-preview")
async def animate_scene_preview(
    request: SceneAnimationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> SceneAnimationResponse:
    """
    Generate preview animation for a single scene.
    Always uses cheapest option (480p/Standard Quality).
    Per-scene only - never bulk generation.
    """
    # 1. Validate single scene only
    # 2. Use Standard Quality (480p) - cheapest option
    # 3. Generate video with automatic provider routing
    # 4. Return preview video URL
    pass
```

**Cost Management**:
- Always uses Standard Quality (480p) - $0.25 per scene
- Pre-flight validation before generation
- Clear cost display in tooltip
- Per-scene only prevents bulk waste

---

### 5. New "Animate Story with VoiceOver" Button in Writing Phase

#### 5.1 Complete Story Animation

**Location**: `frontend/src/components/StoryWriter/Phases/StoryWriting.tsx`

**Feature**: New button alongside existing HuggingFace video options

**Implementation**:
- Add button in Writing phase toolbar
- Generates complete animated story with synchronized voiceover
- Uses user's voice preference from Setup (AI Clone or Default)
- Shows comprehensive cost breakdown in tooltip
- Pre-flight validation before generation

**UI Component**:
```typescript
<Button
  variant="contained"
  startIcon={<SmartDisplayIcon />}
  onClick={handleAnimateStoryWithVoiceOver}
  disabled={!state.storyContent || isGenerating}
  title={`Animate Story with VoiceOver\n\nCost Breakdown:\n- Video: $${videoCost} (${scenes.length} scenes × $${costPerScene})\n- Audio: $${audioCost} (${totalAudioMinutes} minutes)\n- Total: $${totalCost}\n\nQuality: ${state.videoQuality}\nVoice: ${state.voiceType === 'ai_clone' ? 'AI Clone' : 'Default'}`}
>
  Animate Story with VoiceOver
</Button>
```

**Backend Endpoint**:
```python
@router.post("/animate-story-with-voiceover")
async def animate_story_with_voiceover(
    request: StoryAnimationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> StoryAnimationResponse:
    """
    Generate complete animated story with synchronized voiceover.
    Uses user's quality and voice preferences from Setup.
    """
    # 1. Pre-flight validation (cost, credits, limits)
    # 2. Generate audio for all scenes (using user's voice preference)
    # 3. Generate videos for all scenes (using user's quality preference)
    # 4. Synchronize audio with video
    # 5. Compile into final story video
    # 6. Return video URL and cost breakdown
    pass
```

**Cost Tooltip Example**:
```
Animate Story with VoiceOver

Cost Breakdown:
├─ Video (Standard Quality): $2.50
│  └─ 10 scenes × $0.25 per scene
├─ Audio (AI Clone Voice): $1.00
│  └─ 50 minutes total × $0.02/minute
└─ Total: $3.50

Settings:
├─ Quality: Standard (480p)
├─ Voice: AI Clone Voice
└─ Duration: 5 seconds per scene

⚠️ This will use $3.50 of your monthly credits
```

---

## Implementation Phases

### Phase 1: Provider-Agnostic Video System (Week 1-2)

**Priority**: HIGH - Solves immediate HuggingFace issues with provider abstraction

**Tasks**:
1. ✅ Create WaveSpeed API client (`backend/services/wavespeed/client.py`)
2. ✅ Add WAN 2.5 text-to-video function
3. ✅ Implement smart provider routing in `main_video_generation.py`
4. ✅ Add quality-based selection (Standard/High/Premium)
5. ✅ Preserve HuggingFace as fallback option
6. ✅ Update `hd_video.py` with provider routing
7. ✅ Add pre-flight cost validation
8. ✅ Update frontend with quality selector (remove provider names)
9. ✅ Add cost tooltips to all buttons
10. ✅ Update subscription limits
11. ✅ Testing and error handling

**Files to Modify**:
- `backend/services/llm_providers/main_video_generation.py` (add routing logic)
- `backend/api/story_writer/utils/hd_video.py` (use quality-based API)
- `backend/api/story_writer/routes/video_generation.py`
- `frontend/src/components/StoryWriter/Phases/StorySetup/GenerationSettingsSection.tsx` (quality selector)
- `frontend/src/components/StoryWriter/components/HdVideoSection.tsx`
- `backend/services/subscription/pricing_service.py`

**Success Criteria**:
- Video generation works reliably with automatic provider routing
- Users see quality options, not provider names
- HuggingFace preserved as fallback
- Cost tracking accurate
- Pre-flight validation prevents waste
- Error messages clear and actionable

---

### Phase 2: Voice Cloning Integration (Week 3-4)

**Priority**: MEDIUM - Enhances audio quality with simple user choice

**Tasks**:
1. ✅ Create Minimax API client (`backend/services/minimax/voice_clone.py`)
2. ✅ Add voice training endpoint
3. ✅ Add voice generation endpoint
4. ✅ Update `audio_generation_service.py` with "AI Clone" vs "Default" logic
5. ✅ Preserve gTTS as always-available fallback
6. ✅ Add automatic fallback when credits exhausted
7. ✅ Update Story Setup with simple voice type selector
8. ✅ Add cost tooltips to voice options
9. ✅ Add voice preview and testing (if AI Clone selected)
10. ✅ Ensure gTTS always works even when credits exhausted

**Files to Create**:
- `backend/services/minimax/voice_clone.py`
- `backend/services/story_writer/voice_management_service.py`

**Files to Modify**:
- `backend/services/story_writer/audio_generation_service.py` (add voice type logic)
- `frontend/src/components/StoryWriter/Phases/StorySetup/GenerationSettingsSection.tsx` (voice type selector)
- `backend/models/story_models.py` (add voice type field)

**Success Criteria**:
- Users see simple choice: "Default Voice" or "AI Clone Voice"
- gTTS always available as fallback
- Automatic fallback when credits exhausted
- Cost tracking accurate
- Voice quality significantly better than gTTS when AI Clone used

---

### Phase 3: New Features - Animate Scene & Animate Story (Week 5-6)

**Priority**: MEDIUM - Add preview and complete animation features

**Tasks**:
1. ✅ Add "Animate Scene" hover option in Outline phase
2. ✅ Implement per-scene animation preview (cheapest option only)
3. ✅ Add "Animate Story with VoiceOver" button in Writing phase
4. ✅ Implement complete story animation with voiceover
5. ✅ Add comprehensive cost tooltips to all buttons
6. ✅ Add pre-flight validation for all animation features
7. ✅ Ensure per-scene only (no bulk generation in Outline)
8. ✅ Update documentation
9. ✅ User testing and feedback

**Files to Create**:
- `backend/api/story_writer/routes/scene_animation.py` (new endpoint)
- `frontend/src/components/StoryWriter/components/AnimateSceneButton.tsx`

**Files to Modify**:
- `frontend/src/components/StoryWriter/Phases/StoryOutlineParts/OutlineHoverActions.tsx` (add Animate Scene)
- `frontend/src/components/StoryWriter/Phases/StoryWriting.tsx` (add Animate Story button)
- `backend/api/story_writer/routes/video_generation.py` (add story animation endpoint)

**Success Criteria**:
- "Animate Scene" works in Outline (per-scene, cheapest option)
- "Animate Story with VoiceOver" works in Writing phase
- All buttons show cost in tooltips
- Pre-flight validation prevents waste
- Good user experience

---

### Phase 4: Integration & Optimization (Week 7-8)

**Priority**: MEDIUM - Polish and optimize

**Tasks**:
1. ✅ Integrate audio with video (synchronized videos)
2. ✅ Improve error handling and retry logic
3. ✅ Add progress indicators
4. ✅ Optimize cost calculations
5. ✅ Add usage analytics
6. ✅ Update documentation
7. ✅ User testing and feedback

**Success Criteria**:
- Smooth end-to-end workflow
- Cost-effective for users
- Reliable generation
- Excellent user experience
- All features work seamlessly together

---

## Cost Management & Prevention of Waste

### Pre-Flight Validation

**Implementation**: `backend/services/subscription/preflight_validator.py`

**Checks Before Generation**:
1. User has sufficient subscription tier
2. Estimated cost within monthly budget
3. Video generation limit not exceeded
4. Audio generation limit not exceeded
5. Total story cost reasonable (<$5 for typical story)

**Validation Flow**:
```python
def validate_story_generation(
    pricing_service: PricingService,
    user_id: str,
    num_scenes: int,
    video_resolution: str,
    video_duration: int,
    use_voice_clone: bool,
) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Pre-flight validation before story generation.
    Returns: (allowed, message, cost_breakdown)
    """
    # Calculate estimated costs
    video_cost_per_scene = get_wavespeed_cost(video_resolution, video_duration)
    audio_cost_per_scene = get_voice_clone_cost() if use_voice_clone else 0.0
    
    total_estimated_cost = (video_cost_per_scene + audio_cost_per_scene) * num_scenes
    
    # Check limits
    limits = pricing_service.get_user_limits(user_id)
    current_usage = pricing_service.get_current_usage(user_id)
    
    # Validation logic...
    return (allowed, message, cost_breakdown)
```

### Cost Estimation Display

**Frontend Implementation**:
- Real-time cost calculator in Story Setup
- Per-scene cost breakdown
- Total story cost estimate
- Monthly budget remaining
- Warning if approaching limits

**UI Example**:
```
Video Generation Cost Estimate:
├─ Resolution: 720p ($0.10/second)
├─ Duration: 5 seconds per scene
├─ Scenes: 10
└─ Total: $5.00

Audio Generation Cost Estimate:
├─ Provider: Voice Clone ($0.02/minute)
├─ Average: 30 seconds per scene
├─ Scenes: 10
└─ Total: $1.00

Total Estimated Cost: $6.00
Monthly Budget Remaining: $44.00
```

### Usage Tracking

**Enhanced Tracking**:
- Track video generation per scene
- Track audio generation per scene
- Track total story cost
- Alert users approaching limits
- Provide cost breakdown in analytics

---

## Pricing Integration

### WaveSpeed WAN 2.5 Pricing

**Add to `pricing_service.py`**:
```python
# WaveSpeed WAN 2.5 Text-to-Video
{
    "provider": APIProvider.VIDEO,  # Or new WAVESPEED provider
    "model_name": "wan-2.5-480p",
    "cost_per_second": 0.05,
    "description": "WaveSpeed WAN 2.5 Text-to-Video (480p)"
},
{
    "provider": APIProvider.VIDEO,
    "model_name": "wan-2.5-720p",
    "cost_per_second": 0.10,
    "description": "WaveSpeed WAN 2.5 Text-to-Video (720p)"
},
{
    "provider": APIProvider.VIDEO,
    "model_name": "wan-2.5-1080p",
    "cost_per_second": 0.15,
    "description": "WaveSpeed WAN 2.5 Text-to-Video (1080p)"
}
```

### Minimax Voice Clone Pricing

**Add to `pricing_service.py`**:
```python
# Minimax Voice Clone
{
    "provider": APIProvider.AUDIO,  # New provider type
    "model_name": "minimax-voice-clone-train",
    "cost_per_request": 0.75,  # One-time training cost
    "description": "Minimax Voice Clone Training"
},
{
    "provider": APIProvider.AUDIO,
    "model_name": "minimax-voice-clone-generate",
    "cost_per_minute": 0.02,  # Per minute of generated audio
    "description": "Minimax Voice Clone Generation"
}
```

### Subscription Tier Limits

**Update subscription limits**:
- **Free**: 3 stories/month, 480p only, gTTS only
- **Basic**: 10 stories/month, up to 720p, voice clone available
- **Pro**: 50 stories/month, up to 1080p, voice clone included
- **Enterprise**: Unlimited, all features

---

## Technical Architecture

### Backend Services

```
backend/services/
├── wavespeed/
│   ├── __init__.py
│   ├── client.py              # WaveSpeed API client
│   ├── wan25_video.py        # WAN 2.5 video generation
│   └── models.py              # Request/response models
├── minimax/
│   ├── __init__.py
│   ├── client.py              # Minimax API client
│   ├── voice_clone.py         # Voice cloning service
│   └── models.py
└── story_writer/
    ├── audio_generation_service.py  # Updated with voice clone
    └── video_generation_service.py   # Updated with WaveSpeed
```

### Frontend Components

```
frontend/src/components/StoryWriter/
├── Phases/StorySetup/
│   └── GenerationSettingsSection.tsx  # Enhanced with new settings
├── components/
│   ├── HdVideoSection.tsx              # Updated for WaveSpeed
│   ├── VoiceTrainingSection.tsx        # NEW: Voice training UI
│   └── CostEstimationDisplay.tsx        # NEW: Cost calculator
└── hooks/
    └── useStoryGenerationCost.ts        # NEW: Cost calculation hook
```

---

## Error Handling & User Experience

### Error Scenarios

1. **WaveSpeed API Failure**:
   - Retry with exponential backoff (3 attempts)
   - Fallback to HuggingFace if available
   - Clear error message with cost refund notice

2. **Voice Clone Training Failure**:
   - Provide specific error (audio quality, length, format)
   - Suggest improvements
   - Allow retry with different audio

3. **Cost Limit Exceeded**:
   - Pre-flight validation prevents this
   - Show upgrade prompt
   - Suggest reducing scenes/resolution

4. **Audio/Video Mismatch**:
   - Validate audio length matches video duration
   - Auto-trim or extend audio
   - Warn user before generation

### User Feedback

- Progress indicators for all operations
- Clear cost breakdowns
- Quality previews before final generation
- Regeneration options with cost tracking
- Usage analytics dashboard

---

## Testing Plan

### Unit Tests
- WaveSpeed API client
- Voice clone service
- Cost calculation
- Pre-flight validation

### Integration Tests
- End-to-end story generation
- Audio + video synchronization
- Error handling and fallbacks
- Subscription limit enforcement

### User Acceptance Tests
- Story generation workflow
- Voice training process
- Cost estimation accuracy
- Error recovery

---

## Success Metrics

### Technical Metrics
- Video generation success rate >95%
- Audio generation success rate >98%
- Average generation time per scene <30s
- API error rate <2%

### Business Metrics
- User satisfaction with video quality
- Cost per story (target: <$5 for 10-scene story)
- Voice clone adoption rate
- Story completion rate

### User Experience Metrics
- Time to generate story
- Error recovery time
- User understanding of costs
- Feature discovery rate

---

## Provider Management Strategy

### Always-Available Options
- **gTTS**: Always available, always free, works even when credits exhausted
- **HuggingFace**: Preserved as fallback option, works when WaveSpeed unavailable

### Automatic Provider Routing
- **Primary**: WaveSpeed WAN 2.5 (when credits available)
- **Fallback**: HuggingFace (when WaveSpeed unavailable or credits exhausted)
- **Audio Fallback**: gTTS (always available, always free)

### User Experience
- Users never see provider names
- System automatically selects best available option
- Seamless fallback when credits exhausted
- Clear notifications when fallback occurs
- No user intervention required

### No Deprecation
- **HuggingFace**: Kept as permanent fallback option
- **gTTS**: Kept as permanent free option
- All existing functionality preserved
- New features are additions, not replacements

---

## Next Steps

1. **Week 1**: Set up WaveSpeed API access and credentials
2. **Week 1**: Implement provider-agnostic routing system
3. **Week 2**: Integrate into Story Writer with quality-based UI
4. **Week 3**: Implement voice cloning with simple "AI Clone" vs "Default" choice
5. **Week 4**: Add voice training UI (only if AI Clone selected)
6. **Week 5**: Add "Animate Scene" hover option in Outline
7. **Week 6**: Add "Animate Story with VoiceOver" button in Writing
8. **Week 7-8**: Testing, optimization, and polish

## Key Design Principles

1. **Provider Abstraction**: Users never see provider names - only quality/voice options
2. **Preserve Existing**: gTTS and HuggingFace remain available as fallbacks
3. **Cost Transparency**: All buttons show costs in tooltips
4. **Automatic Fallback**: System automatically uses free options when credits exhausted
5. **Per-Scene Only**: Outline phase only allows per-scene generation (no bulk)
6. **User-Friendly**: Simple choices like "Standard Quality" not "WaveSpeed 480p"

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| WaveSpeed API changes | Version pinning, abstraction layer |
| Cost overruns | Strict pre-flight validation |
| Voice quality issues | Quality checks, fallback options |
| User confusion | Clear UI, tooltips, documentation |
| Integration complexity | Phased rollout, extensive testing |

---

*Document Version: 1.0*  
*Last Updated: January 2025*  
*Priority: HIGH - Immediate Implementation*

