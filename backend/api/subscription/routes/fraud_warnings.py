from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from pydantic import BaseModel
from services.database import get_db
from middleware.auth_middleware import get_current_user
from loguru import logger
import stripe
import os
from datetime import datetime
from models.subscription_models import FraudWarning


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
        raise HTTPException(status_code=403, detail="Admin access required for fraud warning operations")


def _get_stripe_client() -> None:
    api_key = os.getenv("STRIPE_SECRET_KEY")
    if not api_key:
        logger.error("STRIPE_SECRET_KEY is not configured; fraud warning operations are disabled")
        raise HTTPException(status_code=500, detail="Payment service not configured")
    stripe.api_key = api_key


class FraudWarningRefundRequest(BaseModel):
    notes: Optional[str] = None


class FraudWarningIgnoreRequest(BaseModel):
    notes: Optional[str] = None


@router.get("/fraud-warnings")
async def list_fraud_warnings(
    status: Optional[str] = "open",
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    _ensure_admin(current_user)

    query = db.query(FraudWarning)
    if status:
        query = query.filter(FraudWarning.status == status)

    limit = max(1, min(limit, 100))
    items = (
        query.order_by(FraudWarning.created_at.desc())
        .offset(max(0, offset))
        .limit(limit)
        .all()
    )

    data = []
    for fw in items:
        data.append(
            {
                "id": fw.id,
                "charge_id": fw.charge_id,
                "payment_intent_id": fw.payment_intent_id,
                "user_id": fw.user_id,
                "amount": fw.amount,
                "currency": fw.currency,
                "status": fw.status,
                "action": fw.action,
                "action_at": fw.action_at.isoformat() if fw.action_at else None,
                "created_at": fw.created_at.isoformat() if fw.created_at else None,
            }
        )

    return {"data": data}


@router.get("/fraud-warnings/{warning_id}")
async def get_fraud_warning(
    warning_id: str,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    _ensure_admin(current_user)

    fw = db.query(FraudWarning).filter(FraudWarning.id == warning_id).first()
    if not fw:
        raise HTTPException(status_code=404, detail="Fraud warning not found")

    payload: Dict[str, Any] = {
        "id": fw.id,
        "charge_id": fw.charge_id,
        "payment_intent_id": fw.payment_intent_id,
        "user_id": fw.user_id,
        "amount": fw.amount,
        "currency": fw.currency,
        "status": fw.status,
        "action": fw.action,
        "action_at": fw.action_at.isoformat() if fw.action_at else None,
        "reason_notes": fw.reason_notes,
        "created_at": fw.created_at.isoformat() if fw.created_at else None,
        "meta_info": fw.meta_info,
    }

    return {"data": payload}


@router.post("/fraud-warnings/{warning_id}/refund")
async def refund_fraud_warning(
    warning_id: str,
    payload: FraudWarningRefundRequest,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    _ensure_admin(current_user)
    _get_stripe_client()

    fw = db.query(FraudWarning).filter(FraudWarning.id == warning_id).first()
    if not fw:
        raise HTTPException(status_code=404, detail="Fraud warning not found")

    if fw.status == "refunded":
        raise HTTPException(status_code=400, detail="Fraud warning already refunded")

    try:
        stripe.Refund.create(charge=fw.charge_id)
    except stripe.error.InvalidRequestError as e:
        logger.warning(f"Refund failed for fraud warning {warning_id}, charge {fw.charge_id}: {e}")
        raise HTTPException(status_code=400, detail="Refund failed for this charge")
    except Exception as e:
        logger.error(f"Unexpected error refunding fraud warning {warning_id}: {e}")
        raise HTTPException(status_code=500, detail="Unexpected error while processing refund")

    fw.status = "refunded"
    fw.action = "refund_full"
    fw.action_at = datetime.utcnow()
    if payload and payload.notes:
        fw.reason_notes = payload.notes

    db.commit()
    db.refresh(fw)

    return {
        "data": {
            "id": fw.id,
            "status": fw.status,
            "action": fw.action,
            "action_at": fw.action_at.isoformat() if fw.action_at else None,
            "reason_notes": fw.reason_notes,
        }
    }


@router.post("/fraud-warnings/{warning_id}/ignore")
async def ignore_fraud_warning(
    warning_id: str,
    payload: FraudWarningIgnoreRequest,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    _ensure_admin(current_user)

    fw = db.query(FraudWarning).filter(FraudWarning.id == warning_id).first()
    if not fw:
        raise HTTPException(status_code=404, detail="Fraud warning not found")

    fw.status = "ignored"
    fw.action = "ignored"
    fw.action_at = datetime.utcnow()
    if payload and payload.notes:
        fw.reason_notes = payload.notes

    db.commit()
    db.refresh(fw)

    return {
        "data": {
            "id": fw.id,
            "status": fw.status,
            "action": fw.action,
            "action_at": fw.action_at.isoformat() if fw.action_at else None,
            "reason_notes": fw.reason_notes,
        }
    }

