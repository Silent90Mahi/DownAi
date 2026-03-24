"""
WebSocket Connection Manager
Handles real-time bidirectional communication for live updates
"""
import json
import asyncio
from typing import Dict, Set, Optional, List
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from core.logging import get_logger
from core.config import settings

logger = get_logger(__name__)


class ConnectionManager:
    """Manages WebSocket connections and broadcasts"""

    def __init__(self):
        # Active connections by user_id
        self.active_connections: Dict[int, WebSocket] = {}

        # Connections by room (for multi-user broadcasts)
        self.rooms: Dict[str, Set[int]] = {}

        # User subscriptions (which rooms they're in)
        self.user_rooms: Dict[int, Set[str]] = {}

        logger.info("WebSocket connection manager initialized")

    async def connect(self, websocket: WebSocket, user_id: int):
        """Accept and register a new connection"""
        await websocket.accept()
        self.active_connections[user_id] = websocket
        self.user_rooms[user_id] = set()

        # Add to personal room
        await self.join_room(user_id, f"user_{user_id}")

        logger.info(f"WebSocket connected: user_{user_id}")

        # Send welcome message
        await self.send_personal_message({
            "type": "connected",
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "message": "WebSocket connection established"
        }, user_id)

    async def disconnect(self, user_id: int):
        """Remove connection and cleanup"""
        if user_id in self.active_connections:
            del self.active_connections[user_id]

        # Remove from all rooms
        if user_id in self.user_rooms:
            for room in self.user_rooms[user_id]:
                if room in self.rooms and user_id in self.rooms[room]:
                    self.rooms[room].discard(user_id)
                    if not self.rooms[room]:
                        del self.rooms[room]
            del self.user_rooms[user_id]

        logger.info(f"WebSocket disconnected: user_{user_id}")

    async def join_room(self, user_id: int, room: str):
        """Add user to a room for broadcasts"""
        if room not in self.rooms:
            self.rooms[room] = set()

        self.rooms[room].add(user_id)

        if user_id not in self.user_rooms:
            self.user_rooms[user_id] = set()
        self.user_rooms[user_id].add(room)

        logger.debug(f"user_{user_id} joined room: {room}")

    async def leave_room(self, user_id: int, room: str):
        """Remove user from a room"""
        if room in self.rooms and user_id in self.rooms[room]:
            self.rooms[room].discard(user_id)
            if not self.rooms[room]:
                del self.rooms[room]

        if user_id in self.user_rooms and room in self.user_rooms[user_id]:
            self.user_rooms[user_id].discard(room)

        logger.debug(f"user_{user_id} left room: {room}")

    async def send_personal_message(self, message: dict, user_id: int):
        """Send message to specific user"""
        if user_id in self.active_connections:
            try:
                websocket = self.active_connections[user_id]
                await websocket.send_json(message)
                return True
            except Exception as e:
                logger.error(f"Failed to send message to user_{user_id}: {e}")
                await self.disconnect(user_id)
                return False
        return False

    async def broadcast_to_room(self, message: dict, room: str, exclude_user: Optional[int] = None):
        """Broadcast message to all users in a room"""
        if room not in self.rooms:
            return 0

        sent_count = 0
        failed_users = []

        for user_id in self.rooms[room].copy():
            if exclude_user and user_id == exclude_user:
                continue

            if not await self.send_personal_message(message, user_id):
                failed_users.append(user_id)
            else:
                sent_count += 1

        if failed_users:
            logger.warning(f"Failed to send to {len(failed_users)} users in room {room}")

        return sent_count

    async def broadcast_to_all(self, message: dict, exclude_user: Optional[int] = None):
        """Broadcast message to all connected users"""
        sent_count = 0

        for user_id in list(self.active_connections.keys()):
            if exclude_user and user_id == exclude_user:
                continue

            if await self.send_personal_message(message, user_id):
                sent_count += 1

        return sent_count

    def get_connected_users(self) -> List[int]:
        """Get list of currently connected user IDs"""
        return list(self.active_connections.keys())

    def get_user_rooms(self, user_id: int) -> List[str]:
        """Get rooms a user is subscribed to"""
        return list(self.user_rooms.get(user_id, set()))

    def get_room_users(self, room: str) -> List[int]:
        """Get users in a specific room"""
        return list(self.rooms.get(room, set()))

    def is_connected(self, user_id: int) -> bool:
        """Check if user is currently connected"""
        return user_id in self.active_connections

    def get_connection_count(self) -> int:
        """Get total number of active connections"""
        return len(self.active_connections)


