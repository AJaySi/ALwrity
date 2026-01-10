"""
Usage alerts endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Dict, Any
from datetime import datetime
from loguru import logger

from services.database import get_db
from models.subscription_models import UsageAlert

router = APIRouter()


@router.get("/alerts/{user_id}")
async def get_usage_alerts(
    user_id: str,
    unread_only: bool = Query(False, description="Only return unread alerts"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of alerts"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get usage alerts for a user."""
    
    try:
        query = db.query(UsageAlert).filter(
            UsageAlert.user_id == user_id
        )
        
        if unread_only:
            query = query.filter(UsageAlert.is_read == False)
        
        alerts = query.order_by(
            UsageAlert.created_at.desc()
        ).limit(limit).all()
        
        alerts_data = []
        for alert in alerts:
            alerts_data.append({
                "id": alert.id,
                "type": alert.alert_type,
                "threshold_percentage": alert.threshold_percentage,
                "provider": alert.provider.value if alert.provider else None,
                "title": alert.title,
                "message": alert.message,
                "severity": alert.severity,
                "is_sent": alert.is_sent,
                "sent_at": alert.sent_at.isoformat() if alert.sent_at else None,
                "is_read": alert.is_read,
                "read_at": alert.read_at.isoformat() if alert.read_at else None,
                "billing_period": alert.billing_period,
                "created_at": alert.created_at.isoformat()
            })
        
        return {
            "success": True,
            "data": {
                "alerts": alerts_data,
                "total": len(alerts_data),
                "unread_count": len([a for a in alerts_data if not a["is_read"]])
            }
        }
    
    except Exception as e:
        logger.error(f"Error getting usage alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/alerts/{alert_id}/mark-read")
async def mark_alert_read(
    alert_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Mark an alert as read."""
    
    try:
        alert = db.query(UsageAlert).filter(UsageAlert.id == alert_id).first()
        
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        alert.is_read = True
        alert.read_at = datetime.utcnow()
        db.commit()
        
        return {
            "success": True,
            "message": "Alert marked as read"
        }
    
    except Exception as e:
        logger.error(f"Error marking alert as read: {e}")
        raise HTTPException(status_code=500, detail=str(e))
