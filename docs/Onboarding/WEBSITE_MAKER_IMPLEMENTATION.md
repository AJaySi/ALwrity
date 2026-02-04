# ALwrity Website Maker — Implementation Guide (Developer SSOT)

This document is the **Single Source of Truth** for the current Website Maker implementation. It describes **what is implemented today**, **how the flow is wired end-to-end**, and **how to extend it safely**. All references below are to current code in the repo.

---

## 1) End-to-end flow (current implementation)

### 1.1 User flow (frontend)
1. **Onboarding Step 2 (No Website)** collects a **website-specific intake** from non‑technical users. Defaults include “Don’t know yet” for uncertain inputs. The intake is cached client-side. The same step still persists a minimal `BusinessInfo` record for backward compatibility. **Source**: `BusinessDescriptionStep.tsx` and onboarding cache service.【F:frontend/src/components/OnboardingWizard/BusinessDescriptionStep.tsx†L1-L225】【F:frontend/src/services/onboardingCache.ts†L1-L200】
2. **Onboarding Final Step** loads cached Step 2 intake and **requests a preview** from the backend. The response includes HTML/CSS and the preview URL, which is rendered in an iframe. **Source**: `FinalStep.tsx` and `generateWebsitePreview`.【F:frontend/src/components/OnboardingWizard/FinalStep/FinalStep.tsx†L1-L492】【F:frontend/src/api/onboarding.ts†L200-L252】
3. From the preview section, the user can **Deploy Website**. This posts the cached intake to `/api/onboarding/website-deploy` and surfaces the live URL. **Source**: `FinalStep.tsx`, `deployWebsite`.【F:frontend/src/components/OnboardingWizard/FinalStep/FinalStep.tsx†L382-L470】【F:frontend/src/api/onboarding.ts†L232-L241】

### 1.2 Server flow (backend)
1. **Preview endpoint**: `/api/onboarding/website-preview` (FastAPI) takes the intake, runs LLM intake analysis (site brief + Exa query map), generates CSS tokens, writes local HTML/CSS preview files, and stores `preview_url` in the user website record. **Source**: `onboarding_manager.py`, `endpoints_config_data.py`, `website_intake_service.py`, `website_style_service.py`, `website_automation_service.py` (preview generator).【F:backend/alwrity_utils/onboarding_manager.py†L360-L412】【F:backend/api/onboarding_utils/endpoints_config_data.py†L200-L256】【F:backend/services/onboarding/website_intake_service.py†L1-L170】【F:backend/services/onboarding/website_style_service.py†L1-L130】【F:backend/services/website_automation_service.py†L1-L286】
2. **Deploy endpoint**: `/api/onboarding/website-deploy` runs the same intake analysis + style generation and then triggers **GitHub + Netlify automation**, persisting `github_repo_url` and `netlify_site_url` for the current user. **Source**: `endpoints_config_data.py`, `api/onboarding_utils/website_automation_service.py`, `user_website_service.py`.【F:backend/api/onboarding_utils/endpoints_config_data.py†L260-L304】【F:backend/api/onboarding_utils/website_automation_service.py†L1-L301】【F:backend/services/user_website_service.py†L1-L99】

---

## 2) Data model & persistence

### 2.1 `user_websites` table (platform DB)
Stores preview and deployment metadata per user.
- `user_id` is a **string** (Clerk user ID). 
- `preview_url` + `netlify_site_url` allow continuity between preview and deployment.

**Schema**: `backend/database/migrations/add_user_websites_table.sql` and SQLAlchemy model in `models/user_website.py`.【F:backend/database/migrations/add_user_websites_table.sql†L1-L24】【F:backend/models/user_website.py†L1-L52】

### 2.2 Migration runner
A lightweight script exists for SQLite dev environments.
- `backend/scripts/run_user_websites_migration.py` will create the table in `backend/alwrity.db` if missing.【F:backend/scripts/run_user_websites_migration.py†L1-L47】

### 2.3 Access layer
`UserWebsiteService` creates and updates records (preview, deploy, status). It is used in preview and deploy endpoints. **Source**: `backend/services/user_website_service.py`.【F:backend/services/user_website_service.py†L1-L99】

