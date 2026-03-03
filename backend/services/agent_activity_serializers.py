from __future__ import annotations

from typing import Any, Dict
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse

from models.agent_activity_models import AgentAlert, AgentApprovalRequest, AgentEvent, AgentRun

DETAIL_TIER_SUMMARY = "summary"
DETAIL_TIER_DETAILED = "detailed"
DETAIL_TIER_DEBUG = "debug"
ALLOWED_DETAIL_TIERS = {DETAIL_TIER_SUMMARY, DETAIL_TIER_DETAILED, DETAIL_TIER_DEBUG}

SENSITIVE_KEYWORDS = {
    "token", "secret", "password", "pass", "api_key", "apikey", "auth", "authorization",
    "cookie", "session", "credential", "ssn", "email", "phone", "address", "prompt", "raw_prompt",
}
SENSITIVE_QUERY_PARAMS = {
    "token", "access_token", "auth", "authorization", "apikey", "api_key", "signature", "sig", "secret",
}


def normalize_detail_tier(value: Any) -> str:
    tier = str(value or DETAIL_TIER_SUMMARY).strip().lower()
    if tier not in ALLOWED_DETAIL_TIERS:
        return DETAIL_TIER_SUMMARY
    return tier


def redact_sensitive_data(value: Any, key_hint: str | None = None) -> Any:
    if isinstance(value, dict):
        return {k: redact_sensitive_data(v, key_hint=str(k)) for k, v in value.items()}
    if isinstance(value, list):
        return [redact_sensitive_data(item, key_hint=key_hint) for item in value]

    lowered_hint = (key_hint or "").lower()
    if any(word in lowered_hint for word in SENSITIVE_KEYWORDS):
        return "[REDACTED]"

    if isinstance(value, str):
        if "@" in value and any(word in lowered_hint for word in {"user", "contact", "owner", "email"}):
            return "[REDACTED_EMAIL]"
        if _looks_like_secret(value):
            return "[REDACTED]"
        return _sanitize_url(value)
    return value


def serialize_alert(alert: AgentAlert, detail_tier: str) -> Dict[str, Any]:
    payload = redact_sensitive_data(alert.payload)
    base = {
        "id": alert.id,
        "source": alert.source,
        "type": alert.alert_type,
        "severity": alert.severity,
        "title": alert.title,
        "message": alert.message,
        "created_at": alert.created_at.isoformat() if alert.created_at else None,
        "read_at": alert.read_at.isoformat() if alert.read_at else None,
    }
    if detail_tier in {DETAIL_TIER_DETAILED, DETAIL_TIER_DEBUG}:
        base["cta_path"] = alert.cta_path
        base["payload"] = payload
    return base


def serialize_run(run: AgentRun, detail_tier: str) -> Dict[str, Any]:
    serialized = {
        "id": run.id,
        "agent_type": run.agent_type,
        "status": run.status,
        "success": run.success,
        "result_summary": run.result_summary,
        "started_at": run.started_at.isoformat() if run.started_at else None,
        "finished_at": run.finished_at.isoformat() if run.finished_at else None,
    }
    if detail_tier in {DETAIL_TIER_DETAILED, DETAIL_TIER_DEBUG}:
        serialized["error_message"] = redact_sensitive_data(run.error_message, key_hint="error_message")
        serialized["mlflow_run_id"] = run.mlflow_run_id
    if detail_tier == DETAIL_TIER_DEBUG:
        serialized["user_id"] = run.user_id
        serialized["prompt"] = redact_sensitive_data(run.prompt, key_hint="prompt")
    return serialized


def serialize_event(event: AgentEvent, detail_tier: str) -> Dict[str, Any]:
    serialized = {
        "id": event.id,
        "run_id": event.run_id,
        "agent_type": event.agent_type,
        "event_type": event.event_type,
        "severity": event.severity,
        "message": event.message,
        "created_at": event.created_at.isoformat() if event.created_at else None,
    }
    if detail_tier in {DETAIL_TIER_DETAILED, DETAIL_TIER_DEBUG}:
        serialized["payload"] = redact_sensitive_data(event.payload)
    return serialized


def serialize_approval(approval: AgentApprovalRequest, detail_tier: str) -> Dict[str, Any]:
    serialized = {
        "id": approval.id,
        "status": approval.status,
        "decision": approval.decision,
        "action_id": approval.action_id,
        "action_type": approval.action_type,
        "agent_type": approval.agent_type,
        "target_resource": redact_sensitive_data(approval.target_resource, key_hint="target_resource"),
        "risk_level": approval.risk_level,
        "created_at": approval.created_at.isoformat() if approval.created_at else None,
        "decided_at": approval.decided_at.isoformat() if approval.decided_at else None,
    }
    if detail_tier in {DETAIL_TIER_DETAILED, DETAIL_TIER_DEBUG}:
        serialized["payload"] = redact_sensitive_data(approval.payload)
    if detail_tier == DETAIL_TIER_DEBUG:
        serialized["user_comments"] = redact_sensitive_data(approval.user_comments, key_hint="user_comments")
    return serialized


def _looks_like_secret(value: str) -> bool:
    compact = value.strip()
    if len(compact) > 32 and any(ch.isdigit() for ch in compact) and any(ch.isalpha() for ch in compact):
        return True
    return False


def _sanitize_url(value: str) -> str:
    if not value.startswith(("http://", "https://")):
        return value
    try:
        parsed = urlparse(value)
        query_items = []
        for k, v in parse_qsl(parsed.query, keep_blank_values=True):
            if k.lower() in SENSITIVE_QUERY_PARAMS:
                query_items.append((k, "[REDACTED]"))
            else:
                query_items.append((k, v))
        netloc = parsed.netloc
        if parsed.username or parsed.password:
            host = parsed.hostname or ""
            if parsed.port:
                host = f"{host}:{parsed.port}"
            netloc = f"[REDACTED]@{host}"
        return urlunparse(parsed._replace(netloc=netloc, query=urlencode(query_items)))
    except Exception:
        return "[REDACTED_URL]"
