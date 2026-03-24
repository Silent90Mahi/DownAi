"""
Payment Service
Handles mock payment processing for UPI, Trust Coins, etc.
"""
import os
import random
import string
from datetime import datetime, timedelta
from typing import Dict, Optional
from sqlalchemy.orm import Session
from .. import models

async def initiate_payment(order_id: int,
                         user_id: int,
                         amount: float,
                         payment_method: str = "UPI",
                         use_coins: bool = False,
                         coins_to_use: int = 0,
                         db: Session = None) -> Dict:
    """
    Initiate payment for an order

    Args:
        order_id: Order ID
        user_id: User ID making payment
        amount: Payment amount
        payment_method: Payment method (UPI, Trust_Coins, Mixed)
        use_coins: Whether to use coins
        coins_to_use: Number of coins to use
        db: Database session

    Returns:
        Payment initiation response
    """
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise ValueError("Order not found")

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise ValueError("User not found")

    # Generate payment ID
    payment_id = f"PAY{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(1000, 9999)}"

    # Calculate final amount
    final_amount = amount

    # Process coin deduction
    coins_used = 0
    if use_coins and coins_to_use > 0:
        # Each coin = ₹1
        if user.trust_coins < coins_to_use:
            raise ValueError(f"Insufficient coins. Available: {user.trust_coins}, Requested: {coins_to_use}")

        coins_used = min(coins_to_use, int(amount))  # Can't use more coins than amount
        final_amount = amount - coins_used

        # Deduct coins
        user.trust_coins -= coins_used

        # Record coin transaction
        coin_txn = models.CoinTransaction(
            user_id=user_id,
            amount=-coins_used,
            transaction_type="spent",
            source="payment",
            description=f"Coins used for order #{order.order_number}",
            reference_type="order",
            reference_id=order_id,
            balance_after=user.trust_coins
        )
        db.add(coin_txn)

    # Update order
    order.payment_id = payment_id
    order.payment_method = payment_method
    order.coins_used = coins_used
    order.payment_status = models.PaymentStatus.PENDING

    db.commit()

    # Generate mock payment details
    expires_at = datetime.now() + timedelta(minutes=15)

    if payment_method == "UPI":
        # Generate UPI QR code URL (mock)
        upi_link = f"upi://pay?pa=ooumph@upi&pn=Ooumph&am={final_amount:.2f}&tr={payment_id}"

        response = {
            "payment_id": payment_id,
            "order_id": order_id,
            "amount": final_amount,
            "original_amount": amount,
            "coins_used": coins_used,
            "payment_method": payment_method,
            "status": "pending",
            "expires_at": expires_at.strftime("%Y-%m-%d %H:%M:%S"),
            "upi_link": upi_link,
            "qr_code_url": f"/api/payments/qr/{payment_id}",
            "instructions": [
                "Scan the QR code using any UPI app",
                "Or click the UPI link to pay directly",
                "Payment expires in 15 minutes",
                f"Amount to pay: ₹{final_amount:.2f}"
            ]
        }
    else:
        # Cash on Delivery or other methods
        response = {
            "payment_id": payment_id,
            "order_id": order_id,
            "amount": final_amount,
            "coins_used": coins_used,
            "payment_method": payment_method,
            "status": "pending",
            "instructions": [
                f"Pay ₹{final_amount:.2f} on delivery",
                "Keep exact change ready"
            ]
        }

    return response

async def check_payment_status(payment_id: str,
                             db: Session = None) -> Dict:
    """
    Check status of a payment

    Args:
        payment_id: Payment ID
        db: Database session

    Returns:
        Payment status
    """
    # Find order with this payment ID
    order = db.query(models.Order).filter(models.Order.payment_id == payment_id).first()

    if not order:
        return {
            "payment_id": payment_id,
            "status": "not_found",
            "message": "Payment not found"
        }

    # For mock, randomly complete pending payments
    if order.payment_status == models.PaymentStatus.PENDING:
        # Simulate payment completion (in real app, this would check with payment gateway)
        if random.random() > 0.3:  # 70% chance of completion for demo
            order.payment_status = models.PaymentStatus.COMPLETED
            order.order_status = models.OrderStatus.CONFIRMED
            db.commit()

    return {
        "payment_id": payment_id,
        "order_id": order.id,
        "order_number": order.order_number,
        "status": order.payment_status.value.lower(),
        "amount": order.final_amount,
        "payment_method": order.payment_method,
        "completed_at": order.updated_at.strftime("%Y-%m-%d %H:%M:%S") if order.payment_status == models.PaymentStatus.COMPLETED else None
    }

async def process_payment_callback(payment_id: str,
                                  status: str,
                                  transaction_id: Optional[str] = None,
                                  db: Session = None) -> Dict:
    """
    Process payment callback from payment gateway (mock)

    Args:
        payment_id: Payment ID
        status: Payment status (success, failed, pending)
        transaction_id: Gateway transaction ID
        db: Database session

    Returns:
        Callback processing result
    """
    order = db.query(models.Order).filter(models.Order.payment_id == payment_id).first()

    if not order:
        return {"success": False, "message": "Order not found"}

    if status == "success":
        order.payment_status = models.PaymentStatus.COMPLETED
        order.order_status = models.OrderStatus.CONFIRMED

        # Create audit log
        audit = models.AuditLog(
            actor_id=order.buyer_id,
            action="payment_completed",
            entity_type="order",
            entity_id=order.id,
            details={"payment_id": payment_id, "transaction_id": transaction_id, "amount": order.final_amount}
        )
        db.add(audit)

    elif status == "failed":
        order.payment_status = models.PaymentStatus.FAILED

        # Refund coins if used
        if order.coins_used > 0:
            buyer = db.query(models.User).filter(models.User.id == order.buyer_id).first()
            if buyer:
                buyer.trust_coins += order.coins_used

                coin_txn = models.CoinTransaction(
                    user_id=buyer.id,
                    amount=order.coins_used,
                    transaction_type="refunded",
                    source="payment_failed",
                    description=f"Coins refunded for failed payment",
                    reference_type="order",
                    reference_id=order.id,
                    balance_after=buyer.trust_coins
                )
                db.add(coin_txn)

    db.commit()

    return {
        "success": status == "success",
        "order_id": order.id,
        "order_number": order.order_number,
        "payment_status": order.payment_status.value,
        "order_status": order.order_status.value
    }

