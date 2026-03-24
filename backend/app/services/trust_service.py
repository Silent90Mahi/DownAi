"""
Agent Vishwas (विश्वास) - Trust & Compliance Service
Calculates and manages trust scores, badges, and compliance
"""
import os
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from .. import models
from core.logging import get_logger

logger = get_logger(__name__)

# Trust score weights
TRUST_WEIGHTS = {
    "quality": 0.25,      # Product quality and reviews
    "delivery": 0.20,     # On-time delivery
    "financial": 0.20,    # Payment history, loan repayment
    "community": 0.15,    # Community participation
    "sustainability": 0.10, # Eco-friendly practices
    "digital": 0.10       # Platform engagement
}

# Badge thresholds
BADGE_THRESHOLDS = {
    "Bronze": (50, 69),
    "Silver": (70, 89),
    "Gold": (90, 100)
}

# Coin earning rules (enhanced)
COIN_EARNING_RULES = {
    # Order-related
    "order_complete": 10,
    "on_time_delivery": 5,
    "early_delivery": 8,
    "positive_review": 5,
    "bulk_order": 20,
    "repeat_customer": 15,

    # Quality & certification
    "training_complete": 20,
    "audit_passed": 15,
    "certification_earned": 50,
    "product_verified": 25,
    "quality_badge": 30,

    # Community & engagement
    "referral": 25,
    "community_help": 10,
    "forum_post": 5,
    "webinar_attend": 15,
    "mentorship": 20,

    # Marketplace activities
    "product_listed": 5,
    "ondc_listed": 15,
    "gem_bid": 10,
    "exhibition_participate": 30,

    # Compliance
    "profile_complete": 10,
    "kyc_verified": 50,
    "tax_filed": 25,
    "report_submitted": 10
}

# Alias for COIN_EARNING_RULES for backward compatibility
COIN_RULES = COIN_EARNING_RULES

# Coin redemption options
COIN_REWARDS = {
    "premium_listing": {
        "name": "Premium Product Listing",
        "cost": 50,
        "description": "Highlight your product for 7 days",
        "duration_days": 7
    },
    "discount_coupon": {
        "name": "Platform Fee Discount",
        "cost": 100,
        "description": "50% off platform fee for next 5 orders",
        "value": "50%"
    },
    "badge_unlock": {
        "name": "Exclusive Badge",
        "cost": 200,
        "description": "Unlock 'Trusted Seller' badge",
        "permanent": True
    },
    "featured_seller": {
        "name": "Featured Seller Slot",
        "cost": 150,
        "description": "Be featured on homepage for 3 days",
        "duration_days": 3
    },
    "analytics_upgrade": {
        "name": "Advanced Analytics",
        "cost": 75,
        "description": "Access detailed market insights for 30 days",
        "duration_days": 30
    },
    "priority_support": {
        "name": "Priority Support",
        "cost": 25,
        "description": "Get priority support for 7 days",
        "duration_days": 7
    },
    "bulk_purchase_discount": {
        "name": "Bulk Purchase Discount",
        "cost": 80,
        "description": "Get notifications for bulk orders",
        "permanent": True
    },
    "training_access": {
        "name": "Exclusive Training",
        "cost": 60,
        "description": "Access premium training content",
        "permanent": True
    }
}

