from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import User, UserCreate, UserUpdate
from app.crud import user as user_crud
from app.api.deps import get_current_user, check_admin_role

router = APIRouter()

@router.get("/", response_model=List[User])
def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    hospital_id: str = None,
    db: Session = Depends(get_db),
    admin = Depends(check_admin_role)
):
    """Get all users (admin only)"""
    if hospital_id:
        return user_crud.get_by_hospital(db, hospital_id, skip=skip, limit=limit)
    return user_crud.get_multi(db, skip=skip, limit=limit)

@router.get("/{user_id}", response_model=User)
def get_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get specific user"""
    user = user_crud.get(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/hospital/{hospital_id}", response_model=List[User])
def get_hospital_users(
    hospital_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all users in a hospital"""
    return user_crud.get_by_hospital(db, hospital_id, skip=skip, limit=limit)

@router.post("/", response_model=User, status_code=201)
def create_user(
    user_create: UserCreate,
    db: Session = Depends(get_db),
    admin = Depends(check_admin_role)
):
    """Create new user"""
    existing = user_crud.get_by_email(db, email=user_create.user_email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    return user_crud.create(db, obj_in=user_create)

@router.put("/{user_id}", response_model=User)
def update_user(
    user_id: str,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update user"""
    user = user_crud.get(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user_crud.update(db, user_id, obj_in=user_update)

@router.patch("/{user_id}/deactivate")
def deactivate_user(
    user_id: str,
    db: Session = Depends(get_db),
    admin = Depends(check_admin_role)
):
    """Deactivate user"""
    user = user_crud.get(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_crud.deactivate(db, user_id)
    return {"message": "User deactivated"}

@router.patch("/{user_id}/role")
def update_user_role(
    user_id: str,
    user_role: str,
    db: Session = Depends(get_db),
    admin = Depends(check_admin_role)
):
    """Update user role"""
    user = user_crud.get(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    from app.schemas.user import UserUpdate
    user_update = UserUpdate(user_role=user_role)
    user_crud.update(db, user_id, obj_in=user_update)
    return {"message": "User role updated"}
