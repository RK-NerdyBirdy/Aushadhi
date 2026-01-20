from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import date
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.stock import Stock, StockCreate, StockUpdate
from app.crud import stock as stock_crud
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[Stock])
def get_stock(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all stock for user's hospital"""
    return stock_crud.get_multi(db, hospital_id=current_user.hospital_id, skip=skip, limit=limit)

@router.get("/{medicine_id}", response_model=Stock)
def get_medicine_stock(
    medicine_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get stock for specific medicine"""
    stock = stock_crud.get(db, hospital_id=current_user.hospital_id, medicine_id=medicine_id)
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    return stock

@router.post("/", response_model=Stock, status_code=201)
def create_stock(
    stock_create: StockCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add stock entry"""
    from app.api.deps import check_hospital_access
    check_hospital_access(stock_create.hospital_id, current_user)
    
    existing = stock_crud.get(db, hospital_id=stock_create.hospital_id, medicine_id=stock_create.medicine_id)
    if existing:
        raise HTTPException(status_code=400, detail="Stock already exists for this medicine")
    
    return stock_crud.create(db, obj_in=stock_create)

@router.put("/{medicine_id}", response_model=Stock)
def update_stock(
    medicine_id: str,
    stock_update: StockUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update stock quantity"""
    stock = stock_crud.get(db, hospital_id=current_user.hospital_id, medicine_id=medicine_id)
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    
    return stock_crud.update(db, hospital_id=current_user.hospital_id, medicine_id=medicine_id, obj_in=stock_update)

@router.get("/low-stock/list", response_model=List[Stock])
def get_low_stock_medicines(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get medicines below reorder point"""
    return stock_crud.get_low_stock(db, hospital_id=current_user.hospital_id)

@router.get("/expiring/list", response_model=List[Stock])
def get_expiring_medicines(
    days: int = Query(90, ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get medicines expiring soon"""
    return stock_crud.get_expiring_soon(db, hospital_id=current_user.hospital_id, days=days)

@router.patch("/{medicine_id}/adjust")
def adjust_stock(
    medicine_id: str,
    adjustment_quantity: int,
    reason: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Manual stock adjustment"""
    stock = stock_crud.get(db, hospital_id=current_user.hospital_id, medicine_id=medicine_id)
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    
    new_quantity = stock.medicine_quantity + adjustment_quantity
    if new_quantity < 0:
        raise HTTPException(status_code=400, detail="Adjustment would result in negative quantity")
    
    updated_stock = stock_crud.adjust_quantity(db, current_user.hospital_id, medicine_id, adjustment_quantity)
    return {"message": f"Stock adjusted by {adjustment_quantity}", "new_quantity": updated_stock.medicine_quantity}
