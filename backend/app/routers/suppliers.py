from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import SessionLocal
from .. import schemas
from ..routers.auth import get_current_user
from .. import models
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
            supplier=m["supplier"]
        )
        for m in materials
    ]

@router.get("/supplier/{supplier_id}", response_model=schemas.SupplierResponse)
async def get_supplier(
    supplier_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get supplier details"""
    supplier = await supplier_service.get_supplier_by_id(supplier_id, db)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return supplier

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
