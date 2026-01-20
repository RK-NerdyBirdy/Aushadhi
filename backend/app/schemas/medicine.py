from pydantic import BaseModel
from decimal import Decimal
from typing import Optional

class MedicineBase(BaseModel):
    medicine_name: str
    medicine_price: Decimal
    cold_storage: bool
    abc_category: Optional[str] = None
    ved_category: Optional[str] = None
    salt_composition: Optional[str] = None
    pack_size: Optional[str] = None

class MedicineCreate(MedicineBase):
    hospital_id: str
    medicine_id: str

class MedicineUpdate(BaseModel):
    medicine_name: Optional[str] = None
    medicine_price: Optional[Decimal] = None
    cold_storage: Optional[bool] = None
    abc_category: Optional[str] = None
    ved_category: Optional[str] = None
    salt_composition: Optional[str] = None
    pack_size: Optional[str] = None

class Medicine(MedicineBase):
    hospital_id: str
    medicine_id: str
    
    class Config:
        from_attributes = True
