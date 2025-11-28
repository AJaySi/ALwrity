# Product Marketing Suite - Action Plan & Next Steps

**Created**: December 2024  
**Status**: Ready for Implementation  
**Timeline**: 1-2 weeks to MVP

---

## 🎯 Immediate Action Items (Do First)

### ✅ Priority 1: Fix Proposal Persistence (30 minutes) 🔴

**Issue**: Proposals generated but not saved to database - line 195-202 in `backend/routers/product_marketing.py`

**Fix Required**:
```python
# backend/routers/product_marketing.py
# After line 199, before line 201:

proposals = orchestrator.generate_asset_proposals(
    user_id=user_id,
    blueprint=blueprint,
    product_context=request.product_context,
)

# ADD THIS (save proposals to database):
campaign_storage.save_proposals(user_id, campaign_id, proposals)

logger.info(f"[Product Marketing] ✅ Generated {proposals['total_assets']} proposals")
return proposals
```

**Impact**: Critical - Without this, proposals are lost between sessions

---

### ✅ Priority 2: Create Database Migration (1 hour) 🔴

**Issue**: Database tables don't exist - models exist but migration not created

**Steps**:
```bash
cd backend
alembic revision --autogenerate -m "Add product marketing tables"
# Review the generated migration file
alembic upgrade head
```

**Verify Tables Created**:
- `product_marketing_campaigns`
- `product_marketing_proposals`  
- `product_marketing_assets`

**Impact**: Critical - No data persistence without tables

---

### ✅ Priority 3: Test End-to-End Flow (30 minutes) 🟡

**Manual Testing Checklist**:

1. **Campaign Creation**
   - [ ] Navigate to `/product-marketing`
   - [ ] Click "Create Campaign"
   - [ ] Complete wizard (name, goal, channels, product info)
   - [ ] Verify campaign appears in dashboard

2. **Proposal Generation**
   - [ ] After wizard, verify proposals are generated
   - [ ] Check database: `SELECT * FROM product_marketing_proposals WHERE campaign_id = '...'`
   - [ ] Verify proposals appear in ProposalReview component

3. **Asset Generation**
   - [ ] Select proposals to generate
   - [ ] Click "Generate Selected Assets"
   - [ ] Verify assets appear in Asset Library
   - [ ] Check database: `SELECT * FROM content_assets WHERE source_module = 'product_marketing'`

4. **Campaign Status**
   - [ ] Verify campaign status updates to "ready" after asset generation
   - [ ] Check asset node statuses update correctly

**Impact**: High - Validates entire workflow works

---

## 📋 Week 1: Core Workflow Completion

### Day 1-2: Database & Persistence ✅

**Tasks**:
- [x] Fix proposal persistence (30 min)
- [x] Create database migration (1 hour)
- [x] Test end-to-end flow (30 min)
- [ ] **Add error handling** for database operations (1 hour)
- [ ] **Add logging** for proposal generation lifecycle (30 min)

**Deliverable**: All data persists correctly through workflow

---

### Day 3-4: Asset Generation Integration 🟡

**Current State**: 
- `ProposalReview.tsx` calls `generateAsset()` hook ✅
- Backend endpoint exists ✅
- **Issue**: Need to verify Image Studio integration works

**Tasks**:
- [ ] **Test image generation** from proposal review
- [ ] **Verify asset tracking** - assets appear in Asset Library with correct metadata
- [ ] **Update campaign status** after asset generation completes
- [ ] **Handle errors gracefully** - show user-friendly messages
- [ ] **Add loading states** - show progress for each asset being generated

**Code Locations to Verify**:
- `frontend/src/components/ProductMarketing/ProposalReview.tsx` (lines 110-158)
- `backend/routers/product_marketing.py` (lines 209-240)
- `backend/services/product_marketing/orchestrator.py` (lines 199-259)

**Deliverable**: Users can generate images from proposals successfully

---

### Day 5-6: Text Generation Integration 🟡

