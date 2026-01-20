from pydantic import BaseModel
from decimal import Decimal
from datetime import date
from typing import Optional

class OrderBase(BaseModel):
    medicine_name: str
    medicine_quantity_predicted: int
    expected_delivery_date: date
    medicine_price: Decimal
    order_status: str

class OrderCreate(BaseModel):
    hospital_id: str
    medicine_id: str
    medicine_name: str
    medicine_quantity_predicted: int
    expected_delivery_date: date
    medicine_price: Decimal

class OrderUpdate(BaseModel):
    medicine_quantity_predicted: Optional[int] = None
    recieved_quantity: Optional[int] = None
    expected_delivery_date: Optional[date] = None
    actual_delivery_date: Optional[date] = None
    order_status: Optional[str] = None

class Order(OrderBase):
    order_id: int
    hospital_id: str
    medicine_id: str
    recieved_quantity: Optional[int] = None
    actual_delivery_date: Optional[date] = None
    
    class Config:
        from_attributes = True
