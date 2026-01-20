from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.medicine import Medicine, MedicineCreate, MedicineUpdate
from app.crud import medicine as medicine_crud
from app.api.deps import get_current_user, check_hospital_access
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[Medicine])
def get_medicines(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    abc_category: str = None,
    ved_category: str = None,
    cold_storage: bool = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all medicines for user's hospital"""
    return medicine_crud.get_multi(
        db,
        hospital_id=current_user.hospital_id,
        skip=skip,
        limit=limit,
        abc_category=abc_category,
        ved_category=ved_category,
        cold_storage=cold_storage
    )

@router.get("/{medicine_id}", response_model=Medicine)
def get_medicine(
    medicine_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get specific medicine"""
    medicine = medicine_crud.get(db, hospital_id=current_user.hospital_id, medicine_id=medicine_id)
    if not medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")
    return medicine

@router.post("/", response_model=Medicine, status_code=201)
def create_medicine(
    medicine_create: MedicineCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add new medicine to catalog"""
    check_hospital_access(medicine_create.hospital_id, current_user)
    
    existing = medicine_crud.get(db, hospital_id=medicine_create.hospital_id, medicine_id=medicine_create.medicine_id)
    if existing:
        raise HTTPException(status_code=400, detail="Medicine already exists")
    
    return medicine_crud.create(db, obj_in=medicine_create)

@router.put("/{medicine_id}", response_model=Medicine)
def update_medicine(
    medicine_id: str,
    medicine_update: MedicineUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update medicine information"""
    medicine = medicine_crud.get(db, hospital_id=current_user.hospital_id, medicine_id=medicine_id)
    if not medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")
    
    return medicine_crud.update(db, hospital_id=current_user.hospital_id, medicine_id=medicine_id, obj_in=medicine_update)

@router.delete("/{medicine_id}", status_code=204)
def delete_medicine(
    medicine_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove medicine from catalog"""
    medicine = medicine_crud.get(db, hospital_id=current_user.hospital_id, medicine_id=medicine_id)
    if not medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")
    
    medicine_crud.remove(db, hospital_id=current_user.hospital_id, medicine_id=medicine_id)
    return None
