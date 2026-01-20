from sqlalchemy.orm import Session
from app.models.organization import Organization
from app.schemas.organization import OrganizationCreate, OrganizationUpdate
from app.crud.base import CRUDBase

class CRUDOrganization(CRUDBase[Organization, OrganizationCreate, OrganizationUpdate]):
    def get_by_id(self, db: Session, organization_id: str):
        return db.query(Organization).filter(
            Organization.organization_id == organization_id
        ).first()
    
    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100):
        return db.query(Organization).offset(skip).limit(limit).all()
    
    def create(self, db: Session, obj_in: OrganizationCreate):
        db_obj = Organization(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(self, db: Session, organization_id: str, obj_in: OrganizationUpdate):
        db_obj = self.get_by_id(db, organization_id)
        if db_obj:
            update_data = obj_in.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_obj, field, value)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        return db_obj
    
    def remove(self, db: Session, organization_id: str):
        db_obj = self.get_by_id(db, organization_id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
        return db_obj

organization = CRUDOrganization(Organization)
