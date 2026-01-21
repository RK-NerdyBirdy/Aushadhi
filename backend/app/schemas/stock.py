from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class StockUploadResponse(BaseModel):
    message: str
    records_processed: int
    records_inserted: int
    records_updated: int
    errors: list = []


class StockResponse(BaseModel):
    hospital_id: str
    medicine_id: str
    medicine_name: str
    medicine_expiry: date
    medicine_quantity: int
    
    class Config:
        from_attributes = True
