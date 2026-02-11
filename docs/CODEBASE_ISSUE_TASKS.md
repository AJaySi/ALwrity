# Codebase Issue Triage Tasks

## 1) Typo fix task — rename misspelled documentation section
**Issue found**
- The documentation folder is named `docs/Content Calendar/` (corrected typo), and one file in it is also a likely accidental copy artifact: `calendar_generation_transparency_modal_implementation_plan copy.md`.

**Proposed task**
- ✅ Implemented: renamed the misspelled content calendar docs directory to the corrected spelling.
- ✅ Implemented: removed duplicate `calendar_generation_transparency_modal_implementation_plan copy.md` after confirming identical content.
- Updated any path references in repository docs where needed.

**Acceptance criteria**
- No paths in the repository reference the old misspelled folder name (validated).
- No ` copy.md` planning files remain unless intentionally documented.

---

## 2) Bug fix task — calendar event fetch silently returns empty data
**Issue found**
- `CalendarService.get_calendar_events()` promises optional strategy filtering, but when `strategy_id` is not provided it returns an empty list because the non-filtered branch is left as a TODO.

**Evidence**
- In `backend/api/content_planning/services/calendar_service.py`, the `else` branch under `get_calendar_events` has `# TODO: Implement get_all_calendar_events method` and sets `events = []`.

**Proposed task**
✅ Implemented `ContentPlanningDBService.get_all_calendar_events()`.
✅ Wired `CalendarService.get_calendar_events()` to call it when `strategy_id` is `None`.
Follow-up: add pagination/limits if needed to prevent unbounded queries.

**Acceptance criteria**
- Calling `get_calendar_events()` without `strategy_id` returns persisted events instead of `[]`.
- Existing filtered behavior remains unchanged.

---

## 3) Comment/documentation discrepancy task — align intent vs actual behavior
**Issue found**
- The method docstring says "Get calendar events, optionally filtered by strategy," but current behavior does not actually support the unfiltered path.

**Evidence**
- `backend/api/content_planning/services/calendar_service.py` method docstring describes optional filtering while implementation hardcodes empty results in the unfiltered branch.

**Proposed task**
✅ Completed implementation so the existing docstring now matches behavior.
Added code-level alignment; optional changelog update can follow release process.

**Acceptance criteria**
- No mismatch remains between method docs/comments and runtime behavior.
- Developer-facing docs clearly describe both filtered and unfiltered retrieval.

---

## 4) Test improvement task — strengthen polling integration assertions
**Issue found**
- `frontend/src/components/BlogWriter/__tests__/PollingIntegration.test.tsx` contains weak assertions:
  - It mainly checks that `startResearch` was called, without validating polling cadence, completed-state behavior, or callback payloads.
  - The second test defines `onError` but does not assert error handling effects.

**Proposed task**
✅ Improved polling integration tests with deterministic assertions for:
  - `pollResearchStatus` call count/arguments.
  - `onResearchComplete` invocation with expected final payload.
  - Error path UX behavior (error state/message) and retry/abort behavior where applicable.

**Acceptance criteria**
- Tests fail when polling completion/error handling regresses.
- Assertions cover success path, in-progress path, and error path with concrete expectations.
