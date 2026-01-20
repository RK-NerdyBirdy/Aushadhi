from pydantic import BaseModel, Field
from typing import List

class LLMQuantityPrediction(BaseModel):
    hospital_id: str
    medicine_id: str
    llm_predicted_quantity: int = Field(ge=0)
    confidence: float = Field(ge=0.0, le=1.0)
    assumptions: List[str]
    risk_flags: List[str]
