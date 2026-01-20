from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.usage import HospitalUsage
from app.schemas.usage import UsageCreate, UsageUpdate
from datetime import date

class CRUDUsage:
    def get(self, db: Session, hospital_id: str, medicine_id: str):
        return db.query(HospitalUsage).filter(
            and_(
                HospitalUsage.hospital_id == hospital_id,
                HospitalUsage.medicine_id == medicine_id
            )
        ).first()
    
    def get_multi(self, db: Session, hospital_id: str, *, skip: int = 0, limit: int = 100):
        return db.query(HospitalUsage).filter(
            HospitalUsage.hospital_id == hospital_id
        ).offset(skip).limit(limit).all()
    
    def get_by_date_range(self, db: Session, hospital_id: str, start_date: date, end_date: date):
        return db.query(HospitalUsage).filter(
            HospitalUsage.hospital_id == hospital_id,
            HospitalUsage.usage_date >= start_date,
            HospitalUsage.usage_date <= end_date
        ).all()
    
    def create(self, db: Session, obj_in: UsageCreate):
        db_obj = HospitalUsage(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(self, db: Session, hospital_id: str, medicine_id: str, obj_in: UsageUpdate):
        db_obj = self.get(db, hospital_id, medicine_id)
        if db_obj:
            update_data = obj_in.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_obj, field, value)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        return db_obj
    
    def remove(self, db: Session, hospital_id: str, medicine_id: str):
        db_obj = self.get(db, hospital_id, medicine_id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
        return db_obj

usage = CRUDUsage()