# Global connection manager instance
manager = ConnectionManager()


class MessageType:
    """Standard message types for WebSocket communication"""

    # Order updates
    ORDER_CREATED = "order_created"
    ORDER_UPDATED = "order_updated"
    ORDER_CANCELLED = "order_cancelled"
    ORDER_DELIVERED = "order_delivered"

    # Product updates
    PRODUCT_CREATED = "product_created"
    PRODUCT_UPDATED = "product_updated"
    PRODUCT_STATUS_CHANGED = "product_status_changed"
    PRODUCT_PRICE_CHANGED = "product_price_changed"

    # Notifications
    NOTIFICATION = "notification"
    SYSTEM_ANNOUNCEMENT = "system_announcement"

    # Chat/Negotiation
    NEW_MESSAGE = "new_message"
    NEGOTIATION_UPDATE = "negotiation_update"

    # Real-time events
    USER_PRESENCE = "user_presence"
    TYPING_INDICATOR = "typing_indicator"


async def notify_order_created(order_id: int, buyer_id: int, seller_id: int, order_data: dict):
    """Notify relevant users about new order"""
    message = {
        "type": MessageType.ORDER_CREATED,
        "order_id": order_id,
        "timestamp": datetime.now().isoformat(),
        "data": order_data
    }

    # Notify buyer
    await manager.send_personal_message(message, buyer_id)

    # Notify seller
    await manager.send_personal_message(message, seller_id)

    logger.info(f"Notified order created: order_{order_id}")


async def notify_order_updated(order_id: int, buyer_id: int, seller_id: int, update_data: dict):
    """Notify about order status update"""
    message = {
        "type": MessageType.ORDER_UPDATED,
        "order_id": order_id,
        "timestamp": datetime.now().isoformat(),
        "data": update_data
    }

    await manager.send_personal_message(message, buyer_id)
    await manager.send_personal_message(message, seller_id)

    logger.info(f"Notified order updated: order_{order_id}")


async def notify_product_created(product_id: int, seller_id: int, product_data: dict):
    """Broadcast new product listing"""
    message = {
        "type": MessageType.PRODUCT_CREATED,
        "product_id": product_id,
        "timestamp": datetime.now().isoformat(),
        "data": product_data
    }

    # Broadcast to all users
    await manager.broadcast_to_all(message)

    logger.info(f"Broadcasted product created: product_{product_id}")


async def notify_notification(user_id: int, notification: dict):
    """Send notification to user"""
    message = {
        "type": MessageType.NOTIFICATION,
        "notification_id": notification.get("id"),
        "timestamp": datetime.now().isoformat(),
        "data": notification
    }

    await manager.send_personal_message(message, user_id)

    logger.info(f"Sent notification to user_{user_id}")


async def notify_new_message(
    conversation_id: int,
    sender_id: int,
    receiver_id: int,
    message_data: dict
):
    """Notify about new message"""
    message = {
        "type": MessageType.NEW_MESSAGE,
        "conversation_id": conversation_id,
        "sender_id": sender_id,
        "timestamp": datetime.now().isoformat(),
        "data": message_data
    }

    await manager.send_personal_message(message, receiver_id)

    logger.info(f"Notified new message in conversation_{conversation_id}")


