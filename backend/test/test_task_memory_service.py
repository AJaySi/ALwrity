from datetime import datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.daily_workflow_models import TaskHistory
from models.enhanced_strategy_models import Base
from services.task_memory_service import TaskMemoryService


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine, tables=[TaskHistory.__table__])
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.mark.asyncio
async def test_filter_redundant_proposals_suppresses_exact_hash_duplicates(db_session):
    service = TaskMemoryService(user_id="user-1", db=db_session)
    service.intelligence = SimpleNamespace(search=AsyncMock(return_value=[]))

    title = "Create LinkedIn post"
    description = "Draft a post about customer success stories"

    db_session.add(
        TaskHistory(
            user_id="user-1",
            task_hash=service._compute_hash(title, description),
            title=title,
            description=description,
            pillar_id="engage",
            status="completed",
            created_at=datetime.utcnow(),
            vector_id="vec-exact",
        )
    )
    db_session.commit()

    proposals = [SimpleNamespace(title=title, description=description)]
    filtered = await service.filter_redundant_proposals(proposals)

    assert filtered == []


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "indexed_status,expected_filtered",
    [
        ("completed", False),
        ("skipped_not_today", False),
        ("dismissed_dont_show", True),
        ("rejected", True),
    ],
)
async def test_filter_redundant_proposals_semantic_behavior_for_each_outcome_status(
    db_session, indexed_status, expected_filtered
):
    service = TaskMemoryService(user_id="user-semantic", db=db_session)
    service.intelligence = SimpleNamespace(
        search=AsyncMock(return_value=[{"status": indexed_status, "score": 0.93}])
    )

    proposal = SimpleNamespace(
        title="Plan daily content topics",
        description="Choose 3 content ideas for this week",
    )
    filtered = await service.filter_redundant_proposals([proposal])

    assert (filtered == []) is expected_filtered


@pytest.mark.asyncio
async def test_filter_redundant_proposals_suppresses_semantic_dismissed_by_vector_id_lookup(db_session):
    service = TaskMemoryService(user_id="user-2", db=db_session)
    service.intelligence = SimpleNamespace(
        search=AsyncMock(return_value=[{"id": "vec-dismissed", "score": 0.93}])
    )

    db_session.add(
        TaskHistory(
            user_id="user-2",
            task_hash="hash-1",
            title="Old task",
            description="Old description",
            pillar_id="plan",
            status="dismissed_dont_show",
            created_at=datetime.utcnow(),
            vector_id="vec-dismissed",
        )
    )
    db_session.commit()

    proposals = [
        SimpleNamespace(
            title="Plan daily content topics",
            description="Choose 3 content ideas for this week",
        )
    ]

    filtered = await service.filter_redundant_proposals(proposals)

    assert filtered == []


@pytest.mark.asyncio
async def test_filter_redundant_proposals_keeps_non_duplicates(db_session):
    service = TaskMemoryService(user_id="user-3", db=db_session)
    service.intelligence = SimpleNamespace(
        search=AsyncMock(return_value=[{"id": "vec-completed", "score": 0.40}])
    )

    proposal = SimpleNamespace(
        title="Write newsletter intro",
        description="Prepare a short intro for the weekly newsletter",
    )
    filtered = await service.filter_redundant_proposals([proposal])

    assert filtered == [proposal]
    service.intelligence.search.assert_awaited_once()
