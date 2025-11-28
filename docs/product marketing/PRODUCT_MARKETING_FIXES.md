# Product Marketing Suite - Critical Fixes

## Issues Identified

1. **Campaigns lost on refresh** - Campaigns stored only in component state
2. **User journey paths not clear** - No visible guided flows
3. **APIs not properly mapped to UI** - Missing proposal review and asset generation flows

## Fixes Implemented

### 1. Campaign Persistence (Backend)

#### Database Models Created
- `Campaign` - Stores campaign blueprints
- `CampaignProposal` - Stores AI-generated proposals
- `CampaignAsset` - Links generated assets to campaigns

#### New API Endpoints
- `GET /api/product-marketing/campaigns` - List all campaigns
- `GET /api/product-marketing/campaigns/{id}` - Get specific campaign
- `GET /api/product-marketing/campaigns/{id}/proposals` - Get proposals for campaign

#### Campaign Storage Service
- `CampaignStorageService` - Handles all database operations
- Auto-saves campaigns when created
- Auto-saves proposals when generated

### 2. User Journey Flows (Frontend - TODO)

Need to create:
- **Journey A**: "Launch Net-New Campaign" - Multi-step wizard with clear progress
- **Journey B**: "Enhance & Reuse Existing Assets" - Asset audit → enhancement flow
- **Journey C**: "Always-On Optimization" - Dashboard insights and suggestions

### 3. API-UI Mapping (Frontend - TODO)

Need to implement:
- Proposal review screen after blueprint creation
- Asset generation queue
- Campaign detail view with progress tracking
- Proposal approval/rejection workflow

## Next Steps

1. Update frontend to load campaigns from API
2. Create user journey selection screen
3. Implement proposal review component
4. Connect asset generation flow
5. Add campaign detail view

