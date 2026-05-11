"""DB models for production backlink outreach tracking."""

from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, Index, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class BacklinkCampaign(Base):
    __tablename__ = "backlink_campaigns"
    id = Column(String(64), primary_key=True)
    user_id = Column(String(255), nullable=False, index=True)
    workspace_id = Column(String(255), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    status = Column(String(32), nullable=False, default="drafted", index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class BacklinkLead(Base):
    __tablename__ = "backlink_leads"
    id = Column(String(64), primary_key=True)
    campaign_id = Column(String(64), ForeignKey("backlink_campaigns.id"), nullable=False, index=True)
    domain = Column(String(255), nullable=False, index=True)
    email = Column(String(255), nullable=True, index=True)
    status = Column(String(32), nullable=False, default="drafted", index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class OutreachAttempt(Base):
    __tablename__ = "backlink_outreach_attempts"
    id = Column(String(64), primary_key=True)
    lead_id = Column(String(64), ForeignKey("backlink_leads.id"), nullable=False, index=True)
    campaign_id = Column(String(64), ForeignKey("backlink_campaigns.id"), nullable=False, index=True)
    idempotency_key = Column(String(128), nullable=False, unique=True, index=True)
    status = Column(String(32), nullable=False, default="queued", index=True)
    decision_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class OutreachReply(Base):
    __tablename__ = "backlink_replies"
    id = Column(String(64), primary_key=True)
    attempt_id = Column(String(64), ForeignKey("backlink_outreach_attempts.id"), nullable=False, index=True)
    received_at = Column(DateTime, default=datetime.utcnow, index=True)
    classification = Column(String(32), nullable=False, default="replied")
    body = Column(Text, nullable=True)


class FollowUpSchedule(Base):
    __tablename__ = "backlink_followup_schedules"
    id = Column(String(64), primary_key=True)
    attempt_id = Column(String(64), ForeignKey("backlink_outreach_attempts.id"), nullable=False, index=True)
    scheduled_for = Column(DateTime, nullable=False, index=True)
    sent = Column(Boolean, default=False, index=True)


Index("idx_backlink_campaign_user_date", BacklinkCampaign.user_id, BacklinkCampaign.created_at)
Index("idx_backlink_attempt_campaign_date", OutreachAttempt.campaign_id, OutreachAttempt.created_at)
