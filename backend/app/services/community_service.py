"""
Agent Sampark (संपर्क) - Community Orchestration Service
Manages SHG hierarchy (SHG -> SLF -> TLF) and federation operations
"""
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from openai import OpenAI
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from .. import models

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "dummy"))

async def get_federation_members(federation_id: int,
                                federation_level: str,
                                include_children: bool = True,
                                db: Session = None) -> List[Dict]:
    """
    Get members of a federation (SLF or TLF)

    Args:
        federation_id: Federation user ID
        federation_level: Level of federation (SLF or TLF)
        include_children: Include nested SHGs
        db: Database session

    Returns:
        List of federation members
    """
    # Get direct children
    members = db.query(models.User).filter(
        models.User.federation_id == federation_id
    ).all()

    result = []
    for member in members:
        member_data = {
            "id": member.id,
            "name": member.name,
            "phone": member.phone,
            "district": member.district,
            "hierarchy_level": member.hierarchy_level.value if member.hierarchy_level else "SHG",
            "trust_score": member.trust_score,
            "trust_badge": member.trust_badge,
            "products_count": len([p for p in member.products if p.status == "Active"]),
            "created_at": member.created_at.strftime("%Y-%m-%d")
        }

        # Calculate revenue
        seller_orders = db.query(models.Order).filter(
            models.Order.seller_id == member.id,
            models.Order.order_status == "Delivered"
        ).all()
        member_data["revenue"] = sum([o.final_amount for o in seller_orders])

        result.append(member_data)

    return result

async def get_federation_stats(federation_id: int,
                              federation_level: str,
                              db: Session = None) -> Dict:
    """
    Get aggregate statistics for a federation

    Args:
        federation_id: Federation user ID
        federation_level: Level (SLF or TLF)
        db: Database session

    Returns:
        Federation statistics
    """
    members = await get_federation_members(federation_id, federation_level, True, db)

    if not members:
        return {
            "federation_id": federation_id,
            "federation_level": federation_level,
            "total_members": 0,
            "active_members": 0,
            "total_products": 0,
            "total_revenue": 0.0,
            "avg_trust_score": 0.0,
            "top_performers": []
        }

    # Calculate stats
    total_members = len(members)
    active_members = len([m for m in members if m["products_count"] > 0])
    total_products = sum([m["products_count"] for m in members])
    total_revenue = sum([m["revenue"] for m in members])
    avg_trust_score = sum([m["trust_score"] for m in members]) / total_members

    # Top performers
    top_performers = sorted(members, key=lambda x: x["revenue"], reverse=True)[:5]

    return {
        "federation_id": federation_id,
        "federation_level": federation_level,
        "total_members": total_members,
        "active_members": active_members,
        "total_products": total_products,
        "active_listings": total_products,
        "total_revenue": round(total_revenue, 2),
        "avg_trust_score": round(avg_trust_score, 1),
        "top_performers": [
            {
                "name": p["name"],
                "district": p["district"],
                "trust_score": p["trust_score"],
                "products": p["products_count"],
                "revenue": p["revenue"]
            }
            for p in top_performers
        ]
    }

async def send_community_alert(creator_id: int, title: str, message: str,
                              target_level: str,
                              district: Optional[str] = None,
                              db: Session = None) -> Dict:
    """
    Send alert to community members

    Args:
        creator_id: Admin user ID creating the alert
        title: Alert title
        message: Alert message
        target_level: Target hierarchy level (SHG, SLF, TLF, All)
        district: Filter by district
        db: Database session

    Returns:
        Alert creation result
    """
    # Build recipient list
    query = db.query(models.User)

    if target_level != "All":
        query = query.filter(models.User.hierarchy_level == target_level)

    if district:
        query = query.filter(models.User.district == district)

    recipients = query.all()

    # Create notifications for all recipients
    notifications_created = 0
    for recipient in recipients:
        notification = models.Notification(
            user_id=recipient.id,
            title=title,
            message=message,
            notification_type="alert",
            reference_type="community_alert",
            created_at=datetime.now()
        )
        db.add(notification)
        notifications_created += 1

    db.commit()

    # Also alert RTGS (mock) for governance monitoring
    await send_rtgs_alert(title, message, target_level, district)

    return {
        "success": True,
        "recipients_count": notifications_created,
        "target_level": target_level,
        "district": district
    }

