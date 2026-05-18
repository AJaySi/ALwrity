from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, ForeignKey, Index, Float, UniqueConstraint
from sqlalchemy.orm import relationship

from models.enhanced_strategy_models import Base


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    agent_type = Column(String(100), nullable=False, index=True)
    prompt = Column(Text, nullable=True)
    status = Column(String(30), nullable=False, default="running", index=True)
    success = Column(Boolean, nullable=True)
    error_message = Column(Text, nullable=True)
    result_summary = Column(Text, nullable=True)
    mlflow_run_id = Column(String(255), nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow, index=True)
    finished_at = Column(DateTime, nullable=True, index=True)

    events = relationship("AgentEvent", back_populates="run", cascade="all, delete-orphan")


class AgentEvent(Base):
    __tablename__ = "agent_events"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("agent_runs.id"), nullable=True, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    agent_type = Column(String(100), nullable=True, index=True)
    event_type = Column(String(50), nullable=False, index=True)
    severity = Column(String(20), nullable=False, default="info", index=True)
    message = Column(Text, nullable=True)
    payload = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    run = relationship("AgentRun", back_populates="events")


class AgentAlert(Base):
    __tablename__ = "agent_alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    source = Column(String(30), nullable=False, default="agents", index=True)
    alert_type = Column(String(50), nullable=False, index=True)
    severity = Column(String(20), nullable=False, default="info", index=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    cta_path = Column(String(255), nullable=True)
    payload = Column(JSON, nullable=True)
    dedupe_key = Column(String(255), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    read_at = Column(DateTime, nullable=True, index=True)


Index("ix_agent_alerts_user_unread", AgentAlert.user_id, AgentAlert.read_at)


class AgentApprovalRequest(Base):
    __tablename__ = "agent_approval_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    run_id = Column(Integer, ForeignKey("agent_runs.id"), nullable=True, index=True)
    agent_type = Column(String(100), nullable=True, index=True)
    action_id = Column(String(255), nullable=False, index=True)
    action_type = Column(String(255), nullable=False, index=True)
    target_resource = Column(String(255), nullable=True)
    risk_level = Column(Float, nullable=False, default=0.5)
    payload = Column(JSON, nullable=True)
    status = Column(String(30), nullable=False, default="pending", index=True)
    expires_at = Column(DateTime, nullable=True, index=True)
    decided_at = Column(DateTime, nullable=True, index=True)
    decision = Column(String(30), nullable=True)
    user_comments = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


Index("ix_agent_approval_user_status", AgentApprovalRequest.user_id, AgentApprovalRequest.status)


class AgentProfile(Base):
    __tablename__ = "agent_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    agent_key = Column(String(100), nullable=False, index=True)
    agent_type = Column(String(100), nullable=True, index=True)

    display_name = Column(String(255), nullable=True)
    enabled = Column(Boolean, nullable=False, default=True, index=True)

    schedule = Column(JSON, nullable=True)
    notification_prefs = Column(JSON, nullable=True)

    tone = Column(JSON, nullable=True)
    system_prompt = Column(Text, nullable=True)
    task_prompt_template = Column(Text, nullable=True)
    reporting_prefs = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, index=True)


Index("ix_agent_profiles_user_key", AgentProfile.user_id, AgentProfile.agent_key, unique=True)


class GoalInstance(Base):
    __tablename__ = "goal_instances"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    invocation_id = Column(String(255), nullable=False, index=True)
    status = Column(String(30), nullable=False, default="active", index=True)
    goal_input = Column(JSON, nullable=True)
    latest_output = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)
    completed_at = Column(DateTime, nullable=True, index=True)

    checkpoints = relationship("GoalCheckpoint", back_populates="goal_instance", cascade="all, delete-orphan")
    action_logs = relationship("GoalActionLog", back_populates="goal_instance", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("user_id", "invocation_id", name="uq_goal_instances_user_invocation"),
    )


class GoalCheckpoint(Base):
    __tablename__ = "goal_checkpoints"

    id = Column(Integer, primary_key=True, index=True)
    goal_instance_id = Column(Integer, ForeignKey("goal_instances.id"), nullable=False, index=True)
    checkpoint_key = Column(String(50), nullable=False, index=True)  # T+2h, T+24h, T+7d
    status = Column(String(30), nullable=False, default="pending", index=True)  # pending, running, completed, failed
    due_at = Column(DateTime, nullable=False, index=True)
    started_at = Column(DateTime, nullable=True, index=True)
    completed_at = Column(DateTime, nullable=True, index=True)
    payload = Column(JSON, nullable=True)
    output = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)

    goal_instance = relationship("GoalInstance", back_populates="checkpoints")

    __table_args__ = (
        UniqueConstraint("goal_instance_id", "checkpoint_key", name="uq_goal_checkpoint_instance_key"),
    )


class GoalActionLog(Base):
    __tablename__ = "goal_action_logs"

    id = Column(Integer, primary_key=True, index=True)
    goal_instance_id = Column(Integer, ForeignKey("goal_instances.id"), nullable=False, index=True)
    checkpoint_id = Column(Integer, ForeignKey("goal_checkpoints.id"), nullable=True, index=True)
    action = Column(String(100), nullable=False, index=True)
    status = Column(String(30), nullable=False, default="info", index=True)
    detail = Column(Text, nullable=True)
    payload = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    goal_instance = relationship("GoalInstance", back_populates="action_logs")
