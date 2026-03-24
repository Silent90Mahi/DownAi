from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import SessionLocal
from .. import schemas
from ..routers.auth import get_current_user
from .. import models
from ..services import notification_service

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============================================================================
# NOTIFICATION ENDPOINTS
# ============================================================================

@router.get("/", response_model=list[schemas.NotificationResponse])
async def get_notifications(
    unread_only: bool = False,
    limit: int = 50,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's notifications"""
    notifications = await notification_service.get_user_notifications(
        current_user.id, unread_only, limit, db
    )

    return [
        schemas.NotificationResponse(
            id=n["id"],
            title=n["title"],
            message=n["message"],
            notification_type=n["notification_type"],
            reference_type=n.get("reference_type"),
            reference_id=n.get("reference_id"),
            is_read=n["is_read"],
            action_url=n.get("action_url"),
            action_label=n.get("action_label"),
            created_at=datetime.fromisoformat(n["created_at"])
        )
        for n in notifications
    ]

@router.get("/unread-count")
async def get_unread_count(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get count of unread notifications"""
    count = await notification_service.get_unread_count(current_user.id, db)
    return {"count": count}

@router.put("/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark notification as read"""
    result = await notification_service.mark_notification_read(
        notification_id, current_user.id, db
    )
    return result

@router.put("/read-all")
async def mark_all_read(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark all notifications as read"""
    result = await notification_service.mark_all_read(current_user.id, db)
    return result

@router.delete("/old")
async def delete_old_notifications(
    days_old: int = 90,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete notifications older than specified days"""
    result = await notification_service.delete_old_notifications(days_old, db)
    return result
