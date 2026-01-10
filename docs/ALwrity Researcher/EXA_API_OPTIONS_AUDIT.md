# Exa API Options Audit

**Date**: 2025-01-29  
**Status**: Comparison of Current Implementation vs Exa API Documentation

---

## 📊 Summary

This document compares our current Exa implementation with the official Exa API documentation to identify missing options and configuration gaps.

---

## ✅ Currently Supported Options

### Main Search Parameters
1. ✅ **`type`** - Search type (auto, neural, fast, deep)
   - **Frontend**: `exa_search_type` dropdown
   - **Backend**: `config.exa_search_type` → `type` parameter
   - **Status**: Fully supported

2. ✅ **`category`** - Content category filter
   - **Frontend**: `exa_category` dropdown
   - **Backend**: `config.exa_category` → `category` parameter
   - **Status**: Fully supported

3. ✅ **`numResults`** - Number of results (5-100)
   - **Frontend**: `exa_num_results` input (5-25 limit shown, but API supports up to 100)
   - **Backend**: Uses `config.max_sources` (capped at 25), should use `config.exa_num_results`
   - **Status**: Partially supported (needs to use `exa_num_results` instead of `max_sources`)

4. ✅ **`includeDomains`** - Domain inclusion filter
   - **Frontend**: `exa_include_domains` text input
   - **Backend**: `config.exa_include_domains` → `include_domains` parameter
   - **Status**: Fully supported

5. ✅ **`excludeDomains`** - Domain exclusion filter
   - **Frontend**: `exa_exclude_domains` text input
   - **Backend**: `config.exa_exclude_domains` → `exclude_domains` parameter
   - **Status**: Fully supported

### Contents Parameters (Currently Hardcoded)
6. ⚠️ **`text`** - Full page text retrieval
   - **Current**: Hardcoded to `{'max_characters': 1000}`
   - **Should be**: Configurable via `exa_text_max_characters` and `exa_text_include_html`
   - **Status**: Needs configuration

7. ⚠️ **`highlights`** - Text snippets extraction
   - **Current**: Hardcoded to `{'num_sentences': 2, 'highlights_per_url': 3}`
   - **Should be**: Configurable via `exa_highlights_num_sentences`, `exa_highlights_per_url`, `exa_highlights_query`
   - **Status**: Needs configuration (we have `exa_highlights` boolean but not the detailed config)

8. ⚠️ **`summary`** - Webpage summary
   - **Current**: Hardcoded to `{'query': f"Key insights about {topic}"}`
   - **Should be**: Configurable via `exa_summary_query` and `exa_summary_schema`
   - **Status**: Needs configuration

9. ⚠️ **`context`** - Context string for RAG
   - **Current**: Not used (we have `exa_context` boolean in config but not applied)
   - **Should be**: Configurable via `exa_context` (boolean) or `exa_context_max_characters` (object)
   - **Status**: Partially supported (config exists but not used)

---

## ❌ Missing Options

### Date Filters
10. ❌ **`startPublishedDate`** - Filter by publish date (start)
    - **Frontend**: We have `exa_date_filter` but it's not being used
    - **Backend**: Not passed to Exa API
    - **Status**: Config exists but not implemented

11. ❌ **`endPublishedDate`** - Filter by publish date (end)
    - **Frontend**: Not exposed
    - **Backend**: Not implemented
    - **Status**: Missing

12. ❌ **`startCrawlDate`** - Filter by crawl date (start)
    - **Frontend**: Not exposed
    - **Backend**: Not implemented
    - **Status**: Missing

13. ❌ **`endCrawlDate`** - Filter by crawl date (end)
    - **Frontend**: Not exposed
    - **Backend**: Not implemented
    - **Status**: Missing

### Text Filters
14. ❌ **`includeText`** - Text that must be present in results
    - **Frontend**: Not exposed
    - **Backend**: Not implemented
    - **Status**: Missing

15. ❌ **`excludeText`** - Text that must not be present in results
    - **Frontend**: Not exposed
    - **Backend**: Not implemented
    - **Status**: Missing

### Advanced Options
16. ❌ **`userLocation`** - Two-letter ISO country code
    - **Frontend**: Not exposed
    - **Backend**: Not implemented
    - **Status**: Missing

17. ❌ **`moderation`** - Content moderation filter
    - **Frontend**: Not exposed
    - **Backend**: Not implemented
    - **Status**: Missing

