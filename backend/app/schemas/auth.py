from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    user_email: EmailStr
    user_password: str


class UserLogin(BaseModel):
    user_email: EmailStr
    user_password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    user_name: str
    organization_id: str
    user_role: str


class UserResponse(BaseModel):
    user_id: str
    user_name: str
    user_email: str
    organization_id: str
    organization_name: Optional[str] = None
    user_role: str
    
    class Config:
        from_attributes = True
