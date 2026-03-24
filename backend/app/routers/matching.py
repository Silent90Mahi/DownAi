from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import SessionLocal
from .. import schemas
from ..routers.auth import get_current_user
from .. import models
from ..services import matching_service

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============================================================================
# BUYER MATCHING ENDPOINTS (Agent Jodi)
# ============================================================================

@router.post("/buyers", response_model=list[schemas.BuyerMatchResponse])
async def find_buyers(
    request: schemas.BuyerMatchRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Find matching buyers for a product"""
    matches = await matching_service.find_buyers_for_product(
        request.product_id,
        request.quantity,
        request.price,
        request.district,
        current_user.trust_score,
        db
    )

    return matches

@router.get("/requirements", response_model=list[schemas.BuyerRequirementResponse])
async def get_buyer_requirements(
    category: str = None,
    district: str = None,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get buyer requirements"""
    requirements = await matching_service.get_buyer_requirements(
        category,
        district,
        db
    )

    return [
        schemas.BuyerRequirementResponse(
            id=r["id"],
            buyer_id=r.get("buyer_id", 0),
            title=r["title"],
            description=r["description"],
            category=r["category"],
            quantity=r["quantity"],
            unit=r["unit"],
            budget_range_min=r.get("budget_range_min"),
            budget_range_max=r.get("budget_range_max"),
            required_by=datetime.fromisoformat(r["required_by"]) if r.get("required_by") else None,
            status=r["status"],
            created_at=datetime.now()
        )
        for r in requirements
    ]

@router.post("/negotiate")
async def simulate_negotiation(
    buyer_id: int,
    product_id: int,
    initial_price: float,
    quantity: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Simulate price negotiation"""
    result = await matching_service.simulate_negotiation(
        buyer_id,
        current_user.id,
        product_id,
        initial_price,
        quantity,
        db
    )

    return result

@router.get("/gem-opportunities")
async def get_gem_opportunities(
    category: str = None,
    district: str = None,
    current_user: models.User = Depends(get_current_user)
):
    """Get GeM (Government e-Marketplace) opportunities"""
    opportunities = await matching_service.get_gem_opportunities(category, district)
    return opportunities

@router.get("/ondc-status")
async def get_ondc_status(
    current_user: models.User = Depends(get_current_user)
):
    """Get ONDC catalog sync status"""
    status = await matching_service.get_ondc_catalog_sync()
    return status
