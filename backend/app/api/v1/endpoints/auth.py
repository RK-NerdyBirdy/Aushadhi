from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from app.database import get_db
from app.schemas.user import UserCreate, User
from app.schemas.token import Token
from app.crud import user as user_crud
from app.core.security import verify_password, create_access_token
from app.core.config import settings
from app.api.deps import get_current_user

router = APIRouter()

@router.post("/register", response_model=User, status_code=201)
def register(user_create: UserCreate, db: Session = Depends(get_db)):
    """Register new user"""
    existing_user = user_crud.get_by_email(db, email=user_create.user_email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user = user_crud.create(db, obj_in=user_create)
    return user

@router.post("/login", response_model=Token)
def login(email: str, password: str, db: Session = Depends(get_db)):
    """Login user"""
    user = user_crud.get_by_email(db, email=email)
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.user_id},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout")
def logout():
    """Logout user (client-side token removal)"""
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=User)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user info"""
    return current_user

@router.put("/change-password")
def change_password(
    old_password: str,
    new_password: str,
    db: Session = Depends(get_db),
):
    """Change user password"""
    from app.api.deps import get_current_user
    current_user = get_current_user(db)
    
    if not verify_password(old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect password")
    
    from app.crud.user import user as user_crud_obj
    from app.core.security import get_password_hash
    current_user.hashed_password = get_password_hash(new_password)
    db.add(current_user)
    db.commit()
    
    return {"message": "Password changed successfully"}
