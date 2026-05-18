"""Models for autonomous social/goal execution tracking."""

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, JSON, String, Text
from sqlalchemy.orm import relationship

from models.enhanced_strategy_models import Base


class GoalInstance(Base):
    """A persisted goal configuration and execution state for a user."""

    __tablename__ = "goal_instances"
    __table_args__ = (
        Index("ix_goal_instances_user_id", "user_id"),
        Index("ix_goal_instances_status", "status"),
        Index("ix_goal_instances_next_wakeup_at", "next_wakeup_at"),
    )

    id = Column(Integer, primary_key=True)
    user_id = Column(String(255), nullable=False)
    goal_type = Column(String(100), nullable=False)
    objective_json = Column(JSON, nullable=False)
    cadence_json = Column(JSON, nullable=False)
    status = Column(String(50), nullable=False, default="active")

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    next_wakeup_at = Column(DateTime, nullable=True)
    last_error = Column(Text, nullable=True)

    checkpoints = relationship(
        "GoalCheckpoint",
        back_populates="goal_instance",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    action_logs = relationship(
        "GoalActionLog",
        back_populates="goal_instance",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class GoalCheckpoint(Base):
    """Checkpoint schedule and execution metadata for a goal instance."""

    __tablename__ = "goal_checkpoints"

    id = Column(Integer, primary_key=True)
    goal_instance_id = Column(
        Integer,
        ForeignKey("goal_instances.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    checkpoint_key = Column(String(30), nullable=False)
    scheduled_for = Column(DateTime, nullable=False)
    executed_at = Column(DateTime, nullable=True)
    status = Column(String(50), nullable=False, default="scheduled", index=True)
    result_summary = Column(Text, nullable=True)
    metrics_snapshot_json = Column(JSON, nullable=True)

    goal_instance = relationship("GoalInstance", back_populates="checkpoints")


class GoalActionLog(Base):
    """Audit records for autonomous actions, edits, and escalations."""

    __tablename__ = "goal_action_logs"

    id = Column(Integer, primary_key=True)
    goal_instance_id = Column(
        Integer,
        ForeignKey("goal_instances.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    action_type = Column(String(100), nullable=False)
    actor = Column(String(100), nullable=True)
    status = Column(String(50), nullable=False, default="success", index=True)
    summary = Column(Text, nullable=True)
    payload_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    goal_instance = relationship("GoalInstance", back_populates="action_logs")
