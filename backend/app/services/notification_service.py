"""
Notification Service
Manages user notifications and alerts
"""
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from .. import models

async def create_notification(user_id: int,
                             title: str,
                             message: str,
                             notification_type: str,
                             reference_type: Optional[str] = None,
                             reference_id: Optional[int] = None,
                             action_url: Optional[str] = None,
                             action_label: Optional[str] = None,
                             db: Session = None) -> Dict:
    """
    Create a new notification

    Args:
        user_id: User ID
        title: Notification title
        message: Notification message
        notification_type: Type (order, payment, trust, alert, etc.)
        reference_type: Reference entity type
        reference_id: Reference entity ID
        action_url: Action URL
        action_label: Action button label
        db: Database session

    Returns:
        Created notification
    """
    notification = models.Notification(
        user_id=user_id,
        title=title,
        message=message,
        notification_type=notification_type,
        reference_type=reference_type,
        reference_id=reference_id,
        action_url=action_url,
        action_label=action_label,
        is_read=False,
        created_at=datetime.now()
    )

    db.add(notification)
    db.commit()
    db.refresh(notification)

    return {
        "id": notification.id,
        "title": notification.title,
        "message": notification.message,
        "notification_type": notification.notification_type,
        "is_read": notification.is_read,
        "created_at": notification.created_at.strftime("%Y-%m-%d %H:%M:%S")
    }

async def get_user_notifications(user_id: int,
                                 unread_only: bool = False,
                                 limit: int = 50,
                                 db: Session = None) -> List[Dict]:
    """
    Get notifications for a user

    Args:
        user_id: User ID
        unread_only: Only fetch unread notifications
        limit: Maximum notifications to return
        db: Database session

    Returns:
        List of notifications
    """
    query = db.query(models.Notification).filter(
        models.Notification.user_id == user_id
    )

    if unread_only:
        query = query.filter(models.Notification.is_read == False)

    notifications = query.order_by(
        models.Notification.created_at.desc()
    ).limit(limit).all()

    return [
        {
            "id": n.id,
            "title": n.title,
            "message": n.message,
            "notification_type": n.notification_type,
            "reference_type": n.reference_type,
            "reference_id": n.reference_id,
            "is_read": n.is_read,
            "action_url": n.action_url,
            "action_label": n.action_label,
            "created_at": n.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }
        for n in notifications
    ]

async def mark_notification_read(notification_id: int,
                                user_id: int,
                                db: Session = None) -> Dict:
    """
    Mark a notification as read

    Args:
        notification_id: Notification ID
        user_id: User ID (for verification)
        db: Database session

    Returns:
        Updated notification
    """
    notification = db.query(models.Notification).filter(
        and_(
            models.Notification.id == notification_id,
            models.Notification.user_id == user_id
        )
    ).first()

    if not notification:
        raise ValueError("Notification not found")

    notification.is_read = True
    notification.read_at = datetime.now()

    db.commit()

    return {
        "id": notification.id,
        "is_read": True,
        "read_at": notification.read_at.strftime("%Y-%m-%d %H:%M:%S")
    }

async def mark_all_read(user_id: int,
                       db: Session = None) -> Dict:
    """
    Mark all notifications as read for a user

    Args:
        user_id: User ID
        db: Database session

    Returns:
        Number of notifications marked
    """
    count = db.query(models.Notification).filter(
        and_(
            models.Notification.user_id == user_id,
            models.Notification.is_read == False
        )
    ).update({
        "is_read": True,
        "read_at": datetime.now()
    })

    db.commit()

    return {
        "marked_count": count,
        "message": f"Marked {count} notifications as read"
    }

async def get_unread_count(user_id: int,
                           db: Session = None) -> int:
    """
    Get count of unread notifications

    Args:
        user_id: User ID
        db: Database session

    Returns:
        Unread notification count
    """
    count = db.query(models.Notification).filter(
        and_(
            models.Notification.user_id == user_id,
            models.Notification.is_read == False
        )
    ).count()

    return count

async def delete_old_notifications(days_old: int = 90,
                                  db: Session = None) -> Dict:
    """
    Delete notifications older than specified days

    Args:
        days_old: Delete notifications older than this
        db: Database session

    Returns:
        Deletion result
    """
    cutoff_date = datetime.now() - timedelta(days=days_old)

    deleted = db.query(models.Notification).filter(
        models.Notification.created_at < cutoff_date
    ).delete()

    db.commit()

    return {
        "deleted_count": deleted,
        "cutoff_date": cutoff_date.strftime("%Y-%m-%d")
    }

