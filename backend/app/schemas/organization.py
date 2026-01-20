from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class OrganizationBase(BaseModel):
    organization_id: str
    organization_name: str
    organization_type: str

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationUpdate(BaseModel):
    organization_name: Optional[str] = None
    organization_type: Optional[str] = None

class Organization(OrganizationBase):
    created_at: datetime
    
    class Config:
        from_attributes = True