18. ❌ **`additionalQueries`** - Additional queries for deep search
    - **Frontend**: Not exposed
    - **Backend**: Not implemented
    - **Status**: Missing (only works with `type="deep"`)

### Contents Advanced Options
19. ❌ **`livecrawl`** - Live crawling options (never, fallback, preferred, always)
    - **Frontend**: Not exposed
    - **Backend**: Not implemented
    - **Status**: Missing

20. ❌ **`livecrawlTimeout`** - Timeout for live crawling (ms)
    - **Frontend**: Not exposed
    - **Backend**: Not implemented
    - **Status**: Missing

21. ❌ **`subpages`** - Number of subpages to crawl
    - **Frontend**: Not exposed
    - **Backend**: Not implemented
    - **Status**: Missing

22. ❌ **`subpageTarget`** - Term to find specific subpages
    - **Frontend**: Not exposed
    - **Backend**: Not implemented
    - **Status**: Missing

23. ❌ **`extras`** - Extra parameters (links, imageLinks)
    - **Frontend**: Not exposed
    - **Backend**: Not implemented
    - **Status**: Missing

---

## 🔧 Implementation Gaps

### 1. Date Filter Not Applied
- **Issue**: `exa_date_filter` exists in config but is not passed to Exa API
- **Fix**: Map `exa_date_filter` → `startPublishedDate` in `exa_provider.py`

### 2. Context Not Applied
- **Issue**: `exa_context` boolean exists but is not used
- **Fix**: Apply `context` parameter based on `exa_context` value

### 3. Num Results Uses Wrong Field
- **Issue**: Uses `config.max_sources` instead of `config.exa_num_results`
- **Fix**: Use `config.exa_num_results` if available, fallback to `max_sources`

### 4. Contents Parameters Hardcoded
- **Issue**: `text`, `highlights`, `summary` are hardcoded
- **Fix**: Make them configurable via ResearchConfig

---

## 📋 Recommended Priority

### Priority 1: Fix Existing Config Not Applied
1. ✅ Apply `exa_date_filter` → `startPublishedDate`
2. ✅ Apply `exa_context` → `context`
3. ✅ Use `exa_num_results` instead of `max_sources`

### Priority 2: Make Contents Configurable
4. ✅ Make `text.max_characters` configurable
5. ✅ Make `highlights` configurable (num_sentences, highlights_per_url, query)
6. ✅ Make `summary.query` configurable

### Priority 3: Add Common Date Filters
7. ✅ Add `endPublishedDate` support
8. ✅ Add `startCrawlDate` / `endCrawlDate` support (if needed)

### Priority 4: Add Text Filters (If Needed)
9. ✅ Add `includeText` / `excludeText` support (if needed)

### Priority 5: Advanced Options (Low Priority)
10. ✅ Add `userLocation`, `moderation`, `livecrawl`, `subpages`, `extras` (if needed)

---

## 🎯 Current Status

**Total Exa API Options**: ~23 options  
**Currently Supported**: 5 fully, 4 partially  
**Missing**: 14 options  
**Hardcoded**: 3 options (text, highlights, summary)

**Recommendation**: Focus on Priority 1 and 2 to make existing config work and make contents configurable.

---

## ✅ Recent Fixes (2025-01-29)

### Fixed Critical Issues
1. ✅ **Updated `type` enum**: Removed `deep`, added `keyword` and `fast` to match latest API
2. ✅ **Updated `category` enum**: Removed `movie` and `song`, kept `linkedin profile` 
3. ✅ **Applied `exa_date_filter`**: Now maps to `start_published_date` parameter
4. ✅ **Applied `exa_context`**: Now properly passed to Exa API when enabled
5. ✅ **Fixed `exa_num_results`**: Now uses `exa_num_results` instead of `max_sources`, supports up to 100 results
6. ✅ **Updated frontend**: Added `fast` option, updated category list, increased num_results limit to 100

### Updated Files
- `backend/services/research/intent/unified_research_analyzer.py` - Updated AI prompt enum values
- `backend/services/blog_writer/research/exa_provider.py` - Applied date filter, context, and num_results
- `frontend/src/components/Research/steps/utils/constants.ts` - Updated search types and categories
- `frontend/src/components/Research/steps/components/ExaOptions.tsx` - Updated num_results limit and type handling
