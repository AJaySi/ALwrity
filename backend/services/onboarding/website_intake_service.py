"""
Website Intake Service
Normalizes onboarding website intake payloads for site generation.
"""

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class SiteBrief(BaseModel):
    """Schema for a site brief used in website automation."""

    title: Optional[str] = None
    page_images: Optional[Dict[str, str]] = None


class WebsiteIntake(BaseModel):
    """Schema for website intake collected during onboarding."""

    business_name: Optional[str] = None
    business_description: Optional[str] = None
    offerings: Optional[str] = None
    page_images: Optional[Dict[str, str]] = None
    site_brief: SiteBrief = Field(default_factory=SiteBrief)


def build_site_brief_from_intake(intake: Dict[str, Any]) -> Dict[str, Any]:
    """Construct a site brief from intake data, including page images."""
    site_brief: Dict[str, Any] = dict(intake.get("site_brief") or {})
    page_images = intake.get("page_images") or site_brief.get("page_images")
    if page_images:
        site_brief["page_images"] = page_images
    return site_brief
