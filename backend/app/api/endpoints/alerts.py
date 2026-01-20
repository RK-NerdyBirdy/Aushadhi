from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.alert import Alert
from app.models.order import Order
from app.schemas.alert import AlertsListResponse, AlertResponse
from app.schemas.order import OrderResponse
from app.services.procurement_service import AlertService

router = APIRouter(prefix="/api/hospital", tags=["alerts and orders"])


@router.get("/alerts", response_model=AlertsListResponse)
async def get_alerts(
    status: str = Query(None, description="Filter: unread, read, resolved"),
    severity: str = Query(None, description="Filter: critical, high, medium, low"),
    alert_type: str = Query(None, description="Filter: low_stock, expiry_warning, order_delayed"),
    limit: int = Query(50, ge=1, le=500),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get system alerts with filters
    
    **Query Parameters:**
    - `status`: unread, read, resolved
    - `severity`: critical, high, medium, low
    - `alert_type`: low_stock, expiry_warning, order_delayed
    - `limit`: Maximum number of alerts (default: 50)
    """
    alerts = AlertService.get_alerts(
        db,
        current_user.hospital_id,
        status=status,
        severity=severity,
        alert_type=alert_type,
        limit=limit
    )
    
    alert_responses = [
        AlertResponse(
            alert_id=a.alert_id,
            medicine_id=a.medicine_id,
            alert_type=a.alert_type,
            alert_message=a.alert_message,
            severity=a.severity or "medium",
            alert_status=a.alert_status,
            created_at=a.created_at
        )
        for a in alerts
    ]
    
    return AlertsListResponse(
        total_count=len(alert_responses),
        alerts=alert_responses
    )


@router.get("/orders")
async def get_orders(
    status: str = Query(None, description="Filter: pending, completed, cancelled"),
    from_date: str = Query(None, description="Start date (YYYY-MM-DD)"),
    to_date: str = Query(None, description="End date (YYYY-MM-DD)"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=500),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all orders with filters
    
    **Query Parameters:**
    - `status`: pending, completed, cancelled
    - `from_date`: Start date in YYYY-MM-DD format
    - `to_date`: End date in YYYY-MM-DD format
    - `page`: Page number (default: 1)
    - `limit`: Items per page (default: 20)
    """
    query = db.query(Order).filter(Order.hospital_id == current_user.hospital_id)
    
    if status:
        query = query.filter(Order.order_status == status)
    
    if from_date:
        from datetime import datetime
        start = datetime.strptime(from_date, "%Y-%m-%d").date()
        query = query.filter(Order.order_date >= start)
    
    if to_date:
        from datetime import datetime
        end = datetime.strptime(to_date, "%Y-%m-%d").date()
        query = query.filter(Order.order_date <= end)
    
    total_count = query.count()
    
    orders = query.order_by(Order.order_date.desc()).offset(
        (page - 1) * limit
    ).limit(limit).all()
    
    order_responses = [
        OrderResponse(
            order_id=o.order_id,
            medicine_name=o.medicine_name,
            quantity_ordered=o.medicine_quantity_predicted,
            received_quantity=o.received_quantity,
            order_status=o.order_status,
            order_date=o.order_date,
            expected_delivery_date=o.expected_delivery_date,
            actual_delivery_date=o.actual_delivery_date,
            total_cost=o.medicine_quantity_predicted * float(o.medicine_price)
        )
        for o in orders
    ]
    
    return {
        "total_count": total_count,
        "page": page,
        "limit": limit,
        "orders": order_responses
    }
