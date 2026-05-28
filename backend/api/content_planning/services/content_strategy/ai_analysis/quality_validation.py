"""
Quality Validation Service
AI response quality assessment and strategic analysis.
"""

import logging
from typing import Dict, Any, List, Tuple

logger = logging.getLogger(__name__)


class QualityValidationService:
    """Service for quality validation and strategic analysis."""

    _RECOMMENDATION_FIELDS = ("recommendation", "title", "action", "description")
    _EVIDENCE_FIELDS = ("evidence", "rationale", "reason", "justification", "supporting_data")
    _SPECIFICITY_FIELDS = ("owner", "timeline", "kpi", "metric", "target", "channel", "audience")

    def __init__(self):
        pass

    def validate_against_schema(self, data: Dict[str, Any], schema: Dict[str, Any]) -> None:
        """Validate data against a minimal JSON-like schema definition.
        Raises ValueError on failure.
        Schema format example:
        {"type": "object", "required": ["strategy_brief", "channels"], "properties": {"strategy_brief": {"type": "object"}, "channels": {"type": "array"}}}
        """

        def _check(node, sch, path="$"):
            t = sch.get("type")
            if t == "object":
                if not isinstance(node, dict):
                    raise ValueError(f"Schema error at {path}: expected object")
                for req in sch.get("required", []):
                    if req not in node or node[req] in (None, ""):
                        raise ValueError(f"Schema error at {path}.{req}: required field missing")
                for key, sub in sch.get("properties", {}).items():
                    if key in node:
                        _check(node[key], sub, f"{path}.{key}")
            elif t == "array":
                if not isinstance(node, list):
                    raise ValueError(f"Schema error at {path}: expected array")
                item_s = sch.get("items")
                if item_s:
                    for i, item in enumerate(node):
                        _check(item, item_s, f"{path}[{i}]")
            elif t == "string":
                if not isinstance(node, str) or not node.strip():
                    raise ValueError(f"Schema error at {path}: expected non-empty string")
            elif t == "number":
                if not isinstance(node, (int, float)):
                    raise ValueError(f"Schema error at {path}: expected number")
            elif t == "boolean":
                if not isinstance(node, bool):
                    raise ValueError(f"Schema error at {path}: expected boolean")
            elif t == "any":
                return
            else:
                return

        _check(data, schema)

    def _safe_text(self, value: Any) -> str:
        return value.strip() if isinstance(value, str) else ""

    def _normalize_recommendations(self, ai_recommendations: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], List[Dict[str, str]]]:
        """Flatten heterogeneous AI payload into normalized recommendation entries."""
        entries: List[Dict[str, Any]] = []
        failures: List[Dict[str, str]] = []

        if not isinstance(ai_recommendations, dict):
            failures.append({"error": "invalid_root", "detail": "ai_recommendations must be a dictionary"})
            return entries, failures

        for section, payload in ai_recommendations.items():
            if not isinstance(payload, dict):
                failures.append({"section": str(section), "error": "invalid_section", "detail": "section payload must be an object"})
                continue

            items = payload.get("recommendations")
            if items is None:
                candidate = payload.get("recommendation") or payload.get("action") or payload.get("description")
                if isinstance(candidate, str) and candidate.strip():
                    items = [{"recommendation": candidate}]
                else:
                    failures.append({"section": str(section), "error": "missing_recommendations", "detail": "section missing recommendations list"})
                    continue

            if isinstance(items, dict):
                items = [items]
            if not isinstance(items, list):
                failures.append({"section": str(section), "error": "invalid_recommendations", "detail": "recommendations must be list or object"})
                continue

            for idx, item in enumerate(items):
                if not isinstance(item, dict):
                    failures.append({"section": str(section), "error": "invalid_item", "detail": f"recommendation[{idx}] must be object"})
                    continue

                rec_text = next((self._safe_text(item.get(field)) for field in self._RECOMMENDATION_FIELDS if self._safe_text(item.get(field))), "")
                if not rec_text:
                    failures.append({"section": str(section), "error": "missing_text", "detail": f"recommendation[{idx}] missing primary recommendation text"})
                    continue

                confidence = item.get("confidence", payload.get("metrics", {}).get("confidence", 0.5))
                try:
                    confidence = float(confidence)
                except (ValueError, TypeError):
                    confidence = 0.5

                evidence = next((self._safe_text(item.get(field)) for field in self._EVIDENCE_FIELDS if self._safe_text(item.get(field))), "")

                entry = {
                    "section": section,
                    "text": rec_text,
                    "confidence": max(0.0, min(1.0, confidence)),
                    "priority": self._safe_text(item.get("priority")) or "medium",
                    "impact": self._safe_text(item.get("impact")) or "medium",
                    "probability": self._safe_text(item.get("probability")) or "medium",
                    "implementation": self._safe_text(item.get("implementation")) or self._safe_text(item.get("status")) or "unspecified",
                    "evidence": evidence,
                    "metadata": item,
                }
                entries.append(entry)

        if failures:
            logger.warning("quality_validation_normalization_failures", extra={"validation_failures": failures})
        return entries, failures

    def _compute_recommendation_quality(self, entries: List[Dict[str, Any]]) -> Dict[str, float]:
        if not entries:
            return {"evidence_density": 0.0, "specificity": 0.0, "field_coverage": 0.0, "overall_quality": 0.0}

        evidence_count = sum(1 for e in entries if e.get("evidence"))
        specificity_hits = 0
        for entry in entries:
            metadata = entry.get("metadata", {})
            for field in self._SPECIFICITY_FIELDS:
                if self._safe_text(metadata.get(field)):
                    specificity_hits += 1
            if any(ch.isdigit() for ch in entry.get("text", "")):
                specificity_hits += 1

        coverage_fields = ["text", "priority", "impact", "confidence", "implementation", "section"]
        present = sum(1 for e in entries for field in coverage_fields if e.get(field) not in (None, ""))
        max_fields = len(entries) * len(coverage_fields)

        evidence_density = evidence_count / len(entries)
        specificity = min(1.0, specificity_hits / (len(entries) * 3))
        field_coverage = present / max_fields if max_fields else 0.0
        overall = (0.35 * evidence_density) + (0.35 * specificity) + (0.30 * field_coverage)

        return {
            "evidence_density": evidence_density,
            "specificity": specificity,
            "field_coverage": field_coverage,
            "overall_quality": overall,
        }

    def calculate_strategic_scores(self, ai_recommendations: Dict[str, Any]) -> Dict[str, float]:
        entries, _ = self._normalize_recommendations(ai_recommendations)
        quality = self._compute_recommendation_quality(entries)

        if not entries:
            return {
                "overall_score": 0.0,
                "content_quality_score": 0.0,
                "engagement_score": 0.0,
                "conversion_score": 0.0,
                "innovation_score": 0.0,
            }

        weighted_score = 0.0
        total_confidence = 0.0
        for entry in entries:
            weight = entry["confidence"]
            priority_boost = {"high": 1.1, "medium": 1.0, "low": 0.9}.get(entry["priority"].lower(), 1.0)
            impact_boost = {"high": 1.1, "medium": 1.0, "low": 0.9}.get(entry["impact"].lower(), 1.0)
            entry_score = 100.0 * quality["overall_quality"] * priority_boost * impact_boost
            weighted_score += entry_score * weight
            total_confidence += weight

        overall = weighted_score / total_confidence if total_confidence else 0.0
        return {
            "overall_score": round(overall, 2),
            "content_quality_score": round(min(100.0, overall * (1.0 + quality["field_coverage"] * 0.15)), 2),
            "engagement_score": round(min(100.0, overall * (0.9 + quality["specificity"] * 0.2)), 2),
            "conversion_score": round(min(100.0, overall * (0.9 + quality["evidence_density"] * 0.2)), 2),
            "innovation_score": round(min(100.0, overall * (0.95 + quality["specificity"] * 0.15)), 2),
        }

    def extract_market_positioning(self, ai_recommendations: Dict[str, Any]) -> Dict[str, Any]:
        entries, _ = self._normalize_recommendations(ai_recommendations)
        if not entries:
            return {"industry_position": "unknown", "competitive_advantage": "insufficient_data", "market_share": "unknown", "positioning_score": 0}

        top = max(entries, key=lambda e: e["confidence"])
        positioning_score = int(min(5, max(1, round(1 + (top["confidence"] * 4)))))
        return {
            "industry_position": top["priority"],
            "competitive_advantage": top["text"],
            "market_share": "unknown",
            "positioning_score": positioning_score,
        }

    def extract_competitive_advantages(self, ai_recommendations: Dict[str, Any]) -> List[Dict[str, Any]]:
        entries, _ = self._normalize_recommendations(ai_recommendations)
        return [
            {"advantage": e["text"], "impact": e["impact"].title(), "implementation": e["implementation"]}
            for e in entries[:5]
        ]

    def extract_strategic_risks(self, ai_recommendations: Dict[str, Any]) -> List[Dict[str, Any]]:
        entries, _ = self._normalize_recommendations(ai_recommendations)
        risks = [e for e in entries if any(k in e["text"].lower() for k in ["risk", "threat", "decline", "churn"])]
        return [{"risk": e["text"], "probability": e["probability"].title(), "impact": e["impact"].title()} for e in risks[:5]]

    def extract_opportunity_analysis(self, ai_recommendations: Dict[str, Any]) -> List[Dict[str, Any]]:
        entries, _ = self._normalize_recommendations(ai_recommendations)
        opportunities = [e for e in entries if any(k in e["text"].lower() for k in ["opportunity", "expand", "growth", "increase"])]
        return [
            {"opportunity": e["text"], "potential_impact": e["impact"].title(), "implementation_ease": e["implementation"]}
            for e in opportunities[:5]
        ]

    def validate_ai_response_quality(self, ai_response: Dict[str, Any]) -> Dict[str, Any]:
        entries, failures = self._normalize_recommendations(ai_response)
        quality = self._compute_recommendation_quality(entries)

        required_fields = ["recommendations", "insights", "metrics"]
        present_fields = sum(1 for field in required_fields if field in ai_response)
        completeness = present_fields / len(required_fields)

        confidence = 0.0
        if entries:
            confidence = sum(e["confidence"] for e in entries) / len(entries)

        return {
            "completeness": completeness,
            "relevance": quality["field_coverage"],
            "actionability": quality["specificity"],
            "confidence": confidence,
            "overall_quality": (completeness + quality["overall_quality"] + confidence) / 3,
            "validation_failures": failures,
        }

    def assess_strategy_quality(self, strategy_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess the overall quality of a content strategy."""
        quality_assessment = {
            'data_completeness': 0.0,
            'strategic_clarity': 0.0,
            'implementation_readiness': 0.0,
            'competitive_positioning': 0.0,
            'overall_quality': 0.0
        }

        required_fields = [
            'business_objectives', 'target_metrics', 'content_budget',
            'team_size', 'implementation_timeline'
        ]
        present_fields = sum(1 for field in required_fields if strategy_data.get(field))
        quality_assessment['data_completeness'] = present_fields / len(required_fields)
        quality_assessment['strategic_clarity'] = 0.7 if strategy_data.get('business_objectives') else 0.3
        quality_assessment['implementation_readiness'] = 0.6 if strategy_data.get('team_size') else 0.2
        quality_assessment['competitive_positioning'] = 0.5 if strategy_data.get('competitive_position') else 0.2
        quality_assessment['overall_quality'] = sum(quality_assessment.values()) / len(quality_assessment)

        return quality_assessment
