from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session

from ..database import SessionLocal
from .. import models, schemas
from ..routers.auth import get_current_user
from ..services.recommendation_service import RecommendationService, ProductRecommendation, SHGRecommendation
from core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class RecommendationType(str, Enum):
    products = "products"
    shgs = "shgs"
    all = "all"


class ProductRecommendationResponse(BaseModel):
    product_id: int
    product: schemas.ProductResponse
    score: float
    recommendation_type: str
    trust_weighted_score: float
    seller_trust_score: float

    class Config:
        from_attributes = True


class SimilarProductResponse(BaseModel):
    product_id: int
    product: schemas.ProductResponse
    similarity_score: float
    trust_weighted_score: float
    seller_trust_score: float

    class Config:
        from_attributes = True


class TrendingProductResponse(BaseModel):
    product_id: int
    product: schemas.ProductResponse
    score: float
    order_count: int
    trust_weighted_score: float
    seller_trust_score: float

    class Config:
        from_attributes = True


class SHGRecommendationResponse(BaseModel):
    shg_id: int
    shg: schemas.UserResponse
    score: float
    recommendation_reason: str
    trust_score: float

    class Config:
        from_attributes = True


class RecommendationExplanationFactor(BaseModel):
    type: str
    description: str
    weight: float


class RecommendationExplanationResponse(BaseModel):
    product_id: int
    user_id: int
    factors: List[RecommendationExplanationFactor]
    overall_score: float


def _product_to_response(product: models.Product) -> schemas.ProductResponse:
    return schemas.ProductResponse(
        id=product.id,
        name=product.name,
        description=product.description,
        category=product.category,
        subcategory=product.subcategory,
        price=product.price,
        stock=product.stock,
        min_order_quantity=product.min_order_quantity,
        unit=product.unit,
        images=product.images,
        thumbnail=product.thumbnail,
        status=product.status.value if hasattr(product.status, 'value') else str(product.status),
        is_featured=product.is_featured,
        tags=product.tags,
        quality_rating=product.quality_rating,
        total_reviews=product.total_reviews,
        trust_verified=product.trust_verified,
        seller_id=product.seller_id,
        created_at=product.created_at
    )


def _user_to_response(user: models.User) -> schemas.UserResponse:
    return schemas.UserResponse(
        id=user.id,
        phone=user.phone,
        name=user.name,
        email=user.email,
        role=user.role.value if hasattr(user.role, 'value') else str(user.role),
        hierarchy_level=user.hierarchy_level.value if user.hierarchy_level and hasattr(user.hierarchy_level, 'value') else str(user.hierarchy_level) if user.hierarchy_level else None,
        district=user.district,
        state=user.state.value if hasattr(user.state, 'value') else str(user.state),
        profile_image=user.profile_image,
        language_preference=user.language_preference,
        trust_score=user.trust_score,
        trust_coins=user.trust_coins,
        trust_badge=user.trust_badge,
        quality_score=user.quality_score,
        delivery_score=user.delivery_score,
        financial_score=user.financial_score,
        community_score=user.community_score,
        sustainability_score=user.sustainability_score,
        digital_score=user.digital_score,
        low_bandwidth_mode=user.low_bandwidth_mode,
        notification_enabled=user.notification_enabled,
        federation_id=user.federation_id,
        created_at=user.created_at
    )


def _run_async_recommendation(db: Session, coro):
    import asyncio
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
    
    DATABASE_URL = "sqlite+aiosqlite:///./ooumph.db"
    async_engine = create_async_engine(DATABASE_URL, echo=False)
    AsyncSessionLocal = async_sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)
    
    async def run():
        async with AsyncSessionLocal() as async_db:
            service = RecommendationService(async_db)
            return await coro(service)
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(run())
    finally:
        loop.close()


