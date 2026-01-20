from pydantic import BaseModel
from datetime import date
from typing import Optional

class UsageBase(BaseModel):
    medicine_name: str
    usage_amount: int
    usage_date: Optional[date] = None

class UsageCreate(UsageBase):
    hospital_id: str
    medicine_id: str

class UsageUpdate(BaseModel):
    usage_amount: Optional[int] = None
    usage_date: Optional[date] = None

class Usage(UsageBase):
    hospital_id: str
    medicine_id: str
    
    class Config:
        from_attributes = True
