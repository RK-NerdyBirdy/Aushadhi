from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.stock import HospitalStock
from app.schemas.stock import StockCreate, StockUpdate
from datetime import date, timedelta

class CRUDStock:
    def get(self, db: Session, hospital_id: str, medicine_id: str):
        return db.query(HospitalStock).filter(
            and_(
                HospitalStock.hospital_id == hospital_id,
                HospitalStock.medicine_id == medicine_id
            )
        ).first()
    
    def get_multi(self, db: Session, hospital_id: str, *, skip: int = 0, limit: int = 100):
        return db.query(HospitalStock).filter(
            HospitalStock.hospital_id == hospital_id
        ).offset(skip).limit(limit).all()
    
    def get_low_stock(self, db: Session, hospital_id: str):
        from app.models.prediction import HospitalPrediction
        return db.query(HospitalStock).join(
            HospitalPrediction,
            and_(
                HospitalStock.hospital_id == HospitalPrediction.hospital_id,
                HospitalStock.medicine_id == HospitalPrediction.medicine_id
            )
        ).filter(
            HospitalStock.hospital_id == hospital_id,
            HospitalStock.medicine_quantity <= HospitalPrediction.reorder_stock
        ).all()
    
    def get_expiring_soon(self, db: Session, hospital_id: str, days: int = 90):
        expiry_date = date.today() + timedelta(days=days)
        return db.query(HospitalStock).filter(
            HospitalStock.hospital_id == hospital_id,
            HospitalStock.medicine_expiry <= expiry_date,
            HospitalStock.medicine_expiry > date.today()
        ).order_by(HospitalStock.medicine_expiry).all()
    
    def create(self, db: Session, obj_in: StockCreate):
        db_obj = HospitalStock(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(self, db: Session, hospital_id: str, medicine_id: str, obj_in: StockUpdate):
        db_obj = self.get(db, hospital_id, medicine_id)
        if db_obj:
            update_data = obj_in.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_obj, field, value)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        return db_obj
    
    def adjust_quantity(self, db: Session, hospital_id: str, medicine_id: str, adjustment: int):
        db_obj = self.get(db, hospital_id, medicine_id)
        if db_obj:
            db_obj.medicine_quantity += adjustment
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

stock = CRUDStock()
