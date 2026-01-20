from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.order import Order
from app.schemas.order import OrderCreate, OrderCreateResponse
from app.services.procurement_service import ProcurementService

router = APIRouter(prefix="/api/hospital/procurement", tags=["procurement"])


class RecommendationResponse:
    """Response for procurement recommendations"""
    pass


@router.get("/recommendations")
async def get_procurement_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get AI-recommended medicines to order
    
    **Returns:**
    - List of medicines that need reordering
    - Sorted by urgency (critical → high → medium)
    - Includes estimated costs and delivery times
    """
    recommendations = ProcurementService.get_recommendations(
        current_user.organization_id,
        db
    )
    
    total_cost = sum(rec['estimated_cost'] for rec in recommendations)
    
    # Count by urgency
    summary = {
        'critical': len([r for r in recommendations if r['urgency'] == 'critical']),
        'high': len([r for r in recommendations if r['urgency'] == 'high']),
        'medium': len([r for r in recommendations if r['urgency'] == 'medium'])
    }
    
    return {
        "recommendations": recommendations,
        "total_recommendations": len(recommendations),
        "total_estimated_cost": total_cost,
        "summary": summary
    }


@router.post("/create-order", response_model=OrderCreateResponse)
async def create_procurement_order(
    request: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create procurement order from recommendations
    
    **Request Body:**
    - `medicines`: List of medicines to order with quantity and price
    - `expected_delivery_days`: Expected delivery timeline (default: 5)
    - `notes`: Optional order notes
    
    **Returns:**
    - List of created order IDs
    - Total cost and quantity
    - Order status (pending)
    """
    if not request.medicines:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one medicine is required"
        )
    
    # Validate medicines
    for medicine in request.medicines:
        if medicine.quantity <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid quantity for {medicine.medicine_name}"
            )
        if medicine.unit_price <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid price for {medicine.medicine_name}"
            )
    
    # Create orders
    order_ids = ProcurementService.create_orders(
        current_user.organization_id,
        [m.dict() for m in request.medicines],
        request.expected_delivery_days,
        db
    )
    
    total_quantity = sum(m.quantity for m in request.medicines)
    total_cost = sum(m.quantity * m.unit_price for m in request.medicines)
    
    expected_delivery_date = (
        datetime.utcnow() + 
        timedelta(days=request.expected_delivery_days)
    ).date()
    
    return OrderCreateResponse(
        message="Order created successfully",
        order_ids=order_ids,
        total_medicines=len(request.medicines),
        total_quantity=total_quantity,
        total_cost=total_cost,
        expected_delivery_date=expected_delivery_date,
        order_status="pending"
    )


from datetime import timedelta
