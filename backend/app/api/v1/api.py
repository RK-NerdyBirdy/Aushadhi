from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth, organizations, users, medicines, stock, usage,
    predictions, orders, alerts, dashboard, reports
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(organizations.router, prefix="/organizations", tags=["Organizations"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(medicines.router, prefix="/medicines", tags=["Medicines"])
api_router.include_router(stock.router, prefix="/stock", tags=["Stock"])
api_router.include_router(usage.router, prefix="/usage", tags=["Usage"])
api_router.include_router(predictions.router, prefix="/predictions", tags=["Predictions"])
api_router.include_router(orders.router, prefix="/orders", tags=["Orders"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["Alerts"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(reports.router, prefix="/reports", tags=["Reports"])
