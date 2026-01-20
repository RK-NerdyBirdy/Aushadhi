from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.security import decode_token
from app.database import get_db
from app.models.user import User
from app.models.organization import Organization

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get the current authenticated user from JWT token.
    Works for both hospital and vendor users.
    """
    token = credentials.credentials
    
    # Decode the token
    payload = decode_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    user = db.query(User).filter(User.user_id == user_id).first()
    
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def require_hospital_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Enforce that user is a hospital user (role starts with 'hospital_').
    Used for all hospital endpoints.
    """
    if not current_user.user_role.startswith("hospital_"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint is restricted to hospital users"
        )
    return current_user


async def require_vendor_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Enforce that user is a vendor user (role starts with 'vendor_').
    Reserved for future vendor APIs.
    """
    if not current_user.user_role.startswith("vendor_"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint is restricted to vendor users"
        )
    return current_user
