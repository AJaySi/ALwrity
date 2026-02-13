"""Website automation service placeholder for ALwrity Instant Site orchestration."""
from typing import Dict, Any, Optional, List
from loguru import logger
from pathlib import Path

from models.user_website_request import UserWebsiteRequest
from services.user_website_service import user_website_service
from services.onboarding.website_style_service import website_style_service


class WebsiteAutomationService:
    """Orchestrates GitHub + Netlify automation for AI-generated websites.

    NOTE: This is a scaffold service. External API calls should be implemented
    in dedicated adapters once credentials and templates are finalized.
    """

    def initialize_site(
        self,
        user_id: str,
        template_type: str = "blog",
        site_brief: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        logger.info(f"🚀 Initializing site automation for user_id={user_id}, template={template_type}")

        request = UserWebsiteRequest(
            user_id=user_id,
            template_type=template_type,
            status="initializing",
        )
        record = user_website_service.create_user_website(request)
        theme_tokens = None
        css_output = None
        if site_brief:
            theme_tokens = website_style_service.generate_theme_tokens(site_brief, user_id=str(user_id))
            if theme_tokens and not theme_tokens.get("error"):
                css_output = website_style_service.render_css(theme_tokens)
        return {
            "website_id": record.id,
            "status": record.status,
            "template_type": record.template_type,
            "theme_tokens": theme_tokens,
            "css": css_output,
        }

    def update_deployment_status(
        self,
        user_id: str,
        status: str,
        github_repo_url: Optional[str] = None,
        netlify_site_id: Optional[str] = None,
        netlify_site_url: Optional[str] = None,
        preview_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        logger.info(f"🔄 Updating deployment status for user_id={user_id} to {status}")
        record = user_website_service.update_user_website_status(
            user_id=user_id,
            status=status,
            github_repo_url=github_repo_url,
            netlify_site_id=netlify_site_id,
            netlify_site_url=netlify_site_url,
            preview_url=preview_url,
        )
        if record is None:
            return {"status": "not_found"}
        return {"status": record.status, "netlify_site_url": record.netlify_site_url}

    def generate_preview_site(
        self,
        user_id: str,
        site_brief: Dict[str, Any],
        css: str
    ) -> Dict[str, Any]:
        repo_root = Path(__file__).resolve().parents[2]
        preview_root = repo_root / "generated_sites" / f"user_{user_id}"
        preview_root.mkdir(parents=True, exist_ok=True)

        pages = self._extract_pages(site_brief)
        preview_files = []
        preview_html = None
        template_type = site_brief.get("site_brief", {}).get("template_type", "blog")

        for page in pages:
            filename = f"{page['page']}.html"
            html = self._render_page_html(site_brief, page, css, template_type)
            file_path = preview_root / filename
            file_path.write_text(html, encoding="utf-8")
            preview_files.append(str(file_path))
            if page.get("page") == "home":
                preview_html = html

        css_path = preview_root / "styles.css"
        css_path.write_text(css, encoding="utf-8")

        preview_url = f"file://{preview_root / 'home.html'}"
        self.update_deployment_status(user_id=user_id, status="preview_ready", preview_url=preview_url)
        return {
            "preview_url": preview_url,
            "preview_root": str(preview_root),
            "preview_files": preview_files,
            "css_path": str(css_path),
            "preview_html": preview_html,
        }

    def _extract_pages(self, site_brief: Dict[str, Any]) -> List[Dict[str, Any]]:
        content_plan = site_brief.get("content_plan", {})
        required_pages = content_plan.get("required_pages", [])
        if required_pages:
            return required_pages
        return [
            {"page": "home", "goal": "Introduce the business", "key_points": [], "cta": "Get in touch"},
            {"page": "about", "goal": "Share the story", "key_points": [], "cta": "Learn more"},
            {"page": "contact", "goal": "Make it easy to contact", "key_points": [], "cta": "Contact us"},
        ]

    def _render_page_html(
        self,
        site_brief: Dict[str, Any],
        page: Dict[str, Any],
        css: str,
        template_type: str,
    ) -> str:
        site = site_brief.get("site_brief", {})
        title = site.get("business_name") or "ALwrity Instant Site"
        tagline = site.get("tagline") or "AI-generated website"
        goal = page.get("goal", "")
        key_points = page.get("key_points", []) or []
        cta = page.get("cta", "Get Started")
        page_name = page.get("page", "home")
        canonical_url = self._build_canonical_url(site, page_name)
        description = self._build_meta_description(tagline, page_name, goal, key_points, site)
        og_image = self._build_og_image(site)
        structured_data = self._build_structured_data(site, canonical_url, template_type, key_points)

        bullets = "\n".join([f"<li>{point}</li>" for point in key_points])
        product_assets_html = ""
        if template_type.lower() == "shop":
            product_assets_html = self._render_shop_assets_html(site)
        return (
            "<!doctype html>\n"
            "<html lang=\"en\">\n"
            "<head>\n"
            "  <meta charset=\"utf-8\" />\n"
            "  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />\n"
            f"  <title>{title} - {page.get('page', '').title()}</title>\n"
            f"  <meta name=\"description\" content=\"{description}\" />\n"
            f"  <link rel=\"canonical\" href=\"{canonical_url}\" />\n"
            f"  <meta property=\"og:title\" content=\"{title}\" />\n"
            f"  <meta property=\"og:description\" content=\"{description}\" />\n"
            f"  <meta property=\"og:type\" content=\"website\" />\n"
            f"  <meta property=\"og:url\" content=\"{canonical_url}\" />\n"
            f"  <meta property=\"og:image\" content=\"{og_image}\" />\n"
            f"  <meta name=\"twitter:card\" content=\"summary_large_image\" />\n"
            f"  <meta name=\"twitter:title\" content=\"{title}\" />\n"
            f"  <meta name=\"twitter:description\" content=\"{description}\" />\n"
            f"  <meta name=\"twitter:image\" content=\"{og_image}\" />\n"
            "  <style>\n"
            f"{css}\n"
            "  body { margin: 0; padding: 0; }\n"
            "  .alwrity-theme { min-height: 100vh; padding: 48px; }\n"
            "  .alwrity-card { padding: 24px; margin-top: 24px; }\n"
            "  </style>\n"
            f"  <script type=\"application/ld+json\">{structured_data}</script>\n"
            "</head>\n"
            "<body>\n"
            "  <main class=\"alwrity-theme\">\n"
            f"    <h1>{title}</h1>\n"
            f"    <p>{tagline}</p>\n"
            f"    <div class=\"alwrity-card\">\n"
            f"      <h2>{page.get('page', '').title()}</h2>\n"
            f"      <p>{goal}</p>\n"
            "      <ul>\n"
            f"{bullets}\n"
            "      </ul>\n"
            f"{product_assets_html}\n"
            f"      <button class=\"alwrity-button\">{cta}</button>\n"
            "    </div>\n"
            "  </main>\n"
            "</body>\n"
            "</html>\n"
        )

    def _render_shop_assets_html(self, site: Dict[str, Any]) -> str:
        product_assets = site.get("product_assets", {}) if isinstance(site, dict) else {}
        urls = product_assets.get("urls") or []
        asset_ids = product_assets.get("asset_ids") or []
        if not urls and not asset_ids:
            return ""

        asset_items = []
        for url in urls:
            asset_items.append(f"<li><a href=\"{url}\" target=\"_blank\" rel=\"noreferrer\">{url}</a></li>")
        for asset_id in asset_ids:
            asset_items.append(f"<li>Asset ID: {asset_id}</li>")
        assets_list = "\n".join(asset_items)
        return (
            "<h3>Product Assets</h3>\n"
            "<ul>\n"
            f"{assets_list}\n"
            "</ul>\n"
        )

    def _build_canonical_url(self, site: Dict[str, Any], page_name: str) -> str:
        canonical_base = site.get("canonical_url")
        if canonical_base:
            base_url = canonical_base.rstrip("/")
        else:
            business_name = site.get("business_name") or "alwrity-site"
            slug = business_name.lower().replace(" ", "-")
            base_url = f"https://{slug}.netlify.app"
        if page_name == "home":
            return base_url
        return f"{base_url}/{page_name}"

    def _build_meta_description(
        self,
        tagline: str,
        page_name: str,
        goal: str,
        key_points: List[str],
        site: Dict[str, Any],
    ) -> str:
        offerings = site.get("primary_offerings") or []
        offerings_text = ", ".join(offerings[:3]) if isinstance(offerings, list) else ""
        page_label = page_name.replace("_", " ").title()
        parts = [
            f"{page_label} - {tagline}" if tagline else page_label,
            goal,
            offerings_text,
            ", ".join(key_points[:3]),
        ]
        description = " ".join([part for part in parts if part])
        return description[:160] if description else "AI-generated website preview."

    def _build_og_image(self, site: Dict[str, Any]) -> str:
        product_assets = site.get("product_assets", {}) if isinstance(site, dict) else {}
        urls = product_assets.get("urls") or []
        if urls:
            return urls[0]
        return "https://alwrity.com/og-default.png"

    def _build_structured_data(
        self,
        site: Dict[str, Any],
        canonical_url: str,
        template_type: str,
        key_points: List[str],
    ) -> str:
        business_name = site.get("business_name") or "ALwrity Instant Site"
        if template_type.lower() == "shop":
            product_assets = site.get("product_assets", {}) if isinstance(site, dict) else {}
            urls = product_assets.get("urls") or []
            items = []
            for idx, url in enumerate(urls, start=1):
                items.append(
                    "{"
                    f"\"@type\":\"ListItem\","
                    f"\"position\":{idx},"
                    "\"item\":{"
                    f"\"@type\":\"Product\","
                    f"\"name\":\"{business_name} Product {idx}\","
                    f"\"image\":\"{url}\","
                    f"\"url\":\"{canonical_url}\""
                    "}"
                    "}"
                )
            return (
                "{"
                "\"@context\":\"https://schema.org\","
                "\"@type\":\"ItemList\","
                f"\"name\":\"{business_name} Products\","
                f"\"url\":\"{canonical_url}\","
                f"\"itemListElement\":[{','.join(items)}]"
                "}"
            )
        return (
            "{"
            f"\"@context\":\"https://schema.org\","
            f"\"@type\":\"Organization\","
            f"\"name\":\"{business_name}\","
            f"\"url\":\"{canonical_url}\""
            "}"
        )


website_automation_service = WebsiteAutomationService()
