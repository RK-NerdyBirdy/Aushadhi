from pydantic import BaseModel
from typing import Dict, Optional
from datetime import datetime


class InventorySummary(BaseModel):
    total_medicines: int
    total_stock_value: float
    medicines_below_reorder: int
    medicines_near_expiry: int
    out_of_stock: int


class AbcVedMatrix(BaseModel):
    A_V: int
    A_E: int
    B_V: int
    B_E: int
    C_D: int


class PendingOrdersSummary(BaseModel):
    count: int
    total_value: float


class AlertsSummary(BaseModel):
    critical: int
    high: int
    medium: int
    low: int


class DashboardSummary(BaseModel):
    hospital_name: str
    last_updated: datetime
    inventory_summary: InventorySummary
    cluster_distribution: Dict[str, int]
    abc_ved_matrix: AbcVedMatrix
    pending_orders: PendingOrdersSummary
    alerts: AlertsSummary
