"""
Progress tracking utilities for competitor analysis.
"""

import time
import asyncio
from typing import Dict, Any, Optional, Callable, List
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from loguru import logger


class ProgressStatus(Enum):
    """Analysis progress status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ProgressUpdate:
    """Progress update information."""
    analysis_id: str
    status: ProgressStatus
    current_step: int
    total_steps: int
    current_item: str
    message: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnalysisProgress:
    """Analysis progress tracker."""
    analysis_id: str
    total_items: int
    completed_items: int = 0
    failed_items: int = 0
    current_item: str = ""
    status: ProgressStatus = ProgressStatus.PENDING
    start_time: datetime = field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    updates: List[ProgressUpdate] = field(default_factory=list)
    callbacks: List[Callable[[ProgressUpdate], None]] = field(default_factory=list)
    
    @property
    def progress_percentage(self) -> float:
        """Calculate progress percentage."""
        if self.total_items == 0:
            return 0.0
        return (self.completed_items / self.total_items) * 100
    
    @property
    def elapsed_time(self) -> float:
        """Get elapsed time in seconds."""
        end = self.end_time or datetime.utcnow()
        return (end - self.start_time).total_seconds()
    
    @property
    def estimated_remaining_time(self) -> Optional[float]:
        """Estimate remaining time in seconds."""
        if self.completed_items == 0 or self.status != ProgressStatus.IN_PROGRESS:
            return None
        
        avg_time_per_item = self.elapsed_time / self.completed_items
        remaining_items = self.total_items - self.completed_items
        return avg_time_per_item * remaining_items


class ProgressTracker:
    """
    Progress tracking system for competitor analysis.
    
    Features:
    - Real-time progress updates
    - Multiple callback support
    - ETA calculation
    - Error tracking
    - Cancellation support
    """
    
    def __init__(self):
        self._active_analyses: Dict[str, AnalysisProgress] = {}
        self._completed_analyses: Dict[str, AnalysisProgress] = {}
        
        logger.info("✅ ProgressTracker initialized")
    
    def create_analysis(self, 
                       analysis_id: str, 
                       total_items: int,
                       callbacks: Optional[List[Callable[[ProgressUpdate], None]]] = None) -> AnalysisProgress:
        """
        Create a new analysis progress tracker.
        
        Args:
            analysis_id: Unique analysis identifier
            total_items: Total number of items to process
            callbacks: Progress callback functions
            
        Returns:
            Analysis progress tracker
        """
        progress = AnalysisProgress(
            analysis_id=analysis_id,
            total_items=total_items,
            callbacks=callbacks or []
        )
        
        self._active_analyses[analysis_id] = progress
        
        # Send initial update
        self._send_update(progress, ProgressUpdate(
            analysis_id=analysis_id,
            status=ProgressStatus.PENDING,
            current_step=0,
            total_steps=total_items,
            current_item="",
            message="Analysis initialized"
        ))
        
        logger.info(f"📊 Created progress tracker for {analysis_id} ({total_items} items)")
        return progress
    
    def start_analysis(self, analysis_id: str, current_item: str = "") -> None:
        """Start the analysis."""
        if analysis_id not in self._active_analyses:
            logger.warning(f"Analysis {analysis_id} not found")
            return
        
        progress = self._active_analyses[analysis_id]
        progress.status = ProgressStatus.IN_PROGRESS
        progress.current_item = current_item
        
        self._send_update(progress, ProgressUpdate(
            analysis_id=analysis_id,
            status=ProgressStatus.IN_PROGRESS,
            current_step=0,
            total_steps=progress.total_items,
            current_item=current_item,
            message="Analysis started"
        ))
        
        logger.info(f"🚀 Started analysis {analysis_id}")
    
    def update_progress(self, 
                       analysis_id: str, 
                       completed_item: str,
                       step: int,
                       message: str = "",
                       metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Update progress for an analysis.
        
        Args:
            analysis_id: Analysis identifier
            completed_item: Item that was just completed
            step: Current step number
            message: Progress message
            metadata: Additional metadata
        """
        if analysis_id not in self._active_analyses:
            logger.warning(f"Analysis {analysis_id} not found")
            return
        
        progress = self._active_analyses[analysis_id]
        progress.completed_items += 1
        progress.current_item = completed_item
        
        update = ProgressUpdate(
            analysis_id=analysis_id,
            status=ProgressStatus.IN_PROGRESS,
            current_step=step,
            total_steps=progress.total_items,
            current_item=completed_item,
            message=message or f"Completed {completed_item}",
            metadata=metadata or {}
        )
        
        self._send_update(progress, update)
        
        logger.debug(f"📈 Progress {analysis_id}: {progress.progress_percentage:.1f}% ({progress.completed_items}/{progress.total_items})")
    
    def fail_item(self, 
                  analysis_id: str, 
                  failed_item: str,
                  error: str,
                  step: int) -> None:
        """
        Mark an item as failed.
        
        Args:
            analysis_id: Analysis identifier
            failed_item: Item that failed
            error: Error message
            step: Current step number
        """
        if analysis_id not in self._active_analyses:
            logger.warning(f"Analysis {analysis_id} not found")
            return
        
        progress = self._active_analyses[analysis_id]
        progress.failed_items += 1
        
        update = ProgressUpdate(
            analysis_id=analysis_id,
            status=ProgressStatus.IN_PROGRESS,
            current_step=step,
            total_steps=progress.total_items,
            current_item=failed_item,
            message=f"Failed: {failed_item}",
            error=error
        )
        
        self._send_update(progress, update)
        
        logger.warning(f"❌ Failed item in {analysis_id}: {failed_item} - {error}")
    
    def complete_analysis(self, analysis_id: str, message: str = "Analysis completed") -> None:
        """Mark analysis as completed."""
        if analysis_id not in self._active_analyses:
            logger.warning(f"Analysis {analysis_id} not found")
            return
        
        progress = self._active_analyses[analysis_id]
        progress.status = ProgressStatus.COMPLETED
        progress.end_time = datetime.utcnow()
        
        update = ProgressUpdate(
            analysis_id=analysis_id,
            status=ProgressStatus.COMPLETED,
            current_step=progress.total_items,
            total_steps=progress.total_items,
            current_item="",
            message=message
        )
        
        self._send_update(progress, update)
        
        # Move to completed
        self._completed_analyses[analysis_id] = progress
        del self._active_analyses[analysis_id]
        
        logger.info(f"✅ Completed analysis {analysis_id} in {progress.elapsed_time:.2f}s")
    
    def fail_analysis(self, analysis_id: str, error: str) -> None:
        """Mark analysis as failed."""
        if analysis_id not in self._active_analyses:
            logger.warning(f"Analysis {analysis_id} not found")
            return
        
        progress = self._active_analyses[analysis_id]
        progress.status = ProgressStatus.FAILED
        progress.end_time = datetime.utcnow()
        
        update = ProgressUpdate(
            analysis_id=analysis_id,
            status=ProgressStatus.FAILED,
            current_step=progress.completed_items,
            total_steps=progress.total_items,
            current_item="",
            message="Analysis failed",
            error=error
        )
        
        self._send_update(progress, update)
        
        # Move to completed
        self._completed_analyses[analysis_id] = progress
        del self._active_analyses[analysis_id]
        
        logger.error(f"❌ Failed analysis {analysis_id}: {error}")
    
    def cancel_analysis(self, analysis_id: str) -> None:
        """Cancel an ongoing analysis."""
        if analysis_id not in self._active_analyses:
            logger.warning(f"Analysis {analysis_id} not found")
            return
        
        progress = self._active_analyses[analysis_id]
        progress.status = ProgressStatus.CANCELLED
        progress.end_time = datetime.utcnow()
        
        update = ProgressUpdate(
            analysis_id=analysis_id,
            status=ProgressStatus.CANCELLED,
            current_step=progress.completed_items,
            total_steps=progress.total_items,
            current_item="",
            message="Analysis cancelled"
        )
        
        self._send_update(progress, update)
        
        # Move to completed
        self._completed_analyses[analysis_id] = progress
        del self._active_analyses[analysis_id]
        
        logger.info(f"⏹️ Cancelled analysis {analysis_id}")
    
    def get_progress(self, analysis_id: str) -> Optional[AnalysisProgress]:
        """Get progress for an analysis."""
        return self._active_analyses.get(analysis_id) or self._completed_analyses.get(analysis_id)
    
    def get_all_active(self) -> Dict[str, AnalysisProgress]:
        """Get all active analyses."""
        return self._active_analyses.copy()
    
    def cleanup_completed(self, max_age_hours: int = 24) -> int:
        """Clean up old completed analyses."""
        cutoff_time = datetime.utcnow().timestamp() - (max_age_hours * 3600)
        
        to_remove = []
        for analysis_id, progress in self._completed_analyses.items():
            if progress.end_time and progress.end_time.timestamp() < cutoff_time:
                to_remove.append(analysis_id)
        
        for analysis_id in to_remove:
            del self._completed_analyses[analysis_id]
        
        logger.info(f"🧹 Cleaned up {len(to_remove)} old completed analyses")
        return len(to_remove)
    
    def _send_update(self, progress: AnalysisProgress, update: ProgressUpdate) -> None:
        """Send update to all callbacks."""
        progress.updates.append(update)
        
        # Send to all callbacks
        for callback in progress.callbacks:
            try:
                callback(update)
            except Exception as e:
                logger.error(f"Error in progress callback: {e}")


