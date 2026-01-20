from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.stock import HospitalStock
from app.models.prediction import HospitalPrediction
from app.models.medicine import MedicineInfo
from app.models.order import Order
from app.models.alert import Alert


class ProcurementService:
    """Service for procurement recommendations and order management"""
    
    @staticmethod
    def get_recommendations(hospital_id: str, db: Session) -> list:
        """
        Get AI-recommended medicines to order
        
        Criteria:
        - Current stock <= Reorder point (s)
        - Sort by urgency (critical → high → medium)
        """
        # Get all medicines with predictions and stock
        medicines = db.query(HospitalPrediction, HospitalStock, MedicineInfo).outerjoin(
            HospitalStock,
            (HospitalPrediction.hospital_id == HospitalStock.hospital_id) &
            (HospitalPrediction.medicine_id == HospitalStock.medicine_id)
        ).join(
            MedicineInfo,
            (HospitalPrediction.hospital_id == MedicineInfo.hospital_id) &
            (HospitalPrediction.medicine_id == MedicineInfo.medicine_id)
        ).filter(HospitalPrediction.hospital_id == hospital_id).all()
        
        recommendations = []
        
        for pred, stock, medicine in medicines:
            current_stock = stock.medicine_quantity if stock else 0
            reorder_point = pred.reorder_stock or 0
            max_stock = pred.max_stock or 0
            
            # Check if stock is below reorder point
            if current_stock <= reorder_point:
                suggested_qty = max_stock - current_stock
                
                # Determine urgency
                if current_stock < (reorder_point * 0.5):
                    urgency = "critical"
                elif current_stock < (reorder_point * 0.75):
                    urgency = "high"
                else:
                    urgency = "medium"
                
                estimated_cost = suggested_qty * float(medicine.medicine_price)
                
                recommendation = {
                    "medicine_id": pred.medicine_id,
                    "medicine_name": pred.medicine_name,
                    "current_stock": current_stock,
                    "reorder_point": reorder_point,
                    "max_stock": max_stock,
                    "suggested_order_quantity": int(suggested_qty),
                    "urgency": urgency,
                    "reason": f"Stock below reorder point" if current_stock < reorder_point else "Stock low",
                    "estimated_cost": estimated_cost,
                    "expected_delivery_days": pred.lead_time or 3,
                    "cluster_group": pred.cluster_group,
                    "abc_category": medicine.abc_category or "N/A",
                    "ved_category": medicine.ved_category or "N/A"
                }
                
                # Enhanced reason for critical medicines
                if pred.cluster_group == 3:  # High chronic usage
                    recommendation["reason"] = "Stock below reorder point, high chronic usage"
                
                recommendations.append(recommendation)
        
        # Sort by urgency
        urgency_order = {'critical': 0, 'high': 1, 'medium': 2}
        recommendations.sort(key=lambda x: urgency_order[x['urgency']])
        
        return recommendations
    
    @staticmethod
    def create_orders(
        hospital_id: str,
        medicines_list: list,
        expected_delivery_days: int,
        db: Session
    ) -> list:
        """
        Create procurement orders from list of medicines
        """
        order_ids = []
        
        for medicine in medicines_list:
            medicine_id = medicine.get('medicine_id')
            medicine_name = medicine.get('medicine_name')
            quantity = medicine.get('quantity')
            unit_price = medicine.get('unit_price')
            
            # Calculate expected delivery date
            expected_delivery_date = (
                datetime.utcnow() + timedelta(days=expected_delivery_days)
            ).date()
            
            # Create order
            order = Order(
                hospital_id=hospital_id,
                medicine_id=medicine_id,
                medicine_name=medicine_name,
                medicine_quantity_predicted=quantity,
                expected_delivery_date=expected_delivery_date,
                order_status='pending',
                medicine_price=unit_price
            )
            
            db.add(order)
            db.flush()  # Get order_id
            
            order_ids.append(order.order_id)
            
            # Create alert for order confirmation
            AlertService.create_alert(
                db,
                hospital_id=hospital_id,
                medicine_id=medicine_id,
                alert_type='order_placed',
                alert_message=f"Order placed for {quantity} units of {medicine_name}",
                severity='low'
            )
        
        db.commit()
        return order_ids


class AlertService:
    """Service for alert management"""
    
    @staticmethod
    def create_alert(
        db: Session,
        hospital_id: str,
        medicine_id: str,
        alert_type: str,
        alert_message: str,
        severity: str = 'medium'
    ) -> Alert:
        """Create a new alert"""
        alert = Alert(
            hospital_id=hospital_id,
            medicine_id=medicine_id,
            alert_type=alert_type,
            alert_message=alert_message,
            alert_status='unread',
            severity=severity
        )
        
        db.add(alert)
        return alert
    
    @staticmethod
    def get_alerts(
        db: Session,
        hospital_id: str,
        status: str = None,
        severity: str = None,
        alert_type: str = None,
        limit: int = 50
    ) -> list:
        """Get alerts with filters"""
        query = db.query(Alert).filter(Alert.hospital_id == hospital_id)
        
        if status:
            query = query.filter(Alert.alert_status == status)
        
        if severity:
            query = query.filter(Alert.severity == severity)
        
        if alert_type:
            query = query.filter(Alert.alert_type == alert_type)
        
        return query.order_by(Alert.created_at.desc()).limit(limit).all()
    
    @staticmethod
    def mark_alert_as_read(db: Session, alert_id: int) -> Alert:
        """Mark alert as read"""
        alert = db.query(Alert).filter(Alert.alert_id == alert_id).first()
        if alert:
            alert.alert_status = 'read'
            db.commit()
        return alert
    
    @staticmethod
    def resolve_alert(db: Session, alert_id: int) -> Alert:
        """Mark alert as resolved"""
        alert = db.query(Alert).filter(Alert.alert_id == alert_id).first()
        if alert:
            alert.alert_status = 'resolved'
            alert.resolved_at = datetime.utcnow()
            db.commit()
        return alert
