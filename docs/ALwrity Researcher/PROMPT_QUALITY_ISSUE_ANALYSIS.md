# Prompt Quality Issue Analysis

**Date**: 2025-01-29  
**Issue**: Quality degradation after prompt builder changes  
**Status**: Investigating

---

## 🔍 Problem Statement

User reports that after changes to `unified_prompt_builder.py`, the quality of AI-generated research intent and Exa/Tavily options has significantly degraded. Previously getting great results, now getting poor quality.

---

## 📊 Current Prompt Analysis

### Prompt Length & Complexity

**Current Unified Prompt**: ~500 lines
- Very detailed instructions
- Multiple "CRITICAL" sections
- Extensive provider options documentation
- Complex query linking rules
- Detailed optimization rules

**Potential Issues**:
1. **Prompt Too Long**: ~500 lines may be overwhelming the LLM
2. **Too Many Constraints**: Multiple "CRITICAL" sections may conflict
3. **Over-Prescriptive**: Too many rules may confuse rather than guide
4. **Information Overload**: Provider options table is very detailed

---

## 🔄 What Changed Recently

Based on conversation history, recent changes include:

1. **Added keyword emphasis** - "MUST include user's actual keywords"
2. **Removed confidence optimization** - Reverted confidence instructions
3. **Added query linking rules** - Explicit linking to intent fields
4. **Enhanced provider optimization** - More detailed rules

---

## 🎯 Key Differences: Original vs Current

### Original Intent Prompt (Simple, Working)
- ~200 lines
- Clear, focused instructions
- Simple confidence scoring
- Straightforward query generation
- Basic provider selection

### Current Unified Prompt (Complex, Degraded)
- ~500 lines
- Multiple "CRITICAL" sections
- Complex query linking
- Extensive provider documentation
- Detailed optimization rules

---

## 💡 Hypothesis

**The prompt may be too complex**, causing the LLM to:
1. Get confused by conflicting instructions
2. Focus on wrong aspects (too many rules)
3. Produce lower quality due to information overload
4. Miss the core task (intent inference) due to complexity

---

## 🔧 Recommended Fixes

### Option 1: Simplify the Prompt (Recommended)
- Reduce prompt length by 50%
- Remove redundant instructions
- Simplify provider documentation
- Focus on core task: intent inference + query generation

### Option 2: Split Back to Separate Calls
- Use original `intent_prompt_builder.py` for intent
- Use separate query generation
- Use separate parameter optimization
- Trade-off: More LLM calls but better quality

### Option 3: Hybrid Approach
- Keep unified call but simplify prompt
- Remove detailed provider documentation (reference only)
- Focus on clear, concise instructions
- Let LLM infer more, prescribe less

---

## 📝 Next Steps

1. Review original working prompt structure
2. Identify what made it work well
3. Simplify current prompt while keeping essential features
4. Test with same inputs that previously worked
5. Compare quality before/after

---

**Status**: Ready for prompt simplification
