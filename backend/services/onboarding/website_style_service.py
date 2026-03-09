"""Website Style Service for generating themes and CSS based on site brief."""
from typing import Dict, Any, Optional, List
from loguru import logger
import json


class WebsiteStyleService:
    """Service for generating website themes and CSS from site brief data."""
    
    def __init__(self):
        logger.info("🔄 Initializing WebsiteStyleService...")
        self.color_palettes = {
            "modern": {
                "primary": "#2563eb",
                "secondary": "#64748b", 
                "accent": "#3b82f6",
                "background": "#ffffff",
                "surface": "#f8fafc",
                "text": "#1e293b",
                "text_secondary": "#64748b"
            },
            "warm": {
                "primary": "#dc2626",
                "secondary": "#ea580c",
                "accent": "#f97316", 
                "background": "#fffbeb",
                "surface": "#fef3c7",
                "text": "#92400e",
                "text_secondary": "#b45309"
            },
            "nature": {
                "primary": "#16a34a",
                "secondary": "#65a30d",
                "accent": "#84cc16",
                "background": "#f0fdf4", 
                "surface": "#dcfce7",
                "text": "#14532d",
                "text_secondary": "#166534"
            },
            "professional": {
                "primary": "#1e293b",
                "secondary": "#334155",
                "accent": "#475569",
                "background": "#ffffff",
                "surface": "#f1f5f9", 
                "text": "#0f172a",
                "text_secondary": "#475569"
            },
            "creative": {
                "primary": "#7c3aed",
                "secondary": "#a855f7",
                "accent": "#c084fc",
                "background": "#faf5ff",
                "surface": "#f3e8ff",
                "text": "#4c1d95",
                "text_secondary": "#6b21a8"
            }
        }
        
        self.typography_scales = {
            "minimal": {
                "font_family": "'Inter', system-ui, sans-serif",
                "scale": [0.75, 0.875, 1, 1.125, 1.25, 1.5, 1.875, 2.25],
                "line_height": 1.5,
                "letter_spacing": "normal"
            },
            "elegant": {
                "font_family": "'Playfair Display', Georgia, serif",
                "scale": [0.8, 0.9, 1, 1.1, 1.25, 1.5, 1.875, 2.25],
                "line_height": 1.6,
                "letter_spacing": "0.01em"
            },
            "modern": {
                "font_family": "'Space Grotesk', system-ui, sans-serif", 
                "scale": [0.75, 0.875, 1, 1.125, 1.25, 1.5, 1.875, 2.5],
                "line_height": 1.4,
                "letter_spacing": "-0.01em"
            },
            "friendly": {
                "font_family": "'Nunito', system-ui, sans-serif",
                "scale": [0.8, 0.9, 1, 1.125, 1.25, 1.5, 1.75, 2],
                "line_height": 1.6,
                "letter_spacing": "0.02em"
            }
        }
        
        self.spacing_scales = {
            "compact": {"unit": "0.25rem", "scale": [0, 1, 2, 4, 6, 8, 12, 16, 24]},
            "comfortable": {"unit": "0.5rem", "scale": [0, 1, 2, 3, 4, 6, 8, 12, 16]},
            "spacious": {"unit": "1rem", "scale": [0, 1, 2, 3, 4, 6, 8, 12, 16, 20]}
        }

    def _extract_brand_personality(self, site_brief: Dict[str, Any]) -> Dict[str, Any]:
        """Extract brand personality from site brief."""
        site_brief_data = site_brief.get("site_brief", {})
        brand_voice = site_brief_data.get("brand_voice", {})
        
        tone = brand_voice.get("tone", "professional").lower()
        adjectives = brand_voice.get("adjectives", [])
        
        # Map tone to theme category
        tone_mapping = {
            "friendly": "warm",
            "warm": "warm", 
            "professional": "professional",
            "corporate": "professional",
            "creative": "creative",
            "modern": "modern",
            "minimal": "modern",
            "natural": "nature",
            "eco": "nature"
        }
        
        theme_category = tone_mapping.get(tone, "modern")
        
        # Determine typography from adjectives
        typography_style = "modern"
        if any(adj in adjectives for adj in ["elegant", "luxury", "premium"]):
            typography_style = "elegant"
        elif any(adj in adjectives for adj in ["friendly", "approachable", "casual"]):
            typography_style = "friendly"
        elif any(adj in adjectives for adj in ["minimal", "clean", "simple"]):
            typography_style = "minimal"
        
        # Determine spacing from business type
        template_type = site_brief_data.get("template_type", "blog")
        spacing_style = "comfortable"
        if template_type == "shop":
            spacing_style = "spacious"
        elif template_type == "profile":
            spacing_style = "compact"
        
        return {
            "theme_category": theme_category,
            "typography_style": typography_style,
            "spacing_style": spacing_style,
            "tone": tone,
            "adjectives": adjectives
        }

    def _generate_color_variations(self, base_palette: Dict[str, str], brand_adjectives: List[str]) -> Dict[str, str]:
        """Generate color variations based on brand adjectives."""
        colors = base_palette.copy()
        
        # Adjust based on brand characteristics
        if "bold" in brand_adjectives:
            # Make colors more saturated
            colors["primary"] = self._saturate_color(colors["primary"], 1.2)
            colors["accent"] = self._saturate_color(colors["accent"], 1.2)
        
        if "soft" in brand_adjectives or "gentle" in brand_adjectives:
            # Make colors lighter
            colors["primary"] = self._lighten_color(colors["primary"], 0.8)
            colors["secondary"] = self._lighten_color(colors["secondary"], 0.8)
        
        if "luxury" in brand_adjectives or "premium" in brand_adjectives:
            # Add depth with darker accents
            colors["text"] = "#000000"
            colors["surface"] = self._darken_color(colors["surface"], 0.95)
        
        return colors

    def _saturate_color(self, hex_color: str, factor: float) -> str:
        """Simple color saturation (placeholder implementation)."""
        # In production, use a proper color library
        return hex_color

    def _lighten_color(self, hex_color: str, factor: float) -> str:
        """Simple color lightening (placeholder implementation)."""
        # In production, use a proper color library
        return hex_color

    def _darken_color(self, hex_color: str, factor: float) -> str:
        """Simple color darkening (placeholder implementation)."""
        # In production, use a proper color library
        return hex_color

    def generate_theme_tokens(self, site_brief: Dict[str, Any], user_id: Optional[str] = None) -> Dict[str, Any]:
        """Generate design tokens from site brief."""
        try:
            logger.info(f"Generating theme tokens for user {user_id}")
            
            brand_personality = self._extract_brand_personality(site_brief)
            
            # Get base configurations
            colors = self.color_palettes[brand_personality["theme_category"]]
            typography = self.typography_scales[brand_personality["typography_style"]]
            spacing = self.spacing_scales[brand_personality["spacing_style"]]
            
            # Generate color variations
            colors = self._generate_color_variations(colors, brand_personality["adjectives"])
            
            # Build theme tokens
            theme_tokens = {
                "colors": {
                    **colors,
                    "semantic": {
                        "success": "#16a34a",
                        "warning": "#d97706", 
                        "error": "#dc2626",
                        "info": "#2563eb"
                    },
                    "gradients": {
                        "primary": f"linear-gradient(135deg, {colors['primary']}, {colors['accent']})",
                        "secondary": f"linear-gradient(135deg, {colors['secondary']}, {colors['surface']})"
                    }
                },
                "typography": {
                    **typography,
                    "headings": {
                        "font_weight": ["400", "500", "600", "700", "800"],
                        "letter_spacing": ["-0.02em", "-0.01em", "0", "0.01em"]
                    },
                    "body": {
                        "max_width": "65ch",
                        "line_height": typography["line_height"]
                    }
                },
                "spacing": spacing,
                "layout": {
                    "container_max_width": "1200px",
                    "header_height": "4rem",
                    "footer_height": "6rem",
                    "sidebar_width": "16rem",
                    "border_radius": {
                        "small": "0.25rem",
                        "medium": "0.5rem", 
                        "large": "1rem",
                        "full": "9999px"
                    },
                    "shadows": {
                        "small": "0 1px 2px 0 rgb(0 0 0 / 0.05)",
                        "medium": "0 4px 6px -1px rgb(0 0 0 / 0.1)",
                        "large": "0 10px 15px -3px rgb(0 0 0 / 0.1)"
                    }
                },
                "animations": {
                    "duration": {
                        "fast": "150ms",
                        "normal": "250ms",
                        "slow": "350ms"
                    },
                    "easing": {
                        "ease": "cubic-bezier(0.4, 0, 0.2, 1)",
                        "ease_in": "cubic-bezier(0.4, 0, 1, 1)",
                        "ease_out": "cubic-bezier(0, 0, 0.2, 1)"
                    }
                },
                "brand": {
                    "personality": brand_personality,
                    "template_type": site_brief.get("site_brief", {}).get("template_type", "blog")
                }
            }
            
            logger.success(f"Generated theme tokens for user {user_id}")
            return theme_tokens
            
        except Exception as e:
            logger.error(f"Failed to generate theme tokens: {str(e)}")
            return {"error": f"Theme generation failed: {str(e)}"}

    def render_css(self, theme_tokens: Dict[str, Any]) -> str:
        """Render theme tokens as CSS custom properties."""
        try:
            if "error" in theme_tokens:
                logger.warning("Cannot render CSS from error tokens")
                return ""
            
            logger.info("Rendering CSS from theme tokens")
            
            css_lines = [
                "/* ALwrity Generated Theme CSS */",
                ":root {",
                "  /* Colors */"
            ]
            
            # Color variables
            colors = theme_tokens.get("colors", {})
            for key, value in colors.items():
                if key == "gradients":
                    for grad_key, grad_value in value.items():
                        css_lines.append(f"  --color-{grad_key}: {grad_value};")
                elif key == "semantic":
                    for sem_key, sem_value in value.items():
                        css_lines.append(f"  --color-{sem_key}: {sem_value};")
                else:
                    css_lines.append(f"  --color-{key}: {value};")
            
            # Typography variables
            css_lines.extend([
                "",
                "  /* Typography */",
                f"  --font-family: {theme_tokens.get('typography', {}).get('font_family', 'system-ui')};",
                f"  --line-height: {theme_tokens.get('typography', {}).get('line_height', 1.5)};",
                f"  --letter-spacing: {theme_tokens.get('typography', {}).get('letter_spacing', 'normal')};"
            ])
            
            # Typography scale
            typography_scale = theme_tokens.get("typography", {}).get("scale", [])
            for i, size in enumerate(typography_scale):
                css_lines.append(f"  --font-size-{i}: {size}rem;")
            
            # Spacing variables
            css_lines.extend([
                "",
                "  /* Spacing */"
            ])
            spacing = theme_tokens.get("spacing", {})
            spacing_unit = spacing.get("unit", "1rem")
            spacing_scale = spacing.get("scale", [])
            for i, value in enumerate(spacing_scale):
                css_lines.append(f"  --spacing-{i}: {spacing_unit * value};")
            
            # Layout variables
            css_lines.extend([
                "",
                "  /* Layout */"
            ])
            layout = theme_tokens.get("layout", {})
            css_lines.append(f"  --container-max-width: {layout.get('container_max_width', '1200px')};")
            css_lines.append(f"  --header-height: {layout.get('header_height', '4rem')};")
            css_lines.append(f"  --footer-height: {layout.get('footer_height', '6rem')};")
            
            # Border radius
            border_radius = layout.get("border_radius", {})
            for key, value in border_radius.items():
                css_lines.append(f"  --border-radius-{key}: {value};")
            
            # Shadows
            css_lines.extend([
                "",
                "  /* Shadows */"
            ])
            shadows = layout.get("shadows", {})
            for key, value in shadows.items():
                css_lines.append(f"  --shadow-{key}: {value};")
            
            # Animation variables
            css_lines.extend([
                "",
                "  /* Animations */"
            ])
            animations = theme_tokens.get("animations", {})
            duration = animations.get("duration", {})
            for key, value in duration.items():
                css_lines.append(f"  --duration-{key}: {value};")
            
            easing = animations.get("easing", {})
            for key, value in easing.items():
                css_lines.append(f"  --easing-{key}: {value};")
            
            css_lines.append("}")
            
            # Utility classes
            css_lines.extend([
                "",
                "/* Utility Classes */",
                ".text-primary { color: var(--color-primary); }",
                ".text-secondary { color: var(--color-secondary); }",
                ".bg-primary { background-color: var(--color-primary); }",
                ".bg-secondary { background-color: var(--color-secondary); }",
                ".bg-surface { background-color: var(--color-surface); }",
                "",
                "/* Typography Utilities */",
                ".font-heading { font-family: var(--font-family); font-weight: 600; }",
                ".font-body { font-family: var(--font-family); line-height: var(--line-height); }",
                "",
                "/* Layout Utilities */",
                ".container { max-width: var(--container-max-width); margin: 0 auto; padding: 0 var(--spacing-4); }",
                ".section { padding: var(--spacing-8) 0; }",
                "",
                "/* Component Styles */",
                ".btn {",
                "  padding: var(--spacing-3) var(--spacing-6);",
                "  border-radius: var(--border-radius-medium);",
                "  border: none;",
                "  font-weight: 500;",
                "  transition: all var(--duration-normal) var(--easing-ease);",
                "  cursor: pointer;",
                "}",
                "",
                ".btn-primary {",
                "  background-color: var(--color-primary);",
                "  color: white;",
                "}",
                "",
                ".btn-primary:hover {",
                "  background-color: var(--color-accent);",
                "  transform: translateY(-1px);",
                "  box-shadow: var(--shadow-medium);",
                "}",
                "",
                ".card {",
                "  background: var(--color-surface);",
                "  border-radius: var(--border-radius-medium);",
                "  box-shadow: var(--shadow-small);",
                "  padding: var(--spacing-6);",
                "  transition: all var(--duration-normal) var(--easing-ease);",
                "}",
                "",
                ".card:hover {",
                "  box-shadow: var(--shadow-medium);",
                "  transform: translateY(-2px);",
                "}"
            ])
            
            css = "\n".join(css_lines)
            logger.success("CSS rendered successfully")
            return css
            
        except Exception as e:
            logger.error(f"Failed to render CSS: {str(e)}")
            return f"/* Error rendering CSS: {str(e)} */"

    def get_theme_preview_data(self, theme_tokens: Dict[str, Any]) -> Dict[str, Any]:
        """Get preview data for theme visualization."""
        try:
            colors = theme_tokens.get("colors", {})
            typography = theme_tokens.get("typography", {})
            brand = theme_tokens.get("brand", {})
            
            return {
                "primary_color": colors.get("primary", "#2563eb"),
                "secondary_color": colors.get("secondary", "#64748b"),
                "background_color": colors.get("background", "#ffffff"),
                "text_color": colors.get("text", "#1e293b"),
                "font_family": typography.get("font_family", "system-ui"),
                "theme_category": brand.get("personality", {}).get("theme_category", "modern"),
                "template_type": brand.get("template_type", "blog"),
                "preview_css": self.render_css(theme_tokens)
            }
            
        except Exception as e:
            logger.error(f"Failed to generate theme preview: {str(e)}")
            return {"error": f"Preview generation failed: {str(e)}"}


# Singleton instance
website_style_service = WebsiteStyleService()