async def calculate_trust_score(user_id: int, db: Session) -> Dict:
    """
    Calculate comprehensive trust score for a user

    Args:
        user_id: User ID
        db: Database session

    Returns:
        Trust score breakdown
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise ValueError("User not found")

    # Get component scores
    quality_score = user.quality_score or 50.0
    delivery_score = user.delivery_score or 50.0
    financial_score = user.financial_score or 50.0
    community_score = user.community_score or 50.0
    sustainability_score = user.sustainability_score or 50.0
    digital_score = user.digital_score or 50.0

    # Calculate weighted score
    overall_score = (
        quality_score * TRUST_WEIGHTS["quality"] +
        delivery_score * TRUST_WEIGHTS["delivery"] +
        financial_score * TRUST_WEIGHTS["financial"] +
        community_score * TRUST_WEIGHTS["community"] +
        sustainability_score * TRUST_WEIGHTS["sustainability"] +
        digital_score * TRUST_WEIGHTS["digital"]
    )

    # Round to 1 decimal
    overall_score = round(overall_score, 1)

    # Determine badge
    badge = get_badge_for_score(overall_score)

    return {
        "overall_score": overall_score,
        "quality_score": quality_score,
        "delivery_score": delivery_score,
        "financial_score": financial_score,
        "community_score": community_score,
        "sustainability_score": sustainability_score,
        "digital_score": digital_score,
        "badge": badge
    }

def get_badge_for_score(score: float) -> str:
    """Get badge name for a given score"""
    for badge, (min_score, max_score) in BADGE_THRESHOLDS.items():
        if min_score <= score <= max_score:
            return badge
    return "Bronze"

async def update_trust_score(user_id: int, reason: str,
                            component_updates: Dict[str, float],
                            reference_type: Optional[str] = None,
                            reference_id: Optional[int] = None,
                            db: Session = None) -> Dict:
    """
    Update trust score with history tracking

    Args:
        user_id: User ID
        reason: Reason for update
        component_updates: Dict of component scores to update
        reference_type: Reference entity type
        reference_id: Reference entity ID
        db: Database session

    Returns:
        Updated trust score with change details
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise ValueError("User not found")

    previous_score = user.trust_score or 50.0
    previous_badge = user.trust_badge or "Bronze"

    # Update component scores
    for component, value in component_updates.items():
        if hasattr(user, f"{component}_score"):
            setattr(user, f"{component}_score", value)

    # Recalculate overall score
    breakdown = await calculate_trust_score(user_id, db)
    new_score = breakdown["overall_score"]
    new_badge = breakdown["badge"]

    # Update user
    user.trust_score = new_score
    user.trust_badge = new_badge

    # Record history
    score_change = new_score - previous_score
    badge_change = previous_badge if previous_badge == new_badge else f"{previous_badge} → {new_badge}"

    history = models.TrustHistory(
        user_id=user_id,
        previous_score=previous_score,
        new_score=new_score,
        score_change=score_change,
        reason=reason,
        reference_type=reference_type,
        reference_id=reference_id,
        badge_change=badge_change if previous_badge != new_badge else None,
        quality_score=breakdown["quality_score"],
        delivery_score=breakdown["delivery_score"],
        financial_score=breakdown["financial_score"],
        community_score=breakdown["community_score"],
        sustainability_score=breakdown["sustainability_score"],
        digital_score=breakdown["digital_score"]
    )

    db.add(history)
    db.commit()

    return {
        "previous_score": previous_score,
        "new_score": new_score,
        "score_change": score_change,
        "badge_change": badge_change,
        "new_badge": new_badge,
        "breakdown": breakdown
    }

