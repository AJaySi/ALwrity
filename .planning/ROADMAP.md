# Roadmap: Alwrity - ALwrity Frontend Optimization

## Overview

Optimize the frontend build to reduce build time from 5 minutes to under 30 seconds and shrink bundle size from 8.42MB to under 1MB. First, implement code splitting with React.lazy and feature-gated loading using ALWRITY_ENABLED_FEATURES. Then migrate from Create React App to Vite for faster builds. Finally, optimize dependencies for maximum performance.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3, 4): Planned work
- All phases planned and ready for execution

---

### Phase 1: Code Splitting & Feature-Based Lazy Loading ✅ Complete
**Goal**: Replace all static imports with React.lazy dynamic imports and add feature-gated loading using ALWRITY_ENABLED_FEATURES. Also convert MUI icon barrel imports to individual imports (moved here from Phase 3 for Vite readiness).
**Depends on**: Nothing (first phase)
**Requirements**: VITE-04 (code splitting), VITE-06 (dependency optimization)
**Success Criteria** (what must be TRUE):
   1. ✅ All 31+ route components loaded via React.lazy (not static imports)
   2. ✅ Initial bundle size reduced from 8.42MB to 2.50MB (70% reduction)
   3. ✅ Disabled features (via ALWRITY_ENABLED_FEATURES) don't load their bundles
   4. ✅ All existing routes still work correctly
   5. ✅ No build warnings or errors with CRA
   6. ✅ All MUI icon imports changed from barrel to individual (111 files)

**Plans**: 3 plans (all complete)

Plans:
- [x] 01-01: Convert 31 static imports to React.lazy with Suspense
- [x] 01-02: Add feature-gated route loading using ALWRITY_ENABLED_FEATURES
- [x] 01-03: Convert MUI icon barrel imports to individual imports (111 files)

---

### Phase 2: Migrate from CRA to Vite (Next)
**Goal**: Migrate frontend from Create React App to Vite for fast builds
**Depends on**: Phase 1 ✅
**Requirements**: VITE-01, VITE-02, VITE-03
**Success Criteria** (what must be TRUE):
   1. `npm run dev` starts Vite dev server with HMR
   2. `npm run build` completes in under 30 seconds (down from 5 minutes)
   3. All environment variables work with `VITE_*` prefix
   4. TypeScript compiles without errors
   5. Material UI theme renders correctly

**Plans**: 3 plans

Plans:
- [ ] 02-01: Install Vite dependencies and create configuration
- [ ] 02-02: Migrate index.html and entry point
- [ ] 02-03: Update environment variables and scripts

---

### Phase 3: Dependency Cleanup & Production Validation
**Goal**: Remove unused dependencies and deploy Vite build to production
**Depends on**: Phase 2
**Requirements**: VITE-07, VITE-08, VITE-09
**Success Criteria** (what must be TRUE):
   1. Unused dependencies identified and removed
   2. Production build serves correctly (preview mode)
   3. All features tested and working (Clerk auth, Stripe, CopilotKit)
   4. Vercel deployment config updated for Vite
   5. Build time consistently under 30 seconds
   6. Total bundle size under 2MB

**Plans**: 2 plans (consolidated from former Phase 3 & 4)

Plans:
- [ ] 03-01: Audit and remove unused dependencies, update Vercel config
- [ ] 03-02: Full feature testing and performance validation

---

## Execution Order

Phases execute in numeric order: 1 → 2 → 3

**Key insight:** Phase 1 (code splitting) works with CRA, so we immediately reduce bundle size. Phase 2 (Vite) gives build speed bonus on already-split bundles. Phase 3 is cleanup and deployment.

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Code Splitting & MUI Optimization | 3/3 | ✅ Complete | 2026-05-08 |
| 2. Migrate CRA to Vite | 0/3 | ⏳ Ready | - |
| 3. Cleanup & Production | 0/2 | ⏳ Planned | - |
