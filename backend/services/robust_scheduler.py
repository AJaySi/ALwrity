"""
Robust Scheduler Implementation for ALwrity
Enhanced with connection pool management, error recovery, and monitoring
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from loguru import logger
from contextlib import asynccontextmanager
from dataclasses import dataclass
from enum import Enum

class SchedulerStatus(Enum):
    STARTING = "starting"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"

@dataclass
class SchedulerMetrics:
    """Scheduler performance metrics"""
    total_cycles: int = 0
    successful_cycles: int = 0
    failed_cycles: int = 0
    last_cycle_time: Optional[datetime] = None
    last_cycle_duration: float = 0.0
    average_cycle_duration: float = 0.0
    active_tasks: int = 0
    queued_tasks: int = 0
    connection_pool_status: Dict[str, Any] = None

class RobustScheduler:
    """
    Enhanced scheduler with robust error handling and connection management
    """
    
    def __init__(self, check_interval_minutes: int = 60):
        self.check_interval = check_interval_minutes * 60  # Convert to seconds
        self.status = SchedulerStatus.STOPPED
        self.metrics = SchedulerMetrics()
        self.start_time: Optional[datetime] = None
        self.last_health_check: Optional[datetime] = None
        self.error_count = 0
        self.max_consecutive_errors = 5
        self._shutdown_event = asyncio.Event()
        
    async def start(self):
        """Start the scheduler with enhanced error handling"""
        if self.status != SchedulerStatus.STOPPED:
            logger.warning(f"[RobustScheduler] Scheduler already running (status: {self.status.value})")
            return
            
        logger.info("[RobustScheduler] 🚀 Starting enhanced scheduler...")
        self.status = SchedulerStatus.STARTING
        self.start_time = datetime.now()
        self.error_count = 0
        
        try:
            # Initialize connection pools
            await self._initialize_connection_pools()
            
            # Validate database connectivity
            await self._validate_database_connectivity()
            
            # Start main scheduler loop
            self.status = SchedulerStatus.RUNNING
            logger.info(f"[RobustScheduler] ✅ Scheduler started successfully")
            logger.info(f"[RobustScheduler] 📊 Check interval: {self.check_interval}s")
            
            await self._main_scheduler_loop()
            
        except Exception as e:
            logger.error(f"[RobustScheduler] ❌ Failed to start scheduler: {e}")
            self.status = SchedulerStatus.ERROR
            raise
    
    async def stop(self):
        """Gracefully stop the scheduler"""
        if self.status == SchedulerStatus.STOPPED:
            return
            
        logger.info("[RobustScheduler] 🛑 Stopping scheduler...")
        self.status = SchedulerStatus.STOPPING
        self._shutdown_event.set()
        
        # Wait for current cycle to complete
        await asyncio.sleep(2)
        
        # Close connections
        await self._cleanup_resources()
        
        self.status = SchedulerStatus.STOPPED
        logger.info("[RobustScheduler] ✅ Scheduler stopped gracefully")
    
    async def _main_scheduler_loop(self):
        """Main scheduler loop with error recovery"""
        consecutive_errors = 0
        
        while not self._shutdown_event.is_set():
            try:
                if self.status != SchedulerStatus.RUNNING:
                    await asyncio.sleep(1)
                    continue
                
                cycle_start = time.time()
                logger.info(f"[RobustScheduler] 🔄 Starting check cycle #{self.metrics.total_cycles + 1}")
                
                # Execute check cycle with connection management
                success = await self._execute_check_cycle()
                
                cycle_duration = time.time() - cycle_start
                self._update_metrics(success, cycle_duration)
                
                # Reset error count on successful cycle
                if success:
                    consecutive_errors = 0
                    logger.info(f"[RobustScheduler] ✅ Check cycle completed in {cycle_duration:.2f}s")
                else:
                    consecutive_errors += 1
                    logger.warning(f"[RobustScheduler] ⚠️ Check cycle failed (consecutive errors: {consecutive_errors})")
                
                # Check if we should pause due to too many errors
                if consecutive_errors >= self.max_consecutive_errors:
                    logger.error(f"[RobustScheduler] 🚨 Too many consecutive errors ({consecutive_errors}), pausing scheduler")
                    self.status = SchedulerStatus.ERROR
                    await asyncio.sleep(60)  # Wait 1 minute before retrying
                    self.status = SchedulerStatus.RUNNING
                    consecutive_errors = 0
                
                # Wait for next cycle
                await self._wait_for_next_cycle()
                
            except asyncio.CancelledError:
                logger.info("[RobustScheduler] 🛑 Scheduler loop cancelled")
                break
            except Exception as e:
                logger.error(f"[RobustScheduler] ❌ Unexpected error in scheduler loop: {e}")
                consecutive_errors += 1
                await asyncio.sleep(min(60, consecutive_errors * 10))  # Exponential backoff
    
    async def _execute_check_cycle(self) -> bool:
        """Execute a single check cycle with proper connection management"""
        try:
            # Import here to avoid circular dependencies
            from services.scheduler.core.check_cycle_handler import CheckCycleHandler
            
            # Use connection context manager
            async with self._get_database_session() as db:
                if not db:
                    logger.error("[RobustScheduler] ❌ Failed to get database session")
                    return False
                
                # Execute check cycle
                handler = CheckCycleHandler()
                await handler.execute_check_cycle(db)
                
                return True
                
        except Exception as e:
            logger.error(f"[RobustScheduler] ❌ Check cycle execution failed: {e}")
            return False
    
    @asynccontextmanager
    async def _get_database_session(self):
        """Context manager for database sessions with error handling"""
        db = None
        try:
            from services.database import get_db_session
            db = get_db_session()
            if not db:
                raise Exception("Failed to create database session")
            yield db
        except Exception as e:
            logger.error(f"[RobustScheduler] Database session error: {e}")
            raise
        finally:
            if db:
                try:
                    db.close()
                except Exception as e:
                    logger.error(f"[RobustScheduler] Error closing database session: {e}")
    
    async def _initialize_connection_pools(self):
        """Initialize database connection pools"""
        try:
            logger.info("[RobustScheduler] 🔧 Initializing connection pools...")
            
            # Test database connections
            from services.database import get_platform_db_session, get_user_data_db_session
            
            platform_db = get_platform_db_session()
            if platform_db:
                platform_db.close()
                logger.info("[RobustScheduler] ✅ Platform database connection verified")
            
            user_db = get_user_data_db_session()
            if user_db:
                user_db.close()
                logger.info("[RobustScheduler] ✅ User data database connection verified")
            
            logger.info("[RobustScheduler] ✅ Connection pools initialized successfully")
            
        except Exception as e:
            logger.error(f"[RobustScheduler] ❌ Failed to initialize connection pools: {e}")
            raise
    
    async def _validate_database_connectivity(self):
        """Validate database connectivity and required tables"""
        try:
            logger.info("[RobustScheduler] 🔍 Validating database connectivity...")
            
            # Check platform database tables
            async with self._get_database_session() as db:
                # Test basic queries
                result = db.execute("SELECT 1").fetchone()
                if not result:
                    raise Exception("Database connectivity test failed")
                
                logger.info("[RobustScheduler] ✅ Database connectivity validated")
                
        except Exception as e:
            logger.error(f"[RobustScheduler] ❌ Database connectivity validation failed: {e}")
            raise
    
    async def _cleanup_resources(self):
        """Clean up scheduler resources"""
        try:
            logger.info("[RobustScheduler] 🧹 Cleaning up resources...")
            
            # Close any open connections
            from services.database import close_database
            close_database()
            
            logger.info("[RobustScheduler] ✅ Resources cleaned up successfully")
            
        except Exception as e:
            logger.error(f"[RobustScheduler] ❌ Error during cleanup: {e}")
    
    async def _wait_for_next_cycle(self):
        """Wait for the next scheduled cycle with shutdown support"""
        end_time = time.time() + self.check_interval
        
        while time.time() < end_time and not self._shutdown_event.is_set():
            remaining = end_time - time.time()
            if remaining > 0:
                await asyncio.sleep(min(1, remaining))
    
    def _update_metrics(self, success: bool, duration: float):
        """Update scheduler metrics"""
        self.metrics.total_cycles += 1
        
        if success:
            self.metrics.successful_cycles += 1
        else:
            self.metrics.failed_cycles += 1
        
        self.metrics.last_cycle_time = datetime.now()
        self.metrics.last_cycle_duration = duration
        
        # Calculate average duration
        if self.metrics.total_cycles > 0:
            total_duration = (self.metrics.average_cycle_duration * (self.metrics.total_cycles - 1) + duration)
            self.metrics.average_cycle_duration = total_duration / self.metrics.total_cycles
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive scheduler status"""
        uptime = None
        if self.start_time:
            uptime = datetime.now() - self.start_time
        
        return {
            "status": self.status.value,
            "uptime_seconds": uptime.total_seconds() if uptime else None,
            "metrics": {
                "total_cycles": self.metrics.total_cycles,
                "successful_cycles": self.metrics.successful_cycles,
                "failed_cycles": self.metrics.failed_cycles,
                "success_rate": (self.metrics.successful_cycles / max(1, self.metrics.total_cycles)) * 100,
                "last_cycle_time": self.metrics.last_cycle_time.isoformat() if self.metrics.last_cycle_time else None,
                "last_cycle_duration": self.metrics.last_cycle_duration,
                "average_cycle_duration": self.metrics.average_cycle_duration,
            },
            "configuration": {
                "check_interval_seconds": self.check_interval,
                "max_consecutive_errors": self.max_consecutive_errors,
            },
            "health": {
                "error_count": self.error_count,
                "last_health_check": self.last_health_check.isoformat() if self.last_health_check else None,
            }
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check"""
        try:
            self.last_health_check = datetime.now()
            
            # Check database connectivity
            db_healthy = True
            try:
                async with self._get_database_session() as db:
                    db.execute("SELECT 1").fetchone()
            except Exception as e:
                db_healthy = False
                logger.error(f"[RobustScheduler] Health check database error: {e}")
            
            return {
                "healthy": db_healthy and self.status == SchedulerStatus.RUNNING,
                "status": self.status.value,
                "database_healthy": db_healthy,
                "timestamp": self.last_health_check.isoformat(),
                "metrics": self.get_status()["metrics"]
            }
            
        except Exception as e:
            logger.error(f"[RobustScheduler] Health check failed: {e}")
            return {
                "healthy": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

# Global scheduler instance
_robust_scheduler: Optional[RobustScheduler] = None

def get_robust_scheduler() -> RobustScheduler:
    """Get the global robust scheduler instance"""
    global _robust_scheduler
    if _robust_scheduler is None:
        _robust_scheduler = RobustScheduler()
    return _robust_scheduler