**Current State**: 
- Text generation in orchestrator returns placeholder (line 245-252 in `orchestrator.py`)
- Need to integrate `llm_text_gen` service

**Implementation Required**:

```python
# backend/services/product_marketing/orchestrator.py
# Replace lines 245-252:

elif asset_type == "text":
    # Import text generation service
    from services.llm_providers.main_text_generation import llm_text_gen
    from utils.text_asset_tracker import save_and_track_text_content
    from services.database import SessionLocal
    
    # Get enhanced prompt from proposal
    text_prompt = asset_proposal.get('proposed_prompt')
    
    # Generate text using LLM
    db = SessionLocal()
    try:
        text_result = await llm_text_gen(
            prompt=text_prompt,
            user_id=user_id,
            # Add persona/context if available
        )
        
        # Save to Asset Library
        save_and_track_text_content(
            db=db,
            user_id=user_id,
            content=text_result.get('content', ''),
            title=f"{asset_proposal.get('channel', '')} {asset_proposal.get('asset_type', 'copy')}",
            description=f"Marketing copy for {asset_proposal.get('channel')}",
            source_module="product_marketing",
            tags=["product_marketing", asset_proposal.get('channel', ''), "text"],
            asset_metadata={
                "campaign_id": campaign_id,  # Need to pass this
                "asset_type": "text",
                "channel": asset_proposal.get('channel'),
            }
        )
        
        return {
            "success": True,
            "asset_type": "text",
            "content": text_result.get('content'),
            "asset_id": text_result.get('asset_id'),
        }
    finally:
        db.close()
```

**Tasks**:
- [ ] **Integrate `llm_text_gen` service** for text asset generation
- [ ] **Save text assets** to Asset Library using `save_and_track_text_content`
- [ ] **Test text generation** with campaign workflow
- [ ] **Handle errors** - what if LLM fails?

**Deliverable**: Text assets (captions, CTAs) generate and save correctly

---

## 📋 Week 2: UX Polish & Testing

### Day 7-8: Pre-flight Validation UI 🟢

**Current State**: 
- Backend validation exists in `orchestrator.validate_campaign_preflight()` ✅
- Frontend doesn't show cost/limits before generation

**Implementation Required**:

1. **Add validation step in CampaignWizard** (before proposal generation):
```typescript
// In CampaignWizard.tsx, add validation before generating proposals:

const [validationResult, setValidationResult] = useState<any>(null);

const validateCampaign = async () => {
  // Call pre-flight check API
  const response = await fetch('/api/product-marketing/campaigns/validate', {
    method: 'POST',
    body: JSON.stringify({
      campaign_id: blueprint.campaign_id,
      channels: selectedChannels,
    })
  });
  const result = await response.json();
  setValidationResult(result);
  
  if (!result.can_proceed) {
    // Show error with upgrade prompt
  }
};
```

2. **Show cost breakdown** before proposal generation
3. **Display subscription limits** clearly
4. **Block workflow** if limits exceeded (with upgrade CTA)

**Tasks**:
- [ ] **Create validation endpoint** (or use existing orchestrator method)
- [ ] **Add validation UI** in CampaignWizard
- [ ] **Show cost estimates** for all assets
- [ ] **Handle subscription limit errors** gracefully
- [ ] **Add upgrade prompts** when limits exceeded

**Deliverable**: Users see costs and limits before generating assets

---

### Day 9-10: Proposal Review Enhancements 🟢

**Current State**: 
- ProposalReview component exists ✅
- Basic functionality works
- **Missing**: Better UX features

**Enhancements Needed**:

1. **Prompt Editing** (Partially implemented):
   - [x] Edit prompt UI exists (line 97-108)
   - [ ] **Save edited prompt** back to proposal in database
   - [ ] **Validate prompt** before saving

2. **Cost Display**:
   - [ ] **Show individual costs** prominently for each proposal
   - [ ] **Total cost** calculation for selected assets
   - [ ] **Cost breakdown** by asset type

