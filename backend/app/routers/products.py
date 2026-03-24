from fastapi import APIRouter, Depends, HTTPException, Form, File, UploadFile, Query
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload
from typing import List, Optional
from datetime import datetime
from ..database import SessionLocal
from .. import schemas
from ..routers.auth import get_current_user
from .. import models
from ..schema_types.pagination import PaginatedResponse, PaginationParams
from core.websocket import notify_product_created, notify_product_updated, notify_product_deleted, notify_inventory_updated

from core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============================================================================
# PRODUCT ENDPOINTS
# ============================================================================

@router.post("/", response_model=schemas.ProductResponse)
async def create_product(
    name: str = Form(...),
    description: Optional[str] = Form(None),
    category: str = Form(...),
    price: float = Form(...),
    quantity: int = Form(...),  # Maps to stock
    unit: str = Form("piece"),
    district: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new product with image upload support"""
    # Handle image upload if present
    image_url = None
    if image:
        # In production, upload to cloud storage and get URL
        # For now, just store the filename
        image_url = f"/uploads/products/{image.filename}"

    new_product = models.Product(
        name=name,
        description=description,
        category=category,
        subcategory=None,
        price=price,
        stock=quantity,  # quantity maps to stock
        min_order_quantity=1,
        unit=unit,
        images=[image_url] if image_url else [],
        tags=[],
        seller_id=current_user.id,
        status=models.ProductStatus.ACTIVE
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    
    await notify_product_created(
        new_product.id,
        current_user.id,
        {
            "name": new_product.name,
            "category": new_product.category,
            "price": float(new_product.price),
            "stock": new_product.stock,
            "unit": new_product.unit
        }
    )
    logger.info(f"Product created: {new_product.id} by user {current_user.id}")
    
    return new_product

@router.get("/", response_model=PaginatedResponse[schemas.ProductResponse])
async def get_products(
    category: Optional[str] = None,
    status: str = "Active",
    pagination: PaginationParams = Depends(),
    db: Session = Depends(get_db)
):
    """
    Get all products with pagination.

    - **category**: Filter by product category
    - **status**: Filter by product status (Active, Sold Out, Draft, Inactive)
    - **page**: Page number (starts from 1)
    - **page_size**: Number of items per page (max 100)

    Returns paginated list of products with seller information eagerly loaded.
    """
    # Build query with filters
    query = db.query(models.Product)

    if category:
        query = query.filter(models.Product.category == category)

    if status:
        query = query.filter(models.Product.status == status)

    # Get total count before pagination
    total = query.count()

    # Apply pagination
    offset = (pagination.page - 1) * pagination.page_size
    products = query.options(
        joinedload(models.Product.seller)  # Eager load seller to avoid N+1 queries
    ).order_by(
        models.Product.created_at.desc()
    ).offset(offset).limit(pagination.page_size).all()

    # Calculate total pages
    total_pages = (total + pagination.page_size - 1) // pagination.page_size

    return PaginatedResponse(
        items=products,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=total_pages
    )

@router.get("/{product_id}", response_model=schemas.ProductResponse)
async def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    """Get specific product details with seller information"""
    product = db.query(models.Product).options(
        joinedload(models.Product.seller)  # Eager load seller to avoid N+1 queries
    ).filter(models.Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return product

@router.put("/{product_id}", response_model=schemas.ProductResponse)
async def update_product(
    product_id: int,
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    price: Optional[float] = Form(None),
    quantity: Optional[int] = Form(None),
    unit: Optional[str] = Form(None),
    district: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a product with optional image upload"""
    product = db.query(models.Product).filter(
        models.Product.id == product_id
    ).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Verify ownership
    if product.seller_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Update fields if provided
    if name is not None:
        product.name = name
    if description is not None:
        product.description = description
    if category is not None:
        product.category = category
    if price is not None:
        product.price = price
    if quantity is not None:
        product.stock = quantity
    if unit is not None:
        product.unit = unit
    if district is not None:
        product.district = district

    # Handle image upload if present
    if image:
        image_url = f"/uploads/products/{image.filename}"
        product.images = [image_url]

    product.updated_at = datetime.now()
    db.commit()
    db.refresh(product)

    
    await notify_product_updated(
        product.id,
        current_user.id,
        {
            "name": product.name,
            "category": product.category,
            "price": float(product.price),
            "stock": product.stock,
            "changes": {
                "name": name,
                "category": category,
                "price": price,
                "stock": quantity,
                "unit": unit,
                "district": district
            }
        }
    )
    
    logger.info(f"Product updated: {product.id} by user {current_user.id}")
    
    return product

@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a product"""
    product = db.query(models.Product).filter(
        models.Product.id == product_id
    ).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Verify ownership
    if product.seller_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    db.delete(product)
    db.commit()
    
    await notify_product_deleted(
        product.id,
        current_user.id,
        {"name": product.name, "category": product.category}
    )
    
    return {"message": "Product deleted successfully"}

@router.get("/my/products", response_model=List[schemas.ProductResponse])
async def get_my_products(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's products"""
    products = db.query(models.Product).filter(
        models.Product.seller_id == current_user.id
    ).order_by(models.Product.created_at.desc()).all()

    return products
