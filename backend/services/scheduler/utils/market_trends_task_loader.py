"""
Market Trends Task Loader
Loads due market trends tasks from the database.
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

from models.website_analysis_monitoring_models import MarketTrendsTask
from utils.logger_utils import get_service_logger

logger = get_service_logger("market_trends_task_loader")


def load_due_market_trends_tasks(db: Session, user_id: Optional[str] = None) -> List[MarketTrendsTask]:
    try:
        now = datetime.utcnow()

        query = db.query(MarketTrendsTask).filter(
            MarketTrendsTask.status == "active",
            or_(MarketTrendsTask.next_execution <= now, MarketTrendsTask.next_execution == None),
        )

        if user_id:
            query = query.filter(MarketTrendsTask.user_id == user_id)

        tasks = query.all()
        if tasks:
            logger.info(f"Loaded {len(tasks)} due market trends tasks")
        return tasks
    except Exception as e:
        logger.error(f"Error loading market trends tasks: {e}")
        return []

