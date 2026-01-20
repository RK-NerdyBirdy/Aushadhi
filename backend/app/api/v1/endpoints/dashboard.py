from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from decimal import Decimal
from app.database import get_db
from app.crud import stock as stock_crud, order as order_crud, alert as alert_crud
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("/")
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get dashboard overview for user's hospital"""
    hospital_id = current_user.hospital_id
    
    # Get all stock
    all_stock = stock_crud.get_multi(db, hospital_id=hospital_id, skip=0, limit=99999)
    total_medicines = len(all_stock)
    
    # Calculate total stock value
    total_stock_value = Decimal('0')
    for stock in all_stock:
        from app.crud import medicine as medicine_crud
        med = medicine_crud.get(db, hospital_id=hospital_id, medicine_id=stock.medicine_id)
        if med:
            total_stock_value += stock.medicine_quantity * med.medicine_price
    
    # Low stock count
    low_stock = stock_crud.get_low_stock(db, hospital_id=hospital_id)
    low_stock_count = len(low_stock)
    
    # Expiring soon count
    expiring_soon = stock_crud.get_expiring_soon(db, hospital_id=hospital_id, days=90)
    expiring_soon_count = len(expiring_soon)
    
    # Pending orders
    pending_orders = order_crud.get_by_status(db, hospital_id=hospital_id, status='pending')
    pending_orders_count = len(pending_orders)
    
    # Active alerts
    active_alerts = alert_crud.get_active(db, hospital_id=hospital_id)
    active_alerts_count = len(active_alerts)
    
    return {
        "total_medicines": total_medicines,
        "total_stock_value": float(total_stock_value),
        "low_stock_count": low_stock_count,
        "expiring_soon_count": expiring_soon_count,
        "pending_orders_count": pending_orders_count,
        "active_alerts_count": active_alerts_count,
    }

@router.get("/metrics")
def get_dashboard_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get key metrics"""
    dashboard_data = get_dashboard(db, current_user)
    return {
        "metrics": dashboard_data,
        "timestamp": __import__('datetime').datetime.utcnow().isoformat(),
    }
