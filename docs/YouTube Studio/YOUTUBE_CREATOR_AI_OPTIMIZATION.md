# YouTube Creator AI Call Optimization Report

## Current AI Call Analysis

### 1. Video Planning (`planner.py`)
- **Current**: 1 AI call (`llm_text_gen`) to generate video plan
- **Status**: ✅ Optimized - Single call for complete plan
- **Optimization Potential**: None (necessary for quality)

### 2. Scene Generation (`scene_builder.py`)
- **Current**: 
  - 1 AI call (`llm_text_gen`) to generate all scenes
  - Enhancement calls based on duration:
    - Shorts: 0 calls (skip enhancement) ✅
    - Medium: 1 call (batch enhancement) ✅
    - Long: 2 calls (split batch enhancement) ✅
- **Status**: ✅ Already optimized
- **Optimization Potential**: Combine plan + scenes for shorts (save 1 call)

### 3. Audio Generation (`renderer.py`)
- **Current**: 1 external API call per scene (`generate_audio`)
- **Status**: ⚠️ Can be optimized
- **Optimization Potential**: 
  - Shorts: Batch all narrations into 1-2 calls
  - Medium/Long: Batch narrations in groups of 3-5 scenes

### 4. Video Generation (`renderer.py`)
- **Current**: 1 external API call per scene (`generate_text_video` - WaveSpeed)
- **Status**: ✅ Cannot optimize (API limitation - one video per call)
- **Optimization Potential**: None (external API constraint)

## Optimization Strategy

### Shorts (≤60 seconds, ~8 scenes)
**Current**: 1 (plan) + 1 (scenes) + 0 (enhancement) + 8 (audio) = **10 calls**
**Optimized**: 1 (plan+scenes combined) + 0 (enhancement) + 2 (batched audio) = **3 calls**
**Savings**: 70% reduction (7 fewer calls)

### Medium (1-4 minutes, ~12 scenes)
**Current**: 1 (plan) + 1 (scenes) + 1 (enhancement) + 12 (audio) = **15 calls**
**Optimized**: 1 (plan) + 1 (scenes) + 1 (enhancement) + 3 (batched audio) = **6 calls**
**Savings**: 60% reduction (9 fewer calls)

### Long (4-10 minutes, ~20 scenes)
**Current**: 1 (plan) + 1 (scenes) + 2 (enhancement) + 20 (audio) = **24 calls**
**Optimized**: 1 (plan) + 1 (scenes) + 2 (enhancement) + 5 (batched audio) = **9 calls**
**Savings**: 62.5% reduction (15 fewer calls)

## Implementation Plan

1. ✅ Combine plan + scene generation for shorts (save 1 call) - **IMPLEMENTED**
2. ⚠️ Audio generation: Cannot batch (each scene needs separate audio file - external API limitation)
3. ✅ Keep video generation as-is (external API limitation)

## Final Optimized Call Counts

### Shorts (≤60 seconds, ~8 scenes)
**Before**: 1 (plan) + 1 (scenes) + 0 (enhancement) + 8 (audio) = **10 calls**
**After**: 1 (plan+scenes combined) + 0 (enhancement) + 8 (audio) = **9 calls**
**Savings**: 10% reduction (1 fewer call)
**Note**: Audio calls are necessary per scene (external API limitation)

### Medium (1-4 minutes, ~12 scenes)
**Before**: 1 (plan) + 1 (scenes) + 1 (enhancement) + 12 (audio) = **15 calls**
**After**: 1 (plan) + 1 (scenes) + 1 (enhancement) + 12 (audio) = **15 calls**
**Savings**: Already optimized (enhancement batched)
**Note**: Audio calls are necessary per scene (external API limitation)

### Long (4-10 minutes, ~20 scenes)
**Before**: 1 (plan) + 1 (scenes) + 2 (enhancement) + 20 (audio) = **24 calls**
**After**: 1 (plan) + 1 (scenes) + 2 (enhancement) + 20 (audio) = **24 calls**
**Savings**: Already optimized (enhancement batched)
**Note**: Audio calls are necessary per scene (external API limitation)

## Key Optimizations Implemented

1. **Shorts Optimization**: Combined plan + scene generation into single AI call
   - Saves 1 LLM text generation call
   - Maintains quality by generating both in one comprehensive prompt

2. **Scene Enhancement Batching**: Already optimized
   - Shorts: Skip enhancement (0 calls)
   - Medium: Batch all scenes (1 call)
   - Long: Split into 2 batches (2 calls)

3. **Audio Generation**: Cannot be optimized further
   - Each scene requires separate audio file
   - External API (WaveSpeed) limitation - one audio per call
   - This is necessary for quality (each scene has unique narration)

4. **Video Generation**: Cannot be optimized
   - External API (WaveSpeed WAN 2.5) limitation
   - One video per API call is required

## Quality Preservation

All optimizations maintain output quality:
- Combined plan+scenes for shorts uses comprehensive prompt
- Batch enhancement maintains scene consistency
- No quality loss from optimizations