# Global progress tracker instance
_progress_tracker = ProgressTracker()

def get_progress_tracker() -> ProgressTracker:
    """Get the global progress tracker instance."""
    return _progress_tracker

# Decorator for progress tracking
def track_progress(total_items: int, 
                  analysis_id: Optional[str] = None,
                  callbacks: Optional[List[Callable[[ProgressUpdate], None]]] = None):
    """
    Decorator to track progress of analysis methods.
    
    Args:
        total_items: Total number of items to process
        analysis_id: Analysis identifier (auto-generated if not provided)
        callbacks: Progress callback functions
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Generate analysis ID if not provided
            current_analysis_id = analysis_id or f"analysis_{int(time.time())}_{id(func)}"
            
            # Create progress tracker
            tracker = get_progress_tracker()
            progress = tracker.create_analysis(
                analysis_id=current_analysis_id,
                total_items=total_items,
                callbacks=callbacks
            )
            
            try:
                # Start analysis
                tracker.start_analysis(current_analysis_id)
                
                # Execute function with progress context
                result = await func(*args, **kwargs, progress=progress)
                
                # Complete analysis
                tracker.complete_analysis(current_analysis_id)
                
                return result
                
            except Exception as e:
                # Fail analysis
                tracker.fail_analysis(current_analysis_id, str(e))
                raise
        
        return wrapper
    return decorator

# Utility callback functions
def console_progress_callback(update: ProgressUpdate) -> None:
    """Simple console progress callback."""
    status_icon = {
        ProgressStatus.PENDING: "⏳",
        ProgressStatus.IN_PROGRESS: "🔄",
        ProgressStatus.COMPLETED: "✅",
        ProgressStatus.FAILED: "❌",
        ProgressStatus.CANCELLED: "⏹️"
    }
    
    icon = status_icon.get(update.status, "❓")
    percentage = (update.current_step / update.total_steps) * 100 if update.total_steps > 0 else 0
    
    print(f"{icon} [{update.analysis_id}] {percentage:.1f}% - {update.message}")

def logging_progress_callback(update: ProgressUpdate) -> None:
    """Logging progress callback."""
    level = "INFO" if update.status != ProgressStatus.FAILED else "ERROR"
    logger.log(
        level,
        f"[{update.analysis_id}] {update.status.value}: {update.message} "
        f"({update.current_step}/{update.total_steps})"
    )
