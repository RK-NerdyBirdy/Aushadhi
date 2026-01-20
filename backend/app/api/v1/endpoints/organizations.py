from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.organization import Organization, OrganizationCreate, OrganizationUpdate
from app.crud import organization as org_crud
from app.api.deps import get_current_user, check_admin_role

router = APIRouter()

@router.get("/", response_model=List[Organization])
def get_organizations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    admin = Depends(check_admin_role)
):
    """Get all organizations"""
    return org_crud.get_multi(db, skip=skip, limit=limit)

@router.get("/{organization_id}", response_model=Organization)
def get_organization(
    organization_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get specific organization"""
    org = org_crud.get_by_id(db, organization_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org

@router.post("/", response_model=Organization, status_code=201)
def create_organization(
    org_create: OrganizationCreate,
    db: Session = Depends(get_db),
    admin = Depends(check_admin_role)
):
    """Create new organization"""
    existing = org_crud.get_by_id(db, org_create.organization_id)
    if existing:
        raise HTTPException(status_code=400, detail="Organization already exists")
    
    return org_crud.create(db, obj_in=org_create)

@router.put("/{organization_id}", response_model=Organization)
def update_organization(
    organization_id: str,
    org_update: OrganizationUpdate,
    db: Session = Depends(get_db),
    admin = Depends(check_admin_role)
):
    """Update organization"""
    org = org_crud.get_by_id(db, organization_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    return org_crud.update(db, organization_id, obj_in=org_update)

@router.delete("/{organization_id}", status_code=204)
def delete_organization(
    organization_id: str,
    db: Session = Depends(get_db),
    admin = Depends(check_admin_role)
):
    """Delete organization"""
    org = org_crud.get_by_id(db, organization_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    org_crud.remove(db, organization_id)
    return None
