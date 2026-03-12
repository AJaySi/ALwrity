# Step 4 Flat File Context Design (Persona Data)

## Intent
Capture onboarding Step 4 persona outputs in an agent-first flat file so agents can quickly personalize strategy, content, and platform execution.

## Storage location
- `workspace/workspace_<safe_user_id>/agent_context/step4_persona_data.json`

## Required Step 4 coverage
- core persona profile (`core_persona`)
- platform personas (`platform_personas`)
- quality metrics (`quality_metrics`)
- selected platforms (`selected_platforms`)
- research persona/notes when available
- source payload + timestamps for traceability

## Agent summary expectations
- quick facts: selected platform count, persona availability flags
- retrieval hints: persona/profile adaptation queries
- persona focus: compact actionable slice of core persona + quality constraints

## Usage policy
1. Start with `agent_summary`.
2. Expand into `data` only when a task needs full fidelity.
3. Use `document_context.related_documents` to fetch upstream Step 2/Step 3 context as needed.
