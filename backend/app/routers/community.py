from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import SessionLocal
from .. import schemas
from ..routers.auth import get_current_user
from .. import models
from ..services import community_service

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============================================================================
# COMMUNITY ENDPOINTS (Agent Sampark)
# ============================================================================

@router.get("/hierarchy")
async def get_hierarchy_overview(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get hierarchy overview for current user"""
    overview = await community_service.get_hierarchy_overview(current_user.id, db)
    return overview

@router.get("/federation/{federation_id}/members")
async def get_federation_members(
    federation_id: int,
    federation_level: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get members of a federation"""
    members = await community_service.get_federation_members(
        federation_id, federation_level, True, db
    )
    return members

@router.get("/federation/{federation_id}/stats")
async def get_federation_stats(
    federation_id: int,
    federation_level: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get federation statistics"""
    stats = await community_service.get_federation_stats(
        federation_id, federation_level, db
    )
    return stats

@router.post("/alert")
async def send_community_alert(
    title: str,
    message: str,
    target_level: str,
    district: str = None,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send alert to community members"""
    result = await community_service.send_community_alert(
        current_user.id, title, message, target_level, district, db
    )
    return result

@router.get("/district/{district}")
async def get_district_overview(
    district: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get district overview"""
    overview = await community_service.get_district_overview(district, db)
    return overview

@router.post("/escalate")
async def escalate_to_leadership(
    issue_type: str,
    issue_details: str,
    urgency: str = "medium",
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Escalate issue to federation leadership"""
    result = await community_service.escalate_to_Leadership(
        current_user.id, issue_type, issue_details, urgency, db
    )
    return result

@router.get("/announcements")
async def get_announcements(
    district: str = None,
    limit: int = 10,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get community announcements"""
    announcements = await community_service.get_community_announcements(
        district, limit, db
    )
    return announcements

@router.get("/federation/{federation_id}/performance")
async def get_federation_performance(
    federation_id: int,
    period_months: int = 6,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get federation performance metrics"""
    performance = await community_service.get_federation_performances(
        federation_id, period_months, db
    )
    return performance
