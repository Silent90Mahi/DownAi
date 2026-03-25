from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import random
from ..database import SessionLocal
from .. import schemas, models
from ..routers.auth import get_current_user
from ..services import supplier_service

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============================================================================
# SUPPLIER/MATERIAL ENDPOINTS (Agent Samagri)
# ============================================================================

@router.get("/search", response_model=list[schemas.MaterialResponse])
async def search_materials(
    query: str,
    category: str = None,
    district: str = None,
    min_price: float = None,
    max_price: float = None,
    is_organic: bool = None,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Search for raw materials"""
    materials = await supplier_service.search_materials(
        query, category, district, min_price, max_price, is_organic, db
    )

    return [
        schemas.MaterialResponse(
            id=m["id"],
            name=m["name"],
            description=m.get("description"),
            category=m["category"],
            subcategory=m.get("subcategory"),
            price_per_unit=m["price_per_unit"],
            unit=m["unit"],
            min_order_quantity=m["min_order_quantity"],
            bulk_discount_available=m["bulk_discount_available"],
            bulk_discount_percentage=m["bulk_discount_percentage"],
            stock_available=m["stock_available"],
            is_available=m["is_available"],
            quality_grade=m.get("quality_grade"),
            is_organic=m["is_organic"],
            certifications=m.get("certifications"),
            district=m["district"],
            images=m.get("images"),
            supplier=schemas.SupplierResponse(
                id=m["supplier"]["id"],
                business_name=m["supplier"]["business_name"],
                district=m["supplier"]["district"],
                rating=m["supplier"]["rating"],
                trust_score=m["supplier"]["trust_score"],
                total_reviews=m["supplier"]["total_reviews"],
                is_verified=m["supplier"]["is_verified"],
                categories_supplied=m["supplier"]["categories_supplied"],
                service_areas=m["supplier"]["service_areas"]
            )
        )
        for m in materials
    ]

@router.get("/supplier/{supplier_id}", response_model=schemas.SupplierProfileResponse)
async def get_supplier_profile(
    supplier_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get supplier details with reviews and materials"""
    supplier = await supplier_service.get_supplier_profile(supplier_id, current_user.id, db)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return supplier

@router.get("/list")
async def list_suppliers(
    district: str = None,
    category: str = None,
    min_rating: float = None,
    verified_only: bool = False,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all suppliers with filters"""
    suppliers = await supplier_service.list_suppliers(district, category, min_rating, verified_only, db)
    return suppliers

# ============================================================================
# SUPPLIER REVIEWS
# ============================================================================

@router.get("/supplier/{supplier_id}/reviews", response_model=list[schemas.SupplierReviewResponse])
async def get_supplier_reviews(
    supplier_id: int,
    limit: int = 10,
    offset: int = 0,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get reviews for a supplier"""
    reviews = await supplier_service.get_supplier_reviews(supplier_id, limit, offset, db)
    return reviews

@router.post("/reviews", response_model=schemas.SupplierReviewResponse)
async def create_supplier_review(
    review: schemas.SupplierReviewCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a review for a supplier"""
    result = await supplier_service.create_supplier_review(
        current_user.id, review, db
    )
    if not result:
        raise HTTPException(status_code=400, detail="Unable to create review")
    return result

@router.post("/reviews/{review_id}/helpful")
async def mark_review_helpful(
    review_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a review as helpful"""
    result = await supplier_service.mark_review_helpful(review_id, db)
    return {"success": result}

# ============================================================================
# SUPPLIER CONNECTIONS
# ============================================================================

@router.post("/connect", response_model=schemas.SupplierConnectionResponse)
async def connect_with_supplier(
    connection: schemas.SupplierConnectionCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a connection request to a supplier"""
    result = await supplier_service.create_connection_request(
        current_user.id, connection.supplier_id, connection.message, db
    )
    if not result:
        raise HTTPException(status_code=400, detail="Connection request already exists or invalid")
    return result

@router.get("/connections", response_model=list[schemas.SupplierConnectionResponse])
async def get_my_connections(
    status: str = None,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's supplier connections"""
    connections = await supplier_service.get_user_connections(current_user.id, status, db)
    return connections

@router.post("/connections/{connection_id}/accept")
async def accept_connection(
    connection_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Accept a connection request"""
    result = await supplier_service.respond_to_connection(connection_id, "accepted", db)
    return {"success": result, "message": "Connection accepted"}

@router.post("/connections/{connection_id}/reject")
async def reject_connection(
    connection_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reject a connection request"""
    result = await supplier_service.respond_to_connection(connection_id, "rejected", db)
    return {"success": result, "message": "Connection rejected"}

# ============================================================================
# QUOTE REQUESTS
# ============================================================================

@router.post("/quotes", response_model=schemas.QuoteRequestResponse)
async def request_quote(
    quote: schemas.QuoteRequestCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Request a quote from a supplier"""
    result = await supplier_service.create_quote_request(current_user.id, quote, db)
    if not result:
        raise HTTPException(status_code=400, detail="Unable to create quote request")
    return result

@router.get("/quotes", response_model=list[schemas.QuoteRequestResponse])
async def get_my_quotes(
    status: str = None,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's quote requests"""
    quotes = await supplier_service.get_user_quotes(current_user.id, status, db)
    return quotes

@router.post("/quotes/{quote_id}/accept")
async def accept_quote(
    quote_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Accept a quoted price"""
    result = await supplier_service.respond_to_quote(quote_id, "accepted", db)
    return {"success": result, "message": "Quote accepted"}

@router.post("/quotes/{quote_id}/reject")
async def reject_quote(
    quote_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reject a quoted price"""
    result = await supplier_service.respond_to_quote(quote_id, "rejected", db)
    return {"success": result, "message": "Quote rejected"}

# ============================================================================
# BULK REQUESTS
# ============================================================================

@router.post("/bulk-request")
async def create_bulk_request(
    request: schemas.BulkRequestCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a bulk purchase request"""
    result = await supplier_service.create_bulk_request(
        current_user.id,
        request.title,
        request.description,
        request.materials,
        request.target_quantity,
        request.district,
        request.serving_districts,
        request.expires_in_days,
        db
    )
    return result

@router.post("/bulk-request/{request_id}/join")
async def join_bulk_request(
    request_id: int,
    quantity: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Join an existing bulk request"""
    result = await supplier_service.join_bulk_request(
        request_id, current_user.id, quantity, db
    )
    return result

@router.get("/bulk-requests")
async def get_bulk_requests(
    district: str = None,
    status: str = "Open",
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of bulk requests"""
    requests = await supplier_service.get_bulk_requests_list(district, status, db)
    return requests

@router.get("/price-trends/{material_name}")
async def get_price_trends(
    material_name: str,
    district: str,
    months: int = 6,
    current_user: models.User = Depends(get_current_user)
):
    """Get price trends for a material"""
    trends = await supplier_service.get_price_trends(material_name, district, months)
    return trends
