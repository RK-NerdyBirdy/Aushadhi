from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class AlertResponse(BaseModel):
    alert_id: int
    medicine_id: Optional[str] = None
    medicine_name: Optional[str] = None
    alert_type: str
    alert_message: str
    severity: str
    alert_status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class AlertsListResponse(BaseModel):
    total_count: int
    alerts: List[AlertResponse]
