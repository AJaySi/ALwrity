"""Structured observability helpers for LLM routing decisions."""

from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, Optional


def _mask_user_id(user_id: Optional[str]) -> str:
    if not user_id:
        return "anonymous"
    return hashlib.sha256(str(user_id).encode("utf-8")).hexdigest()[:12]


def emit_routing_event(logger, event: str, *, user_id: Optional[str] = None, **fields: Any) -> None:
    payload: Dict[str, Any] = {
        "event": event,
        "tenant": _mask_user_id(user_id),
        **fields,
    }
    logger.info("[llm_routing] {}", json.dumps(payload, sort_keys=True, default=str))