async def notify_price_update(
    product_id: int,
    seller_id: int,
    old_price: float,
    new_price: float
):
    """Broadcast price update for product"""
    message = {
        "type": MessageType.PRODUCT_PRICE_CHANGED,
        "product_id": product_id,
        "seller_id": seller_id,
        "timestamp": datetime.now().isoformat(),
        "data": {
            "old_price": old_price,
            "new_price": new_price,
            "discount_percent": round((old_price - new_price) / old_price * 100, 2)
        }
    }

    # Broadcast to all users (price changes are important)
    await manager.broadcast_to_all(message)

    logger.info(f"Broadcasted price update: product_{product_id} ₹{old_price} → ₹{new_price}")


async def notify_user_presence(user_id: int, status: str):
    """Notify about user presence status (online/offline)"""
    message = {
        "type": MessageType.USER_PRESENCE,
        "user_id": user_id,
        "timestamp": datetime.now().isoformat(),
        "data": {
            "status": status  # "online" or "offline"
        }
    }

    # Broadcast to all users
    await manager.broadcast_to_all(message, exclude_user=user_id)

    logger.info(f"Broadcasted user presence: user_{user_id} → {status}")


async def notify_product_created(product_id: int, seller_id: int, product_data: dict):
    """Broadcast new product creation to all users"""
    message = {
        "type": MessageType.PRODUCT_CREATED,
        "product_id": product_id,
        "seller_id": seller_id,
        "timestamp": datetime.now().isoformat(),
        "data": product_data
    }

    await manager.broadcast_to_all(message)

    logger.info(f"Broadcasted product created: product_{product_id}")


async def notify_product_updated(product_id: int, seller_id: int, update_data: dict):
    """Broadcast product update to all users"""
    message = {
        "type": MessageType.PRODUCT_UPDATED,
        "product_id": product_id,
        "seller_id": seller_id,
        "timestamp": datetime.now().isoformat(),
        "data": update_data
    }

    await manager.broadcast_to_all(message)

    logger.info(f"Broadcasted product updated: product_{product_id}")


async def notify_product_deleted(product_id: int, seller_id: int):
    """Broadcast product deletion to all users"""
    message = {
        "type": "product_deleted",
        "product_id": product_id,
        "seller_id": seller_id,
        "timestamp": datetime.now().isoformat()
    }

    await manager.broadcast_to_all(message)

    logger.info(f"Broadcasted product deleted: product_{product_id}")


async def notify_inventory_updated(product_id: int, seller_id: int, old_stock: int, new_stock: int):
    """Broadcast inventory update"""
    message = {
        "type": "inventory_updated",
        "product_id": product_id,
        "seller_id": seller_id,
        "timestamp": datetime.now().isoformat(),
        "data": {
            "old_stock": old_stock,
            "new_stock": new_stock,
            "change": new_stock - old_stock
        }
    }

    await manager.broadcast_to_all(message)

    logger.info(f"Broadcasted inventory updated: product_{product_id} stock {old_stock} → {new_stock}")


async def broadcast_system_announcement(title: str, message: str, target_users: Optional[List[int]] = None):
    """Broadcast system announcement"""
    announcement = {
        "type": MessageType.SYSTEM_ANNOUNCEMENT,
        "timestamp": datetime.now().isoformat(),
        "data": {
            "title": title,
            "message": message,
            "priority": "info"
        }
    }

    if target_users:
        for user_id in target_users:
            await manager.send_personal_message(announcement, user_id)
    else:
        await manager.broadcast_to_all(announcement)

    logger.info(f"Broadcasted system announcement: {title}")


# Helper function to create notification payload
def create_notification(
    title: str,
    message: str,
    notification_type: str,
    action_url: Optional[str] = None,
    metadata: Optional[dict] = None
) -> dict:
    """Create standardized notification payload"""
    return {
        "title": title,
        "message": message,
        "type": notification_type,
        "action_url": action_url,
        "metadata": metadata or {},
        "read": False,
        "created_at": datetime.now().isoformat()
    }
