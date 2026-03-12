# Step 2 Flat File Context Design (Website Analysis)

## Intent
Step 2 context must be optimized for **AI-agent retrieval speed and token efficiency**, not human readability.

## Current storage location
- `workspace/workspace_<safe_user_id>/agent_context/step2_website_analysis.json`

## Current retrieval chain
1. Flat file (fastest)
2. DB (`website_analyses`)
3. SIF semantic fallback

## Compactness strategy
For implementation, keep two logical layers:
- **`d` equivalent (full canonical data)** for deep reasoning.
- **`s` equivalent (high-signal summary)** for fast agent prompts and most decisions.
- **`document_context`** for machine-readable orientation (purpose, journey stage, fallback contract, context-window guidance).

Agents should default to summary-first reads and only open full data when needed.

## Step 2 coverage requirements
The Step 2 context should preserve these semantic groups:
- identity/state: website url, timestamps, status/error/warning
- brand/style: writing style, style patterns/guidelines, brand analysis
- audience/content: target audience, content type, recommended settings, characteristics
- strategy/seo: strategy insights, SEO audit, strategic history
- crawl/discovery: crawl output, meta info, sitemap analysis
- traceability: raw inbound payload snapshots

## Agent-readability best practices
- Keep keys stable and deterministic.
- Prefer arrays/enums over long free text.
- Keep summary fields flattened and high signal.
- Avoid duplicate verbose nested structures unless required for correctness.
- Include retrieval hints for consistent downstream querying.

## Practical guidance for consumers
- Use summary/high-signal fields first for routing and lightweight reasoning.
- Pull deep fields only for specialist tasks (SEO, persona fidelity, editorial style checks).
- If flat-file missing/stale: auto-fallback to DB then SIF.

## Note
A generalized compact framework is documented in:
- `docs/flat_file_context/FLAT_FILE_CONTEXT_FRAMEWORK_DESIGN.md`

Future enhancements are tracked in:
- `docs/flat_file_context/FLAT_FILE_CONTEXT_ENHANCEMENTS_BACKLOG.md`


## Context window guidance
- Keep summary compact and deterministic.
- Add byte-size metadata to help agents decide whether to expand into full data.
- Prefer short keys and avoid verbose natural language in machine envelopes.
