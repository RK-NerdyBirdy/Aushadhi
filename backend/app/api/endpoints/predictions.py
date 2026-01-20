from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.api.deps import require_hospital_user
from app.models.user import User
from app.models.stock import HospitalStock
from app.models.prediction import HospitalPrediction
from app.schemas.prediction import (
    PredictionRequest,
    PredictionResponse,
    PredictionsListResponse,
    MedicinePredictionResponse
)
from app.services.prediction_engine import PredictionEngine

router = APIRouter(prefix="/api/hospital", tags=["predictions"])


@router.post("/calculate-predictions", response_model=PredictionResponse)
async def calculate_predictions(
    request: PredictionRequest,
    current_user: User = Depends(require_hospital_user),
    db: Session = Depends(get_db)
):
    """
    Calculate X1, X2, X3, X4 and inventory parameters for all medicines (Hospital users only).
    
    **Authentication:** Requires hospital_admin or hospital_staff role
    
    **Implementation Steps:**
    1. Fetch stock and usage data from database
    2. Calculate X1_AMC (Average Monthly Consumption)
    3. Calculate X2_Prescriptions (Monthly average prescriptions)
    4. Calculate X3_CDPR (Chronic Disease Prescription Ratio)
    5. Calculate X4_CV (Coefficient of Variation)
    6. Apply K-Means clustering (4 clusters)
    7. Calculate (s, S) inventory parameters
    8. Save predictions to database
    """
    # Derive hospital_id from organization_id (for hospital users)
    hospital_id = current_user.organization_id
    
    result = PredictionEngine.calculate_predictions(
        hospital_id,
        db,
        request.medicine_ids if request.medicine_ids else None
    )
    
    return PredictionResponse(**result)


@router.get("/predictions", response_model=PredictionsListResponse)
async def get_predictions(
    cluster_group: int = Query(None, description="Filter by cluster group (1-4)"),
    low_stock_only: bool = Query(False, description="Show only items below reorder point"),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=500),
    current_user: User = Depends(require_hospital_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve calculated predictions with filters (Hospital users only).
    
    **Authentication:** Requires hospital_admin or hospital_staff role
    
    **Query Parameters:**
    - `cluster_group`: Filter by cluster (1, 2, 3, or 4)
    - `low_stock_only`: Boolean - show only items below reorder point
    - `page`: Page number (default: 1)
    - `limit`: Items per page (default: 50)
    """
    # Derive hospital_id from organization_id (for hospital users)
    hospital_id = current_user.organization_id
    
    # Build query
    query = db.query(HospitalPrediction, HospitalStock).outerjoin(
        HospitalStock,
        (HospitalPrediction.hospital_id == HospitalStock.hospital_id) &
        (HospitalPrediction.medicine_id == HospitalStock.medicine_id)
    ).filter(HospitalPrediction.hospital_id == hospital_id)
    
    if cluster_group:
        query = query.filter(HospitalPrediction.cluster_group == cluster_group)
    
    # Get total count
    total_count = query.count()
    
    # Apply pagination
    predictions = query.offset((page - 1) * limit).limit(limit).all()
    
    medicines_list = []
    for pred, stock in predictions:
        current_stock = stock.medicine_quantity if stock else 0
        
        # Filter low stock if requested
        if low_stock_only and current_stock > (pred.reorder_stock or 0):
            continue
        
        needs_reorder = current_stock <= (pred.reorder_stock or 0)
        suggested_qty = (pred.max_stock or 0) - current_stock if needs_reorder else 0
        
        medicine = MedicinePredictionResponse(
            medicine_id=pred.medicine_id,
            medicine_name=pred.medicine_name,
            current_stock=current_stock,
            X1_amc=float(pred.X1_amc) if pred.X1_amc else None,
            X2_prescriptions=pred.X2_prescriptions,
            X3_CDPR=float(pred.X3_CDPR) if pred.X3_CDPR else None,
            X4_CV=float(pred.X4_CV) if pred.X4_CV else None,
            safety_stock=pred.safety_stock,
            reorder_stock=pred.reorder_stock,
            max_stock=pred.max_stock,
            cluster_group=pred.cluster_group,
            needs_reorder=needs_reorder,
            suggested_order_quantity=int(suggested_qty) if suggested_qty > 0 else 0
        )
        medicines_list.append(medicine)
    
    return PredictionsListResponse(
        total_count=total_count,
        page=page,
        limit=limit,
        medicines=medicines_list
    )
