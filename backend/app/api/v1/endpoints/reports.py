from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import date, datetime, timedelta
from decimal import Decimal
from app.database import get_db
from app.crud import stock as stock_crud, medicine as medicine_crud, usage as usage_crud, order as order_crud
from app.api.deps import get_current_user
from app.models.user import User
from app.models.stock import HospitalStock
from app.models.usage import HospitalUsage
from app.models.order import Order

router = APIRouter()

@router.get("/inventory")
def get_inventory_report(
    hospital_id: str = None,
    format: str = Query("json", regex="^(json|csv|pdf)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate comprehensive inventory report"""
    if not hospital_id:
        hospital_id = current_user.hospital_id
    else:
        from app.api.deps import check_hospital_access
        check_hospital_access(hospital_id, current_user)
    
    all_stock = stock_crud.get_multi(db, hospital_id=hospital_id, skip=0, limit=99999)
    
    report_data = []
    total_value = Decimal('0')
    
    for stock in all_stock:
        med = medicine_crud.get(db, hospital_id=hospital_id, medicine_id=stock.medicine_id)
        if med:
            stock_value = stock.medicine_quantity * med.medicine_price
            total_value += stock_value
            
            # Calculate days to expiry
            days_to_expiry = (stock.medicine_expiry - date.today()).days
            status = "expired" if days_to_expiry < 0 else "expiring_soon" if days_to_expiry < 30 else "active"
            
            report_data.append({
                "medicine_id": stock.medicine_id,
                "medicine_name": stock.medicine_name,
                "quantity": stock.medicine_quantity,
                "price_per_unit": float(med.medicine_price),
                "total_value": float(stock_value),
                "expiry_date": stock.medicine_expiry.isoformat(),
                "days_to_expiry": days_to_expiry,
                "status": status,
                "category": med.abc_category or "unclassified",
            })
    
    # Sort by value
    report_data = sorted(report_data, key=lambda x: x['total_value'], reverse=True)
    
    if format == "json":
        return {
            "report_type": "inventory",
            "generated_at": datetime.now().isoformat(),
            "total_medicines": len(report_data),
            "total_inventory_value": float(total_value),
            "data": report_data
        }
    elif format == "csv":
        return {"message": "CSV export - download feature pending"}
    else:
        return {"message": "PDF export - download feature pending"}

@router.get("/consumption")
def get_consumption_report(
    hospital_id: str = None,
    start_date: date = None,
    end_date: date = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate consumption report with trends"""
    if not hospital_id:
        hospital_id = current_user.hospital_id
    else:
        from app.api.deps import check_hospital_access
        check_hospital_access(hospital_id, current_user)
    
    if not start_date:
        start_date = date.today() - timedelta(days=30)
    if not end_date:
        end_date = date.today()
    
    usage_data = usage_crud.get_by_date_range(db, hospital_id=hospital_id, start_date=start_date, end_date=end_date)
    
    # Group by medicine
    medicine_usage = {}
    total_consumption = 0
    
    for usage in usage_data:
        if usage.medicine_id not in medicine_usage:
            medicine_usage[usage.medicine_id] = {
                "medicine_name": usage.medicine_name,
                "total_usage": 0,
                "usage_days": 0
            }
        medicine_usage[usage.medicine_id]["total_usage"] += usage.usage_amount
        medicine_usage[usage.medicine_id]["usage_days"] += 1
        total_consumption += usage.usage_amount
    
    # Calculate daily average
    days_in_range = (end_date - start_date).days + 1
    daily_avg = total_consumption / days_in_range if days_in_range > 0 else 0
    
    report_data = [
        {
            "medicine_id": med_id,
            **data,
            "avg_daily_usage": round(data["total_usage"] / days_in_range, 2)
        }
        for med_id, data in sorted(medicine_usage.items(), 
                                   key=lambda x: x[1]['total_usage'], 
                                   reverse=True)
    ]
    
    return {
        "report_type": "consumption",
        "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
        "total_consumption": total_consumption,
        "daily_average": round(daily_avg, 2),
        "data": report_data,
    }

@router.get("/financial")
def get_financial_report(
    hospital_id: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate financial report with cost analysis"""
    if not hospital_id:
        hospital_id = current_user.hospital_id
    else:
        from app.api.deps import check_hospital_access
        check_hospital_access(hospital_id, current_user)
    
    # Current stock value
    all_stock = stock_crud.get_multi(db, hospital_id=hospital_id, skip=0, limit=99999)
    total_stock_value = Decimal('0')
    
    for stock in all_stock:
        med = medicine_crud.get(db, hospital_id=hospital_id, medicine_id=stock.medicine_id)
        if med:
            total_stock_value += stock.medicine_quantity * med.medicine_price
    
    # Order analysis
    all_orders = order_crud.get_multi(db, hospital_id=hospital_id, skip=0, limit=99999)
    total_spent = Decimal('0')
    pending_orders_value = Decimal('0')
    delivered_orders = 0
    
    for order in all_orders:
        order_value = order.medicine_price * (order.recieved_quantity or order.medicine_quantity_predicted)
        if order.order_status == 'delivered':
            total_spent += order_value
            delivered_orders += 1
        elif order.order_status == 'pending':
            pending_orders_value += order_value
    
    avg_order_cost = float(total_spent / delivered_orders) if delivered_orders > 0 else 0
    
    return {
        "report_type": "financial",
        "timestamp": datetime.now().isoformat(),
        "stock": {
            "total_inventory_value": float(total_stock_value),
            "total_medicines": len(all_stock),
        },
        "orders": {
            "total_spent": float(total_spent),
            "pending_value": float(pending_orders_value),
            "delivered_count": delivered_orders,
            "average_order_cost": avg_order_cost,
        },
        "financial_health": {
            "working_capital": float(total_stock_value),
            "pending_obligations": float(pending_orders_value),
        }
    }

@router.get("/abc-analysis")
def get_abc_analysis_report(
    hospital_id: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """ABC analysis report - Always-Better-Control classification"""
    if not hospital_id:
        hospital_id = current_user.hospital_id
    else:
        from app.api.deps import check_hospital_access
        check_hospital_access(hospital_id, current_user)
    
    all_medicines = medicine_crud.get_multi(db, hospital_id=hospital_id, skip=0, limit=99999)
    
    abc_data = {"A": [], "B": [], "C": [], "unclassified": []}
    
    for med in all_medicines:
        stock = stock_crud.get(db, hospital_id=hospital_id, medicine_id=med.medicine_id)
        medicine_info = {
            "medicine_id": med.medicine_id,
            "medicine_name": med.medicine_name,
            "price": float(med.medicine_price),
            "quantity_on_hand": stock.medicine_quantity if stock else 0,
        }
        
        category = med.abc_category or "unclassified"
        abc_data[category].append(medicine_info)
    
    return {
        "report_type": "abc_analysis",
        "description": "Classification based on value and importance",
        "data": abc_data
    }

@router.get("/ved-analysis")
def get_ved_analysis_report(
    hospital_id: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """VED analysis report - Vital-Essential-Desirable classification"""
    if not hospital_id:
        hospital_id = current_user.hospital_id
    else:
        from app.api.deps import check_hospital_access
        check_hospital_access(hospital_id, current_user)
    
    all_medicines = medicine_crud.get_multi(db, hospital_id=hospital_id, skip=0, limit=99999)
    
    ved_data = {"V": [], "E": [], "D": [], "unclassified": []}
    
    for med in all_medicines:
        stock = stock_crud.get(db, hospital_id=hospital_id, medicine_id=med.medicine_id)
        medicine_info = {
            "medicine_id": med.medicine_id,
            "medicine_name": med.medicine_name,
            "price": float(med.medicine_price),
            "quantity_on_hand": stock.medicine_quantity if stock else 0,
        }
        
        category = med.ved_category or "unclassified"
        ved_data[category].append(medicine_info)
    
    return {
        "report_type": "ved_analysis",
        "description": "Classification based on criticality",
        "data": ved_data
    }

@router.get("/expiry")
def get_expiry_report(
    hospital_id: str = None,
    days: int = Query(90, ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Expiry and shelf-life management report"""
    if not hospital_id:
        hospital_id = current_user.hospital_id
    else:
        from app.api.deps import check_hospital_access
        check_hospital_access(hospital_id, current_user)
    
    today = date.today()
    expiring_medicines = stock_crud.get_expiring_soon(db, hospital_id=hospital_id, days=days)
    
    expired = []
    expiring_soon = []
    
    for stock in expiring_medicines:
        days_left = (stock.medicine_expiry - today).days
        medicine_info = {
            "medicine_id": stock.medicine_id,
            "medicine_name": stock.medicine_name,
            "quantity": stock.medicine_quantity,
            "expiry_date": stock.medicine_expiry.isoformat(),
            "days_until_expiry": days_left,
        }
        
        if days_left < 0:
            expired.append(medicine_info)
        else:
            expiring_soon.append(medicine_info)
    
    # Sort by expiry date
    expired = sorted(expired, key=lambda x: x['days_until_expiry'])
    expiring_soon = sorted(expiring_soon, key=lambda x: x['days_until_expiry'])
    
    return {
        "report_type": "expiry",
        "days_threshold": days,
        "summary": {
            "expired_count": len(expired),
            "expiring_soon_count": len(expiring_soon),
        },
        "expired": expired,
        "expiring_soon": expiring_soon,
    }

@router.get("/stock-valuation")
def get_stock_valuation_report(
    hospital_id: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Stock valuation and aging report"""
    if not hospital_id:
        hospital_id = current_user.hospital_id
    else:
        from app.api.deps import check_hospital_access
        check_hospital_access(hospital_id, current_user)
    
    all_stock = stock_crud.get_multi(db, hospital_id=hospital_id, skip=0, limit=99999)
    
    total_value = Decimal('0')
    high_value_items = []
    slow_moving_items = []
    
    for stock in all_stock:
        med = medicine_crud.get(db, hospital_id=hospital_id, medicine_id=stock.medicine_id)
        if med:
            stock_value = stock.medicine_quantity * med.medicine_price
            total_value += stock_value
            
            # High value items (value > 10% of total)
            if stock_value > Decimal('0'):
                high_value_items.append({
                    "medicine_id": stock.medicine_id,
                    "medicine_name": stock.medicine_name,
                    "quantity": stock.medicine_quantity,
                    "value": float(stock_value),
                })
            
            # Slow moving items (low quantity)
            if stock.medicine_quantity < 10:
                slow_moving_items.append({
                    "medicine_id": stock.medicine_id,
                    "medicine_name": stock.medicine_name,
                    "quantity": stock.medicine_quantity,
                    "value": float(stock_value),
                })
    
    high_value_items = sorted(high_value_items, key=lambda x: x['value'], reverse=True)[:10]
    slow_moving_items = sorted(slow_moving_items, key=lambda x: x['quantity'])[:10]
    
    return {
        "report_type": "stock_valuation",
        "total_inventory_value": float(total_value),
        "high_value_items": high_value_items,
        "slow_moving_items": slow_moving_items,
    }
