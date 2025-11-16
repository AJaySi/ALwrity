<div align="center">

# 🚀 ALwrity — AI-Powered Digital Marketing Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://react.dev/)
[![Stars](https://img.shields.io/github/stars/AJaySi/AI-Writer?style=social)](https://github.com/AJaySi/AI-Writer/stargazers)

**Create, optimize, and publish high‑quality content across platforms — in minutes, not months.**

[🌐 Live Demo](https://www.alwrity.com) • [📚 Docs Site](https://ajaysi.github.io/ALwrity/) • [📖 Wiki](https://github.com/AJaySi/AI-Writer/wiki) • [💬 Discussions](https://github.com/AJaySi/AI-Writer/discussions) • [🐛 Issues](https://github.com/AJaySi/AI-Writer/issues)

</div>

<p align="center">
  <a href="https://ajaysi.github.io/ALwrity/"><img src="../docs-site/docs/assets/hero-1.jpg" alt="ALwrity dashboard overview" width="30%"/></a>
  <a href="https://ajaysi.github.io/ALwrity/features/blog-writer/overview/"><img src="../docs-site/docs/assets/hero-2.png" alt="Story Writer workflow" width="30%"/></a>
  <a href="https://ajaysi.github.io/ALwrity/features/seo-dashboard/overview/"><img src="../docs-site/docs/assets/hero-3.png" alt="SEO dashboard insights" width="30%"/></a>
</p>

---

### Why ALwrity
- **AI-first outcomes**: Strategy-to-publishing in one flow — strategy, research, creation, QA, and distribution.
- **Grounded & reliable**: Google grounding, Exa/Tavily research, citation management.
- **Secure & scalable**: JWT auth, OAuth2, rate limiting, monitoring, subscription/usage tracking.
- **Built for solopreneurs**: Enterprise-grade capabilities with a fast, friendly UI.

---

### Why it matters for creators & marketers
- **Reduce complexity of AI tools**: Guided flows (research → outline → write → optimize → publish) remove prompt engineering and tool-juggling.
- **Save time, ship consistently**: Phase navigation and checklists keep you moving, ensuring on-time publishing across platforms.
- **Trust the content**: Google grounding, retrieval (web/semantic/neural), and citations mean fewer rewrites and safer publishing.
- **Stay on-brand and compliant**: Personas, tone controls, and rate limits help maintain voice and prevent platform penalties.
- **Catch issues early**: Scheduler “tasks needing intervention,” alerts, and logs highlight problems before your audience sees them.

---

### What’s functional now
- **AI Blog Writer (Phases)**: Research → Outline → Content → SEO → Publish, with guarded navigation and local persistence (`frontend/src/hooks/usePhaseNavigation.ts`).
- **SEO Dashboard**: Analysis, metadata, and Google Search Console insights (see docs under `docs-site/docs/features/seo-dashboard`).
- **Story Writer**: Setup (premise) → Outline → Writing → Export with phase navigation and reset (`frontend/src/hooks/useStoryWriterPhaseNavigation.ts`).
- **LinkedIn (Factual, Google‑Grounded)**: Real Google grounding + citations + quality metrics for posts/articles/carousels/scripts (see `frontend/docs/linkedin_factual_google_grounded_url_content.md`).
- **Persona System**: Core personas and platform adaptations via APIs (`backend/api/persona.py`).
- **Facebook Persona Service**: Gemini structured JSON for Facebook‑specific persona optimization (`backend/services/persona/facebook/facebook_persona_service.py`).
- **Personalization & Brand Voice**: Validation and configuration of writing style, tone, structure (`backend/services/component_logic/personalization_logic.py`).

See details in the Wiki: [Docs Home](https://github.com/AJaySi/AI-Writer/wiki)

---

### Quick Start
1) Clone & install

```bash
git clone https://github.com/AJaySi/AI-Writer.git
cd AI-Writer/backend && pip install -r requirements.txt
cd ../frontend && npm install
```

2) Run locally

```bash
# Backend
cd backend && python start_alwrity_backend.py
# Frontend
cd frontend && npm start
```

3) Open and create
- Frontend: http://localhost:3000
- API docs (local): http://localhost:8000/api/docs
- Complete onboarding → generate content → publish

---

### Integrations & Security
- **Integrations**: Google Search Console (SEO Dashboard), LinkedIn (factual/grounded content).
- **AI Models**: OpenAI, Google Gemini/Imagen, Hugging Face, Anthropic, Mistral.
- **Security**: JWT auth, OAuth2, rate limiting, monitoring/logging.
- **Reliability**: Grounding + retrieval and citation tracking for factual generation.

---

### Tech Stack

| Area | Technologies |
| --- | --- |
| Backend | FastAPI, Python 3.10+, SQLAlchemy |
| Frontend | React 18+, TypeScript, Material‑UI, CopilotKit |
| AI/Research | OpenAI, Gemini/Imagen, Hugging Face, Anthropic, Mistral; Exa, Tavily, Serper (auto provider selection: Gemini default, HF fallback) |
| Data | SQLite (PostgreSQL‑ready) |
| Integrations | Google Search Console, LinkedIn |
| Ops | Loguru monitoring, rate limiting, JWT/OAuth2 |

---

### LLM Providers: Gemini & Hugging Face
- **Auto‑selection**: The backend auto‑selects the provider based on `GPT_PROVIDER` and available keys.  
  - Default: Gemini (if `GEMINI_API_KEY` present)  
  - Fallback: Hugging Face (if `HF_TOKEN` present)
- **Configure**:
  - `GEMINI_API_KEY=...` (text + structured JSON; image via Imagen)
  - `HF_TOKEN=...` (text via Inference API; image via supported HF models)
  - Optional: `GPT_PROVIDER=gemini` or `GPT_PROVIDER=hf_response_api`
- **Text generation**:
  - Gemini: optimized for structured outputs and fast general generation
  - HF: broad model access via the Inference Providers
- **Image generation**:
  - Gemini/Imagen and Hugging Face providers are supported with a unified interface

For module details, see `backend/services/llm_providers/README.md`.

---

### Documentation
- Docs Site (MkDocs): https://ajaysi.github.io/ALwrity/
- Blog Writer (phases and UI): `docs-site/docs/features/blog-writer/overview.md`
- SEO Dashboard overview: `docs-site/docs/features/seo-dashboard/overview.md`
- SEO Dashboard GSC integration: `docs-site/docs/features/seo-dashboard/gsc-integration.md`
- LinkedIn factual, Google-grounded content: `frontend/docs/linkedin_factual_google_grounded_url_content.md`
- Persona Development (docs-site): `docs-site/docs/features/content-strategy/personas.md`

For additional pages, browse the `docs-site/docs/` folder.

---

### Personas (Brief)
ALwrity generates a core writing persona from onboarding data, then adapts it per platform (e.g., Facebook, LinkedIn). Personas guide tone, structure, and content preferences across tools.

- Core Persona & API: `backend/api/persona.py`
- Facebook Persona Service (Gemini structured JSON): `backend/services/persona/facebook/facebook_persona_service.py`
- Personalization/Brand Voice logic: `backend/services/component_logic/personalization_logic.py`
- Docs (GitHub paths):
  - Personas (docs-site): https://github.com/AJaySi/AI-Writer/blob/main/docs-site/docs/features/content-strategy/personas.md
  - LinkedIn Grounded Content plan: https://github.com/AJaySi/AI-Writer/blob/main/frontend/docs/linkedin_factual_google_grounded_url_content.md

At a glance:
- Data → Persona: Onboarding + website analysis → core persona
- Platform adaptations: Platform-specific JSON with validations/optimizations
- Usage: Informs tone, content length, structure, and platform best practices

---

### Community
- **Docs & Wiki**: https://github.com/AJaySi/AI-Writer/wiki  
- **Discussions**: https://github.com/AJaySi/AI-Writer/discussions  
- **Issues**: https://github.com/AJaySi/AI-Writer/issues  
- **Website**: https://www.alwrity.com

---

### License
MIT — see [LICENSE](../LICENSE).

<div align="center">

Made with ❤️ by the ALwrity team

</div>
