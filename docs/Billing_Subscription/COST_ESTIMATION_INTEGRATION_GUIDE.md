# Cost Estimation Integration Guide

## Overview

The cost estimation feature allows users to see estimated costs before executing operations. This helps users make informed decisions and avoid unexpected charges.

## Components

### 1. `CostEstimationModal` Component

A reusable modal component that displays cost estimates for operations.

**Location**: `frontend/src/components/billing/CostEstimationModal.tsx`

**Props**:
```typescript
interface CostEstimationModalProps {
  open: boolean;
  onClose: () => void;
  onConfirm: () => void;
  operations: PreflightOperation[];
  userId?: string;
}
```

### 2. `useCostEstimation` Hook

A React hook that manages cost estimation state.

**Location**: `frontend/src/hooks/useCostEstimation.ts`

**Returns**:
```typescript
{
  showEstimation: (operations: PreflightOperation[]) => void;
  estimationOperations: PreflightOperation[];
  isEstimationOpen: boolean;
  closeEstimation: () => void;
}
```

## Usage Example

### Basic Integration

```typescript
import React from 'react';
import { useCostEstimation } from '../../hooks/useCostEstimation';
import CostEstimationModal from '../billing/CostEstimationModal';
import { PreflightOperation } from '../../services/billingService';

const MyComponent: React.FC = () => {
  const { 
    showEstimation, 
    estimationOperations, 
    isEstimationOpen, 
    closeEstimation 
  } = useCostEstimation();

  const handleGenerate = () => {
    // Define operations that will be performed
    const operations: PreflightOperation[] = [
      {
        provider: 'gemini',
        model: 'gemini-2.5-flash',
        operation_type: 'text_generation',
        tokens_requested: 2000
      }
    ];

    // Show cost estimation modal
    showEstimation(operations);
  };

  const performActualOperation = async () => {
    // Your actual operation logic here
    console.log('Performing operation...');
  };

  return (
    <>
      <button onClick={handleGenerate}>
        Generate Content
      </button>

      <CostEstimationModal
        open={isEstimationOpen}
        onClose={closeEstimation}
        onConfirm={performActualOperation}
        operations={estimationOperations}
      />
    </>
  );
};
```

### Advanced Example: Blog Writer

```typescript
import React, { useState } from 'react';
import { useCostEstimation } from '../../hooks/useCostEstimation';
import CostEstimationModal from '../billing/CostEstimationModal';
import { PreflightOperation } from '../../services/billingService';

const BlogWriter: React.FC = () => {
  const [keywords, setKeywords] = useState('');
  const { 
    showEstimation, 
    estimationOperations, 
    isEstimationOpen, 
    closeEstimation 
  } = useCostEstimation();

  const handleGenerateBlog = () => {
    // Estimate costs for blog generation workflow
    // Typically involves: research (1 call) + outline (1 call) + content (1-3 calls)
    const operations: PreflightOperation[] = [
      {
        provider: 'gemini',
        model: 'gemini-2.5-flash',
        operation_type: 'research',
        tokens_requested: 1500
      },
      {
        provider: 'gemini',
        model: 'gemini-2.5-flash',
        operation_type: 'outline_generation',
        tokens_requested: 1000
      },
      {
        provider: 'gemini',
        model: 'gemini-2.5-flash',
        operation_type: 'content_generation',
        tokens_requested: 3000
      }
    ];

    showEstimation(operations);
  };

  const performBlogGeneration = async () => {
    // Actual blog generation logic
    // This will only be called if user confirms in the modal
    console.log('Generating blog...');
  };

  return (
    <>
      <div>
        <input 
          value={keywords} 
          onChange={(e) => setKeywords(e.target.value)}
          placeholder="Enter blog topic..."
        />
        <button onClick={handleGenerateBlog}>
          Generate Blog
        </button>
      </div>

      <CostEstimationModal
        open={isEstimationOpen}
        onClose={closeEstimation}
        onConfirm={performBlogGeneration}
        operations={estimationOperations}
      />
    </>
  );
};
```

### Example: Image Generation

```typescript
const ImageStudio: React.FC = () => {
  const { showEstimation, estimationOperations, isEstimationOpen, closeEstimation } = useCostEstimation();

  const handleGenerateImage = () => {
    const operations: PreflightOperation[] = [
      {
        provider: 'stability',
        operation_type: 'image_generation',
        // tokens_requested not needed for image generation
      }
    ];

    showEstimation(operations);
  };

  return (
    <>
      <button onClick={handleGenerateImage}>
        Generate Image
      </button>

      <CostEstimationModal
        open={isEstimationOpen}
        onClose={closeEstimation}
        onConfirm={() => generateImage()}
        operations={estimationOperations}
      />
    </>
  );
};
```

