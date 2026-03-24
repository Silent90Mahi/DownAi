"""
Offline-First Sync Service
Handles synchronization of offline data with conflict detection and resolution
"""
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from .. import models
from ..models import SyncStatus, SyncAction


async def process_offline_changes(
    user_id: int,
    records: List[Dict[str, Any]],
    db: Session
) -> Tuple[int, int, List[Dict[str, Any]]]:
    """
    Process incoming offline changes from client
    
    Args:
        user_id: User ID
        records: List of sync records from client
        db: Database session
        
    Returns:
        Tuple of (accepted_count, conflicts_count, details)
    """
    accepted = 0
    conflicts = 0
    details = []
    
    for record in records:
        entity_type = record.get("entity_type")
        entity_id = record.get("entity_id")
        action = record.get("action")
        data = record.get("data", {})
        client_timestamp = record.get("client_timestamp")
        
        conflict_info = await detect_conflicts(
            user_id=user_id,
            entity_type=entity_type,
            entity_id=entity_id,
            client_data=data,
            client_timestamp=client_timestamp,
            db=db
        )
        
        if conflict_info:
            sync_record = models.SyncRecord(
                user_id=user_id,
                entity_type=entity_type,
                entity_id=entity_id,
                action=SyncAction(action),
                data=data,
                server_data=conflict_info.get("server_data"),
                sync_status=SyncStatus.CONFLICT,
                client_timestamp=client_timestamp
            )
            db.add(sync_record)
            db.commit()
            db.refresh(sync_record)
            
            conflicts += 1
            details.append({
                "record_id": sync_record.id,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "status": "conflict",
                "message": "Conflict detected with server data"
            })
        else:
            success = await _apply_change(
                user_id=user_id,
                entity_type=entity_type,
                entity_id=entity_id,
                action=action,
                data=data,
                db=db
            )
            
            if success:
                sync_record = models.SyncRecord(
                    user_id=user_id,
                    entity_type=entity_type,
                    entity_id=entity_id,
                    action=SyncAction(action),
                    data=data,
                    sync_status=SyncStatus.SYNCED,
                    client_timestamp=client_timestamp,
                    synced_at=datetime.utcnow()
                )
                db.add(sync_record)
                db.commit()
                db.refresh(sync_record)
                
                accepted += 1
                details.append({
                    "record_id": sync_record.id,
                    "entity_type": entity_type,
                    "entity_id": entity_id,
                    "status": "synced",
                    "message": None
                })
            else:
                sync_record = models.SyncRecord(
                    user_id=user_id,
                    entity_type=entity_type,
                    entity_id=entity_id,
                    action=SyncAction(action),
                    data=data,
                    sync_status=SyncStatus.PENDING,
                    client_timestamp=client_timestamp
                )
                db.add(sync_record)
                db.commit()
                db.refresh(sync_record)
                
                details.append({
                    "record_id": sync_record.id,
                    "entity_type": entity_type,
                    "entity_id": entity_id,
                    "status": "pending",
                    "message": "Could not apply change, saved as pending"
                })
    
    return accepted, conflicts, details


async def detect_conflicts(
    user_id: int,
    entity_type: str,
    entity_id: int,
    client_data: Dict[str, Any],
    client_timestamp: Optional[datetime],
    db: Session
) -> Optional[Dict[str, Any]]:
    """
    Detect conflicts between client and server data
    
    Args:
        user_id: User ID
        entity_type: Type of entity (product, order, etc.)
        entity_id: Entity ID
        client_data: Client data
        client_timestamp: Timestamp from client
        db: Database session
        
    Returns:
        Conflict info if conflict exists, None otherwise
    """
    server_entity = await _get_server_entity(entity_type, entity_id, user_id, db)
    
    if not server_entity:
        return None
    
    server_updated_at = getattr(server_entity, 'updated_at', None) or getattr(server_entity, 'created_at', None)
    
    if server_updated_at and client_timestamp:
        recent_sync = db.query(models.SyncRecord).filter(
            and_(
                models.SyncRecord.user_id == user_id,
                models.SyncRecord.entity_type == entity_type,
                models.SyncRecord.entity_id == entity_id,
                models.SyncRecord.sync_status == SyncStatus.SYNCED,
                models.SyncRecord.synced_at >= server_updated_at
            )
        ).first()
        
        if recent_sync:
            return None
    
    if server_updated_at and client_timestamp and server_updated_at > client_timestamp:
        server_data = _entity_to_dict(server_entity)
        return {"server_data": server_data}
    
    return None


async def resolve_conflict(
    record_id: int,
    resolution: str,
    user_id: int,
    db: Session
) -> Optional[models.SyncRecord]:
    """
    Resolve a sync conflict
    
    Args:
        record_id: Sync record ID
        resolution: Resolution type (server_wins, client_wins, merge)
        user_id: User ID
        db: Database session
        
    Returns:
        Resolved sync record or None if not found
    """
    sync_record = db.query(models.SyncRecord).filter(
        and_(
            models.SyncRecord.id == record_id,
            models.SyncRecord.user_id == user_id,
            models.SyncRecord.sync_status == SyncStatus.CONFLICT
        )
    ).first()
    
    if not sync_record:
        return None
    
    final_data = None
    
    if resolution == "server_wins":
        final_data = sync_record.server_data
    elif resolution == "client_wins":
        final_data = sync_record.data
    elif resolution == "merge":
        final_data = _merge_data(
            client_data=sync_record.data,
            server_data=sync_record.server_data or {}
        )
    
    if final_data:
        await _apply_change(
            user_id=user_id,
            entity_type=sync_record.entity_type,
            entity_id=sync_record.entity_id,
            action=sync_record.action.value,
            data=final_data,
            db=db
        )
    
    sync_record.sync_status = SyncStatus.SYNCED
    sync_record.synced_at = datetime.utcnow()
    if final_data and resolution == "merge":
        sync_record.data = final_data
    
    db.commit()
    db.refresh(sync_record)
    
    return sync_record


