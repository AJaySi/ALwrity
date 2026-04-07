# Podcast Maker Journey - Developers

Use this journey to integrate Podcast Maker into repeatable, testable pipelines for scripted audio generation and distribution.

## Overview

### Entry Conditions
- **Inputs:** API credentials, topic payload schema, content constraints, output destination.
- **Skill level:** Intermediate to advanced (API and workflow automation).
- **Expected time:** 60-120 minutes for first implementation.

### Success Target
Automate one full podcast generation path from prompt to exported artifact with predictable quality.

## Setup

### Recommended Defaults
- **Duration:** 10-20 minutes (configurable per template)
- **Speakers:** 1-2 synthetic speakers
- **Voice style:** Neutral/professional with stable pacing
- **Research provider:** Perplexity (structured fact gathering for scripted outputs)

### Pre-Production Checklist
1. Define request schema for analysis/research/script/render/export stages.
2. Store provider credentials via environment variables.
3. Configure retry/error policy for external research and render calls.
4. Add logging for prompt versions and output hashes.

## Production

### Podcast Maker Workflow
1. **Analysis**
   - Validate input payload and enforce required fields.
   - Derive episode objective and section plan programmatically.
2. **Research**
   - Fetch source context with provider abstraction.
   - Normalize citations and drop low-confidence results.
3. **Script**
   - Generate structured script JSON (intro/segments/outro/CTA).
   - Run lint-style checks for length and forbidden terms.
4. **Render**
   - Render audio using configured speaker profile.
   - Execute post-render QA hooks (duration, loudness, clipping checks).
5. **Export**
   - Persist artifact + metadata to storage.
   - Trigger downstream publish/webhook integration.

## Optimization

### Success Criteria
- End-to-end pipeline completes without manual intervention.
- Output passes automated quality checks.
- Metadata includes provenance for research and prompt version.
- Failure paths are observable with actionable logs.

### Checkpoints
- **Before render:** Unit/integration checks pass for script payload.
- **After render:** Verify duration bounds and transcript alignment.
- **After publish:** Monitor error rate, latency, and output quality metrics.

## Troubleshooting

### Common Issues and Fixes
- **Provider timeouts:** Add retries with exponential backoff and fallback provider.
- **Inconsistent scripts:** Pin model settings and enforce schema validation.
- **Audio quality failures:** Add deterministic render settings and QA thresholds.
- **Broken exports:** Validate storage credentials and file naming conventions.
- **Debug difficulty:** Log stage-level inputs/outputs with correlation IDs.

---

Next step: integrate this into **[Advanced Usage](advanced-usage.md)** automation patterns.
