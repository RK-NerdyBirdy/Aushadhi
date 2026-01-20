from pydantic import BaseModel
from decimal import Decimal
from typing import Optional

class PredictionBase(BaseModel):
    medicine_name: str
    X1_amc: Optional[Decimal] = None
    X2_prescriptions: Optional[int] = None
    X3_CDPR: Optional[Decimal] = None
    X4_CV: Optional[Decimal] = None
    lead_time: Optional[int] = None
    safety_stock: Optional[int] = None
    reorder_stock: Optional[int] = None
    max_stock: Optional[int] = None
    daily_holding_charges: Optional[Decimal] = None

class PredictionCreate(PredictionBase):
    hospital_id: str
    medicine_id: str

class PredictionUpdate(BaseModel):
    lead_time: Optional[int] = None
    safety_stock: Optional[int] = None
    reorder_stock: Optional[int] = None
    max_stock: Optional[int] = None
    daily_holding_charges: Optional[Decimal] = None

class Prediction(PredictionBase):
    hospital_id: str
    medicine_id: str
    
    class Config:
        from_attributes = True