async def send_rtgs_alert(title: str, message: str,
                         target_level: str,
                         district: Optional[str] = None) -> Dict:
    """
    Send alert to RTGS AWARE platform (mock)

    Args:
        title: Alert title
        message: Alert message
        target_level: Target level
        district: District

    Returns:
        Mock RTGS response
    """
    # In production, this would call RTGS API
    return {
        "rtgs_alert_id": f"RTGS{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "status": "sent",
        "platform": "AWARE",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

async def get_hierarchy_overview(user_id: int,
                                db: Session = None) -> Dict:
    """
    Get complete hierarchy overview for a user

    Args:
        user_id: User ID
        db: Database session

    Returns:
        Hierarchy overview with upstream and downstream
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise ValueError("User not found")

    result = {
        "current_user": {
            "id": user.id,
            "name": user.name,
            "hierarchy_level": user.hierarchy_level.value if user.hierarchy_level else "SHG",
            "district": user.district
        },
        "upstream": [],
        "downstream": [],
        "peers": []
    }

    # Get upstream (parent federation)
    if user.federation_id:
        parent = db.query(models.User).filter(models.User.id == user.federation_id).first()
        if parent:
            result["upstream"].append({
                "id": parent.id,
                "name": parent.name,
                "level": parent.hierarchy_level.value if parent.hierarchy_level else "Unknown",
                "district": parent.district
            })

    # Get downstream (children SHGs)
    children = db.query(models.User).filter(models.User.federation_id == user_id).all()
    for child in children:
        result["downstream"].append({
            "id": child.id,
            "name": child.name,
            "level": child.hierarchy_level.value if child.hierarchy_level else "SHG",
            "district": child.district,
            "trust_score": child.trust_score
        })

    # Get peers (same parent)
    if user.federation_id:
        peers = db.query(models.User).filter(
            and_(
                models.User.federation_id == user.federation_id,
                models.User.id != user_id
            )
        ).all()

        for peer in peers:
            result["peers"].append({
                "id": peer.id,
                "name": peer.name,
                "district": peer.district,
                "trust_score": peer.trust_score
            })

    return result

async def get_district_overview(district: str,
                              db: Session = None) -> Dict:
    """
    Get overview of all SHGs in a district

    Args:
        district: District name
        db: Database session

    Returns:
        District overview
    """
    # Get all SHGs in district
    shgs = db.query(models.User).filter(
        and_(
            models.User.role == "SHG",
            models.User.district == district
        )
    ).all()

    # Calculate stats
    total_shgs = len(shgs)
    active_shgs = len([s for s in shgs if len([p for p in s.products if p.status == "Active"]) > 0])

    # Get products
    all_products = []
    for shg in shgs:
        all_products.extend([p for p in shg.products if p.status == "Active"])

    total_products = len(all_products)

    # Get revenue
    shg_ids = [s.id for s in shgs]
    delivered_orders = db.query(models.Order).filter(
        and_(
            models.Order.seller_id.in_(shg_ids),
            models.Order.order_status == "Delivered"
        )
    ).all()

    total_revenue = sum([o.final_amount for o in delivered_orders])
    total_orders = len(delivered_orders)

    # Average trust score
    avg_trust = sum([s.trust_score for s in shgs]) / total_shgs if total_shgs > 0 else 0

    # Get federation breakdown
    slf_count = len([s for s in shgs if s.hierarchy_level and s.hierarchy_level.value == "SLF"])
    tlf_count = len([s for s in shgs if s.hierarchy_level and s.hierarchy_level.value == "TLF"])
    shg_count = total_shgs - slf_count - tlf_count

    return {
        "district": district,
        "total_shgs": total_shgs,
        "active_shgs": active_shgs,
        "hierarchy_breakdown": {
            "TLF": tlf_count,
            "SLF": slf_count,
            "SHG": shg_count
        },
        "total_products": total_products,
        "total_orders": total_orders,
        "total_revenue": round(total_revenue, 2),
        "avg_trust_score": round(avg_trust, 1)
    }

async def escalate_to_leadership(user_id: int,
                                 issue_type: str,
                                 issue_details: str,
                                 urgency: str = "medium",
                                 db: Session = None) -> Dict:
    """
    Escalate an issue to federation leadership

    Args:
        user_id: User ID reporting the issue
        issue_type: Type of issue
        issue_details: Issue details
        urgency: Urgency level (low, medium, high)
        db: Database session

    Returns:
        Escalation result
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise ValueError("User not found")

    # Find the leadership chain
    recipients = []

    # Direct parent (SLF or TLF)
    if user.federation_id:
        recipients.append(user.federation_id)

    # Create escalation record
    escalation_id = f"ESC{datetime.now().strftime('%Y%m%d%H%M%S')}"

    # Notify leaders
    for recipient_id in recipients:
        notification = models.Notification(
            user_id=recipient_id,
            title=f"Issue Escalation: {issue_type}",
            message=f"Issue from {user.name} ({user.district}): {issue_details}\nUrgency: {urgency}",
            notification_type="escalation",
            reference_type="escalation",
            reference_id=escalation_id
        )
        db.add(notification)

    db.commit()

    return {
        "escalation_id": escalation_id,
        "recipients_notified": len(recipients),
        "urgency": urgency,
        "status": "escalated"
    }

async def get_community_announcements(district: Optional[str] = None,
                                     limit: int = 10,
                                     db: Session = None) -> List[Dict]:
    """
    Get community announcements

    Args:
        district: Filter by district
        limit: Maximum announcements
        db: Database session

    Returns:
        List of announcements
    """
    # In production, this would fetch from a dedicated announcements table
    # For now, return mock announcements

    announcements = [
        {
            "id": 1,
            "title": "Training Workshop on Quality Standards",
            "message": "Free workshop on improving product quality. Register by end of this month.",
            "type": "training",
            "district": "All",
            "valid_until": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
            "posted_date": (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")
        },
        {
            "id": 2,
            "title": "Government Tender Opportunity",
            "message": "New GeM tender for handicraft items. Minimum trust score: 60 required.",
            "type": "opportunity",
            "district": "All",
            "valid_until": (datetime.now() + timedelta(days=15)).strftime("%Y-%m-%d"),
            "posted_date": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
        },
        {
            "id": 3,
            "title": "Bulk Purchase Initiative",
            "message": "Join the bulk raw material purchase initiative. Save up to 25% on costs.",
            "type": "initiative",
            "district": district or "All",
            "valid_until": (datetime.now() + timedelta(days=20)).strftime("%Y-%m-%d"),
            "posted_date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        }
    ]

    if district:
        announcements = [a for a in announcements if a["district"] in ["All", district]]

    return announcements[:limit]

async def get_federation_performances(federation_id: int,
                                    period_months: int = 6,
                                    db: Session = None) -> Dict:
    """
    Get performance metrics for a federation over time

    Args:
        federation_id: Federation user ID
        period_months: Number of months to analyze
        db: Database session

    Returns:
        Performance metrics
    """
    start_date = datetime.now() - timedelta(days=30 * period_months)

    # Get members
    members = db.query(models.User).filter(
        models.User.federation_id == federation_id
    ).all()

    member_ids = [m.id for m in members]

    # Get orders in period
    orders = db.query(models.Order).filter(
        and_(
            models.Order.seller_id.in_(member_ids),
            models.Order.created_at >= start_date
        )
    ).all()

    # Calculate metrics
    total_orders = len(orders)
    delivered_orders = len([o for o in orders if o.order_status == "Delivered"])
    total_revenue = sum([o.final_amount for o in orders if o.order_status == "Delivered"])

    # Get products created in period
    products = db.query(models.Product).filter(
        and_(
            models.Product.seller_id.in_(member_ids),
            models.Product.created_at >= start_date
        )
    ).all()

    # Calculate month-over-month growth
    monthly_data = []
    for i in range(period_months):
        month_start = start_date + timedelta(days=30 * i)
        month_end = month_start + timedelta(days=30)

        month_orders = [o for o in orders if month_start <= o.created_at < month_end]
        month_revenue = sum([o.final_amount for o in month_orders if o.order_status == "Delivered"])

        monthly_data.append({
            "month": month_start.strftime("%b %Y"),
            "orders": len(month_orders),
            "revenue": round(month_revenue, 2)
        })

    return {
        "period_months": period_months,
        "total_members": len(members),
        "total_orders": total_orders,
        "delivered_orders": delivered_orders,
        "completion_rate": round((delivered_orders / total_orders * 100) if total_orders > 0 else 0, 1),
        "total_revenue": round(total_revenue, 2),
        "new_products": len(products),
        "monthly_breakdown": monthly_data
    }
