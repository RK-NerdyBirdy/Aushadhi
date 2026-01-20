from pydantic import BaseModel
from typing import Optional

class QuantityRequest(BaseModel):
    hospital_id: str
    medicine_id: str
    forecast_days: Optional[int] = 14


class BatchQuantityRequest(BaseModel):
    hospital_id: str
    medicine_ids: list[str]
    forecast_days: Optional[int] = 14


QuantityRequest.model_rebuild()
BatchQuantityRequest.model_rebuild()
