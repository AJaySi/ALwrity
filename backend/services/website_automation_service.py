"""
Website Automation Service
Renders HTML pages and injects generated page imagery.
"""

from typing import Any, Dict
import re


class WebsiteAutomationService:
    """Service for rendering website pages with optional page imagery."""

    def _render_page_html(self, page: str, content_html: str, site_brief: Dict[str, Any]) -> str:
        """Render HTML for a page and inject an image if available."""
        page_images = (site_brief or {}).get("page_images") or {}
        image_base64 = page_images.get(page)
        html = content_html or ""

        if not image_base64:
            return html

        image_src = image_base64 if image_base64.startswith("data:") else f"data:image/png;base64,{image_base64}"
        img_tag = (
            f'<img src="{image_src}" alt="{page} page image" '
            'style="width:100%;max-height:420px;object-fit:cover;border-radius:12px;" />'
        )
        html = f"{img_tag}\n{html}"
        return self._inject_og_image(html, image_src)

    def _inject_og_image(self, html: str, image_src: str) -> str:
        """Ensure og:image is set to the generated page image."""
        og_tag = f'<meta property="og:image" content="{image_src}" />'
        if "property=\"og:image\"" in html:
            return re.sub(
                r'<meta\\s+property=\"og:image\"\\s+content=\"[^\"]*\"\\s*/?>',
                og_tag,
                html,
                flags=re.IGNORECASE,
            )
        if "</head>" in html:
            return html.replace("</head>", f"  {og_tag}\n</head>")
        return f"{og_tag}\n{html}"
