"""Backlink outreach persistence service (campaign-creator style)."""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4
from typing import List

from services.database import get_session_for_user
from models.backlink_outreach_models import Base, BacklinkCampaign


class BacklinkOutreachStorageService:
    def _ensure_tables(self, user_id: str) -> None:
        db = get_session_for_user(user_id)
        if not db:
            return
        try:
            Base.metadata.create_all(bind=db.get_bind(), checkfirst=True)
        finally:
            db.close()

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
