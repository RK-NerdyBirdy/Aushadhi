from pydantic import BaseModel
from typing import List


class DailyForecast(BaseModel):
    date: str
    predicted_quantity: int
    cumulative_total: int


class LLMQuantityPrediction(BaseModel):
    adjustment_factor: float
    confidence: float = 0.5
    assumptions: List[str] = []
    risk_flags: List[str] = []