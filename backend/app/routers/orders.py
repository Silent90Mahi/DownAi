from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload, selectinload
from typing import Optional
from ..database import SessionLocal
from .. import schemas
from ..routers.auth import get_current_user
from .. import models
from ..schema_types.pagination import PaginatedResponse, PaginationParams
from datetime import datetime, timedelta

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============================================================================
# ORDER ENDPOINTS
# ============================================================================

def generate_order_number():
    """Generate unique order number"""
    return f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}"

@router.post("/", response_model=schemas.OrderResponse)
async def create_order(
    order: schemas.OrderCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new order"""
    # Get first product to determine seller
    first_product = db.query(models.Product).filter(
        models.Product.id == order.items[0].product_id
    ).first()

    if not first_product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Calculate total
    total_amount = 0
    for item in order.items:
        product = db.query(models.Product).filter(
            models.Product.id == item.product_id
        ).first()
        if product:
            total_amount += product.price * item.quantity

    # Create order
    new_order = models.Order(
        order_number=generate_order_number(),
        buyer_id=current_user.id,
        seller_id=first_product.seller_id,
        total_amount=total_amount,
        discount_amount=0.0,
        tax_amount=0.0,
        final_amount=total_amount,
        order_status=models.OrderStatus.PLACED,
        payment_status=models.PaymentStatus.PENDING,
        payment_method=order.payment_method,
        coins_used=order.coins_used,
        delivery_name=order.delivery_name,
        delivery_phone=order.delivery_phone,
        delivery_address=order.delivery_address,
        delivery_city=order.delivery_city,
        delivery_district=order.delivery_district,
        delivery_pincode=order.delivery_pincode,
        delivery_notes=order.delivery_notes,
        expected_delivery=datetime.now() + timedelta(days=7)
    )

    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    # Add order items
    for item in order.items:
        product = db.query(models.Product).filter(
            models.Product.id == item.product_id
        ).first()

        order_item = models.OrderItem(
            order_id=new_order.id,
            product_id=item.product_id,
            product_name=product.name if product else "Unknown",
            quantity=item.quantity,
            unit_price=product.price if product else 0,
            total_price=(product.price * item.quantity) if product else 0
        )
        db.add(order_item)

    db.commit()

    return new_order

@router.get("/", response_model=PaginatedResponse[schemas.OrderResponse])
async def get_orders(
    status: Optional[str] = None,
    pagination: PaginationParams = Depends(),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's orders with pagination.

    - **status**: Filter by order status
    - **page**: Page number (starts from 1)
    - **page_size**: Number of items per page (max 100)

    Returns paginated list of orders with buyer and seller information eagerly loaded.
    """
    # Build query with filters
    query = db.query(models.Order).filter(
        (models.Order.buyer_id == current_user.id) |
        (models.Order.seller_id == current_user.id)
    )

    if status:
        query = query.filter(models.Order.order_status == status)

    # Get total count before pagination
    total = query.count()

    # Apply pagination with eager loading to avoid N+1 queries
    offset = (pagination.page - 1) * pagination.page_size
    orders = query.options(
        joinedload(models.Order.buyer),
        joinedload(models.Order.seller),
        selectinload(models.Order.items)  # Eager load order items
    ).order_by(
        models.Order.created_at.desc()
    ).offset(offset).limit(pagination.page_size).all()

    # Calculate total pages
    total_pages = (total + pagination.page_size - 1) // pagination.page_size

    return PaginatedResponse(
        items=orders,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=total_pages
    )

@router.get("/{order_id}", response_model=schemas.OrderResponse)
async def get_order(
    order_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific order details with all relationships eagerly loaded"""
    order = db.query(models.Order).options(
        joinedload(models.Order.buyer),
        joinedload(models.Order.seller),
        selectinload(models.Order.items)  # Eager load order items
    ).filter(models.Order.id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Verify access
    if order.buyer_id != current_user.id and order.seller_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    return order

@router.patch("/{order_id}/status")
async def update_order_status(
    order_id: int,
    status: str,
    tracking_number: str = None,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update order status (seller only)"""
    order = db.query(models.Order).filter(models.Order.id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.seller_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only seller can update status")

    order.order_status = models.OrderStatus(status)

    if tracking_number:
        order.tracking_number = tracking_number

    if status == "Shipped":
        order.shipped_at = datetime.now()
    elif status == "Delivered":
        order.delivered_at = datetime.now()

    db.commit()

    return {"message": "Order status updated", "order_id": order_id, "status": status}
