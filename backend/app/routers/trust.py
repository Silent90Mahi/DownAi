from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import SessionLocal
from .. import schemas
from ..routers.auth import get_current_user
from .. import models
from ..services import trust_service

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============================================================================
# TRUST & COMPLIANCE ENDPOINTS (Agent Vishwas)
# ============================================================================

@router.get("/score", response_model=schemas.TrustScoreBreakdown)
async def get_trust_score(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's trust score breakdown"""
    breakdown = await trust_service.calculate_trust_score(current_user.id, db)
    return breakdown

@router.get("/history", response_model=list[schemas.TrustHistoryResponse])
async def get_trust_history(
    limit: int = 50,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get trust score history"""
    history = await trust_service.get_trust_history(current_user.id, limit, db)

    return [
        schemas.TrustHistoryResponse(
            id=h["id"],
            previous_score=h["previous_score"],
            new_score=h["new_score"],
            score_change=h["score_change"],
            reason=h["reason"],
            reference_type=h.get("reference_type"),
            reference_id=h.get("reference_id"),
            badge_change=h.get("badge_change"),
            created_at=datetime.fromisoformat(h["created_at"])
        )
        for h in history
    ]

@router.get("/coins", response_model=schemas.CoinWalletResponse)
async def get_coin_wallet(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get trust coin wallet details"""
    wallet = await trust_service.get_coin_wallet(current_user.id, db)

    return schemas.CoinWalletResponse(
        balance=wallet["balance"],
        total_earned=wallet["total_earned"],
        total_spent=wallet["total_spent"],
        recent_transactions=[
            schemas.CoinTransactionResponse(
                id=t["id"],
                amount=t["amount"],
                transaction_type=t["transaction_type"],
                source=t["source"],
                description=t.get("description"),
                reference_type=t.get("reference_type"),
                reference_id=t.get("reference_id"),
                balance_after=t["balance_after"],
                created_at=datetime.fromisoformat(t["created_at"])
            )
            for t in wallet["recent_transactions"]
        ]
    )

@router.get("/leaderboard")
async def get_trust_leaderboard(
    limit: int = 50,
    district: str = None,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get trust score leaderboard"""
    leaderboard = await trust_service.get_trust_leaderboard(limit, district, db)
    return leaderboard

@router.post("/redeem")
async def redeem_coins(
    amount: int,
    reward_type: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Redeem trust coins for rewards"""
    try:
        result = await trust_service.redeem_coins(current_user.id, amount, reward_type, db)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/audit-logs")
async def get_audit_logs(
    entity_type: str = None,
    limit: int = 100,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get audit logs"""
    logs = await trust_service.get_audit_logs(current_user.id, entity_type, limit, db)
    return logs
