"""
Website Analysis Monitoring Models
Database models for tracking website analysis tasks and execution logs.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, Index, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

# Import the same Base from enhanced_strategy_models
from models.enhanced_strategy_models import Base


class WebsiteAnalysisTask(Base):
    """
    Model for storing website analysis monitoring tasks.
    
    Tracks per-user, per-URL website analysis with recurring checks.
    """
    __tablename__ = "website_analysis_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # User and URL Identification
    user_id = Column(String(255), nullable=False, index=True)  # Clerk user ID (string)
    website_url = Column(String(500), nullable=False)  # URL to analyze
    task_type = Column(String(50), nullable=False)  # 'user_website' or 'competitor'
    competitor_id = Column(String(255), nullable=True)  # For competitor tasks (domain or identifier)
    
    # Task Status
    status = Column(String(50), default='active')  # 'active', 'failed', 'paused', 'needs_intervention'
    
    # Execution Tracking
    last_check = Column(DateTime, nullable=True)
    last_success = Column(DateTime, nullable=True)
    last_failure = Column(DateTime, nullable=True)
    failure_reason = Column(Text, nullable=True)
    
    # Failure Pattern Tracking
    consecutive_failures = Column(Integer, default=0)  # Count of consecutive failures
    failure_pattern = Column(JSON, nullable=True)  # JSON storing failure analysis
    
    # Scheduling
    next_check = Column(DateTime, nullable=True, index=True)  # Next scheduled check time
    frequency_days = Column(Integer, default=10)  # Recurring frequency in days
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Execution Logs Relationship
    execution_logs = relationship(
        "WebsiteAnalysisExecutionLog",
        back_populates="task",
        cascade="all, delete-orphan"
    )
    
    # Indexes for efficient queries
    # Note: Index names match migration script to avoid conflicts
    __table_args__ = (
        Index('idx_website_analysis_tasks_user_url', 'user_id', 'website_url'),
        Index('idx_website_analysis_tasks_user_task_type', 'user_id', 'task_type'),
        Index('idx_website_analysis_tasks_next_check', 'next_check'),
        Index('idx_website_analysis_tasks_status', 'status'),
        Index('idx_website_analysis_tasks_task_type', 'task_type'),
    )
    
    def __repr__(self):
        return f"<WebsiteAnalysisTask(id={self.id}, user_id={self.user_id}, url={self.website_url}, type={self.task_type}, status={self.status})>"


class WebsiteAnalysisExecutionLog(Base):
    """
    Model for storing website analysis execution logs.
    
    Tracks individual execution attempts with results and error details.
    """
    __tablename__ = "website_analysis_execution_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Task Reference
    task_id = Column(Integer, ForeignKey("website_analysis_tasks.id"), nullable=False, index=True)
    
    # Execution Details
    execution_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    status = Column(String(50), nullable=False)  # 'success', 'failed', 'skipped', 'running'
    
    # Results
    result_data = Column(JSON, nullable=True)  # Analysis results (style_analysis, crawl_result, etc.)
    error_message = Column(Text, nullable=True)
    execution_time_ms = Column(Integer, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to task
    task = relationship("WebsiteAnalysisTask", back_populates="execution_logs")
    
    # Indexes for efficient queries
    # Note: Index names match migration script to avoid conflicts
    __table_args__ = (
        Index('idx_website_analysis_execution_logs_task_execution_date', 'task_id', 'execution_date'),
        Index('idx_website_analysis_execution_logs_status', 'status'),
    )
    
    def __repr__(self):
        return f"<WebsiteAnalysisExecutionLog(id={self.id}, task_id={self.task_id}, status={self.status}, execution_date={self.execution_date})>"

