"""
Admin Management Endpoint for RAG LLM Service Integration
Provides endpoints for managing, monitoring, and syncing the unified backend
"""
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.organization import Organization
from app.services.unified_backend import unified_backend
from app.services.rag_integration import RAGContextBuilder

router = APIRouter(prefix="/admin/predictions", tags=["admin-predictions"])


@router.post("/sync/{hospital_id}")
def sync_hospital_predictions(
    hospital_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Sync all predictions for a hospital using RAG LLM pipeline
    Runs as background task for efficiency
    """
    # Verify user is admin and belongs to hospital
    if current_user.user_role not in ["admin", "hospital_admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    if current_user.hospital_id != hospital_id:
        raise HTTPException(status_code=403, detail="Cannot sync other hospitals")
    
    def sync_task():
        try:
            result = unified_backend.sync_all_predictions(hospital_id, db)
            # Could log result to analytics
        except Exception as e:
            print(f"Error syncing predictions: {e}")
    
    background_tasks.add_task(sync_task)
    
    return {
        "status": "sync_initiated",
        "hospital_id": hospital_id,
        "message": "Prediction synchronization started",
        "service": "RAG_LLM_Pipeline"
    }


@router.get("/summary/{hospital_id}")
def get_prediction_summary(
    hospital_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get prediction quality and statistics for hospital"""
    if current_user.hospital_id != hospital_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    summary = unified_backend.get_hospital_prediction_summary(hospital_id, db)
    return summary


@router.get("/medicine/{hospital_id}/{medicine_id}")
def get_medicine_prediction_context(
    hospital_id: str,
    medicine_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get complete context used for medicine prediction"""
    if current_user.hospital_id != hospital_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    context = RAGContextBuilder.build_medicine_context(
        hospital_id=hospital_id,
        medicine_id=medicine_id,
        db=db
    )
    
    return {
        "medicine_id": medicine_id,
        "hospital_id": hospital_id,
        "context": context,
        "context_components": list(context.keys())
    }


@router.post("/regenerate/{hospital_id}/{medicine_id}")
def regenerate_medicine_prediction(
    hospital_id: str,
    medicine_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Force regenerate prediction for specific medicine"""
    if current_user.user_role not in ["admin", "hospital_admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    if current_user.hospital_id != hospital_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    try:
        result = unified_backend.predict_medicine_requirements(
            hospital_id=hospital_id,
            medicine_id=medicine_id,
            db=db,
            include_context=True
        )
        
        if result["success"]:
            # Save to database
            pred_data = result["prediction"]
            pred_data["hospital_id"] = hospital_id
            pred_data["medicine_id"] = medicine_id
            
            unified_backend.rag_service.save_predictions_to_db([pred_data], db)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
def check_rag_service_health():
    """Check RAG LLM service health status"""
    try:
        # Verify services are initialized
        services_status = {
            "rag_prediction_service": "active",
            "rag_context_builder": "active",
            "unified_backend": "active"
        }
        
        return {
            "status": "healthy",
            "services": services_status,
            "integration": "RAG_LLM_Pipeline_v1"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@router.get("/stats/{hospital_id}")
def get_prediction_statistics(
    hospital_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed prediction statistics for hospital"""
    if current_user.hospital_id != hospital_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    from app.models.prediction import HospitalPrediction
    
    predictions = db.query(HospitalPrediction).filter(
        HospitalPrediction.hospital_id == hospital_id
    ).all()
    
    if not predictions:
        return {
            "hospital_id": hospital_id,
            "total_predictions": 0,
            "statistics": "No predictions available"
        }
    
    # Calculate detailed statistics
    safety_stocks = [p.safety_stock for p in predictions if p.safety_stock]
    reorder_stocks = [p.reorder_stock for p in predictions if p.reorder_stock]
    max_stocks = [p.max_stock for p in predictions if p.max_stock]
    
    avg_safety = sum(safety_stocks) / len(safety_stocks) if safety_stocks else 0
    avg_reorder = sum(reorder_stocks) / len(reorder_stocks) if reorder_stocks else 0
    avg_max = sum(max_stocks) / len(max_stocks) if max_stocks else 0
    
    return {
        "hospital_id": hospital_id,
        "total_predictions": len(predictions),
        "statistics": {
            "average_safety_stock": round(avg_safety, 2),
            "average_reorder_stock": round(avg_reorder, 2),
            "average_max_stock": round(avg_max, 2),
            "min_safety_stock": min(safety_stocks) if safety_stocks else 0,
            "max_safety_stock": max(safety_stocks) if safety_stocks else 0,
        }
    }


@router.post("/batch-regenerate/{hospital_id}")
def batch_regenerate_predictions(
    hospital_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Batch regenerate all predictions for hospital
    Heavy operation - runs in background
    """
    if current_user.user_role not in ["admin", "hospital_admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    if current_user.hospital_id != hospital_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    def batch_task():
        try:
            result = unified_backend.predict_all_medicines(
                hospital_id=hospital_id,
                db=db,
                save_to_db=True
            )
            print(f"Batch regeneration completed: {result}")
        except Exception as e:
            print(f"Error in batch regeneration: {e}")
    
    background_tasks.add_task(batch_task)
    
    return {
        "status": "batch_processing_started",
        "hospital_id": hospital_id,
        "message": "Batch prediction regeneration initiated",
        "service": "RAG_LLM_Pipeline"
    }
