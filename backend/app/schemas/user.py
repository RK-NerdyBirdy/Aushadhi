from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    user_name: str
    user_email: EmailStr
    hospital_id: str
    user_role: str

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    user_name: Optional[str] = None
    user_email: Optional[EmailStr] = None
    user_role: Optional[str] = None
    is_active: Optional[bool] = None

class User(UserBase):
    user_id: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserInDB(User):
    hashed_password: str

class UserResponse(User):
    pass
