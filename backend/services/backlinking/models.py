"""
Data models for the backlinking service.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Optional


@dataclass
class BacklinkOpportunity:
    """Represents a potential backlinking opportunity."""
    url: str
    title: str
    description: str
    contact_email: Optional[str] = None
    contact_name: Optional[str] = None
    domain_authority: Optional[int] = None
    content_topics: List[str] = None
    submission_guidelines: Optional[str] = None
    status: str = "discovered"  # discovered, contacted, responded, published


@dataclass
class BacklinkingCampaign:
    """Represents a backlinking campaign."""
    campaign_id: str
    user_id: int
    name: str
    keywords: List[str]
    status: str = "active"  # active, paused, completed
    created_at: datetime = None
    opportunities: List[BacklinkOpportunity] = None
    email_stats: Dict[str, int] = None