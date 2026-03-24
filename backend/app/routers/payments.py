from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import SessionLocal
from .. import schemas
from ..routers.auth import get_current_user
from .. import models
from ..services import payment_service
import uuid
from datetime import timedelta

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============================================================================
# PAYMENT ENDPOINTS
# ============================================================================

@router.post("/initiate")
async def initiate_payment(
    order_id: int,
    use_coins: bool = False,
    coins_to_use: int = 0,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Initiate payment for an order"""
    order = db.query(models.Order).filter(
        models.Order.id == order_id
    ).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.buyer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    result = await payment_service.initiate_payment(
        order_id,
        current_user.id,
        order.final_amount,
        order.payment_method or "UPI",
        use_coins,
        coins_to_use,
        db
    )

    return result

@router.get("/status/{payment_id}")
async def get_payment_status(
    payment_id: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check payment status"""
    status = await payment_service.check_payment_status(payment_id, db)
    return status

@router.post("/callback/{payment_id}")
async def payment_callback(
    payment_id: str,
    status: str,
    transaction_id: str = None,
    db: Session = Depends(get_db)
):
    """Process payment gateway callback (webhook)"""
    result = await payment_service.process_payment_callback(
        payment_id, status, transaction_id, db
    )
    return result

@router.get("/qr/{payment_id}")
async def get_payment_qr(payment_id: str):
    """Get payment QR code"""
    qr_url = await payment_service.get_payment_qr_code(payment_id)
    return {"qr_url": qr_url}

@router.get("/methods")
async def get_payment_methods(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get available payment methods"""
    methods = await payment_service.get_payment_methods(current_user.id, db)
    return methods

@router.post("/calculate")
async def calculate_payment_breakdown(
    order_id: int,
    use_coins: bool = False,
    coins_to_use: int = 0,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Calculate payment breakdown"""
    breakdown = await payment_service.calculate_payment_breakdown(
        order_id, use_coins, coins_to_use, db
    )
    return breakdown

@router.post("/refund/{order_id}")
async def refund_payment(
    order_id: int,
    reason: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Process refund for an order"""
    try:
        result = await payment_service.refund_payment(order_id, reason, db)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# ============================================================================
# LEGACY ENDPOINTS (Mock)
# ============================================================================

@router.post("/process_upi")
def process_upi_payment(amount: float, vpa: str):
    """Mock UPI payment processing endpoint (legacy)"""
    mock_txn_id = f"UPI_{uuid.uuid4().hex[:12].upper()}"
    return {
        "status": "SUCCESS",
        "txn_id": mock_txn_id,
        "amount_processed": amount,
        "vpa": vpa,
        "message": "Payment verified via Mock UPI Gateway"
    }

@router.post("/process_gateway")
def process_gateway_payment(amount: float, card_type: str = "DEBIT"):
    """Mock standard payment gateway (legacy)"""
    mock_txn_id = f"PG_{uuid.uuid4().hex[:12].upper()}"
    return {
        "status": "SUCCESS",
        "txn_id": mock_txn_id,
        "amount_processed": amount,
        "message": "Payment verified via Mock Payment Gateway"
    }
