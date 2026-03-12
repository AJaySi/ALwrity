"""Flat-file context storage for AI agents.

Stores onboarding context in per-user workspace files, optimized for fast agent reads.
Includes minimal security hardening, context-size controls, and internal document linking.
"""

from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from loguru import logger


class AgentFlatContextStore:
    """Read/write agent-only flat-file context in per-user workspace."""

    CONTEXT_DIRNAME = "agent_context"
    STEP2_FILENAME = "step2_website_analysis.json"
    STEP3_FILENAME = "step3_research_preferences.json"
    STEP4_FILENAME = "step4_persona_data.json"
    STEP5_FILENAME = "step5_integrations.json"
    MANIFEST_FILENAME = "context_manifest.json"

    SCHEMA_VERSION = "1.3"
    DEFAULT_MAX_BYTES = 300_000
    SUMMARY_TEXT_LIMIT = 800

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.safe_user_id = self._sanitize_user_id(user_id)

    @staticmethod
    def _sanitize_user_id(user_id: str) -> str:
        safe = "".join(c for c in str(user_id) if c.isalnum() or c in ("-", "_"))
        return safe or "unknown_user"

    def _workspace_dir(self) -> Path:
        root_dir = Path(__file__).resolve().parents[3]
        return root_dir / "workspace" / f"workspace_{self.safe_user_id}"

    def _context_dir(self) -> Path:
        return self._workspace_dir() / self.CONTEXT_DIRNAME

    def _context_file(self, filename: str) -> Path:
        return self._context_dir() / filename

    @staticmethod
    def _estimate_size_bytes(value: Any) -> int:
        try:
            return len(json.dumps(value, ensure_ascii=False).encode("utf-8"))
        except Exception:
            return 0

    @staticmethod
    def _to_context_list(value: Any) -> Any:
        if value is None:
            return []
        if isinstance(value, list):
            return value
        if isinstance(value, dict):
            return list(value.keys())
        return [str(value)]

    @staticmethod
    def _truncate_text(value: Any, max_chars: int = SUMMARY_TEXT_LIMIT) -> str:
        text = value if isinstance(value, str) else ""
        if len(text) <= max_chars:
            return text
        return f"{text[:max_chars]}..."

    @staticmethod
    def _redact_sensitive(data: Any) -> Any:
        """Minimal recursive redaction for sensitive-like keys in payload snapshots."""
        sensitive_tokens = {"api_key", "token", "secret", "password", "authorization", "cookie"}
        if isinstance(data, dict):
            redacted = {}
            for k, v in data.items():
                key_lower = str(k).lower()
                if any(token in key_lower for token in sensitive_tokens):
                    redacted[k] = "[REDACTED]"
                else:
                    redacted[k] = AgentFlatContextStore._redact_sensitive(v)
            return redacted
        if isinstance(data, list):
            return [AgentFlatContextStore._redact_sensitive(v) for v in data]
        return data

    def _related_documents(self, context_type: str) -> list:
        if context_type == "onboarding_step2_website_analysis":
            return [
                {"type": "onboarding_step3_research_preferences", "path": self.STEP3_FILENAME, "relationship": "next_step"},
                {"type": "onboarding_step4_persona_data", "path": self.STEP4_FILENAME, "relationship": "future_dependency"},
                {"type": "onboarding_step5_integrations", "path": self.STEP5_FILENAME, "relationship": "future_dependency"},
            ]
        if context_type == "onboarding_step3_research_preferences":
            return [
                {"type": "onboarding_step2_website_analysis", "path": self.STEP2_FILENAME, "relationship": "previous_step"},
                {"type": "onboarding_step4_persona_data", "path": self.STEP4_FILENAME, "relationship": "next_step"},
                {"type": "onboarding_step5_integrations", "path": self.STEP5_FILENAME, "relationship": "future_dependency"},
            ]
        if context_type == "onboarding_step4_persona_data":
            return [
                {"type": "onboarding_step3_research_preferences", "path": self.STEP3_FILENAME, "relationship": "previous_step"},
                {"type": "onboarding_step2_website_analysis", "path": self.STEP2_FILENAME, "relationship": "upstream_context"},
                {"type": "onboarding_step5_integrations", "path": self.STEP5_FILENAME, "relationship": "next_step"},
            ]
        if context_type == "onboarding_step5_integrations":
            return [
                {"type": "onboarding_step4_persona_data", "path": self.STEP4_FILENAME, "relationship": "previous_step"},
                {"type": "onboarding_step3_research_preferences", "path": self.STEP3_FILENAME, "relationship": "upstream_context"},
            ]
        return []

    def _build_document_context(
        self,
        *,
        context_type: str,
        source: str,
        journey_stage: str,
        fallback_order: list,
        payload_size: int,
        summary_size: int,
        payload_within_budget: bool,
    ) -> Dict[str, Any]:
        total_size = payload_size + summary_size
        return {
            "audience": "ai_agents",
            "purpose": "fast_context_retrieval",
            "context_type": context_type,
            "source": source,
            "tenant": {"user_id_safe": self.safe_user_id, "isolation_scope": "workspace_user"},
            "journey": {
                "stage": journey_stage,
                "user_action": "onboarding",
                "agent_expectation": "read_summary_first_then_expand",
            },
            "retrieval_contract": {
                "preferred": "flat_file",
                "fallback_order": fallback_order,
            },
            "context_window_guidance": {
                "max_raw_bytes": self.DEFAULT_MAX_BYTES,
                "total_bytes": total_size,
                "raw_document_within_budget": payload_within_budget,
                "agent_policy": "Use agent_summary first; open full data only for specialist tasks",
            },
            "related_documents": self._related_documents(context_type),
        }

    def _build_step2_summary(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        seo_audit = payload.get("seo_audit") if isinstance(payload.get("seo_audit"), dict) else {}
        brand = payload.get("brand_analysis") if isinstance(payload.get("brand_analysis"), dict) else {}
        rec_settings = payload.get("recommended_settings") if isinstance(payload.get("recommended_settings"), dict) else {}
        target_audience = payload.get("target_audience") if isinstance(payload.get("target_audience"), dict) else {}
        social = payload.get("social_media_presence") if isinstance(payload.get("social_media_presence"), dict) else {}

        technical_issues = self._to_context_list(seo_audit.get("technical_issues"))
        recommendations = self._to_context_list(seo_audit.get("recommendations"))

        quick_facts = {
            "website_url": payload.get("website_url") or "",
            "brand_voice": brand.get("brand_voice") or "",
            "industry": brand.get("industry") or "",
            "target_segment": target_audience.get("primary_audience") or target_audience.get("audience_type") or "",
            "writing_tone": rec_settings.get("writing_tone") or "",
            "primary_content_type": (payload.get("content_type") or {}).get("primary_type") if isinstance(payload.get("content_type"), dict) else "",
            "social_platforms": sorted(list(social.keys())),
            "seo_issue_count": len(technical_issues),
            "seo_recommendation_count": len(recommendations),
        }

        return {
            "quick_facts": quick_facts,
            "retrieval_hints": {
                "high_signal_terms": [
                    term
                    for term in [
                        quick_facts.get("brand_voice"),
                        quick_facts.get("industry"),
                        quick_facts.get("writing_tone"),
                        quick_facts.get("primary_content_type"),
                    ]
                    if term
                ],
                "agent_queries": [
                    "brand voice guidelines",
                    "website style patterns",
                    "seo technical issues",
                    "content strategy opportunities",
                    "target audience profile",
                ],
            },
            "profile": {
                "writing_style": payload.get("writing_style") or {},
                "style_patterns": payload.get("style_patterns") or {},
                "style_guidelines": payload.get("style_guidelines") or {},
                "recommended_settings": rec_settings,
                "target_audience": target_audience,
            },
            "seo_focus": {
                "technical_issues": technical_issues,
                "recommendations": recommendations,
            },
        }

    def _build_step3_summary(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        competitors = payload.get("competitors") if isinstance(payload.get("competitors"), list) else []
        domains = []
        for comp in competitors[:20]:
            if isinstance(comp, dict):
                dom = comp.get("domain") or comp.get("url")
                if dom:
                    domains.append(str(dom))

        research_depth = payload.get("research_depth") or ""
        content_types = payload.get("content_types") if isinstance(payload.get("content_types"), list) else []
        industry_context = self._truncate_text(payload.get("industry_context") or payload.get("industryContext") or "", 500)

        return {
            "quick_facts": {
                "research_depth": research_depth,
                "content_types": content_types,
                "auto_research": bool(payload.get("auto_research", True)),
                "factual_content": bool(payload.get("factual_content", True)),
                "competitor_count": len(competitors),
            },
            "retrieval_hints": {
                "high_signal_terms": [research_depth, *content_types[:5]],
                "agent_queries": [
                    "competitor landscape summary",
                    "content opportunities by competitor",
                    "research depth preferences",
                    "factual content constraints",
                ],
            },
            "competitor_focus": {
                "top_competitor_domains": domains[:10],
                "industry_context": industry_context,
            },
        }

    def _build_step4_summary(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        core_persona = payload.get("core_persona") if isinstance(payload.get("core_persona"), dict) else {}
        platform_personas = payload.get("platform_personas") if isinstance(payload.get("platform_personas"), dict) else {}
        quality_metrics = payload.get("quality_metrics") if isinstance(payload.get("quality_metrics"), dict) else {}
        selected_platforms = payload.get("selected_platforms") if isinstance(payload.get("selected_platforms"), list) else []

        persona_name = core_persona.get("name") or core_persona.get("persona_name") or ""
        primary_goal = self._truncate_text(core_persona.get("primary_goal") or core_persona.get("goal") or "", 250)

        return {
            "quick_facts": {
                "persona_name": persona_name,
                "selected_platforms": selected_platforms,
                "platform_persona_count": len(platform_personas.keys()) if isinstance(platform_personas, dict) else 0,
                "has_research_persona": bool(payload.get("research_persona")),
            },
            "retrieval_hints": {
                "high_signal_terms": [persona_name, *selected_platforms[:5]],
                "agent_queries": [
                    "core persona profile",
                    "platform persona adaptations",
                    "persona quality metrics",
                    "research persona defaults",
                ],
            },
            "persona_focus": {
                "primary_goal": primary_goal,
                "core_persona": core_persona,
                "quality_metrics": quality_metrics,
            },
        }

    def _build_step5_summary(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        integrations = payload.get("integrations") if isinstance(payload.get("integrations"), dict) else {}
        providers = payload.get("providers") if isinstance(payload.get("providers"), list) else []
        connected = [k for k, v in integrations.items() if bool(v)]
        notes = self._truncate_text(payload.get("notes") or payload.get("integration_notes") or "", 300)

        return {
            "quick_facts": {
                "connected_integrations_count": len(connected),
                "connected_integrations": connected[:20],
                "providers_count": len(providers),
            },
            "retrieval_hints": {
                "high_signal_terms": connected[:5],
                "agent_queries": [
                    "integration readiness",
                    "connected providers summary",
                    "missing integration dependencies",
                ],
            },
            "integration_focus": {
                "notes": notes,
                "integrations": integrations,
            },
        }

    def _shrink_payload_if_needed(self, payload: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Keep payload under budget by trimming heavy optional sections first."""
        payload = self._redact_sensitive(payload if isinstance(payload, dict) else {})
        original_size = self._estimate_size_bytes(payload)
        trim_info = {"trimmed": False, "original_size_bytes": original_size, "trimmed_fields": []}

        if original_size <= self.DEFAULT_MAX_BYTES:
            return payload, trim_info

        candidates = [
            "raw_step2_payload",
            "raw_analysis_payload",
            "source_payload",
            "crawl_result",
            "competitors",
            "strategic_insights_history",
            "seo_audit",
        ]

        mutable = dict(payload)
        for field in candidates:
            if self._estimate_size_bytes(mutable) <= self.DEFAULT_MAX_BYTES:
                break
            if field in mutable:
                value = mutable.get(field)
                if field == "competitors" and isinstance(value, list):
                    mutable[field] = value[:20]
                elif isinstance(value, (dict, list)):
                    mutable[field] = {"omitted": True, "reason": "size_budget", "original_type": type(value).__name__}
                elif isinstance(value, str):
                    mutable[field] = self._truncate_text(value, 500)
                else:
                    mutable[field] = "[OMITTED:size_budget]"
                trim_info["trimmed_fields"].append(field)

        trim_info["trimmed"] = self._estimate_size_bytes(mutable) < original_size
        trim_info["final_size_bytes"] = self._estimate_size_bytes(mutable)
        return mutable, trim_info

    def _atomic_write_json(self, target_file: Path, data: Dict[str, Any]) -> None:
        target_file.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_path = tempfile.mkstemp(dir=str(target_file.parent), prefix=f".{target_file.name}.", suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp_path, target_file)
            try:
                os.chmod(target_file, 0o600)
            except Exception:
                pass
        except Exception:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass
            raise

    def _update_manifest(self, context_type: str, filename: str, doc: Dict[str, Any]) -> None:
        manifest_file = self._context_file(self.MANIFEST_FILENAME)
        existing = {}
        if manifest_file.exists():
            try:
                with open(manifest_file, "r", encoding="utf-8") as f:
                    existing = json.load(f) or {}
            except Exception:
                existing = {}

        items = existing.get("documents") if isinstance(existing.get("documents"), list) else []
        items = [i for i in items if not (isinstance(i, dict) and i.get("type") == context_type)]
        items.append(
            {
                "type": context_type,
                "path": filename,
                "updated_at": doc.get("updated_at"),
                "size_bytes": (doc.get("meta") or {}).get("data_size_bytes", 0) + (doc.get("meta") or {}).get("summary_size_bytes", 0),
                "related_documents": (doc.get("document_context") or {}).get("related_documents", []),
            }
        )

        manifest = {
            "schema_version": self.SCHEMA_VERSION,
            "user_id": str(self.user_id),
            "updated_at": datetime.utcnow().isoformat(),
            "documents": items,
        }
        self._atomic_write_json(manifest_file, manifest)

    def _save_context_document(
        self,
        *,
        filename: str,
        context_type: str,
        payload: Dict[str, Any],
        summary: Dict[str, Any],
        source: str,
        journey_stage: str,
    ) -> bool:
        try:
            target_file = self._context_file(filename)
            payload = payload if isinstance(payload, dict) else {}
            summary = summary if isinstance(summary, dict) else {}

            compact_payload, trim_info = self._shrink_payload_if_needed(payload)
            payload_size = self._estimate_size_bytes(compact_payload)
            summary_size = self._estimate_size_bytes(summary)

            context_doc = {
                "schema_version": self.SCHEMA_VERSION,
                "context_type": context_type,
                "user_id": str(self.user_id),
                "updated_at": datetime.utcnow().isoformat(),
                "source": source,
                "document_context": self._build_document_context(
                    context_type=context_type,
                    source=source,
                    journey_stage=journey_stage,
                    fallback_order=["flat_file", "database", "sif_semantic"],
                    payload_size=payload_size,
                    summary_size=summary_size,
                    payload_within_budget=payload_size <= self.DEFAULT_MAX_BYTES,
                ),
                "data": compact_payload,
                "agent_summary": summary,
                "meta": {
                    "data_size_bytes": payload_size,
                    "summary_size_bytes": summary_size,
                    "trim": trim_info,
                },
            }

            self._atomic_write_json(target_file, context_doc)
            self._update_manifest(context_type, filename, context_doc)
            return True
        except Exception as exc:
            logger.error(f"Failed to save context for user {self.user_id} ({context_type}): {exc}")
            return False

    def save_step2_website_analysis(self, payload: Dict[str, Any], *, source: str = "onboarding_step2") -> bool:
        return self._save_context_document(
            filename=self.STEP2_FILENAME,
            context_type="onboarding_step2_website_analysis",
            payload=payload,
            summary=self._build_step2_summary(payload if isinstance(payload, dict) else {}),
            source=source,
            journey_stage="onboarding_step_2",
        )

    def save_step3_research_preferences(self, payload: Dict[str, Any], *, source: str = "onboarding_step3") -> bool:
        return self._save_context_document(
            filename=self.STEP3_FILENAME,
            context_type="onboarding_step3_research_preferences",
            payload=payload,
            summary=self._build_step3_summary(payload if isinstance(payload, dict) else {}),
            source=source,
            journey_stage="onboarding_step_3",
        )

    def save_step4_persona_data(self, payload: Dict[str, Any], *, source: str = "onboarding_step4") -> bool:
        return self._save_context_document(
            filename=self.STEP4_FILENAME,
            context_type="onboarding_step4_persona_data",
            payload=payload,
            summary=self._build_step4_summary(payload if isinstance(payload, dict) else {}),
            source=source,
            journey_stage="onboarding_step_4",
        )

    def save_step5_integrations(self, payload: Dict[str, Any], *, source: str = "onboarding_step5") -> bool:
        return self._save_context_document(
            filename=self.STEP5_FILENAME,
            context_type="onboarding_step5_integrations",
            payload=payload,
            summary=self._build_step5_summary(payload if isinstance(payload, dict) else {}),
            source=source,
            journey_stage="onboarding_step_5",
        )

    def _load_context_document(self, filename: str) -> Optional[Dict[str, Any]]:
        try:
            target_file = self._context_file(filename)
            if not target_file.exists():
                return None
            with open(target_file, "r", encoding="utf-8") as f:
                doc = json.load(f)
            if isinstance(doc, dict) and str(doc.get("user_id")) != str(self.user_id):
                logger.warning(f"Context user mismatch for {filename} (expected {self.user_id})")
                return None
            return doc if isinstance(doc, dict) else None
        except Exception as exc:
            logger.warning(f"Failed to load context document for user {self.user_id} ({filename}): {exc}")
            return None

    def load_context_manifest(self) -> Optional[Dict[str, Any]]:
        return self._load_context_document(self.MANIFEST_FILENAME)

    def load_step2_context_document(self) -> Optional[Dict[str, Any]]:
        return self._load_context_document(self.STEP2_FILENAME)

    def load_step2_website_analysis(self) -> Optional[Dict[str, Any]]:
        doc = self.load_step2_context_document()
        return doc.get("data") if isinstance(doc, dict) and isinstance(doc.get("data"), dict) else None

    def load_step3_context_document(self) -> Optional[Dict[str, Any]]:
        return self._load_context_document(self.STEP3_FILENAME)

    def load_step3_research_preferences(self) -> Optional[Dict[str, Any]]:
        doc = self.load_step3_context_document()
        return doc.get("data") if isinstance(doc, dict) and isinstance(doc.get("data"), dict) else None

    def load_step4_context_document(self) -> Optional[Dict[str, Any]]:
        return self._load_context_document(self.STEP4_FILENAME)

    def load_step4_persona_data(self) -> Optional[Dict[str, Any]]:
        doc = self.load_step4_context_document()
        return doc.get("data") if isinstance(doc, dict) and isinstance(doc.get("data"), dict) else None

    def load_step5_context_document(self) -> Optional[Dict[str, Any]]:
        return self._load_context_document(self.STEP5_FILENAME)

    def load_step5_integrations(self) -> Optional[Dict[str, Any]]:
        doc = self.load_step5_context_document()
        return doc.get("data") if isinstance(doc, dict) and isinstance(doc.get("data"), dict) else None
