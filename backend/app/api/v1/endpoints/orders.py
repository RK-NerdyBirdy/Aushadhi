from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import date
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.order import Order, OrderCreate, OrderUpdate
from app.crud import order as order_crud
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[Order])
def get_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all orders for user's hospital"""
    orders = order_crud.get_multi(db, hospital_id=current_user.hospital_id, skip=skip, limit=limit)
    if status:
        orders = [o for o in orders if o.order_status == status]
    return orders

@router.get("/{order_id}", response_model=Order)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get specific order"""
    order = order_crud.get(db, order_id=order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.post("/", response_model=Order, status_code=201)
def create_order(
    order_create: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new order"""
    from app.api.deps import check_hospital_access
    check_hospital_access(order_create.hospital_id, current_user)
    
    order_with_status = OrderCreate(**order_create.model_dump())
    from app.schemas.order import OrderCreate as OC
    order_data = order_create.model_dump()
    order_data['order_status'] = 'pending'
    
    return order_crud.create(db, obj_in=OrderCreate(**order_data))

@router.put("/{order_id}", response_model=Order)
def update_order(
    order_id: int,
    order_update: OrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update order"""
    order = order_crud.get(db, order_id=order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return order_crud.update(db, order_id=order_id, obj_in=order_update)

@router.patch("/{order_id}/status")
def update_order_status(
    order_id: int,
    order_status: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update order status"""
    order = order_crud.get(db, order_id=order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    valid_statuses = ['pending', 'approved', 'in_transit', 'delivered', 'cancelled']
    if order_status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of {valid_statuses}")
    
    order_update = OrderUpdate(order_status=order_status)
    order_crud.update(db, order_id=order_id, obj_in=order_update)
    return {"message": f"Order status updated to {order_status}"}

@router.patch("/{order_id}/receive")
def receive_order(
    order_id: int,
    recieved_quantity: int,
    actual_delivery_date: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark order as received"""
    order = order_crud.get(db, order_id=order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order_update = OrderUpdate(
        recieved_quantity=recieved_quantity,
        actual_delivery_date=actual_delivery_date,
        order_status='delivered'
    )
    order_crud.update(db, order_id=order_id, obj_in=order_update)
    
    # Update stock
    from app.crud import stock as stock_crud
    stock = stock_crud.get(db, hospital_id=order.hospital_id, medicine_id=order.medicine_id)
    if stock:
        stock_crud.adjust_quantity(db, order.hospital_id, order.medicine_id, recieved_quantity)
    
    return {"message": "Order received and stock updated"}

@router.get("/pending/list", response_model=List[Order])
def get_pending_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get pending orders"""
    return order_crud.get_by_status(db, hospital_id=current_user.hospital_id, status='pending')

@router.delete("/{order_id}", status_code=204)
def cancel_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cancel order"""
    order = order_crud.get(db, order_id=order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order_update = OrderUpdate(order_status='cancelled')
    order_crud.update(db, order_id=order_id, obj_in=order_update)
    return None