async def get_delta_changes(
    user_id: int,
    since: datetime,
    db: Session
) -> List[models.SyncRecord]:
    """
    Get changes since a specific timestamp for delta sync
    
    Args:
        user_id: User ID
        since: Timestamp to get changes after
        db: Database session
        
    Returns:
        List of sync records since timestamp
    """
    changes = db.query(models.SyncRecord).filter(
        and_(
            models.SyncRecord.user_id == user_id,
            models.SyncRecord.sync_status == SyncStatus.SYNCED,
            models.SyncRecord.synced_at >= since
        )
    ).order_by(models.SyncRecord.synced_at.asc()).all()
    
    return changes


async def get_pending_records(
    user_id: int,
    db: Session
) -> List[models.SyncRecord]:
    """
    Get all pending sync records for a user
    
    Args:
        user_id: User ID
        db: Database session
        
    Returns:
        List of pending sync records
    """
    return db.query(models.SyncRecord).filter(
        and_(
            models.SyncRecord.user_id == user_id,
            models.SyncRecord.sync_status == SyncStatus.PENDING
        )
    ).order_by(models.SyncRecord.created_at.asc()).all()


async def get_sync_status(
    user_id: int,
    db: Session
) -> Dict[str, Any]:
    """
    Get sync status for a user
    
    Args:
        user_id: User ID
        db: Database session
        
    Returns:
        Dict with pending_count, last_sync, conflicts_count
    """
    pending_count = db.query(models.SyncRecord).filter(
        and_(
            models.SyncRecord.user_id == user_id,
            models.SyncRecord.sync_status == SyncStatus.PENDING
        )
    ).count()
    
    conflicts_count = db.query(models.SyncRecord).filter(
        and_(
            models.SyncRecord.user_id == user_id,
            models.SyncRecord.sync_status == SyncStatus.CONFLICT
        )
    ).count()
    
    last_sync_record = db.query(models.SyncRecord).filter(
        and_(
            models.SyncRecord.user_id == user_id,
            models.SyncRecord.sync_status == SyncStatus.SYNCED
        )
    ).order_by(models.SyncRecord.synced_at.desc()).first()
    
    last_sync = last_sync_record.synced_at if last_sync_record else None
    
    return {
        "pending_count": pending_count,
        "last_sync": last_sync,
        "conflicts_count": conflicts_count
    }


async def _get_server_entity(
    entity_type: str,
    entity_id: int,
    user_id: int,
    db: Session
) -> Optional[Any]:
    """
    Get server entity by type and ID
    
    Args:
        entity_type: Type of entity
        entity_id: Entity ID
        user_id: User ID for access control
        db: Database session
        
    Returns:
        Entity or None
    """
    entity_map = {
        "product": models.Product,
        "order": models.Order,
        "user": models.User,
        "supplier": models.Supplier,
        "buyer": models.Buyer,
        "material": models.Material,
        "bulk_request": models.BulkRequest,
        "buyer_requirement": models.BuyerRequirement,
    }
    
    model = entity_map.get(entity_type.lower())
    if not model:
        return None
    
    return db.query(model).filter(model.id == entity_id).first()


async def _apply_change(
    user_id: int,
    entity_type: str,
    entity_id: int,
    action: str,
    data: Dict[str, Any],
    db: Session
) -> bool:
    """
    Apply a change to the database
    
    Args:
        user_id: User ID
        entity_type: Type of entity
        entity_id: Entity ID
        action: Action (create, update, delete)
        data: Data to apply
        db: Database session
        
    Returns:
        True if successful, False otherwise
    """
    entity_map = {
        "product": models.Product,
        "order": models.Order,
        "supplier": models.Supplier,
        "buyer": models.Buyer,
        "material": models.Material,
        "bulk_request": models.BulkRequest,
        "buyer_requirement": models.BuyerRequirement,
    }
    
    model = entity_map.get(entity_type.lower())
    if not model:
        return False
    
    try:
        if action == "create":
            data["seller_id"] = user_id
            entity = model(**data)
            db.add(entity)
            db.commit()
            return True
            
        elif action == "update":
            entity = db.query(model).filter(model.id == entity_id).first()
            if entity:
                for key, value in data.items():
                    if hasattr(entity, key):
                        setattr(entity, key, value)
                db.commit()
                return True
            return False
            
        elif action == "delete":
            entity = db.query(model).filter(model.id == entity_id).first()
            if entity:
                db.delete(entity)
                db.commit()
                return True
            return False
            
        return False
    except Exception:
        db.rollback()
        return False


def _entity_to_dict(entity: Any) -> Dict[str, Any]:
    """
    Convert entity to dictionary
    
    Args:
        entity: Database entity
        
    Returns:
        Dictionary representation
    """
    result = {}
    for column in entity.__table__.columns:
        value = getattr(entity, column.name)
        if isinstance(value, datetime):
            value = value.isoformat()
        result[column.name] = value
    return result


def _merge_data(
    client_data: Dict[str, Any],
    server_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Merge client and server data
    
    Args:
        client_data: Client data
        server_data: Server data
        
    Returns:
        Merged data
    """
    merged = server_data.copy()
    
    non_merge_fields = {'id', 'created_at', 'updated_at', 'user_id', 'seller_id', 'buyer_id'}
    
    for key, value in client_data.items():
        if key not in non_merge_fields:
            if key not in server_data or value is not None:
                merged[key] = value
    
    return merged
