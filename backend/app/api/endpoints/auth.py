from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.api.deps import get_current_user, require_hospital_user
from app.models.user import User
from app.schemas.auth import UserLogin, TokenResponse, UserResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/api/auth", tags=["authentication"])


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return JWT token.
    Works for both hospital and vendor users.
    
    **Request Body:**
    - `user_email`: User email address
    - `user_password`: User password
    
    **Returns:**
    - `access_token`: JWT token for authenticated requests
    - `token_type`: Bearer token type
    - `user_id`: User identifier
    - `user_name`: User name
    - `organization_id`: Hospital/Vendor/Organization ID
    - `user_role`: User role (hospital_admin, hospital_staff, vendor_admin, vendor_staff)
    """
    # Authenticate user
    user_data = AuthService.authenticate_user(
        db,
        credentials.user_email,
        credentials.user_password
    )
    
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token with organization_id and user_role
    access_token = AuthService.create_access_token_for_user(
        user_data["user_id"],
        user_data["organization_id"],
        user_data["user_role"]
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=user_data["user_id"],
        user_name=user_data["user_name"],
        organization_id=user_data["organization_id"],
        user_role=user_data["user_role"]
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current logged-in user details.
    Works for both hospital and vendor users.
    
    **Headers:**
    - `Authorization: Bearer <token>`
    
    **Returns:**
    - User details with organization information
    """
    user_data = AuthService.get_user_with_organization(db, current_user.user_id)
    
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(**user_data)
