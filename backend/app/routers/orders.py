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
    query = db.query(models.Order).filter(
        (models.Order.buyer_id == current_user.id) |
        (models.Order.seller_id == current_user.id)
    )

    if status:
        query = query.filter(models.Order.order_status == status)

    total = query.count()

    if total == 0:
        mock_orders = create_mock_orders(current_user.id)
        return PaginatedResponse(
            items=mock_orders,
            total=len(mock_orders),
            page=1,
            page_size=20,
            total_pages=1
        )

    offset = (pagination.page - 1) * pagination.page_size
    orders = query.options(
        joinedload(models.Order.buyer),
        joinedload(models.Order.seller),
        selectinload(models.Order.items)
    ).order_by(
        models.Order.created_at.desc()
    ).offset(offset).limit(pagination.page_size).all()

    total_pages = (total + pagination.page_size - 1) // pagination.page_size

    return PaginatedResponse(
        items=orders,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=total_pages
    )


def create_mock_orders(user_id: int):
    """Create mock orders for demo when no real orders exist"""
    from datetime import datetime, timedelta
    import random
    
    mock_data = [
        {
            "id": 1,
            "order_number": "ORD20250326001",
            "buyer_id": user_id,
            "seller_id": 999,
            "total_amount": 2500.00,
            "discount_amount": 250.00,
            "tax_amount": 0.0,
            "final_amount": 2250.00,
            "order_status": "Delivered",
            "payment_status": "Paid",
            "payment_method": "UPI",
            "coins_used": 0,
            "delivery_name": "Demo User",
            "delivery_phone": "9876543210",
            "delivery_address": "123 Main Street",
            "delivery_city": "Hyderabad",
            "delivery_district": "Hyderabad",
            "delivery_pincode": "500001",
            "tracking_number": "TRK123456",
            "created_at": datetime.now() - timedelta(days=10),
            "items": [
                {"product_name": "Organic Turmeric Powder", "quantity": 5, "unit_price": 450, "total_price": 2250}
            ]
        },
        {
            "id": 2,
            "order_number": "ORD20250324002",
            "buyer_id": user_id,
            "seller_id": 998,
            "total_amount": 1800.00,
            "discount_amount": 0.0,
            "tax_amount": 0.0,
            "final_amount": 1800.00,
            "order_status": "Shipped",
            "payment_status": "Paid",
            "payment_method": "Trust Coins",
            "coins_used": 100,
            "delivery_name": "Demo User",
            "delivery_phone": "9876543210",
            "delivery_address": "456 Park Avenue",
            "delivery_city": "Guntur",
            "delivery_district": "Guntur",
            "delivery_pincode": "522001",
            "tracking_number": "TRK789012",
            "created_at": datetime.now() - timedelta(days=3),
            "items": [
                {"product_name": "Handwoven Cotton Saree", "quantity": 1, "unit_price": 1500, "total_price": 1500},
                {"product_name": "Matching Blouse Piece", "quantity": 1, "unit_price": 300, "total_price": 300}
            ]
        },
        {
            "id": 3,
            "order_number": "ORD20250325003",
            "buyer_id": user_id,
            "seller_id": 997,
            "total_amount": 750.00,
            "discount_amount": 0.0,
            "tax_amount": 0.0,
            "final_amount": 750.00,
            "order_status": "Processing",
            "payment_status": "Paid",
            "payment_method": "COD",
            "coins_used": 0,
            "delivery_name": "Demo User",
            "delivery_phone": "9876543210",
            "delivery_address": "789 Market Road",
            "delivery_city": "Vijayawada",
            "delivery_district": "Krishna",
            "delivery_pincode": "520001",
            "tracking_number": None,
            "created_at": datetime.now() - timedelta(days=1),
            "items": [
                {"product_name": "Bamboo Basket Set", "quantity": 3, "unit_price": 250, "total_price": 750}
            ]
        },
        {
            "id": 4,
            "order_number": "ORD20250326004",
            "buyer_id": user_id,
            "seller_id": 996,
            "total_amount": 3200.00,
            "discount_amount": 320.00,
            "tax_amount": 0.0,
            "final_amount": 2880.00,
            "order_status": "Placed",
            "payment_status": "Pending",
            "payment_method": "UPI",
            "coins_used": 0,
            "delivery_name": "Demo User",
            "delivery_phone": "9876543210",
            "delivery_address": "321 Green Colony",
            "delivery_city": "Kurnool",
            "delivery_district": "Kurnool",
            "delivery_pincode": "518001",
            "tracking_number": None,
            "created_at": datetime.now() - timedelta(hours=5),
            "items": [
                {"product_name": "Pure Honey (500ml)", "quantity": 4, "unit_price": 800, "total_price": 3200}
            ]
        },
        {
            "id": 5,
            "order_number": "ORD20250320005",
            "buyer_id": user_id,
            "seller_id": 995,
            "total_amount": 950.00,
            "discount_amount": 0.0,
            "tax_amount": 0.0,
            "final_amount": 950.00,
            "order_status": "Cancelled",
            "payment_status": "Refunded",
            "payment_method": "UPI",
            "coins_used": 0,
            "delivery_name": "Demo User",
            "delivery_phone": "9876543210",
            "delivery_address": "555 Lake View",
            "delivery_city": "Rajahmundry",
            "delivery_district": "East Godavari",
            "delivery_pincode": "533101",
            "tracking_number": None,
            "created_at": datetime.now() - timedelta(days=6),
            "items": [
                {"product_name": "Jute Shopping Bag", "quantity": 5, "unit_price": 190, "total_price": 950}
            ]
        }
    ]
    
    orders = []
    for data in mock_data:
        order = models.Order(
            id=data["id"],
            order_number=data["order_number"],
            buyer_id=data["buyer_id"],
            seller_id=data["seller_id"],
            total_amount=data["total_amount"],
            discount_amount=data["discount_amount"],
            tax_amount=data["tax_amount"],
            final_amount=data["final_amount"],
            order_status=data["order_status"],
            payment_status=data["payment_status"],
            payment_method=data["payment_method"],
            coins_used=data["coins_used"],
            delivery_name=data["delivery_name"],
            delivery_phone=data["delivery_phone"],
            delivery_address=data["delivery_address"],
            delivery_city=data["delivery_city"],
            delivery_district=data["delivery_district"],
            delivery_pincode=data["delivery_pincode"],
            tracking_number=data["tracking_number"],
            created_at=data["created_at"]
        )
        
        for idx, item_data in enumerate(data["items"], start=1):
            item = models.OrderItem(
                id=idx,
                order_id=data["id"],
                product_name=item_data["product_name"],
                quantity=item_data["quantity"],
                unit_price=item_data["unit_price"],
                total_price=item_data["total_price"]
            )
            order.items.append(item)
        
        orders.append(order)
    
    return orders

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
