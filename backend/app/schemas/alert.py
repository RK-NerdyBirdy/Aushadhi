from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AlertBase(BaseModel):
    alert_type: str
    alert_message: str
    alert_status: str

class AlertCreate(AlertBase):
    hospital_id: str
    medicine_id: Optional[str] = None

class AlertUpdate(BaseModel):
    alert_status: Optional[str] = None
    resolved_at: Optional[datetime] = None

class Alert(AlertBase):
    alert_id: int
    hospital_id: str
    medicine_id: Optional[str] = None
    created_at: datetime
    resolved_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
