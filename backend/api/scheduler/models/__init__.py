"""Scheduler API Models Package"""

# Import all models for easy access
from .dashboard import *
from .monitoring import *
from .oauth import *
from .platform_insights import *
from .website_analysis import *
from .shared import *

__all__ = [
    # Dashboard models
    "SchedulerStats", "SchedulerDashboardResponse", "JobInfo", "UserIsolationInfo",

    # Monitoring models
    "ExecutionLogEntry", "ExecutionLogsResponse", "EventLogEntry", "EventHistoryResponse",
    "EventLogStats", "EventLogCleanupRequest", "EventLogCleanupResponse",

    # Task management models
    "TaskInterventionInfo", "ManualTriggerRequest", "ManualTriggerResponse",
    "TaskRetryRequest", "TaskRetryResponse",

    # Platform insights models
    "PlatformInsightsStatus", "PlatformInsightsStatusResponse",

    # Website analysis models
    "WebsiteAnalysisStatus", "WebsiteAnalysisStatusResponse", "WebsiteAnalysisLogEntry",

    # Shared models
    "PaginationInfo", "TaskStatus", "TaskType"
]