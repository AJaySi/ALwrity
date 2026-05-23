"""Backlink outreach persistence service (campaign-creator style)."""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4
from typing import List, Optional
from sqlalchemy import text as sql_text

from services.database import get_session_for_user
from models.backlink_outreach_models import Base, BacklinkCampaign, BacklinkLead


class BacklinkOutreachStorageService:
    _NEW_LEAD_COLUMNS = [
        "url", "page_title", "snippet", "confidence_score", "discovery_source", "notes"
    ]

    def _ensure_tables(self, user_id: str) -> None:
        db = get_session_for_user(user_id)
        if not db:
            return
        try:
            Base.metadata.create_all(bind=db.get_bind(), checkfirst=True)
            self._migrate_lead_columns(db)
        finally:
            db.close()

    def _migrate_lead_columns(self, db) -> None:
        """Add new columns to backlink_leads if they don't exist (dev migration)."""
        try:
            for col in self._NEW_LEAD_COLUMNS:
                db.execute(sql_text(
                    f"ALTER TABLE backlink_leads ADD COLUMN IF NOT EXISTS {col} TEXT"
                ))
            # confidence_score is Float, add separately
            db.execute(sql_text(
                "ALTER TABLE backlink_leads ADD COLUMN IF NOT EXISTS confidence_score FLOAT DEFAULT 0.0"
            ))
            db.commit()
        except Exception:
            db.rollback()

    def create_campaign(self, user_id: str, workspace_id: str, name: str) -> dict:
        self._ensure_tables(user_id)
        db = get_session_for_user(user_id)
        if not db:
            raise RuntimeError("Database session unavailable")
        try:
            campaign = BacklinkCampaign(
                id=f"bl_{uuid4().hex[:16]}",
                user_id=user_id,
                workspace_id=workspace_id,
                name=name,
                status="drafted",
                created_at=datetime.utcnow(),
            )
            db.add(campaign)
            db.commit()
            return {"campaign_id": campaign.id, "name": campaign.name, "status": campaign.status}
        finally:
            db.close()

    def list_campaigns(self, user_id: str, workspace_id: str, limit: int = 50) -> List[dict]:
        self._ensure_tables(user_id)
        db = get_session_for_user(user_id)
        if not db:
            return []
        try:
            rows = (
                db.query(BacklinkCampaign)
                .filter(BacklinkCampaign.user_id == user_id, BacklinkCampaign.workspace_id == workspace_id)
                .order_by(BacklinkCampaign.created_at.desc())
                .limit(limit)
                .all()
            )
            return [{"campaign_id": r.id, "name": r.name, "status": r.status, "created_at": r.created_at.isoformat()} for r in rows]
        finally:
            db.close()

    def get_campaign(self, campaign_id: str, user_id: str) -> Optional[dict]:
        self._ensure_tables(user_id)
        db = get_session_for_user(user_id)
        if not db:
            return None
        try:
            campaign = (
                db.query(BacklinkCampaign)
                .filter(BacklinkCampaign.id == campaign_id, BacklinkCampaign.user_id == user_id)
                .first()
            )
            if not campaign:
                return None
            lead_count = db.query(BacklinkLead).filter(BacklinkLead.campaign_id == campaign_id).count()
            leads = (
                db.query(BacklinkLead)
                .filter(BacklinkLead.campaign_id == campaign_id)
                .order_by(BacklinkLead.created_at.desc())
                .limit(50)
                .all()
            )
            return {
                "campaign_id": campaign.id,
                "name": campaign.name,
                "status": campaign.status,
                "created_at": campaign.created_at.isoformat() if campaign.created_at else None,
                "lead_count": lead_count,
                "leads": [self._lead_to_dict(l) for l in leads],
            }
        finally:
            db.close()

    # -- Lead CRUD --

    def add_lead(
        self,
        campaign_id: str,
        user_id: str,
        url: str,
        domain: str,
        page_title: str = "",
        snippet: str = "",
        email: Optional[str] = None,
        confidence_score: float = 0.0,
        discovery_source: str = "duckduckgo",
        notes: Optional[str] = None,
    ) -> dict:
        self._ensure_tables(user_id)
        db = get_session_for_user(user_id)
        if not db:
            raise RuntimeError("Database session unavailable")
        try:
            lead = BacklinkLead(
                id=f"bl_{uuid4().hex[:16]}",
                campaign_id=campaign_id,
                url=url,
                domain=domain,
                page_title=page_title,
                snippet=snippet,
                email=email,
                confidence_score=confidence_score,
                discovery_source=discovery_source,
                status="discovered",
                notes=notes,
                created_at=datetime.utcnow(),
            )
            db.add(lead)
            db.commit()
            return self._lead_to_dict(lead)
        finally:
            db.close()

    def bulk_add_leads(self, campaign_id: str, user_id: str, leads_data: List[dict]) -> List[dict]:
        self._ensure_tables(user_id)
        db = get_session_for_user(user_id)
        if not db:
            raise RuntimeError("Database session unavailable")
        try:
            added = []
            for data in leads_data:
                lead = BacklinkLead(
                    id=f"bl_{uuid4().hex[:16]}",
                    campaign_id=campaign_id,
                    url=data.get("url", ""),
                    domain=data.get("domain", ""),
                    page_title=data.get("page_title", ""),
                    snippet=data.get("snippet", ""),
                    email=data.get("email"),
                    confidence_score=data.get("confidence_score", 0.0),
                    discovery_source=data.get("discovery_source", "duckduckgo"),
                    status="discovered",
                    notes=data.get("notes"),
                    created_at=datetime.utcnow(),
                )
                db.add(lead)
                added.append(lead)
            db.commit()
            return [self._lead_to_dict(l) for l in added]
        finally:
            db.close()

    def list_leads(
        self, campaign_id: str, user_id: str, status: Optional[str] = None, limit: int = 50
    ) -> List[dict]:
        self._ensure_tables(user_id)
        db = get_session_for_user(user_id)
        if not db:
            return []
        try:
            q = db.query(BacklinkLead).filter(BacklinkLead.campaign_id == campaign_id)
            if status:
                q = q.filter(BacklinkLead.status == status)
            rows = q.order_by(BacklinkLead.created_at.desc()).limit(limit).all()
            return [self._lead_to_dict(r) for r in rows]
        finally:
            db.close()

    def update_lead_status(
        self, lead_id: str, user_id: str, status: str, notes: Optional[str] = None
    ) -> Optional[dict]:
        db = get_session_for_user(user_id)
        if not db:
            return None
        try:
            lead = db.query(BacklinkLead).filter(BacklinkLead.id == lead_id).first()
            if not lead:
                return None
            lead.status = status
            if notes is not None:
                lead.notes = notes
            db.commit()
            return self._lead_to_dict(lead)
        finally:
            db.close()

    @staticmethod
    def _lead_to_dict(lead) -> dict:
        return {
            "lead_id": lead.id,
            "campaign_id": lead.campaign_id,
            "url": lead.url,
            "domain": lead.domain,
            "page_title": lead.page_title or "",
            "snippet": lead.snippet or "",
            "email": lead.email,
            "confidence_score": lead.confidence_score or 0.0,
            "discovery_source": lead.discovery_source or "duckduckgo",
            "status": lead.status,
            "notes": lead.notes,
            "created_at": lead.created_at.isoformat() if lead.created_at else None,
        }
