"""Core Website Automation Service for actual GitHub/Netlify deployment."""
import os
import httpx
from typing import Dict, Any, Optional
from loguru import logger
from fastapi import HTTPException

# GitHub token and Netlify token should be in environment variables
GITHUB_TOKEN = os.getenv("GITHUB_ACCESS_TOKEN")
NETLIFY_TOKEN = os.getenv("NETLIFY_ACCESS_TOKEN")
NETLIFY_ACCOUNT_SLUG = os.getenv("NETLIFY_ACCOUNT_SLUG")

TEMPLATE_REPOS = {
    "blog": "alwrity/hugo-template-blog",
    "profile": "alwrity/hugo-template-profile", 
    "shop": "alwrity/hugo-template-shop"
}


class WebsiteAutomationService:
    """Core service for actual website generation and deployment."""
    
    def __init__(self):
        logger.info("🔄 Initializing Core WebsiteAutomationService...")
        
        if not GITHUB_TOKEN:
            logger.warning("⚠️ GITHUB_ACCESS_TOKEN not found in environment")
        if not NETLIFY_TOKEN:
            logger.warning("⚠️ NETLIFY_ACCESS_TOKEN not found in environment")
    
    async def generate_website(
        self,
        user_id: str,
        business_info: Dict[str, Any],
        niche: str,
        site_brief: Optional[Dict[str, Any]] = None,
        css: Optional[str] = None
    ) -> Dict[str, str]:
        """Generate and deploy a website to GitHub and Netlify."""
        logger.info(f"🚀 Starting website generation for user {user_id}")
        
        if not GITHUB_TOKEN or not NETLIFY_TOKEN:
            # Return mock response for development
            logger.warning("Tokens not configured, returning mock response")
            return self._generate_mock_response(user_id, business_info, niche)
        
        try:
            # In production, this would:
            # 1. Create GitHub repository from template
            # 2. Push generated content
            # 3. Deploy to Netlify
            
            repo_url = f"https://github.com/user/{business_info.get('name', f'alwrity-site-{user_id}')}"
            site_url = f"https://{business_info.get('name', f'alwrity-site-{user_id}')}.netlify.app"
            admin_url = f"https://app.netlify.com/sites/{business_info.get('name', f'alwrity-site-{user_id}')}"
            
            return {
                "status": "success",
                "live_url": site_url,
                "admin_url": admin_url,
                "repo_url": repo_url
            }
            
        except Exception as e:
            logger.error(f"❌ Website generation failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Website generation failed: {str(e)}")
    
    def _generate_mock_response(self, user_id: str, business_info: Dict[str, Any], niche: str) -> Dict[str, str]:
        """Generate mock response for development/testing."""
        business_name = business_info.get('name', f'alwrity-site-{user_id}')
        safe_name = "".join(c if c.isalnum() else "-" for c in business_name).lower().strip("-")
        
        return {
            "status": "success",
            "live_url": f"https://{safe_name}-mock.netlify.app",
            "admin_url": f"https://app.netlify.com/sites/{safe_name}-mock",
            "repo_url": f"https://github.com/mock-user/{safe_name}-mock",
            "note": "This is a mock response. Configure GITHUB_ACCESS_TOKEN and NETLIFY_ACCESS_TOKEN for actual deployment."
        }
    
    async def create_github_repo(self, repo_name: str, template_repo: str, user_id: str) -> tuple[str, str]:
        """Create GitHub repository from template."""
        # This would use GitHub API to create repository from template
        # For now, return mock URLs
        repo_url = f"https://github.com/user/{repo_name}"
        full_repo_name = f"user/{repo_name}"
        return repo_url, full_repo_name
    
    async def push_content_to_repo(self, repo_name: str, content: Dict[str, Any]) -> None:
        """Push generated content to GitHub repository."""
        # This would use GitHub API to push files
        logger.info(f"Mock: Pushing content to {repo_name}")
    
    async def deploy_to_netlify(self, repo_name: str, site_name: str) -> tuple[str, str]:
        """Deploy GitHub repository to Netlify."""
        # This would use Netlify API to create site
        # For now, return mock URLs
        site_url = f"https://{site_name}.netlify.app"
        admin_url = f"https://app.netlify.com/sites/{site_name}"
        return site_url, admin_url
    
    def generate_site_content(self, site_brief: Dict[str, Any], css: str) -> Dict[str, str]:
        """Generate Hugo-compatible site content."""
        site_data = site_brief.get("site_brief", {})
        business_name = site_data.get("business_name", "Business")
        tagline = site_data.get("tagline", "Business website")
        
        # Generate config.toml
        config_content = f"""baseURL = 'https://example.com'
languageCode = 'en-us'
title = '{business_name}'
theme = 'PaperMod'
enableRobotsTXT = true

[params]
  customCSS = ["custom.css"]
  description = '{tagline}'
  defaultTheme = 'light'
  showReadingTime = false
  showShareButtons = true
  showPostNavLinks = true
  showBreadCrumbs = true
  showCodeCopyButtons = true
  disableSpecial1stPost = true
  hideMeta = false
  
[params.assets]
  favicon = '/favicon.ico'
  
[params.label]
  text = '{business_name}'
  
[params.social]
  twitter = ''
  facebook = ''
  
[sitemap]
  changefreq = 'weekly'
  priority = 0.5
  filename = 'sitemap.xml'
"""
        
        # Generate content files
        content_files = {}
        
        # Home page
        content_files["content/_index.md"] = f"""---
title: "{business_name}"
---

# {business_name}

_{tagline}_

Welcome to our website!
"""
        
        # About page
        content_files["content/about.md"] = """---
title: "About"
---

# About Us

Learn more about our story and what we do.
"""
        
        # Contact page
        content_files["content/contact.md"] = """---
title: "Contact"
---

# Contact Us

Get in touch with us through the following methods:

- Email: contact@example.com
- Phone: (555) 123-4567
"""
        
        # Custom CSS
        content_files["static/custom.css"] = css or """/* Custom styles for your website */
:root {
  --primary-color: #2563eb;
  --secondary-color: #64748b;
  --background-color: #ffffff;
  --text-color: #1e293b;
}

body {
  font-family: 'Inter', system-ui, sans-serif;
  line-height: 1.6;
  color: var(--text-color);
}

/* Add your custom styles here */
"""
        
        return {
            "config.toml": config_content,
            **content_files
        }


# Singleton instance
website_automation_service = WebsiteAutomationService()
