"""Website Automation Service for API layer - orchestrates website creation."""
from typing import Dict, Any, Optional
from loguru import logger
import os
import tempfile
import json
from fastapi import HTTPException

# Import the actual automation service
from services.onboarding.website_automation_service import WebsiteAutomationService as CoreAutomationService


class WebsiteAutomationService:
    """API layer service for website automation operations."""
    
    def __init__(self):
        logger.info("🔄 Initializing WebsiteAutomationService (API layer)...")
        self.core_service = CoreAutomationService()
    
    async def generate_preview_site(
        self, 
        user_id: str, 
        site_brief: Dict[str, Any], 
        css: str
    ) -> Dict[str, Any]:
        """Generate a preview site for the user."""
        try:
            logger.info(f"Generating preview site for user {user_id}")
            
            # For preview, we'll create a temporary HTML file
            # In production, this could be hosted on a preview server
            preview_html = self._generate_preview_html(site_brief, css)
            
            # Save to temporary file (in production, use proper hosting)
            preview_url = f"/preview/{user_id}/index.html"
            
            return {
                "preview_url": preview_url,
                "preview_root": f"/preview/{user_id}",
                "preview_files": ["index.html", "custom.css"],
                "preview_html": preview_html
            }
            
        except Exception as e:
            logger.error(f"Failed to generate preview site: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Preview generation failed: {str(e)}")
    
    def _generate_preview_html(self, site_brief: Dict[str, Any], css: str) -> str:
        """Generate HTML preview from site brief and CSS."""
        try:
            site_data = site_brief.get("site_brief", {})
            business_name = site_data.get("business_name", "Your Business")
            tagline = site_data.get("tagline", "Your tagline here")
            
            # Get content plan
            content_plan = site_brief.get("content_plan", {})
            required_pages = content_plan.get("required_pages", [])
            
            # Generate HTML
            html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{business_name}</title>
    <style>
        {css}
        
        /* Additional preview styles */
        .preview-banner {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            text-align: center;
            margin-bottom: 2rem;
        }}
        .preview-banner h1 {{
            margin: 0;
            font-size: 2.5rem;
        }}
        .preview-banner p {{
            margin: 0.5rem 0 0 0;
            font-size: 1.2rem;
            opacity: 0.9;
        }}
        .preview-content {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 2rem;
        }}
        .preview-section {{
            margin-bottom: 3rem;
        }}
        .preview-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            margin-bottom: 2rem;
        }}
        .preview-card {{
            background: var(--color-surface, #f8fafc);
            padding: 1.5rem;
            border-radius: var(--border-radius-medium, 0.5rem);
            box-shadow: var(--shadow-small, 0 1px 2px 0 rgb(0 0 0 / 0.05));
        }}
        .preview-watermark {{
            position: fixed;
            bottom: 1rem;
            right: 1rem;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 0.25rem;
            font-size: 0.875rem;
            z-index: 1000;
        }}
    </style>
</head>
<body>
    <div class="preview-banner">
        <h1>{business_name}</h1>
        <p>{tagline}</p>
        <div class="preview-watermark">ALwrity Preview</div>
    </div>
    
    <div class="preview-content">
        {self._generate_page_content(required_pages)}
    </div>
    
    <script>
        // Basic interactions for preview
        document.addEventListener('DOMContentLoaded', function() {{
            console.log('ALwrity website preview loaded');
        }});
    </script>
</body>
</html>"""
            
            return html
            
        except Exception as e:
            logger.error(f"Failed to generate preview HTML: {str(e)}")
            return f"<html><body><h1>Preview Error</h1><p>{str(e)}</p></body></html>"
    
    def _generate_page_content(self, required_pages: list) -> str:
        """Generate HTML content for pages."""
        if not required_pages:
            return """
            <div class="preview-section">
                <h2>Welcome to Your Website</h2>
                <p>This is a preview of your new website. The content will be generated based on your business information.</p>
                <div class="preview-grid">
                    <div class="preview-card">
                        <h3>About Us</h3>
                        <p>Learn more about your business and what makes you unique.</p>
                    </div>
                    <div class="preview-card">
                        <h3>Services</h3>
                        <p>Discover the services and products you offer to your customers.</p>
                    </div>
                    <div class="preview-card">
                        <h3>Contact</h3>
                        <p>Get in touch with you through various contact methods.</p>
                    </div>
                </div>
            </div>
            """
        
        content_parts = []
        
        for page in required_pages:
            page_name = page.get("page", "page").title()
            goal = page.get("goal", "")
            key_points = page.get("key_points", [])
            cta = page.get("cta", "Get Started")
            
            page_html = f"""
            <div class="preview-section">
                <h2>{page_name}</h2>
                <p>{goal}</p>
            """
            
            if key_points:
                page_html += "<div class='preview-grid'>"
                for point in key_points:
                    page_html += f"""
                    <div class="preview-card">
                        <p>{point}</p>
                    </div>
                    """
                page_html += "</div>"
            
            if cta:
                page_html += f"""
                <div style="margin-top: 2rem;">
                    <button class="btn btn-primary">{cta}</button>
                </div>
                """
            
            page_html += "</div>"
            content_parts.append(page_html)
        
        return "".join(content_parts)
    
    async def generate_website(
        self,
        user_id: str,
        business_info: Dict[str, Any],
        niche: str,
        site_brief: Optional[Dict[str, Any]] = None,
        css: Optional[str] = None
    ) -> Dict[str, str]:
        """Generate and deploy a full website."""
        try:
            logger.info(f"Generating website for user {user_id}")
            
            # Use the core automation service
            result = await self.core_service.generate_website(
                user_id=user_id,
                business_info=business_info,
                niche=niche,
                site_brief=site_brief,
                css=css
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to generate website: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Website generation failed: {str(e)}")
    
    def get_deployment_status(self, user_id: str) -> Dict[str, Any]:
        """Get the status of website deployment."""
        try:
            # This would typically check the deployment status
            # For now, return a placeholder
            return {
                "status": "pending",
                "message": "Deployment status checking not yet implemented"
            }
        except Exception as e:
            logger.error(f"Failed to get deployment status: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }


# Singleton instance
website_automation_service = WebsiteAutomationService()
