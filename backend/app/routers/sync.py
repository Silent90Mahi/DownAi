from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from ..database import SessionLocal
from .. import schemas
from ..routers.auth import get_current_user
from .. import models
from ..services import sync_service

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/upload", response_model=schemas.SyncUploadResponse)
async def upload_offline_data(
    request: schemas.SyncUploadRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload offline data from client
    
    Accepts a batch of sync records and processes them.
    Returns count of accepted records and conflicts.
    """
    records_data = []
    for record in request.records:
        records_data.append({
            "entity_type": record.entity_type,
            "entity_id": record.entity_id,
            "action": record.action.value,
            "data": record.data,
            "client_timestamp": record.client_timestamp
        })
    
    accepted, conflicts, details = await sync_service.process_offline_changes(
        user_id=current_user.id,
        records=records_data,
        db=db
    )
    
    return schemas.SyncUploadResponse(
        accepted=accepted,
        conflicts=conflicts,
        details=[schemas.SyncUploadDetail(**d) for d in details]
    )


@router.get("/pending", response_model=list[schemas.SyncRecordResponse])
async def get_pending_sync_records(
    user_id: Optional[int] = Query(None, description="Filter by user ID (admin only)"),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get pending sync records
    
    Returns all records that are pending synchronization.
    Regular users can only see their own pending records.
    """
    target_user_id = user_id if user_id and current_user.role == models.UserRole.ADMIN else current_user.id
    
    records = await sync_service.get_pending_records(
        user_id=target_user_id,
        db=db
    )
    
    return [
        schemas.SyncRecordResponse(
            id=r.id,
            user_id=r.user_id,
            entity_type=r.entity_type,
            entity_id=r.entity_id,
            action=r.action.value,
            data=r.data,
            server_data=r.server_data,
            sync_status=r.sync_status.value,
            client_timestamp=r.client_timestamp,
            created_at=r.created_at,
            synced_at=r.synced_at
        )
        for r in records
    ]


@router.post("/resolve", response_model=schemas.SyncRecordResponse)
async def resolve_sync_conflict(
    request: schemas.SyncResolveRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Resolve sync conflicts
    
    Accepts resolution type and applies it to the conflicting record.
    Resolution types:
    - server_wins: Server data overwrites client
    - client_wins: Client data overwrites server
    - merge: Combine both (non-conflicting fields)
    """
    resolved = await sync_service.resolve_conflict(
        record_id=request.record_id,
        resolution=request.resolution.value,
        user_id=current_user.id,
        db=db
    )
    
    if not resolved:
        raise HTTPException(
            status_code=404,
            detail="Conflict record not found or not accessible"
        )
    
    return schemas.SyncRecordResponse(
        id=resolved.id,
        user_id=resolved.user_id,
        entity_type=resolved.entity_type,
        entity_id=resolved.entity_id,
        action=resolved.action.value,
        data=resolved.data,
        server_data=resolved.server_data,
        sync_status=resolved.sync_status.value,
        client_timestamp=resolved.client_timestamp,
        created_at=resolved.created_at,
        synced_at=resolved.synced_at
    )


@router.get("/status", response_model=schemas.SyncStatusResponse)
async def get_sync_status(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get sync status for user
    
    Returns:
    - pending_count: Number of records pending sync
    - last_sync: Timestamp of last successful sync
    - conflicts_count: Number of unresolved conflicts
    """
    status = await sync_service.get_sync_status(
        user_id=current_user.id,
        db=db
    )
    
    return schemas.SyncStatusResponse(
        pending_count=status["pending_count"],
        last_sync=status["last_sync"],
        conflicts_count=status["conflicts_count"]
    )


@router.post("/delta", response_model=schemas.SyncDeltaResponse)
async def delta_sync(
    request: schemas.SyncDeltaRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delta sync - get only changes since timestamp
    
    Returns all synced changes for the user since the given timestamp.
    Useful for incremental sync after offline period.
    """
    changes = await sync_service.get_delta_changes(
        user_id=current_user.id,
        since=request.since,
        db=db
    )
    
    return schemas.SyncDeltaResponse(
        changes=[
            schemas.SyncRecordResponse(
                id=c.id,
                user_id=c.user_id,
                entity_type=c.entity_type,
                entity_id=c.entity_id,
                action=c.action.value,
                data=c.data,
                server_data=c.server_data,
                sync_status=c.sync_status.value,
                client_timestamp=c.client_timestamp,
                created_at=c.created_at,
                synced_at=c.synced_at
            )
            for c in changes
        ],
        timestamp=datetime.utcnow()
    )