3. **Batch Actions**:
   - [x] Select all/none exists
   - [ ] **Batch approve/reject** proposals
   - [ ] **Bulk edit prompts** (for similar assets)

4. **Status Indicators**:
   - [ ] **Visual status** for each proposal (proposed, generating, ready, approved)
   - [ ] **Progress tracking** - show which assets are being generated
   - [ ] **Success/error states** for generated assets

**Tasks**:
- [ ] **Enhance prompt editing** - save to database
- [ ] **Improve cost display** - make it prominent
- [ ] **Add batch operations** - approve/reject multiple
- [ ] **Add status indicators** - visual feedback

**Deliverable**: Better user experience in proposal review

---

### Day 11-12: Testing & Bug Fixes ✅

**End-to-End Testing**:

1. **Happy Path**:
   - [ ] Create campaign → Generate proposals → Review → Generate assets → Verify in Asset Library

2. **Error Scenarios**:
   - [ ] Subscription limits exceeded
   - [ ] API failures during generation
   - [ ] Network timeouts
   - [ ] Invalid proposal data

3. **Edge Cases**:
   - [ ] User with no onboarding data
   - [ ] Campaign with many assets (20+)
   - [ ] Rapid sequential operations
   - [ ] Browser refresh mid-workflow

4. **Performance**:
   - [ ] Page load times
   - [ ] Large proposal lists (50+ proposals)
   - [ ] Concurrent asset generation

**Bug Fixes**:
- [ ] Fix any discovered issues
- [ ] Improve error messages
- [ ] Add loading states where missing
- [ ] Polish UI/UX inconsistencies

**Deliverable**: Stable, tested MVP

---

## 🔍 Code Review Checklist

Before considering MVP complete, verify all items:

### Backend ✅
- [ ] Proposals save to database automatically
- [ ] Database tables exist and migrations run
- [ ] Asset generation works for images
- [ ] Text generation works for captions/CTAs
- [ ] Error handling covers all edge cases
- [ ] Subscription limits are enforced
- [ ] Brand DNA loads from onboarding data
- [ ] Campaign status updates correctly

### Frontend ✅
- [ ] Asset generation works from proposal review
- [ ] Pre-flight validation shows in UI
- [ ] Assets appear in Asset Library with proper metadata
- [ ] Campaign progress updates correctly
- [ ] Error states show user-friendly messages
- [ ] Loading states provide feedback
- [ ] Mobile responsive (test on mobile)

### Integration ✅
- [ ] End-to-end workflow works smoothly
- [ ] Data flows correctly: Wizard → Proposals → Assets → Library
- [ ] Campaign state persists across page refreshes
- [ ] Asset metadata links back to campaigns

---

## 📊 Success Criteria

**MVP is complete when**:
1. ✅ User can create campaign via wizard
2. ✅ Proposals generate automatically with brand DNA
3. ✅ User can review and edit proposals
4. ✅ User can generate assets (images + text) from proposals
5. ✅ Generated assets appear in Asset Library
6. ✅ Campaign status tracks progress correctly
7. ✅ Subscription limits are enforced
8. ✅ Error handling works gracefully

---

## 🚀 Quick Start Commands

### 1. Fix Proposal Persistence
```bash
# Edit backend/routers/product_marketing.py
# Add save_proposals() call after line 199
```

### 2. Create Migration
```bash
cd backend
alembic revision --autogenerate -m "Add product marketing tables"
alembic upgrade head
```

### 3. Test Flow
```bash
# Start backend
cd backend && python -m uvicorn app:app --reload

# Start frontend
cd frontend && npm start

# Navigate to http://localhost:3000/product-marketing
```

---

## 📝 Notes

- All backend services follow existing patterns ✅
- Frontend components use Image Studio UI patterns ✅
- Integration points are clean and maintainable ✅
- **Main work**: Connect the pieces and add error handling

**Estimated Time**: 1-2 weeks for MVP completion  
**Priority**: High - Unlocks full campaign workflow

---

**Last Updated**: December 2024  
**Next Review**: After MVP completion

