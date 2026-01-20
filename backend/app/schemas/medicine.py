from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class MedicineCreate(BaseModel):
    medicine_id: str
    medicine_name: str
    medicine_price: float
    cold_storage: bool
    abc_category: Optional[str] = None
    ved_category: Optional[str] = None
    salt_composition: Optional[str] = None
    pack_size: Optional[str] = None


class MedicineResponse(BaseModel):
    hospital_id: str
    medicine_id: str
    medicine_name: str
    medicine_price: float
    cold_storage: bool
    abc_category: Optional[str] = None
    ved_category: Optional[str] = None
    
    class Config:
        from_attributes = True
