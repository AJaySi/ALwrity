import os
import httpx
from github import Github, GithubException, Auth
from loguru import logger
from fastapi import HTTPException
from typing import Optional, Dict, Any, List

TEMPLATE_REPOS = {
    "blog": "alwrity/hugo-template-blog",
    "profile": "alwrity/hugo-template-profile",
    "shop": "alwrity/hugo-template-shop"
}


class WebsiteAutomationService:
    """
    Orchestrates creation of a GitHub repository and Netlify site
    to provide a black-box website generation experience.
    """

    def __init__(self):
        self.github_token = os.getenv("GITHUB_ACCESS_TOKEN")
        self.netlify_token = os.getenv("NETLIFY_ACCESS_TOKEN")
        self.netlify_account_slug = os.getenv("NETLIFY_ACCOUNT_SLUG")

        if not self.github_token or not self.netlify_token:
            logger.warning("⚠️ GitHub or Netlify tokens missing. Website automation will fail.")

    async def generate_website(
        self,
        user_id: str,
        business_info: Dict[str, Any],
        niche: str,
        site_brief: Optional[Dict[str, Any]] = None,
        css: Optional[str] = None
    ) -> Dict[str, str]:
        logger.info(f"🚀 Starting website generation for user {user_id} (Niche: {niche})")

        repo_name = self._sanitize_repo_name(business_info.get("name", f"alwrity-site-{user_id}"))
        template_repo = TEMPLATE_REPOS.get(niche.lower(), TEMPLATE_REPOS["blog"])

        try:
            repo_url, full_repo_name = self._create_github_repo(repo_name, template_repo, user_id)
            await self._push_initial_content(
                full_repo_name,
                business_info,
                site_brief=site_brief,
                css=css,
                template_type=niche
            )
            site_url, admin_url = await self._deploy_to_netlify(full_repo_name, repo_name)

            return {
                "status": "success",
                "live_url": site_url,
                "admin_url": admin_url,
                "repo_url": repo_url
            }

        except Exception as e:
            logger.error(f"❌ Website generation failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Website generation failed: {str(e)}")

    def _create_github_repo(self, repo_name: str, template_repo_name: str, user_id: str):
        try:
            auth = Auth.Token(self.github_token)
            g = Github(auth=auth)
            user = g.get_user()

            try:
                user.get_repo(repo_name)
                repo_name = f"{repo_name}-{user_id[:4]}"
            except Exception:
                pass

            logger.info(f"Creating GitHub Repo: {repo_name} from {template_repo_name}")

            template = g.get_repo(template_repo_name)
            new_repo = user.create_repo_from_template(
                name=repo_name,
                repo=template,
                description=f"AI Generated Website for {repo_name} by ALwrity",
                private=False
            )

            return new_repo.html_url, new_repo.full_name

        except GithubException as e:
            logger.error(f"GitHub API Error: {e}")
            raise Exception(f"Failed to create GitHub repository: {e.data.get('message', str(e))}")

    async def _push_initial_content(
        self,
        full_repo_name: str,
        business_info: Dict[str, Any],
        site_brief: Optional[Dict[str, Any]] = None,
        css: Optional[str] = None,
        template_type: str = "blog"
    ):
        try:
            auth = Auth.Token(self.github_token)
            g = Github(auth=auth)
            repo = g.get_repo(full_repo_name)

            site_name = business_info.get("name") or "ALwrity Instant Site"
            new_config_content = (
                "baseURL = 'https://{site}.netlify.app'\n"
                "languageCode = 'en-us'\n"
                "title = '{site}'\n"
                "theme = 'PaperMod'\n"
                "enableRobotsTXT = true\n"
                "[params]\n"
                "  customCSS = [\"custom.css\"]\n"
                "  description = 'AI-generated website preview'\n"
                "  defaultTheme = 'light'\n"
                "  showReadingTime = false\n"
                "  showShareButtons = true\n"
                "  showPostNavLinks = true\n"
                "  showBreadCrumbs = true\n"
                "  showCodeCopyButtons = true\n"
                "  disableSpecial1stPost = true\n"
                "  hideMeta = false\n"
                "  env = 'production'\n"
                "  canonicalURL = 'https://{site}.netlify.app'\n"
                "[params.assets]\n"
                "  favicon = '/favicon.ico'\n"
                "[params.label]\n"
                "  text = '{site}'\n"
                "[params.social]\n"
                "  twitter = ''\n"
                "  facebook = ''\n"
                "[sitemap]\n"
                "  changefreq = 'weekly'\n"
                "  priority = 0.5\n"
                "  filename = 'sitemap.xml'\n"
            ).format(site=site_name)
            try:
                contents = repo.get_contents("config.toml")
                repo.update_file(contents.path, "ALwrity AI: Update Config", new_config_content, contents.sha)
            except Exception:
                repo.create_file("config.toml", "ALwrity AI: Init Config", new_config_content)

            if site_brief:
                pages = self._extract_pages(site_brief)
                for page in pages:
                    page_name = page.get("page", "home")
                    markdown = self._render_markdown_page(site_brief, page, template_type)
                    path = "content/_index.md" if page_name == "home" else f"content/{page_name}.md"
                    self._upsert_repo_file(repo, path, f"ALwrity AI: Update {page_name} content", markdown)

            if css:
                self._upsert_repo_file(
                    repo,
                    "static/custom.css",
                    "ALwrity AI: Add custom theme styles",
                    css
                )

            logger.info(f"✅ Pushed initial content to {full_repo_name}")

        except Exception as e:
            logger.error(f"Failed to push content: {e}")

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

    def _render_markdown_page(self, site_brief: Dict[str, Any], page: Dict[str, Any], template_type: str) -> str:
        site = site_brief.get("site_brief", {})
        title = site.get("business_name") or "ALwrity Instant Site"
        tagline = site.get("tagline") or "AI-generated website"
        page_title = page.get("page", "Page").title()
        goal = page.get("goal", "")
        key_points = page.get("key_points", []) or []
        cta = page.get("cta", "Get Started")

        bullet_lines = "\n".join([f"- {point}" for point in key_points])
        base_content = (
            f"# {title}\n\n"
            f"_{tagline}_\n\n"
            f"## {page_title}\n\n"
            f"{goal}\n\n"
            f"{bullet_lines}\n\n"
            f"**Next step:** {cta}\n"
        )

        if template_type.lower() == "shop":
            product_assets = site.get("product_assets", {}) if isinstance(site, dict) else {}
            return self._render_shop_page(page_title, base_content, key_points, product_assets)
        if template_type.lower() == "profile":
            return self._render_profile_page(page_title, base_content, key_points)
        return self._render_blog_page(page_title, base_content, key_points)

    def _render_blog_page(self, page_title: str, base_content: str, key_points: List[str]) -> str:
        highlights = "\n".join([f"- {point}" for point in key_points[:5]])
        return (
            f"---\n"
            f"title: \"{page_title}\"\n"
            f"layout: \"post\"\n"
            f"---\n\n"
            f"{base_content}\n\n"
            f"## Highlights\n\n"
            f"{highlights}\n"
        )

    def _render_profile_page(self, page_title: str, base_content: str, key_points: List[str]) -> str:
        services = "\n".join([f"- {point}" for point in key_points[:6]])
        return (
            f"---\n"
            f"title: \"{page_title}\"\n"
            f"---\n\n"
            f"{base_content}\n\n"
            f"## Services\n\n"
            f"{services}\n"
        )

    def _render_shop_page(
        self,
        page_title: str,
        base_content: str,
        key_points: List[str],
        product_assets: Optional[Dict[str, Any]] = None,
    ) -> str:
        products = "\n".join([f"- {point} — starting price TBD" for point in key_points[:6]])
        product_assets = product_assets or {}
        asset_urls = product_assets.get("urls") or []
        asset_ids = product_assets.get("asset_ids") or []
        asset_lines = []
        for idx, url in enumerate(asset_urls, start=1):
            asset_lines.append(f"- [Product image {idx}]({url})")
        for asset_id in asset_ids:
            asset_lines.append(f"- Asset ID: {asset_id}")
        assets_section = ""
        if asset_lines:
            assets_section = "\n\n## Product Assets\n\n" + "\n".join(asset_lines) + "\n"
        return (
            f"---\n"
            f"title: \"{page_title}\"\n"
            f"---\n\n"
            f"{base_content}\n\n"
            f"## Featured Products\n\n"
            f"{products}\n"
            f"{assets_section}"
        )

    def _upsert_repo_file(self, repo, path: str, message: str, content: str) -> None:
        try:
            existing = repo.get_contents(path)
            repo.update_file(existing.path, message, content, existing.sha)
        except Exception:
            repo.create_file(path, message, content)

    async def _deploy_to_netlify(self, full_repo_name: str, site_name: str):
        url = "https://api.netlify.com/api/v1/sites"
        headers = {
            "Authorization": f"Bearer {self.netlify_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "name": self._sanitize_site_name(site_name),
            "repo": {
                "provider": "github",
                "repo": full_repo_name,
                "private": False,
                "branch": "main",
                "cmd": "hugo --gc --minify",
                "dir": "public"
            }
        }

        if self.netlify_account_slug:
            payload["account_slug"] = self.netlify_account_slug

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)

            if response.status_code == 422:
                del payload["name"]
                response = await client.post(url, json=payload, headers=headers)

            if response.status_code not in [200, 201]:
                logger.error(f"Netlify API Error: {response.text}")
                raise Exception(f"Netlify Deployment Failed: {response.text}")

            data = response.json()
            return data.get("ssl_url") or data.get("url"), data.get("admin_url")

    def _sanitize_repo_name(self, name: str) -> str:
        return "".join(c if c.isalnum() else "-" for c in name).lower().strip("-")

    def _sanitize_site_name(self, name: str) -> str:
        base = self._sanitize_repo_name(name)
        return f"{base}-alwrity"
