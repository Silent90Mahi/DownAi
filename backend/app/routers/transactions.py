from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import SessionLocal
from .. import models, schemas
from pydantic import BaseModel
from .auth import get_current_user
from typing import List

router = APIRouter(prefix="/transactions", tags=["transactions"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class TransactionCreate(BaseModel):
    product_id: int
    status: str = "Placed"

class TransactionResponse(BaseModel):
    id: int
    product_id: int
    buyer_id: int
    seller_id: int
    status: str
    
    class Config:
        orm_mode = True

@router.post("/", response_model=TransactionResponse)
def create_transaction(txn: TransactionCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Assuming user is buyer
    product = db.query(models.Product).filter(models.Product.id == txn.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
        
    new_txn = models.Transaction(
        product_id=product.id,
        buyer_id=current_user.id,
        seller_id=product.seller_id,
        status=txn.status
    )
    db.add(new_txn)
    
    # Give user a trust coin for a mock successful transaction
    current_user.trust_coins += 1
    current_user.trust_score = min(100.0, current_user.trust_score + 0.5)
    
    db.commit()
    db.refresh(new_txn)
    return new_txn

@router.get("/", response_model=List[TransactionResponse])
def get_transactions(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    txns = db.query(models.Transaction).filter((models.Transaction.buyer_id == current_user.id) | (models.Transaction.seller_id == current_user.id)).all()
    return txns
