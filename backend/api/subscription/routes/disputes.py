from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from pydantic import BaseModel
from services.database import get_db
from middleware.auth_middleware import get_current_user
from loguru import logger
import stripe
import os

router = APIRouter()


def _ensure_admin(current_user: Dict[str, Any]) -> None:
    disable_auth = os.getenv("DISABLE_AUTH", "false").lower() == "true"
    if disable_auth:
        return

    email = (current_user.get("email") or "").lower()
    role = None
    public_metadata = current_user.get("public_metadata")
    if isinstance(public_metadata, dict):
        role = public_metadata.get("role") or current_user.get("role")
    else:
        role = current_user.get("role")

    admin_emails_raw = os.getenv("ADMIN_EMAILS", "")
    admin_emails = {
        e.strip().lower() for e in admin_emails_raw.split(",") if e.strip()
    }
    admin_domain = (os.getenv("ADMIN_EMAIL_DOMAIN") or "").lower().strip()

    is_admin_email = email and email in admin_emails
    is_admin_domain = email and admin_domain and email.endswith("@" + admin_domain)
    is_admin_role = role == "admin"

    if not (is_admin_email or is_admin_domain or is_admin_role):
        raise HTTPException(status_code=403, detail="Admin access required for dispute operations")


def _get_stripe_client() -> None:
    api_key = os.getenv("STRIPE_SECRET_KEY")
    if not api_key:
        logger.error("STRIPE_SECRET_KEY is not configured; dispute operations are disabled")
        raise HTTPException(status_code=500, detail="Payment service not configured")
    stripe.api_key = api_key


class DisputeEvidenceUpdateRequest(BaseModel):
    evidence: Optional[Dict[str, Any]] = None


@router.get("/disputes")
async def list_disputes(
    limit: int = 10,
    starting_after: Optional[str] = None,
    ending_before: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    _get_stripe_client()
    _ensure_admin(current_user)

    try:
        params: Dict[str, Any] = {"limit": max(1, min(limit, 100))}
        if starting_after:
            params["starting_after"] = starting_after
        if ending_before:
            params["ending_before"] = ending_before

        disputes = stripe.Dispute.list(**params)
        return {"data": disputes}
    except Exception as e:
        logger.error(f"Error listing disputes: {e}")
        raise HTTPException(status_code=500, detail="Failed to list disputes")


@router.get("/disputes/{dispute_id}")
async def get_dispute(
    dispute_id: str,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    _get_stripe_client()
    _ensure_admin(current_user)

    try:
        dispute = stripe.Dispute.retrieve(dispute_id)
        return {"data": dispute}
    except stripe.error.InvalidRequestError as e:
        logger.warning(f"Invalid dispute id {dispute_id}: {e}")
        raise HTTPException(status_code=404, detail="Dispute not found")
    except Exception as e:
        logger.error(f"Error retrieving dispute {dispute_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve dispute")


@router.post("/disputes/{dispute_id}")
async def update_dispute(
    dispute_id: str,
    payload: DisputeEvidenceUpdateRequest,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    _get_stripe_client()
    _ensure_admin(current_user)

    if not payload.evidence:
        raise HTTPException(status_code=400, detail="Evidence payload is required to update a dispute")

    try:
        dispute = stripe.Dispute.modify(
            dispute_id,
            evidence=payload.evidence,
        )
        return {"data": dispute}
    except stripe.error.InvalidRequestError as e:
        logger.warning(f"Invalid dispute id {dispute_id} during update: {e}")
        raise HTTPException(status_code=404, detail="Dispute not found")
    except Exception as e:
        logger.error(f"Error updating dispute {dispute_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update dispute")


@router.post("/disputes/{dispute_id}/close")
async def close_dispute(
    dispute_id: str,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    _get_stripe_client()
    _ensure_admin(current_user)

    try:
        dispute = stripe.Dispute.close(dispute_id)
        return {"data": dispute}
    except stripe.error.InvalidRequestError as e:
        logger.warning(f"Invalid dispute id {dispute_id} during close: {e}")
        raise HTTPException(status_code=404, detail="Dispute not found")
    except Exception as e:
        logger.error(f"Error closing dispute {dispute_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to close dispute")
