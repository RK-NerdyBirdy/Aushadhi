from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime


class PredictionRequest(BaseModel):
    medicine_ids: Optional[List[str]] = None
    recalculate_all: bool = False


class PredictionResponse(BaseModel):
    message: str
    medicines_analyzed: int
    clusters_formed: Dict[str, int]
    calculation_time_seconds: float


class MedicinePredictionResponse(BaseModel):
    medicine_id: str
    medicine_name: str
    current_stock: int
    X1_amc: Optional[float] = None
    X2_prescriptions: Optional[int] = None
    X3_CDPR: Optional[float] = None
    X4_CV: Optional[float] = None
    safety_stock: Optional[int] = None
    reorder_stock: Optional[int] = None
    max_stock: Optional[int] = None
    cluster_group: Optional[int] = None
    needs_reorder: bool = False
    suggested_order_quantity: Optional[int] = None
    
    class Config:
        from_attributes = True


class PredictionsListResponse(BaseModel):
    total_count: int
    page: int
    limit: int
    medicines: List[MedicinePredictionResponse]