async def award_coins(user_id: int, amount: int, source: str,
                    description: str,
                    reference_type: Optional[str] = None,
                    reference_id: Optional[int] = None,
                    db: Session = None) -> Dict:
    """
    Award trust coins to a user

    Args:
        user_id: User ID
        amount: Amount of coins (positive for earning, negative for spending)
        source: Source of coins
        description: Description
        reference_type: Reference entity type
        reference_id: Reference entity ID
        db: Database session

    Returns:
        Updated coin balance
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise ValueError("User not found")

    previous_balance = user.trust_coins or 0

    # Update balance
    user.trust_coins = previous_balance + amount
    new_balance = user.trust_coins

    # Record transaction
    transaction = models.CoinTransaction(
        user_id=user_id,
        amount=amount,
        transaction_type="earned" if amount > 0 else "spent",
        source=source,
        description=description,
        reference_type=reference_type,
        reference_id=reference_id,
        balance_after=new_balance
    )

    db.add(transaction)
    db.commit()

    return {
        "previous_balance": previous_balance,
        "amount": amount,
        "new_balance": new_balance,
        "transaction_type": "earned" if amount > 0 else "spent"
    }

async def process_order_completion(order_id: int, db: Session) -> Dict:
    """
    Process trust score updates on order completion

    Args:
        order_id: Order ID
        db: Database session

    Returns:
        Trust and coin updates
    """
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise ValueError("Order not found")

    updates = {
        "seller": None,
        "buyer": None
    }

    # Update seller trust
    seller = db.query(models.User).filter(models.User.id == order.seller_id).first()
    if seller:
        # Improve delivery score for completing order
        component_updates = {
            "delivery": min(100, (seller.delivery_score or 50) + random.uniform(2, 5)),
            "quality": min(100, (seller.quality_score or 50) + random.uniform(1, 3)),
            "financial": min(100, (seller.financial_score or 50) + random.uniform(1, 2))
        }

        seller_update = await update_trust_score(
            seller.id,
            "order_complete",
            component_updates,
            "order",
            order_id,
            db
        )

        # Award coins
        coin_award = await award_coins(
            seller.id,
            COIN_RULES["order_complete"],
            "order_complete",
            f"Coins earned for completing order #{order.order_number}",
            "order",
            order_id,
            db
        )

        updates["seller"] = {
            "trust_update": seller_update,
            "coins_awarded": coin_award
        }

    # Update buyer trust (smaller impact)
    buyer = db.query(models.User).filter(models.User.id == order.buyer_id).first()
    if buyer:
        component_updates = {
            "financial": min(100, (buyer.financial_score or 50) + random.uniform(1, 2)),
            "digital": min(100, (buyer.digital_score or 50) + random.uniform(0.5, 1))
        }

        buyer_update = await update_trust_score(
            buyer.id,
            "order_complete",
            component_updates,
            "order",
            order_id,
            db
        )

        updates["buyer"] = {
            "trust_update": buyer_update
        }

    return updates

async def get_trust_history(user_id: int, limit: int = 50,
                           db: Session = None) -> List[Dict]:
    """
    Get trust score history for a user

    Args:
        user_id: User ID
        limit: Maximum records to return
        db: Database session

    Returns:
        List of trust history records
    """
    history = db.query(models.TrustHistory).filter(
        models.TrustHistory.user_id == user_id
    ).order_by(
        models.TrustHistory.created_at.desc()
    ).limit(limit).all()

    return [
        {
            "id": h.id,
            "previous_score": h.previous_score,
            "new_score": h.new_score,
            "score_change": h.score_change,
            "reason": h.reason,
            "reference_type": h.reference_type,
            "reference_id": h.reference_id,
            "badge_change": h.badge_change,
            "created_at": h.created_at.strftime("%Y-%m-%d %H:%M")
        }
        for h in history
    ]

async def get_coin_wallet(user_id: int, db: Session) -> Dict:
    """
    Get user's coin wallet details

    Args:
        user_id: User ID
        db: Database session

    Returns:
        Wallet details with recent transactions
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise ValueError("User not found")

    # Get transaction summary
    earned = db.query(
        func.coalesce(func.sum(models.CoinTransaction.amount), 0)
    ).filter(
        and_(
            models.CoinTransaction.user_id == user_id,
            models.CoinTransaction.amount > 0
        )
    ).scalar()

    spent = db.query(
        func.coalesce(func.sum(abs(models.CoinTransaction.amount)), 0)
    ).filter(
        and_(
            models.CoinTransaction.user_id == user_id,
            models.CoinTransaction.amount < 0
        )
    ).scalar()

    # Get recent transactions
    recent = db.query(models.CoinTransaction).filter(
        models.CoinTransaction.user_id == user_id
    ).order_by(
        models.CoinTransaction.created_at.desc()
    ).limit(20).all()

    recent_transactions = [
        {
            "id": t.id,
            "amount": t.amount,
            "transaction_type": t.transaction_type,
            "source": t.source,
            "description": t.description,
            "balance_after": t.balance_after,
            "created_at": t.created_at.strftime("%Y-%m-%d %H:%M")
        }
        for t in recent
    ]

    return {
        "balance": user.trust_coins or 0,
        "total_earned": int(earned),
        "total_spent": int(spent),
        "recent_transactions": recent_transactions
    }

