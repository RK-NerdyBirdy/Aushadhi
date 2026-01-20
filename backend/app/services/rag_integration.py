"""
RAG Service Integration Module
Provides bridge between RAG LLM service and app backend
Handles context building, data fetching, and result processing
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.medicine import MedicineInfo
from app.models.stock import HospitalStock
from app.models.usage import HospitalUsage
from app.models.order import Order
from app.models.alert import Alert


class RAGContextBuilder:
    """
    Builds rich context for RAG pipeline by fetching data from app database
    """
    
    @staticmethod
    def build_medicine_context(
        hospital_id: str,
        medicine_id: str,
        db: Session,
        days_lookback: int = 90
    ) -> Dict[str, Any]:
        """
        Build comprehensive context for a specific medicine
        Used by RAG pipeline to make informed predictions
        """
        context = {
            "medicine_id": medicine_id,
            "hospital_id": hospital_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # 1. Medicine info
        medicine = db.query(MedicineInfo).filter(
            MedicineInfo.hospital_id == hospital_id,
            MedicineInfo.medicine_id == medicine_id
        ).first()
        
        if medicine:
            context["medicine"] = {
                "name": medicine.medicine_name,
                "price": float(medicine.medicine_price) if medicine.medicine_price else None,
                "cold_storage": medicine.cold_storage,
                "abc_category": medicine.abc_category,
                "ved_category": medicine.ved_category,
                "salt_composition": medicine.salt_composition,
                "pack_size": medicine.pack_size
            }
        
        # 2. Current stock level
        stock = db.query(HospitalStock).filter(
            HospitalStock.hospital_id == hospital_id,
            HospitalStock.medicine_id == medicine_id
        ).first()
        
        if stock:
            days_until_expiry = (stock.medicine_expiry - datetime.now().date()).days if stock.medicine_expiry else None
            context["stock"] = {
                "quantity": stock.medicine_quantity,
                "expiry_date": stock.medicine_expiry.isoformat() if stock.medicine_expiry else None,
                "days_until_expiry": days_until_expiry,
                "expiry_status": RAGContextBuilder._get_expiry_status(days_until_expiry)
            }
        
        # 3. Recent usage patterns
        cutoff_date = datetime.now().date() - timedelta(days=days_lookback)
        usage_records = db.query(HospitalUsage).filter(
            HospitalUsage.hospital_id == hospital_id,
            HospitalUsage.medicine_id == medicine_id,
            HospitalUsage.usage_date >= cutoff_date
        ).order_by(HospitalUsage.usage_date.desc()).all()
        
        usage_amounts = [u.usage_amount for u in usage_records]
        if usage_amounts:
            context["usage"] = {
                "recent_records": len(usage_records),
                "average_daily": sum(usage_amounts) / len(usage_amounts),
                "min_daily": min(usage_amounts),
                "max_daily": max(usage_amounts),
                "total_lookback_days": days_lookback,
                "trend": RAGContextBuilder._calculate_usage_trend(usage_amounts)
            }
        
        # 4. Recent orders
        recent_orders = db.query(Order).filter(
            Order.hospital_id == hospital_id,
            Order.medicine_id == medicine_id
        ).order_by(Order.order_id.desc()).limit(5).all()
        
        if recent_orders:
            context["recent_orders"] = [
                {
                    "order_id": o.order_id,
                    "quantity_predicted": o.medicine_quantity_predicted,
                    "received_quantity": o.recieved_quantity,
                    "status": o.order_status,
                    "expected_delivery": o.expected_delivery_date.isoformat() if o.expected_delivery_date else None
                }
                for o in recent_orders
            ]
        
        # 5. Active alerts
        alerts = db.query(Alert).filter(
            Alert.hospital_id == hospital_id,
            Alert.medicine_id == medicine_id,
            Alert.alert_status == "active"
        ).all()
        
        if alerts:
            context["active_alerts"] = [
                {
                    "type": a.alert_type,
                    "message": a.alert_message,
                    "severity": a.alert_status
                }
                for a in alerts
            ]
        
        return context
    
    @staticmethod
    def _get_expiry_status(days: Optional[int]) -> str:
        """Determine expiry urgency"""
        if days is None:
            return "unknown"
        elif days < 0:
            return "expired"
        elif days < 30:
            return "critical"
        elif days < 90:
            return "warning"
        else:
            return "healthy"
    
    @staticmethod
    def _calculate_usage_trend(usage_amounts: List[int]) -> str:
        """Calculate usage trend from recent data"""
        if len(usage_amounts) < 2:
            return "insufficient_data"
        
        recent = usage_amounts[:len(usage_amounts)//2]
        older = usage_amounts[len(usage_amounts)//2:]
        
        recent_avg = sum(recent) / len(recent) if recent else 0
        older_avg = sum(older) / len(older) if older else 0
        
        if older_avg == 0:
            return "starting"
        
        change = (recent_avg - older_avg) / older_avg
        
        if change > 0.2:
            return "increasing"
        elif change < -0.2:
            return "decreasing"
        else:
            return "stable"


class RAGResultProcessor:
    """
    Processes RAG pipeline results and integrates with app schemas
    """
    
    @staticmethod
    def format_prediction_response(
        raw_prediction: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Format RAG prediction output into app-compatible schema
        """
        return {
            "hospital_id": context["hospital_id"],
            "medicine_id": context["medicine_id"],
            "medicine_name": context.get("medicine", {}).get("name"),
            "prediction_timestamp": datetime.utcnow().isoformat(),
            "forecasting_method": "RAG_LLM_Pipeline",
            "baseline_metrics": raw_prediction.get("baseline_metrics", {}),
            "llm_adjustments": raw_prediction.get("llm_adjustments", {}),
            "final_metrics": raw_prediction.get("final_metrics", {}),
            "confidence_score": raw_prediction.get("confidence", 0),
            "context_used": {
                "usage_trend": context.get("usage", {}).get("trend"),
                "stock_status": context.get("stock", {}).get("expiry_status"),
                "active_alerts": len(context.get("active_alerts", []))
            }
        }
    
    @staticmethod
    def extract_prediction_metrics(formatted: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract prediction metrics for database storage
        """
        metrics = formatted.get("final_metrics", {})
        
        return {
            "X1_amc": metrics.get("average_daily_consumption"),
            "X2_prescriptions": metrics.get("prescription_count"),
            "X3_CDPR": metrics.get("chronic_disease_prevalence"),
            "X4_CV": metrics.get("coefficient_of_variation"),
            "lead_time": metrics.get("lead_time", 7),
            "safety_stock": metrics.get("safety_stock"),
            "reorder_stock": metrics.get("reorder_point"),
            "max_stock": metrics.get("max_stock"),
            "daily_holding_charges": metrics.get("daily_holding_cost")
        }


class RAGServiceIntegration:
    """
    Main integration class that coordinates RAG service with app backend
    """
    
    @staticmethod
    def get_hospital_context(
        hospital_id: str,
        db: Session
    ) -> Dict[str, Any]:
        """
        Build comprehensive hospital-wide context for RAG
        """
        # Get all medicines for hospital
        medicines = db.query(MedicineInfo).filter(
            MedicineInfo.hospital_id == hospital_id
        ).all()
        
        medicine_contexts = []
        for medicine in medicines:
            context = RAGContextBuilder.build_medicine_context(
                hospital_id=hospital_id,
                medicine_id=medicine.medicine_id,
                db=db
            )
            medicine_contexts.append(context)
        
        return {
            "hospital_id": hospital_id,
            "total_medicines": len(medicines),
            "medicines": medicine_contexts,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def process_predictions_batch(
        predictions: List[Dict[str, Any]],
        contexts: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Process batch of predictions with their contexts
        """
        processed = []
        
        for prediction, context in zip(predictions, contexts):
            formatted = RAGResultProcessor.format_prediction_response(
                prediction,
                context
            )
            processed.append(formatted)
        
        return processed
