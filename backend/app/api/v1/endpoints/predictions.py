from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.prediction import Prediction, PredictionCreate, PredictionUpdate
from app.crud import prediction as prediction_crud
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[Prediction])
def get_predictions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all predictions for user's hospital"""
    return prediction_crud.get_multi(db, hospital_id=current_user.hospital_id, skip=skip, limit=limit)

@router.get("/{medicine_id}", response_model=Prediction)
def get_prediction(
    medicine_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get prediction for specific medicine"""
    prediction = prediction_crud.get(db, hospital_id=current_user.hospital_id, medicine_id=medicine_id)
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")
    return prediction

@router.post("/sync", status_code=202)
def sync_predictions_from_ml(
    hospital_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Sync predictions from external ML service"""
    from app.api.deps import check_hospital_access
    check_hospital_access(hospital_id, current_user)
    
    # TODO: Implement async task to fetch from ML service
    return {"message": "Prediction sync initiated for hospital", "hospital_id": hospital_id}

@router.put("/{medicine_id}", response_model=Prediction)
def update_prediction(
    medicine_id: str,
    prediction_update: PredictionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update prediction parameters manually"""
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