async def create_audit_log(actor_id: int, action: str,
                          entity_type: Optional[str] = None,
                          entity_id: Optional[int] = None,
                          details: Optional[Dict] = None,
                          is_compliance_violation: bool = False,
                          severity: str = "low",
                          ip_address: Optional[str] = None,
                          user_agent: Optional[str] = None,
                          db: Session = None) -> Dict:
    """
    Create an audit log entry

    Args:
        actor_id: User ID performing the action
        action: Action performed
        entity_type: Type of entity affected
        entity_id: ID of entity affected
        details: Additional details
        is_compliance_violation: Whether this is a compliance issue
        severity: Severity level
        ip_address: IP address
        user_agent: User agent string
        db: Database session

    Returns:
        Created audit log
    """
    log = models.AuditLog(
        actor_id=actor_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
        is_compliance_violation=is_compliance_violation,
        severity=severity,
        ip_address=ip_address,
        user_agent=user_agent
    )

    db.add(log)
    db.commit()
    db.refresh(log)

    return {
        "id": log.id,
        "actor_id": log.actor_id,
        "action": log.action,
        "entity_type": log.entity_type,
        "entity_id": log.entity_id,
        "is_compliance_violation": log.is_compliance_violation,
        "severity": log.severity,
        "timestamp": log.timestamp.strftime("%Y-%m-%d %H:%M:%S")
    }

async def get_audit_logs(actor_id: Optional[int] = None,
                        entity_type: Optional[str] = None,
                        limit: int = 100,
                        db: Session = None) -> List[Dict]:
    """
    Get audit logs with optional filters

    Args:
        actor_id: Filter by actor
        entity_type: Filter by entity type
        limit: Maximum records
        db: Database session

    Returns:
        List of audit logs
    """
    query = db.query(models.AuditLog)

    if actor_id:
        query = query.filter(models.AuditLog.actor_id == actor_id)
    if entity_type:
        query = query.filter(models.AuditLog.entity_type == entity_type)

    logs = query.order_by(models.AuditLog.timestamp.desc()).limit(limit).all()

    # Get actor names
    actor_ids = list(set([log.actor_id for log in logs]))
    actors = {u.id: u.name for u in db.query(models.User).filter(models.User.id.in_(actor_ids)).all()}

    return [
        {
            "id": log.id,
            "actor_id": log.actor_id,
            "actor_name": actors.get(log.actor_id, f"User {log.actor_id}"),
            "action": log.action,
            "entity_type": log.entity_type,
            "entity_id": log.entity_id,
            "details": log.details,
            "is_compliance_violation": log.is_compliance_violation,
            "severity": log.severity,
            "timestamp": log.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }
        for log in logs
    ]

async def get_trust_leaderboard(limit: int = 50,
                                district: Optional[str] = None,
                                db: Session = None) -> List[Dict]:
    """
    Get trust score leaderboard

    Args:
        limit: Maximum users to return
        district: Filter by district
        db: Database session

    Returns:
        List of top users by trust score
    """
    query = db.query(models.User).filter(
        models.User.role == "SHG"
    )

    if district:
        query = query.filter(models.User.district == district)

    users = query.order_by(
        models.User.trust_score.desc()
    ).limit(limit).all()

    return [
        {
            "rank": idx + 1,
            "user_id": u.id,
            "name": u.name,
            "district": u.district,
            "trust_score": u.trust_score,
            "trust_badge": u.trust_badge,
            "products_count": len([p for p in u.products if p.status == "Active"])
        }
        for idx, u in enumerate(users)
    ]

