"""
Router Manager Module
Handles FastAPI router inclusion and management.
"""

from fastapi import FastAPI
from loguru import logger
from typing import List, Dict, Any, Optional


class RouterManager:
    """Manages FastAPI router inclusion and organization."""
    
    def __init__(self, app: FastAPI):
        self.app = app
        self.included_routers = []
        self.failed_routers = []
    
    def include_router_safely(self, router, router_name: str = None) -> bool:
        """Include a router safely with error handling."""
        try:
            self.app.include_router(router)
            router_name = router_name or getattr(router, 'prefix', 'unknown')
            self.included_routers.append(router_name)
            logger.info(f"✅ Router included successfully: {router_name}")
            return True
        except Exception as e:
            router_name = router_name or 'unknown'
            self.failed_routers.append({"name": router_name, "error": str(e)})
            logger.warning(f"❌ Router inclusion failed: {router_name} - {e}")
            return False
    
    def include_core_routers(self) -> bool:
        """Include core application routers."""
        try:
            logger.info("Including core routers...")
            
            # Component logic router
            from api.component_logic import router as component_logic_router
            self.include_router_safely(component_logic_router, "component_logic")
            
            # Subscription router
            from api.subscription_api import router as subscription_router
            self.include_router_safely(subscription_router, "subscription")
            
            # Step 3 Research router (core onboarding functionality)
            from api.onboarding_utils.step3_routes import router as step3_research_router
            self.include_router_safely(step3_research_router, "step3_research")
            
            # GSC router
            from routers.gsc_auth import router as gsc_auth_router
            self.include_router_safely(gsc_auth_router, "gsc_auth")
            
            # WordPress router
            from routers.wordpress_oauth import router as wordpress_oauth_router
            self.include_router_safely(wordpress_oauth_router, "wordpress_oauth")
            
            # SEO tools router
            from routers.seo_tools import router as seo_tools_router
            self.include_router_safely(seo_tools_router, "seo_tools")
            
            # Facebook Writer router
            from api.facebook_writer.routers import facebook_router
            self.include_router_safely(facebook_router, "facebook_writer")
            
            # LinkedIn routers
            from routers.linkedin import router as linkedin_router
            self.include_router_safely(linkedin_router, "linkedin")
            
            from api.linkedin_image_generation import router as linkedin_image_router
            self.include_router_safely(linkedin_image_router, "linkedin_image")
            
            # Brainstorm router
            from api.brainstorm import router as brainstorm_router
            self.include_router_safely(brainstorm_router, "brainstorm")
            
            # Hallucination detector and writing assistant
            from api.hallucination_detector import router as hallucination_detector_router
            self.include_router_safely(hallucination_detector_router, "hallucination_detector")
            
            from api.writing_assistant import router as writing_assistant_router
            self.include_router_safely(writing_assistant_router, "writing_assistant")
            
            # Content planning and user data
            from api.content_planning.api.router import router as content_planning_router
            self.include_router_safely(content_planning_router, "content_planning")
            
            from api.user_data import router as user_data_router
            self.include_router_safely(user_data_router, "user_data")
            
            from api.user_environment import router as user_environment_router
            self.include_router_safely(user_environment_router, "user_environment")
            
            # Strategy copilot
            from api.content_planning.strategy_copilot import router as strategy_copilot_router
            self.include_router_safely(strategy_copilot_router, "strategy_copilot")
            
            # Error logging router
            from routers.error_logging import router as error_logging_router
            self.include_router_safely(error_logging_router, "error_logging")
            
            # Frontend environment manager router
            from routers.frontend_env_manager import router as frontend_env_router
            self.include_router_safely(frontend_env_router, "frontend_env_manager")
            
            logger.info("✅ Core routers included successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error including core routers: {e}")
            return False
    
    def include_optional_routers(self) -> bool:
        """Include optional routers with error handling."""
        try:
            logger.info("Including optional routers...")
            
            # AI Blog Writer router
            try:
                from api.blog_writer.router import router as blog_writer_router
                self.include_router_safely(blog_writer_router, "blog_writer")
            except Exception as e:
                logger.warning(f"AI Blog Writer router not mounted: {e}")
            
            # Wix Integration router
            try:
                from api.wix_routes import router as wix_router
                self.include_router_safely(wix_router, "wix")
            except Exception as e:
                logger.warning(f"Wix Integration router not mounted: {e}")
            
            # Blog Writer SEO Analysis router
            try:
                from api.blog_writer.seo_analysis import router as blog_seo_analysis_router
                self.include_router_safely(blog_seo_analysis_router, "blog_seo_analysis")
            except Exception as e:
                logger.warning(f"Blog Writer SEO Analysis router not mounted: {e}")
            
            # Persona router
            try:
                from api.persona_routes import router as persona_router
                self.include_router_safely(persona_router, "persona")
            except Exception as e:
                logger.warning(f"Persona router not mounted: {e}")
            
            # Stability AI routers
            try:
                from routers.stability import router as stability_router
                self.include_router_safely(stability_router, "stability")
                
                from routers.stability_advanced import router as stability_advanced_router
                self.include_router_safely(stability_advanced_router, "stability_advanced")
                
                from routers.stability_admin import router as stability_admin_router
                self.include_router_safely(stability_admin_router, "stability_admin")
            except Exception as e:
                logger.warning(f"Stability AI routers not mounted: {e}")
            
            
            logger.info("✅ Optional routers processed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error including optional routers: {e}")
            return False
    
    def get_router_status(self) -> Dict[str, Any]:
        """Get the status of router inclusion."""
        return {
            "included_routers": self.included_routers,
            "failed_routers": self.failed_routers,
            "total_included": len(self.included_routers),
            "total_failed": len(self.failed_routers)
        }
