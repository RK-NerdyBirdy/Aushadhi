from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.organization import Organization
from app.models.stock import HospitalStock
from app.models.prediction import HospitalPrediction
from app.models.order import Order
from app.models.alert import Alert
from app.models.medicine import MedicineInfo
from app.schemas.dashboard import (
    DashboardSummary,
    InventorySummary,
    AbcVedMatrix,
    PendingOrdersSummary,
    AlertsSummary
)

router = APIRouter(prefix="/api/hospital/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary)
async def get_dashboard_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get dashboard overview metrics
    
    **Returns:**
    - Inventory summary (total medicines, stock value, below reorder)
    - Cluster distribution
    - ABC-VED matrix distribution
    - Pending orders
    - Alert summary
    """
    hospital_id = current_user.hospital_id
    
    # Get hospital name
    hospital = db.query(Organization).filter(
        Organization.organization_id == hospital_id
    ).first()
    hospital_name = hospital.organization_name if hospital else "Unknown"
    
    # Inventory summary
    stock_data = db.query(HospitalStock).filter(
        HospitalStock.hospital_id == hospital_id
    ).all()
    
    total_medicines = len(stock_data)
    total_stock_value = sum(s.medicine_quantity * 0 for s in stock_data)  # Will update with actual prices
    
    # Get predictions for better metrics
    predictions = db.query(HospitalPrediction).filter(
        HospitalPrediction.hospital_id == hospital_id
    ).all()
    
    # Recalculate with actual prices
    total_stock_value = 0
    medicines_below_reorder = 0
    
    for pred in predictions:
        stock = db.query(HospitalStock).filter(
            HospitalStock.hospital_id == hospital_id,
            HospitalStock.medicine_id == pred.medicine_id
        ).first()
        
        medicine = db.query(MedicineInfo).filter(
            MedicineInfo.hospital_id == hospital_id,
            MedicineInfo.medicine_id == pred.medicine_id
        ).first()
        
        if stock and medicine:
            total_stock_value += stock.medicine_quantity * float(medicine.medicine_price)
            if stock.medicine_quantity <= (pred.reorder_stock or 0):
                medicines_below_reorder += 1
    
    # Check for near expiry (within 30 days)
    from datetime import timedelta, datetime as dt
    expiry_date = (dt.utcnow() + timedelta(days=30)).date()
    medicines_near_expiry = len(db.query(HospitalStock).filter(
        HospitalStock.hospital_id == hospital_id,
        HospitalStock.medicine_expiry <= expiry_date
    ).all())
    
    # Out of stock
    out_of_stock = len(db.query(HospitalStock).filter(
        HospitalStock.hospital_id == hospital_id,
        HospitalStock.medicine_quantity == 0
    ).all())
    
    inventory_summary = InventorySummary(
        total_medicines=total_medicines,
        total_stock_value=total_stock_value,
        medicines_below_reorder=medicines_below_reorder,
        medicines_near_expiry=medicines_near_expiry,
        out_of_stock=out_of_stock
    )
    
    # Cluster distribution
    cluster_dist = {}
    for i in range(1, 5):
        count = len([p for p in predictions if p.cluster_group == i])
        cluster_dist[f"group_{i}"] = count
    
    # ABC-VED matrix
    medicines_full = db.query(MedicineInfo).filter(
        MedicineInfo.hospital_id == hospital_id
    ).all()
    
    abc_ved = {
        "A_V": 0, "A_E": 0, "B_V": 0, "B_E": 0, "C_D": 0
    }
    
    for med in medicines_full:
        abc = med.abc_category or "C"
        ved = med.ved_category or "D"
        key = f"{abc}_{ved}"
        if key in abc_ved:
            abc_ved[key] += 1
        else:
            abc_ved["C_D"] += 1
    
    abc_ved_matrix = AbcVedMatrix(**abc_ved)
    
    # Pending orders
    pending_orders = db.query(Order).filter(
        Order.hospital_id == hospital_id,
        Order.order_status == 'pending'
    ).all()
    
    total_pending_cost = sum(
        o.medicine_quantity_predicted * float(o.medicine_price) 
        for o in pending_orders
    )
    
    pending_orders_summary = PendingOrdersSummary(
        count=len(pending_orders),
        total_value=total_pending_cost
    )
    
    # Alerts
    alerts = db.query(Alert).filter(
        Alert.hospital_id == hospital_id
    ).all()
    
    alerts_summary = AlertsSummary(
        critical=len([a for a in alerts if a.severity == 'critical']),
        high=len([a for a in alerts if a.severity == 'high']),
        medium=len([a for a in alerts if a.severity == 'medium']),
        low=len([a for a in alerts if a.severity == 'low'])
    )
    
    return DashboardSummary(
        hospital_name=hospital_name,
        last_updated=datetime.utcnow(),
        inventory_summary=inventory_summary,
        cluster_distribution=cluster_dist,
        abc_ved_matrix=abc_ved_matrix,
        pending_orders=pending_orders_summary,
        alerts=alerts_summary
    )