### 2.4 Onboarding summary
The onboarding summary now exposes `preview_url` and `live_url` from `user_websites`, enabling the frontend to display them later. **Source**: `backend/api/onboarding_utils/onboarding_summary_service.py`.【F:backend/api/onboarding_utils/onboarding_summary_service.py†L40-L80】

---

## 3) Website intake (LLM-driven site brief + Exa query map)

### 3.1 Input expectations
The intake is designed for **minimal user input** and supports **“dont_know”** values. It expects:
- Business summary + optional brand info
- Template type (blog/profile/shop/dont_know)
- Geo scope + audience type
- Product asset URLs/IDs for shops
- Optional competitor URLs

**Frontend intake UI**: `BusinessDescriptionStep.tsx`.【F:frontend/src/components/OnboardingWizard/BusinessDescriptionStep.tsx†L1-L225】

### 3.2 LLM schema (structured output)
The intake service uses `llm_text_gen` with a strict JSON schema:
- `site_brief`: business name, template, geo scope, offerings, audience, contact, competitor URLs, product assets
- `content_plan`: required pages + key points + CTA
- `exa_query_map`: per‑page queries for Exa research
- `quality_flags`: confidence + missing fields + follow‑ups

**Source**: `SITE_BRIEF_SCHEMA` in `website_intake_service.py`.【F:backend/services/onboarding/website_intake_service.py†L1-L134】

### 3.3 Prompting rules
The prompt explicitly **minimizes assumptions** and prefers `dont_know` when input is missing. This keeps results consistent for low‑input users. **Source**: `WebsiteIntakeService.build_prompt`.【F:backend/services/onboarding/website_intake_service.py†L80-L109】

---

## 4) Styling (AI‑generated CSS tokens)

### 4.1 Style token generation
The system asks the LLM for **safe, minimal tokens** (hex colors, fonts, px values). It uses a strict JSON schema to avoid malformed CSS. **Source**: `website_style_service.py` and `STYLE_SCHEMA`.【F:backend/services/onboarding/website_style_service.py†L1-L64】

### 4.2 Rendering CSS safely
Tokens are rendered into **scoped CSS variables** + minimal class overrides:
- `:root` variables
- `.alwrity-theme`, `.alwrity-button`, `.alwrity-card`

This avoids breaking base templates and keeps the theme isolated. **Source**: `WebsiteStyleService.render_css`.【F:backend/services/onboarding/website_style_service.py†L42-L128】

---

## 5) Preview generation (local HTML/CSS)

