from sqlalchemy.orm import Session
from datetime import timedelta
from app.models.user import User
from app.models.organization import Organization
from app.core.security import verify_password, hash_password, create_access_token
from app.schemas.auth import TokenResponse


class AuthService:
    """Service for authentication operations - supports both hospital and vendor users"""
    
    @staticmethod
    def authenticate_user(
        db: Session,
        email: str,
        password: str
    ) -> dict | None:
        """
        Authenticate user with email and password.
        Returns user data if successful, None if failed.
        Works for both hospital_* and vendor_* roles.
        """
        # Find user by email
        user = db.query(User).filter(User.user_email == email).first()
        
        if not user or not user.is_active:
            return None
        
        # Verify password
        if not verify_password(password, user.user_password):
            return None
        
        # Get organization details
        organization = db.query(Organization).filter(
            Organization.organization_id == user.organization_id
        ).first()
        
        return {
            "user_id": user.user_id,
            "user_name": user.user_name,
            "user_email": user.user_email,
            "organization_id": user.organization_id,
            "organization_name": organization.organization_name if organization else None,
            "user_role": user.user_role
        }
    
    @staticmethod
    def create_access_token_for_user(
        user_id: str,
        organization_id: str,
        user_role: str
    ) -> str:
        """Create JWT access token with user info and role"""
        access_token_expires = timedelta(minutes=1440)  # 24 hours
        return create_access_token(
            user_id=user_id,
            organization_id=organization_id,
            user_role=user_role,
            expires_delta=access_token_expires
        )
    
    @staticmethod
    def get_user_with_organization(
        db: Session,
        user_id: str
    ) -> dict | None:
        """Get user details with organization information"""
        user = db.query(User).filter(User.user_id == user_id).first()
        
        if not user or not user.is_active:
            return None
        
        organization = db.query(Organization).filter(
            Organization.organization_id == user.organization_id
        ).first()
        
        return {
            "user_id": user.user_id,
            "user_name": user.user_name,
            "user_email": user.user_email,
            "organization_id": user.organization_id,
            "organization_name": organization.organization_name if organization else None,
            "user_role": user.user_role
        }
