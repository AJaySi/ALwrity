"""Website intake analysis service for AI-generated website creation."""
from typing import Dict, Any, Optional
from loguru import logger

from services.llm_providers.main_text_generation import llm_text_gen


SITE_BRIEF_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "site_brief": {
            "type": "object",
            "properties": {
                "business_name": {"type": "string"},
                "tagline": {"type": "string"},
                "template_type": {"type": "string", "enum": ["blog", "profile", "shop", "dont_know"]},
                "geo_scope": {"type": "string", "enum": ["global", "local", "hyper_local", "dont_know"]},
                "primary_offerings": {"type": "array", "items": {"type": "string"}},
                "product_assets": {
                    "type": "object",
                    "properties": {
                        "urls": {"type": "array", "items": {"type": "string"}},
                        "asset_ids": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["urls", "asset_ids"],
                },
                "audience": {
                    "type": "object",
                    "properties": {
                        "segment": {"type": "string"},
                        "b2b_b2c": {"type": "string", "enum": ["B2B", "B2C", "Both", "dont_know"]},
                        "persona_notes": {"type": "string"},
                    },
                    "required": ["segment", "b2b_b2c", "persona_notes"],
                },
                "brand_voice": {
                    "type": "object",
                    "properties": {
                        "tone": {"type": "string"},
                        "adjectives": {"type": "array", "items": {"type": "string"}},
                        "avoid": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["tone", "adjectives", "avoid"],
                },
                "contact": {
                    "type": "object",
                    "properties": {
                        "email": {"type": "string"},
                        "phone": {"type": ["string", "null"]},
                        "location": {"type": ["string", "null"]},
                    },
                    "required": ["email", "phone", "location"],
                },
                "competitor_urls": {"type": "array", "items": {"type": "string"}},
            },
            "required": [
                "business_name",
                "tagline",
                "template_type",
                "geo_scope",
                "primary_offerings",
                "audience",
                "brand_voice",
                "contact",
                "competitor_urls",
            ],
        },
        "content_plan": {
            "type": "object",
            "properties": {
                "required_pages": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "page": {
                                "type": "string",
                                "enum": ["home", "about", "services", "products", "contact", "blog", "faq"],
                            },
                            "goal": {"type": "string"},
                            "key_points": {"type": "array", "items": {"type": "string"}},
                            "cta": {"type": "string"},
                        },
                        "required": ["page", "goal", "key_points", "cta"],
                    },
                },
                "optional_sections": {"type": "array", "items": {"type": "string"}},
                "min_content_items": {"type": "integer"},
            },
            "required": ["required_pages", "optional_sections", "min_content_items"],
        },
        "exa_query_map": {
            "type": "object",
            "properties": {
                "home": {"$ref": "#/$defs/exaSection"},
                "about": {"$ref": "#/$defs/exaSection"},
                "services_or_products": {"$ref": "#/$defs/exaSection"},
                "contact": {"$ref": "#/$defs/exaSection"},
                "competitor_optional": {"$ref": "#/$defs/exaSection"},
            },
            "required": ["home", "about", "services_or_products", "contact", "competitor_optional"],
        },
        "quality_flags": {
            "type": "object",
            "properties": {
                "confidence": {"type": "number"},
                "missing_fields": {"type": "array", "items": {"type": "string"}},
                "followup_questions": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["confidence", "missing_fields", "followup_questions"],
        },
    },
    "required": ["site_brief", "content_plan", "exa_query_map", "quality_flags"],
    "$defs": {
        "exaSection": {
            "type": "object",
            "properties": {
                "queries": {"type": "array", "items": {"type": "string"}},
                "summary_query": {"type": "string"},
                "include_text": {"type": "array", "items": {"type": "string"}},
                "search_type": {"type": "string", "enum": ["auto", "neural", "fast", "deep"]},
                "category": {"type": "string"},
            },
            "required": ["queries", "summary_query", "include_text", "search_type", "category"],
        }
    },
}


class WebsiteIntakeService:
    """Generate site briefs and Exa query maps from minimal intake inputs."""

    def _normalize_list(self, value: Any) -> list:
        if not value:
            return []
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return [str(value).strip()] if str(value).strip() else []

    def _extract_product_assets(self, intake: Dict[str, Any]) -> Dict[str, list]:
        urls = self._normalize_list(intake.get("product_asset_urls"))
        asset_ids = self._normalize_list(intake.get("product_asset_ids"))
        return {"urls": urls, "asset_ids": asset_ids}

    def build_prompt(self, intake: Dict[str, Any]) -> str:
        return (
            "You are creating a website brief and research plan for a non-technical user. "
            "Use the inputs below, keep assumptions minimal, and prefer 'dont_know' when unsure. "
            "Ensure at least 5 content items across required pages.\n\n"
            f"INTAKE INPUTS:\n{intake}\n\n"
            "Output structured JSON that matches the schema exactly."
        )

    def generate_site_brief(self, intake: Dict[str, Any], user_id: Optional[str] = None) -> Dict[str, Any]:
        logger.info("Generating site brief and Exa query map from intake")
        prompt = self.build_prompt(intake)
        result = llm_text_gen(prompt=prompt, json_struct=SITE_BRIEF_SCHEMA, user_id=user_id)
        if isinstance(result, str):
            logger.warning("LLM returned string response; expected structured JSON")
            return {"error": "invalid_response", "raw": result}
        product_assets = self._extract_product_assets(intake)
        if product_assets.get("urls") or product_assets.get("asset_ids"):
            result.setdefault("site_brief", {})
            result["site_brief"]["product_assets"] = product_assets
        return result


website_intake_service = WebsiteIntakeService()
