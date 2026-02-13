# GSC Step-5 + SEO Dashboard Task Reporting: Design Review (Issues 1–4)

## Scope
This document summarizes final design considerations, issues solved, and exact code changes for the GSC task-reporting implementation used by:
- Onboarding Step 5 (optional “run once” testing UX)
- SEO Dashboard (continuous monitoring visibility)

## Issues Addressed
1. **Issue 1 – Task bootstrapping after onboarding**
   - Ensured onboarding completion creates/verifies platform-insights tasks for connected `gsc`/`bing`.

2. **Issue 2 – GSC query request correctness & scale**
   - Standardized Search Analytics request bodies with documented fields (`type`, `rowLimit` cap, `startRow`) and removed ambiguous aggregate request shape (`dimensions: []`).

3. **Issue 3 – Opportunity/decay reliability**
   - Fixed decay comparison to use equivalent windows (current 30d vs previous 30d), not a sliced 60d dataset.

4. **Issue 4 – Shared reporting contract + exact query templates**
   - Preserved a single backend contract for task sections and exact Google query templates reused in onboarding/dashboard UI.

## Design Considerations
- **Single source of truth**: `GSCTaskReportService` remains the only section-construction service consumed by both UI surfaces.
- **Docs-aligned GSC requests**: request builder enforces valid defaults and bounded limits for stable behavior.
- **Non-blocking onboarding**: task creation is best-effort and logged; onboarding completion is not failed by monitoring setup issues.
- **Composable UI**: `GSCTaskReportsPanel` is shared to avoid duplicated behavior and drift.

## Specific Code Edits
- **GSC request builder + docs-aligned usage**
  - `backend/services/gsc_service.py`
  - Added `_build_search_analytics_request(...)` and switched verification/aggregate/query requests to use it.
  - Added constants: `DEFAULT_SEARCH_TYPE='web'`, `MAX_ROW_LIMIT=25000`.

- **Correct period-over-period decay logic**
  - `backend/services/gsc_task_report_service.py`
  - Added `_fetch_query_rows_range(...)`.
  - Updated comparison windows to current 30d vs previous 30d.

- **Task report API contract (already in previous commit; retained)**
  - `backend/routers/gsc_auth.py`
  - `GET /gsc/task-reports`, `POST /gsc/task-reports/run`.

- **Onboarding task bootstrap (already in previous commit; retained)**
  - `backend/api/onboarding_utils/onboarding_completion_service.py`

- **Validation tests added**
  - `backend/services/gsc_query_request_shapes_tests.py`
  - Verifies request shape constraints and aggregate request behavior.

## Validation Performed
- Unit tests for GSC query request shapes and constraints.
- Python compilation checks for modified backend modules.

