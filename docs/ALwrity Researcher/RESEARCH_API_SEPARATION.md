# Research API Separation of Concerns

**Date**: 2025-01-29  
**Status**: Completed

---

## Overview

Properly separated Research API types from Blog Writer API to ensure clean separation of concerns. Research components now use dedicated `researchApi.ts` instead of `blogWriterApi.ts`.

---

## Problem

Research components were importing types from `blogWriterApi.ts`, which violated separation of concerns:
- Research is a standalone engine used by multiple tools (Blog Writer, Podcast Maker, YouTube Creator, etc.)
- Mixing research types with blog writer types created confusion and tight coupling
- Made it difficult to maintain and extend research functionality independently

---

## Solution

### Created Dedicated Research API File

**`frontend/src/services/researchApi.ts`** - New dedicated file containing:
- `ResearchMode` - Research depth levels
- `ResearchProvider` - Provider types (google, exa, tavily)
- `SourceType` - Source categories
- `DateRange` - Date filter options
- `ResearchSource` - Source data structure
- `ResearchConfig` - Complete research configuration (Exa, Tavily options)
- `ResearchResponse` - Generic research response interface
- `ResearchRequest` - Research request interface

### Updated All Research Components

All Research components now import from `researchApi.ts`:

**Updated Files:**
1. `ExaOptions.tsx` - Uses `ResearchConfig` from `researchApi.ts`
2. `TavilyOptions.tsx` - Uses `ResearchConfig` from `researchApi.ts`
3. `ResearchInput.tsx` - Uses `ResearchProvider`, `ResearchMode` from `researchApi.ts`
4. `AdvancedProviderOptionsSection.tsx` - Uses `ResearchProvider` from `researchApi.ts`
5. `useResearchWizard.ts` - Uses `ResearchMode`, `ResearchConfig`, `ResearchResponse` from `researchApi.ts`
6. `research.types.ts` - Uses `ResearchResponse`, `ResearchMode`, `ResearchConfig` from `researchApi.ts`
7. `StepResults.tsx` - Uses `ResearchResponse` from `researchApi.ts` (casts to `BlogResearchResponse` when needed)
8. `AdvancedOptionsSection.tsx` - Uses `ResearchConfig` from `researchApi.ts`
9. `useResearchConfig.ts` - Uses `ResearchProvider` from `researchApi.ts`
10. `StepOptions.tsx` - Uses `ResearchProvider` from `researchApi.ts`
11. `researchModeSuggester.ts` - Uses `ResearchMode` from `researchApi.ts`

### Backward Compatibility

**`frontend/src/services/blogWriterApi.ts`** - Maintains backward compatibility:
- Re-exports research types from `researchApi.ts` for existing blog writer code
- `BlogResearchResponse` extends `ResearchResponse` (adds blog-specific fields like `search_widget`, `grounding_metadata`)
- Blog Writer components continue to work without changes

### Adapter Pattern

**`BlogWriterAdapter.tsx`** - Uses `BlogResearchResponse`:
- This is correct - it's an adapter that bridges Research and Blog Writer
- Adapters are allowed to use both APIs as they translate between domains

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Research Engine                       │
│  (Standalone, used by multiple tools)                    │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  researchApi.ts                                  │  │
│  │  - ResearchConfig                                │  │
│  │  - ResearchResponse                              │  │
│  │  - ResearchMode, ResearchProvider                │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                          │
                          │ extends
                          ▼
┌─────────────────────────────────────────────────────────┐
│                    Blog Writer                           │
│  (Uses Research Engine)                                  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  blogWriterApi.ts                                │  │
│  │  - BlogResearchResponse extends ResearchResponse │  │
│  │  - Blog-specific fields (search_widget, etc.)    │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## Benefits

1. **Clear Separation**: Research types are separate from Blog Writer types
2. **Reusability**: Research API can be used by Podcast Maker, YouTube Creator, etc.
3. **Maintainability**: Changes to research don't affect blog writer and vice versa
4. **Type Safety**: Proper TypeScript types ensure compile-time safety
5. **Backward Compatibility**: Existing blog writer code continues to work

---

## Migration Status

✅ **Completed:**
- Created `researchApi.ts` with all research types
- Updated all Research components to use `researchApi.ts`
- Updated `researchEngineApi.ts` to use `ResearchResponse`
- Maintained backward compatibility in `blogWriterApi.ts`
- `BlogResearchResponse` properly extends `ResearchResponse`

⚠️ **Future Work:**
- Update blog writer components to import from `researchApi.ts` directly (currently using re-exports)
- Consider creating adapter components for other tools (Podcast Maker, YouTube Creator)

---

## File Structure

```
frontend/src/services/
├── researchApi.ts          ← NEW: Dedicated research types
├── researchEngineApi.ts     ← Updated: Uses researchApi.ts
└── blogWriterApi.ts        ← Updated: Re-exports + BlogResearchResponse extends ResearchResponse

frontend/src/components/Research/
├── steps/
│   ├── components/
│   │   ├── ExaOptions.tsx           ← Uses researchApi.ts
│   │   ├── TavilyOptions.tsx        ← Uses researchApi.ts
│   │   └── AdvancedOptionsSection.tsx ← Uses researchApi.ts
│   ├── hooks/
│   │   └── useResearchConfig.ts     ← Uses researchApi.ts
│   └── utils/
│       └── researchModeSuggester.ts ← Uses researchApi.ts
├── types/
│   └── research.types.ts            ← Uses researchApi.ts
└── integrations/
    └── BlogWriterAdapter.tsx        ← Uses blogWriterApi.ts (adapter, correct)
```

---

**Status**: ✅ Separation of concerns achieved - Research API is now independent from Blog Writer API
