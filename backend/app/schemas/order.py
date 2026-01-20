from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date


class OrderItemCreate(BaseModel):
    medicine_id: str
    medicine_name: str
    quantity: int
    unit_price: float


class OrderCreate(BaseModel):
    medicines: List[OrderItemCreate]
    expected_delivery_days: int = 5
    notes: Optional[str] = None


class OrderResponse(BaseModel):
    order_id: int
    medicine_name: str
    quantity_ordered: int
    received_quantity: Optional[int] = None
    order_status: str
    order_date: datetime
    expected_delivery_date: date
    actual_delivery_date: Optional[date] = None
    total_cost: float
    
    class Config:
        from_attributes = True


class OrderCreateResponse(BaseModel):
    message: str
    order_ids: List[int]
    total_medicines: int
    total_quantity: int
    total_cost: float
    expected_delivery_date: date
    order_status: str