@router.get("/", response_model=List[ProductRecommendationResponse])
async def get_recommendations(
    limit: int = Query(10, ge=1, le=50, description="Maximum number of recommendations to return"),
    type: RecommendationType = Query(RecommendationType.all, description="Type of recommendations to fetch"),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get personalized recommendations for the current user.
    
    Supports three types:
    - products: Product recommendations only
    - shgs: SHG recommendations only  
    - all: Both products and SHGs
    """
    try:
        recommendations = _run_async_recommendation(
            db,
            lambda service: service.get_recommendations_for_user(current_user.id, limit)
        )
        
        response = []
        for rec in recommendations:
            product_response = _product_to_response(rec.product)
            response.append(ProductRecommendationResponse(
                product_id=rec.product_id,
                product=product_response,
                score=rec.score,
                recommendation_type=rec.recommendation_type,
                trust_weighted_score=rec.trust_weighted_score,
                seller_trust_score=rec.seller_trust_score
            ))
        
        return response
        
    except Exception as e:
        logger.error(f"Error getting recommendations for user {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get recommendations")


@router.get("/products/{product_id}/similar", response_model=List[SimilarProductResponse])
async def get_similar_products(
    product_id: int = Path(..., description="Product ID to find similar products for"),
    limit: int = Query(5, ge=1, le=20, description="Maximum number of similar products to return"),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get products similar to a specific product.
    
    Uses content-based similarity with trust weighting.
    """
    try:
        target_product = db.query(models.Product).filter(models.Product.id == product_id).first()
        if not target_product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        similar_products = _run_async_recommendation(
            db,
            lambda service: service.get_similar_products(product_id, limit)
        )
        
        response = []
        for rec in similar_products:
            product_response = _product_to_response(rec.product)
            response.append(SimilarProductResponse(
                product_id=rec.product_id,
                product=product_response,
                similarity_score=rec.score,
                trust_weighted_score=rec.trust_weighted_score,
                seller_trust_score=rec.seller_trust_score
            ))
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting similar products for product {product_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get similar products")


@router.get("/trending", response_model=List[TrendingProductResponse])
async def get_trending_products(
    district: Optional[str] = Query(None, description="Filter by district"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of trending products to return"),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get trending products based on recent order volume.
    
    Trending is determined by:
    - Recent order volume (last 30 days)
    - Product quality rating
    - Seller trust score
    """
    try:
        target_district = district or current_user.district
        
        if not target_district:
            raise HTTPException(
                status_code=400, 
                detail="District is required. Please specify in query params or update your profile."
            )
        
        trending = _run_async_recommendation(
            db,
            lambda service: service.get_trending_products(target_district, limit)
        )
        
        response = []
        for rec in trending:
            product_response = _product_to_response(rec.product)
            order_count = int(rec.score * 10)
            response.append(TrendingProductResponse(
                product_id=rec.product_id,
                product=product_response,
                score=rec.score,
                order_count=order_count,
                trust_weighted_score=rec.trust_weighted_score,
                seller_trust_score=rec.seller_trust_score
            ))
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting trending products: {e}")
        raise HTTPException(status_code=500, detail="Failed to get trending products")


@router.get("/shgs", response_model=List[SHGRecommendationResponse])
async def get_recommended_shgs(
    limit: int = Query(5, ge=1, le=20, description="Maximum number of SHG recommendations to return"),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get recommended SHGs for the current user to follow.
    
    Based on:
    - Similar users' followed SHGs
    - Category preferences matching SHG products
    - Trust scores
    """
    try:
        shg_recommendations = _run_async_recommendation(
            db,
            lambda service: service.get_recommended_shgs(current_user.id, limit)
        )
        
        response = []
        for rec in shg_recommendations:
            shg_response = _user_to_response(rec.shg)
            response.append(SHGRecommendationResponse(
                shg_id=rec.shg_id,
                shg=shg_response,
                score=rec.score,
                recommendation_reason=rec.recommendation_reason,
                trust_score=rec.trust_score
            ))
        
        return response
        
    except Exception as e:
        logger.error(f"Error getting SHG recommendations for user {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get SHG recommendations")


@router.get("/explain/{product_id}", response_model=RecommendationExplanationResponse)
async def explain_recommendation(
    product_id: int = Path(..., description="Product ID to explain recommendation for"),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get an explanation for why a product was recommended to the user.
    
    Returns factors including:
    - collaborative_filtering: Similar users purchased this
    - content_similarity: Similar to products you've purchased
    - category_preference: Matches your category preferences
    - trust_score: Seller trust score weighting
    """
    try:
        product = db.query(models.Product).filter(models.Product.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        explanation = _run_async_recommendation(
            db,
            lambda service: service.get_recommendation_explanation(current_user.id, product_id)
        )
        
        factors = [
            RecommendationExplanationFactor(
                type=factor["type"],
                description=factor["description"],
                weight=factor["weight"]
            )
            for factor in explanation.get("factors", [])
        ]
        
        return RecommendationExplanationResponse(
            product_id=explanation["product_id"],
            user_id=explanation["user_id"],
            factors=factors,
            overall_score=explanation["overall_score"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error explaining recommendation for product {product_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to explain recommendation")
