from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from decimal import Decimal
from datetime import datetime, timedelta
from app.database import get_db
from app.crud import stock as stock_crud, order as order_crud, alert as alert_crud, usage as usage_crud, medicine as medicine_crud
from app.api.deps import get_current_user
from app.models.user import User
from app.models.stock import HospitalStock
from app.models.usage import HospitalUsage
from app.models.order import Order
from app.models.prediction import HospitalPrediction
from app.services.rag_integration import RAGContextBuilder

router = APIRouter()

@router.get("/")
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive dashboard overview with RAG LLM-enhanced predictions"""
    hospital_id = current_user.hospital_id
    
    # Get all stock
    all_stock = stock_crud.get_multi(db, hospital_id=hospital_id, skip=0, limit=99999)
    total_medicines = len(all_stock) if all_stock else 0
    
    # Calculate total stock value
    total_stock_value = Decimal('0')
    if all_stock:
        for stock in all_stock:
            med = medicine_crud.get(db, hospital_id=hospital_id, medicine_id=stock.medicine_id)
            if med and med.medicine_price:
                total_stock_value += Decimal(stock.medicine_quantity) * Decimal(str(med.medicine_price))
    
    # Low stock count
    low_stock = stock_crud.get_low_stock(db, hospital_id=hospital_id)
    low_stock_count = len(low_stock) if low_stock else 0
    
    # Expiring soon count
    expiring_soon = stock_crud.get_expiring_soon(db, hospital_id=hospital_id, days=90)
    expiring_soon_count = len(expiring_soon) if expiring_soon else 0
    
    # Expired medicines
    expired_count = db.query(HospitalStock).filter(
        and_(
            HospitalStock.hospital_id == hospital_id,
            HospitalStock.medicine_expiry < datetime.now().date()
        )
    ).count()
    
    # RAG LLM Predictions Summary
    rag_predictions = db.query(HospitalPrediction).filter(
        HospitalPrediction.hospital_id == hospital_id
    ).all()
    
    # Get confidence metrics from RAG predictions
    rag_metrics = {
        "total_predictions": len(rag_predictions),
        "average_confidence": 0,
        "active_risk_flags": 0
    }
    
    if rag_predictions:
        confidences = [getattr(p, 'llm_confidence', 0.5) for p in rag_predictions if hasattr(p, 'llm_confidence')]
        if confidences:
            rag_metrics["average_confidence"] = sum(confidences) / len(confidences)
    
    # Pending orders
    pending_orders = order_crud.get_by_status(db, hospital_id=hospital_id, status='pending')
    pending_orders_count = len(pending_orders) if pending_orders else 0
    
    # Total orders value
    total_orders_value = Decimal('0')
    if pending_orders:
        for order in pending_orders:
            if order.medicine_price:
                total_orders_value += Decimal(order.medicine_quantity_predicted) * Decimal(str(order.medicine_price))
    
    # Active alerts
    active_alerts = alert_crud.get_active(db, hospital_id=hospital_id)
    active_alerts_count = len(active_alerts) if active_alerts else 0
    
    # Usage trends (last 7 days)
    last_7_days = datetime.now().date() - timedelta(days=7)
    usage_last_7_days = db.query(HospitalUsage).filter(
        and_(
            HospitalUsage.hospital_id == hospital_id,
            HospitalUsage.usage_date >= last_7_days
        )
    ).all()
    total_usage_7_days = sum(u.usage_amount for u in usage_last_7_days) if usage_last_7_days else 0
    avg_daily_usage = total_usage_7_days / 7 if total_usage_7_days > 0 else 0
    
    # Top 5 medicines by stock quantity
    top_medicines_data = []
    if all_stock:
        top_medicines = sorted(all_stock, key=lambda x: x.medicine_quantity, reverse=True)[:5]
        top_medicines_data = [
            {
                "medicine_id": m.medicine_id,
                "medicine_name": m.medicine_name,
                "quantity": m.medicine_quantity
            }
            for m in top_medicines
        ]
    
    # Top 5 medicines by usage
    top_usage_data = []
    top_usage = db.query(
        HospitalUsage.medicine_id,
        HospitalUsage.medicine_name,
        func.sum(HospitalUsage.usage_amount).label('total_usage')
    ).filter(HospitalUsage.hospital_id == hospital_id).group_by(
        HospitalUsage.medicine_id, HospitalUsage.medicine_name
    ).order_by(func.sum(HospitalUsage.usage_amount).desc()).limit(5).all()
    
    if top_usage:
        top_usage_data = [
            {
                "medicine_id": m.medicine_id,
                "medicine_name": m.medicine_name,
                "total_usage": m.total_usage
            }
            for m in top_usage
        ]
    
    return {
        "summary": {
            "total_medicines": total_medicines,
            "total_stock_value": float(total_stock_value),
            "low_stock_count": low_stock_count,
            "expired_count": expired_count,
            "expiring_soon_count": expiring_soon_count,
            "pending_orders_count": pending_orders_count,
            "pending_orders_value": float(total_orders_value),
            "active_alerts_count": active_alerts_count,
        },
        "usage_metrics": {
            "total_usage_7_days": total_usage_7_days,
            "avg_daily_usage": round(avg_daily_usage, 2)
        },
        "top_medicines": top_medicines_data,
        "top_usage": top_usage_data,
        "recent_alerts": [
            {
                "alert_id": a.alert_id,
                "alert_type": a.alert_type,
                "alert_message": a.alert_message,
                "created_at": a.created_at.isoformat()
            }
            for a in active_alerts[:5]
        ] if active_alerts else []
    }

@router.get("/inventory-health")
def get_inventory_health(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get inventory health metrics"""
    hospital_id = current_user.hospital_id
    
    all_stock = stock_crud.get_multi(db, hospital_id=hospital_id, skip=0, limit=99999)
    
    if not all_stock:
        return {"status": "empty", "message": "No inventory data"}
    
    # Calculate health score
    low_stock = len(stock_crud.get_low_stock(db, hospital_id=hospital_id))
    expired = db.query(HospitalStock).filter(
        and_(
            HospitalStock.hospital_id == hospital_id,
            HospitalStock.medicine_expiry < datetime.now().date()
        )
    ).count()
    expiring_soon = len(stock_crud.get_expiring_soon(db, hospital_id=hospital_id, days=30))
    
    total = len(all_stock)
    problem_medicines = low_stock + expired + expiring_soon
    health_score = max(0, 100 - (problem_medicines / total * 100)) if total > 0 else 0
    
    status = "good" if health_score >= 80 else "warning" if health_score >= 50 else "critical"
    
    return {
        "health_score": round(health_score, 2),
        "status": status,
        "total_medicines": total,
        "low_stock_medicines": low_stock,
        "expired_medicines": expired,
        "expiring_soon_medicines": expiring_soon,
        "recommendations": [
            "Reorder low stock items" if low_stock > 0 else None,
            "Remove expired medicines" if expired > 0 else None,
            "Verify expiring medicines" if expiring_soon > 0 else None,
        ]
    }

@router.get("/stock-distribution")
def get_stock_distribution(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get stock distribution by category"""
    hospital_id = current_user.hospital_id
    
    all_medicines = medicine_crud.get_multi(
        db, hospital_id=hospital_id, skip=0, limit=99999
    )
    
    distribution = {}
    for med in all_medicines:
        category = med.abc_category or "unclassified"
        if category not in distribution:
            distribution[category] = 0
        
        stock = stock_crud.get(db, hospital_id=hospital_id, medicine_id=med.medicine_id)
        if stock:
            distribution[category] += stock.medicine_quantity
    
    return {"distribution": distribution}

@router.get("/metrics")
def get_dashboard_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get key metrics"""
    dashboard_data = get_dashboard(db, current_user)
    return {
        "metrics": dashboard_data["summary"],
        "timestamp": datetime.utcnow().isoformat(),
    }
