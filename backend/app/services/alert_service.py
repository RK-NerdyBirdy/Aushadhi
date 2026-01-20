from sqlalchemy.orm import Session
from datetime import date
from typing import List
from app.crud import stock as stock_crud, prediction as prediction_crud, alert as alert_crud
from app.schemas.alert import AlertCreate
from app.core.utils import parse_expiry_warning_days

class AlertService:
    """Service for generating and managing alerts"""
    
    @staticmethod
    def check_low_stock_alerts(db: Session, hospital_id: str):
        """Generate alerts for medicines below reorder point"""
        stocks = stock_crud.get_multi(db, hospital_id=hospital_id, skip=0, limit=99999)
        
        for stock in stocks:
            prediction = prediction_crud.get(
                db,
                hospital_id=hospital_id,
                medicine_id=stock.medicine_id
            )
            
            if prediction and stock.medicine_quantity <= (prediction.reorder_stock or 0):
                # Check if alert already exists
                existing_alerts = alert_crud.get_active(
                    db,
                    hospital_id=hospital_id,
                    medicine_id=stock.medicine_id,
                    alert_type="low_stock"
                )
                
                if not existing_alerts:
                    alert = AlertCreate(
                        hospital_id=hospital_id,
                        medicine_id=stock.medicine_id,
                        alert_type="low_stock",
                        alert_message=f"{stock.medicine_name} is below reorder point. "
                                     f"Current: {stock.medicine_quantity}, "
                                     f"Reorder at: {prediction.reorder_stock}",
                        alert_status="active"
                    )
                    alert_crud.create(db, obj_in=alert)
    
    @staticmethod
    def check_expiry_alerts(db: Session, hospital_id: str):
        """Generate alerts for medicines expiring soon"""
        days_list = parse_expiry_warning_days()
        stocks = stock_crud.get_multi(db, hospital_id=hospital_id, skip=0, limit=99999)
        today = date.today()
        
        for stock in stocks:
            days_to_expiry = (stock.medicine_expiry - today).days
            
            if days_to_expiry in days_list and days_to_expiry > 0:
                existing_alerts = alert_crud.get_active(
                    db,
                    hospital_id=hospital_id,
                    medicine_id=stock.medicine_id,
                    alert_type="expiry_warning"
                )
                
                if not existing_alerts:
                    alert = AlertCreate(
                        hospital_id=hospital_id,
                        medicine_id=stock.medicine_id,
                        alert_type="expiry_warning",
                        alert_message=f"{stock.medicine_name} expires in {days_to_expiry} days. "
                                     f"Expiry date: {stock.medicine_expiry}",
                        alert_status="active"
                    )
                    alert_crud.create(db, obj_in=alert)
    
    @staticmethod
    def check_overstock_alerts(db: Session, hospital_id: str):
        """Generate alerts for medicines above maximum stock"""
        stocks = stock_crud.get_multi(db, hospital_id=hospital_id, skip=0, limit=99999)
        
        for stock in stocks:
            prediction = prediction_crud.get(
                db,
                hospital_id=hospital_id,
                medicine_id=stock.medicine_id
            )
            
            if prediction and stock.medicine_quantity > (prediction.max_stock or 0):
                existing_alerts = alert_crud.get_active(
                    db,
                    hospital_id=hospital_id,
                    medicine_id=stock.medicine_id,
                    alert_type="overstock"
                )
                
                if not existing_alerts:
                    alert = AlertCreate(
                        hospital_id=hospital_id,
                        medicine_id=stock.medicine_id,
                        alert_type="overstock",
                        alert_message=f"{stock.medicine_name} is overstocked. "
                                     f"Current: {stock.medicine_quantity}, "
                                     f"Max: {prediction.max_stock}",
                        alert_status="active"
                    )
                    alert_crud.create(db, obj_in=alert)

alert_service = AlertService()
