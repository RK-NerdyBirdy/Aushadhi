from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date, datetime
from decimal import Decimal
from app.database import get_db
from app.crud import stock as stock_crud, medicine as medicine_crud, usage as usage_crud, order as order_crud
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("/inventory")
def get_inventory_report(
    hospital_id: str = None,
    format: str = Query("json", regex="^(json|csv|pdf)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate inventory report"""
    if not hospital_id:
        hospital_id = current_user.hospital_id
    else:
        from app.api.deps import check_hospital_access
        check_hospital_access(hospital_id, current_user)
    
    all_stock = stock_crud.get_multi(db, hospital_id=hospital_id, skip=0, limit=99999)
    
    report_data = []
    for stock in all_stock:
        med = medicine_crud.get(db, hospital_id=hospital_id, medicine_id=stock.medicine_id)
        if med:
            report_data.append({
                "medicine_id": stock.medicine_id,
                "medicine_name": stock.medicine_name,
                "quantity": stock.medicine_quantity,
                "price_per_unit": float(med.medicine_price),
                "total_value": float(stock.medicine_quantity * med.medicine_price),
                "expiry_date": stock.medicine_expiry.isoformat(),
            })
    
    if format == "json":
        return {"report_type": "inventory", "data": report_data}
    elif format == "csv":
        return {"message": "CSV export pending"}
    else:
        return {"message": "PDF export pending"}

@router.get("/consumption")
def get_consumption_report(
    hospital_id: str = None,
    start_date: date = None,
    end_date: date = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate consumption report"""
    if not hospital_id:
        hospital_id = current_user.hospital_id
    else:
        from app.api.deps import check_hospital_access
        check_hospital_access(hospital_id, current_user)
    
    if not start_date:
        start_date = date(date.today().year, 1, 1)
    if not end_date:
        end_date = date.today()
    
    usage_data = usage_crud.get_by_date_range(db, hospital_id=hospital_id, start_date=start_date, end_date=end_date)
    
    report_data = []
    for usage in usage_data:
        report_data.append({
            "medicine_id": usage.medicine_id,
            "medicine_name": usage.medicine_name,
            "usage_date": usage.usage_date.isoformat(),
            "usage_amount": usage.usage_amount,
        })
    
    return {
        "report_type": "consumption",
        "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
        "data": report_data,
    }

@router.get("/financial")
def get_financial_report(
    hospital_id: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate financial report"""
    if not hospital_id:
        hospital_id = current_user.hospital_id
    else:
        from app.api.deps import check_hospital_access
        check_hospital_access(hospital_id, current_user)
    
    all_stock = stock_crud.get_multi(db, hospital_id=hospital_id, skip=0, limit=99999)
    
    total_stock_value = Decimal('0')
    for stock in all_stock:
        med = medicine_crud.get(db, hospital_id=hospital_id, medicine_id=stock.medicine_id)
        if med:
            total_stock_value += stock.medicine_quantity * med.medicine_price
    
    all_orders = order_crud.get_multi(db, hospital_id=hospital_id, skip=0, limit=99999)
    total_spent = Decimal('0')
    for order in all_orders:
        if order.order_status == 'delivered':
            total_spent += order.medicine_price * order.recieved_quantity
    
    return {
        "report_type": "financial",
        "total_stock_value": float(total_stock_value),
        "total_spent": float(total_spent),
        "average_unit_cost": float(total_spent / len(all_orders)) if all_orders else 0,
    }

@router.get("/abc-analysis")
def get_abc_analysis_report(
    hospital_id: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """ABC analysis report"""
    if not hospital_id:
        hospital_id = current_user.hospital_id
    else:
        from app.api.deps import check_hospital_access
        check_hospital_access(hospital_id, current_user)
    
    all_medicines = medicine_crud.get_multi(db, hospital_id=hospital_id, skip=0, limit=99999)
    
    abc_data = {"A": [], "B": [], "C": []}
    for med in all_medicines:
        if med.abc_category:
            abc_data[med.abc_category].append({
                "medicine_id": med.medicine_id,
                "medicine_name": med.medicine_name,
                "price": float(med.medicine_price),
            })
    
    return {"report_type": "abc_analysis", "data": abc_data}

@router.get("/ved-analysis")
def get_ved_analysis_report(
    hospital_id: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """VED analysis report"""
    if not hospital_id:
        hospital_id = current_user.hospital_id
    else:
        from app.api.deps import check_hospital_access
        check_hospital_access(hospital_id, current_user)
    
    all_medicines = medicine_crud.get_multi(db, hospital_id=hospital_id, skip=0, limit=99999)
    
    ved_data = {"V": [], "E": [], "D": []}
    for med in all_medicines:
        if med.ved_category:
            ved_data[med.ved_category].append({
                "medicine_id": med.medicine_id,
                "medicine_name": med.medicine_name,
                "price": float(med.medicine_price),
            })
    
    return {"report_type": "ved_analysis", "data": ved_data}

@router.get("/expiry")
def get_expiry_report(
    hospital_id: str = None,
    days: int = Query(90, ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Expiry report"""
    if not hospital_id:
        hospital_id = current_user.hospital_id
    else:
        from app.api.deps import check_hospital_access
        check_hospital_access(hospital_id, current_user)
    
    expiring_medicines = stock_crud.get_expiring_soon(db, hospital_id=hospital_id, days=days)
    
    report_data = []
    for stock in expiring_medicines:
        days_left = (stock.medicine_expiry - date.today()).days
        report_data.append({
            "medicine_id": stock.medicine_id,
            "medicine_name": stock.medicine_name,
            "quantity": stock.medicine_quantity,
            "expiry_date": stock.medicine_expiry.isoformat(),
            "days_until_expiry": days_left,
        })
    
    return {
        "report_type": "expiry",
        "days_threshold": days,
        "data": report_data,
    }
