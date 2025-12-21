# YouTube Creator Operation Helpers

This utility module provides YouTube-specific operation definitions for use with the shared `OperationButton` component.

## Purpose

- **Separation of Concerns**: Keeps YouTube-specific operation logic isolated from shared components
- **Non-Invasive**: No changes required to `OperationButton` or Image Studio
- **Consistent UX**: Provides cost estimation and preflight checks like Image Studio

## Functions

### `buildVideoPlanningOperation(durationType, providerOverride?)`
Builds operation object for video plan generation.

**Token Estimates:**
- Shorts: 9000 tokens (includes scenes in one call)
- Medium: 6000 tokens
- Long: 7000 tokens

### `buildSceneBuildingOperation(durationType, hasPlan, providerOverride?)`
Builds operation object for scene generation.

**Token Estimates:**
- Shorts: 0 tokens (already included in planning)
- Medium: 6500 tokens (base + 1 batch enhancement)
- Long: 10000 tokens (base + 2 batch enhancements)

### `buildImageEditingOperation()`
Builds operation object for image editing (Make Presentable).

### `buildImageGenerationOperation(providerOverride?)`
Builds operation object for image generation (avatars/scenes).

## Usage

```typescript
import { buildVideoPlanningOperation } from '../utils/operationHelpers';

<OperationButton
  operation={buildVideoPlanningOperation(durationType)}
  label="Generate Video Plan"
  onClick={handleGenerate}
  showCost={true}
  checkOnHover={true}
/>
```

## Operation Types

- `video_planning` - YouTube-specific operation type for plan generation
- `scene_building` - YouTube-specific operation type for scene generation
- `image_editing` - Shared operation type (used by Image Studio too)
- `image_generation` - Shared operation type (used by Image Studio too)

## Provider Mapping

- Default: `gemini` (most common)
- HuggingFace: Maps to `mistral` enum for usage tracking
- Backend will use actual provider from `GPT_PROVIDER` env var regardless of frontend estimate

