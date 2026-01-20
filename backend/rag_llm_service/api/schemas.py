from pydantic import BaseModel
from typing import Optional

class QuantityRequest(BaseModel):
    hospital_id: str
    medicine_id: str
    forecast_days: int = 14


class BatchQuantityRequest(BaseModel):
    hospital_id: str
    medicine_ids: List[str]
    forecast_days: int = 14