async def notify_order_status_change(order_id: int,
                                     new_status: str,
                                     db: Session = None) -> List[Dict]:
    """
    Notify buyer and seller about order status change

    Args:
        order_id: Order ID
        new_status: New order status
        db: Database session

    Returns:
        Created notifications
    """
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise ValueError("Order not found")

    notifications = []

    # Status messages
    status_messages = {
        "Confirmed": "Your order has been confirmed!",
        "Shipped": f"Your order has been shipped. Tracking: {order.tracking_number or 'Coming soon'}",
        "Delivered": "Your order has been delivered. Thank you for your purchase!",
        "Cancelled": "Your order has been cancelled."
    }

    message = status_messages.get(new_status, f"Order status updated to: {new_status}")

    # Notify buyer
    buyer_notif = await create_notification(
        order.buyer_id,
        f"Order {order.order_number} {new_status}",
        message,
        "order",
        "order",
        order.id,
        f"/orders/{order.id}",
        "View Order",
        db
    )
    notifications.append(buyer_notif)

    # Notify seller for certain statuses
    if new_status in ["Confirmed", "Delivered"]:
        seller_message = f"Order {order.order_number} {new_status.lower()}"
        seller_notif = await create_notification(
            order.seller_id,
            f"Order Update: {new_status}",
            seller_message,
            "order",
            "order",
            order.id,
            f"/orders/{order.id}",
            "View Order",
            db
        )
        notifications.append(seller_notif)

    return notifications

async def notify_trust_score_update(user_id: int,
                                    new_score: float,
                                    badge_change: Optional[str] = None,
                                    db: Session = None) -> Dict:
    """
    Notify user about trust score update

    Args:
        user_id: User ID
        new_score: New trust score
        badge_change: Badge change if any
        db: Database session

    Returns:
        Created notification
    """
    title = "Trust Score Updated!"

    if badge_change:
        message = f"Congratulations! Your trust score is now {new_score} and you've earned the {badge_change.split(' → ')[1] if ' → ' in badge_change else badge_change} badge!"
    else:
        message = f"Your trust score has been updated to {new_score}. Keep up the good work!"

    return await create_notification(
        user_id,
        title,
        message,
        "trust",
        "user",
        user_id,
        "/profile",
        "View Profile",
        db
    )

async def notify_coins_awarded(user_id: int,
                               amount: int,
                               reason: str,
                               reference_type: Optional[str] = None,
                               reference_id: Optional[int] = None,
                               db: Session = None) -> Dict:
    """
    Notify user about coins awarded

    Args:
        user_id: User ID
        amount: Coins awarded
        reason: Reason for awarding
        reference_type: Reference type
        reference_id: Reference ID
        db: Database session

    Returns:
        Created notification
    """
    message = f"You've earned {amount} Trust Coins! {reason}"

    return await create_notification(
        user_id,
        f"{amount} Trust Coins Earned!",
        message,
        "coins",
        reference_type,
        reference_id,
        "/wallet",
        "View Wallet",
        db
    )

async def notify_buyer_match(user_id: int,
                            product_name: str,
                            match_count: int,
                            db: Session = None) -> Dict:
    """
    Notify user about buyer matches

    Args:
        user_id: User ID
        product_name: Product name
        match_count: Number of matches
        db: Database session

    Returns:
        Created notification
    """
    message = f"Agent Jodi found {match_count} potential buyer(s) for your product '{product_name}'. View matches and connect!"

    return await create_notification(
        user_id,
        f"Buyer Matches Found for {product_name}",
        message,
        "buyer_match",
        "product",
        None,
        "/matches",
        "View Matches",
        db
    )

async def notify_bulk_request_joined(request_id: int,
                                    user_id: int,
                                    title: str,
                                    db: Session = None) -> Dict:
    """
    Notify user about new participant in their bulk request

    Args:
        request_id: Bulk request ID
        user_id: Request creator ID
        title: Request title
        db: Database session

    Returns:
        Created notification
    """
    message = f"A new SHG has joined your bulk request '{title}'. View progress!"

    return await create_notification(
        user_id,
        "New Participant Joined!",
        message,
        "bulk_request",
        "bulk_request",
        request_id,
        f"/bulk-requests/{request_id}",
        "View Request",
        db
    )

async def send_bulk_announcement(title: str,
                                message: str,
                                target_roles: List[str],
                                district: Optional[str] = None,
                                db: Session = None) -> Dict:
    """
    Send announcement to multiple users

    Args:
        title: Announcement title
        message: Announcement message
        target_roles: Target user roles
        district: Filter by district
        db: Database session

    Returns:
        Send result
    """
    # Build recipient query
    query = db.query(models.User).filter(
        models.User.role.in_(target_roles)
    )

    if district:
        query = query.filter(models.User.district == district)

    recipients = query.all()

    # Create notifications
    notifications_created = 0
    for recipient in recipients:
        notification = models.Notification(
            user_id=recipient.id,
            title=title,
            message=message,
            notification_type="announcement",
            created_at=datetime.now()
        )
        db.add(notification)
        notifications_created += 1

    db.commit()

    return {
        "success": True,
        "recipients_count": notifications_created,
        "target_roles": target_roles,
        "district": district
    }
