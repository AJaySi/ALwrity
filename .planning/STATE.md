# Project State: Alwrity

## Current Position

**Active Phase:** Phase 1 - Code Splitting & Feature-Based Lazy Loading  
**Phase Status:** ✅ Complete — Ready for Phase 2  
**Milestone:** v1.0 - Frontend Optimization

## Phase Progress

### Phase 1: Code Splitting & Feature-Based Lazy Loading
- **Status:** ✅ Complete
- **Plans:** 3 plans executed (01-01, 01-02, 01-03)

**Plans:**
- [x] 01-01: Convert 31 static imports to React.lazy with Suspense
- [x] 01-02: Add feature-gated route loading using ALWRITY_ENABLED_FEATURES
- [x] 01-03: Convert MUI icon barrel imports to individual imports (111 files)

**Results:**
- Main bundle: 8.42MB → 2.50MB (70% reduction via React.lazy)
- 190+ chunk files for route-level code splitting
- 47 routes feature-gated with ALWRITY_ENABLED_FEATURES
- 16 feature keys in FEATURE_KEYS constant
- 111 files converted from barrel to individual MUI icon imports
- Zero barrel imports from @mui/icons-material remain

### Phase 2: Migrate CRA to Vite
- **Status:** Ready to start (Phase 1 complete)
- **Plans:** 3 plans created (02-01, 02-02, 02-03)
- **Dependencies:** Phase 1 complete

**Plans:**
- [ ] 02-01: Install Vite dependencies and create configuration
- [ ] 02-02: Migrate index.html and entry point
- [ ] 02-03: Update environment variables and scripts

### Phase 3: Production Validation (Planned)
- Depends on: Phase 2
- Focus: Vercel deploy, full feature testing

### Phase 4: (Removed — MUI icon optimization folded into Phase 1-03)

## Decisions Made

### Locked Decisions
- **Code splitting first**, then Vite migration (not the other way around) ✅ Done
- Use React.lazy for ALL route components (this is a React feature, NOT bundler-specific) ✅ Done
- Use ALWRITY_ENABLED_FEATURES for feature-gated route loading ✅ Done
- **MUI icon imports before Vite migration** — barrel imports converted to individual per-file default imports ✅ Done
- Use Vite 5.x with @vitejs/plugin-react
- Disable sourcemaps in production build for speed
- Migrate env vars from `REACT_APP_*` to `VITE_*`

### Patterns Established
- **MUI icon imports**: Always `import IconName from '@mui/icons-material/IconName'` — never barrel destructuring
- **Route splitting**: All route components use React.lazy with Suspense
- **Feature gating**: FeatureRoute wraps inside ProtectedRoute (auth → then feature check)

## Key Insight

**React.lazy is a React feature (not CRA or Vite specific).** Doing code splitting first with CRA:
1. Immediately reduces main bundle from 8.42MB → ~1-2MB
2. Adds no risk (React.lazy is stable since React 16.6)
3. Makes Vite migration smoother (bundles are already split)
4. ALWRITY_ENABLED_FEATURES can prevent disabled feature bundles from loading at all

**MUI icon barrel imports eliminated** — 111 files converted to individual per-file imports. This ensures reliable tree-shaking during Vite migration and beyond.

---

*Last updated: 2026-05-08*
*Updated by: gsd-executor*