async def get_payment_qr_code(payment_id: str) -> str:
    """
    Generate QR code for payment (mock)

    Args:
        payment_id: Payment ID

    Returns:
        QR code URL
    """
    # In production, this would generate an actual QR code image
    # For mock, return a placeholder
    return f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=Ooumph_Payment_{payment_id}"

async def refund_payment(order_id: int,
                        reason: str,
                        db: Session = None) -> Dict:
    """
    Process refund for an order

    Args:
        order_id: Order ID
        reason: Refund reason
        db: Database session

    Returns:
        Refund result
    """
    order = db.query(models.Order).filter(models.Order.id == order_id).first()

    if not order:
        raise ValueError("Order not found")

    if order.payment_status != models.PaymentStatus.COMPLETED:
        raise ValueError("Can only refund completed payments")

    # Update order
    order.payment_status = models.PaymentStatus.REFUNDED
    order.order_status = models.OrderStatus.REFUNDED

    # Refund coins if used
    refund_amount = order.coins_used
    if refund_amount > 0:
        buyer = db.query(models.User).filter(models.User.id == order.buyer_id).first()
        if buyer:
            buyer.trust_coins += refund_amount

            coin_txn = models.CoinTransaction(
                user_id=buyer.id,
                amount=refund_amount,
                transaction_type="refunded",
                source="refund",
                description=f"Refund for order #{order.order_number}: {reason}",
                reference_type="order",
                reference_id=order.id,
                balance_after=buyer.trust_coins
            )
            db.add(coin_txn)

    # Create audit log
    audit = models.AuditLog(
        actor_id=order.buyer_id,
        action="payment_refunded",
        entity_type="order",
        entity_id=order.id,
        details={"reason": reason, "amount": order.final_amount, "coins_refunded": refund_amount}
    )
    db.add(audit)

    db.commit()

    return {
        "success": True,
        "order_id": order_id,
        "order_number": order.order_number,
        "refund_amount": order.final_amount,
        "coins_refunded": refund_amount,
        "reason": reason
    }

async def get_payment_methods(user_id: int,
                             db: Session = None) -> Dict:
    """
    Get available payment methods for a user

    Args:
        user_id: User ID
        db: Database session

    Returns:
        Available payment methods
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise ValueError("User not found")

    methods = [
        {
            "id": "UPI",
            "name": "UPI Payment",
            "description": "Pay using any UPI app (GPay, PhonePe, Paytm)",
            "icon": "upi",
            "enabled": True
        },
        {
            "id": "Trust_Coins",
            "name": "Trust Coins",
            "description": f"Pay using your trust coins (Balance: {user.trust_coins})",
            "icon": "coins",
            "enabled": user.trust_coins > 0
        },
        {
            "id": "Mixed",
            "name": "Mixed Payment",
            "description": "Use both UPI and Trust Coins",
            "icon": "mixed",
            "enabled": user.trust_coins > 0
        },
        {
            "id": "COD",
            "name": "Cash on Delivery",
            "description": "Pay when you receive the order",
            "icon": "cash",
            "enabled": True
        }
    ]

    return {
        "available_methods": methods,
        "coin_balance": user.trust_coins,
        "coin_value": "₹1 per coin"
    }

async def calculate_payment_breakdown(order_id: int,
                                    use_coins: bool = False,
                                    coins_to_use: int = 0,
                                    db: Session = None) -> Dict:
    """
    Calculate payment breakdown for an order

    Args:
        order_id: Order ID
        use_coins: Whether to use coins
        coins_to_use: Coins to use
        db: Database session

    Returns:
        Payment breakdown
    """
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise ValueError("Order not found")

    user = db.query(models.User).filter(models.User.id == order.buyer_id).first()
    if not user:
        raise ValueError("User not found")

    base_amount = order.final_amount
    coins_available = user.trust_coins
    coins_to_use = min(coins_to_use, coins_available, int(base_amount))

    remaining_amount = base_amount - coins_to_use

    breakdown = {
        "order_id": order_id,
        "order_number": order.order_number,
        "base_amount": base_amount,
        "coins": {
            "available": coins_available,
            "max_usable": min(coins_available, int(base_amount)),
            "to_use": coins_to_use,
            "value": f"₹{coins_to_use}"
        },
        "upi_amount": remaining_amount,
        "total_payment": remaining_amount + (coins_to_use if use_coins else base_amount),
        "savings": coins_to_use,
        "payment_methods": ["UPI"] if remaining_amount > 0 else []
    }

    if use_coins and coins_to_use > 0:
        breakdown["payment_methods"].insert(0, "Trust_Coins")

    return breakdown
