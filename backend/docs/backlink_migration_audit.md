# Backlink Migration Audit (Legacy vs Current)

Legacy prototype reference:
- `ToBeMigrated/ai_marketing_tools/ai_backlinker/ai_backlinking.py`
- `ToBeMigrated/ai_marketing_tools/ai_backlinker/backlinking_ui_streamlit.py`

## Implemented in current branch

- Canonical backend entrypoint with backlink-specific naming:
  - `backend/routers/backlink_outreach.py`
  - `backend/services/backlink_outreach_service.py`
- Legacy-style guest-post query template generation exposed over API:
  - `GET /api/backlink-outreach/query-templates?keyword=<keyword>`
- Migration traceability metadata endpoints:
  - `GET /api/backlink-outreach/modules`
  - `GET /api/backlink-outreach/migration-coverage`
- Frontend integration points with backlink-specific naming:
  - `frontend/src/api/backlinkOutreachApi.ts`
  - `frontend/src/stores/backlinkOutreachStore.ts`
  - `frontend/src/components/SEODashboard/BacklinkOutreachModuleList.tsx`

## Not yet migrated (planned)

- Live web prospect discovery / scraping execution loop (`find_backlink_opportunities`).
- Outreach email sending + reply monitoring loop (`send_email`, IMAP checks).
- End-to-end campaign orchestration from keyword batch -> outreach -> follow-up.

## Notes

This branch intentionally provides a clean migration seam and auditable entrypoints first.
Feature-complete parity can now be implemented incrementally behind these stable backend and frontend contracts.
