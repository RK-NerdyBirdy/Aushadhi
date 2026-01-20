from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import date
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.usage import Usage, UsageCreate, UsageUpdate
from app.crud import usage as usage_crud
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[Usage])
def get_usage(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    start_date: date = None,
    end_date: date = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get usage data for user's hospital"""
    if start_date and end_date:
        return usage_crud.get_by_date_range(db, hospital_id=current_user.hospital_id, start_date=start_date, end_date=end_date)
    return usage_crud.get_multi(db, hospital_id=current_user.hospital_id, skip=skip, limit=limit)

@router.get("/{medicine_id}", response_model=Usage)
def get_medicine_usage(
    medicine_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get usage for specific medicine"""
    usage = usage_crud.get(db, hospital_id=current_user.hospital_id, medicine_id=medicine_id)
    if not usage:
        raise HTTPException(status_code=404, detail="Usage record not found")
    return usage

@router.post("/", response_model=Usage, status_code=201)
def record_usage(
    usage_create: UsageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Record medicine usage"""
    from app.api.deps import check_hospital_access
    check_hospital_access(usage_create.hospital_id, current_user)
    
    if usage_create.usage_date is None:
        from datetime import date
        usage_create.usage_date = date.today()
    
    return usage_crud.create(db, obj_in=usage_create)

@router.put("/{medicine_id}", response_model=Usage)
def update_usage(
    medicine_id: str,
    usage_update: UsageUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update usage record"""
    usage = usage_crud.get(db, hospital_id=current_user.hospital_id, medicine_id=medicine_id)
    if not usage:
        raise HTTPException(status_code=404, detail="Usage record not found")
    
    return usage_crud.update(db, hospital_id=current_user.hospital_id, medicine_id=medicine_id, obj_in=usage_update)

@router.get("/date-range/query", response_model=List[Usage])
def get_usage_date_range(
    start_date: date,
    end_date: date,
    hospital_id: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get usage within date range"""
    if not hospital_id:
        hospital_id = current_user.hospital_id
    else:
        from app.api.deps import check_hospital_access
        check_hospital_access(hospital_id, current_user)
    
    return usage_crud.get_by_date_range(db, hospital_id=hospital_id, start_date=start_date, end_date=end_date)

@router.get("/analytics/trends", response_model=dict)
def get_usage_analytics(
    hospital_id: str = None,
    period: str = "monthly",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get usage analytics and trends"""
    if not hospital_id:
        hospital_id = current_user.hospital_id
    else:
        from app.api.deps import check_hospital_access
        check_hospital_access(hospital_id, current_user)
    
    return {"message": "Analytics computation in progress", "period": period}