### 5.1 Preview outputs
Preview generation writes HTML files to `generated_sites/user_<id>/` and returns:
- `preview_url` (file:// URL)
- `preview_files`
- `preview_html` (HTML for iframe rendering)

**Source**: `WebsiteAutomationService.generate_preview_site`.【F:backend/services/website_automation_service.py†L63-L123】

### 5.2 SEO metadata in preview
Preview HTML includes:
- `<title>`, meta description, canonical URL
- Open Graph + Twitter cards
- JSON‑LD (Organization or ItemList + Product)

**Source**: `_render_page_html`, `_build_meta_description`, `_build_canonical_url`, `_build_structured_data`.【F:backend/services/website_automation_service.py†L140-L286】

### 5.3 Canonical URL strategy
Canonical URLs prefer **stored Netlify live URLs** when available; otherwise they fall back to a slug‑based Netlify preview domain. **Source**: `_build_canonical_url`.【F:backend/services/website_automation_service.py†L189-L221】

### 5.4 Shop preview assets
If shop template + product assets exist, they are listed in the preview body, and the first product image (if any) is used as the OG image. **Source**: `_render_shop_assets_html` and `_build_og_image`.【F:backend/services/website_automation_service.py†L167-L245】

---

## 6) Deployment pipeline (GitHub + Netlify)

### 6.1 GitHub repo creation
Deploy uses PyGithub `create_repo_from_template` with a template repo based on the selected template type. **Source**: `WebsiteAutomationService._create_github_repo`.【F:backend/api/onboarding_utils/website_automation_service.py†L56-L102】

### 6.2 Hugo content population
The deploy pipeline writes Hugo content in the new repo:
- `config.toml` with SEO-friendly defaults + custom CSS reference
- `content/_index.md` for home
- `content/<page>.md` for other pages

**Source**: `_push_initial_content`.【F:backend/api/onboarding_utils/website_automation_service.py†L104-L172】

### 6.3 Template-specific markdown
Each template variant renders content differently:
- **Blog**: frontmatter with `layout: post`, highlights section
- **Profile**: services list
- **Shop**: featured products + product asset links

**Source**: `_render_markdown_page` + `_render_blog_page` + `_render_profile_page` + `_render_shop_page`.【F:backend/api/onboarding_utils/website_automation_service.py†L176-L258】

### 6.4 CSS injection into Hugo repo
Generated CSS is committed into `static/custom.css` so the deployed site inherits unique styling. **Source**: `_push_initial_content` CSS upsert. 【F:backend/api/onboarding_utils/website_automation_service.py†L142-L160】

### 6.5 Netlify deployment
Uses Netlify’s `POST /sites` API and connects the repo + Hugo build command:
- `cmd`: `hugo --gc --minify`
- `dir`: `public`

**Source**: `_deploy_to_netlify`.【F:backend/api/onboarding_utils/website_automation_service.py†L260-L299】

---

## 7) Exa search integration (for research enrichment)

### 7.1 Search helper aligned to Exa `/search`
`ExaService.search_with_contents` uses the Exa SDK with a payload aligned to the `/search` OpenAPI spec:
- supports `type`, `category`, `includeText`, `excludeText`, `maxAgeHours`
- pulls text, highlights, summaries, and LLM context

**Source**: `ExaService.search_with_contents`.【F:backend/services/research/exa_service.py†L724-L820】

### 7.2 Subscription checks + usage tracking
The helper:
- calls `validate_exa_research_operations` for subscription gating
- tracks costs via `ExaResearchProvider().track_exa_usage`

**Source**: `search_with_contents` body. 【F:backend/services/research/exa_service.py†L742-L806】

### 7.3 API constraints enforced
- `includeText` + `excludeText` are truncated to **1 entry** (Exa limit)
- `company` and `people` categories disable unsupported filters

**Source**: `search_with_contents` sanitization. 【F:backend/services/research/exa_service.py†L758-L772】

---

## 8) Frontend API & caching

### 8.1 API calls
Frontend uses new API clients:
- `generateWebsitePreview()` → `/api/onboarding/website-preview`
- `deployWebsite()` → `/api/onboarding/website-deploy`

**Source**: `frontend/src/api/onboarding.ts`.【F:frontend/src/api/onboarding.ts†L200-L241】

### 8.2 Intake caching
The intake form persists to a client‑side cache so Final Step can generate previews. **Source**: `onboardingCache` and `BusinessDescriptionStep`.【F:frontend/src/services/onboardingCache.ts†L1-L200】【F:frontend/src/components/OnboardingWizard/BusinessDescriptionStep.tsx†L1-L225】

---

## 9) Environment variables

| Variable | Purpose | Required for | Location |
|---|---|---|---|
| `EXA_API_KEY` | Exa search API | Exa research | Backend env |
| `GITHUB_ACCESS_TOKEN` | GitHub API PAT | Deploy | Backend env |
| `NETLIFY_ACCESS_TOKEN` | Netlify API token | Deploy | Backend env |
| `NETLIFY_ACCOUNT_SLUG` | Netlify team account | Optional | Backend env |

**Source**: `api/onboarding_utils/website_automation_service.py` and `services/research/exa_service.py`.【F:backend/api/onboarding_utils/website_automation_service.py†L14-L43】【F:backend/services/research/exa_service.py†L33-L83】

---

## 10) Known limitations & gaps (current implementation)

1. **Preview uses local `file://` URLs** (not hosted). Deployment is required for a real public preview.
2. **Product assets show as links in preview and markdown**, not as image tags (future enhancement if desired).
3. **Template config** uses PaperMod defaults; per‑template config is not yet specialized.
4. **SEO tags in deployed Hugo** depend on theme templates; config provides some metadata but no per‑page SEO injection.

---

## 11) Extending the system safely

### 11.1 Adding a new template type
1. Add to `templateOptions` in `BusinessDescriptionStep.tsx`.【F:frontend/src/components/OnboardingWizard/BusinessDescriptionStep.tsx†L30-L55】
2. Update `SITE_BRIEF_SCHEMA.site_brief.template_type` enum. 【F:backend/services/onboarding/website_intake_service.py†L10-L33】
3. Add a template repo mapping in `api/onboarding_utils/website_automation_service.py`.【F:backend/api/onboarding_utils/website_automation_service.py†L9-L13】
4. Implement a renderer in `_render_markdown_page` or new `_render_<template>_page`.

### 11.2 Adding richer SEO
- Preview: update `_render_page_html` in `services/website_automation_service.py`.
- Deploy: update Hugo page markdown frontmatter or theme partials to emit OG/Twitter tags and JSON‑LD.

**Source**: `services/website_automation_service.py`, `api/onboarding_utils/website_automation_service.py`.【F:backend/services/website_automation_service.py†L140-L286】【F:backend/api/onboarding_utils/website_automation_service.py†L104-L258】

### 11.3 Using Exa results in generation
Currently, the intake produces an Exa query map but does **not execute searches** in the preview or deploy pipeline. To extend:
1. Call `ExaService.search_with_contents()` per section (`home`, `about`, etc.).【F:backend/services/research/exa_service.py†L724-L820】
2. Feed the summaries into page content generation (markdown or HTML).

### 11.4 Connecting Product Marketing Studio assets
The intake allows product asset URLs and IDs and provides a link to the Product Marketing Studio UI. To deepen integration:
- Read assets directly from Product Marketing Studio APIs instead of manual URLs
- Render assets as `![image](url)` in Hugo markdown for shop template

**Current intake fields**: `product_asset_urls`, `product_asset_ids`.【F:frontend/src/components/OnboardingWizard/BusinessDescriptionStep.tsx†L160-L225】

---

## 12) Quick reference: Key files

### Backend
- `services/onboarding/website_intake_service.py` — LLM schema & brief generation
- `services/onboarding/website_style_service.py` — CSS token generation + rendering
- `services/website_automation_service.py` — Local preview HTML/CSS
- `api/onboarding_utils/website_automation_service.py` — GitHub + Netlify deployment and Hugo content population
- `services/user_website_service.py` — User website persistence
- `models/user_website.py` — User website table definition
- `database/migrations/add_user_websites_table.sql` — Migration
- `api/onboarding_utils/endpoints_config_data.py` — Preview + deploy handlers

### Frontend
- `components/OnboardingWizard/BusinessDescriptionStep.tsx` — Step 2 intake UI
- `components/OnboardingWizard/FinalStep/FinalStep.tsx` — Preview + deploy UI
- `api/onboarding.ts` — Preview/deploy API calls
- `services/onboardingCache.ts` — Intake caching

---

## 13) Operational checklist

1. **Run migration** (dev):
   ```bash
   python backend/scripts/run_user_websites_migration.py
   ```
2. **Ensure env vars**: GitHub + Netlify tokens and Exa key.
3. **Frontend**: Complete Step 2 intake → Final Step preview → Deploy.
4. **Backend**: Confirm `user_websites` records for preview/live URLs.

---

## 14) Next steps (recommended)

1. **Hosted preview**: replace `file://` preview with a temporary Netlify/Vercel preview URL.
2. **Exa-enriched content**: feed Exa summaries into page generation for more factual, industry‑specific content.
3. **Image generation**: reuse Blog Writer’s image generation for page‑level images and inject into preview and Hugo content.
4. **Template-specific SEO**: emit theme‑compatible OG/Twitter tags in Hugo layouts and add structured data per page.

---

If you extend or change any of the above, update this document so it remains the implementation SSOT.
