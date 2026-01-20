"""
Unified Backend Service Coordinator
Coordinates RAG LLM Service, Prediction Service, and other backend services
"""
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from app.services.rag_prediction_service import rag_prediction_service
from app.services.rag_integration import RAGContextBuilder, RAGResultProcessor, RAGServiceIntegration
from app.models.medicine import MedicineInfo
from app.models.prediction import HospitalPrediction


class UnifiedBackendService:
    """
    Coordinates all backend services into a unified interface
    Handles:
    - RAG LLM predictions
    - Context building and retrieval
    - Data synchronization
    - Result processing and storage
    """
    
    def __init__(self):
        self.rag_service = rag_prediction_service
        self.context_builder = RAGContextBuilder
        self.result_processor = RAGResultProcessor
        self.integration = RAGServiceIntegration
    
    def predict_medicine_requirements(
        self,
        hospital_id: str,
        medicine_id: str,
        db: Session,
        include_context: bool = True
    ) -> Dict[str, Any]:
        """
        Main prediction endpoint - unified interface for all prediction methods
        
        Process:
        1. Build rich context from database
        2. Run RAG LLM pipeline
        3. Process and format results
        4. Return comprehensive prediction with context
        """
        try:
            # Step 1: Build context
            context = self.context_builder.build_medicine_context(
                hospital_id=hospital_id,
                medicine_id=medicine_id,
                db=db
            )
            
            # Step 2: Generate prediction
            raw_prediction = self.rag_service.generate_predictions_for_medicine(
                hospital_id=hospital_id,
                medicine_id=medicine_id,
                db=db
            )
            
            if "error" in raw_prediction:
                return {
                    "success": False,
                    "error": raw_prediction["error"],
                    "context": context if include_context else None
                }
            
            # Step 3: Format result
            formatted = self.result_processor.format_prediction_response(
                raw_prediction,
                context
            )
            
            return {
                "success": True,
                "prediction": formatted,
                "context": context if include_context else None,
                "method": "RAG_LLM_Pipeline"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "context": context if include_context else None
            }
    
    def predict_all_medicines(
        self,
        hospital_id: str,
        db: Session,
        save_to_db: bool = True
    ) -> Dict[str, Any]:
        """
        Generate predictions for all medicines in hospital
        
        Returns detailed status including success/failure counts
        """
        try:
            # Get all medicines
            medicines = db.query(MedicineInfo).filter(
                MedicineInfo.hospital_id == hospital_id
            ).all()
            
            predictions = []
            errors = []
            
            for medicine in medicines:
                try:
                    pred = self.predict_medicine_requirements(
                        hospital_id=hospital_id,
                        medicine_id=medicine.medicine_id,
                        db=db,
                        include_context=False
                    )
                    
                    if pred["success"]:
                        predictions.append(pred["prediction"])
                    else:
                        errors.append({
                            "medicine_id": medicine.medicine_id,
                            "error": pred.get("error")
                        })
                except Exception as e:
                    errors.append({
                        "medicine_id": medicine.medicine_id,
                        "error": str(e)
                    })
            
            # Save to database if requested
            saved_count = 0
            if save_to_db and predictions:
                # Convert formatted predictions to database schema
                db_predictions = self._convert_to_db_schema(predictions)
                result = self.rag_service.save_predictions_to_db(db_predictions, db)
                saved_count = result.get("inserted", 0) + result.get("updated", 0)
            
            return {
                "success": len(errors) == 0,
                "hospital_id": hospital_id,
                "total_medicines": len(medicines),
                "successful_predictions": len(predictions),
                "failed_predictions": len(errors),
                "saved_to_db": saved_count,
                "predictions": predictions,
                "errors": errors if errors else None
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _convert_to_db_schema(self, formatted_predictions: List[Dict]) -> List[Dict]:
        """
        Convert formatted prediction results to database schema
        """
        db_predictions = []
        
        for pred in formatted_predictions:
            db_pred = {
                "hospital_id": pred.get("hospital_id"),
                "medicine_id": pred.get("medicine_id"),
                "medicine_name": pred.get("medicine_name"),
            }
            
            # Extract metrics from final_metrics
            final_metrics = pred.get("final_metrics", {})
            db_pred.update(self.result_processor.extract_prediction_metrics(pred))
            
            # Add RAG-specific fields if available
            if "llm_confidence" in pred:
                db_pred["llm_confidence"] = pred["llm_confidence"]
            if "llm_assumptions" in pred:
                db_pred["llm_assumptions"] = pred["llm_assumptions"]
            if "llm_risk_flags" in pred:
                db_pred["llm_risk_flags"] = pred["llm_risk_flags"]
            
            db_predictions.append(db_pred)
        
        return db_predictions
    
    def get_hospital_prediction_summary(
        self,
        hospital_id: str,
        db: Session
    ) -> Dict[str, Any]:
        """
        Get summary of current predictions for hospital
        Includes statistics and quality metrics
        """
        predictions = db.query(HospitalPrediction).filter(
            HospitalPrediction.hospital_id == hospital_id
        ).all()
        
        if not predictions:
            return {
                "hospital_id": hospital_id,
                "total_predictions": 0,
                "summary": "No predictions available"
            }
        
        # Calculate statistics
        confidences = [
            getattr(p, 'llm_confidence', 0.5) or 0.5
            for p in predictions
            if hasattr(p, 'llm_confidence') and getattr(p, 'llm_confidence', None) is not None
        ]
        
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.5
        
        # Count risk flags
        total_risk_flags = sum(
            len(getattr(p, 'llm_risk_flags', None) or [])
            for p in predictions
            if hasattr(p, 'llm_risk_flags')
        )
        
        return {
            "hospital_id": hospital_id,
            "total_predictions": len(predictions),
            "average_confidence": round(avg_confidence, 2),
            "total_risk_flags": total_risk_flags,
            "prediction_quality": "high" if avg_confidence > 0.8 else "medium" if avg_confidence > 0.6 else "low",
            "last_update": max(
                [getattr(p, 'last_calculated', None) for p in predictions if hasattr(p, 'last_calculated')],
                default=None
            )
        }
    
    def sync_all_predictions(
        self,
        hospital_id: str,
        db: Session
    ) -> Dict[str, Any]:
        """
        Full synchronization of predictions for hospital
        Generates new predictions and updates database
        """
        result = self.predict_all_medicines(
            hospital_id=hospital_id,
            db=db,
            save_to_db=True
        )
        
        # Get summary after sync
        summary = self.get_hospital_prediction_summary(hospital_id, db)
        
        return {
            "sync_result": result,
            "hospital_summary": summary,
            "status": "completed"
        }


# Singleton instance
unified_backend = UnifiedBackendService()
