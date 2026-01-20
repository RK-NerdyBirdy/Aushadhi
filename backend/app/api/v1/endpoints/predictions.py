from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.prediction import Prediction, PredictionCreate, PredictionUpdate
from app.crud import prediction as prediction_crud
from app.api.deps import get_current_user
from app.models.user import User
from app.services.rag_prediction_service import rag_prediction_service

router = APIRouter()

@router.get("/", response_model=List[Prediction])
def get_predictions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all predictions for user's hospital - Powered by RAG LLM"""
    return prediction_crud.get_multi(db, hospital_id=current_user.hospital_id, skip=skip, limit=limit)

@router.get("/{medicine_id}", response_model=Prediction)
def get_prediction(
    medicine_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get RAG LLM-enhanced prediction for specific medicine"""
    prediction = prediction_crud.get(db, hospital_id=current_user.hospital_id, medicine_id=medicine_id)
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")
    return prediction

@router.post("/generate/{medicine_id}", response_model=Dict[str, Any])
def generate_prediction_for_medicine(
    medicine_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate new RAG LLM-enhanced prediction for a specific medicine
    Uses context from usage history, stock, and medicine data to provide
    LLM-informed adjustments to baseline forecasts
    """
    try:
        # Generate prediction using RAG service
        prediction = rag_prediction_service.generate_predictions_for_medicine(
            hospital_id=current_user.hospital_id,
            medicine_id=medicine_id,
            db=db
        )
        
        if "error" in prediction:
            raise HTTPException(status_code=400, detail=prediction["error"])
        
        # Save to database
        saved = rag_prediction_service.save_predictions_to_db([prediction], db)
        
        return {
            "success": True,
            "prediction": prediction,
            "database_status": saved
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction generation failed: {str(e)}")

@router.post("/generate-all", response_model=Dict[str, Any], status_code=202)
def generate_all_predictions(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate RAG LLM-enhanced predictions for all medicines in hospital
    Runs as background task for async execution
    """
    def background_prediction_generation():
        # Generate predictions for all medicines
        results = rag_prediction_service.generate_all_predictions_for_hospital(
            hospital_id=current_user.hospital_id,
            db=db
        )
        
        # Save predictions to database
        if results.get("predictions"):
            rag_prediction_service.save_predictions_to_db(results["predictions"], db)
    
    background_tasks.add_task(background_prediction_generation)
    
    return {
        "status": "processing",
        "message": "Prediction generation started for all medicines",
        "hospital_id": current_user.hospital_id
    }

@router.post("/sync", status_code=202)
def sync_predictions_from_rag(
    background_tasks: BackgroundTasks,
    hospital_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Sync predictions from RAG LLM service for entire hospital
    Uses background tasks for efficient processing
    """
    from app.api.deps import check_hospital_access
    check_hospital_access(hospital_id, current_user)
    
    def sync_task():
        results = rag_prediction_service.generate_all_predictions_for_hospital(hospital_id, db)
        if results.get("predictions"):
            rag_prediction_service.save_predictions_to_db(results["predictions"], db)
    
    background_tasks.add_task(sync_task)
    
    return {
        "message": "Prediction sync initiated for hospital",
        "hospital_id": hospital_id,
        "service": "RAG LLM Pipeline"
    }

@router.put("/{medicine_id}", response_model=Prediction)
def update_prediction(
    medicine_id: str,
    prediction_update: PredictionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update prediction parameters manually (override LLM suggestions)"""
    prediction = prediction_crud.get(db, hospital_id=current_user.hospital_id, medicine_id=medicine_id)
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")
    
    return prediction_crud.update(db, hospital_id=current_user.hospital_id, medicine_id=medicine_id, obj_in=prediction_update)

@router.get("/reorder-alerts/list", response_model=List[Prediction])
def get_reorder_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get medicines needing reorder"""
    from app.crud import stock as stock_crud
    low_stock = stock_crud.get_low_stock(db, hospital_id=current_user.hospital_id)
    return [prediction_crud.get(db, current_user.hospital_id, s.medicine_id) for s in low_stock]
