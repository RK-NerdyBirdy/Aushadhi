from pydantic import BaseModel
from typing import List

class QuantityRequest(BaseModel):
    hospital_id: str
    medicine_id: str

class BatchQuantityRequest(BaseModel):
    hospital_id: str
    medicine_ids: List[str]
