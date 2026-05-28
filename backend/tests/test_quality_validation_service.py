import importlib.util
from pathlib import Path


def _load_service_class():
    module_path = Path(__file__).resolve().parents[1] / "api/content_planning/services/content_strategy/ai_analysis/quality_validation.py"
    spec = importlib.util.spec_from_file_location("quality_validation", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module.QualityValidationService


QualityValidationService = _load_service_class()


def _service():
    return QualityValidationService()


def test_quality_validation_good_payload():
    payload = {
        "market_analysis": {
            "recommendations": [
                {
                    "recommendation": "Expand webinar content to enterprise segment by Q3 with 15% MQL target",
                    "evidence": "Pipeline attribution shows webinars convert 2.1x vs blog traffic",
                    "priority": "high",
                    "impact": "high",
                    "confidence": 0.9,
                    "timeline": "Q3",
                    "owner": "Demand Gen",
                    "kpi": "MQL"
                },
                {
                    "recommendation": "Increase LinkedIn video cadence to 3 posts/week",
                    "evidence": "Audience engagement up 28% on short-form clips",
                    "priority": "medium",
                    "impact": "medium",
                    "confidence": 0.8,
                    "channel": "LinkedIn",
                    "metric": "Engagement rate"
                },
            ]
        }
    }

    service = _service()
    scores = service.calculate_strategic_scores(payload)
    quality = service.validate_ai_response_quality(payload)
    advantages = service.extract_competitive_advantages(payload)

    assert scores["overall_score"] > 50
    assert quality["overall_quality"] > 0.5
    assert quality["validation_failures"] == []
    assert len(advantages) == 2
    assert advantages[0]["advantage"].startswith("Expand webinar")


def test_quality_validation_partial_payload_handles_guardrails():
    payload = {
        "channel_strategy": {
            "recommendation": "Opportunity: expand newsletter personalization for retention"
        },
        "invalid_section": ["bad-shape"],
    }

    service = _service()
    quality = service.validate_ai_response_quality(payload)
    opportunities = service.extract_opportunity_analysis(payload)

    assert quality["overall_quality"] >= 0
    assert len(quality["validation_failures"]) >= 1
    assert len(opportunities) == 1
    assert opportunities[0]["opportunity"].startswith("Opportunity")


def test_quality_validation_invalid_payload():
    service = _service()
    quality = service.validate_ai_response_quality("not-a-dict")
    scores = service.calculate_strategic_scores("not-a-dict")

    assert quality["overall_quality"] == 0
    assert quality["validation_failures"][0]["error"] == "invalid_root"
    assert scores["overall_score"] == 0


def test_risk_extraction_from_deterministic_input():
    payload = {
        "risk_analysis": {
            "recommendations": [
                {
                    "title": "Risk: organic traffic decline due to SERP feature expansion",
                    "probability": "high",
                    "impact": "high",
                    "confidence": 0.7,
                }
            ]
        }
    }

    risks = _service().extract_strategic_risks(payload)
    assert risks == [
        {
            "risk": "Risk: organic traffic decline due to SERP feature expansion",
            "probability": "High",
            "impact": "High",
        }
    ]
