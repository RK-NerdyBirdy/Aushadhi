"""Dashboard and analytics response schemas"""
from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime


class DashboardSummary(BaseModel):
    total_medicines: int
    total_stock_value: float
    low_stock_count: int
    expired_count: int
    expiring_soon_count: int
    pending_orders_count: int
    pending_orders_value: float
    active_alerts_count: int


class UsageMetrics(BaseModel):
    total_usage_7_days: int
    avg_daily_usage: float


class TopMedicine(BaseModel):
    medicine_id: str
    medicine_name: str
    quantity: int


class RecentAlert(BaseModel):
    alert_id: int
    alert_type: str
    alert_message: str
    created_at: str


class DashboardResponse(BaseModel):
    summary: DashboardSummary
    usage_metrics: UsageMetrics
    top_medicines: List[TopMedicine]
    top_usage: List[Dict[str, Any]]
    recent_alerts: List[RecentAlert]


class InventoryHealth(BaseModel):
    health_score: float
    status: str
    total_medicines: int
    low_stock_medicines: int
    expired_medicines: int
    expiring_soon_medicines: int
    recommendations: List[str]


class StockDistribution(BaseModel):
    distribution: Dict[str, int]
