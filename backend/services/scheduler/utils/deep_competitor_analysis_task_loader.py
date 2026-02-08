from datetime import datetime
from typing import List, Optional, Union

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from models.website_analysis_monitoring_models import DeepCompetitorAnalysisTask


def load_due_deep_competitor_analysis_tasks(
    db: Session,
    user_id: Optional[Union[str, int]] = None
) -> List[DeepCompetitorAnalysisTask]:
    now = datetime.utcnow()

    query = db.query(DeepCompetitorAnalysisTask).filter(
        and_(
            DeepCompetitorAnalysisTask.status == 'active',
            or_(
                DeepCompetitorAnalysisTask.next_execution <= now,
                DeepCompetitorAnalysisTask.next_execution.is_(None)
            )
        )
    )

    if user_id is not None:
        query = query.filter(DeepCompetitorAnalysisTask.user_id == str(user_id))

    return query.all()

