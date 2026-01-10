# Exa Integration Enhancements

**Date**: 2025-01-29  
**Status**: Enhanced based on Exa documentation

---

## Overview

Enhanced ALwrity's Exa integration based on comprehensive Exa documentation to provide better search type selection, improved tooltips, and support for advanced features like Deep search.

---

## Key Enhancements

### 1. Enhanced Search Type Tooltips

Updated tooltips to match Exa's official documentation with accurate latency and use case information:

- **Fast**: <500ms - Speed-critical applications, real-time apps, voice agents
- **Auto (Default)**: ~1000ms - Best of all worlds, intelligently combines methods
- **Deep**: ~5000ms - Comprehensive research, agentic workflows, multi-hop queries
- **Neural**: Variable - Semantic similarity, exploratory searches
- **Keyword**: Fastest - Traditional search, exact keyword matching

### 2. Updated AI Prompt

Enhanced the `unified_research_analyzer.py` prompt to better understand:

- **Latency-quality tradeoffs**: When to use Fast vs Auto vs Deep
- **Search type selection guidelines**: Based on use case (SimpleQA, FRAMES, MultiLoKo, etc.)
- **Deep search requirements**: Context=true required, additionalQueries support
- **Livecrawl options**: When to use fallback vs preferred for freshness

### 3. Added Deep Search Support

- Added 'deep' to search type options
- Updated frontend types to support 'deep'
- Enhanced tooltips to explain Deep search capabilities
- Added guidance on when Deep search is appropriate

### 4. Improved Tooltip Content

All Exa options now have comprehensive tooltips that include:
- Clear descriptions
- When to use
- Latency information (for search types)
- Quality characteristics
- Best practices
- AI recommendations (when available)

---

## Search Type Selection Guidelines

Based on Exa documentation, the AI now understands:

### Fast Search (<500ms)
- **Use for**: SimpleQA-style factual QA, real-time applications, voice agents, autocomplete
- **Characteristics**: Streamlined models, good factual accuracy
- **Best for**: Speed-critical applications

### Auto Search (~1000ms) - Default
- **Use for**: General-purpose research, production workloads, versatile queries
- **Characteristics**: Intelligently combines multiple methods, reranker adapts to query
- **Best for**: Most use cases when unsure which method is best

### Deep Search (~5000ms)
- **Use for**: Agentic workflows (FRAMES, MultiLoKo, BrowseComp), complex research, multi-hop queries
- **Characteristics**: Query expansion, rich contextual summaries, comprehensive coverage
- **Requirements**: context=true for detailed summaries
- **Best for**: When comprehensive coverage > speed

### Neural Search
- **Use for**: Exploratory searches, semantic similarity, finding related concepts
- **Characteristics**: Embeddings-based 'next-link prediction', understands meaning
- **Note**: Also incorporated into Fast and Auto search types

### Keyword Search
- **Use for**: Exact keyword matching, specific terms, brands
- **Characteristics**: Traditional search, fastest, max 10 results
- **Best for**: Precise keyword searches

---

## Backend Changes

### Updated AI Prompt (`unified_research_analyzer.py`)

1. **Enhanced search type descriptions** with latency and use case information
2. **Added Deep search guidelines** including:
   - When to use Deep search
   - Requirements (context=true)
   - Additional queries support
3. **Added livecrawl options** with latency impact information
4. **Improved provider selection logic** based on query characteristics

### Schema Updates

Added support for:
- `type: "deep"` in exa_config
- `additionalQueries: []` for Deep search query variations
- `livecrawl: "fallback|never|preferred|always"` for freshness control

---

## Frontend Changes

### Updated Components

1. **ExaOptions.tsx**:
   - Added 'deep' to search type options
   - Updated tooltip function to show latency and quality info
   - Enhanced tooltip content for all search types

2. **constants.ts**:
   - Updated `exaSearchTypes` to include 'deep'
   - Improved labels with latency information

3. **blogWriterApi.ts**:
   - Updated `exa_search_type` type to include 'deep'

4. **exaTooltips.ts**:
   - Completely revamped search type tooltips with:
     - Accurate latency information
     - Quality characteristics
     - When to use guidance
     - Best practices

---

## User Experience Improvements

1. **Better Education**: Users now understand the latency-quality tradeoffs
2. **Informed Decisions**: Tooltips help users choose the right search type
3. **AI Guidance**: The AI prompt better understands when to use each search type
4. **Comprehensive Coverage**: Support for all Exa search types including Deep

---

## Next Steps (Future Enhancements)

1. **Add UI for additionalQueries**: Allow users to provide query variations for Deep search
2. **Add livecrawl selector**: UI control for livecrawl options
3. **Performance monitoring**: Track actual latency vs expected for each search type
4. **Cost transparency**: Show cost implications of different search types
5. **Auto-optimization**: Suggest search type based on user's latency requirements

---

## References

- [Exa Documentation: How Exa Search Works](https://docs.exa.ai/reference/how-exa-search-works)
- [Exa Documentation: How to Evaluate Exa Search](https://docs.exa.ai/reference/how-to-evaluate-exa-search)
- [Exa API Reference: Search](https://docs.exa.ai/reference/search)

---

**Status**: Enhanced - Better search type selection, improved tooltips, Deep search support
