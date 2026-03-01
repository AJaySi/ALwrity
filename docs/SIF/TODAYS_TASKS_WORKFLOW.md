# Multi-Agent Today's Tasks System - Implementation Plan

**Date**: 2025-03-01
**Status**: Architecture Plan
**Target System**: Today's Tasks Workflow (Multi-Agent Committee)

---

## 📋 Executive Summary

This document outlines the implementation plan for transforming the "Today's Tasks" system from a single-prompt generator into a **Multi-Agent "Committee" Architecture**. 

Instead of a generic LLM generating tasks, we will leverage our existing specialized agents (`StrategyArchitect`, `ContentStrategist`, `SEOOptimization`, etc.) to **propose high-value, context-aware tasks** based on their specific domain knowledge. A central "Manager" (Orchestrator) will then consolidate, prioritize, and deduplicate these proposals into a cohesive daily plan.

We will also introduce a **Self-Learning Task Memory** using `txtai` to ensure the system learns from user behavior (acceptances/rejections) and avoids redundant suggestions.

---

## 🏗️ Architecture: The "Committee" Model

### 1. Agent Roles & Responsibilities

Each agent will act as a "Department Head," submitting daily proposals for their specific pillar.

| Workflow Pillar | Owner Agent | Data Sources | Proposal Type Example |
| :--- | :--- | :--- | :--- |
| **PLAN** | `StrategyArchitectAgent` | Content Pillars, Strategy Doc | "Review 'AI Trends' pillar strategy - engagement dropped 10%." |
| **GENERATE** | `ContentStrategyAgent` | Content Gaps, Trends | "Draft a blog post on 'Vector Search' (High Opportunity Gap)." |
| **PUBLISH** | `SocialAmplificationAgent` | Audience Activity, Calendar | "Schedule your 'Weekly Recap' thread for 10 AM (Peak Audience)." |
| **ANALYZE** | `SEOOptimizationAgent` | GSC, Site Health, Rankings | "Fix 3 broken links on your pricing page to recover link equity." |
| **ENGAGE** | `SocialAmplificationAgent` | Social Mentions, Comments | "Reply to 3 unanswered comments on your latest LinkedIn post." |
| **REMARKET** | `CompetitorResponseAgent` | Competitor Activity | "Competitor X posted about [Topic]. Create a counter-narrative Reel." |

### 2. The Workflow (Daily Cycle)

1.  **Morning Briefing (Parallel)**: `TodayWorkflowManager` polls all agents via `propose_daily_tasks(context)`.
2.  **Aggregation**: Manager collects raw proposals (~10-15 tasks).
3.  **Intelligence Filter (Self-Learning)**: 
    *   Check `TaskMemoryIndex` (txtai).
    *   Filter out tasks similar to previously **Rejected** tasks.
    *   Deprioritize tasks similar to recently **Completed** tasks.
4.  **Consolidation**: Deduplicate overlapping ideas (e.g., SEO & Content agents both suggesting the same topic).
5.  **Final Selection**: Select top 1-3 tasks per pillar based on user goals (e.g., "Growth" mode = more Publish/Remarket tasks).

---

## 🚀 Implementation Phases

### Phase 1: Agent Interface Standardization (The "Voice")
**Objective**: Give every agent the ability to speak the "Task Proposal" language.
**Status**: ✅ Completed

*   **Task 1.1**: Define `TaskProposal` schema (Pydantic model). ✅
    *   Fields: `title`, `description`, `pillar`, `priority`, `reasoning`, `estimated_time`, `action_type`.
*   **Task 1.2**: Update `BaseALwrityAgent` with abstract `propose_daily_tasks(context: Dict) -> List[TaskProposal]`. ✅
*   **Task 1.3**: Implement `propose_daily_tasks` in all specialized agents. ✅
    *   *StrategyArchitect*: Logic to check pillar health.
    *   *ContentStrategist*: Logic to check content gaps.
    *   *SEOAgent*: Logic to check GSC alerts/errors.
    *   *SocialAmplification*: Logic for publish/engage.
    *   *CompetitorResponse*: Logic for monitoring.

### Phase 2: The Manager (The "Orchestrator")
**Objective**: Build the backend service that coordinates the committee.
**Status**: ✅ Completed

*   **Task 2.1**: Refactor `TodayWorkflowGenerator` in `today_workflow_service.py`. ✅
    *   Replace single-prompt generation with `gather_agent_proposals()`.
    *   Implement `asyncio.gather` for parallel agent execution (performance critical).
*   **Task 2.2**: Implement `consolidate_proposals()` logic. ✅
    *   Use a lightweight LLM call to merge/rank the raw list if needed, or deterministic logic for speed.
*   **Task 2.3**: Connect to Frontend. ✅
    *   Ensure the API response matches the existing `TodayTask` frontend interface.

### Phase 3: Self-Learning Memory (The "Brain")
**Objective**: Stop the system from nagging users about things they hate or just did.
**Status**: ✅ Completed

*   **Task 3.1**: Create `TaskHistory` model in DB. ✅
    *   Store: `task_vector_id`, `original_text`, `status` (completed/rejected/skipped), `user_feedback`.
*   **Task 3.2**: Implement `TaskMemoryService` using `txtai`. ✅
    *   Index tasks with metadata.
    *   Implement `is_redundant_or_rejected(proposal_text)` check.
*   **Task 3.3**: Wire feedback loop. ✅
    *   When user clicks "Dismiss" or "Complete" in frontend, update the `txtai` index.

### Phase 4: UI Feedback & Transparency
**Objective**: Show the user *why* a task was suggested.

*   **Task 4.1**: Update Frontend `TodayTask` card.
    *   Add "Suggested by [Agent Name]" badge.
    *   Add "Why?" tooltip (e.g., "Because Competitor X did Y").
*   **Task 4.2**: Add "Train my Agents" feedback.
    *   "Don't show this again" vs "Not today".

---

## 📊 Data Models

### 1. TaskProposal (Backend)
```python
class TaskProposal(BaseModel):
    title: str
    description: str
    pillar_id: str  # plan, generate, publish, analyze, engage, remarket
    priority: str   # high, medium, low
    estimated_time: int # minutes
    source_agent: str # e.g., "SEOOptimizationAgent"
    reasoning: str # "Detected 404 error spike"
    context_data: Optional[Dict] # e.g., {"url": "..."}
```

### 2. TaskMemoryDocument (txtai)
```json
{
  "id": "uuid",
  "text": "Write a blog post about AI Trends",
  "embedding": [vector],
  "tags": ["generate", "content_strategy"],
  "user_id": "123",
  "status": "rejected",
  "last_updated": "2024-03-01T10:00:00Z"
}
```

---

## 🛠️ Technical Considerations

*   **Performance**: Calling 6 agents + LLMs in parallel can be slow.
    *   *Mitigation*: Set strict timeouts (e.g., 5s) per agent. Use "Lite" logic for proposals (e.g., check DB/Cache instead of live crawling) where possible.
*   **Fallback**: If agents time out or fail, fall back to the `_fallback_tasks` template currently in place.
*   **Token Usage**: Summarize context before sending to agents to minimize input tokens.

---

## 📅 Execution Timeline

1.  **Day 1**: Phase 1 (Interfaces & 2 core agents).
2.  **Day 2**: Phase 2 (Orchestrator wiring).
3.  **Day 3**: Phase 3 (txtai Memory integration).
4.  **Day 4**: Phase 1 completion (remaining agents) & Phase 4 (UI polish).
