from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import SessionLocal
from .. import schemas
from ..routers.auth import get_current_user
from .. import models
from ..services import market_service

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============================================================================
# MARKET INTELLIGENCE ENDPOINTS (Agent Bazaar Buddhi)
# ============================================================================

@router.post("/analyze", response_model=schemas.MarketAnalysisResponse)
async def analyze_market(
    request: schemas.MarketAnalysisRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analyze market for a product"""
    analysis = await market_service.analyze_market(
        request.product_name,
        request.category,
        request.district,
        request.price,
        db
    )

    return analysis

@router.post("/price-suggestion", response_model=schemas.PriceSuggestionResponse)
async def get_price_suggestion(
    request: schemas.PriceSuggestionRequest,
    current_user: models.User = Depends(get_current_user)
):
    """Get price recommendation"""
    suggestion = await market_service.get_price_suggestion(
        request.product_name,
        request.category,
        request.quality,
        request.district,
        request.cost_price
    )

    return suggestion

@router.get("/trends")
async def get_market_trends(
    category: str = None,
    district: str = None,
    current_user: models.User = Depends(get_current_user)
):
    """Get market trends"""
    trends = await market_service.get_market_trends(category, district)
    return trends
