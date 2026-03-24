from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import SessionLocal
from .. import schemas
from ..routers.auth import get_current_user
from .. import models
from ..services import analytics_service

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============================================================================
# ANALYTICS ENDPOINTS
# ============================================================================

@router.get("/dashboard", response_model=schemas.DashboardStatsResponse)
async def get_dashboard_stats(
    district: str = None,
    federation_id: int = None,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get dashboard statistics"""
    # Non-admins can only see their own stats
    if current_user.role.value not in ["Admin", "DPD"]:
        district = current_user.district

    stats = await analytics_service.get_dashboard_stats(district, federation_id, db)
    return stats

@router.get("/hierarchy_stats")
async def get_hierarchy_stats(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get hierarchy statistics (legacy endpoint)"""
    total_users = db.query(models.User).count()
    avg_trust = db.query(models.User.trust_score).all()
    avg_trust_val = sum(t for t in avg_trust) / len(avg_trust) if avg_trust else 0

    return {
        "viewer_role": current_user.role.value,
        "viewer_level": current_user.hierarchy_level.value if current_user.hierarchy_level else None,
        "total_ecosystem_shgs": total_users,
        "ecosystem_average_trust": round(avg_trust_val, 2)
    }

@router.get("/districts", response_model=list[schemas.DistrictStatsResponse])
async def get_district_stats(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get statistics by district"""
    stats = await analytics_service.get_district_stats(db)

    return [
        schemas.DistrictStatsResponse(
            district=s["district"],
            total_users=s["total_users"],
            total_products=s["total_products"],
            total_orders=s["total_orders"],
            total_revenue=s["total_revenue"],
            avg_trust_score=s["avg_trust_score"]
        )
        for s in stats
    ]

@router.get("/user/{user_id}", response_model=schemas.UserAnalyticsResponse)
async def get_user_analytics(
    user_id: int,
    period_months: int = 6,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get analytics for a specific user"""
    # Users can only see their own analytics unless admin
    if current_user.id != user_id and current_user.role.value not in ["Admin", "DPD"]:
        raise HTTPException(status_code=403, detail="Access denied")

    analytics = await analytics_service.get_user_analytics(user_id, period_months, db)

    return schemas.UserAnalyticsResponse(
        user_id=user_id,
        total_products=analytics["products"]["total"],
        total_orders_sold=analytics["sales"]["total_orders"],
        total_orders_bought=analytics["purchases"]["total_orders"],
        total_revenue=analytics["sales"]["total_revenue"],
        total_purchases=analytics["purchases"]["total_amount"],
        trust_score=analytics["trust_score"],
        trust_coins=analytics["trust_coins"],
        completion_rate=analytics["sales"]["completion_rate"],
        avg_rating=analytics["avg_rating"]
    )

@router.get("/top-performers")
async def get_top_performers(
    limit: int = 20,
    district: str = None,
    period: str = "month",
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get top performing SHGs"""
    performers = await analytics_service.get_top_performers(limit, district, period, db)
    return performers

@router.get("/categories")
async def get_category_analytics(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get analytics by product category"""
    analytics = await analytics_service.get_category_analytics(db)
    return analytics

@router.get("/trust-distribution")
async def get_trust_distribution(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get trust score distribution"""
    distribution = await analytics_service.get_trust_distribution(db)
    return distribution
