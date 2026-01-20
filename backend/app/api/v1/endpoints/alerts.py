from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.alert import Alert, AlertCreate, AlertUpdate
from app.crud import alert as alert_crud
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[Alert])
def get_alerts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    alert_type: str = None,
    alert_status: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all active alerts for user's hospital"""
    alerts = alert_crud.get_multi(db, hospital_id=current_user.hospital_id, skip=skip, limit=limit)
    
    if alert_type:
        alerts = [a for a in alerts if a.alert_type == alert_type]
    if alert_status:
        alerts = [a for a in alerts if a.alert_status == alert_status]
    
    return alerts

@router.get("/{alert_id}", response_model=Alert)
def get_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get specific alert"""
    alert = alert_crud.get(db, alert_id=alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert

@router.post("/", response_model=Alert, status_code=201)
def create_alert(
    alert_create: AlertCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new alert"""
    from app.api.deps import check_hospital_access
    check_hospital_access(alert_create.hospital_id, current_user)
    
    return alert_crud.create(db, obj_in=alert_create)

@router.patch("/{alert_id}/resolve")
def resolve_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Resolve alert"""
    alert = alert_crud.get(db, alert_id=alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    from datetime import datetime
    alert_update = AlertUpdate(alert_status='resolved', resolved_at=datetime.utcnow())
    alert_crud.update(db, alert_id=alert_id, obj_in=alert_update)
    return {"message": "Alert resolved"}

@router.patch("/{alert_id}/dismiss")
def dismiss_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Dismiss alert"""
    alert = alert_crud.get(db, alert_id=alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert_update = AlertUpdate(alert_status='dismissed')
    alert_crud.update(db, alert_id=alert_id, obj_in=alert_update)
    return {"message": "Alert dismissed"}

@router.get("/type/{alert_type}", response_model=List[Alert])
def get_alerts_by_type(
    alert_type: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Filter alerts by type"""
    return alert_crud.get_by_type(db, hospital_id=current_user.hospital_id, alert_type=alert_type)

@router.delete("/{alert_id}", status_code=204)
def delete_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete alert"""
    alert = alert_crud.get(db, alert_id=alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert_crud.remove(db, alert_id=alert_id)
    return None
