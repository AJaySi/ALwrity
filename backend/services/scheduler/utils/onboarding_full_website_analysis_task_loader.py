"""
Onboarding Full Website Analysis Task Loader
Functions to load due onboarding full-site SEO audit tasks from database.
"""

from datetime import datetime
from typing import List, Optional, Union

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from models.website_analysis_monitoring_models import OnboardingFullWebsiteAnalysisTask


def load_due_onboarding_full_website_analysis_tasks(
    db: Session,
    user_id: Optional[Union[str, int]] = None
) -> List[OnboardingFullWebsiteAnalysisTask]:
    now = datetime.utcnow()

    query = db.query(OnboardingFullWebsiteAnalysisTask).filter(
        and_(
            OnboardingFullWebsiteAnalysisTask.status == 'active',
            or_(
                OnboardingFullWebsiteAnalysisTask.next_execution <= now,
                OnboardingFullWebsiteAnalysisTask.next_execution.is_(None)
            )
        )
    )

    if user_id is not None:
        query = query.filter(OnboardingFullWebsiteAnalysisTask.user_id == str(user_id))

    return query.all()

