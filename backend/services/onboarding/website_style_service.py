"""Generate safe, minimal CSS tokens for unique website styling."""
from typing import Dict, Any, Optional
from loguru import logger

from services.llm_providers.main_text_generation import llm_text_gen


STYLE_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "theme": {
            "type": "object",
            "properties": {
                "palette": {
                    "type": "object",
                    "properties": {
                        "primary": {"type": "string"},
                        "secondary": {"type": "string"},
                        "accent": {"type": "string"},
                        "background": {"type": "string"},
                        "surface": {"type": "string"},
                        "text": {"type": "string"},
                        "muted_text": {"type": "string"},
                    },
                    "required": ["primary", "secondary", "accent", "background", "surface", "text", "muted_text"],
                },
                "typography": {
                    "type": "object",
                    "properties": {
                        "font_family": {"type": "string"},
                        "heading_weight": {"type": "string"},
                        "body_weight": {"type": "string"},
                    },
                    "required": ["font_family", "heading_weight", "body_weight"],
                },
                "spacing": {
                    "type": "object",
                    "properties": {
                        "radius_sm": {"type": "string"},
                        "radius_md": {"type": "string"},
                        "radius_lg": {"type": "string"},
                    },
                    "required": ["radius_sm", "radius_md", "radius_lg"],
                },
                "components": {
                    "type": "object",
                    "properties": {
                        "button_bg": {"type": "string"},
                        "button_text": {"type": "string"},
                        "card_border": {"type": "string"},
                    },
                    "required": ["button_bg", "button_text", "card_border"],
                },
            },
            "required": ["palette", "typography", "spacing", "components"],
        }
    },
    "required": ["theme"],
}


class WebsiteStyleService:
    """Generate safe CSS variables and small scoped overrides for themes."""

    def build_prompt(self, brief: Dict[str, Any]) -> str:
        return (
            "Generate a compact design token set for a website theme. "
            "Return safe values only (hex colors, readable font families, and px values). "
            "Avoid experimental CSS, gradients, or animations.\n\n"
            f"SITE BRIEF:\n{brief}\n\n"
            "Output JSON that matches the schema exactly."
        )

    def generate_theme_tokens(self, brief: Dict[str, Any], user_id: Optional[str] = None) -> Dict[str, Any]:
        logger.info("Generating website style tokens from brief")
        prompt = self.build_prompt(brief)
        result = llm_text_gen(prompt=prompt, json_struct=STYLE_SCHEMA, user_id=user_id)
        if isinstance(result, str):
            logger.warning("LLM returned string response; expected structured JSON")
            return {"error": "invalid_response", "raw": result}
        return result

    def render_css(self, tokens: Dict[str, Any]) -> str:
        theme = tokens.get("theme", {})
        palette = theme.get("palette", {})
        typography = theme.get("typography", {})
        spacing = theme.get("spacing", {})
        components = theme.get("components", {})

        return (
            ":root {\n"
            f"  --alwrity-primary: {palette.get('primary', '#1f2933')};\n"
            f"  --alwrity-secondary: {palette.get('secondary', '#3b82f6')};\n"
            f"  --alwrity-accent: {palette.get('accent', '#22c55e')};\n"
            f"  --alwrity-bg: {palette.get('background', '#ffffff')};\n"
            f"  --alwrity-surface: {palette.get('surface', '#f9fafb')};\n"
            f"  --alwrity-text: {palette.get('text', '#111827')};\n"
            f"  --alwrity-muted: {palette.get('muted_text', '#6b7280')};\n"
            f"  --alwrity-font: {typography.get('font_family', 'Inter, sans-serif')};\n"
            f"  --alwrity-heading-weight: {typography.get('heading_weight', '600')};\n"
            f"  --alwrity-body-weight: {typography.get('body_weight', '400')};\n"
            f"  --alwrity-radius-sm: {spacing.get('radius_sm', '6px')};\n"
            f"  --alwrity-radius-md: {spacing.get('radius_md', '10px')};\n"
            f"  --alwrity-radius-lg: {spacing.get('radius_lg', '16px')};\n"
            "}\n\n"
            ".alwrity-theme {\n"
            "  background: var(--alwrity-bg);\n"
            "  color: var(--alwrity-text);\n"
            "  font-family: var(--alwrity-font);\n"
            "  font-weight: var(--alwrity-body-weight);\n"
            "}\n\n"
            ".alwrity-theme h1,\n"
            ".alwrity-theme h2,\n"
            ".alwrity-theme h3 {\n"
            "  font-weight: var(--alwrity-heading-weight);\n"
            "}\n\n"
            ".alwrity-button {\n"
            f"  background: {components.get('button_bg', 'var(--alwrity-primary)')};\n"
            f"  color: {components.get('button_text', '#ffffff')};\n"
            "  border-radius: var(--alwrity-radius-md);\n"
            "}\n\n"
            ".alwrity-card {\n"
            f"  border: 1px solid {components.get('card_border', 'var(--alwrity-secondary)')};\n"
            "  border-radius: var(--alwrity-radius-lg);\n"
            "  background: var(--alwrity-surface);\n"
            "}\n"
        )


website_style_service = WebsiteStyleService()