async def redeem_coins(user_id: int, amount: int, reward_type: str,
                      db: Session = None) -> Dict:
    """
    Redeem trust coins for rewards

    Args:
        user_id: User ID
        amount: Amount to redeem
        reward_type: Type of reward (premium_listing, discount, etc.)
        db: Database session

    Returns:
        Redemption result
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise ValueError("User not found")

    if user.trust_coins < amount:
        raise ValueError("Insufficient coins")

    # Validate reward type
    if reward_type not in COIN_REWARDS:
        raise ValueError(f"Invalid reward type: {reward_type}")

    reward = COIN_REWARDS[reward_type]
    if reward["cost"] != amount:
        raise ValueError(f"Amount mismatch. Expected {reward['cost']} for {reward_type}")

    # Deduct coins
    coin_update = await award_coins(
        user_id,
        -amount,
        "redeemed",
        f"Redeemed for {reward['name']}",
        "redemption",
        None,
        db
    )

    logger.info(f"User {user_id} redeemed {amount} coins for {reward_type}")

    return {
        "success": True,
        "reward_type": reward_type,
        "reward_name": reward["name"],
        "coins_spent": amount,
        "new_balance": coin_update["new_balance"],
        "reward_details": reward
    }


async def get_available_rewards(user_id: Optional[int] = None,
                                 db: Session = None) -> Dict:
    """
    Get available coin redemption rewards

    Args:
        user_id: Optional user ID to show affordable rewards
        db: Database session

    Returns:
        Available rewards with affordability status
    """
    user_balance = 0
    if user_id:
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if user:
            user_balance = user.trust_coins or 0

    rewards = []
    for reward_key, reward_data in COIN_REWARDS.items():
        rewards.append({
            "id": reward_key,
            "name": reward_data["name"],
            "cost": reward_data["cost"],
            "description": reward_data["description"],
            "can_afford": user_balance >= reward_data["cost"],
            "duration_days": reward_data.get("duration_days"),
            "permanent": reward_data.get("permanent", False)
        })

    return {
        "user_balance": user_balance,
        "rewards": rewards,
        "total_rewards": len(rewards)
    }


async def earn_coins_for_action(user_id: int, action: str,
                                reference_type: Optional[str] = None,
                                reference_id: Optional[int] = None,
                                db: Session = None) -> Dict:
    """
    Award coins based on predefined earning rules

    Args:
        user_id: User ID
        action: Action type (key from COIN_EARNING_RULES)
        reference_type: Reference entity type
        reference_id: Reference entity ID
        db: Database session

    Returns:
        Coin earning result
    """
    if action not in COIN_EARNING_RULES:
        logger.warning(f"Unknown coin earning action: {action}")
        return {"success": False, "error": "Unknown action"}

    amount = COIN_EARNING_RULES[action]

    # Get action description
    descriptions = {
        "order_complete": "Completed an order",
        "on_time_delivery": "On-time delivery",
        "early_delivery": "Early delivery bonus",
        "positive_review": "Received positive review",
        "bulk_order": "Fulfilled bulk order",
        "repeat_customer": "Repeat customer order",
        "training_complete": "Completed training program",
        "audit_passed": "Passed quality audit",
        "certification_earned": "Earned certification",
        "product_verified": "Product verified",
        "quality_badge": "Earned quality badge",
        "referral": "Referred new user",
        "community_help": "Helped community member",
        "forum_post": "Contributed to forum",
        "webinar_attend": "Attended webinar",
        "mentorship": "Mentored another SHG",
        "product_listed": "Listed new product",
        "ondc_listed": "Listed on ONDC",
        "gem_bid": "Submitted GeM bid",
        "exhibition_participate": "Participated in exhibition",
        "profile_complete": "Completed profile",
        "kyc_verified": "KYC verification",
        "tax_filed": "Filed tax returns",
        "report_submitted": "Submitted compliance report"
    }

    description = descriptions.get(action, f"Coins for {action}")

    result = await award_coins(
        user_id,
        amount,
        action,
        description,
        reference_type,
        reference_id,
        db
    )

    logger.info(f"Awarded {amount} coins to user {user_id} for {action}")

    return {
        "success": True,
        "action": action,
        "coins_earned": amount,
        "description": description,
        "new_balance": result["new_balance"]
    }


async def get_coin_earning_opportunities(user_id: int,
                                        db: Session = None) -> Dict:
    """
    Get available opportunities for earning coins

    Args:
        user_id: User ID
        db: Database session

    Returns:
        List of earning opportunities
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise ValueError("User not found")

    opportunities = [
        {
            "category": "Sales",
            "actions": [
                {"action": "order_complete", "name": "Complete an order", "coins": COIN_EARNING_RULES["order_complete"]},
                {"action": "on_time_delivery", "name": "Deliver on time", "coins": COIN_EARNING_RULES["on_time_delivery"]},
                {"action": "early_delivery", "name": "Early delivery bonus", "coins": COIN_EARNING_RULES["early_delivery"]},
                {"action": "bulk_order", "name": "Fulfill bulk order", "coins": COIN_EARNING_RULES["bulk_order"]},
            ]
        },
        {
            "category": "Quality",
            "actions": [
                {"action": "positive_review", "name": "Get positive review", "coins": COIN_EARNING_RULES["positive_review"]},
                {"action": "product_verified", "name": "Verify product", "coins": COIN_EARNING_RULES["product_verified"]},
                {"action": "quality_badge", "name": "Earn quality badge", "coins": COIN_EARNING_RULES["quality_badge"]},
            ]
        },
        {
            "category": "Learning",
            "actions": [
                {"action": "training_complete", "name": "Complete training", "coins": COIN_EARNING_RULES["training_complete"]},
                {"action": "webinar_attend", "name": "Attend webinar", "coins": COIN_EARNING_RULES["webinar_attend"]},
                {"action": "mentorship", "name": "Mentor another SHG", "coins": COIN_EARNING_RULES["mentorship"]},
            ]
        },
        {
            "category": "Marketplace",
            "actions": [
                {"action": "product_listed", "name": "List new product", "coins": COIN_EARNING_RULES["product_listed"]},
                {"action": "ondc_listed", "name": "List on ONDC", "coins": COIN_EARNING_RULES["ondc_listed"]},
                {"action": "gem_bid", "name": "Submit GeM bid", "coins": COIN_EARNING_RULES["gem_bid"]},
                {"action": "exhibition_participate", "name": "Join exhibition", "coins": COIN_EARNING_RULES["exhibition_participate"]},
            ]
        },
        {
            "category": "Community",
            "actions": [
                {"action": "referral", "name": "Refer new SHG", "coins": COIN_EARNING_RULES["referral"]},
                {"action": "community_help", "name": "Help community", "coins": COIN_EARNING_RULES["community_help"]},
                {"action": "forum_post", "name": "Post in forum", "coins": COIN_EARNING_RULES["forum_post"]},
            ]
        }
    ]

    return {
        "current_balance": user.trust_coins or 0,
        "opportunities": opportunities
    }


