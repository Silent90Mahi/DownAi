"""
WebSocket Router
Handles WebSocket connections and real-time message routing
"""
import json
from typing import Dict
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db
from ..routers.auth import get_current_user_optional, get_current_user
from core.websocket import (
    manager,
    MessageType,
    notify_user_presence,
    create_notification
)
from core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint for real-time updates

    Query Parameters:
        token: JWT authentication token

    Message Types:
        - Client → Server:
          * ping: Heartbeat
          * join_room: Join a specific room
          * leave_room: Leave a room
          * typing_indicator: Typing status
          * mark_read: Mark message as read

        - Server → Client:
          * connected: Connection established
          * order_created: New order
          * order_updated: Order status change
          * product_created: New product listing
          * notification: New notification
          * new_message: New chat message
          * user_presence: User online/offline
    """
    # Authenticate user from token
    try:
        from ..routers.auth import get_current_user

        # Create a mock request object for authentication
        from fastapi import Request
        from starlette.datastructures import Headers

        # We'll try to authenticate, if it fails, close connection
        user = None
        try:
            # This will work if token is valid
            user = await get_current_user(token, db)
        except Exception as e:
            logger.warning(f"WebSocket authentication failed: {e}")
            await websocket.close(code=1008, reason="Authentication failed")
            return

        if not user:
            await websocket.close(code=1008, reason="Invalid token")
            return

        # Connect the user
        await manager.connect(websocket, user.id)

        # Notify others that user is online
        await notify_user_presence(user.id, "online")

        try:
            while True:
                # Receive message from client
                data = await websocket.receive_text()
                message_data = json.loads(data)

                # Handle different message types
                await handle_websocket_message(user.id, message_data, websocket, db)

        except WebSocketDisconnect:
            await manager.disconnect(user.id)
            await notify_user_presence(user.id, "offline")
            logger.info(f"WebSocket disconnected: user_{user.id}")

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await websocket.close(code=1011, reason="Internal server error")
        except:
            pass


async def handle_websocket_message(
    user_id: int,
    message_data: dict,
    websocket: WebSocket,
    db: Session
):
    """Handle incoming WebSocket message from client"""

    message_type = message_data.get("type")
    data = message_data.get("data", {})

    try:
        if message_type == "ping":
            # Heartbeat - respond with pong
            await websocket.send_json({
                "type": "pong",
                "timestamp": message_data.get("timestamp")
            })

        elif message_type == "join_room":
            # Join a room for broadcasts
            room = data.get("room")
            if room:
                await manager.join_room(user_id, room)
                await websocket.send_json({
                    "type": "room_joined",
                    "room": room,
                    "timestamp": message_data.get("timestamp")
                })
                logger.debug(f"user_{user_id} joined room: {room}")

        elif message_type == "leave_room":
            # Leave a room
            room = data.get("room")
            if room:
                await manager.leave_room(user_id, room)
                await websocket.send_json({
                    "type": "room_left",
                    "room": room,
                    "timestamp": message_data.get("timestamp")
                })
                logger.debug(f"user_{user_id} left room: {room}")

        elif message_type == "typing_indicator":
            # Broadcast typing indicator
            conversation_id = data.get("conversation_id")
            is_typing = data.get("is_typing", False)

            if conversation_id:
                room = f"conversation_{conversation_id}"
                message = {
                    "type": MessageType.TYPING_INDICATOR,
                    "user_id": user_id,
                    "conversation_id": conversation_id,
                    "is_typing": is_typing,
                    "timestamp": message_data.get("timestamp")
                }
                await manager.broadcast_to_room(message, room, exclude_user=user_id)

        elif message_type == "mark_read":
            # Mark messages/conversations as read
            conversation_id = data.get("conversation_id")
            if conversation_id:
                # Update in database
                messages = db.query(models.Message).filter(
                    models.Message.conversation_id == conversation_id,
                    models.Message.sender_id != user_id,
                    models.Message.read == False
                ).all()

                for msg in messages:
                    msg.read = True

                db.commit()

                # Notify sender that messages were read
                if messages:
                    sender_ids = set(m.sender_id for m in messages)
                    for sender_id in sender_ids:
                        await manager.send_personal_message({
                            "type": "messages_read",
                            "conversation_id": conversation_id,
                            "reader_id": user_id,
                            "timestamp": message_data.get("timestamp")
                        }, sender_id)

        else:
            logger.warning(f"Unknown WebSocket message type: {message_type}")

    except Exception as e:
        logger.error(f"Error handling WebSocket message: {e}")


@router.get("/ws/status")
async def websocket_status(current_user: models.User = Depends(get_current_user_optional)):
    """Get WebSocket connection status"""
    return {
        "enabled": True,  # From settings
        "is_connected": manager.is_connected(current_user.id) if current_user else False,
        "connected_users": manager.get_connection_count(),
        "user_rooms": manager.get_user_rooms(current_user.id) if current_user else []
    }


@router.get("/ws/stats")
async def websocket_stats(current_user: models.User = Depends(get_current_user)):
    """Get WebSocket statistics (admin only)"""
    # Check if user is admin
    if current_user.role != models.UserRole.ADMIN:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Admin access required")

    return {
        "connected_users": manager.get_connection_count(),
        "active_connections": len(manager.active_connections),
        "total_rooms": len(manager.rooms),
        "connected_user_ids": manager.get_connected_users()
    }


@router.post("/ws/broadcast")
async def broadcast_message(
    broadcast: schemas.BroadcastCreate,
    current_user: models.User = Depends(get_current_user)
):
    """
    Broadcast a message to other users

    Args:
        broadcast: Broadcast details (message, target_type, target_users)

    Broadcast Types:
        - all: Send to all connected users
        - users: Send to specific user IDs
        - room: Send to all users in a room
    """
    message = {
        "type": MessageType.NOTIFICATION,
        "sender_id": current_user.id,
        "sender_name": current_user.name,
        "timestamp": broadcast.timestamp,
        "data": {
            "title": broadcast.title,
            "message": broadcast.message,
            "type": broadcast.notification_type or "info"
        }
    }

    if broadcast.target_type == "all":
        count = await manager.broadcast_to_all(message)
    elif broadcast.target_type == "users" and broadcast.target_users:
        count = 0
        for user_id in broadcast.target_users:
            if await manager.send_personal_message(message, user_id):
                count += 1
    elif broadcast.target_type == "room" and broadcast.target_room:
        count = await manager.broadcast_to_room(message, broadcast.target_room)
    else:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Invalid broadcast parameters")

    return {
        "success": True,
        "recipients": count,
        "message": "Broadcast sent successfully"
    }


@router.post("/ws/notify/user/{user_id}")
async def notify_user(
    user_id: int,
    notification: schemas.NotificationCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send notification to specific user via WebSocket"""
    # Verify target user exists
    target_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not target_user:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="User not found")

    # Create notification record in database
    db_notification = models.Notification(
        user_id=user_id,
        title=notification.title,
        message=notification.message,
        notification_type=notification.type,
        action_url=notification.action_url,
        metadata=notification.metadata or {}
    )
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)

    # Send via WebSocket
    await manager.send_personal_message({
        "type": MessageType.NOTIFICATION,
        "notification_id": db_notification.id,
        "timestamp": db_notification.created_at.isoformat(),
        "data": {
            "title": notification.title,
            "message": notification.message,
            "type": notification.type,
            "action_url": notification.action_url,
            "metadata": notification.metadata
        }
    }, user_id)

    return {
        "success": True,
        "notification_id": db_notification.id,
        "delivered": manager.is_connected(user_id)
    }


@router.get("/ws/rooms")
async def get_active_rooms(current_user: models.User = Depends(get_current_user)):
    """Get list of active chat rooms and their user counts"""
    rooms = []
    for room_name, user_ids in manager.rooms.items():
        rooms.append({
            "name": room_name,
            "user_count": len(user_ids),
            "users": list(user_ids)
        })

    return {
        "total_rooms": len(rooms),
        "rooms": rooms
    }
