# Step 5 Flat File Context Design (Integrations)

## Intent
Capture onboarding Step 5 integration configuration in a compact agent-readable context so agents can reason about connected services and execution constraints.

## Storage location
- `workspace/workspace_<safe_user_id>/agent_context/step5_integrations.json`

## Required Step 5 coverage
- integration map (`integrations`)
- provider list (`providers`)
- connected account references (`connected_accounts`)
- integration status and notes
- source payload and timestamps

## Agent summary expectations
- connected integration count/list
- provider count
- retrieval hints for integration readiness checks

## Linked traversal
Use `document_context.related_documents` and `context_manifest.json` to navigate Step 2/3/4 upstream dependencies when deciding tool execution paths.
