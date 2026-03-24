"""
Analytics Service
Provides comprehensive analytics for SHG ecosystem
"""
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from .. import models

async def get_dashboard_stats(district: Optional[str] = None,
                            federation_id: Optional[int] = None,
                            db: Session = None) -> Dict:
    """
    Get overall dashboard statistics

    Args:
        district: Filter by district
        federation_id: Filter by federation
        db: Database session

    Returns:
        Dashboard statistics
    """
    # Build base queries
    user_query = db.query(models.User).filter(models.User.role == "SHG")
    product_query = db.query(models.Product)
    order_query = db.query(models.Order)

    # Apply filters
    if district:
        user_query = user_query.filter(models.User.district == district)

    if federation_id:
        member_ids = db.query(models.User.id).filter(
            models.User.federation_id == federation_id
        ).all()
        member_ids = [m[0] for m in member_ids]
        product_query = product_query.filter(models.Product.seller_id.in_(member_ids))
        order_query = order_query.filter(
            models.Order.seller_id.in_(member_ids)
        )

    # Calculate metrics
    total_users = user_query.count()
    active_users = user_query.filter(
        models.User.last_login >= datetime.now() - timedelta(days=30)
    ).count()

    new_users = user_query.filter(
        models.User.created_at >= datetime.now() - timedelta(days=30)
    ).count()

    total_products = product_query.count()
    active_listings = product_query.filter(
        models.Product.status == "Active"
    ).count()

    total_orders = order_query.count()
    completed_orders = order_query.filter(
        models.Order.order_status == "Delivered"
    ).count()

    total_revenue = db.query(func.sum(models.Order.final_amount)).filter(
        models.Order.order_status == "Delivered"
    ).scalar() or 0

    # Trust metrics
    avg_trust = db.query(func.avg(models.User.trust_score)).filter(
        models.User.role == "SHG"
    ).scalar() or 50.0

    # Coin metrics
    coins_earned = db.query(func.sum(models.CoinTransaction.amount)).filter(
        models.CoinTransaction.amount > 0
    ).scalar() or 0

    coins_redeemed = abs(db.query(func.sum(models.CoinTransaction.amount)).filter(
        models.CoinTransaction.amount < 0
    ).scalar() or 0)

    # Agent interaction metrics (from chat history)
    vaani_interactions = db.query(models.ChatHistory).count()
    bazaar_queries = 0  # Track via market data queries
    jodi_matches = 0  # Track via buyer matches
    samagri_searches = 0  # Track via material searches

    return {
        "total_users": total_users,
        "active_users": active_users,
        "new_users": new_users,
        "total_products": total_products,
        "active_listings": active_listings,
        "total_orders": total_orders,
        "completed_orders": completed_orders,
        "total_revenue": round(float(total_revenue), 2),
        "avg_trust_score": round(float(avg_trust), 1),
        "total_coins_earned": int(coins_earned),
        "total_coins_redeemed": int(coins_redeemed),
        "agent_metrics": {
            "vaani_interactions": vaani_interactions,
            "bazaar_queries": bazaar_queries,
            "jodi_matches": jodi_matches,
            "samagri_searches": samagri_searches
        },
        "period": "all_time",
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

async def get_district_stats(db: Session = None) -> List[Dict]:
    """
    Get statistics grouped by district

    Args:
        db: Database session

    Returns:
        List of district statistics
    """
    districts = ["Hyderabad", "Visakhapatnam", "Vijayawada", "Guntur", "Tirupati",
                "Rajahmundry", "Kakinada", "Kurnool", "Nellore", "Kadapa"]

    stats = []
    for district in districts:
        # Get users in district
        users = db.query(models.User).filter(
            and_(
                models.User.role == "SHG",
                models.User.district == district
            )
        ).all()

        if not users:
            continue

        user_ids = [u.id for u in users]

        # Products
        products = db.query(models.Product).filter(
            models.Product.seller_id.in_(user_ids)
        ).count()

        # Orders
        orders = db.query(models.Order).filter(
            models.Order.seller_id.in_(user_ids)
        ).count()

        delivered = db.query(models.Order).filter(
            and_(
                models.Order.seller_id.in_(user_ids),
                models.Order.order_status == "Delivered"
            )
        ).count()

        revenue = db.query(func.sum(models.Order.final_amount)).filter(
            and_(
                models.Order.seller_id.in_(user_ids),
                models.Order.order_status == "Delivered"
            )
        ).scalar() or 0

        # Avg trust
        avg_trust = sum([u.trust_score for u in users]) / len(users) if users else 0

        stats.append({
            "district": district,
            "total_users": len(users),
            "total_products": products,
            "total_orders": orders,
            "total_revenue": round(float(revenue), 2),
            "avg_trust_score": round(avg_trust, 1),
            "completion_rate": round((delivered / orders * 100) if orders > 0 else 0, 1)
        })

    # Sort by revenue
    stats.sort(key=lambda x: x["total_revenue"], reverse=True)

    return stats

async def get_user_analytics(user_id: int,
                            period_months: int = 6,
                            db: Session = None) -> Dict:
    """
    Get detailed analytics for a specific user

    Args:
        user_id: User ID
        period_months: Period to analyze (months)
        db: Database session

    Returns:
        User analytics
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise ValueError("User not found")

    start_date = datetime.now() - timedelta(days=30 * period_months)

    # Products
    total_products = len([p for p in user.products if p.created_at >= start_date])
    active_products = len([p for p in user.products if p.status == "Active"])

    # Orders as seller
    seller_orders = db.query(models.Order).filter(
        and_(
            models.Order.seller_id == user_id,
            models.Order.created_at >= start_date
        )
    ).all()

    completed_sales = [o for o in seller_orders if o.order_status == "Delivered"]
    total_revenue = sum([o.final_amount for o in completed_sales])

    # Orders as buyer
    buyer_orders = db.query(models.Order).filter(
        and_(
            models.Order.buyer_id == user_id,
            models.Order.created_at >= start_date
        )
    ).count()

    total_purchases = db.query(func.sum(models.Order.final_amount)).filter(
        and_(
            models.Order.buyer_id == user_id,
            models.Order.created_at >= start_date,
            models.Order.order_status == "Delivered"
        )
    ).scalar() or 0

    # Completion rate
    completion_rate = (len(completed_sales) / len(seller_orders) * 100) if seller_orders else 0

    # Average rating (from products)
    avg_rating = sum([p.quality_rating or 0 for p in user.products]) / len(user.products) if user.products else 0

    # Monthly breakdown
    monthly_data = []
    for i in range(period_months):
        month_start = start_date + timedelta(days=30 * i)
        month_end = month_start + timedelta(days=30)

        month_orders = [o for o in seller_orders if month_start <= o.created_at < month_end]
        month_revenue = sum([o.final_amount for o in month_orders if o.order_status == "Delivered"])

        monthly_data.append({
            "month": month_start.strftime("%b %Y"),
            "orders": len(month_orders),
            "revenue": round(month_revenue, 2)
        })

    return {
        "user_id": user_id,
        "period_months": period_months,
        "trust_score": user.trust_score,
        "trust_coins": user.trust_coins,
        "trust_badge": user.trust_badge,
        "products": {
            "total": total_products,
            "active": active_products
        },
        "sales": {
            "total_orders": len(seller_orders),
            "completed_orders": len(completed_sales),
            "total_revenue": round(total_revenue, 2),
            "completion_rate": round(completion_rate, 1)
        },
        "purchases": {
            "total_orders": buyer_orders,
            "total_amount": round(float(total_purchases), 2)
        },
        "avg_rating": round(avg_rating, 1),
        "monthly_breakdown": monthly_data
    }

async def get_top_performers(limit: int = 20,
                            district: Optional[str] = None,
                            period: str = "month",
                            db: Session = None) -> List[Dict]:
    """
    Get top performing SHGs

    Args:
        limit: Number of performers to return
        district: Filter by district
        period: Time period (week, month, quarter)
        db: Database session

    Returns:
        List of top performers
    """
    # Calculate period
    if period == "week":
        start_date = datetime.now() - timedelta(days=7)
    elif period == "quarter":
        start_date = datetime.now() - timedelta(days=90)
    else:
        start_date = datetime.now() - timedelta(days=30)

    # Build query
    query = db.query(models.User).filter(models.User.role == "SHG")

    if district:
        query = query.filter(models.User.district == district)

    users = query.all()

    # Calculate performance for each user
    performers = []
    for user in users:
        # Get revenue in period
        orders = db.query(func.sum(models.Order.final_amount)).filter(
            and_(
                models.Order.seller_id == user.id,
                models.Order.created_at >= start_date,
                models.Order.order_status == "Delivered"
            )
        ).scalar() or 0

        if orders > 0:
            performers.append({
                "user_id": user.id,
                "name": user.name,
                "district": user.district,
                "revenue": round(float(orders), 2),
                "trust_score": user.trust_score,
                "trust_badge": user.trust_badge,
                "products_count": len([p for p in user.products if p.status == "Active"])
            })

    # Sort by revenue
    performers.sort(key=lambda x: x["revenue"], reverse=True)

    return performers[:limit]

async def get_category_analytics(db: Session = None) -> List[Dict]:
    """
    Get analytics by product category

    Args:
        db: Database session

    Returns:
        Category analytics
    """
    categories = ["Handicrafts", "Food Products", "Textiles", "Pickles", "Spices", "Handmade Baskets"]

    analytics = []
    for category in categories:
        products = db.query(models.Product).filter(
            models.Product.category == category
        ).all()

        product_ids = [p.id for p in products]

        # Get orders for these products
        orders = db.query(func.sum(models.Order.final_amount)).join(
            models.OrderItem
        ).filter(
            models.OrderItem.product_id.in_(product_ids)
        ).scalar() or 0

        analytics.append({
            "category": category,
            "total_products": len(products),
            "active_products": len([p for p in products if p.status == "Active"]),
            "total_revenue": round(float(orders), 2)
        })

    # Sort by revenue
    analytics.sort(key=lambda x: x["total_revenue"], reverse=True)

    return analytics

async def get_trust_distribution(db: Session = None) -> Dict:
    """
    Get distribution of trust scores

    Args:
        db: Database session

    Returns:
        Trust score distribution
    """
    users = db.query(models.User).filter(models.User.role == "SHG").all()

    if not users:
        return {
            "total_users": 0,
            "bronze": 0,
            "silver": 0,
            "gold": 0,
            "average_score": 0
        }

    # Count badges
    bronze = len([u for u in users if u.trust_badge == "Bronze"])
    silver = len([u for u in users if u.trust_badge == "Silver"])
    gold = len([u for u in users if u.trust_badge == "Gold"])

    # Calculate average
    avg_score = sum([u.trust_score for u in users]) / len(users)

    return {
        "total_users": len(users),
        "bronze": bronze,
        "silver": silver,
        "gold": gold,
        "average_score": round(avg_score, 1),
        "distribution": [
            {"badge": "Bronze", "count": bronze, "percentage": round(bronze / len(users) * 100, 1)},
            {"badge": "Silver", "count": silver, "percentage": round(silver / len(users) * 100, 1)},
            {"badge": "Gold", "count": gold, "percentage": round(gold / len(users) * 100, 1)}
        ]
    }

async def generate_report(report_type: str,
                         filters: Dict,
                         date_range: Optional[Dict] = None,
                         db: Session = None) -> Dict:
    """
    Generate analytics report

    Args:
        report_type: Type of report (user, federation, district, market)
        filters: Report filters
        date_range: Date range for report
        db: Database session

    Returns:
        Generated report
    """
    report_id = f"RPT{datetime.now().strftime('%Y%m%d%H%M%S')}"

    # Gather data based on report type
    if report_type == "user":
        user_id = filters.get("user_id")
        data = await get_user_analytics(user_id, 6, db)

    elif report_type == "federation":
        federation_id = filters.get("federation_id")
        from .community_service import get_federation_stats
        data = await get_federation_stats(federation_id, "TLF", db)

    elif report_type == "district":
        district = filters.get("district")
        all_districts = await get_district_stats(db)
        data = next((d for d in all_districts if d["district"] == district), None)

    elif report_type == "market":
        data = await get_category_analytics(db)

    else:
        data = await get_dashboard_stats(db=db)

    return {
        "report_id": report_id,
        "report_type": report_type,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "filters": filters,
        "data": data
    }
