"""Persistent shared backend for task, latest strategy, and streaming cache state."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from models.content_strategy_state_models import (
    StrategyGenerationTaskState,
    LatestGeneratedStrategyState,
    StreamingCacheState,
)


class SharedStateBackend:
    """DB-backed state storage that supports multi-worker reads/writes."""

    TASK_TTL_SECONDS = 60 * 60
    LATEST_STRATEGY_TTL_SECONDS = 24 * 60 * 60
    STREAMING_CACHE_TTL_SECONDS = 5 * 60

    def __init__(self, db: Session):
        self.db = db

    def _now(self) -> datetime:
        return datetime.utcnow()

    def cleanup_expired(self) -> None:
        now = self._now()
        self.db.query(StrategyGenerationTaskState).filter(StrategyGenerationTaskState.expires_at <= now).delete()
        self.db.query(LatestGeneratedStrategyState).filter(LatestGeneratedStrategyState.expires_at <= now).delete()
        self.db.query(StreamingCacheState).filter(StreamingCacheState.expires_at <= now).delete()
        self.db.commit()

    def _ensure_not_expired(self, record: Any) -> bool:
        if not record:
            return False
        if record.expires_at <= self._now():
            self.db.delete(record)
            self.db.commit()
            return False
        return True

    # Task lifecycle/status
    def set_task_status(self, user_id: str, task_id: str, status_payload: Dict[str, Any], ttl_seconds: Optional[int] = None) -> Dict[str, Any]:
        expires_at = self._now() + timedelta(seconds=ttl_seconds or self.TASK_TTL_SECONDS)
        row = self.db.query(StrategyGenerationTaskState).filter(
            StrategyGenerationTaskState.user_id == user_id,
            StrategyGenerationTaskState.task_id == task_id,
        ).first()
        if not row:
            row = StrategyGenerationTaskState(
                user_id=user_id,
                task_id=task_id,
                status_payload=status_payload,
                expires_at=expires_at,
            )
            self.db.add(row)
        else:
            row.status_payload = status_payload
            row.expires_at = expires_at
        self.db.commit()
        return status_payload

    def update_task_status(self, user_id: str, task_id: str, updates: Dict[str, Any], ttl_seconds: Optional[int] = None) -> Optional[Dict[str, Any]]:
        current = self.get_task_status(user_id, task_id)
        if not current:
            return None
        current.update(updates)
        return self.set_task_status(user_id, task_id, current, ttl_seconds=ttl_seconds)

    def get_task_status(self, user_id: str, task_id: str) -> Optional[Dict[str, Any]]:
        row = self.db.query(StrategyGenerationTaskState).filter(
            StrategyGenerationTaskState.user_id == user_id,
            StrategyGenerationTaskState.task_id == task_id,
        ).first()
        if not self._ensure_not_expired(row):
            return None
        return row.status_payload

    def list_user_tasks(self, user_id: str) -> Dict[str, Dict[str, Any]]:
        tasks = {}
        for row in self.db.query(StrategyGenerationTaskState).filter(StrategyGenerationTaskState.user_id == user_id).all():
            if self._ensure_not_expired(row):
                tasks[row.task_id] = row.status_payload
        return tasks

    # Latest strategy refs
    def set_latest_strategy(self, user_id: str, strategy_payload: Dict[str, Any], resource_id: str = "comprehensive", ttl_seconds: Optional[int] = None) -> Dict[str, Any]:
        expires_at = self._now() + timedelta(seconds=ttl_seconds or self.LATEST_STRATEGY_TTL_SECONDS)
        row = self.db.query(LatestGeneratedStrategyState).filter(
            LatestGeneratedStrategyState.user_id == user_id,
            LatestGeneratedStrategyState.resource_id == resource_id,
        ).first()
        if not row:
            row = LatestGeneratedStrategyState(
                user_id=user_id,
                resource_id=resource_id,
                strategy_payload=strategy_payload,
                expires_at=expires_at,
            )
            self.db.add(row)
        else:
            row.strategy_payload = strategy_payload
            row.expires_at = expires_at
        self.db.commit()
        return strategy_payload

    def get_latest_strategy(self, user_id: str, resource_id: str = "comprehensive") -> Optional[Dict[str, Any]]:
        row = self.db.query(LatestGeneratedStrategyState).filter(
            LatestGeneratedStrategyState.user_id == user_id,
            LatestGeneratedStrategyState.resource_id == resource_id,
        ).first()
        if not self._ensure_not_expired(row):
            return None
        return row.strategy_payload

    # Streaming cache
    def set_streaming_cache(self, user_id: str, cache_key: str, cache_payload: Dict[str, Any], ttl_seconds: Optional[int] = None) -> Dict[str, Any]:
        expires_at = self._now() + timedelta(seconds=ttl_seconds or self.STREAMING_CACHE_TTL_SECONDS)
        row = self.db.query(StreamingCacheState).filter(
            StreamingCacheState.user_id == user_id,
            StreamingCacheState.cache_key == cache_key,
        ).first()
        if not row:
            row = StreamingCacheState(
                user_id=user_id,
                cache_key=cache_key,
                cache_payload=cache_payload,
                expires_at=expires_at,
            )
            self.db.add(row)
        else:
            row.cache_payload = cache_payload
            row.expires_at = expires_at
        self.db.commit()
        return cache_payload

    def get_streaming_cache(self, user_id: str, cache_key: str) -> Optional[Dict[str, Any]]:
        row = self.db.query(StreamingCacheState).filter(
            StreamingCacheState.user_id == user_id,
            StreamingCacheState.cache_key == cache_key,
        ).first()
        if not self._ensure_not_expired(row):
            return None
        return row.cache_payload