async def get_coin_summary(user_id: int, days: int = 30,
                          db: Session = None) -> Dict:
    """
    Get comprehensive coin summary for a user

    Args:
        user_id: User ID
        days: Number of days to analyze
        db: Database session

    Returns:
        Coin usage summary
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise ValueError("User not found")

    # Calculate date range
    start_date = datetime.now() - timedelta(days=days)

    # Get transactions in date range
    transactions = db.query(models.CoinTransaction).filter(
        and_(
            models.CoinTransaction.user_id == user_id,
            models.CoinTransaction.created_at >= start_date
        )
    ).all()

    # Calculate totals
    earned = sum(t.amount for t in transactions if t.amount > 0)
    spent = sum(abs(t.amount) for t in transactions if t.amount < 0)

    # Group by source
    earned_by_source = {}
    spent_by_source = {}

    for t in transactions:
        if t.amount > 0:
            earned_by_source[t.source] = earned_by_source.get(t.source, 0) + t.amount
        else:
            spent_by_source[t.source] = spent_by_source.get(t.source, 0) + abs(t.amount)

    # Calculate earning rate (coins per day)
    earning_rate = earned / days if days > 0 else 0

    return {
        "summary_period_days": days,
        "current_balance": user.trust_coins or 0,
        "earned_in_period": int(earned),
        "spent_in_period": int(spent),
        "net_change": int(earned - spent),
        "earning_rate_per_day": round(earning_rate, 1),
        "earned_by_source": earned_by_source,
        "spent_by_source": spent_by_source,
        "total_transactions": len(transactions)
    }
