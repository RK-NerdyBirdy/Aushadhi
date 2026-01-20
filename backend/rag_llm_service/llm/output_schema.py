from pydantic import BaseModel
from typing import List


class DailyForecast(BaseModel):
    date: str
    predicted_quantity: int
    cumulative_total: int


class LLMQuantityPrediction(BaseModel):
    medicine: str
    hospital_id: str
    forecast_period: str
    total_predicted_demand: int
    data: List[DailyForecast]
