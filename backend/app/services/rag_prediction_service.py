"""
RAG LLM Prediction Service - Integrates RAG pipeline with app predictions
Replaces K-Means clustering with LLM-based context-aware predictions
"""
import json
from typing import List, Dict, Any, Optional
from decimal import Decimal
from sqlalchemy.orm import Session
from rag_llm_service.pipelines.rag_pipeline import RAGPipeline
from rag_llm_service.db.sql_queries import USAGE_SUMMARY_QUERY, STOCK_QUERY, PREDICTION_INPUTS_QUERY
from rag_llm_service.db.neon_client import NeonClient
from app.models.prediction import HospitalPrediction
from app.models.medicine import MedicineInfo
from app.models.stock import HospitalStock
from app.models.usage import HospitalUsage
from app.core.config import settings


class RAGPredictionService:
    """
    Service that uses RAG LLM pipeline to generate predictions
    Replaces traditional ML-based predictions with LLM-enhanced context-aware predictions
    """
    
    def __init__(self):
        # Load prompts
        self.system_prompt = self._load_prompt("system.txt")
        self.forecast_prompt = self._load_prompt("quantity_forecast.txt")
        self.constraints_prompt = self._load_prompt("constraints.txt")
        
        # Initialize RAG pipeline
        self.rag_pipeline = RAGPipeline(
            system_prompt=self.system_prompt,
            forecast_prompt=self.forecast_prompt,
            constraints_prompt=self.constraints_prompt
        )
        self.neon_db = NeonClient()
    
    def _load_prompt(self, filename: str) -> str:
        """Load prompt from file"""
        import os
        from pathlib import Path
        
        prompt_dir = Path(__file__).parent.parent.parent / "rag_llm_service" / "prompts"
        prompt_path = prompt_dir / filename
        
        try:
            with open(prompt_path, 'r') as f:
                return f.read()
        except FileNotFoundError:
            print(f"Warning: Prompt file {filename} not found, using default")
            return ""
    
    def generate_predictions_for_medicine(
        self,
        hospital_id: str,
        medicine_id: str,
        db: Session,
        forecast_days: int = 14
    ) -> Dict[str, Any]:
        """
        Generate LLM-enhanced predictions for a specific medicine
        
        Args:
            hospital_id: Hospital ID
            medicine_id: Medicine ID
            db: Database session
            forecast_days: Number of days to forecast
            
        Returns:
            Dictionary with prediction data ready to save to database
        """
        try:
            # Get baseline metrics from database
            medicine = db.query(MedicineInfo).filter(
                MedicineInfo.hospital_id == hospital_id,
                MedicineInfo.medicine_id == medicine_id
            ).first()
            
            if not medicine:
                return {"error": f"Medicine {medicine_id} not found"}
            
            # Get current stock
            stock = db.query(HospitalStock).filter(
                HospitalStock.hospital_id == hospital_id,
                HospitalStock.medicine_id == medicine_id
            ).first()
            
            # Get usage history
            usage_records = db.query(HospitalUsage).filter(
                HospitalUsage.hospital_id == hospital_id,
                HospitalUsage.medicine_id == medicine_id
            ).all()
            
            # Build baseline forecast from usage data
            baseline_metrics = self._calculate_baseline_metrics(usage_records)
            
            # Run RAG pipeline to get LLM-enhanced predictions
            llm_result = self.rag_pipeline.run(
                hospital_id=hospital_id,
                medicine_id=medicine_id,
                forecast_days=forecast_days
            )
            
            # Combine baseline with LLM adjustments
            adjusted_prediction = self._apply_llm_adjustments(
                baseline_metrics,
                llm_result,
                medicine
            )
            
            return adjusted_prediction
            
        except Exception as e:
            print(f"Error generating predictions: {e}")
            return {"error": str(e)}
    
    def _calculate_baseline_metrics(self, usage_records: List[HospitalUsage]) -> Dict[str, Any]:
        """
        Calculate baseline metrics from usage history
        These serve as input to the LLM for context-aware adjustments
        """
        if not usage_records:
            return {
                "average_usage": 0,
                "total_records": 0,
                "usage_trend": "unknown"
            }
        
        usage_amounts = [u.usage_amount for u in usage_records]
        average_usage = sum(usage_amounts) / len(usage_amounts) if usage_amounts else 0
        
        # Detect trend
        if len(usage_amounts) >= 2:
            recent_avg = sum(usage_amounts[-5:]) / min(5, len(usage_amounts))
            old_avg = sum(usage_amounts[:5]) / min(5, len(usage_amounts))
            trend = "increasing" if recent_avg > old_avg else "decreasing"
        else:
            trend = "stable"
        
        return {
            "average_usage": float(average_usage),
            "total_records": len(usage_records),
            "usage_trend": trend,
            "min_usage": min(usage_amounts) if usage_amounts else 0,
            "max_usage": max(usage_amounts) if usage_amounts else 0
        }
    
    def _apply_llm_adjustments(
        self,
        baseline: Dict[str, Any],
        llm_result: Any,
        medicine: MedicineInfo
    ) -> Dict[str, Any]:
        """
        Apply LLM-suggested adjustments to baseline metrics
        LLM provides adjustment_factor and confidence scores
        """
        adjustment_factor = getattr(llm_result, 'adjustment_factor', 1.0)
        confidence = getattr(llm_result, 'confidence', 0.5)
        
        # Calculate adjusted metrics
        adjusted_amc = baseline.get('average_usage', 0) * adjustment_factor
        
        # Safety stock calculation with LLM context
        lead_time = 7  # Default lead time
        safety_stock = int(adjusted_amc * 1.5)  # 1.5x average as safety buffer
        
        # Reorder point and max stock
        reorder_stock = int(adjusted_amc + safety_stock)
        max_stock = int(reorder_stock * 2)
        
        # Daily holding charge
        daily_holding_charge = float(medicine.medicine_price) * 0.01 if medicine.medicine_price else 0
        
        return {
            "hospital_id": medicine.hospital_id,
            "medicine_id": medicine.medicine_id,
            "medicine_name": medicine.medicine_name,
            "X1_amc": Decimal(str(adjusted_amc)),
            "X2_prescriptions": int(baseline.get('total_records', 0)),
            "X3_CDPR": Decimal("0.5"),  # Chronic disease prevalence (placeholder)
            "X4_CV": Decimal(str(0.3 + (0.2 * (1 - confidence)))),  # Coefficient of variation
            "lead_time": lead_time,
            "safety_stock": safety_stock,
            "reorder_stock": reorder_stock,
            "max_stock": max_stock,
            "daily_holding_charges": Decimal(str(daily_holding_charge)),
            "llm_confidence": confidence,
            "llm_assumptions": getattr(llm_result, 'assumptions', []),
            "llm_risk_flags": getattr(llm_result, 'risk_flags', [])
        }
    
    def generate_all_predictions_for_hospital(
        self,
        hospital_id: str,
        db: Session
    ) -> Dict[str, Any]:
        """
        Generate predictions for all medicines in a hospital
        """
        try:
            # Get all medicines for hospital
            medicines = db.query(MedicineInfo).filter(
                MedicineInfo.hospital_id == hospital_id
            ).all()
            
            predictions = []
            errors = []
            
            for medicine in medicines:
                try:
                    pred = self.generate_predictions_for_medicine(
                        hospital_id=hospital_id,
                        medicine_id=medicine.medicine_id,
                        db=db
                    )
                    
                    if "error" not in pred:
                        predictions.append(pred)
                    else:
                        errors.append({"medicine_id": medicine.medicine_id, "error": pred["error"]})
                        
                except Exception as e:
                    errors.append({"medicine_id": medicine.medicine_id, "error": str(e)})
            
            return {
                "hospital_id": hospital_id,
                "total_medicines": len(medicines),
                "successful_predictions": len(predictions),
                "predictions": predictions,
                "errors": errors
            }
            
        except Exception as e:
            print(f"Error generating predictions for hospital: {e}")
            return {"error": str(e)}
    
    def save_predictions_to_db(
        self,
        predictions: List[Dict[str, Any]],
        db: Session
    ) -> Dict[str, int]:
        """
        Save generated predictions to database
        Uses upsert pattern: update if exists, create if new
        """
        inserted = 0
        updated = 0
        
        for pred_data in predictions:
            if "error" in pred_data:
                continue
            
            try:
                existing = db.query(HospitalPrediction).filter(
                    HospitalPrediction.hospital_id == pred_data["hospital_id"],
                    HospitalPrediction.medicine_id == pred_data["medicine_id"]
                ).first()
                
                if existing:
                    # Update existing
                    for key, value in pred_data.items():
                        if key not in ["hospital_id", "medicine_id"]:
                            setattr(existing, key, value)
                    updated += 1
                else:
                    # Create new
                    new_pred = HospitalPrediction(**pred_data)
                    db.add(new_pred)
                    inserted += 1
                    
            except Exception as e:
                print(f"Error saving prediction: {e}")
        
        db.commit()
        return {"inserted": inserted, "updated": updated}


# Singleton instance
rag_prediction_service = RAGPredictionService()
