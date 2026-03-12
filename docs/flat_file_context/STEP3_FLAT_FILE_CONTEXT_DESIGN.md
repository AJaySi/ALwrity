# Step 3 Flat File Context Design (Research Preferences + Competitors)

## Intent
Provide agent-ready Step 3 context with compact summaries for routing plus full payload for deep analysis.

## Storage location
- `workspace/workspace_<safe_user_id>/agent_context/step3_research_preferences.json`

## Why this matters for agents
Step 3 is the bridge from website understanding (Step 2) to competitive strategy and research execution. Agents need this file to understand:
- depth and quality preference constraints,
- factuality constraints,
- content-type priorities,
- competitor landscape and industry context.

## Document-context block
Every context file should include machine-readable document metadata to orient agents quickly:
- audience (`ai_agents`)
- purpose (`fast_context_retrieval`)
- journey stage (`onboarding_step_3`)
- retrieval contract and fallback order
- context-window guidance (size budget + summary-first policy)

## Minimal Step 3 data groups
- research config: depth/content types/auto/factual
- inherited style profile (if present): writing style, target audience, recommended settings
- competitors: domain/url/title/relevance highlights
- industry context: compact market framing text
- traceability: source payload and timestamps

## Agent usage policy
1. Start with `agent_summary.quick_facts` and `retrieval_hints`.
2. Use competitor summary before opening full competitor objects.
3. Read full `data` only for tasks requiring strict evidence/fields.
4. Fall back to DB, then SIF semantic if missing or stale.


## Related-document navigation
Agents can consult `context_manifest.json` to discover linked context files and traverse only the required documents for the task.
