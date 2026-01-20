from pydantic import BaseModel
from datetime import date
from typing import Optional

class StockBase(BaseModel):
    medicine_name: str
    medicine_expiry: date
    medicine_quantity: int

class StockCreate(StockBase):
    hospital_id: str
    medicine_id: str

class StockUpdate(BaseModel):
    medicine_expiry: Optional[date] = None
    medicine_quantity: Optional[int] = None

class Stock(StockBase):
    hospital_id: str
    medicine_id: str
    
    class Config:
        from_attributes = True