## Operation Types

Common operation types you can use:

### LLM Operations
- `text_generation` - General LLM text generation
- `research` - Research operations (typically includes search + LLM analysis)
- `outline_generation` - Content outline generation
- `content_generation` - Full content generation
- `seo_analysis` - SEO analysis and optimization
- `content_optimization` - Content refinement and optimization
- `title_generation` - Title/headline generation
- `summary_generation` - Content summarization

### Media Generation Operations
- `image_generation` - Image generation (text-to-image)
- `image_editing` - Image editing operations (inpaint, outpaint, recolor, etc.)
- `image_upscaling` - Image upscaling operations
- `face_swap` - Face swap operations
- `video_generation` - Video generation (text-to-video, image-to-video)
- `video_editing` - Video editing operations
- `audio_generation` - Audio/TTS generation
- `audio_editing` - Audio editing operations

### Search & Research Operations
- `search` - Generic search API operations
- `exa_search` - Exa neural search
- `tavily_search` - Tavily AI search
- `serper_search` - Serper Google search
- `metaphor_search` - Metaphor search
- `firecrawl_extract` - Firecrawl web page extraction

### Specialized Operations
- `character_image_generation` - Character-consistent image generation
- `product_image_generation` - Product-focused image generation
- `avatar_generation` - Avatar/talking head generation
- `scene_generation` - Scene-based video/image generation
- `batch_operation` - Batch processing operations

## Providers

Supported providers:

### LLM Providers
- `gemini` - Google Gemini (default: gemini-2.5-flash)
- `openai` - OpenAI GPT models (default: gpt-4o-mini)
- `anthropic` - Anthropic Claude (default: claude-3.5-sonnet)
- `mistral` - Mistral AI / HuggingFace (default: gpt-oss-120b)

### Search Providers
- `tavily` - Tavily AI Search ($0.001 per search)
- `serper` - Serper Google Search ($0.001 per search)
- `metaphor` - Metaphor Search ($0.003 per search)
- `exa` - Exa Neural Search ($0.005 per search)
- `firecrawl` - Firecrawl Web Extraction ($0.002 per page)

### Media Providers
- `stability` - Stability AI (images: $0.04/image, includes OSS models)
  - OSS Models: `qwen-image` ($0.03), `ideogram-v3-turbo` ($0.05)
- `wavespeed` - WaveSpeed AI (OSS models via Stability provider)
  - Image: `qwen-image`, `ideogram-v3-turbo`
  - Image Edit: `qwen-edit` ($0.02), `flux-kontext-pro` ($0.04)
  - Video: `wan-2.5` ($0.25), `seedance-1.5-pro` ($0.40)
  - Audio: `minimax-speech-02-hd` ($0.05 per 1K chars)
- `video` - Video generation (default: wan-2.5 OSS $0.25)
- `image_edit` - Image editing (default: qwen-edit OSS $0.02)
- `audio` - Audio generation (default: minimax-speech-02-hd OSS)

## Best Practices

1. **Always show estimation before expensive operations** - Operations that cost > $0.01 should show estimation
2. **Group related operations** - If a workflow involves multiple API calls, include all of them in the estimation
3. **Provide accurate token estimates** - More accurate token estimates lead to better cost predictions
4. **Handle errors gracefully** - If estimation fails, allow users to proceed with a warning
5. **Cache estimations** - The API returns a `cached` flag - consider caching for better UX

## Integration Checklist

- [ ] Import `useCostEstimation` hook
- [ ] Import `CostEstimationModal` component
- [ ] Define operations array with `PreflightOperation[]`
- [ ] Call `showEstimation(operations)` before operation
- [ ] Render `CostEstimationModal` with proper props
- [ ] Move actual operation logic to `onConfirm` callback
- [ ] Test with various operation types
- [ ] Handle error states gracefully

## Testing

Test the cost estimation with:

1. **Single operation** - Simple text generation
2. **Multiple operations** - Blog generation workflow
3. **Different providers** - Gemini, OpenAI, etc.
4. **Limit exceeded** - Test when limits are reached
5. **Error handling** - Network errors, API failures

## Notes

- The modal automatically fetches cost estimates when opened
- Users can proceed only if `can_proceed` is `true`
- The modal shows detailed breakdown per operation
- Usage limits are displayed if available
- Actual costs may vary slightly from estimates
