"""Service for retrieving persisted platform opportunity/alert events."""

from typing import Dict, Any, List, Optional

from loguru import logger

from models.platform_insights_monitoring_models import PlatformInsightDeltaEvent
from services.database import get_session_for_user


class OpportunityAlertsService:
    """Read optimized access to latest persisted opportunities/alerts."""

    def get_latest_events(
        self,
        user_id: str,
        platform: str = 'gsc',
        site_url: Optional[str] = None,
        event_types: Optional[List[str]] = None,
        limit: int = 25,
    ) -> List[Dict[str, Any]]:
        db = None
        try:
            db = get_session_for_user(user_id)
            query = db.query(PlatformInsightDeltaEvent).filter(
                PlatformInsightDeltaEvent.user_id == user_id,
                PlatformInsightDeltaEvent.platform == platform,
            )
            if site_url:
                query = query.filter(PlatformInsightDeltaEvent.site_url == site_url)
            if event_types:
                query = query.filter(PlatformInsightDeltaEvent.event_type.in_(event_types))

            rows = query.order_by(PlatformInsightDeltaEvent.created_at.desc()).limit(limit).all()
            return [
                {
                    'id': row.id,
                    'platform': row.platform,
                    'site_url': row.site_url,
                    'event_type': row.event_type,
                    'entity_type': row.entity_type,
                    'entity_key': row.entity_key,
                    'severity': row.severity,
                    'current_window': {
                        'start': row.current_start_date,
                        'end': row.current_end_date,
                    },
                    'prior_window': {
                        'start': row.prior_start_date,
                        'end': row.prior_end_date,
                    },
                    'details': row.details,
                    'created_at': row.created_at.isoformat() if row.created_at else None,
                }
                for row in rows
            ]
        except Exception as e:
            logger.error(f"Failed to load latest opportunity/alert events for user {user_id}: {e}")
            return []
        finally:
            if db:
                db.close()
