"""
Router Manager Module
Handles FastAPI router inclusion and management.
"""

from importlib import import_module
from typing import Any, Dict, List, Optional
import os

from fastapi import FastAPI
from loguru import logger


class RouterManager:
    """Manages FastAPI router inclusion and organization."""

    CORE_ROUTER_REGISTRY = [
        {"name": "component_logic", "module": "api.component_logic", "attr": "router", "profiles": {"all", "default"}},
        {"name": "subscription", "module": "api.subscription", "attr": "router", "profiles": {"all", "default", "podcast"}},
        {"name": "step3_research", "module": "api.onboarding_utils.step3_routes", "attr": "router", "profiles": {"all", "default"}},
        {"name": "step4_assets", "module": "api.onboarding_utils.step4_asset_routes", "attr": "router", "profiles": {"all", "default"}},
        {"name": "step4_persona", "module": "api.onboarding_utils.step4_persona_routes_optimized", "attr": "router", "profiles": {"all", "default"}},
        {"name": "gsc_auth", "module": "routers.gsc_auth", "attr": "router", "profiles": {"all", "default"}},
        {"name": "wordpress_oauth", "module": "routers.wordpress_oauth", "attr": "router", "profiles": {"all", "default"}},
        {"name": "bing_oauth", "module": "routers.bing_oauth", "attr": "router", "profiles": {"all", "default"}},
        {"name": "bing_analytics", "module": "routers.bing_analytics", "attr": "router", "profiles": {"all", "default"}},
        {"name": "bing_analytics_storage", "module": "routers.bing_analytics_storage", "attr": "router", "profiles": {"all", "default"}},
        {"name": "seo_tools", "module": "routers.seo_tools", "attr": "router", "profiles": {"all", "default"}},
        {"name": "facebook_writer", "module": "api.facebook_writer.routers", "attr": "facebook_router", "profiles": {"all", "default"}},
        {"name": "linkedin", "module": "routers.linkedin", "attr": "router", "profiles": {"all", "default"}},
        {"name": "linkedin_image", "module": "api.linkedin_image_generation", "attr": "router", "profiles": {"all", "default"}},
        {"name": "brainstorm", "module": "api.brainstorm", "attr": "router", "profiles": {"all", "default"}},
        {"name": "hallucination_detector", "module": "api.hallucination_detector", "attr": "router", "profiles": {"all", "default"}},
        {"name": "writing_assistant", "module": "api.writing_assistant", "attr": "router", "profiles": {"all", "default"}},
        {"name": "content_planning", "module": "api.content_planning.api.router", "attr": "router", "profiles": {"all", "default"}},
        {"name": "user_data", "module": "api.user_data", "attr": "router", "profiles": {"all", "default"}},
        {"name": "user_environment", "module": "api.user_environment", "attr": "router", "profiles": {"all", "default"}},
        {"name": "strategy_copilot", "module": "api.content_planning.strategy_copilot", "attr": "router", "profiles": {"all", "default"}},
        {"name": "error_logging", "module": "routers.error_logging", "attr": "router", "profiles": {"all", "default"}},
        {"name": "frontend_env_manager", "module": "routers.frontend_env_manager", "attr": "router", "profiles": {"all", "default"}},
        {"name": "platform_analytics", "module": "routers.platform_analytics", "attr": "router", "profiles": {"all", "default"}},
        {"name": "bing_insights", "module": "routers.bing_insights", "attr": "router", "profiles": {"all", "default"}},
        {"name": "background_jobs", "module": "routers.background_jobs", "attr": "router", "profiles": {"all", "default"}},
    ]

    OPTIONAL_ROUTER_REGISTRY = [
        {"name": "blog_writer", "module": "api.blog_writer.router", "attr": "router", "profiles": {"all", "default"}},
        {"name": "story_writer", "module": "api.story_writer.router", "attr": "router", "profiles": {"all", "default"}},
        {"name": "wix", "module": "api.wix_routes", "attr": "router", "profiles": {"all", "default"}},
        {"name": "blog_seo_analysis", "module": "api.blog_writer.seo_analysis", "attr": "router", "profiles": {"all", "default"}},
        {"name": "persona", "module": "api.persona_routes", "attr": "router", "profiles": {"all", "default"}},
        {"name": "video_studio", "module": "api.video_studio.router", "attr": "router", "profiles": {"all", "default"}},
        {"name": "stability", "module": "routers.stability", "attr": "router", "profiles": {"all", "default"}},
        {"name": "stability_advanced", "module": "routers.stability_advanced", "attr": "router", "profiles": {"all", "default"}},
        {"name": "stability_admin", "module": "routers.stability_admin", "attr": "router", "profiles": {"all", "default"}},
        {"name": "images", "module": "api.images", "attr": "router", "profiles": {"all", "default"}},
        {"name": "image_studio", "module": "routers.image_studio", "attr": "router", "profiles": {"all", "default"}},
        {"name": "product_marketing", "module": "routers.product_marketing", "attr": "router", "profiles": {"all", "default"}},
        {"name": "campaign_creator", "module": "routers.campaign_creator", "attr": "router", "profiles": {"all", "default"}},
        {"name": "content_assets", "module": "api.content_assets.router", "attr": "router", "profiles": {"all", "default"}},
        {"name": "podcast", "module": "api.podcast.router", "attr": "router", "profiles": {"all", "default", "podcast"}},
        {"name": "youtube", "module": "api.youtube.router", "attr": "router", "profiles": {"all", "default"}, "include_kwargs": {"prefix": "/api"}},
        {"name": "research_config", "module": "api.research_config", "attr": "router", "profiles": {"all", "default"}, "include_kwargs": {"prefix": "/api/research", "tags": ["research"]}},
        {"name": "research_engine", "module": "api.research.router", "attr": "router", "profiles": {"all", "default"}, "include_kwargs": {"tags": ["Research Engine"]}},
        {"name": "scheduler_dashboard", "module": "api.scheduler_dashboard", "attr": "router", "profiles": {"all", "default"}},
        {"name": "oauth_token_monitoring", "module": "api.oauth_token_monitoring_routes", "attr": "router", "profiles": {"all", "default"}},
        {"name": "agents", "module": "api.agents_api", "attr": "router", "profiles": {"all", "default"}},
        {"name": "today_workflow", "module": "api.today_workflow", "attr": "router", "profiles": {"all", "default"}},
    ]

    def __init__(self, app: FastAPI):
        self.app = app
        self.included_routers = []
        self.failed_routers = []

    def _is_verbose(self) -> bool:
        return os.getenv("ALWRITY_VERBOSE", "false").lower() == "true"

    def _get_profile(self) -> str:
        return os.getenv("ALWRITY_ROUTER_PROFILE", os.getenv("ALWRITY_PROFILE", "all")).strip().lower() or "all"

    def _should_include_router(self, registry_entry: Dict[str, Any], profile: str) -> bool:
        profiles = registry_entry.get("profiles", {"all", "default"})
        return profile in profiles or profile in {"all", "default"}

    def _load_router_from_registry(self, registry_entry: Dict[str, Any]):
        module = import_module(registry_entry["module"])
        return getattr(module, registry_entry["attr"])

    def include_router_safely(self, router, router_name: str = None, include_kwargs: Optional[Dict[str, Any]] = None) -> bool:
        """Include a router safely with error handling."""
        verbose = self._is_verbose()

        try:
            self.app.include_router(router, **(include_kwargs or {}))
            router_name = router_name or getattr(router, 'prefix', 'unknown')
            self.included_routers.append(router_name)
            if verbose:
                logger.info(f"✅ Router included successfully: {router_name}")
            return True
        except Exception as e:
            router_name = router_name or 'unknown'
            self.failed_routers.append({"name": router_name, "error": str(e)})
            if verbose:
                logger.warning(f"❌ Router inclusion failed: {router_name} - {e}")
            return False

    def _include_registry_group(self, registry: List[Dict[str, Any]], group_name: str) -> bool:
        verbose = self._is_verbose()
        profile = self._get_profile()

        try:
            if verbose:
                logger.info(f"Including {group_name} routers for profile '{profile}'...")

            for entry in registry:
                if not self._should_include_router(entry, profile):
                    continue

                try:
                    router = self._load_router_from_registry(entry)
                    self.include_router_safely(router, entry["name"], entry.get("include_kwargs"))
                except Exception as e:
                    logger.warning(f"{entry['name']} router not mounted: {e}")

            logger.info(f"✅ {group_name.capitalize()} routers processed for profile '{profile}'")
            return True
        except Exception as e:
            logger.error(f"❌ Error including {group_name} routers: {e}")
            return False

    def include_core_routers(self) -> bool:
        """Include core application routers."""
        return self._include_registry_group(self.CORE_ROUTER_REGISTRY, "core")

    def include_optional_routers(self) -> bool:
        """Include optional routers with error handling."""
        return self._include_registry_group(self.OPTIONAL_ROUTER_REGISTRY, "optional")

    def get_router_status(self) -> Dict[str, Any]:
        """Get the status of router inclusion."""
        return {
            "active_profile": self._get_profile(),
            "included_routers": self.included_routers,
            "failed_routers": self.failed_routers,
            "total_included": len(self.included_routers),
            "total_failed": len(self.failed_routers)
        }
